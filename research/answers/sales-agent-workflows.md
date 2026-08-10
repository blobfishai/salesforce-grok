# Sales-agent workflows — what sellers actually do, with what tools, mapped onto our mock

> Answers QUESTIONS.md #3 (what each stakeholder does daily), #5 (stakeholder ×
> workflow × tool), and #8 (which tasks appear in evals vs nowhere). Written
> 2026-08-10 from assistant domain knowledge (cutoff 2026-01) + this repo's SOP
> anchor corpus; workflow shapes cross-checked against the coverage census
> (`data/coverage/census-items.json`). Mock mappings cite live tool names —
> including the densification wave landing in `world/blobfish-wave6/tool-specs/`
> (marked Δ where the tool is new).

Format per workflow: **real stack** → **our mock, step by step** → **verifier hook**
(what state change proves it; per QUESTIONS.md #11).

## 1 · SDR outbound loop (the AI-SDR canon)

Real: ZoomInfo/Apollo list-build → Clay enrichment waterfall → Outreach/Salesloft
sequence (email + call + LinkedIn steps) → reply triage → Chili Piper booking →
CRM handoff under an SLA.

| step | real tool | our mock | notes |
|---|---|---|---|
| build target list | ZoomInfo/Apollo | `query_sales_leads` filters over 500-row `sales_leads` + `lead_scoring_policy`/`aum_bands` tables | ICP scoring is doc-driven, not tool-driven |
| enrich | Clay waterfall | `tech_signals` reads; enrichment-provider tools are a named gap (COVERAGE roadmap #5) | wave-7 candidate |
| sequence touches | Outreach cadence | `sequence_design_rules` + `snippets`/`merge_field_conventions` reads, then Δ`post_mail_send` logging to Δ`sg_mail_sends` | the send log is the unlock (roadmap #1) |
| reply triage | Outreach inbox | `retrieve_conversation` (revops-core) + `disposition_codes` | no inbound email object yet (named partial) |
| book meeting | Chili Piper | Δ`calendar_freebusy_query` → Δ`calendar_events_insert` (attendees, recurrence) vs `meeting_scheduling_sla` | booking is fully verifiable now |
| handoff MQL→SAL | CRM task + SLA | `update_sales_leads_status` + `company_sales_handoffs` + `lookup_sales_lead_with_employees`; SLA doc `31-mql-sql-handoff-sla.md` | |

Verifier hook: lead status transition + handoff row + booked event row, with
`no_offtask_table_changes` guarding the other 200+ tables.

## 2 · Inbound speed-to-lead

Real: web form → HubSpot/Marketo capture → routing engine (LeanData/Chili Piper)
→ 5-minute-touch SLA → BANT/MEDDIC qualify → convert.

Mock: `web_form_definitions` + `inbound_routing_matrix` reads → `task_create`
(the 5-minute policy is literally seeded: *"leads contacted within 5 minutes of
creation"* in `world.json.thesis.policies`) → transcript-grounded qualification
against `anchor:39/40` call transcripts + `meddic_scorecard` → `contact_create`
/ `opportunity_create`. Verifier: routing-correct owner + task timestamps +
created records matching the routing matrix row.

## 3 · AE discovery-to-close (the flagship chain)

Real: Gong call → CRM auto-population → stage gates → CPQ quote → discount
approval (Slack thread: Deal Desk → Compliance → Finance) → DocuSign →
closed-won → order activation → billing.

| step | real tool | our mock |
|---|---|---|
| call intelligence | Gong | anchor transcripts + `transcript_evidence`, `tracker_keywords` |
| CRM hygiene | Salesforce | `opportunity_get`/`opportunity_create`, `opportunity_stage_gates` table + `04-opportunity-stage-gates.md` |
| quote + discount | Salesforce CPQ | `order_form` + `fy2026_list_prices` + `volume_bands` + `05-cpq-discount-policy.md` (Quote object = top named partial) |
| approval chain | Slack | deal-room via `conversations_create` today; Δ`chat_post_message` makes the Deal Desk→Compliance→Finance order *observable in state*, not just in trace |
| e-sign | DocuSign | MSA/order-form artifacts (`sow`, `nda`, `matter_documents`); envelope object is a named partial |
| billing chain | Stripe | Δ`post_subscriptions` → Δ`post_invoices` → Δ`post_invoices_invoice_finalize`/`_pay` → `post_charges`; refunds via Δ`post_refunds` with over-refund guard |
| ERP reconcile | NetSuite | Δ`erp_sales_order_create` → Δ`erp_invoice_create` → Δ`erp_customer_payment_create` (overpayment/currency guards) |

Verifier hook: this is the world's flagship cross-system invariant — closed-won
⇒ executed order form ⇒ activated order ⇒ subscription ⇒ invoice — asserted as
state deltas across three vendor namespaces plus mandated approval order in trace.

## 4 · CSM renewal / churn-save motion

Real: Gainsight/ChurnZero health score → 120-day renewal timeline → EBR deck →
uplift per playbook → renewal opp → invoice.

Mock: `deal_health_score` + `risk_notes_csm_post_call` + `stale_opportunity_ladder`
reads → `14-renewal-playbook.md` + `term_and_renewal` (the MSA's notice window)
→ `opportunity_create` (renewal) → Δ`post_subscriptions_subscription`
(uplift/proration) → Δ`erp_invoice_create`. The 120-day timeline tables
(`week_1_t_120_to_t_114` …) are seeded as period fixtures. Verifier: renewal opp
+ subscription delta + invoice, before the notice deadline computed from the MSA.

## 5 · Deal-desk / RevOps hygiene sweep

Real: Clari pipeline inspection → stale-deal flags → forecast rollup → comp
statements in CaptivateIQ → dupe merges.

Mock: `query_sales_opportunities` at 500-row distractor mass →
`25-pipeline-inspection-rules.md` + `sandbagging_red_flags` +
`slipped_pulled_in_lost` → `update_sales_opportunities_status` +
`sheet_agent` rollup artifact → comp via `29-quota-comp-plan.md` + journal
tools. Dupe *detection* works (`data_quality_rules`, `dedupe_race_handling`);
merge/delete ops are deliberately absent (named partial — merges are the classic
collateral-damage trap). Verifier: exactly-the-flagged rows changed; sheet
artifact contents match recomputed rollup.

## 6 · Support escalation with paging

Real: Intercom/Zendesk SLA breach → Jira issue → PagerDuty page → ack/resolve →
RCA in Notion.

Mock: `query_support_tickets` (500 rows) + `case_management_sla` →
Δ`jira_issue_create` → Δ`pd_incident_create` (auto-assigns level-1 on-call from
the escalation policy) → Δ`pd_incident_manage` ack/resolve with stamped
`resolved_at` + typed `pd_log_entries` → Δ`notion_page_create` RCA. Verifier:
incident lifecycle rows + log entries + RCA page, ticket status closed within SLA.

## 7 · Marketing → sales handoff (campaign to MQL)

Real: Marketo/HubSpot campaign → engagement scoring → MQL → SLA'd acceptance.

Mock: `get_campaigns`/`post_campaigns` + `fy2026_campaigns` + `funnel_conversion_rates`
+ `utm_conventions` → `company_marketing_handoffs` status machine with
`update_company_marketing_handoffs_status`. Named partial: no per-touch
CampaignMember table, so multi-touch attribution stays an analytics read, not a
verifiable write.

## What no eval covers yet (QUESTIONS.md #8, the interesting tail)

From the census + this mapping, daily seller work that appears in NO public
benchmark but IS expressible here once the densification lands: suppression-list
compliance before a send (Δ`sg_suppressions_add` + policy doc), calendar
double-booking repair (Δ`calendar_freebusy_query` + `events_patch`),
vendor-bill three-way match (planted fixture BILL-3006 ↔ purchase_order_004),
incident-driven billing-pause coordination (pd + stripe + slack in one episode),
and quota-period comp-statement reproduction (sheet artifact vs recomputed plan).
These are wave-7 task candidates with deterministic verifiers already reachable.

## Follow-ups

- Fill `research/tools/outreach.md` and `gong.md` stubs with verb-level API
  evidence before promoting sequencing/conversation-intelligence to first-class
  vendors.
- Decide wave-7's chaos axis: HubSpot-as-second-CRM (drift tasks) vs
  enrichment-provider mocks with credit metering (budget tasks).
