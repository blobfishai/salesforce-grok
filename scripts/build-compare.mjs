#!/usr/bin/env node
/**
 * Build dashboard/compare.html — CRMArena tasks vs this world's API-generated tasks,
 * plus the tool inventory and the Salesforce MCP spec chain (IR -> manifest -> code).
 */
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const PKG = join(ROOT, "world", "blobfish", "package", "sbx_7d7d8fedcecb4458");
const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const clip = (s, n) => { s = String(s ?? ""); return s.length > n ? s.slice(0, n) + "…" : s; };

const ref = JSON.parse(readFileSync(join(ROOT, "data", "reference", "crmarena-samples.json"), "utf8"));
const tasksJsonl = readFileSync(join(PKG, "tasks.jsonl"), "utf8").trim().split("\n").map((l) => JSON.parse(l));
const worldRaw = JSON.parse(readFileSync(join(PKG, "world.json"), "utf8"));
const world = worldRaw.world ?? worldRaw;
const manifest = JSON.parse(readFileSync(join(PKG, "mcp-assets.json"), "utf8"));
const ir = JSON.parse(readFileSync("/Users/samuelchien/dev/blobfish-0/products/website/data/service-specs/salesforce.ir.json", "utf8"));
const sfPy = readFileSync(join(PKG, "tools", "salesforce.py"), "utf8");

// merged grok results
const flakeDir = join(ROOT, "data", "flake");
const trials = readdirSync(flakeDir).filter((f) => f.endsWith(".json"))
  .flatMap((f) => (JSON.parse(readFileSync(join(flakeDir, f), "utf8")).trialsRaw ?? []))
  .filter((t) => !t.infraError);
const rec = {};
for (const t of trials) { const b = (rec[t.taskId] ??= { p: 0, n: 0 }); b.n++; if (t.passed) b.p++; }
const grokChip = (id) => {
  const b = rec[id];
  if (!b) return `<span class="chip mut">not scanned</span>`;
  const cls = b.p === b.n ? "good" : b.p === 0 ? "crit" : "warn";
  const icon = b.p === b.n ? "✓" : b.p === 0 ? "✗" : "≈";
  return `<span class="chip ${cls}">${icon} grok-4.5 ${b.p}/${b.n}</span>`;
};

// ---- pick representative samples
const pick = (ds, t) => ref.samples.find((s) => s.dataset === ds && s.task === t);
const arenaPicks = [
  pick("CRMArena", "knowledge_qa"), pick("CRMArena", "case_routing"), pick("CRMArena", "handle_time"),
  pick("CRMArena", "policy_violation_identification"), pick("CRMArena", "monthly_trend_analysis"),
  pick("CRMArenaPro", "lead_qualification"), pick("CRMArenaPro", "quote_approval"),
  pick("CRMArenaPro", "invalid_config"), pick("CRMArenaPro", "wrong_stage_rectification"),
  pick("CRMArenaPro", "private_customer_information"),
].filter(Boolean);

const ourPickIds = ["task_004", "task_012", "task_024", "task_014", "task_002", "task_015", "task_005", "task_026"];
const ourPicks = ourPickIds.map((id) => tasksJsonl.find((t) => t.task_id === id)).filter(Boolean);
const verifiers = Object.fromEntries((world.verifiers ?? []).map((v) => [v.task_id, v]));

const arenaCard = (s) => `
  <div class="card">
    <div class="row"><span class="chip blue">${esc(s.dataset)}</span><span class="chip mut">${esc(s.task)}</span><span class="chip mut">${esc(s.metric)}</span></div>
    <div class="q">${esc(clip(s.query, 300))}</div>
    <div class="a"><b>ground truth:</b> <code>${esc(clip(JSON.stringify(s.answer), 110))}</code></div>
    ${s.persona ? `<div class="p">persona: ${esc(clip(s.persona, 100))}</div>` : ""}
  </div>`;

const ourCard = (t) => {
  const v = verifiers[t.task_id];
  const nAssert = v ? (String(v.vcode ?? "").match(/chk\(/g) ?? []).length : null;
  const hops = Array.isArray(t.walk) ? t.walk.length : (t.steps?.length ?? null);
  return `
  <div class="card">
    <div class="row"><span class="chip blue">${esc(t.task_id)}</span><span class="chip mut">${esc(t.difficulty_tier ?? "?")}</span>${hops ? `<span class="chip mut">${hops} hop walk</span>` : ""}${grokChip(t.task_id)}</div>
    <div class="q">${esc(clip(t.prompt, 300))}</div>
    <div class="a"><b>verifier:</b> executable VCode — ${nAssert ?? "?"} assertions over before/after DB state + trace (row pins, read-before-write, collateral guards)</div>
    <div class="p">tables: ${esc((t.tables_affected ?? []).join(", "))} · declared effects: ${esc(clip(JSON.stringify(t.expected_state_changes ?? t.effects ?? []), 90))}</div>
  </div>`;
};

// ---- tools inventory
const assets = (Array.isArray(manifest.assets) ? manifest.assets : Object.values(manifest.assets ?? {}))
  .map((a) => ({ ns: a.namespace ?? a.name, n: (a.tool_names ?? a.tools ?? []).length }))
  .sort((a, b) => b.n - a.n);
const sfAsset = (Array.isArray(manifest.assets) ? manifest.assets : Object.values(manifest.assets ?? {})).find((a) => (a.namespace ?? a.name) === "salesforce");
const toolType = Object.fromEntries((world.tools ?? []).map((t) => [t.name, t.type]));
const sfTools = (sfAsset?.tool_names ?? []).map((full) => {
  const bare = full.split(".").pop();
  return { full, bare, type: toolType[bare] ?? "?" };
});
const nsBar = () => {
  const max = Math.max(...assets.map((a) => a.n));
  const W = 520, padL = 110, rowH = 26;
  let s = "";
  assets.forEach((a, i) => {
    const y = 6 + i * rowH, w = Math.max(3, (W - padL - 50) * (a.n / max));
    s += `<text x="${padL - 8}" y="${y + 13}" text-anchor="end" class="ax">${esc(a.ns)}</text>
          <rect x="${padL}" y="${y}" width="${w}" height="15" rx="4" fill="var(--series-1)"/>
          <text x="${padL + w + 7}" y="${y + 12}" class="val">${a.n}</text>`;
  });
  return `<svg viewBox="0 0 ${W} ${assets.length * rowH + 10}" role="img" aria-label="tools per MCP namespace">${s}</svg>`;
};

const irOps = (ir.operations ?? []).slice(0, 10).map((o) => `<tr><td class="mono">${esc(o.id ?? o.name)}</td><td>${esc(clip(o.summary ?? o.description, 70))}</td></tr>`).join("");
const lifecycleSnippet = sfPy.slice(sfPy.indexOf('"lifecycles"'), sfPy.indexOf('"lifecycles"') + 220);
const schemaTool = (world.tools ?? []).find((t) => t.name === "update_status_lead");

const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Tasks: CRMArena vs API-generated world · Tools & Salesforce MCP specs</title>
<style>
  :root { color-scheme: dark;
    --page:#0d0d0d; --surface-1:#1a1a19; --ink:#ffffff; --ink-2:#c3c2b7; --muted:#898781;
    --grid:#2c2c2a; --border:rgba(255,255,255,.10);
    --series-1:#3987e5; --good:#0ca30c; --warn:#fab219; --crit:#d03b3b; }
  * { box-sizing:border-box; margin:0; }
  body { background:var(--page); color:var(--ink); font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif; padding:24px; }
  .wrap { max-width:1240px; margin:0 auto; }
  h1 { font-size:20px; font-weight:650; margin-bottom:4px; }
  h2 { font-size:15px; font-weight:650; margin:0 0 4px; }
  .sub { color:var(--ink-2); margin-bottom:16px; }
  .cols { display:grid; grid-template-columns:1fr 1fr; gap:14px; align-items:start; }
  .panel { background:var(--surface-1); border:1px solid var(--border); border-radius:12px; padding:14px; }
  .panel .note { color:var(--ink-2); font-size:12.5px; margin-bottom:10px; }
  .card { border:1px solid var(--grid); border-radius:10px; padding:10px 12px; margin-bottom:10px; }
  .card .row { display:flex; flex-wrap:wrap; gap:6px; margin-bottom:6px; }
  .card .q { font-size:13px; margin-bottom:6px; }
  .card .a { font-size:12.5px; color:var(--ink-2); }
  .card .p { font-size:11.5px; color:var(--muted); margin-top:4px; }
  code, .mono { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:12px; }
  .chip { font-size:11px; font-weight:600; border-radius:999px; padding:1px 8px; border:1px solid var(--grid); color:var(--ink-2); white-space:nowrap; }
  .chip.blue { color:var(--series-1); border-color:var(--series-1); }
  .chip.good { color:var(--good); border-color:var(--good); }
  .chip.warn { color:var(--warn); border-color:var(--warn); }
  .chip.crit { color:var(--crit); border-color:var(--crit); }
  .chip.mut { }
  table { width:100%; border-collapse:collapse; font-size:12.5px; }
  th { text-align:left; color:var(--muted); font-size:11px; padding:5px 8px; border-bottom:1px solid var(--grid); }
  td { padding:5px 8px; border-bottom:1px solid var(--grid); vertical-align:top; color:var(--ink-2); }
  td:first-child { color:var(--ink); }
  .dim td:first-child { font-weight:600; width:170px; }
  svg { width:100%; height:auto; display:block; }
  .ax { font:11px system-ui,sans-serif; fill:var(--muted); }
  .val { font:600 11px system-ui,sans-serif; fill:var(--ink-2); }
  .grid2 { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-top:14px; }
  pre { background:var(--page); border:1px solid var(--grid); border-radius:8px; padding:10px; font-size:11.5px; overflow-x:auto; color:var(--ink-2); }
  .toolgrid { display:grid; grid-template-columns:repeat(2,1fr); gap:4px 10px; }
  .toolgrid .t { display:flex; justify-content:space-between; border-bottom:1px solid var(--grid); padding:3px 0; font-size:12px; }
  .rw { font-size:10.5px; font-weight:700; }
  .rw.read { color:var(--series-1); }
  .rw.write { color:var(--warn); }
  footer { color:var(--muted); font-size:12px; margin-top:16px; }
  .mb { margin-bottom:14px; }
</style></head>
<body><div class="wrap">
  <div id="part1">
  <h1>Tasks: CRMArena (Salesforce AI Research) vs the API-generated world</h1>
  <div class="sub">Left: real task instances from the CRMArena / CRMArena-Pro datasets (HuggingFace). Right: tasks from world <span class="mono">sbx_7d7d8fedcecb4458</span>, generated by the blobfish.ai API from our anchor corpus — with grok-4.5's measured record.</div>

  <div class="cols">
    <div class="panel">
      <h2>CRMArena · 9 task types × 1,170 instances — CRMArena-Pro · 22 types × 2,140 (b2b)</h2>
      <div class="note">Q&A-style: agent explores a static Salesforce org, returns an answer graded by exact/fuzzy match.</div>
      ${arenaPicks.map(arenaCard).join("")}
    </div>
    <div class="panel">
      <h2>This world · 27 verifier-backed tasks (API-generated)</h2>
      <div class="note">State-mutating: agent executes tool walks in a session-isolated SQLite world; scored by executable VCode assertions.</div>
      ${ourPicks.map(ourCard).join("")}
    </div>
  </div>

  <div class="panel" style="margin-top:14px">
    <h2>Structural comparison</h2>
    <table class="dim">
      <tr><td>Provenance</td><td>Hand-built benchmark over a curated synthetic Salesforce org (fixed datasets)</td><td>Generated per request by API: research pipeline → tool graph → random-walk tasks → acceptance gate → calibration</td></tr>
      <tr><td>Task style</td><td>Lookup / analytics / policy Q&A (+ interactive splits); 16 persona flavors</td><td>Multi-hop state changes (lead lifecycle, queue processing, workflow paths) + analytics; persona role clusters</td></tr>
      <tr><td>Verification</td><td>Ground-truth answer string; exact_match / fuzzy_match</td><td>Executable VCode over before/after DB snapshots + tool trace: row-pinned values, reads-before-writes, no-collateral guards, append-only audit</td></tr>
      <tr><td>Difficulty iteration</td><td>Fixed dataset releases (CRMArena → Pro)</td><td>API waves: target_failure_rate, mock_services graph density, /regenerate (walk depth), /calibrate (escalation: scrubbed tools, obscured refs, distractor rows)</td></tr>
      <tr><td>Frontier measurement</td><td>Leaderboard pass rates</td><td>Per-task multi-trial flake scan: pass 69% @1–5 tool calls → 28% @6–10 → 0% @21+ (grok-4.5, 84 trials)</td></tr>
    </table>
  </div>

  </div>
  <h1 style="margin-top:22px">Tools created & the Salesforce MCP spec chain</h1>
  <div class="sub">104 tools across 8 MCP namespaces (manifest <span class="mono">blobfish.mcp-assets.v1</span>) — and the three spec documents behind <span class="mono">salesforce.*</span>.</div>

  <div class="cols">
    <div class="panel">
      <h2>Tools per MCP namespace (104 total)</h2>
      ${nsBar()}
      <h2 style="margin-top:12px">salesforce.* — ${sfTools.length} tools</h2>
      <div class="toolgrid">
        ${sfTools.map((t) => `<div class="t"><span class="mono">${esc(t.full)}</span><span class="rw ${t.type === "write" ? "write" : "read"}">${esc(t.type)}</span></div>`).join("")}
      </div>
    </div>
    <div class="panel">
      <h2>Spec 1 — forge service IR (<span class="mono">salesforce.ir.json</span>, blobfish-0)</h2>
      <div class="note">${esc(ir.title ?? "Salesforce service spec")} · irVersion ${esc(ir.irVersion)} · ${(ir.operations ?? []).length} operations over ${(Array.isArray(ir.entities) ? ir.entities.length : Object.keys(ir.entities ?? {}).length)} entities (${esc((Array.isArray(ir.entities) ? ir.entities : Object.keys(ir.entities ?? {})).map((e) => e.name ?? e).join(", "))})</div>
      <table><thead><tr><th>operation</th><th>summary</th></tr></thead><tbody>${irOps}</tbody></table>
    </div>
  </div>

  <div class="grid2">
    <div class="panel">
      <h2>Spec 2 — world MCP manifest (<span class="mono">mcp-assets.json</span>)</h2>
      <div class="note">The per-world MCP contract: transport, session isolation, digests.</div>
      <pre>${esc(JSON.stringify({ schema_version: manifest.schema_version, salesforce: { namespace: sfAsset?.namespace, asset_ref: sfAsset?.asset_ref, behavior_digest: clip(sfAsset?.behavior_digest, 24), transport: sfAsset?.transport } }, null, 1))}</pre>
    </div>
    <div class="panel">
      <h2>Spec 3 — generated tool contract (<span class="mono">tools/salesforce.py</span> + tool schema)</h2>
      <div class="note">Declared lifecycles are the world's law — the exact rules grok-4.5 must look up instead of assuming CRM priors.</div>
      <pre>${esc(lifecycleSnippet)}…</pre>
      <pre>update_status_lead.input_schema =
${esc(JSON.stringify(schemaTool?.input_schema ?? {}, null, 1))}</pre>
    </div>
  </div>

  <footer>Simulation only — synthetic data; not affiliated with Morgan Stanley or Salesforce. CRMArena samples © Salesforce AI Research (HuggingFace: Salesforce/CRMArena, Salesforce/CRMArenaPro), shown for comparison.</footer>
</div>
<script>if (location.hash === "#specs") { document.getElementById("part1").style.display = "none"; document.body.style.paddingTop = "10px"; }</script>
</body></html>`;

writeFileSync(join(ROOT, "dashboard", "compare.html"), html);
console.log(`dashboard/compare.html written — ${arenaPicks.length} arena samples, ${ourPicks.length} world tasks, ${sfTools.length} salesforce tools`);
