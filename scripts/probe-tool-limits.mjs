#!/usr/bin/env node
/**
 * Measure each roster provider's MAX TOOLS PER REQUEST against the real
 * densified tool surface — the limit that decides which models can run the
 * wave-6 world at all (xAI rejects 407 tools outright: "Maximum tools limit
 * reached. 407 tools have been provided but the maximum is 350.").
 *
 * Sends a 1-token completion carrying N real tool definitions from world.json
 * and binary-searches N per model between --min and the full surface. Reports
 * the accepted ceiling per model. Input-token cost only (~$0.10-0.50 total).
 *
 * Usage: node scripts/probe-tool-limits.mjs [--models a,b] [--min 100]
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const argv = process.argv.slice(2);
const opt = (n, d) => (argv.includes(n) ? argv[argv.indexOf(n) + 1] : d);

const env = Object.fromEntries(
  readFileSync(join(ROOT, ".env"), "utf8")
    .split("\n").filter((l) => /^[A-Z0-9_]+=/.test(l))
    .map((l) => [l.slice(0, l.indexOf("=")), l.slice(l.indexOf("=") + 1).trim()]));

const roster = JSON.parse(readFileSync(join(ROOT, "config", "model-roster.json"), "utf8"));

// Pull the SAME normalized schemas the runner sends: the world server's MCP
// tools/list (server.py::mcp_input_schema repairs raw world.json schemas, e.g.
// the duplicate `required` entry on get_contactdb_segments_segment_id).
const WORLD_BASE = process.env.BLOBFISH_LOCAL_BASE ?? "http://127.0.0.1:8971";
const listRes = await fetch(`${WORLD_BASE}/mcp`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "tools/list", params: {} }),
});
if (!listRes.ok) {
  console.error(`world server not reachable at ${WORLD_BASE} (start it first: cd world/blobfish-wave6/package/sbx_291042075d7547f4 && PORT=8971 python3 server.py)`);
  process.exit(1);
}
const listed = (await listRes.json()).result.tools;

// Normalize exactly as mcp/lib/world-upstream.mjs does before exposing tools —
// raw world.json ships a few distilled-schema defects (duplicate `required`
// entries, null `properties`) that the MCP layer repairs. Probing raw schemas
// would measure those defects instead of the provider's tool-count ceiling.
function normSchema(s) {
  if (!s || typeof s !== "object" || Array.isArray(s)) return { type: "object", properties: {} };
  let out;
  if (s.type === "object") out = { properties: {}, ...s };
  else if (s.properties) out = { ...s, type: "object" };
  else return { type: "object", properties: {} };
  if (!out.properties || typeof out.properties !== "object") out.properties = {};
  if (Array.isArray(out.required)) out.required = [...new Set(out.required)];
  return out;
}
const ALL_TOOLS = listed
  .filter((t) => !["verify_task", "reset_session"].includes(t.name))
  .map((t) => ({
    type: "function",
    function: {
      name: (t.name.includes(".") ? t.name.split(".").join("__") : t.name),
      description: t.description,
      parameters: normSchema(t.inputSchema),
    },
  }));
const MIN = Number(opt("--min", "100"));
const MODELS = opt("--models", "grok-4.5,grok-4.3,claude-sonnet-5,claude-haiku-4-5-20251001,deepseek-v4-pro,deepseek-v4-flash").split(",");

const KEY_BY_PROVIDER = { xai: "XAI_API_KEY", anthropic: "ANTHROPIC_API_KEY", deepseek: "DEEPSEEK_API_KEY" };

async function tryN(model, spec, provider, n) {
  const base = provider.baseUrl.replace(/\/$/, "");
  const url = base.endsWith("/v1") ? `${base}/chat/completions` : `${base}/v1/chat/completions`;
  const key = env[KEY_BY_PROVIDER[spec.provider]];
  if (!key) return { ok: false, error: `no key (${KEY_BY_PROVIDER[spec.provider]})`, fatal: true };
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        model: spec.apiModel ?? model,
        messages: [{ role: "user", content: "Reply with the single word ok. Do not call tools." }],
        max_tokens: 4,
        tools: ALL_TOOLS.slice(0, n),
      }),
      signal: AbortSignal.timeout(120000),
    });
    if (res.ok) return { ok: true };
    const text = (await res.text()).slice(0, 300);
    return { ok: false, error: `${res.status}: ${text}` };
  } catch (e) {
    return { ok: false, error: String(e.message ?? e) };
  }
}

const results = [];
for (const model of MODELS) {
  const spec = roster.models?.[model] ?? roster[model];
  if (!spec) { console.log(`${model.padEnd(32)} NOT IN ROSTER`); continue; }
  const provider = roster.providers[spec.provider];
  process.stdout.write(`${model.padEnd(32)} probing full surface (${ALL_TOOLS.length})… `);
  const full = await tryN(model, spec, provider, ALL_TOOLS.length);
  if (full.ok) {
    console.log(`ACCEPTS ALL ${ALL_TOOLS.length}`);
    results.push({ model, provider: spec.provider, ceiling: `>=${ALL_TOOLS.length}`, note: "accepts full densified surface" });
    continue;
  }
  if (full.fatal) { console.log(full.error); results.push({ model, provider: spec.provider, ceiling: null, note: full.error }); continue; }
  console.log(`REJECTED — ${full.error.slice(0, 120)}`);
  // binary search the ceiling
  let lo = MIN, hi = ALL_TOOLS.length, best = null;
  const loRes = await tryN(model, spec, provider, lo);
  if (!loRes.ok) { results.push({ model, provider: spec.provider, ceiling: `<${MIN}`, note: loRes.error.slice(0, 160) }); console.log(`  ceiling < ${MIN}`); continue; }
  best = lo;
  while (lo + 1 < hi) {
    const mid = Math.floor((lo + hi) / 2);
    const r = await tryN(model, spec, provider, mid);
    process.stdout.write(`  n=${mid} ${r.ok ? "ok" : "reject"}\n`);
    if (r.ok) { best = mid; lo = mid; } else hi = mid;
  }
  console.log(`  → max tools accepted: ${best}`);
  results.push({ model, provider: spec.provider, ceiling: best, note: full.error.slice(0, 160) });
}

console.log("\n=== max tools per request ===");
for (const r of results) console.log(`${r.model.padEnd(32)} ${String(r.ceiling).padEnd(10)} ${r.note ?? ""}`.trim());
console.log(`\nDensified wave-6 surface: ${ALL_TOOLS.length} tools`);
