#!/usr/bin/env node
/**
 * Generate docs/COVERAGE.md — the sales-domain coverage proof — from
 * data/coverage/{census-items,verdicts}.json and the wave-6 Flash validation.
 * Reproducible: rerun after editing verdicts or adding world capabilities.
 */
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const items = JSON.parse(readFileSync(join(ROOT, "data", "coverage", "census-items.json"), "utf8"));
const verdicts = JSON.parse(readFileSync(join(ROOT, "data", "coverage", "verdicts.json"), "utf8"));
const byName = Object.fromEntries(items.map((i) => [i.name.toLowerCase().replace(/[\s-]/g, "_"), i]));
const V = { covered: [], partial: [], gap: [], out_of_scope: [] };
for (const v of verdicts) (V[v.verdict] ?? (V[v.verdict] = [])).push(v);
for (const k of Object.keys(V)) V[k].sort((a, b) => a.name.localeCompare(b.name));

const flash = existsSync(join(ROOT, "data", "flake", "w6-flash-validation.json"))
  ? JSON.parse(readFileSync(join(ROOT, "data", "flake", "w6-flash-validation.json"), "utf8")) : null;

const inScope = verdicts.length - V.out_of_scope.length;
const pct = (n) => ((n / inScope) * 100).toFixed(0) + "%";
const kindOf = (n) => byName[n]?.kind ?? "?";
const srcOf = (n) => (byName[n]?.source ?? "").split(";")[0].slice(0, 70);

let md = `# Sales-Domain Coverage Proof — wave-6 world \`sbx_291042075d7547f4\`

> Generated ${new Date().toISOString().slice(0, 10)} by \`scripts/build-coverage-md.mjs\` from
> \`data/coverage/*.json\`. Question answered: *does this world support all the tasks,
> workflows, and evals of the sales-software domain?*

## Method

1. **Census (demand side).** Six parallel researchers enumerated the domain from primary
   sources: CRMArena + CRMArena-Pro (every one of the 9 + 19 task types, incl. the
   confidentiality track), non-CRM agent benchmarks (tau-bench, tau2, WorkBench,
   MCPEval servers, WebArena-class), the open-source AI-SDR/outbound ecosystem
   (github.com/topics/sales-automation, ai-sdr, cold-email), RevOps/admin-certification
   workflow canon, conversation-intelligence + document-centric capabilities
   (Gong/CUAD-style), and trust/safety evals. Result: **${items.length} deduplicated items**
   (${items.filter((i) => i.kind === "eval_task").length} eval tasks, ${items.filter((i) => i.kind === "workflow").length} workflows, ${items.filter((i) => i.kind === "tool_capability").length} tool capabilities), each with concrete
   environment requirements.
2. **Matching (supply side).** Four judges matched every item against the world's full
   inventory — 214 tables, 205 tools across 11 namespaces, the 46-document anchor corpus
   (now seeded in-world via \`scripts/seed-wave6-documents.mjs\`), 25 generated tasks, and
   the harness capabilities (multi-turn simulated users, deterministic state-diff
   verifiers with collateral assertions, reference-relative turn budgets). Verdicts cite
   specific identifiers.
3. **Validation.** DeepSeek V4 Flash only (cheapest working model, $0.14/$0.28 per M):
   full 25-task × 2-trial sweep for $${flash?.totals?.costUsd ?? "?"}. No leaderboard runs.

## Headline

| | count | share of in-scope |
|---|---|---|
| **Covered** — expressible AND verifiable now, evidence cited | ${V.covered.length} | ${pct(V.covered.length)} |
| **Partial** — substrate present, one named piece missing | ${V.partial.length} | ${pct(V.partial.length)} |
| **Gap** — unsupported | ${V.gap.length} | ${pct(V.gap.length)} |
| Out of scope (other verticals / scoring techniques) | ${V.out_of_scope.length} | — |
| **In-scope total** | **${inScope}** | 100% |

**Every gap is an external-channel mock**: LinkedIn (outreach + scraping), SMS/WhatsApp,
live web/SERP scraping, SMTP/MX email verification, job-change signals, multi-agent
negotiation arenas, and OpportunitySplit objects. Nothing inside the CRM/RevOps core is
a gap. The world's identity — state-verified internal business workflows — covers its
ground; the gaps are the boundary where a simulation meets the live internet.

## Flash validation of the shipped tasks

${flash ? `- ${flash.totals.tasks} tasks × 2 trials, ${flash.totals.trialsRun} trials, 0 infra errors, $${flash.totals.costUsd}.
- Official strict: ${flash.totals.solidPass}/${flash.totals.tasks} tasks. Trial-level: ${flash.trialsRaw.filter((t) => t.passed).length}/${flash.totals.trialsRun} official, ${flash.trialsRaw.filter((t) => { const fc = new Set(t.failedConditions ?? []); return t.passed || (fc.size && [...fc].every((c) => c === "required_workflow_path")); }).length}/${flash.totals.trialsRun} audited (ex undocumented-order, per the 2026-08-10 audit protocol).
- Depth frontier: ${flash.depthCurve.map((b) => `${b.bucket} calls → ${b.passRate === null ? "n/a" : Math.round(b.passRate * 100) + "%"} (${b.trials})`).join(" · ")}. The 21+-call tasks are wave-6's frontier; per the audit protocol their failures require transcript forensics before being claimed as capability gaps.` : "- (run data/flake/w6-flash-validation.json missing)"}

## Covered (${V.covered.length})

| capability | kind | evidence |
|---|---|---|
${V.covered.map((v) => `| ${v.name} | ${kindOf(v.name)} | ${(v.evidence ?? []).slice(0, 5).join(", ").slice(0, 160)} |`).join("\n")}

## Partial (${V.partial.length}) — substrate present, named missing piece

| capability | kind | what's missing |
|---|---|---|
${V.partial.map((v) => `| ${v.name} | ${kindOf(v.name)} | ${v.note.replace(/\|/g, "/").slice(0, 200)} |`).join("\n")}

## Gaps (${V.gap.length}) — external-channel mocks

| capability | what closing it needs |
|---|---|
${V.gap.map((v) => `| ${v.name} | ${v.note.replace(/\|/g, "/").slice(0, 220)} |`).join("\n")}

## Out of scope (${V.out_of_scope.length})

${V.out_of_scope.map((v) => `- **${v.name}** — ${v.note.replace(/\|/g, "/").slice(0, 160)}`).join("\n")}

## Prioritized close-the-partials roadmap

The 96 partials cluster into a handful of cross-cutting misses; closing these clusters
resolves most rows at once:

1. **Outbound send channel** (~15 partials): a logged \`send_email\`/\`post_message\` write
   tool + outbound_messages table. Without it, every sequence/nurture/reply workflow can
   read state but not act. Biggest single unlock.
2. **Transcript corpus depth** (~10): 2 seeded call transcripts exist; the
   conversation-intelligence family needs 10+ with planted MEDDIC/competitor/sentiment
   facts and won/lost + competitor fields on opportunities.
3. **Leak/refusal verification** (~6, the confidentiality family): disclosures change no
   state, so the state-diff harness cannot see them — needs a transcript-level assertion
   (deterministic string/entity match on the agent's output, not an LLM judge).
4. **SLA/entitlement timers** (~5): milestone tables with first-response/resolution
   deadlines so escalation and SLA-breach tasks verify from timestamps.
5. **Enrichment-provider mocks** (~5): 2-3 provider tools with distinct coverage/failure
   rates + an enrichment_cache table to make the waterfall executable.
6. **A/B variant + spend accounting tables** (~4): per-variant outcome counts; per-tool
   credit metadata for budget-aware agents.

Wave-7 candidates (the 11 gaps) are a deliberate scope decision: mocking LinkedIn/SMS/
SERP/SMTP surfaces is exactly what the blobfish \`mock_services\` mechanism is for, but
each adds hundreds of ops — gate on demonstrated need, validate Flash-first.

## Reproduce

\`\`\`
node scripts/build-coverage-md.mjs           # this file
node scripts/seed-wave6-documents.mjs        # in-world document corpus
node sim/run-flake-scan.mjs --all --trials 2 --label w6-flash-validation \\
     --world-file world/blobfish-wave6/world.json --model deepseek-v4-flash
\`\`\`
`;

writeFileSync(join(ROOT, "docs", "COVERAGE.md"), md);
console.log(`docs/COVERAGE.md: ${inScope} in-scope items — ${V.covered.length} covered / ${V.partial.length} partial / ${V.gap.length} gap`);
