#!/usr/bin/env node
/**
 * One MCP server per vendor/product — the realistic topology where an agent
 * connects to "salesforce-crm", "stripe-billing", "slack", ... as separate MCP
 * servers rather than one mega-bridge.
 *
 * Usage: node mcp/vendor-server.mjs --vendor salesforce-crm   (or MCP_VENDOR env)
 *
 * The server filters the world's namespaced tool surface down to its vendor's
 * namespaces from config/mcp-servers.json and exposes BARE tool names (a real
 * Salesforce MCP server serves `list_lead`, not `salesforce.list_lead`).
 * Multi-server episodes share one world session (BLOBFISH_SESSION_FILE, created
 * by the runner) and append to one merged trace (BLOBFISH_TRACE_FILE) so
 * cross-vendor state is consistent and verification sees the whole rollout.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { ROOT, WorldUpstream, stdioServe } from "./lib/world-upstream.mjs";

const argv = process.argv.slice(2);
const VENDOR = argv.includes("--vendor") ? argv[argv.indexOf("--vendor") + 1] : process.env.MCP_VENDOR;
const registry = JSON.parse(readFileSync(join(ROOT, "config", "mcp-servers.json"), "utf8"));
const spec = registry.vendors[VENDOR];
if (!spec) {
  process.stderr.write(`[vendor-server] unknown vendor '${VENDOR}' — have: ${Object.keys(registry.vendors).join(", ")}\n`);
  process.exit(1);
}

const up = new WorldUpstream({ clientName: `mcp-${VENDOR}` });
const NS = new Set(spec.namespaces);

let TOOLS = [];        // exposed defs (bare names)
const toUpstream = new Map(); // bare -> namespaced upstream name

const allTools = await up.boot().catch((e) => {
  process.stderr.write(`[${VENDOR}] boot failed: ${e.message}\n`);
  process.exit(1);
});
for (const t of allTools) {
  const dot = t.name.indexOf(".");
  const ns = dot > 0 ? t.name.slice(0, dot) : "";
  if (!NS.has(ns)) continue;
  const bare = dot > 0 ? t.name.slice(dot + 1) : t.name;
  toUpstream.set(bare, t.name);
  TOOLS.push({ name: bare, description: t.description, inputSchema: t.inputSchema });
}
process.stderr.write(`[${VENDOR}] ${TOOLS.length} tools (${[...NS].join(",")}) — session ${up.session}${up.sharedSessionFile ? " (shared)" : ""}\n`);

const clipObs = (s) => (typeof s === "string" && s.length > 4000 ? s.slice(0, 4000) : s);

stdioServe({
  serverInfo: { name: VENDOR, version: "1.0.0" },
  instructions: `${spec.product} — ${spec.blurb} Fully synthetic simulation ("Morgan Stanley (SIMULATED)" scenario; no real entities). Tools execute against shared live world state.`,
  onList: () => TOOLS,
  onCall: async (bare, args) => {
    const upstream = toUpstream.get(bare);
    if (!upstream) return { ok: false, text: `Unknown tool '${bare}' on ${VENDOR}` };
    try {
      const result = await up.mcp("tools/call", { name: upstream, arguments: args });
      const obsText = (result?.content ?? []).map((c) => c.text ?? "").join("\n");
      up.recordTrace({ tool: bare, requested_tool: upstream, arguments: args, observation: clipObs(obsText), ok: !result?.isError, vendor: VENDOR, ts: Date.now() });
      return { raw: result };
    } catch (e) {
      up.recordTrace({ tool: bare, requested_tool: upstream, arguments: args, observation: `ERROR: ${e.message}`, ok: false, vendor: VENDOR, ts: Date.now() });
      return { ok: false, text: `ERROR: ${e.message}` };
    }
  },
  onClose: () => up.releaseSession(),
});
