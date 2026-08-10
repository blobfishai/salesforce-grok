#!/usr/bin/env node
/**
 * Cross-model failure-mode report. Groups every failed VCode assertion across the
 * leaderboard sweep (data/flake/lb-w5-*.json) into named failure modes, shows the
 * model x mode matrix, per-mode real transcript excerpts, and per-model depth curves.
 * Writes dashboard/failure-report-models.html.
 */
import { readFileSync, writeFileSync, readdirSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const roster = JSON.parse(readFileSync(join(ROOT, "config", "model-roster.json"), "utf8"));
const name = (id) => roster.models[id]?.displayName ?? id;

const MODES = [
  { key: "procedure", label: "Procedure defiance", desc: "Ignores the mandated SOP tool path (required_workflow_path): reaches a plausible end-state its own way, or writes without the required review chain.", match: (c) => c === "required_workflow_path" },
  { key: "offtask", label: "Off-task writes", desc: "Mutates tables unrelated to the task (no_offtask_table_changes / no_collateral_*): the collateral-damage signature that grows with tool-call depth.", match: (c) => c === "no_offtask_table_changes" || c.startsWith("no_collateral") },
  { key: "undeclared", label: "Undeclared row creation", desc: "Inserts rows the task never asked for (no_undeclared_rows_created) — usually 'helpful' extra logging or duplicate records.", match: (c) => c === "no_undeclared_rows_created" },
  { key: "wrongstate", label: "Wrong end-state", desc: "The targeted record does not end in the required state (missing status transition, missing insert, or no state change at all).", match: (c) => /_status_is_|rows_inserted_into_|^state_changed$|_is_approved|_is_pending/.test(c) },
  { key: "shortcut", label: "Shortcutting", desc: "Writes without reading first, or direct-update bypass of the declared lifecycle (reads_before_writes / no_shortcut_direct_update).", match: (c) => c === "reads_before_writes" || c === "no_shortcut_direct_update" },
  { key: "toolerr", label: "Unrecovered tool errors", desc: "Finished with failed tool calls it never retried (all_tools_succeeded) — the world injects recoverable friction errors on purpose.", match: (c) => c === "all_tools_succeeded" },
  { key: "audit", label: "Audit tampering", desc: "Mutated or deleted append-only audit rows (audit_logs_append_only / no_rows_destroyed).", match: (c) => c === "audit_logs_append_only" || c === "no_rows_destroyed" },
];
const classify = (c) => MODES.find((m) => m.match(c))?.key ?? "other";

const files = readdirSync(join(ROOT, "data", "flake")).filter((f) => f.startsWith("lb-w5-") && f.endsWith(".json"));
const models = [];
for (const f of files) {
  const d = JSON.parse(readFileSync(join(ROOT, "data", "flake", f), "utf8"));
  const id = d.model;
  const trials = d.trialsRaw.filter((t) => !t.infraError);
  const modeCounts = {};
  const exemplars = {};
  for (const t of trials) {
    const seen = new Set((t.failedConditions ?? []).map(classify));
    for (const m of seen) {
      modeCounts[m] = (modeCounts[m] ?? 0) + 1;
      if (!exemplars[m] && t.log) exemplars[m] = t;
    }
  }
  models.push({ id, name: name(id), depthCurve: d.depthCurve, totals: d.totals, modeCounts, exemplars, trials });
}
models.sort((a, b) => b.totals.solidPass - a.totals.solidPass);

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");

/** Pull an illustrative excerpt (last 3 tool calls + final answer) from a run transcript. */
function excerpt(trial) {
  try {
    if (!trial?.log || !existsSync(trial.log)) return null;
    const lines = readFileSync(trial.log, "utf8").trim().split("\n").map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
    const tools = lines.filter((l) => l.type === "tool").slice(-3);
    const fin = lines.filter((l) => l.type === "final").at(-1);
    let out = tools.map((t) => `→ ${t.name}(${JSON.stringify(t.args).slice(0, 140)})\n   ${String(t.result).replace(/\s+/g, " ").slice(0, 180)}`).join("\n");
    if (fin) out += `\n■ final: ${String(fin.content).replace(/\s+/g, " ").slice(0, 260)}`;
    return out || null;
  } catch { return null; }
}

const activeModes = MODES.filter((m) => models.some((x) => x.modeCounts[m.key]));

const matrix = `<table><thead><tr><th>Model</th>${activeModes.map((m) => `<th>${m.label}</th>`).join("")}<th>Trials failed / run</th></tr></thead><tbody>` +
  models.map((x) => {
    const failed = x.trials.filter((t) => !t.passed).length;
    return `<tr><td><b>${esc(x.name)}</b></td>${activeModes.map((m) => { const n = x.modeCounts[m.key] ?? 0; return `<td class="${n ? "hit" : ""}">${n || ""}</td>`; }).join("")}<td>${failed} / ${x.trials.length}</td></tr>`;
  }).join("") + `</tbody></table>`;

const modeSections = activeModes.map((m) => {
  const hitModels = models.filter((x) => x.modeCounts[m.key]);
  const ex = hitModels.map((x) => ({ x, e: x.exemplars[m.key] })).find((p) => p.e && excerpt(p.e));
  const exHtml = ex ? `<div class="ex"><div class="exhead">${esc(ex.x.name)} · ${ex.e.taskId} · ${ex.e.toolCalls} tool calls · failed: ${(ex.e.failedConditions ?? []).join(", ")}</div><pre>${esc(excerpt(ex.e))}</pre></div>` : "";
  return `<h3>${m.label}</h3><p>${m.desc}</p><p class="sub">Hit by: ${hitModels.map((x) => `${esc(x.name)} (${x.modeCounts[m.key]})`).join(" · ") || "none"}</p>${exHtml}`;
}).join("");

const depth = `<table><thead><tr><th>Model</th><th>1-5 calls</th><th>6-10</th><th>11-20</th><th>21+</th></tr></thead><tbody>` +
  models.map((x) => `<tr><td>${esc(x.name)}</td>${x.depthCurve.map((d) => `<td>${d.passRate === null ? "—" : (d.passRate * 100).toFixed(0) + "%"} <span class="sub">(${d.trials})</span></td>`).join("")}</tr>`).join("") +
  `</tbody></table>`;

const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Failure modes across models — Morgan Stanley (SIMULATED) world</title>
<style>
body{font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;color:#0f172a;background:#f8fafc;margin:0;padding:32px;max-width:1000px;margin-inline:auto}
h1{font-size:25px;margin:0 0 6px}h2{font-size:19px;margin:32px 0 10px;border-bottom:2px solid #e2e8f0;padding-bottom:6px}h3{font-size:16px;margin:24px 0 4px}
.sub{color:#64748b;font-size:12.5px}
table{border-collapse:collapse;width:100%;font-size:13.5px;background:#fff}
th,td{border:1px solid #e2e8f0;padding:6px 9px;text-align:left}th{background:#f1f5f9}
td.hit{background:#fee2e2;text-align:center;font-weight:600}
.ex{background:#0f172a;color:#e2e8f0;border-radius:8px;margin:10px 0;overflow:hidden}
.exhead{background:#1e293b;padding:7px 12px;font-size:12.5px;color:#94a3b8}
pre{margin:0;padding:12px;font:12px/1.5 ui-monospace,Menlo,monospace;white-space:pre-wrap;overflow-x:auto}
.note{background:#eff6ff;border-left:4px solid #2563eb;padding:10px 14px;font-size:13.5px;margin:14px 0}
</style></head><body>
<h1>Failure modes across models</h1>
<p class="sub">Every failed VCode assertion in the leaderboard sweep, grouped into named modes · deterministic verification, no LLM judge · generated ${new Date().toISOString().slice(0, 10)}</p>
<div class="note">A trial counts once per mode it hit (one trial can hit several modes). Excerpts are the last tool calls + final answer from a real failing transcript.</div>
<h2>Model × failure-mode matrix</h2>
${matrix}
<h2>The modes</h2>
${modeSections}
<h2>Depth curves — pass rate vs tool-call count</h2>
<p class="sub">The wave-5 finding for grok-4.5 was a cliff at 11+ calls; this table shows where each model's cliff sits.</p>
${depth}
</body></html>`;

writeFileSync(join(ROOT, "dashboard", "failure-report-models.html"), html);
console.log(`failure report: ${models.length} models, ${activeModes.length} active modes -> dashboard/failure-report-models.html`);
