# Sales-world organization — detailed design (v1, 2026-08-10)

Why this doc: the current generated sales world is not shippable. Symptoms: the tool list
is the generic vendor roster (`erp`, `github`, `pagerduty`, `jira`, `notion`, `stripe`…)
rather than sales-driven tools; tools sit in a flat `tools/` list instead of being
organized as per-product MCP servers; tasks/thesis/mock data show template reuse.
Root cause (with file:line evidence): `~/dev/blobfish-0/docs/BUG-TOOL-ROSTER-INFERENCE.md`
— namespaces are regex-inferred at package-emit time from an 11-entry hardcoded substring
table, while the real per-domain vendor selection (`forge_services`, incl. hubspot/gong/
granola/apollo aliases) is computed upstream and then dropped before the emitter runs. This doc
is the corrected organization, following the proven finance-world architecture
(`~/dev/finance-world`) and the house creation workflow (research → thesis → tool census →
data chaos → task ladder → triage-and-grow).

## 0. Operating rules (identical to finance-world, non-negotiable)

- Research-first and stored: every tool, table, task, and chaos pattern cites a research
  doc in `research/` — no invented realism, no roster copying.
- Deterministic rewards only (VCode over state; `submit_answer` makes answers state).
- Ship-honest: task ships iff its oracle walk replays green through its own verifier.
- Audit-before-blame; infra failures labeled and retried, never counted as model verdicts.
- Fixed world epoch; all "this week/quarter" math is stable.
- Calibration state (`acceptance_label`) lives on the task; flaky = the product.

## 1. Tool census (evidence-driven; each server must be required by ≥1 task)

One MCP server per product, all over one per-run SQLite state, namespaced so the agent
experiences separate systems. Shaped after each product's real MCP/API (research step:
pull each vendor's MCP docs / OpenAPI / GitHub usage before mocking).

| Server | Shaped after | Owns (tables) | Why it exists |
|---|---|---|---|
| `crm` | Salesforce REST/MCP (sobjects, SOQL-lite query, reports) | accounts, contacts, opportunities (stage/amount/close_date/owner), activities, leads | System of record for the AE org — the spine |
| `hubspot` | HubSpot CRM v3 API/MCP | its own companies/deals/contacts (divergent IDs, overlapping accounts) | The acquired SMB team never migrated — THE cross-CRM fragmentation mechanic ("total sales this week?" spans both) |
| `apollo` | Apollo.io API | prospect/enrichment records, sequences | Top-of-funnel data lives outside the CRM |
| `gong` | Gong API/MCP | call records, transcripts, trackers, next-steps | Call truth ≠ CRM truth (commitments made on calls, never logged) |
| `granola` | Granola MCP | meeting notes, action items | Notes capture what reps didn't type into the CRM |
| `sheets` | Excel/Google Sheets reader | pipeline tracker, commission calc, forecast roll-up (stale vs CRM) | The shadow system, same 94%-Excel evidence class as finance |
| `gdrive` | Google Drive API/MCP | proposals, order forms, signed contracts, pricing sheets | Contract truth (signed amount ≠ opportunity amount) |
| `email` | Gmail-shaped read-only | threads with prospects, approvals, PO/invoice handoffs | Deals advance in email before the CRM knows |
| `calendar` | Google Calendar (read-only) | meetings held/scheduled per account | Meeting activity is a pipeline-health signal (justified here, unlike finance) |
| `docs` | Internal doc store | sales SOPs: stage-exit criteria, discount policy, comp plan, territory rules | Consult-don't-know policy knowledge |
| `harness` | eval-only | answers table (submit_answer, list_submitted) | Grading surface, off the business tools |

**Deliberately excluded** (roster-copy tripwires): `erp`, `github`, `pagerduty`, `jira`,
`notion` generic notes, `stripe` (billing enters only if a researched closed-won→invoice
task needs a read surface — then as `billing`, evidence first). Every exclusion is written
down so a reappearance is visibly a regression.

## 2. Harbor format organization (per-task dirs, task-level seeding)

```
sales-world/
├── research/                    # question ledger + evidence docs (eval inventory: CRMArena,
│                                #   τ-bench retail, arena tracks; workflow research; chaos map)
├── THESIS.md                    # company, epoch, personas, fragmentation story
├── world/
│   ├── schema.sql               # all tables, namespaced per server (crm_*, hs_*, gong_*, …)
│   ├── etl/load_core.py         # builds world/build/core.sqlite from seeds; validates GTs
│   └── build/core.sqlite        # (gitignored) shared baseline state
├── mcp/
│   ├── lib/framework.py         # stdio MCP + tracing (+ok flag; error payloads = ok:false)
│   ├── servers/<name>_server.py # ONE SERVER PER PRODUCT (11 above)
│   └── mcp-servers.json         # roster + shaped_after + change-control note
├── tasks/<family>/<slug>/       # TRUE HARBOR TASK DIRS (schema_version 1.4)
│   ├── task.toml                # metadata: family, origin (which eval/article), difficulty,
│   │                            #   acceptance_label, walk_len, chaos notes
│   ├── instruction.md           # persona-voiced prompt + exact submit fields
│   ├── environment/
│   │   ├── Dockerfile           # materialized by exporter
│   │   └── seed/                # TASK-LEVEL SEEDING (the core mechanic):
│   │       ├── seed.sql         #   special core data (this task's accounts/deals)
│   │       ├── mcp_seed.json    #   per-server rows (gong transcript, hubspot deal, email…)
│   │       ├── documents/*.md   #   seeded SOP/policy docs → docs server
│   │       └── inputs/*         #   files staged into agent workdir (CSV exports, PDFs)
│   ├── solution/walk.json       # oracle tool path (+ solve.sh replayer)
│   └── tests/checks.json        # deterministic checks (+ test.sh reward.txt contract)
├── verifiers/vcode.py           # answer checks (tol), trace checks, state vetoes
├── sim/                         # prepare / oracle / run_task / run_batch (infra-aware,
│                                #   resumable) / grow_tasks / build_reports / scaffold
├── traces/<model>/<family>/<slug>/trial-N.(pass|fail|infra).json   # real traces, failures kept
├── reports/                     # summary.json + failure-report-<model>.md (generated)
└── docs/                        # AUDIT.md, TOOL-CENSUS.md, COVERAGE.md, anchors/
```

Answer to "is this Harbor format?": yes at the task level — each `tasks/<family>/<slug>/`
is a spec-compliant Harbor dir (`harbor run -p <task> -a oracle` after export bakes seed +
runtime into `environment/`). Repo-level dirs are the authoring/calibration workspace.

## 3. Mock data & the chaos map (every inconsistency cites a source)

Core mechanic: **one defensible truth, fragmented storage.** Seed generator computes and
pins every cross-system ground truth. Wave-1 chaos (each pattern to be evidenced in
`research/domain-workflows.md` for sales — CRM-hygiene surveys, RevOps articles,
r/sales-adjacent content, Gong/Clari vendor research):

1. Same customer in both CRMs under divergent names/IDs (post-acquisition non-migration).
2. Opportunity amount ≠ signed order form in gdrive (discount applied at signature).
3. Closed-won in salesforce, deal still "in progress" in hubspot (sync lag).
4. Commitments in gong transcript / granola notes never logged as CRM next steps.
5. Pipeline tracker spreadsheet one week stale vs CRM (version drift).
6. "This week's sales" needs salesforce closed-won + hubspot closed-won + a sheet-only
   deal the SMB team hasn't entered anywhere else.
7. Duplicate account pair inside salesforce (pre-merge leftovers).
8. Stage-exit criteria doc vs reality: deals in "Negotiate" missing required security review.

## 4. Task families & ladder (start from researched tasks)

Wave-1 sources: CRMArena(-Pro) tasks (vendored in `external/CRMArena`), τ-bench
methodology, arena occupational sales tracks, RevOps articles. Families:

| Family | Example (submit fields) | Systems |
|---|---|---|
| `crm_qa` | "What's Acme's open pipeline? (amount, stage, owner)" | crm |
| `cross_crm` | "Total closed-won this week across the org?" (sf + hubspot + sheet-only deal) | crm, hubspot, sheets |
| `call_truth` | "What did we commit to on the Northwind call, and is it in the CRM?" | gong, granola, crm |
| `contract_recon` | "Signed amount vs opportunity amount for Fabrikam — any discount leakage?" | gdrive, crm, docs |
| `pipeline_hygiene` | "Which Negotiate-stage deals violate stage-exit criteria?" | crm, docs, calendar |
| `forecast` | "Commit-category forecast for Q1 vs the tracker — where do they disagree?" | crm, sheets |
| `ops_write` (wave 2) | "Log the call outcome + advance the stage per SOP" | crm write + policy |

Difficulty axes: walk depth (2 → 10+), cross-system hops, divergent-ID resolution,
stale-copy arbitration, empty-answer traps ("did we ever quote X?" — no), pagination,
policy-conditional logic, ambiguity of prompt ("handle Acme" vs explicit asks).

Triage-and-grow: 3 trials/model → fail-3x park (after audit) · mixed = flaky, keep &
study · pass-first-try → `sim/grow_tasks` escalates (deeper walk, more ambiguity,
distractor twins, extra system hop) until failure. Budgets reference-relative
(`max(24, walk*3+6)`).

## 5. Verifiers

Same VCode engine as finance-world: answer checks (numeric with tol_abs/tol_rel, string,
contains_all), trace checks (required_servers — e.g. cross_crm REQUIRES both CRMs touched
successfully; min_calls; reads_before_submit), state checks (writes_only allowlist;
wave-2 writes get expected_state_changes diffs + no_collateral vetoes). No LLM judge.
Informative tool errors (`{"error":..., "available": [...]}`) marked ok:false in trace —
recovery is part of the skill; raw stack traces are not.

## 6. Execution order (instantiating the creation workflow)

1. `research/questions.md` ledger (domain, value, personas: AE / SDR / AM / sales manager /
   RevOps / deal desk; done-criteria per task type; scenarios).
2. Eval inventory deep-dive (CRMArena-Pro first — it's already vendored) + tool-surface
   research per vendor (MCP docs, APIs, GitHub workflows).
3. THESIS.md; tool census locked with exclusion list.
4. schema.sql + ETL + core seed; chaos seeded per-task, GTs pinned by generator.
5. Wave-1 tasks from researched scenarios; oracle admission gate.
6. Flake-scan (infra-aware) → failure reports per model → grow/park/keep.
7. Harbor export; blobfish `worlds/import` compatibility.
```
