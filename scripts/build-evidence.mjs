#!/usr/bin/env node
/**
 * Evidence page: proof that tasks ran in the wave-6 world, per-task anchor
 * grounding + realism chain, CRMArena 3-way coverage comparison, the in-world
 * document inventory, and the cross-world failure-mode summary.
 * -> dashboard/evidence.html (screenshot-friendly, self-contained)
 */
import { readFileSync, writeFileSync, readdirSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;");

const w6raw = JSON.parse(readFileSync(join(ROOT, "world", "blobfish-wave6", "world.json"), "utf8"));
const w6 = w6raw.world ?? w6raw;
const w5raw = JSON.parse(readFileSync(join(ROOT, "world", "blobfish-wave5", "world.json"), "utf8"));
const w5 = w5raw.world ?? w5raw;
const flash = JSON.parse(readFileSync(join(ROOT, "data", "flake", "w6-flash-validation.json"), "utf8"));
const ftasks = Object.fromEntries(flash.tasks.map((t) => [t.taskId, t]));
const quality = JSON.parse(readFileSync(join(ROOT, "world", "blobfish-wave6", "quality.json"), "utf8"));
const census = JSON.parse(readFileSync(join(ROOT, "data", "coverage", "census-items.json"), "utf8"));
const verdicts = JSON.parse(readFileSync(join(ROOT, "data", "coverage", "verdicts.json"), "utf8"));
const vByName = Object.fromEntries(verdicts.map((v) => [v.name, v]));

// ---- anchor-doc grounding per task: match task tables/tools/prompt to corpus topics
const CORPUS_TOPICS = [
  [/lead/, ["01-lead-management-sop.md", "02-lead-scoring-policy.md", "21-enrichment-waterfall-config.md", "22-inbound-routing-matrix.md"]],
  [/account|tiering/, ["03-account-tiering.md", "30-territory-rules-of-engagement.md"]],
  [/opportunit|stage|pipeline|forecast/, ["04-opportunity-stage-gates.md", "25-pipeline-inspection-rules.md", "26-forecast-commit-standards.md", "12-forecast-methodology.md"]],
  [/quote|cpq|discount|deal_desk|pricing|price/, ["05-cpq-discount-policy.md", "06-deal-desk-charter.md", "43-artifact-pricing-rate-card.md"]],
  [/compliance|regulat/, ["07-compliance-review-checklist.md", "regulations-compliance-regimes.md"]],
  [/finance|approval|expense|budget/, ["08-finance-approval-thresholds.md"]],
  [/order|activation/, ["09-order-activation-runbook.md", "42-artifact-order-form-summit.md"]],
  [/case|ticket|support|sla/, ["10-case-management-sla.md"]],
  [/activity|task/, ["11-activity-logging-standards.md"]],
  [/product|catalog/, ["13-product-catalog.md"]],
  [/renewal|churn|health/, ["14-renewal-playbook.md", "28-renewal-expansion-runbook.md", "27-customer-success-health-model.md"]],
  [/territory|region/, ["15-territory-model.md", "30-territory-rules-of-engagement.md"]],
  [/dedupe|hygiene|merge|data_quality/, ["16-data-quality-rules.md"]],
  [/sequence|outbound|email|send|template/, ["17-outbound-sequencing-playbook.md", "18-email-template-library.md"]],
  [/call|transcript|meddic|conversation/, ["19-conversation-intelligence-standards.md", "39-artifact-call-transcript-summit.md", "40-artifact-call-transcript-meridian.md"]],
  [/meeting|calendar|schedul/, ["20-meeting-scheduling-sla.md"]],
  [/contract|clause|msa|sign|nda|sow/, ["23-clm-clause-library.md", "41-artifact-msa-ironwood.md"]],
  [/billing|invoice|dunning|payment|charge|subscription|stripe/, ["24-billing-dunning-policy.md"]],
  [/quota|commission|comp|split/, ["29-quota-comp-plan.md"]],
  [/campaign|marketing|mql|nurture|suppression/, ["31-mql-sql-handoff-sla.md", "32-campaign-catalog.md"]],
  [/battlecard|competitor|harborview|atlas|crestline/, ["33-battlecard-harborview.md", "34-battlecards-atlas-crestline.md", "44-artifact-win-loss-q2-2026.md"]],
  [/rfp|questionnaire|proposal/, ["35-rfp-answer-library.md"]],
  [/partner|registration/, ["36-partner-deal-registration.md"]],
  [/webhook|integration|sync/, ["37-revops-integration-map.md"]],
  [/report|kpi|analytic|funnel/, ["38-analytics-kpi-definitions.md"]],
  [/hr|leave|employee/, ["personas_roles-crm-org.md"]],
];
function groundingDocs(task) {
  const hay = [task.prompt, ...(task.tables_affected ?? []), ...(task.walk ?? [])].join(" ").toLowerCase();
  const hits = new Set();
  for (const [re, docs] of CORPUS_TOPICS) if (re.test(hay)) docs.forEach((d) => hits.add(d));
  return [...hits].slice(0, 4);
}

// ---- section 1: task-run proof table + trace excerpts
const trialDir = join(ROOT, "data", "flake", ".trials");
function traceExcerpt(taskId) {
  const f = join(trialDir, `w6-flash-validation-${taskId}-t1.json`);
  if (!existsSync(f)) return null;
  const rec = JSON.parse(readFileSync(f, "utf8"));
  if (!rec.log || !existsSync(rec.log)) return null;
  const lines = readFileSync(rec.log, "utf8").trim().split("\n").map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
  const tools = lines.filter((l) => l.type === "tool");
  const head = tools.slice(0, 4).map((t) => `→ ${t.name}(${JSON.stringify(t.args).slice(0, 90)})\n   ${String(t.result).replace(/\s+/g, " ").slice(0, 110)}`);
  const verify = lines.filter((l) => l.type === "verify").at(-1);
  return { calls: tools.length, head: head.join("\n"), more: Math.max(0, tools.length - 4), verdict: rec.passed };
}

const taskRows = w6.tasks.map((t) => {
  const ft = ftasks[t.task_id] ?? {};
  const docs = groundingDocs({ prompt: t.prompt, tables_affected: t.tables_affected, walk: t.walk });
  return { id: t.task_id, prompt: (t.prompt ?? "").slice(0, 150), tier: t.difficulty_tier, tables: (t.tables_affected ?? []).slice(0, 4), walk: (t.walk ?? []).length, ft, docs, sem: typeof t.semantic_alignment === "object" ? t.semantic_alignment?.verdict : t.semantic_alignment, acc: t.acceptance_label, src: t.provenance?.source_workflow };
});

const runTable = `<table><thead><tr><th>Task</th><th>Prompt (trimmed)</th><th>Ref walk</th><th class="num">Flash result</th><th class="num">Avg calls</th><th>Failed assertions</th></tr></thead><tbody>` +
  taskRows.map((r) => {
    const cls = r.ft.class === "pass" ? "ok" : r.ft.class === "FLAKY" ? "flaky" : "bad";
    return `<tr><td class="mono">${r.id}</td><td class="sm">${esc(r.prompt)}…</td><td class="num">${r.walk}</td><td class="${cls}">${r.ft.passes ?? "—"}/${r.ft.trials ?? "—"}</td><td class="num">${r.ft.avgToolCalls ?? "—"}</td><td class="sm mono">${esc(Object.keys(r.ft.failedConditions ?? {}).slice(0, 3).join(", "))}</td></tr>`;
  }).join("") + `</tbody></table>`;

const excerptIds = ["task_010", "task_016", "task_001"];
const excerpts = excerptIds.map((id) => {
  const e = traceExcerpt(id);
  if (!e) return "";
  return `<div class="ex"><div class="exhead">${id} · deepseek-v4-flash · ${e.calls} tool calls · verifier: ${e.verdict ? "PASSED" : "failed"}</div><pre>${esc(e.head)}${e.more ? `\n… ${e.more} more calls, then POST /verify/${id} with the full trace` : ""}</pre></div>`;
}).join("");

// ---- section 2: CRMArena 3-way
const crmItems = census.filter((i) => (i.source_class ?? "").startsWith("CRM agent benchmarks"));
const crmRows = crmItems.map((i) => {
  const key = i.name.toLowerCase().replace(/[\s-]/g, "_");
  const v = vByName[key] ?? vByName[i.name];
  return `<tr><td class="mono">${esc(i.name)}</td><td class="sm">${esc((i.definition ?? "").slice(0, 130))}</td><td class="${v ? (v.verdict === "covered" ? "ok" : v.verdict === "partial" ? "flaky" : "bad") : ""}">${v?.verdict ?? "?"}</td><td class="sm">${esc((v?.evidence ?? []).slice(0, 3).join(", ").slice(0, 90) || v?.note?.slice(0, 90) || "")}</td></tr>`;
}).join("");

const beyond = [
  ["State-mutation verification", "Every workflow task is graded on DB state diffs + collateral-damage assertions; CRMArena grades answer strings only — routing tasks return an ID, nothing is re-assigned."],
  ["Cross-system quote-to-cash", "Opportunity → quote (tiered discount authority) → sequential Deal Desk→Compliance→Finance approvals → order → Stripe-style subscription/invoice/dunning — CRMArena stays inside one org's query surface."],
  ["Document-grounded policy conflict", "48 in-world documents incl. superseded-vs-current SOP revisions with conditional rules; CRMArena has knowledge articles for QA but no conflicting-revision reasoning."],
  ["Outbound/GTM stack", "SendGrid-style suppression/bounces/domain-auth, campaign catalog, MQL→SAL gate, battlecards vs 3 fictional competitors, comp plans, partner deal-reg — absent from CRMArena's service-centric orgs."],
  ["Side-effect traps", "Lenient side-effectful sub-agent tools (document_agent) that punish flailing exploration — measured as the dominant real cross-model failure mode."],
  ["Frontier-driven difficulty", "Tasks escalated wave-over-wave against the measured model until they flicker; CRMArena templates are static (top tasks at 99%)."],
];
const notCovered = [
  ["Instance scale", "CRMArena-Pro ships 4,280 templated query instances; this world has dozens of deep tasks."],
  ["Live hosted Salesforce org", "Real API friction/governor limits vs our packaged simulation."],
  ["Simulated-user multi-turn at benchmark scale", "Pro runs LLM-user dialogues across all tasks; here multi-turn exists (run-interactive.mjs) but is not the default harness."],
  ["LLM-judged confidentiality track at scale", "480 confidentiality probes in Pro; here leak/refusal verification is a named partial (transcript-level assertions not yet built)."],
];

// ---- section 3: anchors per task
const anchorTable = `<table><thead><tr><th>Task</th><th>Grounding documents (in-world, queryable)</th><th>Source workflow</th><th>Alignment</th><th>Acceptance</th></tr></thead><tbody>` +
  taskRows.map((r) => `<tr><td class="mono">${r.id}</td><td class="sm">${r.docs.map((d) => `<span class="chip">${esc(d)}</span>`).join(" ") || "<span class='sm'>schema-anchored only</span>"}</td><td class="sm">${esc(r.src ?? (r.ft ? "graph walk over anchored tools" : ""))}</td><td class="sm">${esc(r.sem ?? "—")}</td><td class="sm">${esc(r.acc ?? "—")}</td></tr>`).join("") + `</tbody></table>`;

// ---- section 4: documents
function docList(world, label) {
  const rows = [];
  for (const tn of ["agent_documents", "agent_knowledge", "agent_playbooks", "matter_documents", "agent_files"]) {
    const t = world.tables.find((x) => x.name === tn);
    for (const r of t?.sample_rows ?? []) rows.push({ table: tn, id: r.id, title: String(r.title ?? r.name ?? "(untitled)").slice(0, 95), len: String(r.body ?? r.content ?? "").length });
  }
  return { label, rows };
}
const w6docs = docList(w6, "wave-6 (sbx_291042075d7547f4)");
const w5docs = docList(w5, "wave-5 (sbx_36847f702cef4cb4)");
const docsHtml = [w6docs, w5docs].map((d) => `<h3>${d.label} — ${d.rows.length} documents</h3><div class="tablewrap"><table><thead><tr><th>Store</th><th>Id</th><th>Title</th><th class="num">Chars</th></tr></thead><tbody>` +
  d.rows.map((r) => `<tr><td class="mono sm">${r.table}</td><td class="num">${r.id}</td><td class="sm">${esc(r.title)}</td><td class="num">${r.len.toLocaleString()}</td></tr>`).join("") + `</tbody></table></div>`).join("");

// ---- section 5: failure modes (wave-5 multi-model + wave-6 flash)
const w6fails = {};
for (const t of flash.trialsRaw) for (const c of t.failedConditions ?? []) w6fails[c] = (w6fails[c] ?? 0) + 1;
const w6failRows = Object.entries(w6fails).sort((a, b) => b[1] - a[1]).slice(0, 10)
  .map(([c, n]) => `<tr><td class="mono sm">${esc(c)}</td><td class="num">${n}</td><td class="sm">${c === "required_workflow_path" ? "ADVISORY — undocumented-order artifact per audit protocol" : c.startsWith("rows_inserted") ? "missing required record creation (deep multi-object tasks)" : c.startsWith("no_offtask") || c.startsWith("no_undeclared") ? "collateral writes during deep exploration" : "wrong end-state"}</td></tr>`).join("");

const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Evidence — tasks, anchors, documents, failure modes</title>
<style>
body{font:14.5px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;color:#0f172a;background:#f8fafc;margin:0;padding:28px;max-width:1160px;margin-inline:auto}
h1{font-size:24px;margin:0 0 4px}h2{font-size:19px;margin:36px 0 8px;border-bottom:2px solid #e2e8f0;padding-bottom:6px}h3{font-size:15.5px;margin:18px 0 6px}
.sub{color:#64748b;font-size:12.5px}.sm{font-size:12px}.mono{font-family:ui-monospace,Menlo,monospace;font-variant-numeric:tabular-nums}
.tablewrap{overflow-x:auto;background:#fff;border:1px solid #e2e8f0;border-radius:8px;margin:10px 0}
table{border-collapse:collapse;width:100%;font-size:12.5px}
th,td{border-top:1px solid #e2e8f0;padding:5px 9px;text-align:left;vertical-align:top}
thead th{border-top:none;background:#f1f5f9;font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:#64748b}
td.num,th.num{text-align:right;font-family:ui-monospace,Menlo,monospace}
td.ok{background:#dcfce7;text-align:center}td.bad{background:#fee2e2;text-align:center}td.flaky{background:#fef9c3;text-align:center}
.chip{display:inline-block;background:#eef2f7;border:1px solid #dce3ea;border-radius:4px;padding:1px 7px;font-size:11px;font-family:ui-monospace,Menlo,monospace;margin:1px}
.ex{background:#0f172a;color:#e2e8f0;border-radius:8px;margin:10px 0;overflow:hidden}
.exhead{background:#1e293b;padding:6px 12px;font-size:12px;color:#94a3b8}
pre{margin:0;padding:11px;font:11.5px/1.5 ui-monospace,Menlo,monospace;white-space:pre-wrap}
.note{background:#eff6ff;border-left:4px solid #2563eb;padding:9px 13px;font-size:13px;margin:12px 0}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:16px}@media(max-width:900px){.cols{grid-template-columns:1fr}}
ul{padding-left:18px;font-size:13px}li{margin:4px 0}
</style></head><body>
<h1>Evidence: the wave-6 world in operation</h1>
<p class="sub">World sbx_291042075d7547f4 · 214 tables / 205 tools / 48 in-world documents · all runs deepseek-v4-flash (validation-only policy) · generated ${new Date().toISOString().slice(0, 10)}</p>

<h2>1 · Proof of task runs — all 25 tasks × 2 trials ($${flash.totals.costUsd}, 0 infra errors)</h2>
${runTable ? `<div class="tablewrap">${runTable}</div>` : ""}
<h3>Raw trace excerpts (from the actual run transcripts)</h3>
${excerpts}
<div class="note">Every row is backed by per-trial JSON in <span class="mono">data/flake/.trials/w6-flash-validation-*.json</span> and a full JSONL transcript; the verifier runs server-side against the session's copy-on-write DB.</div>

<h2>2 · CRMArena / CRMArena-Pro coverage — three ways</h2>
<h3>Every CRMArena task type, and whether this world supports it</h3>
<div class="tablewrap"><table><thead><tr><th>CRMArena task</th><th>Definition</th><th>Here</th><th>Evidence / missing piece</th></tr></thead><tbody>${crmRows}</tbody></table></div>
<div class="cols">
<div><h3>What this world has that CRMArena doesn't</h3><ul>${beyond.map(([k, v]) => `<li><b>${k}.</b> ${v}</li>`).join("")}</ul></div>
<div><h3>What CRMArena has that this world doesn't</h3><ul>${notCovered.map(([k, v]) => `<li><b>${k}.</b> ${v}</li>`).join("")}</ul></div>
</div>

<h2>3 · Anchors per task, and why the tasks are realistic</h2>
<div class="note"><b>The realism chain:</b> 46 authored SOP/artifact documents (cross-referenced, shared constants) → blobfish thesis &amp; workflow graph → <b>119 schema anchors validated "ok"</b> against the actual tool implementations (quality.json anchor_validation) → tasks generated as walks over anchored tools, each carrying semantic-alignment and acceptance-evidence checks → deterministic verifiers → Flash-validated runs above. Grounding documents below are live in <span class="mono">agent_documents</span> and returned by <span class="mono">notion.query_documents</span>.</div>
<div class="tablewrap">${anchorTable}</div>

<h2>4 · All documents in the worlds</h2>
${docsHtml}

<h2>5 · Failure modes</h2>
<h3>Wave-6 (deepseek-v4-flash, 50 trials)</h3>
<div class="tablewrap"><table><thead><tr><th>Failed assertion</th><th class="num">Trials</th><th>Reading</th></tr></thead><tbody>${w6failRows}</tbody></table></div>
<div class="note">Depth frontier: ${flash.depthCurve.map((b) => `${b.bucket} → ${b.passRate === null ? "n/a" : Math.round(b.passRate * 100) + "%"} (${b.trials})`).join(" · ")}. Cross-model wave-5 failure anatomy (7 models, audited): <span class="mono">dashboard/failure-report-models.html</span>.</div>
</body></html>`;

writeFileSync(join(ROOT, "dashboard", "evidence.html"), html);
console.log(`evidence.html: ${taskRows.length} tasks, ${crmItems.length} CRMArena rows, ${w6docs.rows.length}+${w5docs.rows.length} docs`);
