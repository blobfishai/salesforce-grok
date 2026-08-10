#!/usr/bin/env node
/**
 * Harness MCP server — evaluation-only tools, deliberately separate from the
 * vendor servers so the agent's tool surface stays realistic.
 *   verify_task  — POST the MERGED multi-server trace to the world's VCode verifier
 *   reset_session — fresh session + truncated trace (multi-server mode: rewrites
 *                   the shared session file so every vendor server follows)
 */
import { writeFileSync, truncateSync, existsSync } from "node:fs";
import { WorldUpstream, stdioServe } from "./lib/world-upstream.mjs";

const up = new WorldUpstream({ clientName: "mcp-harness" });
await up.attachSession().catch((e) => { process.stderr.write(`[harness] ${e.message}\n`); process.exit(1); });
process.stderr.write(`[harness] session ${up.session}${up.sharedSessionFile ? " (shared)" : ""} — trace ${up.traceFile ?? "(in-memory)"}\n`);

const TOOLS = [
  { name: "verify_task", description: "HARNESS ONLY: score the current world state + merged rollout trace against a task's ground truth (VCode verifier).", inputSchema: { type: "object", properties: { task_id: { type: "string" } }, required: ["task_id"] } },
  { name: "reset_session", description: "HARNESS ONLY: reset world session state for a fresh rollout.", inputSchema: { type: "object", properties: {} } },
];

stdioServe({
  serverInfo: { name: "eval-harness", version: "1.0.0" },
  instructions: "Evaluation harness. Not part of the agent's business tool surface.",
  onList: () => TOOLS,
  onCall: async (name, args) => {
    if (name === "verify_task") {
      const trace = up.readTrace().map(({ vendor, ts, ...rest }) => rest); // verifier shape
      const path = up.LOCAL ? `/verify/${encodeURIComponent(args.task_id)}` : "/verify";
      const body = up.LOCAL ? { trace } : { task_id: args.task_id, trace };
      const r = await up.rest(path, { method: "POST", body: JSON.stringify(body) });
      return { ok: r.ok, text: r.json ? JSON.stringify(r.json, null, 2) : r.text };
    }
    if (name === "reset_session") {
      try { await up.rest(`/sessions/${encodeURIComponent(up.session)}`, { method: "DELETE" }); } catch { /* gone */ }
      const s = await up.rest("/sessions", { method: "POST", body: "{}" });
      if (!s.ok) return { ok: false, text: `session create failed: ${s.status}` };
      up.session = s.json.session_id ?? null;
      if (up.sharedSessionFile) writeFileSync(up.sharedSessionFile, JSON.stringify({ session_id: up.session }));
      if (up.traceFile && existsSync(up.traceFile)) truncateSync(up.traceFile, 0);
      up.localTrace.length = 0;
      return { ok: true, text: JSON.stringify({ reset: true, session: up.session }) };
    }
    return { ok: false, text: `Unknown harness tool '${name}'` };
  },
  onClose: async () => { /* shared sessions belong to the runner */ },
});
