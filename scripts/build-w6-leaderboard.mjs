#!/usr/bin/env node
/**
 * Wave-6 leaderboard report: every model swept on the wave-6 world
 * (data/flake/w6-*.json), scored three ways:
 *   official  — all VCode assertions bind, 25-task denominator
 *   valid     — the 23 non-broken tasks (task_001/002 excluded: confirmed
 *               unresolvable-referent / wrong-row-verifier environment bugs)
 *   audited   — valid set with required_workflow_path advisory (undocumented order)
 * Plus per-task matrix, depth curves, and cost. -> dashboard/w6-leaderboard.html
 */
import { readFileSync, writeFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const roster = JSON.parse(readFileSync(join(ROOT, "config", "model-roster.json"), "utf8"));
const dispName = (id) => roster.models[id]?.displayName ?? id;
const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;");
const BROKEN = new Set(["task_001", "task_002"]);

const files = readdirSync(join(ROOT, "data", "flake")).filter((f) => /^w6-.*\.json$/.test(f));
const models = [];
for (const f of files) {
  const d = JSON.parse(readFileSync(join(ROOT, "data", "flake", f), "utf8"));
  const trials = d.trialsRaw.filter((t) => !t.infraError);
  const per = {};
  for (const t of trials) {
    const fc = new Set(t.failedConditions ?? []);
    (per[t.taskId] ??= []).push({
      passed: t.passed,
      audited: t.passed || (fc.size > 0 && [...fc].every((c) => c === "required_workflow_path")),
      calls: t.toolCalls ?? 0,
    });
  }
  const allIds = Object.keys(per);
  const validIds = allIds.filter((id) => !BROKEN.has(id));
  const nOff = allIds.length, nVal = validIds.length;
  const passTask = (ids, k) => ids.filter((id) => per[id].every((x) => x[k])).length;
  models.push({
    id: d.model, name: dispName(d.model), label: d.label,
    official: passTask(allIds, "passed") / nOff, nOff,
    valid: passTask(validIds, "passed") / nVal,
    audited: passTask(validIds, "audited") / nVal, nVal,
    trialsAudited: validIds.flatMap((id) => per[id]).filter((x) => x.audited).length,
    trialsTotal: validIds.flatMap((id) => per[id]).length,
    cost: d.totals.costUsd,
    avgCalls: trials.length ? +(trials.reduce((s, t) => s + (t.toolCalls ?? 0), 0) / trials.length).toFixed(1) : 0,
    depth: d.depthCurve,
    per,
  });
}
models.sort((a, b) => b.audited - a.audited);

const pct = (v) => (v * 100).toFixed(1) + "%";
const taskIds = [...new Set(models.flatMap((m) => Object.keys(m.per)))].sort();

const main = `<table><thead><tr><th>Model</th><th class="num">Audited (23 valid)</th><th class="num">Valid strict</th><th class="num">Official (25)</th><th class="num">Audited trials</th><th class="num">Avg calls</th><th class="num">Run cost</th><th class="num">$ / task</th></tr></thead><tbody>` +
  models.map((m, i) => `<tr${i === 0 ? ' class="lead"' : ""}><td><b>${esc(m.name)}</b></td><td class="num"><b>${pct(m.audited)}</b></td><td class="num">${pct(m.valid)}</td><td class="num">${pct(m.official)}</td><td class="num">${m.trialsAudited}/${m.trialsTotal}</td><td class="num">${m.avgCalls}</td><td class="num">$${m.cost.toFixed(2)}</td><td class="num">$${(m.cost / m.nOff).toFixed(2)}</td></tr>`).join("") + `</tbody></table>`;

const matrix = `<table><thead><tr><th>Task</th>${models.map((m) => `<th class="num">${esc(m.name)}</th>`).join("")}<th>Reading</th></tr></thead><tbody>` +
  taskIds.map((tid) => {
    const broken = BROKEN.has(tid);
    const cells = models.map((m) => {
      const v = m.per[tid];
      if (!v) return `<td class="num">—</td>`;
      const p = v.filter((x) => x.audited).length;
      const cls = broken ? "" : p === v.length ? "ok" : p === 0 ? "bad" : "flaky";
      return `<td class="${cls}">${p}/${v.length}</td>`;
    }).join("");
    const note = broken ? "EXCLUDED — confirmed environment bug" : "";
    return `<tr${broken ? ' style="opacity:.5"' : ""}><td class="mono">${tid}${broken ? " ✕" : ""}</td>${cells}<td class="sm">${note}</td></tr>`;
  }).join("") + `</tbody></table>`;

const depth = `<table><thead><tr><th>Model</th><th class="num">1-5 calls</th><th class="num">6-10</th><th class="num">11-20</th><th class="num">21+</th></tr></thead><tbody>` +
  models.map((m) => `<tr><td>${esc(m.name)}</td>${m.depth.map((b) => `<td class="num">${b.passRate === null ? "—" : Math.round(b.passRate * 100) + "%"} <span class="sm">(${b.trials})</span>`).join("")}</tr>`).join("") + `</tbody></table>`;

const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wave-6 leaderboard — audited</title>
<style>
body{font:14.5px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;color:#0f172a;background:#f8fafc;margin:0;padding:28px;max-width:1080px;margin-inline:auto}
h1{font-size:23px;margin:0 0 4px}h2{font-size:18px;margin:30px 0 8px;border-bottom:2px solid #e2e8f0;padding-bottom:5px}
.sub{color:#64748b;font-size:12.5px}.sm{font-size:11.5px;color:#64748b}.mono{font-family:ui-monospace,Menlo,monospace}
table{border-collapse:collapse;width:100%;font-size:13px;background:#fff;border:1px solid #e2e8f0;border-radius:8px;overflow:hidden}
th,td{border-top:1px solid #e2e8f0;padding:6px 10px;text-align:left}
thead th{border-top:none;background:#f1f5f9;font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:#64748b}
td.num,th.num{text-align:right;font-family:ui-monospace,Menlo,monospace;font-variant-numeric:tabular-nums}
td.ok{background:#dcfce7;text-align:center}td.bad{background:#fee2e2;text-align:center}td.flaky{background:#fef9c3;text-align:center}
tr.lead td{background:#e4f1ec}
.note{background:#eff6ff;border-left:4px solid #2563eb;padding:9px 13px;font-size:13px;margin:12px 0}
</style></head><body>
<h1>Wave-6 leaderboard — 205-tool world, audited scoring</h1>
<div class="sub">World sbx_291042075d7547f4 · 214 tables / 205 tools / 48 documents · 2 trials per task · generated ${new Date().toISOString().slice(0, 10)}</div>
<div class="note"><b>Audited</b> = 23 valid tasks (task_001/task_002 excluded — trace forensics confirmed an unexpanded {name} template referencing a nonexistent person, and a verifier pinned to a different row than the prompt names) with the undocumented-order assertion advisory. All state, policy, and collateral assertions bind.</div>
${main}
<h2>Per-task matrix (audited passes/trials)</h2>
${matrix}
<h2>Depth curves — pass rate vs tool-call count (official scoring)</h2>
${depth}
</body></html>`;

writeFileSync(join(ROOT, "dashboard", "w6-leaderboard.html"), html);
console.log(`w6-leaderboard: ${models.length} models`);
for (const m of models) console.log(`  ${m.name}: audited=${pct(m.audited)} valid=${pct(m.valid)} official=${pct(m.official)} cost=$${m.cost.toFixed(2)}`);
