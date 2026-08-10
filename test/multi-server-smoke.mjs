#!/usr/bin/env node
/**
 * No-LLM smoke test for the per-vendor MCP topology against a running local
 * world server. Boots every vendor server + harness on a shared session,
 * checks tool counts, exercises one read tool and one cross-server visibility
 * write path is NOT tested here (covered by run-simulation --multi-server).
 *
 * Usage: BLOBFISH_LOCAL=1 BLOBFISH_LOCAL_BASE=http://127.0.0.1:8979 node test/multi-server-smoke.mjs
 */
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { McpClient } from "../sim/lib/mcp-client.mjs";
import { WorldUpstream } from "../mcp/lib/world-upstream.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const registry = JSON.parse(readFileSync(join(ROOT, "config", "mcp-servers.json"), "utf8"));
const vendors = Object.keys(registry.vendors);

let pass = 0, fail = 0;
const check = (name, ok, detail = "") => { (ok ? pass++ : fail++); console.log(`${ok ? "ok " : "FAIL"} ${name}${detail ? " — " + detail : ""}`); };

const epDir = join(ROOT, "sim", "logs", ".mcp-episodes", `smoke-${Date.now()}`);
mkdirSync(epDir, { recursive: true });
const up = new WorldUpstream({ clientName: "smoke" });
await up.attachSession();
writeFileSync(join(epDir, "session.json"), JSON.stringify({ session_id: up.session }));
writeFileSync(join(epDir, "trace.jsonl"), "");
const env = { BLOBFISH_SESSION_FILE: join(epDir, "session.json"), BLOBFISH_TRACE_FILE: join(epDir, "trace.jsonl") };

const clients = {};
let total = 0;
for (const v of vendors) {
  const c = new McpClient("node", ["mcp/vendor-server.mjs", "--vendor", v], { cwd: ROOT, env });
  const init = await c.start();
  const tools = await c.listTools();
  clients[v] = c;
  total += tools.length;
  check(`${v} boots as its own MCP server`, init.serverInfo.name === v, `${tools.length} tools`);
  check(`${v} exposes bare tool names`, tools.every((t) => !t.name.includes(".")));
}
check("aggregate tool surface matches world (205)", total === 205, String(total));

const harness = new McpClient("node", ["mcp/harness-server.mjs"], { cwd: ROOT, env });
const hi = await harness.start();
check("harness server boots", hi.serverInfo.name === "eval-harness");
const htools = await harness.listTools();
check("harness exposes only verify/reset", htools.length === 2);

// one read through a vendor server records into the shared trace
const sf = clients["salesforce-crm"];
const r = await sf.callTool("accounts_list", { limit: 2 }, 30000);
check("salesforce-crm accounts_list executes", r.ok);
const trace = readFileSync(env.BLOBFISH_TRACE_FILE, "utf8").trim().split("\n").filter(Boolean);
check("shared trace recorded the call", trace.length === 1 && JSON.parse(trace[0]).tool === "accounts_list");

// verify runs against the merged trace (any task id; just needs a JSON verdict)
const v = await harness.callTool("verify_task", { task_id: "task_016" }, 60000);
check("harness verify_task returns a verdict", v.text.includes('"passed"'));

for (const c of Object.values(clients)) c.close();
harness.close();
await new Promise((r2) => setTimeout(r2, 300));
await up.releaseSession();

console.log(`\n${pass} ok, ${fail} failed`);
process.exit(fail ? 1 : 0);
