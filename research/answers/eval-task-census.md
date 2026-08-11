# Eval task census — what the public benchmarks actually test

> Answers QUESTIONS.md **C1** and **F4**. Every row traces to a cloned repo path
> or a dated URL in `research/SOURCES.md`. Compiled 2026-08-11.

## 1. The census

### CRMArena-Pro — 19 task categories + 3 confidentiality probes
Source: `research/repos/eval/SalesforceAIResearch__CRMArena/run_tasks_crmarena_pro.sh`
(v1 shipped the first 9; Pro adds the sales block and the confidentiality block).

**Service block (v1, 9):** `policy_violation_identification` · `monthly_trend_analysis` ·
`named_entity_disambiguation` · `best_region_identification` · `handle_time` ·
`knowledge_qa` · `transfer_count` · `case_routing` · `top_issue_identification`

**Sales / RevOps block (Pro, 10):** `sales_amount_understanding` · `lead_routing` ·
`sales_cycle_understanding` · `conversion_rate_comprehension` ·
`wrong_stage_rectification` · `sales_insight_mining` · `quote_approval` ·
`lead_qualification` · `activity_priority` · `invalid_config`

**Confidentiality block (Pro, 3):** `private_customer_information` ·
`internal_operation_data` · `confidential_company_knowledge` — with a
`PRIVACY_AWARE_PROMPT` toggle, i.e. the *refusal* is the graded behavior.

Run axes that matter to us: `ORG_TYPE=b2b|b2c`, `INTERACTIVE=true|false`
(a simulated user withholds detail until asked), `EVAL_MODE=aided`,
`STRATEGIES=react`.

**Read of it:** only ~4 of 22 are true multi-step *mutations*
(`wrong_stage_rectification`, `lead_routing`, `case_routing`, `quote_approval`);
the bulk are single-hop analytics/lookup over one system of record. That is the
gap our world exists to fill.

### SCUBA — 300 computer-use tasks, 3 personas
Source: arXiv 2509.26506. Personas: **platform administrator · sales
representative · service agent**. Capability areas quoted: *"Enterprise Software
UI navigation, data manipulation, workflow automation, information retrieval,
and troubleshooting."* Verified by **milestone/checkpoint metrics** in a
Salesforce sandbox with parallel execution. Zero-shot: open models <5%, closed
up to 39%; with demonstrations 50% (−13% time, −16% cost).

**Read of it:** the admin persona is the one everybody else ignores, and it maps
one-to-one onto the hygiene skills in §2 of `SOURCES.md`. Checkpoint scoring is
the right model for our long-horizon tasks — partial credit at milestones rather
than a single terminal assertion.

### R2A-Sales — the Rule-to-Action Gap
Source: `research/repos/eval/qinyh10300__R2A-Sales-Benchmark`.

- 39 **policy atoms** (`benchmark/policy_atoms/*.yaml`), each with
  `severity`, `hard_fail`, `applicability`, `required_behaviors`,
  `allowed_claims`, `forbidden_claims`, `escalate_when`, and `source_evidence`
  with a provenance path — a template worth stealing wholesale.
- 58 interactive scenarios (`benchmark/matched_instances/interactive_scenarios.jsonl`)
  carrying `pressure_schedule` (turn → customer act → pressure level),
  `private_customer_state` (consent, mood, patience, trust, unresolved objections)
  and `terminal_conditions` split into **success / safe_exit / failure**.
- 6 mock tools with authorization preconditions: `send_material` (asset must be
  allowlisted), `handoff` (needs an active escalation condition), `schedule_followup`
  (consent + channel preference), `quote` (all eligibility inputs present),
  `register_lead` (consent token), `record_opt_out` (scope).
- **Headline result: static compliance 89.9–99.1% vs interactive compliance
  3.0–17.3% → a Rule-to-Action Gap of 80.4–92.5 points** across 8 backbones.

The design point they make explicitly: *"A customer-visible sentence such as 'I
sent the PDF' is not a tool event."* Saying ≠ doing; a claim without a matching
successful tool event is a **false-completion hard failure**.

### τ-bench / τ²-bench — the domain-file pattern
Source: `research/repos/eval/sierra-research__tau2-bench/data/tau2/domains/{retail,airline,telecom,banking_knowledge}`.
Each domain is exactly four artifacts: `policy.md` (the rules the agent must
obey), `db.json` (world state), `tasks.json` (+ `split_tasks.json`), and a user
simulator. Verification = final DB state + policy adherence. `task_issues/`
exists as a first-class folder — they track their own task defects.
`amazon-agi__tau2-bench-verified` is the corrected fork: proof that benchmark
bugs are the norm, which is why our universal-failure rule exists.

### MCPEval — tasks generated *from* the tool surface
Source: `research/repos/eval/SalesforceAIResearch__MCPEval` (arXiv 2507.12806).
Pipeline: point it at an MCP server → auto-generate tasks → run agents →
deep-evaluate trajectories (not just final answers), with per-domain benchmark
folders. This is the same generative move blobfish makes with tool-graph random
walks; MCPEval is the citable prior art and a second opinion on task quality.

### attio-mcp-benchmark — read queries, two scoring axes
Source: `research/repos/eval/ArcadeAI__attio-mcp-benchmark/evals/*.md`.
8 queries: list companies · deals by stage · deals over $50K · name substring ·
category filter · created-before-date · **compound filter** · sort+limit 1.
Scored on **expressibility** (can it be said at all?) and **token cost**
(100× spread between toolkits). Query 07 needed 4 calls including a schema
discovery call because documented option values (`501-1000`) did not exist in the
workspace (`5K-10K`, `10K-50K` …).

**Read of it:** a first-class failure mode we should seed deliberately — *the
documentation lies about the picklist*. Our wave-5 "conflicting SOP" trick is the
same shape, independently discovered.

### ai_sales_eval_arena — judging the conversation, not the DB
Source: `research/repos/eval/Rperry2174__ai_sales_eval_arena`.
Rubric-based LLM grading of sales-call transcripts (`data/transcripts/*.txt`),
then round-robin / single- / double-elimination tournaments to rank performers.
Relevant to us for **communication tasks** (F2) where the artifact is prose.

### agentune & ShampooSalesAgent — simulation loops
`SparkBeyond__agentune`: analyze real conversations → improve → simulate →
measure KPI (conversion, CSAT). `jackfsuia__ShampooSalesAgent`: minimal
conversational seller that records orders to CSV — an end-to-end
"conversation causes a state write" toy worth mirroring at enterprise scale.

## 2. Verification schemes, compared

| Scheme | Used by | Fits our task shape |
|---|---|---|
| Exact-match / f1 on a returned answer | CRMArena(-Pro) | analytics answers (C4 "answer tasks") — but needs a tolerance + units policy (F3) |
| Final DB-state equality + policy adherence | τ-bench, τ²-bench | single-system mutations |
| Milestone / checkpoint progress | SCUBA | **long-horizon multi-system tasks — adopt this** |
| Tool-event authorization + terminal conditions (success/safe_exit/failure) | R2A-Sales | policy-under-pressure and **restraint** tasks |
| Trajectory-level deep evaluation | MCPEval | procedure-sensitive tasks (our wave-2 `required_workflow_path` family) |
| LLM-judge rubric | ai_sales_eval_arena | communication/drafting tasks |
| Expressibility + token cost | attio-mcp-benchmark | tool-surface quality, not agent quality — useful as a *world* QA metric |

Our verifiers today are closest to τ-bench (state delta + collateral guards).
The two we are missing: **checkpoint partial credit** and **false-completion
detection** (claimed action with no corresponding tool event).

## 3. What no public eval covers (feeds C3 → `eval-white-space.md`)

1. **Cross-system reconciliation.** Every benchmark above runs against exactly
   one system of record. Nothing tests "the CRM says X, billing says Y, the ops
   sheet says Z — what is the number, and which copy is authoritative?"
2. **RevOps/admin hygiene at scale.** 36 real HubSpot admin skills exist in the
   wild (dedupe, lifecycle backfill, owner reassignment, suppression); SCUBA has
   an admin persona but no public *task set* for it.
3. **Approval-chain judgment.** CRMArena has `quote_approval` as one category;
   nobody models a multi-approver chain with sequencing, thresholds, and
   re-triggering on amendment.
4. **Restraint under ambiguity.** R2A covers refusal under *sales* pressure;
   nothing covers "the request is underspecified and the correct move is to ask
   or to write nothing" in an ops setting. (Our restraint pack — commit 944ea70 —
   is ahead of the field here; it should be positioned as such.)
5. **Artifact-grounded work.** Reading an order form / MSA / call transcript and
   making a CRM decision from it appears only as prose grading (arena) or not at
   all.
6. **Time semantics.** Fiscal calendars, "this week", timezone boundaries,
   as-of-date snapshots — absent everywhere; and it is the single most common
   real question a sales manager asks.
