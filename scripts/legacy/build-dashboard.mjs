#!/usr/bin/env node
/**
 * Build dashboard/index.html — multi-wave capability-frontier dashboard:
 * world stats, wave comparison, per-task pass-rate trajectory (wave-2 family),
 * depth curve, failure taxonomy, and an interactive dialogue episode.
 */
import { readFileSync, writeFileSync, mkdirSync, existsSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

const WAVES = [
  { key: "w1", name: "wave 1 · baseline deep build (f=0.5)", files: ["wave1.json", "wave1b.json"], world: "world/blobfish/world.json" },
  { key: "w3l", name: "wave 3-local · distractor escalation", files: ["wave3-local.json"], world: "world/blobfish-wave3local/package/sbx_7d7d8fedcecb4458/world.json" },
  { key: "w2", name: "wave 2 · API-evolved (171 tools · 5-13 hop walks · f=0.58)", files: ["wave2.json", "wave2-nearmiss.json"], world: "world/blobfish-wave2/world.json" },
  { key: "w4", name: "wave 4 · targeted hardening (SOP docs · ambiguous refs)", files: ["wave4.json"], world: "world/blobfish-wave4/world.json" },
  { key: "w5", name: "wave 5 · conflicting SOP versions · conditional rules · collisions", files: ["wave5.json", "wave5b.json"], world: "world/blobfish-wave5/world.json" },
];

const flakeDir = join(ROOT, "data", "flake");
const loadTrials = (files) => files.flatMap((f) => {
  const p = join(flakeDir, f);
  if (!existsSync(p)) return [];
  return (JSON.parse(readFileSync(p, "utf8")).trialsRaw ?? []).filter((t) => !t.infraError);
});
const statsFor = (trials) => {
  const by = {};
  for (const t of trials) { const b = (by[t.taskId] ??= { p: 0, n: 0, calls: [], cost: 0, fails: {} }); b.n++; if (t.passed) b.p++; b.calls.push(t.toolCalls ?? 0); b.cost += t.costUsd ?? 0; for (const c of t.failedConditions ?? []) b.fails[c] = (b.fails[c] ?? 0) + 1; }
  return by;
};
const cls = (b) => (!b ? null : b.p === b.n ? "pass" : b.p === 0 ? "fail" : "flaky");
const depthBuckets = (trials) => [["1–5", 1, 5], ["6–10", 6, 10], ["11–20", 11, 20], ["21+", 21, 1e9]].map(([label, lo, hi]) => {
  const t = trials.filter((x) => (x.toolCalls ?? 0) >= lo && (x.toolCalls ?? 0) <= hi);
  return { label, n: t.length, rate: t.length ? t.filter((x) => x.passed).length / t.length : null };
});

const waves = WAVES.map((w) => {
  const trials = loadTrials(w.files);
  const by = statsFor(trials);
  const classes = Object.values(by).map((b) => cls(b));
  return {
    ...w, trials, by,
    counts: { pass: classes.filter((c) => c === "pass").length, flaky: classes.filter((c) => c === "flaky").length, fail: classes.filter((c) => c === "fail").length },
    cost: +trials.reduce((a, t) => a + (t.costUsd ?? 0), 0).toFixed(2),
    depth: depthBuckets(trials),
  };
}).filter((w) => w.trials.length);

const worldRaw = JSON.parse(readFileSync(join(ROOT, "world", "blobfish-wave2", "world.json"), "utf8"));
const world = worldRaw.world ?? worldRaw;
const models = JSON.parse(readFileSync(join(ROOT, "config", "models.json"), "utf8"));
const grok = models.models["grok-4.5"];
const seededRows = (world.tables ?? []).reduce((a, t) => a + (t.row_count ?? 0), 0);
const totalTrials = waves.reduce((a, w) => a + w.trials.length, 0);
const totalCost = +waves.reduce((a, w) => a + w.cost, 0).toFixed(2);

// frontier trajectory across the wave-2 family (w2 baseline -> w4 hardened)
const w2 = waves.find((w) => w.key === "w2");
const w4 = waves.find((w) => w.key === "w4");
const w5 = waves.find((w) => w.key === "w5");
const taskIds = [...new Set([...(Object.keys(w2?.by ?? {})), ...(Object.keys(w4?.by ?? {})), ...(Object.keys(w5?.by ?? {}))])].sort();
const chip = (c, b) => c === null ? `<span class="chip mut">—</span>`
  : c === "pass" ? `<span class="chip good">✓ ${b.p}/${b.n}</span>`
  : c === "flaky" ? `<span class="chip warn">≈ ${b.p}/${b.n}</span>`
  : `<span class="chip crit">✗ ${b.p}/${b.n}</span>`;
const trajRows = taskIds.map((id) => {
  const b2 = w2?.by[id], b4 = w4?.by[id], b5 = w5?.by[id];
  const c2 = cls(b2), c4 = cls(b4), c5 = cls(b5);
  const frontier = c5 === "flaky" || c4 === "flaky" || c2 === "flaky";
  const avg5 = b5 ? (b5.calls.reduce((a, c) => a + c, 0) / b5.calls.length).toFixed(1) : null;
  const note = c5 === "flaky" ? `FRONTIER FOUND — ${Math.round((b5.p / b5.n) * 100)}% pass at ~${avg5} calls`
    : c5 === "fail" && c2 === "pass" ? `overshot at ~${avg5} calls (wrong SOP branch + off-task writes) — one notch past the limit`
    : c5 === "pass" && c2 === "pass" ? `survives all ratchets (now ~${avg5} calls) — next: interactive drip-feed + procedure mandates`
    : c2 === "fail" ? "kept as-is — beyond frontier (required_workflow_path: mandated tool procedure)"
    : "";
  return { id, b2, b4, b5, c2, c4, c5, frontier, note };
}).sort((a, b) => (b.frontier ? 1 : 0) - (a.frontier ? 1 : 0) || (a.c5 === "fail" || a.c2 === "fail" ? 0 : 1) - (b.c5 === "fail" || b.c2 === "fail" ? 0 : 1));

const sparkbar = (depth) => depth.map((d) => {
  const h = d.rate === null ? 2 : Math.max(2, Math.round(26 * d.rate));
  const color = d.rate === null ? "var(--grid)" : "var(--series-1)";
  return `<div class="sb" title="${d.label}: ${d.rate === null ? "no trials" : Math.round(d.rate * 100) + "% of " + d.n}"><div class="sbf" style="height:${h}px;background:${color}"></div><span>${d.label}</span></div>`;
}).join("");

// merged wave-2-family depth + taxonomy
const famTrials = [...(w2?.trials ?? []), ...(w4?.trials ?? []), ...(w5?.trials ?? [])];
const famDepth = depthBuckets(famTrials);
const tax = {};
for (const t of famTrials) for (const c of t.failedConditions ?? []) tax[c] = (tax[c] ?? 0) + 1;
const taxRows = Object.entries(tax).sort((a, b) => b[1] - a[1]).slice(0, 8);

function depthChart(depth, title) {
  const W = 560, H = 240, padL = 44, padB = 44, padT = 24, padR = 12;
  const plotW = W - padL - padR, plotH = H - padT - padB;
  const bw = Math.min(70, (plotW / depth.length) - 26);
  let out = "";
  for (const g of [0, 0.5, 1]) {
    const y = padT + plotH * (1 - g);
    out += `<line x1="${padL}" y1="${y}" x2="${W - padR}" y2="${y}" stroke="var(--grid)"/><text x="${padL - 8}" y="${y + 4}" text-anchor="end" class="ax">${g * 100}%</text>`;
  }
  depth.forEach((d, i) => {
    const cx = padL + (plotW / depth.length) * (i + 0.5);
    if (d.n > 0) {
      const h = Math.max(2, plotH * (d.rate ?? 0)); const y = padT + plotH - h;
      out += `<rect x="${cx - bw / 2}" y="${y}" width="${bw}" height="${h}" rx="4" fill="var(--series-1)"/><text x="${cx}" y="${y - 6}" text-anchor="middle" class="val">${Math.round((d.rate ?? 0) * 100)}%</text>`;
    } else out += `<text x="${cx}" y="${padT + plotH - 8}" text-anchor="middle" class="ax">no trials</text>`;
    out += `<text x="${cx}" y="${H - 22}" text-anchor="middle" class="ax">${d.label}</text><text x="${cx}" y="${H - 8}" text-anchor="middle" class="axm">${d.n} trials</text>`;
  });
  return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(title)}">${out}<line x1="${padL}" y1="${padT + plotH}" x2="${W - padR}" y2="${padT + plotH}" stroke="var(--baseline)"/></svg>`;
}
function taxonomyChart() {
  const W = 560, rowH = 28, padL = 260, H = taxRows.length * rowH + 8;
  const max = Math.max(...taxRows.map(([, v]) => v), 1);
  return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="failed conditions">` + taxRows.map(([name, v], i) => {
    const y = 6 + i * rowH, w = Math.max(3, (W - padL - 50) * (v / max));
    return `<text x="${padL - 8}" y="${y + 13}" text-anchor="end" class="ax">${esc(name)}</text><rect x="${padL}" y="${y}" width="${w}" height="15" rx="4" fill="var(--series-1)"/><text x="${padL + w + 6}" y="${y + 12}" class="val">${v}</text>`;
  }).join("") + `</svg>`;
}

// interactive episode excerpt
let episodeHtml = "";
const iaFiles = readdirSync(join(ROOT, "sim", "logs")).filter((f) => f.startsWith("interactive-")).sort();
if (iaFiles.length) {
  const ep = JSON.parse(readFileSync(join(ROOT, "sim", "logs", iaFiles[iaFiles.length - 1]), "utf8"));
  const pick = iaFiles.map((f) => JSON.parse(readFileSync(join(ROOT, "sim", "logs", f), "utf8"))).find((e) => e.passed) ?? ep;
  const lbl = { user: ["user", "colleague"], thought: ["thought", "thought"], tool: ["exec", "tool call"], assistant: ["respond", "assistant"], verify: ["verify", "VCode verifier"] };
  episodeHtml = pick.turns.slice(0, 14).map((t) => {
    const [c, l] = lbl[t.role] ?? ["obs", t.role];
    const text = t.role === "tool" ? `${t.name}(${JSON.stringify(t.args)})` : t.content;
    return `<div class="step ${c}"><span class="lbl">${l}</span><div class="tx">${esc(String(text).replace(/\s+/g, " ").slice(0, 210))}</div></div>`;
  }).join("");
  episodeHtml = `<div class="panel"><h2>Interactive episode — ${esc(pick.taskId)} (${pick.passed ? "✓ verified" : "✗ failed"})</h2>
    <div class="note">CRMArena-style dialogue: the stakeholder opens with a problem prompt and reveals details on request; grok-4.5 works it conversationally; VCode scores the end state.</div>${episodeHtml}</div>`;
}

const waveRows = waves.map((w) => `
  <tr><td>${esc(w.name)}</td>
  <td class="num">${Object.keys(w.by).length}</td>
  <td><span class="chip good">✓ ${w.counts.pass}</span> <span class="chip warn">≈ ${w.counts.flaky}</span> <span class="chip crit">✗ ${w.counts.fail}</span></td>
  <td class="num">${w.trials.length}</td>
  <td class="num">$${w.cost}</td>
  <td><div class="sbrow">${sparkbar(w.depth)}</div></td></tr>`).join("");

const trajHtml = trajRows.map((r) => `
  <tr class="${r.frontier ? "hot" : ""}"><td class="mono">${esc(r.id)}</td><td>${chip(r.c2, r.b2)}</td><td>${chip(r.c4, r.b4)}</td><td>${chip(r.c5, r.b5)}</td>
  <td class="cond">${esc(r.note)}</td></tr>`).join("");

const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>grok-4.5 capability frontier — Morgan Stanley (SIMULATED) CRM waves</title>
<style>
  :root { color-scheme: dark;
    --page:#0d0d0d; --surface-1:#1a1a19; --ink:#fff; --ink-2:#c3c2b7; --muted:#898781;
    --grid:#2c2c2a; --baseline:#383835; --border:rgba(255,255,255,.10);
    --series-1:#3987e5; --good:#0ca30c; --warn:#fab219; --crit:#d03b3b; --violet:#9085e9; }
  * { box-sizing:border-box; margin:0; }
  body { background:var(--page); color:var(--ink); font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif; padding:24px; }
  .wrap { max-width:1220px; margin:0 auto; }
  header { display:flex; flex-wrap:wrap; align-items:baseline; gap:10px 14px; }
  h1 { font-size:20px; font-weight:650; }
  .badge { font-size:11px; font-weight:600; color:var(--crit); border:1px solid currentColor; border-radius:999px; padding:2px 9px; }
  .sub { color:var(--ink-2); margin:4px 0 16px; }
  .tiles { display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:10px; margin-bottom:16px; }
  .tile { background:var(--surface-1); border:1px solid var(--border); border-radius:10px; padding:12px 14px; }
  .tile .v { font-size:23px; font-weight:650; } .tile .l { color:var(--muted); font-size:12px; margin-top:2px; }
  .panel { background:var(--surface-1); border:1px solid var(--border); border-radius:12px; padding:16px; margin-bottom:14px; }
  .panel h2 { font-size:14px; font-weight:650; margin-bottom:4px; }
  .panel .note { color:var(--ink-2); font-size:12.5px; margin-bottom:10px; }
  .grid2 { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
  @media (max-width:900px){ .grid2{grid-template-columns:1fr;} }
  table { width:100%; border-collapse:collapse; }
  th { text-align:left; color:var(--muted); font-size:11.5px; font-weight:600; padding:6px 8px; border-bottom:1px solid var(--grid); }
  td { padding:6px 8px; border-bottom:1px solid var(--grid); vertical-align:middle; }
  td.num { text-align:right; font-variant-numeric:tabular-nums; }
  td.cond { color:var(--ink-2); font-size:12px; }
  tr.hot td { background:rgba(250,178,25,.07); }
  .mono { font-family:ui-monospace,Menlo,monospace; font-size:12.5px; }
  .chip { font-size:11.5px; font-weight:600; border-radius:999px; padding:1px 8px; white-space:nowrap; border:1px solid var(--grid); color:var(--ink-2); }
  .chip.good { color:var(--good); border-color:var(--good); } .chip.warn { color:var(--warn); border-color:var(--warn); }
  .chip.crit { color:var(--crit); border-color:var(--crit); } .chip.mut {}
  svg { width:100%; height:auto; display:block; }
  .ax { font:11px system-ui,sans-serif; fill:var(--muted); } .axm { font:10px system-ui,sans-serif; fill:var(--muted); }
  .val { font:600 11.5px system-ui,sans-serif; fill:var(--ink-2); }
  .sbrow { display:flex; gap:10px; align-items:flex-end; }
  .sb { display:flex; flex-direction:column; align-items:center; gap:2px; }
  .sb span { font-size:9.5px; color:var(--muted); }
  .sbf { width:22px; border-radius:3px 3px 0 0; }
  .step { display:flex; gap:10px; padding:5px 10px; border-top:1px solid var(--grid); }
  .step .lbl { flex:0 0 96px; font-size:10.5px; font-weight:700; text-transform:uppercase; padding-top:2px; }
  .step .tx { font-size:12px; color:var(--ink-2); }
  .step.exec .lbl { color:var(--series-1); } .step.exec .tx { font-family:ui-monospace,Menlo,monospace; }
  .step.thought .lbl { color:var(--violet); } .step.thought .tx { font-style:italic; }
  .step.user .lbl { color:var(--ink); } .step.respond .lbl { color:var(--good); }
  .step.verify .lbl { color:var(--good); } .step.verify { background:rgba(12,163,12,.05); }
  footer { color:var(--muted); font-size:12px; margin-top:14px; }
</style></head>
<body><div class="wrap">
  <header><h1>grok-4.5 capability frontier — CRM simulation waves</h1><span class="badge">SIMULATED · SYNTHETIC DATA</span></header>
  <div class="sub">Worlds generated & evolved via the blobfish.ai API · canonical world <span class="mono">${esc(world.world_id ?? "")}</span> · engine grok-4.5 (${(grok.limits.contextWindowTokens / 1000)}k ctx) · built ${new Date().toISOString().slice(0, 16).replace("T", " ")} UTC</div>

  <div class="tiles">
    <div class="tile"><div class="v">${(world.tables ?? []).length}</div><div class="l">tables (wave-2 world)</div></div>
    <div class="tile"><div class="v">${(world.tools ?? []).length}</div><div class="l">tools</div></div>
    <div class="tile"><div class="v">${(world.tasks ?? []).length}</div><div class="l">verifier-backed tasks</div></div>
    <div class="tile"><div class="v">${seededRows.toLocaleString()}</div><div class="l">seeded rows</div></div>
    <div class="tile"><div class="v">${totalTrials}</div><div class="l">grok-4.5 trials all waves</div></div>
    <div class="tile"><div class="v">$${totalCost}</div><div class="l">total eval spend</div></div>
  </div>

  <div class="panel">
    <h2>Waves — difficulty iteration via API + targeted hardening</h2>
    <div class="note">Aggregate pass rate is a property of the task mix; the frontier is per-task. Fails are never removed; passes are hardened until they flicker.</div>
    <table><thead><tr><th>wave</th><th>tasks</th><th>classes</th><th>trials</th><th>cost</th><th>pass rate by depth</th></tr></thead><tbody>${waveRows}</tbody></table>
  </div>

  <div class="panel">
    <h2>Per-task frontier trajectory (wave-2 world: baseline → hardened)</h2>
    <div class="note">Flaky rows (highlighted) are the frontier — grok-4.5 sometimes passes, sometimes fails the same task.</div>
    <table><thead><tr><th>task</th><th>wave 2 baseline</th><th>wave 4 hardened</th><th>wave 5 sharpened</th><th>reading</th></tr></thead><tbody>${trajHtml}</tbody></table>
  </div>

  <div class="grid2">
    <div class="panel"><h2>Pass rate vs interaction depth (wave-2 family)</h2><div class="note">Degradation with chain length — the off-distribution effect under test.</div>${depthChart(famDepth, "depth curve")}</div>
    <div class="panel"><h2>Failed verifier conditions (wave-2 family)</h2><div class="note">required_workflow_path dominates: grok reaches outcomes but skips mandated procedure steps.</div>${taxonomyChart()}</div>
  </div>

  ${episodeHtml}

  <footer>Simulation only — all data synthetic; not affiliated with Morgan Stanley or Salesforce. Worlds by blobfish.ai research pipeline; verification by executable VCode.</footer>
</div></body></html>`;

mkdirSync(join(ROOT, "dashboard"), { recursive: true });
writeFileSync(join(ROOT, "dashboard", "index.html"), html);
console.log(`dashboard/index.html — waves: ${waves.map((w) => `${w.key}(${w.trials.length})`).join(", ")} | trajectory rows: ${trajRows.length}`);
