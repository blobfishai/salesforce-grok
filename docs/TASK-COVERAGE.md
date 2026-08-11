# Task coverage — can the corpus's work actually run in this world?

The claim is that the evals, automations, and workflows collected in
`research/repos/` (381 repos) are *runnable here*, not merely cited. This maps
each source's task inventory onto the world's actual tool surface and says
plainly where a task exists, where the capability exists but no task is written
yet, and where the world genuinely cannot express it.

Status: **RUNS** (a Harbor task exists) · **CAPABLE** (tools + data exist, task not
yet authored) · **GAP** (world cannot express it; named, not hidden).

Tool names below are real entries in `world.json` — see
`docs/TOOL-COVERAGE.md` for the verb-level measurement.

---

## 1. CRMArena / CRMArena-Pro — 22 task categories

Source: `research/repos/eval/SalesforceAIResearch__CRMArena/run_tasks_crmarena_pro.sh`

| CRMArena category | status | world surface |
|---|---|---|
| `sales_amount_understanding` | CAPABLE | `aggregate_query`, `quotes_list`, `sales_opportunities` (501 rows) |
| `sales_cycle_understanding` | CAPABLE | `sales_opportunities.expected_close_date`, `sales_leads.created_at` |
| `conversion_rate_comprehension` | CAPABLE | `sales_leads.status` (6-value funnel), `query_sales_leads` |
| `sales_insight_mining` | CAPABLE | `aggregate_query` over opportunities/leads/quotas |
| `monthly_trend_analysis` | CAPABLE | `campaign_touches_list`, `forecast_submissions_list` |
| `best_region_identification` | GAP | no territory/region column on accounts — territory exists only as policy text |
| `quote_approval` | **RUNS** | `deal-desk-quote-triage` — `quotes_list` → `quote_update_status` |
| `lead_qualification` | CAPABLE | `query_sales_leads`, `update_sales_leads_status`, `lead_scoring_policy` |
| `lead_routing` | CAPABLE | `lead_update_fields` (owner), `routing_decision_table`, `inbound_routing_matrix` |
| `wrong_stage_rectification` | CAPABLE | `opportunity_stage_gates`, `sales_opportunities.status` |
| `activity_priority` | CAPABLE | `task_create`, `tasks` (17 rows), `email_threads_list` |
| `invalid_config` | **RUNS** | `sales_quotes.config_valid` drives two decisions in `deal-desk-quote-triage` |
| `named_entity_disambiguation` | CAPABLE | duplicate leads 901/902 and 903/904; `lead_find_duplicates` |
| `policy_violation_identification` | CAPABLE | 40+ policy tables (`cpq_discount_policy`, `deal_desk_charter`, …) |
| `knowledge_qa` | CAPABLE | `core.search_knowledge`, `notion.query_documents` |
| `case_routing` | CAPABLE | `service_cases` (180 rows), `service_case_update_status` |
| `handle_time` | CAPABLE | `case_history_list`, `case_management_sla` |
| `transfer_count` | CAPABLE | `case_history_list` |
| `top_issue_identification` | CAPABLE | `issue_taxonomy_list`, `service_cases` |
| `private_customer_information` | CAPABLE | `customer_profiles_list` holds PII fields |
| `internal_operation_data` | CAPABLE | `rep_quotas`, `forecast_submissions`, comp policy tables |
| `confidential_company_knowledge` | CAPABLE | battlecards / win-loss anchors in `docs/anchors/wave6/` |

**19 of 22 categories are expressible today; 2 already run; 1 is a named gap**
(region/territory as data rather than prose).

## 2. τ-bench / τ²-bench pattern

Source: `research/repos/eval/sierra-research__tau2-bench/data/tau2/domains/*`

| element | status | here |
|---|---|---|
| `policy.md` (rules the agent must obey) | RUNS | policy is in the instruction (deal desk matrix) and in 40+ policy tables |
| `db.json` (world state) | RUNS | `seed.db`, 313 tables, 9,462 rows |
| `tasks.json` | RUNS | `tasks.spec.jsonl` → generated Harbor task dirs |
| user simulator (withholds detail until asked) | GAP | our tasks are single-shot instructions; no interactive stakeholder in the Harbor packaging yet |
| DB-state verification | RUNS | `/verifier/query` + `unchanged_vs_seed` collateral guards |

## 3. R2A-Sales — policy-under-pressure

Source: `research/repos/eval/qinyh10300__R2A-Sales-Benchmark`

| element | status | here |
|---|---|---|
| policy atoms (severity, hard_fail, forbidden_claims) | CAPABLE | policy tables exist; atom schema not yet ported |
| `pressure_schedule` escalating over turns | GAP | needs the interactive stakeholder above |
| terminal conditions success / safe_exit / failure | **RUNS** (partial) | restraint tasks grade safe_exit as full credit via negative assertions |
| tool authorization preconditions | RUNS | world rejects invalid transitions and rate-limits writes |
| false-completion detection ("I sent the PDF" with no tool event) | GAP | verifiers read state, not the transcript — the highest-value missing check |

## 4. Practitioner skills — 185 inventoried

Source: `research/answers/_data/workflow-skills.tsv`

| family (skills) | status | world surface |
|---|---|---|
| CRM hygiene / RevOps admin (37 in hubspot-admin-skills) | **RUNS** | `merge-duplicate-leads`, `stop-bounced-sequences`; plus `contact_merge`, `account_merge`, `lead_delete`, `lead_find_duplicates` |
| dedupe & merge | **RUNS** | `lead_merge` + `lead_merge_log` audit trail |
| suppression / bounce hygiene | **RUNS** | `stop-bounced-sequences`; `email.sg_suppressions_add`, `sg_bounces_delete` |
| owner reassignment / deactivated users | CAPABLE | `lead_update_fields`, `employees` (18 rows) |
| lifecycle backfill | CAPABLE | `update_sales_leads_status`, `lead_management_sop` |
| outbound sequencing (YALC, gtm-pipeline, gtm-eng: ~86 skills) | CAPABLE | `sequences_list`, `sequence_steps_list`, `sequence_enroll_lead`, `outreach_sequences` |
| enrichment waterfall with credits | GAP | no enrichment provider tools — named in `research/THESIS.md` §4 as mocking priority 3 |
| lead scoring / ICP tiering | CAPABLE | `lead_scoring_policy`, `account_tiering_standard` |
| meeting debrief → CRM records | CAPABLE | `notion.query_documents` (call transcripts) → `task_create`, `opportunity_create` |
| stage-aware follow-up | CAPABLE | `sales_opportunities.status` + `task_create` |
| quotation / proforma generation | CAPABLE | `quote_get`, `quote_lines_list`, `product_catalog_list` |
| inbox ↔ CRM sync | CAPABLE | `email_threads_list`, `email_messages_list`, `email_thread_classify` |
| spreadsheet-as-CRM | CAPABLE | `github.sheet_agent`, `agent_sheets` |
| forecast / pipeline inspection | **RUNS** | `forecast-category-correction`; `rep_quotas_list`, `forecast_submit` |
| renewal & health | CAPABLE | `account_health_list/update` (7 accounts, banded), `renewal_playbook` |
| contract / e-signature | CAPABLE | `signature_envelopes_list`, `signature_envelope_update` |
| quote-to-cash activation | **RUNS** | `quote-to-order-activation` (salesforce → erp) |
| billing reconciliation | **RUNS** | `unlinked-invoice-reconciliation` (erp → jira) |
| destructive cleanup requests | **RUNS** | `restraint-bulk-lead-purge` — meaningful only because `lead_delete` now exists |

## 5. Honest gaps, in priority order

1. **False-completion detection.** R2A's sharpest check: a claimed action with no
   matching tool event. Our verifiers read database state only, so an agent that
   narrates completed work it never did can still score on the collateral guards.
   Fix: assert over the world's trace alongside state.
2. **Interactive stakeholder.** τ-bench and CRMArena-Pro both simulate a user who
   reveals detail only on request; R2A escalates pressure across turns. This repo
   has `sim/run-interactive.mjs`, but it is not wired into the Harbor packaging.
3. **Enrichment providers.** Three independent repos encode the same
   waterfall-with-a-budget pattern; the world has the SOP tables and no provider
   tools, so no task can test provider disagreement or credit exhaustion.
4. **Territory/region as data.** Blocks `best_region_identification` and any
   routing task that turns on geography.
5. **Second CRM.** The thesis argues a HubSpot account that is *also* a Salesforce
   account with a lossy field map is the most realistic hard object available.
   Not built yet; 112 HubSpot verbs + 68 REST endpoint templates are extracted
   and waiting in `research/tools/_extracted/`.
