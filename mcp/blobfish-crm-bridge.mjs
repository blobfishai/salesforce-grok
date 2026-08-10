#!/usr/bin/env node
/**
 * LEGACY mega-bridge: one MCP server exposing the ENTIRE world tool surface
 * (namespaced names) plus the harness tools. Kept for backwards compatibility
 * with single-server runs and all pre-multi-server results.
 *
 * The realistic topology is one server per vendor — mcp/vendor-server.mjs +
 * mcp/harness-server.mjs via `run-simulation.mjs --multi-server`.
 *
 * Modes:
 *   hosted (default): needs BLOBFISH_API_KEY in .env and blobfish.worldId in config.
 *   local:  set BLOBFISH_LOCAL=1 — targets BLOBFISH_LOCAL_BASE / config localBase.
 * Also honors BLOBFISH_SESSION_FILE / BLOBFISH_TRACE_FILE (shared-episode mode).
 */
import { WorldUpstream, stdioServe } from "./lib/world-upstream.mjs";

const up = new WorldUpstream({ clientName: "blobfish-crm-bridge" });
if (!up.LOCAL && (!up.KEY || !up.WORLD_ID || up.WORLD_ID === "PENDING")) {
  process.stderr.write("[blobfish-bridge] hosted mode needs BLOBFISH_API_KEY and config.blobfish.worldId (or set BLOBFISH_LOCAL=1)\n");
  process.exit(1);
}

const HARNESS_TOOLS = [
  {
    name: "verify_task",
    description: "HARNESS ONLY: score the current world state + rollout trace against a task's ground truth using blobfish's VCode verifier. Call once at the end of a rollout with the task_id.",
    inputSchema: { type: "object", properties: { task_id: { type: "string" } }, required: ["task_id"] },
  },
  {
    name: "reset_session",
    description: "HARNESS ONLY: reset the world session state for a fresh rollout.",
    inputSchema: { type: "object", properties: {} },
  },
];

const TOOLS = await up.boot().catch((e) => {
  process.stderr.write(`[blobfish-bridge] boot failed: ${e.message}\n`);
  process.exit(1);
});
process.stderr.write(`[blobfish-bridge] ${up.LOCAL ? "LOCAL" : "hosted"} world ${up.world.worldId ?? up.WORLD_ID} (${up.world.company ?? "?"}) — ${TOOLS.length} world tools, session ${up.session}\n`);

const clipObs = (s) => (typeof s === "string" && s.length > 4000 ? s.slice(0, 4000) : s);

stdioServe({
  serverInfo: { name: "blobfish-crm-bridge", version: "3.0.0" },
  instructions:
    `Bridge to blobfish world ${up.WORLD_ID} ("${up.world.company ?? "simulated org"}") — a fully synthetic ` +
    `Salesforce-CRM-style simulation (Morgan Stanley (SIMULATED) scenario; no real entities). ` +
    `Tools execute against the ${up.LOCAL ? "locally packaged" : "hosted"} world state. ` +
    `Tools marked HARNESS ONLY are for the evaluation harness, not the agent.`,
  onList: () => [...TOOLS, ...HARNESS_TOOLS],
  onCall: async (name, args) => {
    if (name === "verify_task") {
      const trace = up.readTrace().map(({ vendor, ts, ...rest }) => rest);
      const path = up.LOCAL ? `/verify/${encodeURIComponent(args.task_id)}` : "/verify";
      const body = up.LOCAL ? { trace } : { task_id: args.task_id, trace };
      const r = await up.rest(path, { method: "POST", body: JSON.stringify(body) });
      return { ok: r.ok, text: r.json ? JSON.stringify(r.json, null, 2) : r.text };
    }
    if (name === "reset_session") {
      if (up.LOCAL) await up.rest(`/sessions/${encodeURIComponent(up.session)}`, { method: "DELETE" });
      else await up.rest(`/sessions/${encodeURIComponent(up.session)}/reset`, { method: "GET" });
      const s = await up.rest("/sessions", { method: "POST", body: "{}" });
      up.session = s.json?.session_id ?? up.session;
      up.localTrace.length = 0;
      return { ok: true, text: JSON.stringify({ reset: true, session: up.session }) };
    }
    if (!TOOLS.some((t) => t.name === name)) return { ok: false, text: `Unknown tool '${name}'` };
    const bareName = name.includes(".") ? name.split(".").pop() : name; // verifiers match un-namespaced names
    try {
      const result = await up.mcp("tools/call", { name, arguments: args });
      const obsText = (result?.content ?? []).map((c) => c.text ?? "").join("\n");
      up.recordTrace({ tool: bareName, requested_tool: name, arguments: args, observation: clipObs(obsText), ok: !result?.isError });
      return { raw: result };
    } catch (e) {
      up.recordTrace({ tool: bareName, requested_tool: name, arguments: args, observation: `ERROR: ${e.message}`, ok: false });
      return { ok: false, text: `ERROR: ${e.message}` };
    }
  },
  onClose: () => up.releaseSession(),
});
