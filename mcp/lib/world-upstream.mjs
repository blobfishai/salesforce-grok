/**
 * Shared upstream machinery for all blobfish-world MCP servers (the per-vendor
 * servers, the harness server, and the legacy mega-bridge).
 *
 * Multi-server episodes share ONE world session and ONE merged rollout trace:
 *  - BLOBFISH_SESSION_FILE: JSON {"session_id": ...}. The RUNNER creates the
 *    session and writes this file before spawning servers (no race); servers in
 *    shared mode only read it and never delete the session.
 *  - BLOBFISH_TRACE_FILE: append-only JSONL, one verifier-grade record per tool
 *    call ({tool, requested_tool, arguments, observation, ok, vendor, ts}).
 *    Line appends are atomic enough at these sizes; the harness server merges by
 *    parsing the file in order.
 * Standalone mode (no env files) preserves the old behavior: own session,
 * in-memory trace, delete session on close.
 */
import { readFileSync, appendFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

export const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..");

export function loadConfig() {
  return JSON.parse(readFileSync(join(ROOT, "config", "world.config.json"), "utf8"));
}

export function loadEnv() {
  let fileVars = {};
  try {
    fileVars = Object.fromEntries(
      readFileSync(join(ROOT, ".env"), "utf8").split("\n")
        .map((l) => l.trim()).filter((l) => /^[A-Z0-9_]+=/.test(l))
        .map((l) => [l.slice(0, l.indexOf("=")), l.slice(l.indexOf("=") + 1)])
    );
  } catch { /* no .env */ }
  return { ...fileVars, ...process.env };
}

/** Resolve the world base URL + auth from env/config (hosted or local). */
export function resolveWorld(env, config) {
  const LOCAL = env.BLOBFISH_LOCAL === "1" || env.BLOBFISH_LOCAL === "true";
  const KEY = env.BLOBFISH_API_KEY;
  const WORLD_ID = env.BLOBFISH_WORLD_ID ?? config.blobfish.worldId;
  const WORLD_BASE = LOCAL
    ? (env.BLOBFISH_LOCAL_BASE ?? config.blobfish.localBase ?? "http://127.0.0.1:8971")
    : `${config.blobfish.api}/sandbox/worlds/${WORLD_ID}`;
  return { LOCAL, KEY, WORLD_ID, WORLD_BASE, MCP_URL: `${WORLD_BASE}/mcp` };
}

// ---------------------------------------------------------------- schema repair
export function normSchema(s) {
  if (!s || typeof s !== "object" || Array.isArray(s)) return { type: "object", properties: {} };
  let out;
  if (s.type === "object") out = { properties: {}, ...s };
  else if (s.properties) out = { ...s, type: "object" };
  else return { type: "object", properties: {} };
  return dedupeRequired(out);
}

// Distilled tool schemas can ship duplicate `required` entries
// (["segment_id","segment_id"]) — DeepSeek/Anthropic reject the whole request.
export function dedupeRequired(node) {
  if (!node || typeof node !== "object") return node;
  if (Array.isArray(node)) return node.map(dedupeRequired);
  const out = { ...node };
  if (Array.isArray(out.required)) out.required = [...new Set(out.required)];
  for (const k of ["properties", "items", "definitions", "$defs"]) {
    if (out[k] && typeof out[k] === "object") {
      out[k] = Array.isArray(out[k]) ? out[k].map(dedupeRequired)
        : Object.fromEntries(Object.entries(out[k]).map(([n, v]) => [n, dedupeRequired(v)]));
    }
  }
  return out;
}

// ---------------------------------------------------------------- upstream client
export class WorldUpstream {
  constructor({ env, config, clientName }) {
    this.env = env ?? loadEnv();
    this.config = config ?? loadConfig();
    Object.assign(this, resolveWorld(this.env, this.config));
    this.clientName = clientName ?? "world-upstream";
    this.session = null;
    this.sharedSessionFile = this.env.BLOBFISH_SESSION_FILE || null;
    this.traceFile = this.env.BLOBFISH_TRACE_FILE || null;
    this.localTrace = []; // standalone-mode trace
    this.upstreamId = 1000;
    this.world = {};
  }

  headers() {
    return {
      ...(this.KEY ? { "X-API-Key": this.KEY } : {}),
      "Content-Type": "application/json",
      Accept: "application/json, text/event-stream",
      ...(this.session ? { "Mcp-Session-Id": this.session, "X-Blobfish-Session": this.session } : {}),
    };
  }

  async rest(path, opts = {}) {
    const res = await fetch(`${this.WORLD_BASE}${path}`, { ...opts, headers: { ...this.headers(), ...(opts.headers ?? {}) } });
    const text = await res.text();
    let json = null;
    try { json = JSON.parse(text); } catch { /* non-JSON */ }
    return { ok: res.ok, status: res.status, text, json };
  }

  async mcp(method, params, { timeoutMs = 170000, notification = false } = {}) {
    const id = notification ? undefined : ++this.upstreamId;
    const body = JSON.stringify({ jsonrpc: "2.0", ...(notification ? {} : { id }), method, params });
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), timeoutMs);
    try {
      const res = await fetch(this.MCP_URL, { method: "POST", headers: this.headers(), body, signal: ctrl.signal });
      const ctype = res.headers.get("content-type") ?? "";
      const text = await res.text();
      if (notification) return null;
      if (!res.ok) throw new Error(`upstream MCP HTTP ${res.status}: ${text.slice(0, 300)}`);
      let messages = [];
      if (ctype.includes("text/event-stream")) {
        for (const chunk of text.split("\n")) {
          const line = chunk.trim();
          if (line.startsWith("data:")) { try { messages.push(JSON.parse(line.slice(5).trim())); } catch { /* frame */ } }
        }
      } else {
        try { messages = [JSON.parse(text)]; } catch { throw new Error(`upstream MCP non-JSON reply: ${text.slice(0, 300)}`); }
      }
      const match = messages.find((m) => m.id === id) ?? messages.find((m) => m.result !== undefined || m.error !== undefined);
      if (!match) throw new Error("upstream MCP: no response message found");
      if (match.error) throw new Error(`upstream MCP ${match.error.code}: ${match.error.message}`);
      return match.result;
    } finally {
      clearTimeout(t);
    }
  }

  /** Attach to the shared session (file) or create a standalone one. */
  async attachSession() {
    if (this.sharedSessionFile) {
      const deadline = Date.now() + 15000;
      while (Date.now() < deadline) {
        if (existsSync(this.sharedSessionFile)) {
          try {
            const sid = JSON.parse(readFileSync(this.sharedSessionFile, "utf8")).session_id;
            if (sid) { this.session = sid; this.ownsSession = false; return sid; }
          } catch { /* partial write; retry */ }
        }
        await new Promise((r) => setTimeout(r, 150));
      }
      throw new Error(`shared session file never appeared: ${this.sharedSessionFile}`);
    }
    const s = await this.rest("/sessions", { method: "POST", body: "{}" });
    if (!s.ok) throw new Error(`session create ${s.status}: ${s.text.slice(0, 300)}`);
    this.session = s.json.session_id ?? s.json.sessionId ?? null;
    this.ownsSession = true;
    return this.session;
  }

  /** initialize + tools/list against the upstream; returns normalized tool defs. */
  async boot() {
    await this.attachSession();
    const init = await this.mcp("initialize", {
      protocolVersion: "2025-06-18",
      capabilities: {},
      clientInfo: { name: this.clientName, version: "1.0.0" },
    }, { timeoutMs: 30000 });
    this.world = init.world ?? {};
    this.serverInfo = init.serverInfo;
    await this.mcp("notifications/initialized", {}, { notification: true });
    const list = await this.mcp("tools/list", {}, { timeoutMs: 60000 });
    return (list.tools ?? []).map((t) => ({
      name: t.name,
      description: t.description ?? "",
      inputSchema: normSchema(t.inputSchema ?? t.input_schema),
    }));
  }

  /** Record a verifier-grade trace entry (shared file or local memory). */
  recordTrace(entry) {
    if (this.traceFile) {
      try { appendFileSync(this.traceFile, JSON.stringify(entry) + "\n"); } catch (e) {
        process.stderr.write(`[${this.clientName}] trace append failed: ${e.message}\n`);
      }
    } else {
      this.localTrace.push(entry);
    }
  }

  /** Merged trace in call order (shared file wins over local memory). */
  readTrace() {
    if (this.traceFile && existsSync(this.traceFile)) {
      return readFileSync(this.traceFile, "utf8").trim().split("\n").filter(Boolean)
        .map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
    }
    return this.localTrace;
  }

  /** Standalone servers release their own session; shared sessions are the runner's. */
  async releaseSession() {
    if (this.ownsSession && this.session) {
      try { await this.rest(`/sessions/${encodeURIComponent(this.session)}`, { method: "DELETE" }); } catch { /* best effort */ }
    }
  }
}

// ---------------------------------------------------------------- stdio plumbing
export function stdioServe({ serverInfo, instructions, onList, onCall, onClose }) {
  const send = (msg) => process.stdout.write(JSON.stringify(msg) + "\n");
  const reply = (id, result) => send({ jsonrpc: "2.0", id, result });
  const replyErr = (id, code, message) => send({ jsonrpc: "2.0", id, error: { code, message } });
  const toolResult = (id, ok, text) => reply(id, { content: [{ type: "text", text }], isError: !ok });

  async function handle(msg) {
    const { id, method, params = {} } = msg;
    const isNotification = id === undefined || id === null;
    try {
      switch (method) {
        case "initialize":
          return reply(id, {
            protocolVersion: params.protocolVersion ?? "2025-06-18",
            capabilities: { tools: { listChanged: false }, resources: {} },
            serverInfo,
            instructions,
          });
        case "notifications/initialized":
        case "notifications/cancelled":
          return;
        case "ping":
          return reply(id, {});
        case "tools/list":
          return reply(id, { tools: onList() });
        case "tools/call": {
          const out = await onCall(params.name, params.arguments ?? {});
          if (out.raw) return reply(id, out.raw);
          return toolResult(id, out.ok, out.text);
        }
        default:
          if (!isNotification) return replyErr(id, -32601, `Method not found: ${method}`);
      }
    } catch (e) {
      if (!isNotification) return replyErr(id, -32603, `${serverInfo.name} error: ${e.message}`);
      process.stderr.write(`[${serverInfo.name}] error in ${method}: ${e.stack}\n`);
    }
  }

  import("node:readline").then(({ createInterface }) => {
    const rl = createInterface({ input: process.stdin, terminal: false });
    rl.on("line", (line) => {
      if (!line.trim()) return;
      let msg;
      try { msg = JSON.parse(line); } catch { return replyErr(null, -32700, "Parse error"); }
      handle(msg).catch((e) => process.stderr.write(`[${serverInfo.name}] unhandled: ${e.stack}\n`));
    });
    rl.on("close", async () => {
      try { await onClose?.(); } catch { /* best effort */ }
      process.exit(0);
    });
  });
}
