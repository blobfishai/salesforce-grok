# Research questions — the sales world (question-led, not one-shot)

Rules of engagement:

1. A question is **OPEN** until its answer file cites primary sources — a cloned
   repo path under `research/repos/`, an official API/MCP doc, or a dated article.
2. Answers accumulate in `research/answers/<slug>.md`; per-product verb research
   in `research/tools/<product>.md`; every claim carries its source inline.
3. Model-knowledge-only claims are allowed **only** when tagged
   `[UNSOURCED]` — they are debts, not answers, and may not be used to justify a
   table, tool, or task without a grounding source (see `docs/GROUNDING-JUDGE.md`).
4. Evidence corpus: `research/repos.manifest.tsv` → `research/repos/` (clone log
   at `research/repos/CLONE-LOG.tsv`), plus `external/CRMArena`.

Status legend: `OPEN` · `PARTIAL` (some sources, gaps named) · `ANSWERED`.

---

## A. Domain — what business is this?

| # | Question | Status | Answer file |
|---|---|---|---|
| A1 | What exact business is simulated: segment (SMB/mid/enterprise), ACV band, motion (inbound / outbound / PLG / partner), contract shape (subscription / usage / services)? | PARTIAL | `answers/domain-definition.md` |
| A2 | What is the value chain end-to-end — demand → lead → opportunity → quote → order → invoice → renewal/expansion — and **where does money leak** at each hop? | PARTIAL | `answers/sales-workflow-canon.md` |
| A3 | What are the unit economics that make a task *matter* (quota, coverage ratio, win rate, cycle length, ARR/NRR, discount leakage, DSO)? | OPEN | `answers/business-value-metrics.md` |
| A4 | What is the calendar rhythm — daily standup, weekly forecast call, month-end close, quarter-end crunch — and how does it change what a task means on a given day? | OPEN | `answers/operating-cadence.md` |
| A5 | Which regulatory/policy constraints bind actions (data residency, KYC/suitability for a financial-services flavor, SOX-relevant approvals, GDPR deletion)? | PARTIAL | `docs/anchors/wave2/regulations-compliance-regimes.md` |

## B. Stakeholders — who acts, and what does "done" mean to them?

| # | Question | Status | Answer file |
|---|---|---|---|
| B1 | Full role roster (SDR/BDR, AE, AM, CSM, SE/Solutions, Sales Manager, RevOps, Deal Desk, Finance/Rev Rec, Legal/CLM, Marketing Ops, Partner Manager, Support) — headcount ratios and reporting lines. | PARTIAL | `answers/stakeholder-roster.md` |
| B2 | For each role: the **daily loop** (what they open first, what they do 20× a day, what they do once a week). | OPEN | `answers/stakeholder-roster.md` |
| B3 | For each role: **definition of done** per workflow — the observable state change that ends the task. | OPEN | `answers/definitions-of-done.md` |
| B4 | Handoff contracts between roles (MQL→SQL, SDR→AE, AE→Deal Desk, Closed Won→CSM/Finance): what must be true at the boundary, and what breaks when it isn't? | PARTIAL | `docs/anchors/wave6/31-mql-sql-handoff-sla.md` |
| B5 | Who is *allowed* to do what (permissions, approval authority, segregation of duties) — i.e. which agent actions should be **refused**, not merely unperformed? | PARTIAL | `answers/authority-and-refusals.md` |
| B6 | Who does the agent talk to, and in what channel (Slack thread, email reply, CRM chatter, ticket comment)? What makes a *communication* task done? | OPEN | `answers/definitions-of-done.md` |

## C. Tasks — what work actually exists?

| # | Question | Status | Answer file |
|---|---|---|---|
| C1 | Task census from **evals/arenas**: CRMArena / CRMArena-Pro, SCUBA, τ-bench/τ²-bench, MCPEval, R2A-Sales, ai_sales_eval_arena, attio-mcp-benchmark — every task type, its inputs, and its scorer. | PARTIAL | `answers/eval-task-census.md` |
| C2 | Task census from **practitioner repos** (SDR templates, GTM skills, RevOps agents): what do real automations actually do, step by step? | OPEN | `answers/workflow-task-census.md` |
| C3 | Which daily sales tasks appear in **no** public eval (the white space we should own)? | OPEN | `answers/eval-white-space.md` |
| C4 | Task **shape** taxonomy: answer/analytics · state mutation · multi-system reconciliation · communication/drafting · judgment-under-policy · **restraint** (correct action = do nothing). | PARTIAL | `docs/SCENARIO-COVERAGE.md` |
| C5 | Input documents per task: call transcript, email thread, order form, MSA/redline, rate card, RFP, sheet export, dashboard screenshot, voicemail. Which tasks *require* reading an artifact? | PARTIAL | `docs/anchors/wave6/*artifact*` |
| C6 | Long-horizon shape: which tasks legitimately need 10–25 tool calls across ≥3 systems, and what is the natural dependency order? | PARTIAL | `answers/long-horizon-shapes.md` |
| C7 | What are the **ambiguity** variants — underspecified requests where a competent human would ask one clarifying question or state an assumption? | OPEN | `answers/ambiguity-variants.md` |

## D. Tools — the real surface

| # | Question | Status | Answer file |
|---|---|---|---|
| D1 | Stakeholder × workflow × tool matrix: which product does each role actually touch at each step? | PARTIAL | `answers/competitor-tool-landscape.md` |
| D2 | Per product: the real verbs — from official MCP servers, OpenAPI specs, and cloned community MCP implementations. Which verbs appear in **every** implementation (the core), which are long-tail? | PARTIAL | `research/tools/<product>.md` |
| D3 | Per product: object model and the fields that carry decisions (stage, amount, close date, owner, status reason). | PARTIAL | `research/tools/<product>.md` |
| D4 | Competitor sets per category (CRM: Salesforce/HubSpot/Pipedrive/Attio/Twenty/Close; enrichment: Apollo/ZoomInfo/Clay; CI: Gong/Chorus; billing: Stripe/Zuora …) — because a real org runs a *mixture*, and mixtures are where the chaos lives. | PARTIAL | `answers/competitor-tool-landscape.md` |
| D5 | Auth/rate-limit/pagination/error semantics worth simulating (429s, partial writes, idempotency keys, bulk API asynchrony). | OPEN | `answers/api-failure-semantics.md` |
| D6 | Which surfaces are **not** APIs — spreadsheets, PDFs, email bodies, meeting notes — and how does an agent read/write them? | PARTIAL | `answers/non-api-surfaces.md` |

## E. Data chaos — why the world is hard

| # | Question | Status | Answer file |
|---|---|---|---|
| E1 | Where does the same fact live twice (CRM amount vs billing invoice vs the ops spreadsheet vs the order form PDF) and which copy is authoritative *for which question*? | PARTIAL | `answers/data-chaos-catalog.md` |
| E2 | Catalogue of real drift mechanisms: sync lag, dedupe collisions, partial migration, renamed picklists, stale enrichment, cloned renewal deals double-counting, currency/FX, timezone/fiscal-calendar boundaries. | PARTIAL | `answers/data-chaos-catalog.md` |
| E3 | For the canonical question "what's the total sales number this week": how many defensible answers exist, what makes each defensible, and what must the agent disclose? | OPEN | `answers/data-chaos-catalog.md` |
| E4 | Which chaos is **detectable** from inside the world (an agent could notice) vs invisible (must be told)? Only the former can be graded as a miss. | OPEN | `answers/data-chaos-catalog.md` |
| E5 | What does a *healthy* record look like, so that "dirty" is measurable (completeness thresholds, duplicate rates, required-field policy)? | OPEN | `answers/data-quality-baseline.md` |

## F. Verification — what proves the work

| # | Question | Status | Answer file |
|---|---|---|---|
| F1 | Per task: the state delta that proves completion, and the **collateral set** that must not change. | PARTIAL | `bench/verifiers/` |
| F2 | Which tasks need transcript-level assertions (the agent said/disclosed something) rather than DB assertions? | PARTIAL | `bench/verifiers/` |
| F3 | For analytics answers: tolerance, units, and whether an assumption disclosure is required for full credit. | OPEN | `answers/answer-grading-policy.md` |
| F4 | How do the public evals verify (CRMArena exact-match, τ-bench DB-hash + policy, SCUBA checkpoints, MCPEval tool-trajectory match) — and which scheme fits which of our task shapes? | PARTIAL | `answers/eval-task-census.md` |
| F5 | How do we prevent verifier bugs from scoring correct behavior as failure (the wave-8 lesson)? | ANSWERED | `docs/CREATION-PROTOCOL.md`, memory: benchmark-audit-protocol |

## G. Difficulty — where the model breaks

| # | Question | Status | Answer file |
|---|---|---|---|
| G1 | Which task properties predict failure (chain length, cross-system hops, policy-vs-prior conflict, distractor mass, procedure mandates)? | PARTIAL | README waves 1–8 |
| G2 | For each *passed* task: what are the escalation axes (more steps, more systems, more ambiguity, more distractors, more restraint) that push it to the frontier? | PARTIAL | `answers/escalation-axes.md` |
| G3 | Which failures are **our** bugs vs the model's? (Universal-failure rule: a task all models fail is a bug until proven otherwise.) | ANSWERED | `docs/CREATION-PROTOCOL.md` |
