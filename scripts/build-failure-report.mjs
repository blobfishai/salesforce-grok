#!/usr/bin/env node
/**
 * Build dashboard/failure-report.html — grok-4.5 failure-mode report over all waves,
 * and dashboard/frontier-traces.html — the SAME frontier task passing vs failing.
 *
 * Failure modes are derived from the VCode failed_conditions across every trial, then
 * illustrated with a real tool-by-tool excerpt from an actual failing rollout log.
 */
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const clip = (s, n) => { s = String(s ?? "").replace(/\s+/g, " ").trim(); return s.length > n ? s.slice(0, n) + "…" : s; };

const FLAKE = ["wave1.json", "wave1b.json", "wave2.json", "wave2-nearmiss.json", "wave3-local.json", "wave4.json", "wave5.json", "wave5b.json"];
const trials = FLAKE.flatMap((f) => existsSync(join(ROOT, "data", "flake", f)) ? (JSON.parse(readFileSync(join(ROOT, "data", "flake", f), "utf8")).trialsRaw ?? []).map((t) => ({ ...t, wave: f.replace(".json", "") })) : []).filter((t) => !t.infraError);
const failed = trials.filter((t) => !t.passed);

function readSteps(logPath) {
  if (!logPath || !existsSync(logPath)) return null;
  const lines = readFileSync(logPath, "utf8").trim().split("\n").map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
  const steps = [];
  for (const e of lines) {
    if (e.type === "tool") steps.push({ k: "tool", name: e.name, args: e.args, result: clip(e.result, 150) });
    if (e.type === "final") steps.push({ k: "final", text: e.content });
    if (e.type === "verify") { try { const v = JSON.parse(e.result); steps.push({ k: "verify", passed: v.passed, cond: (v.failed_conditions ?? []).join(", "), n: (v.assertions ?? []).length }); } catch { /* raw */ } }
  }
  return steps;
}
const excerpt = (steps, n = 10) => {
  if (!steps) return "";
  const tools = steps.filter((s) => s.k === "tool");
  const shown = tools.length > n ? [...tools.slice(0, n - 2), { k: "gap", text: `… ${tools.length - n + 1} more tool calls …` }, tools[tools.length - 1]] : tools;
  const verify = steps.find((s) => s.k === "verify");
  return [...shown, verify].filter(Boolean).map((s) =>
    s.k === "gap" ? `<div class="step gap">${esc(s.text)}</div>`
    : s.k === "verify" ? `<div class="step verify ${s.passed ? "ok" : "bad"}"><span class="lbl">VCode</span><div class="tx">${s.passed ? "✓ PASSED — " + s.n + " assertions" : "✗ FAILED — " + esc(s.cond)}</div></div>`
    : `<div class="step tool"><span class="lbl">tool</span><div class="tx"><b>${esc(s.name)}</b>(${esc(clip(JSON.stringify(s.args), 60))}) <span class="r">→ ${esc(s.result)}</span></div></div>`
  ).join("");
};

// ---- failure-mode taxonomy (named, with mechanism + exemplar log)
// Prefer a CLEAN exemplar: one whose failure is dominated by this mode (fewest unrelated
// conditions), a log exists, and — where noted — the depth signature matches the mode.
const isStatus = (c) => /_status_is_/.test(c) && !c.startsWith("no_collateral");
const isColl = (c) => c.startsWith("no_collateral");
const pickExemplar = (matchMode, { prefer } = {}) => {
  const cands = failed.filter((t) => existsSync(t.log ?? "") && matchMode(t.failedConditions ?? [], t));
  cands.sort((a, b) => {
    const off = (t) => (t.failedConditions ?? []).filter((c) => !matchMode([c], t)).length; // unrelated conds
    if (prefer) { const p = prefer(b) - prefer(a); if (p) return p; }
    return off(a) - off(b) || (a.toolCalls ?? 0) - (b.toolCalls ?? 0);
  });
  return cands[0];
};
const MODES = [
  {
    id: "off-task-writes", title: "Off-task / undeclared writes past the horizon",
    conds: ["no_offtask_table_changes", "no_undeclared_rows_created"],
    match: (cs) => cs.includes("no_offtask_table_changes") || cs.includes("no_undeclared_rows_created"),
    mech: "Once a correct plan exceeds ~10 tool calls, the model keeps acting — writing to tables the task never named, or inserting rows no effect declared. This is the dominant frontier failure: not giving up, but over-reaching. It is what makes the deepest tasks fail even when the target row is also set correctly.",
    // prefer a deep wave-5 rollout (the true frontier signature), not an early giveaway
    exemplar: pickExemplar((cs, t) => (cs.includes("no_offtask_table_changes") || cs.includes("no_undeclared_rows_created")), { prefer: (t) => (t.wave.startsWith("wave5") ? 10 : 0) + Math.min(20, t.toolCalls ?? 0) }),
  },
  {
    id: "procedure-skip", title: "Procedure-mandate skip (right outcome, wrong path)",
    conds: ["required_workflow_path"],
    match: (cs) => cs.includes("required_workflow_path"),
    mech: "The verifier requires a specific ordered tool procedure (e.g. list → create → get → update_status). grok-4.5 reaches the correct end state by a shorter route and never executes the mandated intermediate steps. Deterministic: 0 of 26 trials on these tasks complied. A behavior gap, not a depth gap.",
    exemplar: pickExemplar((cs) => cs.length === 1 && cs[0] === "required_workflow_path"),
  },
  {
    id: "collateral-sweep", title: "Collateral bulk sweep over a pinned subset",
    conds: ["no_collateral_lead", "no_collateral_quote", "no_collateral_sales_leads"],
    match: (cs) => cs.some(isColl),
    mech: "\"Update all X with status Y\" tasks pin a specific target subset; distractor rows share that status. The model reads the instruction literally and updates every match, tripping the collateral-damage guard on rows it should have left alone.",
    // prefer a PURE collateral failure (no status-assertion contamination)
    exemplar: pickExemplar((cs) => cs.some(isColl) && !cs.some(isStatus)),
  },
  {
    id: "wrong-transition", title: "Wrong lifecycle transition (CRM prior over declared rule)",
    conds: ["<table>_<id>_status_is_<value>"],
    match: (cs) => cs.some(isStatus),
    mech: "The world declares non-obvious status lifecycles (e.g. Working → Converted, or a conditional branch defined only in a current SOP). When the model answers from its Salesforce training prior instead of looking the rule up, it writes a plausible-but-wrong target value — failing the row-pinned status assertion.",
    exemplar: pickExemplar((cs) => cs.some(isStatus), { prefer: (t) => (t.toolCalls ?? 99) <= 4 ? 5 : 0 }),
  },
  {
    id: "read-before-write", title: "Wrote before reading (no inspection)",
    conds: ["reads_before_writes"],
    match: (cs) => cs.includes("reads_before_writes"),
    mech: "The model mutated a record without first inspecting it — skipping the read that would have confirmed the current state and the correct target. Rare, and concentrated on the tasks it treats as trivial.",
    exemplar: pickExemplar((cs) => cs.includes("reads_before_writes")),
  },
];

// counts across all failed trials
const condCount = {};
for (const t of failed) for (const c of t.failedConditions ?? []) condCount[c] = (condCount[c] ?? 0) + 1;
const modeCount = (m) => failed.filter((t) => m.match(t.failedConditions ?? [], t)).length;

const totalFail = failed.length;
const maxMode = Math.max(...MODES.map(modeCount), 1);
const modeBar = () => {
  const W = 620, rowH = 34, padL = 300, H = MODES.length * rowH + 8;
  return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="failure modes by trial count">` + MODES.map((m, i) => {
    const v = modeCount(m), y = 6 + i * rowH, w = Math.max(3, (W - padL - 50) * (v / maxMode));
    return `<text x="${padL - 8}" y="${y + 14}" text-anchor="end" class="ax">${esc(clip(m.title, 40))}</text>
      <rect x="${padL}" y="${y + 2}" width="${w}" height="16" rx="4" fill="var(--series-1)"/><text x="${padL + w + 7}" y="${y + 15}" class="val">${v}</text>`;
  }).join("") + `</svg>`;
};

const modeCard = (m) => {
  const ex = m.exemplar;
  const steps = ex ? readSteps(ex.log) : null;
  return `<div class="panel mode">
    <div class="mhead"><h3>${esc(m.title)}</h3><span class="cnt">${modeCount(m)} failed trials</span></div>
    <div class="conds">${m.conds.map((c) => `<span class="chip mut mono">${esc(c)}</span>`).join(" ")}</div>
    <p class="mech">${esc(m.mech)}</p>
    ${ex ? `<div class="exlabel">Real failing rollout — <span class="mono">${esc(ex.taskId)}</span> · ${esc(ex.wave)} · ${ex.toolCalls} tool calls · $${ex.costUsd}</div><div class="trace">${excerpt(steps)}</div>` : ""}
  </div>`;
};

const genAt = new Date().toISOString().slice(0, 16).replace("T", " ");
const styles = `
  :root { color-scheme: dark;
    --page:#0d0d0d; --surface-1:#1a1a19; --ink:#fff; --ink-2:#c3c2b7; --muted:#898781;
    --grid:#2c2c2a; --baseline:#383835; --border:rgba(255,255,255,.10);
    --series-1:#3987e5; --good:#0ca30c; --warn:#fab219; --crit:#d03b3b; --violet:#9085e9; }
  * { box-sizing:border-box; margin:0; }
  body { background:var(--page); color:var(--ink); font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif; padding:24px; }
  .wrap { max-width:1180px; margin:0 auto; }
  header { display:flex; flex-wrap:wrap; align-items:baseline; gap:10px 14px; }
  h1 { font-size:20px; font-weight:650; } h3 { font-size:14.5px; font-weight:650; }
  .badge { font-size:11px; font-weight:600; color:var(--crit); border:1px solid currentColor; border-radius:999px; padding:2px 9px; }
  .sub { color:var(--ink-2); margin:4px 0 16px; }
  .panel { background:var(--surface-1); border:1px solid var(--border); border-radius:12px; padding:16px; margin-bottom:14px; }
  .panel h2 { font-size:14px; font-weight:650; margin-bottom:6px; }
  .note { color:var(--ink-2); font-size:12.5px; margin-bottom:10px; }
  .mode .mhead { display:flex; justify-content:space-between; align-items:baseline; }
  .mode .cnt { color:var(--crit); font-size:12px; font-weight:600; }
  .conds { margin:6px 0 8px; }
  .mech { color:var(--ink-2); font-size:13px; margin-bottom:10px; }
  .exlabel { color:var(--muted); font-size:11.5px; margin-bottom:6px; }
  .chip { font-size:11px; border-radius:999px; padding:1px 8px; border:1px solid var(--grid); color:var(--ink-2); }
  .mono { font-family:ui-monospace,Menlo,monospace; } .mono.chip { font-size:10.5px; }
  .trace { border:1px solid var(--grid); border-radius:8px; overflow:hidden; }
  .step { display:flex; gap:10px; padding:4px 10px; border-top:1px solid var(--grid); }
  .step:first-child { border-top:none; }
  .step .lbl { flex:0 0 46px; font-size:10px; font-weight:700; text-transform:uppercase; color:var(--series-1); padding-top:2px; }
  .step .tx { font-size:11.5px; color:var(--ink-2); font-family:ui-monospace,Menlo,monospace; }
  .step .tx .r { color:var(--muted); }
  .step.gap { color:var(--muted); font-size:11px; font-style:italic; padding-left:56px; }
  .step.verify.bad { background:rgba(208,59,59,.08); } .step.verify.ok { background:rgba(12,163,12,.06); }
  .step.verify.bad .lbl { color:var(--crit); } .step.verify.ok .lbl { color:var(--good); }
  svg { width:100%; height:auto; display:block; }
  .ax { font:11px system-ui,sans-serif; fill:var(--muted); } .val { font:600 11px system-ui; fill:var(--ink-2); }
  .tiles { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px; margin-bottom:14px; }
  .tile { background:var(--surface-1); border:1px solid var(--border); border-radius:10px; padding:12px 14px; }
  .tile .v { font-size:22px; font-weight:650; } .tile .l { color:var(--muted); font-size:12px; }
  footer { color:var(--muted); font-size:12px; margin-top:14px; }`;

const report = `<!doctype html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>grok-4.5 failure-mode report — CRM simulation world</title><style>${styles}</style></head>
<body><div class="wrap">
  <header><h1>grok-4.5 failure-mode report</h1><span class="badge">SIMULATED · SYNTHETIC DATA</span></header>
  <div class="sub">Every VCode failure across ${trials.length} trials (5 waves) on the Morgan Stanley (SIMULATED) CRM world, grouped into named modes with a real failing rollout for each. Generated ${genAt} UTC.</div>
  <div class="tiles">
    <div class="tile"><div class="v">${trials.length}</div><div class="l">total trials</div></div>
    <div class="tile"><div class="v">${totalFail}</div><div class="l">failed trials</div></div>
    <div class="tile"><div class="v">${MODES.length}</div><div class="l">failure modes</div></div>
    <div class="tile"><div class="v">${condCount["required_workflow_path"] ?? 0}</div><div class="l">procedure-skip failures</div></div>
    <div class="tile"><div class="v">${(condCount["no_offtask_table_changes"] ?? 0)}</div><div class="l">off-task-write failures</div></div>
  </div>
  <div class="panel"><h2>Failure modes by trial count</h2>
    <div class="note">One trial can trip several conditions; a trial counts toward every mode it exhibits.</div>${modeBar()}</div>
  ${MODES.map(modeCard).join("")}
  <footer>Simulation only — synthetic data; not affiliated with Morgan Stanley or Salesforce. Failures scored by executable VCode assertions over before/after world state + tool trace.</footer>
</div></body></html>`;

mkdirSync(join(ROOT, "dashboard"), { recursive: true });
writeFileSync(join(ROOT, "dashboard", "failure-report.html"), report);
console.log(`failure-report.html — ${trials.length} trials, ${totalFail} failed, ${MODES.length} modes`);
for (const m of MODES) console.log(`  ${m.title}: ${modeCount(m)} (exemplar ${m.exemplar?.taskId ?? "none"})`);

// ------------------------------------------------------------------ frontier traces (pass vs fail, same task)
function pickPair(taskId, waveFilter) {
  const pool = trials.filter((t) => t.taskId === taskId && waveFilter(t.wave));
  return { pass: pool.find((t) => t.passed && existsSync(t.log ?? "")), fail: pool.find((t) => !t.passed && existsSync(t.log ?? "")) };
}
const t3 = pickPair("task_003", (w) => w.startsWith("wave5"));
const t18 = pickPair("task_018", (w) => w.startsWith("wave5"));

const traceCol = (title, sub, ep) => {
  if (!ep) return `<div class="panel"><h2>${esc(title)}</h2><div class="note">no rollout found</div></div>`;
  const steps = readSteps(ep.log);
  return `<div class="panel"><div class="thead ${ep.passed ? "ok" : "bad"}"><span>${ep.passed ? "✓ PASSED" : "✗ FAILED"}</span><span class="tmeta">${esc(sub)} · ${ep.toolCalls} tool calls · $${ep.costUsd}</span></div>
    <div class="trace">${excerpt(steps, 16)}</div></div>`;
};

const frontier = `<!doctype html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Frontier traces — same task, pass vs fail (grok-4.5)</title><style>${styles}
  .cols { display:grid; grid-template-columns:1fr 1fr; gap:14px; align-items:start; }
  @media (max-width:900px){ .cols{grid-template-columns:1fr;} }
  .thead { display:flex; justify-content:space-between; padding:6px 4px 10px; font-weight:650; font-size:13px; }
  .thead.ok { color:var(--good); } .thead.bad { color:var(--crit); }
  .thead .tmeta { color:var(--ink-2); font-weight:500; font-size:11.5px; }
  .step .lbl { flex:0 0 42px; }
</style></head>
<body><div class="wrap">
  <header><h1>Frontier traces — the same task, passed vs failed</h1><span class="badge">grok-4.5 · SIMULATED</span></header>
  <div class="sub">The clearest picture of a capability frontier: one task grok-4.5 sometimes solves and sometimes doesn't. Both rollouts are real, against the identical wave-5 world; the only difference is the run.</div>

  <div class="panel" style="border-color:var(--warn)"><h2 style="color:var(--warn)">task_003 — 50% pass (the frontier task)</h2>
    <div class="note">Locate an attribute-ambiguous record among collisions, find the CURRENT (not the outdated) SOP, evaluate its conditional rule, apply exactly one transition. When the chain stays tight it lands; when it lengthens, the model over-writes.</div>
    <div class="cols">${traceCol("pass", "task_003 · winning run", t3.pass)}${traceCol("fail", "task_003 · losing run", t3.fail)}</div>
  </div>

  <div class="panel" style="border-color:var(--crit)"><h2 style="color:var(--crit)">task_018 — 0/6 (one notch past the frontier)</h2>
    <div class="note">Same recipe, harder: the losing runs take the outdated SOP's branch (wrong target status) AND over-write, ballooning to 20+ calls. Shown against a task_003 win for contrast.</div>
    <div class="cols">${traceCol("pass", "task_003 · winning run (reference)", t3.pass)}${traceCol("fail", "task_018 · losing run", t18.fail)}</div>
  </div>
  <footer>Simulation only — synthetic data. Rollouts from sim/logs; verdicts by executable VCode. Not affiliated with Morgan Stanley or Salesforce.</footer>
</div></body></html>`;
writeFileSync(join(ROOT, "dashboard", "frontier-traces.html"), frontier);
console.log(`frontier-traces.html — task_003 pass=${!!t3.pass} fail=${!!t3.fail}, task_018 fail=${!!t18.fail}`);
