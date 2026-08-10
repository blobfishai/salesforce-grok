# Sales-Domain Coverage Proof — wave-6 world `sbx_291042075d7547f4`

> Generated 2026-08-10 by `scripts/build-coverage-md.mjs` from
> `data/coverage/*.json`. Question answered: *does this world support all the tasks,
> workflows, and evals of the sales-software domain?*

## Method

1. **Census (demand side).** Six parallel researchers enumerated the domain from primary
   sources: CRMArena + CRMArena-Pro (every one of the 9 + 19 task types, incl. the
   confidentiality track), non-CRM agent benchmarks (tau-bench, tau2, WorkBench,
   MCPEval servers, WebArena-class), the open-source AI-SDR/outbound ecosystem
   (github.com/topics/sales-automation, ai-sdr, cold-email), RevOps/admin-certification
   workflow canon, conversation-intelligence + document-centric capabilities
   (Gong/CUAD-style), and trust/safety evals. Result: **171 deduplicated items**
   (79 eval tasks, 71 workflows, 21 tool capabilities), each with concrete
   environment requirements.
2. **Matching (supply side).** Four judges matched every item against the world's full
   inventory — 214 tables, 205 tools across 11 namespaces, the 46-document anchor corpus
   (now seeded in-world via `scripts/seed-wave6-documents.mjs`), 25 generated tasks, and
   the harness capabilities (multi-turn simulated users, deterministic state-diff
   verifiers with collateral assertions, reference-relative turn budgets). Verdicts cite
   specific identifiers.
3. **Validation.** DeepSeek V4 Flash only (cheapest working model, $0.14/$0.28 per M):
   full 25-task × 2-trial sweep for $3.18. No leaderboard runs.

## Headline

| | count | share of in-scope |
|---|---|---|
| **Covered** — expressible AND verifiable now, evidence cited | 44 | 29% |
| **Partial** — substrate present, one named piece missing | 96 | 64% |
| **Gap** — unsupported | 11 | 7% |
| Out of scope (other verticals / scoring techniques) | 20 | — |
| **In-scope total** | **151** | 100% |

**Every gap is an external-channel mock**: LinkedIn (outreach + scraping), SMS/WhatsApp,
live web/SERP scraping, SMTP/MX email verification, job-change signals, multi-agent
negotiation arenas, and OpportunitySplit objects. Nothing inside the CRM/RevOps core is
a gap. The world's identity — state-verified internal business workflows — covers its
ground; the gaps are the boundary where a simulation meets the live internet.

## Flash validation of the shipped tasks

- 25 tasks × 2 trials, 50 trials, 0 infra errors, $3.18.
- Official strict: 15/25 tasks. Trial-level: 30/50 official, 33/50 audited (ex undocumented-order, per the 2026-08-10 audit protocol).
- Depth frontier: 1-5 calls → 88% (33) · 6-10 calls → 100% (1) · 11-20 calls → n/a (0) · 21+ calls → 0% (16). The 21+-call tasks are wave-6's frontier; per the audit protocol their failures require transcript forensics before being claimed as capability gaps.

## Covered (44)

| capability | kind | evidence |
|---|---|---|
| activity_priority | eval_task | tasks (table), opportunities (table), tasks_list, task_get, opportunity_get |
| auto_task_generation_and_verification | tool_capability | task_001..task_025 (GENERATED TASKS section), deterministic state-diff verifiers (harness), blobfish MCP tool definitions at /worlds/{id}/mcp |
| bant_qualification_extraction | eval_task | anchor:39-artifact-call-transcript-summit.md, anchor:40-artifact-call-transcript-meridian.md, anchor:02-lead-scoring-policy.md, anchor:31-mql-sql-handoff-sla.md |
| call_grounded_followup_email | eval_task | anchor:39-artifact-call-transcript-summit.md, anchor:40-artifact-call-transcript-meridian.md, contacts (table), contact_get, contacts_list |
| case_routing | eval_task | support_tickets:500, cases:17, employees:18, query_support_tickets, lookup_support_ticket_with_employees |
| confidential_company_knowledge | eval_task | query_documents, search_knowledge, core_records_agent, anchor:05-cpq-discount-policy.md, anchor:02-lead-scoring-policy.md |
| confidentiality_company_secret_refusal | eval_task | anchor:05-cpq-discount-policy.md, anchor:43-artifact-pricing-rate-card.md, fy2026_list_prices (table), pricing_pressure_guidance (table), cpq_discount_policy (t |
| confidentiality_multiturn_persistence | eval_task | harness: multi-turn simulated users, fy2026_list_prices:14, pricing_pressure_guidance:10, anchor:43-artifact-pricing-rate-card.md, employees:18 |
| contract_clause_extraction_cuad | eval_task | anchor:41-artifact-msa-ironwood.md, anchor:42-artifact-order-form-summit.md, anchor:23-clm-clause-library.md, nda, sow |
| contract_hypothesis_entailment | eval_task | anchor:41-artifact-msa-ironwood.md, anchor:42-artifact-order-form-summit.md, anchor:23-clm-clause-library.md, nda:8, sow:19 |
| conversion_rate_comprehension | eval_task | sales_leads, sales_opportunities, query_sales_leads, query_sales_opportunities, lookup_sales_opportunity_with_sales_leads |
| crm_autopopulation_from_call | workflow | anchor:39-artifact-call-transcript-summit.md, opportunities (table), task_create, contact_create, contacts_list |
| crm_end_to_end_operation_eval | eval_task | account_create, contact_create, opportunity_create, case_create, task_create |
| crm_stub_mcp_server_tasks | eval_task | accounts_list, account_get, account_create, contact_create, opportunity_create |
| handle_time | eval_task | support_tickets:500, query_support_tickets, lookup_support_ticket_with_employees, employees:18, cases |
| hr_management_mcp_server_tasks | eval_task | hr_leave_requests:500, hr_performance_reviews:500, departments:7, employees:18, query_hr_leave_requests |
| invalid_config | eval_task | order_form:13, anchor:42-artifact-order-form-summit.md, anchor:13-product-catalog.md, line_items_list_prices_per_13_product_catalogmd:8, fy2026_list_prices:14 |
| knowledge_qa | eval_task | agent_documents (46 anchor docs being seeded), anchor:13-product-catalog.md, anchor:14-renewal-playbook.md, query_documents, search_knowledge |
| lead_qualification | eval_task | sales_leads, query_sales_leads, lookup_sales_lead_with_employees, lead_scoring_policy, mql_definition |
| lead_routing | eval_task | query_sales_leads, sales_leads:500, lookup_sales_lead_with_employees, employees, territory |
| long_horizon_contextualized_office_workflows | eval_task | document_agent, agent_documents (table), sheet_agent, agent_sheets (table), calendar_agent |
| meddic_field_extraction | eval_task | anchor:39-artifact-call-transcript-summit.md, anchor:40-artifact-call-transcript-meridian.md, meddic_scorecard, meddic_extraction_scorecard, transcript_evidence |
| meeting_booking | workflow | calendar_agent, query_calendar_events, agent_events, calendar_calendars_insert, meeting_types_and_durations:15 |
| meeting_prep_and_followup_tasks | workflow | calendar_agent, agent_events (table), query_calendar_events, anchor:20-meeting-scheduling-sla.md, meeting_types_and_durations (table) |
| named_entity_disambiguation | eval_task | anchor:13-product-catalog.md, line_items_list_prices_per_13_product_catalogmd (table), fy2026_list_prices (table), purchase_orders (table), purchase_orders_list |
| next_step_extraction | eval_task | anchor:39-artifact-call-transcript-summit.md, anchor:40-artifact-call-transcript-meridian.md, calls, calls_info, contacts |
| objection_detection_classification | eval_task | anchor:39-artifact-call-transcript-summit.md, anchor:40-artifact-call-transcript-meridian.md, tracker_keywords, disposition_codes, anchor:19-conversation-intell |
| objection_handling | workflow | anchor:33-battlecard-harborview.md, anchor:34-battlecards-atlas-crestline.md, pricing_pressure_guidance:10, winloss_talking_points:13, their_strengths_do_not_di |
| order_form_price_book_consistency | eval_task | anchor:42-artifact-order-form-summit.md, anchor:43-artifact-pricing-rate-card.md, anchor:13-product-catalog.md, anchor:05-cpq-discount-policy.md, order_form (ta |
| personalized_cold_email_generation | workflow | anchor:17-outbound-sequencing-playbook.md, anchor:18-email-template-library.md, sequence_design_rules (table), merge_field_conventions (table), snippets (table) |
| policy_knowledge_qa | eval_task | anchor:05-cpq-discount-policy.md, anchor:08-finance-approval-thresholds.md, anchor:29-quota-comp-plan.md, anchor:30-territory-rules-of-engagement.md, anchor:14- |
| product_catalog_rag | tool_capability | anchor:13-product-catalog.md, anchor:43-artifact-pricing-rate-card.md, fy2026_list_prices, line_items_list_prices_per_13_product_catalogmd, volume_bands |
| renewal_date_notice_deadline | eval_task | anchor:41-artifact-msa-ironwood.md, term_and_renewal, renewal_mechanics_per_msa_and_14_renewal_playbookmd, anchor:14-renewal-playbook.md, anchor:28-renewal-expa |
| rep_compliance_utterance_detection | eval_task | anchor:19-conversation-intelligence-standards.md, anchor:05-cpq-discount-policy.md, conversation_intelligence_standards (table), compliance_review_checklist (ta |
| sales_amount_understanding | eval_task | sales_opportunities, query_sales_opportunities, opportunities, opportunities_list, opportunity_get |
| sales_cycle_understanding | eval_task | opportunities (table), sales_opportunities (table), query_sales_opportunities, opportunities_list, lookup_sales_opportunity_with_sales_leads |
| sales_email_draft_quality_eval | eval_task | contacts, contact_get, accounts, account_get, tech_signals |
| side_effect_classification_scoring | tool_capability | deterministic state-diff verifiers with collateral-damage assertions (harness), per-task expected states on task_003..task_025, deterministic world resets (harn |
| side_effect_collateral_damage_measurement | tool_capability | harness: deterministic state-diff verifiers with collateral-damage assertions, harness: deterministic world resets, mutable-table inventory (sales_leads, sales_ |
| simulated_company_hr_admin_finance_tasks | eval_task | hr_leave_requests (table), hr_performance_reviews (table), finance_expense_reports (table), finance_budgets (table), query_hr_leave_requests |
| stalled_deal_detection_forecasting | workflow | sales_opportunities:500, opportunities:10, query_sales_opportunities, update_sales_opportunities_status, stale_opportunity_ladder:19 |
| tiered_tool_use_call_retrieve_plan | eval_task | ~200-tool deterministic MCP tool surface (accounts_list through update_company_sourcing_handoffs_status), lookup_* join tools, task_003, task_004, task_008 |
| writer_prospect_critique_loop | workflow | sales_leads:500, contacts_list, contact_get, document_agent, draft_matter_document |
| wrong_stage_rectification | eval_task | opportunities (table), tasks (table), opportunity_get, tasks_list, anchor:04-opportunity-stage-gates.md |

## Partial (96) — substrate present, named missing piece

| capability | kind | what's missing |
|---|---|---|
| ab_test_campaign_analytics | workflow | Campaign objects and aggregate engagement-stat tables exist, but there is no per-campaign A/B variants table and no per-variant outcome counts (sends/opens/clicks/replies), so a chi-squared winner ver |
| active_learning_lead_ranking | workflow | Lead corpus, status state-machine writes, label-store surfaces (save_memory/agent_sheets) and enrichment policy doc exist; missing a rationed/metered email-lookup or enrichment tool with credit accoun |
| agent_memory_layers | tool_capability | Memory read/write tools and scheduled-run substrate exist for structured recall and daily snapshot jobs, but there is no per-customer-isolated semantic/vector store, no verbatim-number recall fixtures |
| approval_authority_compliance | eval_task | Authority-matrix docs and adversarial multi-turn pressure exist, but the world lacks a quote object and discount/refund/credit write tools (no update_quote_discount, issue_refund, apply_credit) and ha |
| audit_trail_integrity | eval_task | Trail-policy doc, task/activity write tools, and the harness's world-side diff (the append-only effect log analog) exist; missing are per-object field-history tables and exposed-but-forbidden honeypot |
| battlecard_grounded_objection_handling | eval_task | Battlecard documents/tables, doc-retrieval tools, and multi-turn prospect simulation are all present; the missing piece is a claim-level grounding/entailment verification surface over the agent's conv |
| battlecard_synthesis_from_calls | workflow | Battlecard docs, win/loss artifact, and a document-write tool exist, but the transcript corpus is only 2 calls — the item needs 10+ transcripts seeded with competitor facts plus won/lost+competitor fi |
| best_region_identification | eval_task | Cases/tickets, read tools and a territory model exist, but there is no confirmed geographic (state/region) field on cases/accounts nor guaranteed open/close timestamp pairs, so per-region avg-closure- |
| blacklist_suppression_management | tool_capability | Read-side suppression substrate is present, but there is no write tool targeting blocks/bounces/suppression_groups (no blacklist_add/import), no check/normalization operation, and no export-from-seque |
| buyer_sentiment_engagement_scoring | eval_task | Readable transcripts exist, but only two and without deliberately valenced buyer language; even the recommended coarse 3-class variant needs a larger seeded multi-call corpus. (Item is self-flagged as |
| calendar_email_scheduling_tasks | eval_task | Calendar side is expressible (event create + query, directory via employees, SLA policy doc); missing entirely on the email side: no inbox object with seeded emails and no send/forward/reply/delete em |
| campaign_attribution | workflow | Campaign and opportunity tables plus an attribution policy table and campaign-catalog anchor exist; missing the touch graph itself — no CampaignMember/touchpoint table with timestamps linking leads/co |
| case_escalation_sla | workflow | Cases/tickets, write tools, and the SLA policy doc exist, but there are no entitlement/milestone timer tables and no EmailMessage/CaseComment first-response artifact, so milestone completion and escal |
| churn_risk_save_workflow | workflow | Health rubric, save-play runbook, and account/case/opportunity surfaces exist; missing a per-account usage/engagement-metrics table and a contract/subscription table with renewal_date/ARR to compute r |
| commission_calculation | workflow | Comp-plan anchor doc, closed-won opportunity data, paid-basis invoice/charge tables, and sheet_agent as the statement output surface exist; missing an OpportunitySplit table, a per-rep-per-period quot |
| competitor_intel_monitoring | workflow | Scheduling, semantic-memory store, and battlecard consumption surfaces all exist; missing an in-world competitor-intel source to research — no web_search/fetch tool and news_items is not seeded with c |
| competitor_mention_detection | eval_task | Competitor registry (battlecards + tracker_keywords) exists, but the capability needs a 10+ transcript corpus seeded with alias mentions and false-positive traps across opportunities — only 2 call tra |
| compositional_task_generator | tool_capability | The generator already mints multi-table compositional tasks, but there is no library of atomic subtasks with per-subtask pre/postconditions and fix procedures, nor balanced sampling over an intent x s |
| confidentiality_customer_pii_refusal | eval_task | Contact/lead/case/account records, read tools, and the multi-turn persona simulator exist; missing are confirmed PII field population (email/phone/address/birthdate) on contact rows, per-episode prote |
| confidentiality_internal_ops_refusal | eval_task | Leakable internal data, routing-policy docs, an aggregation surface, and external personas all exist; the concrete miss is a transcript-level leak/refusal verifier — a disclosure changes no state, so  |
| contract_amendment_coterm | workflow | Contract documents (MSA anchor), term/renewal mechanics tables, and price data support the proration reasoning; missing a Subscription/Asset line table holding active quantities/prices and any amendme |
| conversational_bant_qualification | workflow | Multi-turn elicitation, prospect records, structured memory (save_memory), and conversation-policy docs exist; missing evidenced BANT/icp_score/product_interest fields on contact/lead schema and a fie |
| cost_credit_budgeting | tool_capability | Harness turn budgets provide per-run cost ceilings, but the world has no per-tool credit-price metadata, no usage_log table, and no estimate_cost operation, so in-world budget-tracking behavior cannot |
| cpq_configure_price_quote | workflow | Catalog, list prices, volume/discount bands and pricing-waterfall policy are all present and readable, but there is no Quote/QuoteLine object and no quote-create write tool, so the constructed quote c |
| crm_data_hygiene_audit | eval_task | Hygiene-rule docs/tables and the record tables exist with status-write tools; missing field-level write tools beyond status (close_date, email fixes — update_*_status tools only write status), confirm |
| crm_pipeline_record_maintenance | eval_task | Find/create/stage-move are expressible and already exercised (task_017 verify-then-set-status pattern, task_003-009 end-to-end maintenance) with state-diff verification; concretely missing: any delete |
| crm_sync_bidirectional | workflow | Lead reads, status-stage advancement, record creation, and a second store (agent_sheets as the local mirror) exist; missing upsert semantics and field-level writes for enrichment values and document-l |
| cross_domain_conditional_workflows | workflow | Calendar, CRM, docs, sheets, and tasks share an entity graph and multi-table tasks exist, but there is no interpersonal outbound channel — no send_email or message-post write tool (messages has only t |
| customer_health_churn_upsell | workflow | The health-score model (weights, thresholds) and CS policy docs exist, and retention/upsell plays can be written as tasks/opportunities; missing the per-account usage/engagement telemetry fixtures (no |
| deal_risk_signal_detection | eval_task | The risk-signal catalog is unusually rich (pipeline inspection rules, deal health score, stale ladder, sandbagging flags) and CRM joins exist; missing the 3-5-call transcript series per opportunity (o |
| deep_prospect_research | workflow | An in-world research corpus surrogate (news items, articles, tech-signal table, enrichment-waterfall anchor) and a report output surface (document_agent) exist; missing a person/company profile-fetch  |
| deliverability_compliance_management | workflow | Domain-auth and bounce/block/suppression substrate is present, but there is no sending-account object carrying warmup_day/daily_limit state and no logged outbound send tool for a pre-send validation g |
| discount_approval_policy_check | eval_task | Approval-matrix docs, role tables and a discount-bearing order-form artifact support the read-only decide-and-cite variant now; missing a proper Quote object carrying discount_pct/amount/product-line/ |
| draft_review_approval_gate | workflow | Draft/approval status transitions, quality-rubric docs, and simulated approval interrupts are all expressible; missing an actual send/send_test_email tool, so 'nothing sends without approval' can only |
| email_sequence_scheduling | workflow | Campaign/singlesend write tools, sequencing-policy and template docs, merge-field conventions, and scheduling exist; missing a sequence-instance object (ordered steps with per-step delay_days and A/B  |
| enrichment_waterfall | workflow | The waterfall config doc and email-verification outcome tables (accept_all/risky/unknown) are seeded, but there are no enrichment-provider tools with distinct coverage/injected failure rates, no enric |
| followup_timing_optimization | workflow | Campaign-level engagement stats and sequencing/timing policy exist, but the core fixture is missing: a per-lead email interaction log (lead_ref, sent_at, opened_at, replied_at) from which optimal re-e |
| forecast_rollup_commit | workflow | Stage-to-category mapping docs, opportunity data at 500-row scale, and an employee/department hierarchy exist, and sheet_agent/agent_sheets can hold the rollup artifact; missing a Quota table and a Fo |
| human_escalation_handoff | workflow | Escalation-trigger policy docs and a handoff surface (task to owner, deal-room channel creation, context doc) exist; missing a chat message-post tool (the messages table has only the read tool chat_sc |
| icp_company_person_sourcing | workflow | ICP-definition substrate (tiering/scoring anchors, tech_signals, aum_bands) and filterable queries over 500 sales_leads support ICP scoring of known records; missing a discovery-scale external company |
| icp_scoring_qualification | workflow | Scoring policy docs/tables and lead records exist, but there is no website_extract/content tool, no numeric lead_scores field or table to write the 0-10 score into, and no signal_cache — scoring outpu |
| inbound_lead_capture_routing | workflow | Capture/scoring/routing policy substrate is rich (form definitions, routing matrix, scoring policy, UTM/attribution conventions) and contact_create + task_create cover record creation and owner notifi |
| inbound_reply_intent_and_response | eval_task | All response actions (meeting event via calendar_agent, referral contact, task) are executable and the unsubscribe policy is documented; missing an inbound EmailMessage/thread object to classify (mess |
| inbox_triage_labeling | workflow | Inbound thread objects (conversations), a label taxonomy analog (disposition_codes), and routing-rule tables/docs exist; missing an email-inbox object with from/subject/body fields, an apply_label wri |
| internal_operation_data | eval_task | The internal metrics are genuinely computable from seeded records and external personas are definable, but refusal grading requires transcript-level judging/leak-scanning — the state-diff verifier can |
| invoicing_dunning | workflow | Dunning policy and Stripe-style billing tables exist, and ladder actions (billing alert, call task, charge) are executable; missing an invoice create/update tool (invoices has only get_invoices) and a |
| lead_dedupe_merge | workflow | Matching/survivorship policy exists (data_quality_rules, dedupe_race_handling) over sizable lead/contact tables; missing merge and delete operations and any foreign-key re-parent write tools for child |
| lead_magnet_audit_report_generation | workflow | In-world doc generation and prospect records exist, and battlecards/win-loss content can approximate proof points; missing a case-study document corpus and a link field on lead/contact records to stor |
| lead_routing_assignment | workflow | Rule matrix, lead corpus, employee table and lead-to-employee join exist, and the expected owner is deterministically recomputable from the rule table; missing a lead owner_id write tool (only status  |
| lead_scoring_grading | workflow | Scoring policy and a 500-row lead table exist; missing an engagement-event/activity stream table keyed to leads (the raw input for behavioral scoring with decay) and a field-level lead write tool for  |
| monthly_trend_analysis | eval_task | 500 timestamped support tickets plus 17 cases with query tools support month-bucketed count/argmax questions with exact-match answers; missing the product scoping dimension — no Product2/OrderItem-sty |
| mql_sql_handoff_sla | workflow | Stage transitions, handoff records, touch-task creation, and the exact SLA doc exist; missing writable mql_date/sql_date timestamp and rejection-reason fields — the status-only update tools cannot sta |
| multi_turn_sql_db_operations | eval_task | Multi-turn DB question/update episodes with final-state verification are fully supported through typed tools (state diff is the table-state-hash equivalent), but there is no raw SQL execution tool wit |
| negotiation_counteroffer_tracking | workflow | Pricing floors/discount-authority policy docs, escalation via task creation, and memory/document writes exist; missing a dedicated negotiation-log object (offer/counter-offer rows with amounts and tim |
| npc_colleague_communication_dependency | tool_capability | Org-chart identities exist and the single simulated user can role-play one colleague; missing a message-post tool over the Slack-style surface (messages is read-only) and multi-NPC backends with per-N |
| nurture_longterm_followup | workflow | Cron-style scheduled runs, tiering policy for cadence, an in-world news surrogate, and template/snippet tables exist; missing an outbound message-send tool with a delivery queue/send log to verify cad |
| opportunity_stage_gate_enforcement | workflow | Stage writes, gate docs, and generated stage-gate tasks already exist, but there are no Quote or OpportunityContactRole objects, so canonical gates like 'Proposal requires attached quote' or 'decision |
| order_activation | workflow | Activation-precondition policy and the quote/order-form artifact exist, and Stripe-style billing writes exist downstream; missing a sales Order/OrderItem object with a Draft→Activated status write and |
| partner_deal_registration | workflow | Unusually strong policy substrate (deal-reg anchor, partner tiers, 90-day conflict-window table), conflict queries over existing pipeline, and opportunity_create for the approval branch all exist; mis |
| payment_link_close | tool_capability | Stripe-style billing substrate and catalog price lookup exist, and post_charges can record the close; missing a payment-link/checkout-session create tool — checkout_sessions has no write tool — so the |
| pipeline_reporting_alerts | workflow | Scheduled aggregation, stall-threshold policy, KPI definitions, and state-diff-verifiable report artifacts (agent_documents/agent_sheets) are expressible now; missing a channel message-post write tool |
| playbook_grounded_reply_drafting | workflow | A rich playbook/template/snippet corpus and conversation-thread objects exist, but there is no create_draft/send_reply email operation (drafts are only expressible as documents) and no true email-thre |
| policy_violation_identification | eval_task | Checkable policy docs and case tables/tools exist; missing a per-case chat-transcript corpus — the 2 anchor transcripts are sales calls not attached case chats, and identify-the-violating-case require |
| private_customer_information | eval_task | Customer records plus stripe-style transaction data (charges/invoices) give real leak temptation reachable via read tools, and the multi-turn external-persona simulation exists; missing confirmed PII  |
| product_pricebook_administration | tool_capability | Catalog/price tables and the published price-list source docs exist, and core_workflow_agent gives a write path to anchor-derived tables; missing field-level pricebook-entry create/update tools (unit_ |
| project_board_task_management | eval_task | task_001 already requires bulk status moves of an assignee's tasks (write path exists via the workflow agents) and final-board-state verification is exactly what the state-diff harness does; missing a |
| prompt_injection_crm_record_derailment | eval_task | Attacker-writable free-text surfaces (cases, knowledge, documents, matter docs), benign task templates that force reading them, and forbidden-action detection via the collateral-damage state-diff alre |
| prompt_injection_data_exfiltration | eval_task | Confidential fixtures and injectable free-text inbound records exist, and marketing-send object creation is state-diff visible; missing a general send_email/http_post outbound tool with arbitrary reci |
| quota_planning | workflow | Comp-plan/quota policy doc and the org tables exist; missing a quota table (user x period x amount) with a write tool, an explicit role/territory hierarchy surface for parent-child rollup reconciliati |
| quotation_pdf_generation | workflow | Catalog/pricing/currency substrate and a doc-draft surface exist, so quote-content correctness against catalog pricing/MOQ is verifiable on a drafted document; missing a PDF/letterhead render operatio |
| quote_approval | eval_task | Price book, rate card, discount policy, approval thresholds, and an order-form table/artifact make the discount-arithmetic-vs-policy decision expressible and exact-match verifiable; missing dedicated  |
| quote_contract_consistency | eval_task | The document side (MSA, order form) and pricing references exist, but there are no Quote/QuoteLineItem record tables and no quote_id linkage field, so the record-vs-document divergence audit at the he |
| quote_discount_approval_matrix | workflow | Approval-matrix thresholds, role tables and multi-turn approver simulation are in place; missing the Quote object (discount_pct, status Draft/In Review/Approved/Rejected) and an ApprovalRequest/Proces |
| quote_document_generation_esignature | workflow | Template/merge-field conventions, a clause library, contract-shaped tables, and doc rendering via document_agent exist; missing Quote/QuoteLine tables and the entire e-signature surface — an envelope  |
| refusal_calibration_non_answerable | eval_task | Timestamped ticket/case tables and query tools support constructing zero-match time-window questions with 'None' gold plus answerable twins; missing case-transfer and handle-time event-log tables that |
| renewal_expansion_management | workflow | Renewal policy docs, contract artifact (MSA), term/renewal tables, subscription-like active_entitlements, and renewal-opportunity creation all exist; missing a quote/quote-line create surface for the  |
| reply_intent_classification | workflow | Thread objects, an intent-taxonomy analog (disposition_codes), routing-rule tables, and action writes (tasks/cases/ticket status) exist; missing a suppression write tool for the unsubscribe branch (bl |
| rfp_question_answering | workflow | The past-RFP answer library, reuse/approval rules, a multi-doc KB, doc search, and an output surface (draft_matter_document) all exist; missing the inbound artifact itself — no seeded RFP questionnair |
| sales_call_summarization | eval_task | Readable transcripts exist, but no 10k+-token long-context transcript fixture, and checklist-coverage/hallucination-screen scoring of free-text output is outside the state-diff/exact-match verificatio |
| sales_conversation_stage_machine | workflow | Multi-turn selling conversations with policy/product grounding are supported, and conversation-intelligence standards are adjacent; missing an explicit conversation-stage framework document (8-stage e |
| sales_insight_mining | eval_task | Transcripts, activity records, opportunity linkage, and full-text search exist, but the sales-interaction corpus is thin — no EmailMessage-style sales emails and only two transcript docs — insufficien |
| scheduled_batch_outbound_run | workflow | Scheduling, spreadsheet row updates (sheet_agent), batch campaign enrollment, cross-system dedupe sources (leads/contacts/segments) and rate-limit/sequencing policy all exist; missing a chat message-p |
| security_questionnaire_answering | workflow | The grounded document-QA substrate and the adjacent RFP answer library exist; missing the security-policy corpus itself (infosec policy, SOC2 summary, DPA, subprocessor list) and a seeded SIG/CAIQ-sty |
| spin_call_script_generation | workflow | Research-input documents and document-write tools exist, but no SPIN methodology reference doc is in the corpus, and SPIN-structure/pain-point-mapping quality is not verifiable by the state-diff harne |
| suitecrm_policy_aware_web_tasks | eval_task | The sales-domain essence — policy-constrained CRM tasks with violation detection (no-delete, scope limits, action budgets) — is supported via MCP tools, the anchor policy corpus, and the harness's col |
| suppression_consent_outbound_compliance | eval_task | Suppression tables with read tools, a suppression-KPI policy table, campaign/segment objects, and send-object write tools (singlesends/campaigns/contact batches) exist — better than the item's stale l |
| talk_pattern_coaching_metrics | eval_task | Coaching-threshold tables (talk_ratio, coaching_cadence) exist and transcripts are speaker-labeled, but transcript fixtures lack per-utterance start/end timestamps — only question-count/word-share met |
| territory_reassignment | workflow | Territory model, rules-of-engagement and holdout/transfer-protocol policy exist, and sales_workflow_agent gives an account write path; missing field-level owner/territory_id update tools on accounts a |
| top_issue_identification | eval_task | High-volume ticket/case tables with query tools support frequency-count/argmax questions with exact-match answers; missing an issue-taxonomy object linked to cases (categories/category_stats are email |
| transcript_semantic_search | tool_capability | Transcript artifacts and doc query/search tools exist, so keyword retrieval over transcript bodies is expressible; missing scale and semantics: only 2 full call transcripts (need ~20+ with paraphrase- |
| transfer_count | eval_task | Cases and human agents exist, but there is no CaseHistory/ownership-change-event table recording old/new owner with timestamps, so transfer counts cannot be computed at all; adding and seeding a case- |
| unsubscribe_optout_enforcement | workflow | Permanent-suppression tables and reply threads exist, and opt-out policy lives in suppression_and_kpis/anchor:17; missing a write tool to add a contact to the suppression list (all suppression tools a |
| voice_cold_call_lead_reactivation | workflow | Call record objects, calendar booking, lead-status writes, and simulated users to play the prospect exist; missing a place_call/telephony operation and structured call-completion payloads (transcript, |
| web_analytics_reporting_tasks | eval_task | KPI definitions, funnel/attribution tables and campaign engagement stats support aggregate marketing-analytics reporting, with sheet_agent as an output artifact surface; missing a visit-level web-anal |
| web_to_lead_capture_autoresponse | tool_capability | Form definitions, routing/auto-response rule substrate, UTM conventions, and templates all exist; missing a lead-create write tool (no create op targets sales_leads) and a templated-email send/log ope |
| win_loss_theme_extraction | eval_task | Win/loss taxonomy docs, a transcript_evidence table, and two anchor call transcripts exist with doc-retrieval tools; missing corpus scale — the item needs 10+ closed-won/lost opportunities each linked |

## Gaps (11) — external-channel mocks

| capability | what closing it needs |
|---|---|
| buyer_seller_negotiation_market | Essentially unsupported: no multi-agent buyer/seller arena, no market matcher (1:N/N:M topologies), no private reservation values or welfare/utility scoring, no multimodal listings. Only a 1:1 policy-bounded negotiation  |
| email_pattern_discovery_verification | The entire verification tool surface — mx_lookup, smtp_verify, and a verifier-API cascade — is absent and has no analog in this deterministic world; only the enrichment-waterfall policy doc and lead records exist, so the |
| google_dork_profile_discovery | No web_search/SERP tool, no SERP corpus, no scraped-leads table with profile URLs, and no campaign object with lead-count targets; the closed world has no open-web surface for this to be expressed against. |
| job_change_signal_trigger | The core signal source is absent: no live profile-lookup tool, no last_known_title/last_known_company fields to diff against, no sequence-enrollment op, and no channel message-post tool for notification. Only scheduling  |
| linkedin_outreach_sequence | No LinkedIn channel exists: no profile_visit/send_connection_request/send_message operations, no connection-accepted events, no per-account quota counters, no message-pool rotation objects. Nothing in the inventory appro |
| linkedin_post_engager_scraping | No social-post objects, no engager-scrape tool, and no lead-import/create operation (sales_leads exposes only query and status-update tools) — essentially unsupported. |
| local_business_lead_scraping | Sales-prospecting domain but essentially unsupported: no simulated maps/business-directory search tool, no email-finder tool, no external-business directory table, no instagram-like profile surface. Nothing in the invent |
| multi_channel_orchestration_switching | No WhatsApp/Telegram/email send-receive tools exist and even the Slack-style messages table is read-only; no conversation object carries active_channel/window_expiry, so channel-switching before window expiry is essentia |
| offer_extraction_campaign_planning | Only the in-world campaign-catalog side exists; there is no website-scrape tool, no external prospect-search provider taxonomy, and no credit-cost accounting — the core probe-search-and-cost-estimate loop is unsupported  |
| opportunity_splits_credit | Split/overlay policy substrate exists in docs and the co-sell overlap table, but the capability's core objects are absent: no OpportunitySplit table, no OpportunityTeamMember table, and no split create/update/delete writ |
| sms_conversational_followup | No SMS channel exists: no send_sms operation, no inbound SMS webhook/thread objects, no character-limit constraints. The generic multi-turn chat simulator is the only adjacent piece; the channel state (threads per lead,  |

## Out of scope (20)

- **airline_policy_constrained_booking_modification** — tau-bench airline vertical (flights, reservations, fare rules) — another vertical, not a sales-domain environment capability.
- **api_retriever_tool_selection** — A trained dense API retriever with retrieval P/R scoring over a 16k-API corpus is a benchmark/harness technique, not a sales-environment feature. The world's la
- **banking_knowledge_domain** — tau2-bench banking customer-service domain is another vertical; the world's Stripe-style billing tables (charges, invoices, disputes) are B2B billing plumbing, 
- **communicate_info_assertion_scoring** — A transcript-assertion grading protocol from tau2-bench — a benchmark scoring technique, not a sales-environment feature.
- **completion_under_policy_metric** — CuP/Risk-Ratio is a benchmark scoring technique (metric aggregation over success and per-dimension violation signals), not an environment feature; the environme
- **configurable_user_simulator_strategies** — Pluggable user-strategy wrappers (plain/ReAct/Verify/Reflection) and swappable user models are benchmark-harness engineering for varying user difficulty, not a 
- **dual_control_telecom_troubleshooting** — tau2-bench telecom is another vertical (telecom customer service with device-state tools and a dual-control Dec-POMDP user), not a sales-domain environment capa
- **ecommerce_mcp_server_tasks** — E-commerce storefront vertical (products/orders/inventory MCP server) — another vertical, same category as the Magento exclusion.
- **ecommerce_storefront_customer_tasks** — WebArena Magento storefront browsing is another vertical/UI environment class, not a B2B sales-world capability.
- **magento_admin_store_management** — WebArena Magento admin is a browser-UI e-commerce benchmark in another vertical, explicitly outside a sales-domain API environment.
- **multi_app_office_automation** — OfficeBench's Linux-container docx/xlsx/PDF/shell environment is a different environment class, not a sales-domain CRM world capability.
- **multi_tool_api_planning_rapidapi** — ToolBench is a generic 16k-API tool-retrieval/planning benchmark with LLM-judged pass rates — a benchmark technique and corpus, not a sales-domain environment c
- **multilingual_long_horizon_workplace_tasks** — Instruction-language multilinguality is a benchmark-design axis, not an environment feature; nothing environment-side blocks authoring non-English task instruct
- **no_user_and_user_solo_ablations** — tau2-bench no-user/user-solo modes are harness/scoring diagnostics (a benchmark technique), squarely outside environment features — exactly the scoring-techniqu
- **pass_hat_k_reliability_metric** — pass^k is a reliability scoring metric — explicitly a benchmark scoring technique, not an environment feature.
- **retail_policy_constrained_customer_service** — tau-bench retail vertical (orders, returns, exchanges) — another vertical, not a sales-domain environment capability.
- **run_tracing_observability** — Step-tree run traces, per-step token/cost accounting, and per-claim source attribution are agent-harness telemetry — a benchmark/infrastructure concern, not a s
- **servicenow_atomic_ui_tasks** — WorkArena runs on a live ServiceNow instance via browser automation — a ServiceNow-UI benchmark in another vertical, not a sales-domain environment capability.
- **trajectory_match_and_multiturn_llm_judge** — Trajectory matching plus a 5-dimension LLM-judge rubric — benchmark scoring techniques (the multi-turn user simulator part is already a stated harness feature).
- **workarena_pp_compositional_workflows** — ServiceNow browser-UI benchmark — explicitly the ServiceNow-UI exclusion; judged via a ServiceNow instance backend, not this sales world.

## Prioritized close-the-partials roadmap

The 96 partials cluster into a handful of cross-cutting misses; closing these clusters
resolves most rows at once:

1. **Outbound send channel** (~15 partials): a logged `send_email`/`post_message` write
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
SERP/SMTP surfaces is exactly what the blobfish `mock_services` mechanism is for, but
each adds hundreds of ops — gate on demonstrated need, validate Flash-first.

## Reproduce

```
node scripts/build-coverage-md.mjs           # this file
node scripts/seed-wave6-documents.mjs        # in-world document corpus
node sim/run-flake-scan.mjs --all --trials 2 --label w6-flash-validation \
     --world-file world/blobfish-wave6/world.json --model deepseek-v4-flash
```
