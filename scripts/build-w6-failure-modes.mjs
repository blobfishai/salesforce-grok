#!/usr/bin/env node
/**
 * Failure-mode report over ALL failed wave-6 traces, every model swept
 * (data/flake/w6-*.json). Each failed trial is classified from its assertions
 * and transcript:
 *   env_bug       — task_001/002 (confirmed broken by forensics)
 *   artifact_only — only the undocumented-order assertion failed
 *   real          — one or more substantive modes, broken out below
 * Real modes: missing_creation, collateral_writes, wrong_end_state,
 * shortcutting, unrecovered_tool_errors. Also counts budget-exhausted trials
 * (no final answer). Exemplars come from the actual transcripts.
 * -> dashboard/w6-failure-modes.html
 */
import { readFileSync, writeFileSync, readdirSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const roster = JSON.parse(readFileSync(join(ROOT, "config", "model-roster.json"), "utf8"));
const dispName = (id) => roster.models[id]?.displayName ?? id;
const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;");
const BROKEN = new Set(["task_001", "task_002"]);

const MODES = [
  { key: "missing_creation", label: "Missing required creation", match: (c) => c.startsWith("rows_inserted_into"), desc: "The task explicitly demands new records ('Create the required new X record'); the agent explores, narrates, but never creates them — the dominant deep-task failure." },
  { key: "collateral_writes", label: "Collateral writes", match: (c) => c === "no_offtask_table_changes" || c === "no_undeclared_rows_created" || c.startsWith("no_collateral"), desc: "Mutates tables or inserts rows nothing asked for — 'helpful' logging, junk documents via lenient side-effectful tools, duplicate records." },
  { key: "wrong_end_state", label: "Wrong end-state", match: (c) => /_status_is_|^state_changed$/.test(c), desc: "The pinned record does not reach the required status — wrong row, wrong transition, or no write at all." },
  { key: "shortcutting", label: "Shortcutting", match: (c) => c === "reads_before_writes" || c === "no_shortcut_direct_update", desc: "Writes before reading, or bypasses the declared lifecycle with a direct update." },
  { key: "unrecovered_tool_errors", label: "Unrecovered tool errors", match: (c) => c === "all_tools_succeeded", desc: "Finished with failed tool calls never retried; the world injects recoverable friction errors on purpose." },
];

function transcriptFacts(trial) {
  try {
    if (!trial.log || !existsSync(trial.log)) return {};
    const lines = readFileSync(trial.log, "utf8").trim().split("\n").map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
    const fin = lines.filter((l) => l.type === "final").at(-1);
    const tools = lines.filter((l) => l.type === "tool");
    return {
      noFinal: !fin || !String(fin.content ?? "").trim(),
      tail: tools.slice(-3).map((t) => `→ ${t.name}(${JSON.stringify(t.args).slice(0, 100)})\n   ${String(t.result).replace(/\s+/g, " ").slice(0, 130)}`).join("\n"),
      final: fin ? String(fin.content).replace(/\s+/g, " ").slice(0, 220) : "(no final answer — turn budget exhausted)",
    };
  } catch { return {}; }
}

const files = readdirSync(join(ROOT, "data", "flake")).filter((f) => /^w6-.*\.json$/.test(f));
const perModel = [];
for (const f of files) {
  const d = JSON.parse(readFileSync(join(ROOT, "data", "flake", f), "utf8"));
  const failed = d.trialsRaw.filter((t) => !t.infraError && !t.passed);
  const rows = failed.map((t) => {
    const fc = t.failedConditions ?? [];
    const cls = BROKEN.has(t.taskId) ? "env_bug"
      : fc.every((c) => c === "required_workflow_path") ? "artifact_only" : "real";
    const modes = cls === "real" ? MODES.filter((m) => fc.some(m.match)).map((m) => m.key) : [];
    return { ...t, cls, modes, facts: transcriptFacts(t) };
  });
  perModel.push({ model: d.model, name: dispName(d.model), rows, totalTrials: d.trialsRaw.filter((t) => !t.infraError).length });
}
perModel.sort((a, b) => a.name.localeCompare(b.name));

const cnt = (rows, pred) => rows.filter(pred).length;
const summary = `<table><thead><tr><th>Model</th><th class="num">Trials</th><th class="num">Failed</th><th class="num">Env bug</th><th class="num">Artifact only</th><th class="num">Real</th><th class="num">Budget-exhausted</th></tr></thead><tbody>` +
  perModel.map((m) => `<tr><td><b>${esc(m.name)}</b></td><td class="num">${m.totalTrials}</td><td class="num">${m.rows.length}</td><td class="num">${cnt(m.rows, (r) => r.cls === "env_bug")}</td><td class="num">${cnt(m.rows, (r) => r.cls === "artifact_only")}</td><td class="num"><b>${cnt(m.rows, (r) => r.cls === "real")}</b></td><td class="num">${cnt(m.rows, (r) => r.facts.noFinal)}</td></tr>`).join("") + `</tbody></table>`;

const modeMatrix = `<table><thead><tr><th>Real failure mode</th>${perModel.map((m) => `<th class="num">${esc(m.name)}</th>`).join("")}</tr></thead><tbody>` +
  MODES.map((mo) => `<tr><td>${mo.label}</td>${perModel.map((m) => { const n = cnt(m.rows, (r) => r.modes.includes(mo.key)); return `<td class="num ${n ? "hit" : ""}">${n || ""}</td>`; }).join("")}</tr>`).join("") + `</tbody></table>`;

const modeSections = MODES.map((mo) => {
  const hit = perModel.flatMap((m) => m.rows.filter((r) => r.modes.includes(mo.key)).map((r) => ({ m, r })));
  if (!hit.length) return "";
  const ex = hit.find((h) => h.r.facts.tail) ?? hit[0];
  const tasks = [...new Set(hit.map((h) => h.r.taskId))].sort().join(", ");
  return `<h3>${mo.label} — ${hit.length} trials</h3><p class="sub">${mo.desc}<br>Tasks: <span class="mono">${tasks}</span> · Models: ${[...new Set(hit.map((h) => h.m.name))].join(", ")}</p>` +
    (ex.r.facts.tail ? `<div class="ex"><div class="exhead">${esc(ex.m.name)} · ${ex.r.taskId} · ${ex.r.toolCalls} calls · failed: ${esc((ex.r.failedConditions ?? []).slice(0, 4).join(", "))}</div><pre>${esc(ex.r.facts.tail)}\n■ ${esc(ex.r.facts.final)}</pre></div>` : "");
}).join("");

const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wave-6 failure modes — all failed traces</title>
<style>
body{font:14.5px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;color:#0f172a;background:#f8fafc;margin:0;padding:28px;max-width:1060px;margin-inline:auto}
h1{font-size:23px;margin:0 0 4px}h2{font-size:18px;margin:30px 0 8px;border-bottom:2px solid #e2e8f0;padding-bottom:5px}h3{font-size:15.5px;margin:22px 0 4px}
.sub{color:#64748b;font-size:12.5px}.mono{font-family:ui-monospace,Menlo,monospace}
table{border-collapse:collapse;width:100%;font-size:13px;background:#fff;border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;margin:10px 0}
th,td{border-top:1px solid #e2e8f0;padding:6px 10px;text-align:left}
thead th{border-top:none;background:#f1f5f9;font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:#64748b}
td.num,th.num{text-align:right;font-family:ui-monospace,Menlo,monospace}
td.hit{background:#fee2e2;font-weight:600}
.ex{background:#0f172a;color:#e2e8f0;border-radius:8px;margin:8px 0;overflow:hidden}
.exhead{background:#1e293b;padding:6px 12px;font-size:12px;color:#94a3b8}
pre{margin:0;padding:10px;font:11.5px/1.5 ui-monospace,Menlo,monospace;white-space:pre-wrap}
.note{background:#eff6ff;border-left:4px solid #2563eb;padding:9px 13px;font-size:13px;margin:12px 0}
.bug{background:#fef2f2;border-left:4px solid #dc2626;padding:9px 13px;font-size:13px;margin:10px 0}
</style></head><body>
<h1>Wave-6 failure modes — every failed trace, classified</h1>
<div class="sub">World sbx_291042075d7547f4 · classifications from VCode assertions + transcript forensics · turn-by-turn traces: dashboard/failed-traces.html · generated ${new Date().toISOString().slice(0, 10)}</div>

<h2>Where the failures actually come from</h2>
${summary}
<div class="note">A failed trial counts once per bucket; <b>Real</b> is the number that survives the audit (not an environment bug, not the undocumented-order artifact alone). Budget-exhausted = the episode ended with no final answer.</div>

<h2>Confirmed environment bugs (excluded from scoring)</h2>
<div class="bug"><b>task_001 — unresolvable referent.</b> The source matter document contains an unexpanded <span class="mono">{name}</span> template; the prompt says "kofi"; <span class="mono">query_employees({"name":"Kofi"})</span> returns 0 rows and no such person exists in any table. Models search employees → admins → accounts → contacts → sheets for dozens of turns, correctly, for someone the generator never created.</div>
<div class="bug"><b>task_002 — verifier pinned to the wrong row.</b> The prompt names <span class="mono">LEAVE-243410</span> (row 224) and asks for a read+join; the verifier demands row 8 (<span class="mono">LEAVE-857947</span>, a different person's request) be set to <span class="mono">cancelled</span> — a mutation the prompt never requests.</div>

<h2>Real failure modes × model</h2>
${modeMatrix}
${modeSections}
</body></html>`;

writeFileSync(join(ROOT, "dashboard", "w6-failure-modes.html"), html);
console.log(`w6-failure-modes: ${perModel.map((m) => `${m.name}: ${m.rows.length} failed (${cnt(m.rows, (r) => r.cls === "real")} real)`).join(" | ")}`);
