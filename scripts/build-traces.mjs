#!/usr/bin/env node
/**
 * Build dashboard/traces.html — side-by-side EXECUTION TRACES:
 *   left:  real CRMArena trajectories (GPT-4o ReAct, from the repo's LFS results)
 *   right: real grok-4.5 rollouts in our blobfish-generated world (MCP tool calls + VCode verdict)
 * CRMArena publishes raw JSON trajectories without a viewer UI; this page renders both sides
 * in one comparable viewer.
 */
import { readFileSync, writeFileSync, readdirSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const clip = (s, n) => { s = String(s ?? "").replace(/\s+/g, " ").trim(); return s.length > n ? s.slice(0, n) + "…" : s; };

// ---------------- CRMArena side
const arena = JSON.parse(readFileSync(join(ROOT, "data", "reference", "crmarena-traces-sample.json"), "utf8"));

function arenaSteps(traj) {
  const steps = [];
  for (const m of traj) {
    const c = String(m.content ?? "");
    if (m.role === "system") continue;
    if (m.role === "user") {
      if (c.startsWith("Salesforce instance output:")) steps.push({ k: "obs", text: c.replace("Salesforce instance output:", "").trim() });
      else steps.push({ k: "user", text: c });
      continue;
    }
    // assistant: split ReAct markup
    const seg = (tag) => { const m2 = c.match(new RegExp(`<${tag}>([\\s\\S]*?)</${tag}>`)); return m2 ? m2[1].trim() : null; };
    const thought = seg("thought"), ex = seg("execute"), resp = seg("respond");
    if (thought) steps.push({ k: "thought", text: thought });
    if (ex) steps.push({ k: "exec", text: ex });
    if (resp) steps.push({ k: "respond", text: resp });
    if (!thought && !ex && !resp) steps.push({ k: "respond", text: c });
  }
  return steps;
}

const stepHtml = (s) => {
  const map = {
    user: ["user", "user"], obs: ["obs", "Salesforce output"], thought: ["thought", "thought"],
    exec: ["exec", "execute (SOQL)"], respond: ["respond", "respond"],
    tool: ["exec", "tool call"], result: ["obs", "world output"], final: ["respond", "final answer"], verify: ["verify", "VCode verifier"],
  };
  const [cls, label] = map[s.k] ?? ["obs", s.k];
  return `<div class="step ${cls}"><span class="lbl">${label}</span><div class="tx">${esc(clip(s.text, 260))}</div></div>`;
};

const episodeCard = (title, meta, passed, steps, maxSteps = 14) => `
  <div class="card">
    <div class="ehead ${passed ? "ok" : "bad"}">
      <span>${passed ? "✓ reward 1" : "✗ reward 0"}</span><span class="meta">${esc(title)}</span>
    </div>
    <div class="emeta">${esc(meta)}</div>
    ${steps.slice(0, maxSteps).map(stepHtml).join("")}
    ${steps.length > maxSteps ? `<div class="more">… ${steps.length - maxSteps} more steps</div>` : ""}
  </div>`;

const arenaCards = arena.episodes.map((e) =>
  episodeCard(
    `${e.file} · task ${e.task_id} · ${e.traj.length} turns`,
    `ground truth: ${clip(JSON.stringify(e.gt_answer), 60)} · interactive multi-turn · graded by answer match`,
    e.reward === 1,
    arenaSteps(e.traj)
  )).join("");

// ---------------- our side: grok-4.5 MCP rollouts from sim/logs, chosen via flake trial records
const flakeFiles = readdirSync(join(ROOT, "data", "flake")).filter((f) => f.endsWith(".json"));
const trials = flakeFiles.flatMap((f) => JSON.parse(readFileSync(join(ROOT, "data", "flake", f), "utf8")).trialsRaw ?? [])
  .filter((t) => !t.infraError && t.log && existsSync(t.log));

function ourSteps(logPath) {
  const lines = readFileSync(logPath, "utf8").trim().split("\n").map((l) => JSON.parse(l));
  const steps = [];
  for (const e of lines) {
    if (e.type === "tool") {
      steps.push({ k: "tool", text: `${e.name}(${JSON.stringify(e.args)})` });
      steps.push({ k: "result", text: String(e.result) });
    }
    if (e.type === "final") steps.push({ k: "final", text: String(e.content) });
    if (e.type === "verify") {
      try {
        const v = JSON.parse(e.result);
        const failed = (v.failed_conditions ?? []).join(", ");
        steps.push({ k: "verify", text: v.passed ? `PASSED — ${(v.assertions ?? []).length} assertions green` : `FAILED — ${failed}` });
      } catch { steps.push({ k: "verify", text: clip(e.result, 200) }); }
    }
  }
  return steps;
}

const findTrial = (taskId, passed) => trials.find((t) => t.taskId === taskId && t.passed === passed);
const ourPicks = [
  { t: findTrial("task_004", true), title: "task_004 · lead lifecycle advance", meta: "verifier: 11 VCode assertions over DB state + trace" },
  { t: findTrial("task_024", false), title: "task_024 · pinned-subset lead sweep", meta: "verifier: row pins + no_collateral_lead guard" },
  { t: findTrial("task_015", true), title: "task_015 · expense-report workflow (multi-hop)", meta: "verifier: 12 VCode assertions incl. required workflow path" },
  { t: findTrial("task_014", false), title: "task_014 · 6-hop cross-table workflow", meta: "verifier: required_workflow_path + row pins + collateral guards" },
].filter((x) => x.t);

const ourCards = ourPicks.map((x) =>
  episodeCard(
    `${x.title} · ${x.t.toolCalls} tool calls · $${x.t.costUsd}`,
    `${x.meta} · session-isolated SQLite world`,
    x.t.passed,
    ourSteps(x.t.log)
  )).join("");

// ---------------- optional: blobfish Gym run episodes (if the CLI eval produced runs)
let gymNote = "";
const gymRunDirs = [];
for (const base of [join(ROOT, "world", "blobfish", "package", "sbx_7d7d8fedcecb4458"), ROOT]) {
  for (const cand of ["blobfish_runs", "runs", ".blobfish/runs"]) {
    const p = join(base, cand);
    if (existsSync(p)) gymRunDirs.push(p);
  }
}
if (gymRunDirs.length) gymNote = `<div class="note">Blobfish Gym runs also recorded at: ${gymRunDirs.map((p) => `<span class="mono">${esc(p.replace(ROOT + "/", ""))}</span>`).join(", ")} — viewable via <span class="mono">blobfish dashboard</span>.</div>`;

const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Task traces: CRMArena (GPT-4o ReAct) vs our world (grok-4.5 MCP)</title>
<style>
  :root { color-scheme: dark;
    --page:#0d0d0d; --surface-1:#1a1a19; --ink:#fff; --ink-2:#c3c2b7; --muted:#898781;
    --grid:#2c2c2a; --border:rgba(255,255,255,.10);
    --series-1:#3987e5; --good:#0ca30c; --warn:#fab219; --crit:#d03b3b; --violet:#9085e9; }
  * { box-sizing:border-box; margin:0; }
  body { background:var(--page); color:var(--ink); font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif; padding:24px; }
  .wrap { max-width:1280px; margin:0 auto; }
  h1 { font-size:20px; font-weight:650; }
  .sub { color:var(--ink-2); margin:4px 0 16px; }
  .cols { display:grid; grid-template-columns:1fr 1fr; gap:14px; align-items:start; }
  .panel { background:var(--surface-1); border:1px solid var(--border); border-radius:12px; padding:14px; }
  .panel h2 { font-size:14.5px; font-weight:650; margin-bottom:2px; }
  .panel .note { color:var(--ink-2); font-size:12.5px; margin-bottom:10px; }
  .card { border:1px solid var(--grid); border-radius:10px; margin-bottom:12px; overflow:hidden; }
  .ehead { display:flex; justify-content:space-between; padding:7px 12px; font-weight:650; font-size:12.5px; }
  .ehead.ok { color:var(--good); background:rgba(12,163,12,.08); }
  .ehead.bad { color:var(--crit); background:rgba(208,59,59,.08); }
  .ehead .meta { color:var(--ink-2); font-weight:500; }
  .emeta { color:var(--muted); font-size:11.5px; padding:5px 12px 2px; }
  .step { display:flex; gap:10px; padding:5px 12px; border-top:1px solid var(--grid); }
  .step .lbl { flex:0 0 108px; font-size:10.5px; font-weight:700; letter-spacing:.03em; text-transform:uppercase; padding-top:2px; }
  .step .tx { font-size:12px; color:var(--ink-2); font-family:ui-monospace,Menlo,monospace; }
  .step.user .lbl { color:var(--ink); } .step.user .tx { font-family:inherit; }
  .step.thought .lbl { color:var(--violet); } .step.thought .tx { font-family:inherit; font-style:italic; }
  .step.exec .lbl { color:var(--series-1); }
  .step.obs .lbl { color:var(--warn); }
  .step.respond .lbl { color:var(--good); } .step.respond .tx { font-family:inherit; }
  .step.verify .lbl { color:var(--good); } .step.verify { background:rgba(12,163,12,.05); }
  .more { padding:6px 12px; color:var(--muted); font-size:11.5px; border-top:1px solid var(--grid); }
  .mono { font-family:ui-monospace,Menlo,monospace; font-size:12px; }
  footer { color:var(--muted); font-size:12px; margin-top:14px; }
</style></head>
<body><div class="wrap">
  <h1>Task traces — CRMArena vs the world we created</h1>
  <div class="sub">Left: <b>real</b> GPT-4o ReAct trajectories published in the CRMArena repo (rendered here — the repo ships raw JSON with no viewer). Right: <b>real</b> grok-4.5 rollouts against our blobfish-generated world over MCP, scored by executable VCode.</div>
  <div class="cols">
    <div class="panel">
      <h2>CRMArena · GPT-4o (react) · interactive B2B org</h2>
      <div class="note">Source: <span class="mono">results/shared/b2b/multi-turn/*.json</span> (Git LFS). Loop: &lt;thought&gt; → &lt;execute&gt; SOQL → "Salesforce instance output" → &lt;respond&gt;; graded by matching the submitted answer to ground truth.</div>
      ${arenaCards}
    </div>
    <div class="panel">
      <h2>Our world · grok-4.5 · MCP tool calls + VCode verification</h2>
      <div class="note">Source: <span class="mono">sim/logs/*.jsonl</span> (this repo's runs against world <span class="mono">sbx_7d7d8fedcecb4458</span>). Loop: MCP tools/call against session-isolated SQLite; verdict from executable assertions on before/after state + trace.</div>
      ${ourCards}
      ${gymNote}
    </div>
  </div>
  <footer>Simulation only — synthetic data. CRMArena trajectories © Salesforce AI Research (repo LFS artifacts), shown for comparison. Not affiliated with Morgan Stanley or Salesforce.</footer>
</div></body></html>`;

writeFileSync(join(ROOT, "dashboard", "traces.html"), html);
console.log(`dashboard/traces.html — arena episodes: ${arena.episodes.length}, our episodes: ${ourPicks.length}, gym dirs: ${gymRunDirs.length}`);
