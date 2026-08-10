# World-Creation Protocol (canonical)

> The methodology for building a realistic agent-environment world, as specified
> 2026-08-10. Distinct from **Harbor**, which is the *packaging/runtime* contract of a
> built world (`world.json.harbor`, format_version 4: server runtime, endpoints, MCP
> manifest, seed-DB startup, training kit). This document governs the *creation* side.
> Each step is annotated with its current implementation status in this repo.

## 1 · Research — iterative, question-led, stored

Research the user's prompt until we know exactly what the real agent environment looks
like. For the sales world: find all the GitHub workflows in the domain, all the agent
arenas and evals, so we know what tasks are likely. Dive deep into task types, input
documents, MCP tools called, and task variations.

**Not one-shot.** Come up with questions and answer them: What is the domain? The
business value? Who are the stakeholders in the workflow? What tasks do they do? What
counts as done? What are the business scenarios, and how do they interact with which
tools?

All research documents and links are **stored** under `research/`, question by question.

- ✅ Have: the 6-source census (171 items with per-item environment requirements,
  `data/coverage/census-items.json`), competitor deep-dives (`docs/COMPARISON.md`).
- ⚠️ Delta: research was fan-out, not question-led iteration, and lives as result JSON
  rather than a growing `research/` store with links + open questions. **Adopt: a
  `research/` directory — one file per question, links + findings + follow-ups.**

## 2 · Thesis — learnings, framing, data gathered

With the questions answered, fill out the **thesis**: what we learned, how we frame the
world, the data we gathered.

- ✅ Have: blobfish generates `world.json.thesis` (roles, entities, workflows, policies,
  claims, topic clusters) from prompt + anchors; our 46-doc anchor corpus IS the
  gathered-data layer feeding it.
- ⚠️ Delta: the thesis is generator-authored. **Adopt: a human/agent-authored
  `research/THESIS.md` written *before* generation, which the anchors then encode.**

## 3 · Tool universe — the real stack, including competitors

List every tool this world's business uses: Salesforce CRM **and** its competitors and
substitutes — HubSpot, plain Excel/Sheets, Apollo, etc. Mock each by researching its
actual MCP documents, APIs, and GitHub workflows of people driving its CLI/API.

- ✅ Have: 7 vendored service mocks mounted from real API IR specs (salesforce, stripe,
  sendgrid, intercom, slack, gcal, netsuite — 205 tools), validated by 119 schema
  anchors.
- ⚠️ Delta: no HubSpot, no Apollo, no spreadsheet-as-first-class-system mock; the
  coverage audit's 11 gaps are exactly missing tool mocks (LinkedIn, SMS, SERP, SMTP).
  **Adopt: per-tool research files (MCP docs / OpenAPI / usage workflows) under
  `research/tools/`, then IR specs for the missing vendors.**

## 4 · Data chaos — the same business, fragmented across systems

Build the tables in depth and the core-service mocks of how MCP interacts with custom
tables and documents — and mock each tool's own database, so that **some data lives in
a spreadsheet, some in a local DB, some in Salesforce, some in HubSpot** — and a task
like "what's the total sales number this week?" forces cross-system reconciliation.
The chaos is designed from experience: evals, articles, and readings about real
integration messes (sync lag, duplicates, conflicting field values, partial migrations).

- ✅ Have: 214 tables across 11 namespaces over one shared state; sheets tables exist;
  handoff tables (`company_sales_handoffs`) already model cross-system references.
- ⚠️ Delta: fragmentation is not yet *engineered* — no deliberately overlapping entity
  copies with inconsistencies, no aggregation task whose answer requires merging
  spreadsheet + CRM + billing. **Adopt: a fragmentation pass that splits canonical
  entities across systems with seeded discrepancies + reconciliation tasks.** (The
  RevOps integration-map anchor already specifies source-of-truth rules to verify
  against.)

## 5 · Tasks — the ladder

Start from researched tasks: everything seen in evals, arenas, and articles. Then:

| First-run outcome | Meaning | Action |
|---|---|---|
| Fails 3× in a row | Too hard | Park it. Useful for failure modes — but **first verify the failure is not our system's fault** (audit protocol: replay the reference walk, recompute ground truths, read the traces). |
| Fails and passes | **Flaky — the boundary** | Keep and study: these reveal *why* the model sometimes fails. This is the key task class. |
| Passes first time | Too easy | Spawn harder variants: more steps, more depth, more ambiguity; extend the tool-graph walk (3 tools → 10); longer horizon. Model should keep growing in depth until failure. |

- ✅ Have: this is the wave program — flake-scan classes (pass / FLAKY / fail),
  never-delete + escalate-until-flicker (blobfish `/calibrate escalate:true`,
  `harden-wave5.mjs`), reference-relative turn budgets, and the audit protocol that
  caught 5 environment bugs before they read as model failures
  (`memory: benchmark-audit-protocol`).
- ⚠️ Delta: we run 2 trials; the spec says fail **3×** before parking. **Adopt:
  `--trials 3` on frontier candidates** (cheap-model-first keeps this affordable).

## 6 · Task-level seeding — fixtures belong to the task, not just the world

Global seeded data alone is not realistic. Every task carries its own fixture bundle
(`bench/tasks/<world>/<task>.seed.json`, schema `task-seed.v1`):

- **rows** — the specific records this task is about (the deal, the leave request, the
  invoice), full row objects layered into the episode's session
- **documents** / **input_documents** — the artifacts the task hands the agent (the
  matter file, the contract, the transcript) — entries with a `body` are upserted into
  the document stores; pointer-only entries record provenance
- **special core data** — internal-platform rows (playbooks, memories, sheets)
- **mcp_seeding** — which vendor servers' surfaces the task exercises

Runtime: `run-simulation --multi-server --apply-task-seed` applies the bundle to the
episode's copy-on-write session DB *before* the agent starts (verified: fixtures are
instantly visible through every vendor MCP server, and vanish with the session).
**Verifier safety**: the stock server diffs against the static SEED_DB, so fixtures
would read as undeclared agent writes — `scripts/patch-server-verify.mjs` (v2) lets
`/verify` accept per-table post-seed baselines, and the harness sends the snapshot the
applier dumps. Proven: with the override, seeded rows/docs pass
`no_undeclared_rows_created` and `no_offtask_table_changes`; without it they fail.
Re-apply the patch after re-downloading any world package.
Extraction: `scripts/build-bench-folders.mjs` derives baseline bundles from each task's
pinned rows, prompt-referenced documents, and walk namespaces — hand-enrich them with
realistic bodies instead of relying on generator filler.

- ✅ Have: schema, extractor, applier, per-vendor visibility test.
- ⚠️ Delta: today's bundles are extracted pointers; the realism work is authoring
  rich bodies (real-looking order forms, inboxes, spreadsheets) per task.

## Order of operations

research/ (questions → answers → links) → THESIS.md → anchors encode the thesis →
tool-universe specs → generation (deep job) → **fragmentation pass** → seeding
(documents) → Flash-first task ladder with audit-before-blame → escalate the easy,
study the flaky, park the (verified) too-hard → repeat.
