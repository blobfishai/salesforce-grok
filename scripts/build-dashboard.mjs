#!/usr/bin/env node
/**
 * Build dashboard/index.html — a self-contained status page for the simulation world:
 * world stats, grok-4.5 pass/flaky/fail scoreboard (all flake scans merged), the
 * pass-rate-vs-interaction-depth curve, failure taxonomy, and a live rollout excerpt.
 */
import { readFileSync, readdirSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, basename } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

// ------------------------------------------------------------------ load data
const worldRaw = JSON.parse(readFileSync(join(ROOT, "world", "blobfish", "world.json"), "utf8"));
const world = worldRaw.world ?? worldRaw;
const quality = JSON.parse(readFileSync(join(ROOT, "world", "blobfish", "quality.json"), "utf8"));
const models = JSON.parse(readFileSync(join(ROOT, "config", "models.json"), "utf8"));

const flakeDir = join(ROOT, "data", "flake");
const scanFiles = readdirSync(flakeDir).filter((f) => f.endsWith(".json") && !f.startsWith("."));
const scans = scanFiles.map((f) => ({ file: f, ...JSON.parse(readFileSync(join(flakeDir, f), "utf8")) }));

// group scans by worldId => waves
const waves = {};
for (const s of scans) {
  const w = (waves[s.worldId ?? "unknown"] ??= { worldId: s.worldId, labels: [], trials: [] });
  w.labels.push(s.label);
  w.trials.push(...(s.trialsRaw ?? []).filter((t) => !t.infraError));
}
const waveIds = Object.keys(waves);
const primary = waves[world.world_id] ?? waves[waveIds[0]];

// merged per-task stats for a wave
function taskStats(wave, taskMetaById) {
  const byTask = {};
  for (const t of wave.trials) {
    const b = (byTask[t.taskId] ??= { taskId: t.taskId, trials: 0, passes: 0, toolCalls: [], failedConditions: {}, cost: 0, logs: [] });
    b.trials++;
    if (t.passed) b.passes++;
    b.toolCalls.push(t.toolCalls ?? 0);
    b.cost += t.costUsd ?? 0;
    b.logs.push({ log: t.log, passed: t.passed });
    for (const c of t.failedConditions ?? []) b.failedConditions[c] = (b.failedConditions[c] ?? 0) + 1;
  }
  return Object.values(byTask).map((b) => ({
    ...b,
    passRate: b.passes / b.trials,
    cls: b.passes === b.trials ? "pass" : b.passes === 0 ? "fail" : "flaky",
    avgCalls: +(b.toolCalls.reduce((a, c) => a + c, 0) / b.toolCalls.length).toFixed(1),
    difficulty: taskMetaById[b.taskId]?.difficulty_tier ?? null,
    tables: taskMetaById[b.taskId]?.tables_affected ?? [],
  })).sort((a, b) => a.passRate - b.passRate || b.avgCalls - a.avgCalls);
}
const taskMetaById = Object.fromEntries((world.tasks ?? []).map((t) => [t.task_id ?? t.id, t]));
const stats = taskStats(primary, taskMetaById);

// depth buckets across all primary-wave trials
const bucketsDef = [["1–5", 1, 5], ["6–10", 6, 10], ["11–20", 11, 20], ["21+", 21, Infinity]];
const depth = bucketsDef.map(([label, lo, hi]) => {
  const t = primary.trials.filter((x) => (x.toolCalls ?? 0) >= lo && (x.toolCalls ?? 0) <= hi);
  return { label, trials: t.length, passRate: t.length ? t.filter((x) => x.passed).length / t.length : null };
});

// failure taxonomy
const taxonomy = {};
for (const t of primary.trials) for (const c of t.failedConditions ?? []) taxonomy[c] = (taxonomy[c] ?? 0) + 1;
const taxRows = Object.entries(taxonomy).sort((a, b) => b[1] - a[1]).slice(0, 8);

const totals = {
  trials: primary.trials.length,
  cost: +primary.trials.reduce((a, t) => a + (t.costUsd ?? 0), 0).toFixed(2),
  pass: stats.filter((s) => s.cls === "pass").length,
  flaky: stats.filter((s) => s.cls === "flaky").length,
  fail: stats.filter((s) => s.cls === "fail").length,
};
const seededRows = (world.tables ?? []).reduce((a, t) => a + (t.row_count ?? 0), 0);
const grok = models.models["grok-4.5"];

// live rollout excerpt: newest passing trial's log
const passTrial = [...primary.trials].reverse().find((t) => t.passed && existsSync(t.log ?? ""));
let rollout = [];
if (passTrial) {
  const lines = readFileSync(passTrial.log, "utf8").trim().split("\n").map((l) => JSON.parse(l));
  for (const e of lines) {
    if (e.type === "tool") rollout.push({ kind: "tool", name: e.name, args: JSON.stringify(e.args), result: String(e.result).replace(/\s+/g, " ").slice(0, 110) });
    if (e.type === "final") rollout.push({ kind: "final", text: String(e.content).replace(/\s+/g, " ").slice(0, 260) });
    if (e.type === "verify") { const j = JSON.parse(e.result); rollout.push({ kind: "verify", passed: j.passed, n: (j.assertions ?? []).length }); }
  }
  rollout = rollout.slice(0, 12);
}

// ------------------------------------------------------------------ SVG charts
const S1 = "var(--series-1)";
function depthChart() {
  const W = 560, H = 260, padL = 44, padB = 46, padT = 26, padR = 12;
  const plotW = W - padL - padR, plotH = H - padT - padB;
  const bw = Math.min(72, (plotW / depth.length) - 26);
  let bars = "", grid = "", labels = "";
  for (const g of [0, 0.25, 0.5, 0.75, 1]) {
    const y = padT + plotH * (1 - g);
    grid += `<line x1="${padL}" y1="${y}" x2="${W - padR}" y2="${y}" stroke="var(--grid)" stroke-width="1"/>`;
    labels += `<text x="${padL - 8}" y="${y + 4}" text-anchor="end" class="ax">${g * 100}%</text>`;
  }
  depth.forEach((d, i) => {
    const cx = padL + (plotW / depth.length) * (i + 0.5);
    const v = d.passRate ?? 0;
    const h = Math.max(2, plotH * v);
    const y = padT + plotH - h;
    const has = d.trials > 0;
    bars += has
      ? `<rect class="bar" data-tip="${d.label} calls · ${Math.round(v * 100)}% pass · ${d.trials} trials" x="${cx - bw / 2}" y="${y}" width="${bw}" height="${h}" rx="4" fill="${S1}"/>
         <text x="${cx}" y="${y - 7}" text-anchor="middle" class="val">${Math.round(v * 100)}%</text>`
      : `<text x="${cx}" y="${padT + plotH - 8}" text-anchor="middle" class="ax">no trials</text>`;
    labels += `<text x="${cx}" y="${H - 24}" text-anchor="middle" class="ax">${d.label}</text>
               <text x="${cx}" y="${H - 9}" text-anchor="middle" class="axm">${d.trials} trials</text>`;
  });
  return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="grok-4.5 pass rate by tool-call depth">
    ${grid}<line x1="${padL}" y1="${padT + plotH}" x2="${W - padR}" y2="${padT + plotH}" stroke="var(--baseline)" stroke-width="1"/>${bars}${labels}</svg>`;
}

function taxonomyChart() {
  const W = 560, rowH = 30, padL = 250, padR = 60, H = taxRows.length * rowH + 12;
  const max = Math.max(...taxRows.map(([, v]) => v), 1);
  let bars = "";
  taxRows.forEach(([name, v], i) => {
    const y = 8 + i * rowH;
    const w = Math.max(3, (W - padL - padR) * (v / max));
    bars += `<text x="${padL - 10}" y="${y + 15}" text-anchor="end" class="ax">${esc(name)}</text>
      <rect class="bar" data-tip="${esc(name)} · ${v} failed trials" x="${padL}" y="${y + 3}" width="${w}" height="16" rx="4" fill="${S1}"/>
      <text x="${padL + w + 8}" y="${y + 15}" class="val">${v}</text>`;
  });
  return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="failed verifier conditions">${bars}</svg>`;
}

// ------------------------------------------------------------------ HTML
const chip = (cls) => cls === "pass"
  ? `<span class="chip good">✓ pass</span>`
  : cls === "flaky"
    ? `<span class="chip warn">≈ flaky</span>`
    : `<span class="chip crit">✗ fail</span>`;

const scoreRows = stats.map((s) => `
  <tr>
    <td>${chip(s.cls)}</td>
    <td class="mono">${esc(s.taskId)}</td>
    <td>${esc(s.difficulty ?? "—")}</td>
    <td class="num">${s.passes}/${s.trials}</td>
    <td class="num">${s.avgCalls}</td>
    <td class="cond">${esc(Object.keys(s.failedConditions).join(", ") || "—")}</td>
  </tr>`).join("");

const rolloutHtml = rollout.map((r) =>
  r.kind === "tool"
    ? `<div class="step"><span class="t">▸ ${esc(r.name)}</span><span class="a">${esc(r.args)}</span><div class="r">${esc(r.result)}</div></div>`
    : r.kind === "final"
      ? `<div class="step final"><span class="t">agent</span><div class="r">${esc(r.text)}</div></div>`
      : `<div class="step verify"><span class="t">VCode verifier</span><div class="r">${r.passed ? "✓ PASSED" : "✗ failed"} — ${r.n} assertions</div></div>`
).join("");

const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Morgan Stanley (SIMULATED) — CRM world · grok-4.5 frontier scan</title>
<style>
  :root { color-scheme: light;
    --page:#f9f9f7; --surface-1:#fcfcfb; --ink:#0b0b0b; --ink-2:#52514e; --muted:#898781;
    --grid:#e1e0d9; --baseline:#c3c2b7; --border:rgba(11,11,11,.10);
    --series-1:#2a78d6; --good:#0ca30c; --warn:#fab219; --serious:#ec835a; --crit:#d03b3b; }
  @media (prefers-color-scheme: dark) { :root:where(:not([data-theme="light"])) {
    color-scheme: dark;
    --page:#0d0d0d; --surface-1:#1a1a19; --ink:#ffffff; --ink-2:#c3c2b7; --muted:#898781;
    --grid:#2c2c2a; --baseline:#383835; --border:rgba(255,255,255,.10); --series-1:#3987e5; } }
  :root[data-theme="dark"] {
    color-scheme: dark;
    --page:#0d0d0d; --surface-1:#1a1a19; --ink:#ffffff; --ink-2:#c3c2b7; --muted:#898781;
    --grid:#2c2c2a; --baseline:#383835; --border:rgba(255,255,255,.10); --series-1:#3987e5; }
  * { box-sizing: border-box; margin: 0; }
  body { background: var(--page); color: var(--ink); font: 14px/1.45 system-ui, -apple-system, "Segoe UI", sans-serif; padding: 24px; }
  .wrap { max-width: 1180px; margin: 0 auto; }
  header { display:flex; flex-wrap:wrap; align-items:baseline; gap:10px 14px; margin-bottom:6px; }
  h1 { font-size: 20px; font-weight: 650; }
  .badge { font-size: 11px; font-weight: 600; letter-spacing:.04em; color: var(--crit); border: 1px solid currentColor; border-radius: 999px; padding: 2px 9px; }
  .sub { color: var(--ink-2); margin-bottom: 18px; }
  .mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12.5px; }
  .tiles { display:grid; grid-template-columns: repeat(auto-fit, minmax(140px,1fr)); gap:10px; margin-bottom:18px; }
  .tile { background: var(--surface-1); border:1px solid var(--border); border-radius:10px; padding:12px 14px; }
  .tile .v { font-size: 24px; font-weight: 650; }
  .tile .l { color: var(--muted); font-size: 12px; margin-top:2px; }
  .grid2 { display:grid; grid-template-columns: 1fr 1fr; gap:14px; margin-bottom:14px; }
  @media (max-width: 900px){ .grid2{ grid-template-columns:1fr; } }
  .panel { background: var(--surface-1); border:1px solid var(--border); border-radius:12px; padding:16px; }
  .panel h2 { font-size: 14px; font-weight: 650; margin-bottom: 4px; }
  .panel .note { color: var(--ink-2); font-size: 12.5px; margin-bottom: 10px; }
  svg { width:100%; height:auto; display:block; }
  .ax { font: 11px system-ui, sans-serif; fill: var(--muted); }
  .axm { font: 10px system-ui, sans-serif; fill: var(--muted); }
  .val { font: 600 11.5px system-ui, sans-serif; fill: var(--ink-2); }
  .bar:hover { opacity:.85; }
  table { width:100%; border-collapse: collapse; }
  th { text-align:left; color: var(--muted); font-size:11.5px; font-weight:600; padding:6px 8px; border-bottom:1px solid var(--grid); }
  td { padding:6px 8px; border-bottom:1px solid var(--grid); vertical-align: top; }
  td.num { text-align:right; font-variant-numeric: tabular-nums; }
  td.cond { color: var(--ink-2); font-size:12px; }
  .chip { font-size:11.5px; font-weight:600; border-radius:999px; padding:1px 8px; white-space:nowrap; }
  .chip.good { color:var(--good); border:1px solid var(--good); }
  .chip.warn { color:var(--warn); border:1px solid var(--warn); }
  .chip.crit { color:var(--crit); border:1px solid var(--crit); }
  .step { border-left:2px solid var(--grid); padding:4px 10px; margin:6px 0; }
  .step .t { font-weight:600; font-size:12.5px; margin-right:8px; }
  .step .a { color: var(--muted); font-size:11.5px; font-family: ui-monospace, Menlo, monospace; }
  .step .r { color: var(--ink-2); font-size:12px; margin-top:2px; }
  .step.verify { border-left-color: var(--good); }
  .step.final { border-left-color: var(--series-1); }
  footer { color: var(--muted); font-size: 12px; margin-top: 18px; }
  #tip { position:fixed; pointer-events:none; background:var(--surface-1); color:var(--ink); border:1px solid var(--border);
         border-radius:8px; padding:6px 9px; font-size:12px; box-shadow:0 4px 14px rgba(0,0,0,.18); opacity:0; transition:opacity .08s; z-index:9; }
</style></head>
<body><div class="wrap">
  <header>
    <h1>Morgan Stanley — Salesforce-CRM Simulation World</h1>
    <span class="badge">SIMULATED · SYNTHETIC DATA</span>
    <span class="mono" style="color:var(--muted)">${esc(world.world_id ?? "")}</span>
  </header>
  <div class="sub">blobfish.ai research-backed world · engine <b>grok-4.5</b> (${(grok.limits.contextWindowTokens / 1000).toFixed(0)}k-token context) · built ${new Date().toISOString().slice(0, 16).replace("T", " ")} UTC</div>

  <div class="tiles">
    <div class="tile"><div class="v">${(world.tables ?? []).length}</div><div class="l">tables</div></div>
    <div class="tile"><div class="v">${(world.tools ?? []).length}</div><div class="l">tools</div></div>
    <div class="tile"><div class="v">${(world.tasks ?? []).length}</div><div class="l">verifier-backed tasks</div></div>
    <div class="tile"><div class="v">${seededRows.toLocaleString()}</div><div class="l">seeded rows</div></div>
    <div class="tile"><div class="v">${(quality.summary?.mean_discrimination ?? 0).toFixed(2)}</div><div class="l">mean discrimination</div></div>
    <div class="tile"><div class="v">${totals.trials}</div><div class="l">grok-4.5 trials ($${totals.cost})</div></div>
  </div>

  <div class="grid2">
    <div class="panel">
      <h2>Pass rate vs interaction depth</h2>
      <div class="note">grok-4.5 trial pass rate by number of tool calls in the rollout — performance degrades as chains lengthen.</div>
      ${depthChart()}
    </div>
    <div class="panel">
      <h2>Failed verifier conditions</h2>
      <div class="note">What breaks when grok-4.5 fails: VCode assertion failures across all trials.</div>
      ${taxonomyChart()}
    </div>
  </div>

  <div class="grid2">
    <div class="panel">
      <h2>Task scoreboard — ${totals.pass} pass · ${totals.flaky} flaky · ${totals.fail} fail</h2>
      <div class="note">Merged across scans: ${esc(primary.labels.join(", "))}. Flaky = passes some trials, fails others — the capability frontier.</div>
      <table>
        <thead><tr><th>status</th><th>task</th><th>tier</th><th>pass</th><th>avg calls</th><th>failed conditions</th></tr></thead>
        <tbody>${scoreRows}</tbody>
      </table>
    </div>
    <div class="panel">
      <h2>Live rollout — ${esc(passTrial?.taskId ?? "")} (verified ✓)</h2>
      <div class="note">Actual grok-4.5 tool-call transcript against the world, scored by the VCode verifier.</div>
      ${rolloutHtml || '<div class="note">no passing rollout log found</div>'}
    </div>
  </div>

  <footer>Simulation only — every account, record, and figure is synthetic; not affiliated with Morgan Stanley. World generated via the blobfish.ai API (job ${esc(quality.world_id ?? "")}); verified with executable VCode assertions.</footer>
</div>
<div id="tip"></div>
<script>
  const tip = document.getElementById("tip");
  document.querySelectorAll("[data-tip]").forEach((el) => {
    el.addEventListener("mousemove", (e) => {
      tip.textContent = el.dataset.tip;
      tip.style.left = (e.clientX + 12) + "px";
      tip.style.top = (e.clientY + 12) + "px";
      tip.style.opacity = 1;
    });
    el.addEventListener("mouseleave", () => { tip.style.opacity = 0; });
  });
</script>
</body></html>`;

mkdirSync(join(ROOT, "dashboard"), { recursive: true });
writeFileSync(join(ROOT, "dashboard", "index.html"), html);
console.log(`dashboard/index.html written — waves: ${waveIds.join(", ")} | primary trials: ${primary.trials.length} | tasks: ${stats.length}`);
