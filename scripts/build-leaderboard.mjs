#!/usr/bin/env node
/**
 * Multi-model leaderboard page (Harvey LAB-AA-style presentation, VCode-verified data).
 * Reads data/flake/lb-w5-<model>.json (state-verified workflow tasks) and
 * data/flake/lb-arena-<model>.json (CRMArena-style analytics Q&A), plus
 * config/model-roster.json for display names and verified pricing.
 * Writes dashboard/leaderboard.html. Missing model files are skipped, so the page
 * can be rebuilt mid-sweep.
 */
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const roster = JSON.parse(readFileSync(join(ROOT, "config", "model-roster.json"), "utf8"));

const rows = [];
for (const [id, m] of Object.entries(roster.models)) {
  const wPath = join(ROOT, "data", "flake", `lb-w5-${id}.json`);
  const aPath = join(ROOT, "data", "flake", `lb-arena-${id}.json`);
  if (!existsSync(wPath) && !existsSync(aPath)) continue;
  const w = existsSync(wPath) ? JSON.parse(readFileSync(wPath, "utf8")) : null;
  const a = existsSync(aPath) ? JSON.parse(readFileSync(aPath, "utf8")) : null;

  const row = { id, name: m.displayName ?? id, provider: m.provider, pricing: m.pricing ?? null };
  if (w) {
    const trials = w.trialsRaw.filter((t) => !t.infraError);
    row.worldTasks = w.totals.tasks;
    row.worldStrict = w.totals.solidPass / w.totals.tasks;
    row.worldTrial = trials.length ? trials.filter((t) => t.passed).length / trials.length : 0;
    // Audited strict (2026-08-10): required_workflow_path demands a tool order
    // documented nowhere the agent can read — trials whose ONLY failure is that
    // assertion count as passes. End-state and collateral assertions still bind.
    const exPath = {};
    for (const t of trials) {
      const fc = new Set(t.failedConditions ?? []);
      const ok = t.passed || (fc.size > 0 && [...fc].every((c) => c === "required_workflow_path"));
      (exPath[t.taskId] ??= []).push(ok);
    }
    row.worldAudited = Object.values(exPath).filter((v) => v.every(Boolean)).length / w.totals.tasks;
    row.flaky = w.totals.flaky;
    row.infraErrors = w.totals.infraErrors;
    row.worldCost = w.totals.costUsd;
    row.costPerTask = w.totals.costUsd / w.totals.tasks;
    row.avgCalls = trials.length ? trials.reduce((s, t) => s + (t.toolCalls ?? 0), 0) / trials.length : 0;
    row.promptTok = trials.reduce((s, t) => s + (t.usage?.prompt ?? 0), 0);
    row.compTok = trials.reduce((s, t) => s + (t.usage?.completion ?? 0), 0);
    row.depthCurve = w.depthCurve;
    row.failures = {};
    for (const t of trials) for (const c of t.failedConditions ?? []) row.failures[c] = (row.failures[c] ?? 0) + 1;
    row.perTask = Object.fromEntries(w.tasks.map((t) => [t.taskId, { passes: t.passes, trials: t.trials, cls: t.class }]));
  }
  if (a) {
    const at = a.tasks ?? [];
    const passes = at.reduce((s, t) => s + t.passes, 0);
    const trials = at.reduce((s, t) => s + t.trials, 0);
    row.arenaAcc = trials ? passes / trials : null;
    row.arenaCost = a.costUsd ?? 0;
    row.arenaPerTask = Object.fromEntries(at.map((t) => [t.taskId, `${t.passes}/${t.trials}`]));
  }
  rows.push(row);
}
rows.sort((x, y) => (y.worldAudited ?? y.worldStrict ?? -1) - (x.worldAudited ?? x.worldStrict ?? -1) || (y.arenaAcc ?? -1) - (x.arenaAcc ?? -1));

const pct = (v) => (v === null || v === undefined ? "—" : (v * 100).toFixed(1) + "%");
const money = (v) => (v === null || v === undefined ? "—" : "$" + v.toFixed(2));
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");

// union of failure conditions, ranked by total count
const failCounts = {};
for (const r of rows) for (const [c, n] of Object.entries(r.failures ?? {})) failCounts[c] = (failCounts[c] ?? 0) + n;
const failCols = Object.entries(failCounts).sort((a, b) => b[1] - a[1]).map(([c]) => c).slice(0, 8);

// union of world task ids (stable order)
const taskIds = [...new Set(rows.flatMap((r) => Object.keys(r.perTask ?? {})))].sort();

function barChart(rowsIn, valueOf, { fmt = pct, color = "#2563eb" } = {}) {
  const max = Math.max(...rowsIn.map((r) => valueOf(r) ?? 0), 0.0001);
  return `<div class="bars">` + rowsIn.map((r) => {
    const v = valueOf(r);
    const wPct = v === null || v === undefined ? 0 : (v / max) * 100;
    return `<div class="barrow"><div class="blabel">${esc(r.name)}</div><div class="btrack"><div class="bfill" style="width:${wPct}%;background:${color}"></div></div><div class="bval">${fmt(v)}</div></div>`;
  }).join("") + `</div>`;
}

function scatterSvg(rowsIn) {
  const pts = rowsIn.filter((r) => r.costPerTask && r.worldStrict !== undefined);
  if (!pts.length) return "<p>(no data yet)</p>";
  const W = 720, H = 380, P = 55;
  const xs = pts.map((p) => Math.log10(p.costPerTask));
  const xmin = Math.min(...xs) - 0.15, xmax = Math.max(...xs) + 0.15;
  const X = (c) => P + ((Math.log10(c) - xmin) / (xmax - xmin)) * (W - 2 * P);
  const Y = (v) => H - P - v * (H - 2 * P);
  const provColor = { xai: "#0ea5e9", anthropic: "#d97706", deepseek: "#7c3aed" };
  let dots = "";
  for (const p of pts) {
    dots += `<circle cx="${X(p.costPerTask).toFixed(1)}" cy="${Y(p.worldStrict).toFixed(1)}" r="7" fill="${provColor[p.provider] ?? "#334155"}" opacity="0.85"/>` +
      `<text x="${(X(p.costPerTask) + 10).toFixed(1)}" y="${(Y(p.worldStrict) + 4).toFixed(1)}" font-size="11" fill="#334155">${esc(p.name)}</text>`;
  }
  let axes = `<line x1="${P}" y1="${H - P}" x2="${W - P}" y2="${H - P}" stroke="#94a3b8"/><line x1="${P}" y1="${P}" x2="${P}" y2="${H - P}" stroke="#94a3b8"/>`;
  for (const v of [0, 0.25, 0.5, 0.75, 1]) {
    axes += `<text x="${P - 8}" y="${Y(v) + 4}" font-size="10" text-anchor="end" fill="#64748b">${v * 100}%</text><line x1="${P}" x2="${W - P}" y1="${Y(v)}" y2="${Y(v)}" stroke="#e2e8f0"/>`;
  }
  for (const c of [0.05, 0.1, 0.25, 0.5, 1, 2, 5]) {
    if (Math.log10(c) < xmin || Math.log10(c) > xmax) continue;
    axes += `<text x="${X(c)}" y="${H - P + 16}" font-size="10" text-anchor="middle" fill="#64748b">$${c}</text>`;
  }
  return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Pass rate vs cost per task">${axes}${dots}` +
    `<text x="${W / 2}" y="${H - 12}" font-size="11" text-anchor="middle" fill="#475569">cost per task (USD, log scale)</text></svg>`;
}

const failMatrix = `<table><thead><tr><th>Model</th>${failCols.map((c) => `<th class="rot"><span>${esc(c)}</span></th>`).join("")}</tr></thead><tbody>` +
  rows.map((r) => `<tr><td>${esc(r.name)}</td>${failCols.map((c) => { const n = r.failures?.[c] ?? 0; return `<td class="${n ? "hit" : ""}">${n || ""}</td>`; }).join("")}</tr>`).join("") +
  `</tbody></table>`;

const taskMatrix = `<table><thead><tr><th>Task</th>${rows.map((r) => `<th class="rot"><span>${esc(r.name)}</span></th>`).join("")}</tr></thead><tbody>` +
  taskIds.map((tid) => `<tr><td>${tid}</td>${rows.map((r) => { const t = r.perTask?.[tid]; if (!t) return "<td>—</td>"; const cls = t.cls === "pass" ? "ok" : t.cls === "FLAKY" ? "flaky" : "bad"; return `<td class="${cls}">${t.passes}/${t.trials}</td>`; }).join("")}</tr>`).join("") +
  `</tbody></table>`;

const mainTable = `<table><thead><tr><th>#</th><th>Model</th><th>Provider</th><th>Workflow (audited)<br><span class="sub">ex undocumented-path</span></th><th>Workflow strict<br><span class="sub">all assertions</span></th><th>Arena Q&amp;A<br><span class="sub">corrected GT</span></th><th>Avg calls</th><th>Cost/task</th><th>Run cost</th><th>$/M in·out</th></tr></thead><tbody>` +
  rows.map((r, i) => `<tr><td>${i + 1}</td><td><b>${esc(r.name)}</b></td><td>${r.provider}</td><td><b>${pct(r.worldAudited)}</b>${r.flaky ? ` <span class="sub">(${r.flaky} flaky)</span>` : ""}</td><td>${pct(r.worldStrict)}</td><td>${pct(r.arenaAcc)}</td><td>${r.avgCalls?.toFixed(1) ?? "—"}</td><td>${money(r.costPerTask)}</td><td>${money((r.worldCost ?? 0) + (r.arenaCost ?? 0))}</td><td>${r.pricing ? `$${r.pricing.input}·$${r.pricing.output}` : "—"}</td></tr>`).join("") +
  `</tbody></table>`;

const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CRM Agent Leaderboard — Morgan Stanley (SIMULATED) world</title>
<style>
body{font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;color:#0f172a;background:#f8fafc;margin:0;padding:32px;max-width:1080px;margin-inline:auto}
h1{font-size:26px;margin:0 0 6px}h2{font-size:19px;margin:34px 0 10px;border-bottom:2px solid #e2e8f0;padding-bottom:6px}
.sub{color:#64748b;font-size:12px;font-weight:400}
table{border-collapse:collapse;width:100%;font-size:13.5px;background:#fff}
th,td{border:1px solid #e2e8f0;padding:6px 9px;text-align:left}
th{background:#f1f5f9}
td.ok{background:#dcfce7}td.flaky{background:#fef9c3}td.bad{background:#fee2e2}td.hit{background:#fee2e2;text-align:center}
th.rot{height:120px;white-space:nowrap;vertical-align:bottom}th.rot span{writing-mode:vertical-rl;transform:rotate(180deg);font-size:11px}
.bars{margin:10px 0}.barrow{display:flex;align-items:center;gap:8px;margin:4px 0}
.blabel{width:170px;font-size:13px;text-align:right}.btrack{flex:1;background:#e2e8f0;height:20px;border-radius:3px}.bfill{height:100%;border-radius:3px}
.bval{width:60px;font-size:13px;font-weight:600}
.note{background:#eff6ff;border-left:4px solid #2563eb;padding:10px 14px;font-size:13.5px;margin:14px 0}
svg{max-width:100%;height:auto;background:#fff;border:1px solid #e2e8f0}
.toggle button{margin-right:6px;padding:4px 12px;border:1px solid #cbd5e1;background:#fff;border-radius:5px;cursor:pointer}
.toggle button.on{background:#2563eb;color:#fff;border-color:#2563eb}
</style></head><body>
<h1>CRM Agent Leaderboard</h1>
<p class="sub">Morgan Stanley (SIMULATED) revenue-operations world · blobfish.ai-generated, VCode state-verified · wave-5 hardened task set (17 tasks × 2 trials) + CRMArena-style analytics arena (6 tasks × 2 trials) · generated ${new Date().toISOString().slice(0, 10)}</p>

<div class="note"><b>How to read this.</b> <b>Workflow (audited)</b> is the primary metric: strict all-trials-pass on the world's VCode verifiers, after the 2026-08-10 audit reclassified <code>required_workflow_path</code> on task_008/task_012 as an environment artifact (the mandated tool order is documented nowhere an agent can read — all 7 models failed it 0/2). End-state, policy, and collateral assertions still bind. <b>Arena Q&amp;A</b> uses the corrected handle_time ground truth (original GT was computed pre-near-tie-injection over a degenerate window; three models had found the true answer and were scored wrong). Verification is deterministic program checks on final DB state + tool trace — no LLM judge.</div>

<h2>Leaderboard</h2>
${mainTable}

<h2>Workflow pass rate <span class="sub toggle"><button class="on" onclick="tg(this,'strict')">audited</button><button onclick="tg(this,'lenient')">official strict</button></span></h2>
<div id="c-strict">${barChart(rows, (r) => r.worldAudited)}</div>
<div id="c-lenient" style="display:none">${barChart(rows, (r) => r.worldStrict, { color: "#0891b2" })}</div>

<h2>Arena analytics accuracy</h2>
${barChart(rows, (r) => r.arenaAcc, { color: "#d97706" })}

<h2>Pass rate vs cost per task</h2>
${scatterSvg(rows)}

<h2>Per-task matrix (passes/trials)</h2>
${taskMatrix}

<h2>Failure-condition matrix (failed VCode assertions, count across trials)</h2>
${failMatrix}

<h2>Methodology</h2>
<ul style="font-size:13.5px">
<li>World: blobfish deep world <code>sbx_36847f702cef4cb4</code> (49 tables / 171 tools / wave-5 hardening: conflicting SOP versions, conditional rules, entity collisions). Sessions are copy-on-write SQLite; every trial runs in a fresh session.</li>
<li>Task set: 15 wave-5 frontier tasks + 2 procedure-following probes (task_008, task_012 — tasks with a mandated <code>required_workflow_path</code>). Turn budget is reference-relative: max(24, 3×reference-walk + 6).</li>
<li>Scoring: the world's own VCode verifiers — deterministic Python <code>verify(initial_state, final_state, trace)</code> asserting state deltas, read-before-write, no off-task/undeclared writes, append-only audit logs, and (where mandated) workflow path. No LLM judge anywhere in scoring.</li>
<li>Arena: 6 CRMArena-style tasks (case routing, top issue, handle time, BANT lead qualification, policy violation, entity disambiguation) at level-2 hardening (near-ties, superseded policies, decoys), exact/fuzzy/set match, flat 16-turn cap.</li>
<li>Models called through each provider's native OpenAI-compatible endpoint, identical prompts and tool schemas (dotted MCP names mangled to API-safe form uniformly for all providers). Pricing from provider price pages, verified 2026-08-09.</li>
</ul>
<script>function tg(btn,which){document.querySelectorAll('.toggle button').forEach(b=>b.classList.remove('on'));btn.classList.add('on');document.getElementById('c-strict').style.display=which==='strict'?'':'none';document.getElementById('c-lenient').style.display=which==='lenient'?'':'none'}</script>
</body></html>`;

const out = join(ROOT, "dashboard", "leaderboard.html");
writeFileSync(out, html);
console.log(`leaderboard: ${rows.length} models -> ${out}`);
for (const r of rows) console.log(`  ${r.name}: strict=${pct(r.worldStrict)} lenient=${pct(r.worldTrial)} arena=${pct(r.arenaAcc)} cost=${money((r.worldCost ?? 0) + (r.arenaCost ?? 0))}`);
