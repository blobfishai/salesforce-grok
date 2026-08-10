#!/usr/bin/env node
/**
 * Build dashboard/episodes.html — full arena episodes: user prompt, grok-4.5's
 * THINKING traces (reasoning_content), tool calls, final answer vs computed ground
 * truth, verdict. Failure modes become visible in the reasoning itself.
 *
 * Picks: a rich PASS, the always-fail episode (reasoning spiral), and — when level 2
 * results exist — a same-task L1-pass vs L2-fail pair (the hardening flip).
 */
import { readFileSync, readdirSync, writeFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const clip = (s, n) => { s = String(s ?? "").replace(/\s+/g, " ").trim(); return s.length > n ? s.slice(0, n) + "…" : s; };

const loadDir = (d) => existsSync(d) ? readdirSync(d).filter((f) => f.endsWith(".json")).map((f) => JSON.parse(readFileSync(join(d, f), "utf8"))) : [];
const l1 = loadDir(join(ROOT, "sim", "logs", "arena-l1-archive"));
const l2 = loadDir(join(ROOT, "sim", "logs", "arena"));

const stepHtml = (s) => {
  if (s.k === "thinking") return `<div class="step think"><span class="lbl">thinking</span><div class="tx think">${esc(clip(s.text, 620))}</div></div>`;
  if (s.k === "tool") return `<div class="step tool"><span class="lbl">tool</span><div class="tx mono"><b>${esc(s.name)}</b>(${esc(clip(JSON.stringify(s.args), 90))}) <span class="r">→ ${esc(clip(s.result, 170))}</span></div></div>`;
  if (s.k === "answer") return `<div class="step ans"><span class="lbl">answer</span><div class="tx">FINAL ANSWER: <b>${esc(clip(s.text, 140))}</b></div></div>`;
  return "";
};

const episodePanel = (ep, subtitle) => {
  if (!ep) return "";
  const gt = JSON.stringify(ep.gt);
  const steps = (ep.steps ?? []);
  const shown = steps.length > 22 ? [...steps.slice(0, 20), { k: "gap" }, steps[steps.length - 1]] : steps;
  return `<div class="panel ep">
    <div class="ehead ${ep.passed ? "ok" : "bad"}">
      <span>${ep.passed ? "✓ CORRECT" : "✗ WRONG"}</span>
      <span class="emeta">${esc(ep.taskId)} · ${esc(ep.type)} · level ${ep.level} · trial ${ep.trial} · $${ep.costUsd}</span>
    </div>
    <div class="esub">${esc(subtitle)}</div>
    <div class="prompt"><span class="plabel">TASK PROMPT</span>${esc(ep.prompt)}</div>
    ${shown.map((s) => s.k === "gap" ? `<div class="gapline">… ${steps.length - 21} more steps …</div>` : stepHtml(s)).join("")}
    <div class="verdict ${ep.passed ? "ok" : "bad"}">model answer: <b>${esc(clip(ep.answer ?? "(no answer — ran out of turns)", 90))}</b> · ground truth: <b>${esc(gt)}</b> · metric: ${esc(ep.metric)}</div>
  </div>`;
};

const find = (arr, task, passed) => arr.find((e) => e.taskId === task && (passed === undefined || e.passed === passed));

const sections = [];
// 1. rich pass with thinking: case_routing L1
sections.push(episodePanel(find(l1, "arena_case_routing", true), "Real CRMArena task type (case_routing): apply the seeded routing policy — category, eligibility, tie-breaks — and name the agent."));
// 2. the always-fail: handle_time L1 (reasoning spiral)
sections.push(episodePanel(find(l1, "arena_handle_time", false), "Always-fail at level 1 (too hard): aggregating 200 tickets exceeds the paging horizon — watch the thinking as the plan degrades into repeated paging until turns run out."));
// 3. L2 flips: same task L1 pass vs L2 outcome
for (const task of ["arena_lead_qualification", "arena_case_routing", "arena_policy_violation", "arena_ned", "arena_top_issue", "arena_handle_time"]) {
  const a = find(l1, task); const b = find(l2, task);
  if (a && b && a.passed !== b.passed) {
    sections.push(`<div class="pair"><h2>${esc(task)} — level 1 vs level 2 (the hardening flip)</h2><div class="cols">${episodePanel(a, "Level 1 — before hardening")}${episodePanel(b, "Level 2 — after hardening (superseding documents / collisions / near-ties)")}</div></div>`);
    break;
  }
}
// 4. any L2 flaky pair (same task, pass+fail at L2)
for (const task of [...new Set(l2.map((e) => e.taskId))]) {
  const p = find(l2, task, true), f = find(l2, task, false);
  if (p && f) {
    sections.push(`<div class="pair"><h2>${esc(task)} — FLAKY at level 2 (the limit)</h2><div class="cols">${episodePanel(p, "Winning trial")}${episodePanel(f, "Losing trial — same task, same world")}</div></div>`);
    break;
  }
}

const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Arena episodes — prompt, thinking, tools, answer vs ground truth</title><style>
  :root { color-scheme: dark; --page:#0d0d0d; --surface-1:#1a1a19; --ink:#fff; --ink-2:#c3c2b7; --muted:#898781;
    --grid:#2c2c2a; --border:rgba(255,255,255,.10); --series-1:#3987e5; --good:#0ca30c; --crit:#d03b3b; --violet:#9085e9; --warn:#fab219; }
  * { box-sizing:border-box; margin:0; }
  body { background:var(--page); color:var(--ink); font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif; padding:24px; }
  .wrap { max-width:1220px; margin:0 auto; }
  header { display:flex; flex-wrap:wrap; align-items:baseline; gap:10px 14px; }
  h1 { font-size:20px; font-weight:650; } h2 { font-size:14.5px; font-weight:650; margin:4px 0 10px; }
  .badge { font-size:11px; font-weight:600; color:var(--crit); border:1px solid currentColor; border-radius:999px; padding:2px 9px; }
  .sub { color:var(--ink-2); margin:4px 0 16px; }
  .panel { background:var(--surface-1); border:1px solid var(--border); border-radius:12px; padding:14px; margin-bottom:14px; }
  .pair { margin-bottom:14px; }
  .cols { display:grid; grid-template-columns:1fr 1fr; gap:14px; align-items:start; }
  @media (max-width:980px){ .cols{grid-template-columns:1fr;} }
  .ehead { display:flex; justify-content:space-between; font-weight:650; font-size:13px; margin-bottom:2px; }
  .ehead.ok { color:var(--good); } .ehead.bad { color:var(--crit); }
  .emeta { color:var(--ink-2); font-weight:500; font-size:11.5px; }
  .esub { color:var(--muted); font-size:12px; margin-bottom:10px; }
  .prompt { background:var(--page); border:1px solid var(--grid); border-radius:8px; padding:10px 12px; font-size:12.5px; color:var(--ink-2); margin-bottom:8px; white-space:pre-wrap; }
  .plabel { display:block; font-size:10px; font-weight:700; letter-spacing:.05em; color:var(--series-1); margin-bottom:4px; }
  .step { display:flex; gap:10px; padding:5px 8px; border-top:1px solid var(--grid); }
  .step .lbl { flex:0 0 64px; font-size:10px; font-weight:700; text-transform:uppercase; padding-top:2px; }
  .step .tx { font-size:12px; color:var(--ink-2); }
  .step .tx.think { font-style:italic; }
  .step.think .lbl { color:var(--violet); }
  .step.tool .lbl { color:var(--series-1); } .tx.mono, .mono { font-family:ui-monospace,Menlo,monospace; font-size:11.5px; }
  .tx .r { color:var(--muted); }
  .step.ans .lbl { color:var(--warn); }
  .gapline { color:var(--muted); font-size:11px; font-style:italic; padding:6px 0 6px 82px; border-top:1px solid var(--grid); }
  .verdict { margin-top:8px; padding:8px 12px; border-radius:8px; font-size:12.5px; }
  .verdict.ok { background:rgba(12,163,12,.08); color:var(--good); }
  .verdict.bad { background:rgba(208,59,59,.08); color:var(--crit); }
  footer { color:var(--muted); font-size:12px; margin-top:14px; }
</style></head><body><div class="wrap">
  <header><h1>Arena episodes — prompt · thinking · tools · answer vs ground truth</h1><span class="badge">grok-4.5 · SIMULATED</span></header>
  <div class="sub">Real-eval task types (CRMArena) over the simulated world. Every step below is from an actual rollout: the violet lines are grok-4.5's own reasoning (<span class="mono">reasoning_content</span>) — failure modes show up in the thinking before they show up in the answer.</div>
  ${sections.join("")}
  <footer>Simulation only — synthetic data; not affiliated with Morgan Stanley or Salesforce. Ground truths computed from world data at build time; scoring exact/fuzzy/set match (CRMArena-style).</footer>
</div></body></html>`;

writeFileSync(join(ROOT, "dashboard", "episodes.html"), html);
console.log(`episodes.html — l1 episodes: ${l1.length}, l2 episodes: ${l2.length}, sections: ${sections.filter(Boolean).length}`);
