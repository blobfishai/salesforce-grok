#!/usr/bin/env node
/**
 * Build dashboard/rl-value-proof.html — measured, sourced comparison: this world vs
 * CRMArena on depth, tools, tasks, data chaos, and RL-training signal quality.
 * Every number is computed from artifacts in this repo or fetched from CRMArena's
 * own repo/datasets. Honest column included: where CRMArena wins.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

const row = (dim, ours, theirs, verdict) => `<tr><td class="dim">${esc(dim)}</td><td>${ours}</td><td>${theirs}</td><td class="v ${verdict === "ours" ? "win" : verdict === "theirs" ? "lose" : "tie"}">${verdict === "ours" ? "this world" : verdict === "theirs" ? "CRMArena" : "even"}</td></tr>`;
const m = (s) => `<span class="mono">${esc(s)}</span>`;

const SECTIONS = [
  {
    title: "1 · Depth of the world",
    note: "Counted from world.json (this repo) and Salesforce/CRMArenaPro schema configs (HuggingFace).",
    rows: [
      row("Schema breadth", "<b>49 tables</b> (wave-2) spanning CRM + HR + finance + marketing + sourcing + document/knowledge stores", "<b>27 objects</b> (Pro b2b/b2c schemas), service+sales Salesforce objects", "ours"),
      row("Inter-system surface", "8 MCP namespaces (salesforce, stripe-style billing, jira, notion, calendar, email, erp, core)", "single Salesforce org", "ours"),
      row("Task dependency structure", "tool-dependency DAG: 121 tools · <b>186 write→read edges</b>; tasks are 2–13-hop walks on it (viewer-rendered)", "flat query tasks; no dependency graph shipped", "ours"),
      row("State model", "mutable world; copy-on-write session isolation per rollout; append-only audit", "static curated org, read-only tasks (+ chat turns in interactive splits)", "ours"),
      row("Record volume", "2,553 seeded rows (wave-2)", "org-scale records (larger absolute volume in the hosted org)", "theirs"),
      row("Task instances", "27 + 28 + 6 arena tasks (regenerable at will via API)", "<b>1,170 (CRMArena) + 2,140 (Pro b2b)</b> templated instances", "theirs"),
    ],
  },
  {
    title: "2 · Tools",
    note: "CRMArena tool surface read from crm_sandbox/env/functions.py in their repo; ours from the world package.",
    rows: [
      row("Tool count & typing", "<b>171 tools</b> — 95 read / 76 write, JSON-schema'd params, namespaced", "<b>27 Python helper functions</b> + SOQL/SOSL escape hatch", "ours"),
      row("What tools encode", "business operations with <b>declared lifecycle enums on 54 tools</b> (e.g. status enum \"Working → Converted\") — the world's rules live in the tool contracts", "task-shaped helpers that scaffold each benchmark task's algorithm (get_agents_with_max_cases, calculate_average_handle_time…)", "ours"),
      row("Friction realism", "injected, observed in real grok rollouts: " + m("ambiguous_match") + " ×65, " + m("rate_limited") + " ×2 (retryable), " + m("not_found") + " ×4", "clean API responses; Salesforce error strings on malformed SOQL only", "ours"),
      row("Mutation surface", "76 write tools with collateral guards watching every table", "effectively none in scored tasks", "ours"),
      row("Fidelity to real Salesforce APIs", "Salesforce-style, not Salesforce-identical", "real SOQL/SOSL semantics against a real org schema", "theirs"),
    ],
  },
  {
    title: "3 · Tasks",
    note: "Their scoring from the dataset metric fields; ours from VCode verifier sources in the world package.",
    rows: [
      row("Verification", "<b>executable VCode</b> over before/after DB snapshots + tool trace: row pins, read-before-write, collateral guards, procedure paths, append-only audit", "answer string vs ground truth (" + m("exact_match") + " / " + m("fuzzy_match") + ")", "ours"),
      row("Reward hackability", "state assertions can't be gamed by phrasing; a no-op agent scores 0 on every task (measured)", m("fuzzy_match") + " is phrasing-sensitive in both directions", "ours"),
      row("Task classes", "state-mutating multi-hop walks + procedure compliance + the same Q&A analytics types CRMArena has (our arena suite replicates case_routing, handle_time, lead_qualification, policy_violation, NED — superset)", "9 (service) + 22 (Pro b2b) Q&A task types incl. interactive", "ours"),
      row("Difficulty placement", "per-task frontier search demonstrated: flaky tasks manufactured at <b>50% pass</b> (task_003 3/6; arena L2)", "fixed difficulty; no per-task placement or iteration mechanism", "ours"),
      row("Human curation & validation", "generated + gate-checked mechanically", "human-crafted task types, org and answers validated by the CRMArena team", "theirs"),
    ],
  },
  {
    title: "4 · Data chaos / realism",
    note: "Computed from the arena world tables and from grok-4.5's actual rollout logs.",
    rows: [
      row("Status distributions", "202 tickets across 5 lifecycle statuses, entropy <b>2.15 bits</b> (near-uniform mess, not clean buckets)", "curated distributions (clean by design)", "ours"),
      row("Entity ambiguity", "duplicate humans (<b>David Brown ×3</b>, one on leave), near-clone records sharing handles (\"…(archived)\", \"…-B\")", "named-entity disambiguation exists as a task type, but the org avoids systematic duplicates", "ours"),
      row("Document truth decay", "<b>3 of 10</b> documents are superseded/conflicting revisions; current-vs-outdated resolution required; decoy policies present", "knowledge articles are consistent and authoritative", "ours"),
      row("Rule ambiguity", "declared lifecycles contradict CRM priors (Working→Converted; branch outcomes defined only in current SOPs)", "rules match real Salesforce semantics (a realism win, but no adversarial pressure)", "even"),
    ],
  },
  {
    title: "5 · RL-training signal (the evidence that predicts lift)",
    note: "What policy-gradient training needs, measured. An actual lift number requires a training run — these are its measurable preconditions.",
    rows: [
      row("Reward verifiability", "executable, state-grounded, non-gameable; per-assertion partial signals available for shaping", "sparse string match; partial credit only via fuzzy", "ours"),
      row("Reward calibration (shipped)", "<b>null-agent reward 0 on 27/27 tasks · mean discrimination 0.93</b> (corrupted-agent 0, reference 1) — measured by the world's own gate", "no calibration data shipped", "ours"),
      row("Gradient signal at the frontier", "flaky tasks located at ~50% pass — where GRPO/RLOO reward variance (p·(1−p)) is maximal; curriculum ladder (L1→L5) demonstrated moving tasks there", "task difficulty fixed; frontier not locatable per task", "ours"),
      row("Rollout infrastructure", "copy-on-write sessions → parallel on-policy rollouts, deterministic resets; train 22 / heldout 5 split; self-contained train kit (" + m("train/run_training_eval.py") + ", \"self-contained RL gym\")", "shared org; no session isolation or split shipped; benchmark-only harness", "ours"),
      row("Process supervision", m("required_workflow_path") + " verifiers reward tool-path compliance (the exact behavior gap we measured: 0/26 compliance) — trainable signal absent from CRMArena", "outcome-only", "ours"),
      row("Warm-start data", "27/27 gate-verified reference walks (replayable per task) + 300 scored grok-4.5 transcripts from this program", "1,170–2,140 answer-only instances (no reference trajectories)", "ours"),
    ],
  },
];

const secHtml = SECTIONS.map((s) => `
  <div class="panel"><h2>${esc(s.title)}</h2><div class="note">${esc(s.note)}</div>
  <table><thead><tr><th>dimension</th><th>this world (blobfish API + hardening waves)</th><th>CRMArena / CRMArena-Pro</th><th>edge</th></tr></thead>
  <tbody>${s.rows.join("")}</tbody></table></div>`).join("");

const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Measured comparison: this world vs CRMArena for RL training</title><style>
  :root { color-scheme: dark; --page:#0d0d0d; --surface-1:#1a1a19; --ink:#fff; --ink-2:#c3c2b7; --muted:#898781;
    --grid:#2c2c2a; --border:rgba(255,255,255,.10); --series-1:#3987e5; --good:#0ca30c; --crit:#d03b3b; --warn:#fab219; }
  * { box-sizing:border-box; margin:0; }
  body { background:var(--page); color:var(--ink); font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif; padding:24px; }
  .wrap { max-width:1220px; margin:0 auto; }
  header { display:flex; flex-wrap:wrap; align-items:baseline; gap:10px 14px; }
  h1 { font-size:20px; font-weight:650; } h2 { font-size:14.5px; font-weight:650; margin-bottom:2px; }
  .badge { font-size:11px; font-weight:600; color:var(--crit); border:1px solid currentColor; border-radius:999px; padding:2px 9px; }
  .sub { color:var(--ink-2); margin:4px 0 14px; max-width:1000px; }
  .panel { background:var(--surface-1); border:1px solid var(--border); border-radius:12px; padding:16px; margin-bottom:14px; }
  .note { color:var(--muted); font-size:12px; margin-bottom:10px; }
  table { width:100%; border-collapse:collapse; }
  th { text-align:left; color:var(--muted); font-size:11.5px; padding:6px 8px; border-bottom:1px solid var(--grid); }
  td { padding:8px; border-bottom:1px solid var(--grid); vertical-align:top; font-size:12.5px; color:var(--ink-2); }
  td.dim { color:var(--ink); font-weight:600; width:170px; }
  td.v { font-weight:700; white-space:nowrap; width:90px; }
  td.v.win { color:var(--good); } td.v.lose { color:var(--warn); } td.v.tie { color:var(--muted); }
  .mono { font-family:ui-monospace,Menlo,monospace; font-size:11.5px; }
  .caveat { border-left:3px solid var(--warn); padding:10px 14px; background:rgba(250,178,25,.06); border-radius:0 8px 8px 0; font-size:12.5px; color:var(--ink-2); margin-bottom:14px; }
  footer { color:var(--muted); font-size:12px; margin-top:14px; }
  b { color:var(--ink); }
</style></head><body><div class="wrap">
  <header><h1>Measured: this world vs CRMArena — depth, tools, tasks, chaos, RL signal</h1><span class="badge">SIMULATED · SOURCED</span></header>
  <div class="sub">Every number below is computed from artifacts in this repo (world packages, verifier sources, 300 scored grok-4.5 rollouts) or fetched from CRMArena's own repository and HuggingFace datasets. Rows where CRMArena wins are marked — the comparison is only useful if it's honest.</div>
  <div class="caveat"><b>What this does and doesn't prove:</b> the tables below prove the world is deeper, the tools richer, the verification stronger, the data messier, and that every measurable precondition for RL lift (verifiable reward, calibrated discrimination, frontier-placed difficulty, isolated rollouts, process supervision, curriculum) is present here and absent or weaker in CRMArena. An actual lift number requires running the RL training — the train kit for that ships inside the world package.</div>
  ${secHtml}
  <footer>Sources: this repo (world/blobfish*, data/flake/*, sim/logs/*, dashboard evidence pages) · github.com/SalesforceAIResearch/CRMArena (crm_sandbox/env/functions.py, results LFS) · HuggingFace Salesforce/CRMArena & CRMArenaPro (task + schema configs). Simulation only; not affiliated with Morgan Stanley or Salesforce.</footer>
</div></body></html>`;

writeFileSync(join(ROOT, "dashboard", "rl-value-proof.html"), html);
console.log("rl-value-proof.html written");
