# Why a salesperson touches every tool — per-vendor scenario map

> One concrete scenario per tool: who (AE, SDR, CSM, RevOps, deal desk, finance),
> what triggered it, and what they do — grounded in the Morgan Stanley
> (SIMULATED) world (Summit/Riverside/Meridian/Ironwood/Harborview/Atlas/
> Crestline accounts, the SOP corpus, the renewal timeline). Covers all 407
> tools across the 11 vendor MCP servers after the wave-6 densification
> (see docs/MCP-RATIONALE.md for why each vendor exists at all).

## salesforce-crm — Salesforce Sales Cloud (SIMULATED)

The CRM of record for the Morgan Stanley (SIMULATED) sales org — the spine every other system hangs off. AEs, SDRs, AMs, sales managers, and RevOps live here: accounts and contacts for Summit Group, Riverside, Meridian, Ironwood, Harborview, Atlas, and Crestline; leads worked against the lead-scoring policy; opportunities advanced through stage gates; and the handoff records that connect sales to marketing, sourcing, and finance. If it isn't in Salesforce, it didn't happen — which is exactly why reps are in these tools all day.

- **account_create** (write) — After qualifying an inbound lead from Crestline's newly spun-out logistics subsidiary that has no CRM footprint, Mei Huang (SDR) creates a fresh account record so the opportunity she's about to hand to an AE has a proper parent.
- **account_get** (read) — Prepping for the Summit Group renewal call, the AM pulls the Summit account record to confirm tier, owner, and contract anchor dates before opening the renewal playbook.
- **accounts_list** (read) — During Monday pipeline review, the sales manager lists all accounts in the territory to spot which of Riverside, Meridian, and Ironwood are missing an owner after last week's territory reshuffle.
- **contact_create** (write) — When a Harborview discovery call surfaces a new VP of Procurement as the real economic buyer, the AE creates the contact immediately so the opportunity's buying committee is on record before stage-gate review.
- **contact_get** (read) — Before a cold follow-up, Mei Huang pulls the Atlas contact record to check title and last-activity date so she doesn't re-email a prospect the AE already touched yesterday.
- **contacts_list** (read) — Building the invite list for the Meridian executive business review, the AM lists every Meridian contact to catch stakeholders who joined the account since the last QBR.
- **core_records_agent** (read) — Unsure whether a paused Ironwood deal still counts as "active" for tiering, the AE asks the core records agent to read the account-tiering standard and activity-logging standards before the forecast call.
- **core_workflow_agent** (write) — After RevOps ratifies a new revenue threshold for Tier 1, the sales manager runs the core workflow agent to update the account-tiering standard so downstream account classification matches the new policy.
- **get_contactdb_segments_segment_id** (read) — Ahead of her re-engagement blitz, Mei Huang pulls the "warm re-engagement" segment by ID to verify the Crestline contacts she plans to sequence actually landed in it.
- **get_mc_contacts_exports_id** (read) — Marketing ops checks the status of yesterday's contact export job to confirm it finished cleanly before the Harborview event list ships to the mailing vendor.
- **lookup_sales_lead_with_employees** (read) — Triaging an SLA breach, the sales manager looks up the stale Atlas lead joined to its owning employee to see it's assigned to Mei Huang and whether the assignment followed round-robin rules.
- **lookup_sales_opportunity_with_sales_leads** (read) — During pipeline hygiene, RevOps joins a Meridian opportunity back to its originating lead to verify the lead actually cleared the scoring threshold before conversion, per the lead-scoring policy.
- **marketing_records_agent** (read) — Before crediting the webinar campaign as the source of the Ironwood deal, the AE asks the marketing records agent for the segment membership and link-click stats tied to that campaign.
- **marketing_workflow_agent** (write) — After the Crestline nurture sequence is approved, marketing ops runs the marketing workflow agent to update the target segments and rotate the sequencing integration's API key in one pass.
- **opportunity_create** (write) — The moment the Crestline lead clears the lead-scoring threshold, the receiving AE creates a Stage 1 opportunity with amount and close date so the SDR-to-AE handoff has a pipeline anchor.
- **opportunity_get** (read) — Before approving an advance to Negotiate, the sales manager pulls the Harborview opportunity to check the security-review exit criterion is satisfied per the opportunity stage gates.
- **post_marketing_contacts_batch** (write) — Back from the industry conference with 60 badge scans, Mei Huang batch-uploads the new contacts so they enter the nurture flow before the leads go cold.
- **query_sales_leads** (read) — At the start of her shift, Mei Huang queries open leads scored above threshold and untouched for more than 48 hours to build her call list per the lead-scoring policy's SLA.
- **sales_records_agent** (read) — Prepping Monday's forecast, the sales manager asks the sales records agent to sweep accounts, open cases, and pending sales handoffs for anything that could derail the Meridian close this quarter.
- **sales_workflow_agent** (write) — After the Summit renewal signs, the AM runs the sales workflow agent to close the open case, flip the sales handoff to accepted, and update the account record in a single coordinated pass.
- **sourcing_records_agent** (read) — Before quoting an integration that depends on a third-party component, deal desk reads the sourcing handoffs, customer records, and journal entries to confirm the vendor cost is already booked.
- **sourcing_workflow_agent** (write) — When Ironwood's procurement pilot converts to paid, the AM runs the sourcing workflow agent to mark the sourcing handoff complete and post the journal entry against the customer record.
- **update_sales_leads_status** (write) — After three no-answer calls and a bounced email, Mei Huang sets the Atlas lead's status to Recycled per the lead-scoring policy so it drops out of the active SLA queue instead of rotting as "Working".

# revops-core — Internal RevOps data platform (SIMULATED)

The internal system-of-systems the RevOps team runs for the Morgan Stanley (SIMULATED) GTM org: it fronts the cross-team handoff registry, the HR/finance/marketing operational tables, the help-center content stack, the billing read surface, and the agent's own knowledge and memory stores. RevOps analysts live in it daily; sales managers and deal-desk use it for pipeline and policy state; AEs, SDRs, and CSMs touch it indirectly through internal tooling when a deal crosses a team boundary — a lead scored past threshold, a signed order handed to finance, a renewal escalated to sourcing.

## Sales pipeline

- **opportunities_list** (read) — a sales manager running Monday pipeline review lists all open opportunities to see which of the Summit, Riverside, and Meridian deals slipped their close dates over the weekend.
- **query_sales_opportunities** (read) — a RevOps analyst auditing forecast accuracy queries opportunities in Negotiate stage with amounts over $100k to test how many actually cleared the CPQ discount policy's approval gate.
- **update_sales_opportunities_status** (write) — after the Ironwood order form comes back signed, the deal-desk analyst flips the Ironwood opportunity's status to closed-won so the quarter roll-up stops counting it as commit.

## Cross-team handoffs

- **query_company_sales_handoffs** (read) — Mei Huang, the SDR, queries pending sales handoffs each morning to confirm the two leads she scored past threshold yesterday actually landed in an AE's queue per the lead scoring policy.
- **query_company_marketing_handoffs** (read) — a marketing ops teammate queries open marketing handoffs to find which webinar-sourced accounts, including Harborview, are still waiting on a nurture-track assignment.
- **query_company_finance_handoffs** (read) — a finance partner closing the month queries finance handoffs to catch closed-won deals like Ironwood whose invoicing packets never arrived from sales.
- **query_company_sourcing_handoffs** (read) — a RevOps analyst queries sourcing handoffs to see which vendor-replacement requests raised during the Meridian security review are still unassigned.
- **lookup_company_sales_handoff_with_volume_bands** (read) — an AE picking up the Riverside handoff pulls it joined with its volume band to know whether Riverside's projected seat count prices into the enterprise or mid-market tier before the first call.
- **lookup_company_marketing_handoff_with_volume_bands** (read) — a marketing ops analyst planning the Q3 ABM push looks up the Summit Group marketing handoff with its volume band to decide if Summit's spend tier justifies a dedicated campaign.
- **lookup_company_finance_handoff_with_volume_bands** (read) — a finance partner validating the Ironwood invoice looks up its finance handoff with volume bands to confirm the discounted price still lands inside the band the CPQ policy allows.
- **lookup_company_sourcing_handoff_with_volume_bands** (read) — a deal-desk analyst pulls the Harborview sourcing handoff with its volume band to check whether the promised implementation-partner volume triggers a different vendor rate card.
- **update_company_sales_handoffs_status** (write) — after the Riverside discovery call is booked, the accepting AE marks the sales handoff accepted so Mei stops chasing it and the SLA clock closes clean.
- **update_company_marketing_handoffs_status** (write) — a marketing ops teammate marks the Harborview handoff complete once the account is enrolled in the renewal-awareness nurture sequence.
- **update_company_finance_handoffs_status** (write) — the finance partner marks the Ironwood finance handoff processed after the invoice is issued, so month-end reconciliation shows no orphaned closed-won deals.
- **update_company_sourcing_handoffs_status** (write) — a RevOps analyst closes out the Meridian sourcing handoff as resolved once the replacement data vendor is contracted.

## Customers, vendors, and support surface

- **customers_list** (read) — a CSM preparing quarterly business reviews lists customers by segment to build the visit order for the five strategic accounts, Summit first.
- **customer_get** (read) — an AE prepping the Summit Group renewal pulls Summit's customer record to see tenure, plan, and open escalations before drafting the renewal proposal per the renewal playbook.
- **customer_create** (write) — after Riverside signs, the deal-desk analyst creates Riverside's customer record so onboarding and billing have a canonical entity to attach to.
- **vendor_get** (read) — a deal-desk analyst reviewing the Meridian implementation quote pulls the proposed subcontractor's vendor record to verify it passed security review before it goes in the SOW.
- **vendors_list** (read) — a RevOps analyst refreshing the partner directory lists active vendors to spot which data-enrichment providers are up for contract renewal this quarter.
- **vendor_create** (write) — after sourcing approves a new gifting service for the SDR team's outbound plays, a RevOps analyst creates its vendor record so POs can reference it.
- **query_sourcing_vendors** (read) — vetting subcontractors for the Harborview implementation, a deal-desk analyst queries sourcing vendors filtered to approved status to shortlist only ones with a live master agreement.
- **lookup_sourcing_vendor_with_employees** (read) — before escalating a late deliverable on the Meridian rollout, a RevOps analyst looks up the vendor joined with its owning employees to find which internal sponsor manages that relationship.
- **update_sourcing_vendors_status** (write) — after the enrichment provider fails its annual security reassessment, a RevOps analyst sets the vendor's status to suspended so no new SDR tooling POs route to it.
- **case_get** (read) — a CSM walking into the Harborview renewal call pulls the open support case to know exactly where the unresolved SSO ticket stands before the customer raises it.
- **retrieve_conversation** (read) — an AE retrieves the support conversation thread where Meridian's admin complained about API limits, so the upsell pitch addresses it head-on.
- **calls_info** (read) — a sales manager coaching a new AE pulls the record of last week's Ironwood call to review the logged outcome against what actually got committed.
- **calls_add** (write) — after a 40-minute Riverside discovery call, the AE logs the call with its outcome and next step so pipeline hygiene checks stop flagging the account as untouched.
- **calls_update** (write) — Mei updates her logged Harborview cold call to correct the disposition from "no answer" to "connected — meeting booked" after the prospect called back.
- **list_admins** (read) — a RevOps analyst rebalancing support coverage lists workspace admins to see who can take escalations during the EMEA morning window.
- **retrieve_admin** (read) — before routing the Summit escalation, a CSM retrieves the on-call admin's profile to confirm they cover enterprise accounts.
- **identify_admin** (read) — an internal tooling script acting for a sales manager identifies the current admin session to confirm it has the app scopes needed before triggering a data export.
- **create_data_export** (write) — a RevOps analyst kicks off a customer-and-cases data export to build the churn-risk model input file the CRO asked for by Thursday.

## Billing and payments (read surface for deal context)

- **get_balance_transactions** (read) — a finance partner reconciling the Ironwood closed-won pulls balance transactions to confirm the first payment actually settled before commission is released.
- **get_credit_notes** (read) — before quoting the Summit renewal, the deal-desk analyst pulls Summit's credit notes to net out the service-outage credit issued in Q2.
- **get_billing_credit_balance_summary** (read) — a CSM answering Harborview's "why is our invoice smaller" email pulls the credit balance summary to show the promo credit that was applied.
- **get_billing_credit_balance_transactions_id** (read) — a finance partner disputes a line item by pulling the specific credit-balance transaction Meridian's AP team is asking about.
- **get_billing_meters_id** (read) — an AE building the Meridian upsell case pulls the account's usage meter to show consumption running 3x above their contracted band.
- **post_billing_meters** (write) — after the Riverside contract adds a usage-based API tier, a RevOps analyst provisions the new billing meter so overage revenue starts accruing from day one.
- **get_entitlements_active_entitlements** (read) — a CSM fielding "do we have the analytics module?" from Summit pulls active entitlements to answer from the contract's actual feature list.

## Finance: journals and budgets

- **journal_entries_list** (read) — a finance partner closing Q3 lists journal entries tagged to the sales org to verify every commission accrual has a matching entry.
- **journal_entry_get** (read) — auditing the Ironwood deal's revenue recognition, a finance partner pulls the specific journal entry to check the deferred-revenue split.
- **journal_entry_create** (write) — after the Summit renewal signs with a multi-year ramp, the finance partner books the journal entry apportioning year-one revenue versus deferred balance.
- **query_finance_budgets** (read) — a sales manager pitching two extra SDR heads queries the sales department's remaining budget to see if headcount fits without a reforecast.
- **lookup_finance_budget_with_departments** (read) — a RevOps analyst building the annual plan looks up budgets joined with departments to compare marketing's program spend against sales' tooling spend line by line.
- **update_finance_budgets_status** (write) — once the CRO signs off on the revised events budget, the finance partner flips the budget's status to approved so field marketing can commit deposits.

## HR and people

- **query_employees** (read) — a RevOps analyst rebuilding territory assignments queries active sales employees to get the current AE roster before carving the Northeast patch.
- **lookup_employee_with_departments** (read) — routing the Riverside handoff, Mei looks up the accepting AE joined with department to confirm they sit in mid-market, not enterprise.
- **query_departments** (read) — a RevOps analyst standing up the new revenue dashboard queries departments to map which cost centers roll up under the CRO.
- **update_departments_department_code** (write) — after the SDR team merges into demand gen, a RevOps analyst updates the department code so comp reports and handoff routing stop splitting the team in two.
- **query_employee_work_assignments** (read) — a sales manager planning Summit renewal coverage queries work assignments to see who is already staffed on strategic-account motions this quarter.
- **lookup_employee_work_assignment_with_employees** (read) — before assigning the Meridian upsell, the manager looks up current assignments joined with employee records to avoid double-booking the one AE who knows Meridian's stack.
- **update_employee_work_assignments_status** (write) — when the Harborview migration project wraps, the sales manager marks the supporting SE's work assignment complete so they free up for the Ironwood pilot.
- **update_employees_status** (write) — after an AE's last day, a RevOps analyst sets their employee status to inactive so open Riverside-patch opportunities reroute rather than sitting on a ghost owner.
- **query_hr_leave_requests** (read) — a sales manager building the end-of-quarter close schedule queries pending leave requests to see who is out the last week of September.
- **lookup_hr_leave_request_with_employees** (read) — before approving overlapping PTO, the manager looks up the two leave requests joined with employee records to confirm they are not both from the Summit account team.
- **update_hr_leave_requests_status** (write) — the sales manager approves Mei's leave request for the week after pipeline-generation sprint ends, updating its status so payroll and the coverage calendar sync.
- **query_hr_performance_reviews** (read) — preparing comp-cycle calibration, a sales manager queries this cycle's performance reviews to see which AE writeups are still in draft.
- **update_hr_performance_reviews_status** (write) — after the calibration meeting, the manager finalizes each AE's review status so merit letters can generate on schedule.
- **human_resources_records_agent** (read) — a RevOps analyst asks the HR records agent for a combined view of leave and review data to explain why Q2 productivity dipped on the team covering Meridian.
- **human_resources_workflow_agent** (write) — a sales manager delegates the whole end-of-cycle chore to the HR workflow agent: approve the pending leave backlog and submit the finalized reviews in one pass.

## Marketing ops

- **query_marketing_campaigns** (read) — a RevOps analyst auditing pipeline sources queries active campaigns to see which ones actually sourced the Riverside and Harborview opportunities.
- **lookup_marketing_campaign_with_employees** (read) — before the Q3 planning meeting, a marketing ops teammate looks up the ABM campaign joined with its owning employees to know who defends its budget line.
- **update_marketing_campaigns_status** (write) — once the summer webinar series wraps, the marketing ops teammate marks the campaign complete so its spend stops accruing against the events budget.
- **query_marketing_content_assets** (read) — an AE hunting for a security one-pager to send Meridian's CISO queries content assets filtered to the compliance topic.
- **lookup_marketing_content_asset_with_marketing_campaigns** (read) — a marketing ops analyst pruning stale collateral looks up each asset joined with its campaign to find pieces orphaned by retired campaigns.
- **update_marketing_content_assets_status** (write) — after legal flags the old pricing sheet Mei has been attaching to outbound, the marketing ops teammate sets the asset's status to retired so it drops out of the SDR enablement library.

## Email marketing (deliverability and sends)

- **get_campaigns** (read) — a marketing ops teammate reviews the running email campaigns to confirm the renewal-reminder track targeting Summit-sized accounts is live before renewal season.
- **post_campaigns** (write) — for the Q4 pipeline push, the marketing ops teammate creates a new email campaign aimed at accounts the lead scoring policy grades A but that have no open opportunity.
- **patch_campaigns_campaign_id** (write) — after the first send underperforms, the teammate patches the campaign's subject line and send window before the second wave goes to the Harborview segment.
- **get_marketing_singlesends** (read) — before the product-launch announcement, a marketing ops teammate reviews scheduled single sends to make sure it will not land the same day as the Ironwood renewal notice.
- **post_marketing_singlesends** (write) — the CMO wants a same-day note about the analyst-report win, so the teammate creates a one-off single send to all open-opportunity contacts.
- **patch_marketing_singlesends_id** (write) — spotting a broken registration link minutes before launch, the teammate patches the single send's body and reschedules it for the top of the hour.
- **getall_automation_stats** (read) — a RevOps analyst grading the nurture program pulls stats across all automations to see which sequence actually converts scored leads into meetings for SDRs like Mei.
- **get_automation_link_stat** (read) — investigating why the renewal-playbook nurture drives no demo bookings, the analyst pulls per-link click stats to find that nobody clicks past the pricing link.
- **get_suppression_bounces** (read) — after the Meridian buying committee stops receiving sequence emails, a marketing ops teammate pulls the bounce list and finds their new mail gateway rejecting the sends.
- **get_suppression_blocks** (read) — troubleshooting why nothing reaches Harborview, the teammate pulls suppression blocks to see the domain landed on the block list after a mass send.

## Knowledge, memory, and playbooks

- **search_knowledge** (read) — before quoting a 22% discount on Riverside, an AE's assistant searches the knowledge base for the CPQ discount policy to find the approval threshold it crosses.
- **add_to_knowledge** (write) — after deal-desk clarifies how multi-year ramps interact with the discount cap, a RevOps analyst adds the ruling to the knowledge base so the next Summit-sized renewal doesn't relitigate it.
- **search_memory** (read) — picking the Meridian upsell back up after two weeks, the agent searches its memory for the stakeholder map and objection notes captured during the last working session.
- **save_memory** (write) — after learning that Harborview's procurement only reviews contracts on the first Monday of the month, the agent saves that fact to memory so future renewal timelines plan around it.
- **query_files** (read) — assembling the Summit renewal packet, the agent queries its stored files for the signed order form and last year's pricing exhibit.
- **list_playbooks** (read) — starting a renewal motion on Summit, the agent lists available playbooks to confirm which version of the renewal playbook is current before executing its steps.
- **create_playbook** (write) — after three SDRs independently rediscover the same re-engagement sequence for dark accounts, a RevOps analyst codifies it as a playbook so Mei's whole pod runs it the same way.

## Help center and internal content

- **list_articles** (read) — a CSM answering Harborview's SSO question lists help-center articles on authentication to link the customer the canonical setup guide.
- **retrieve_article** (read) — before the Meridian admin call, the CSM retrieves the API rate-limit article to quote its exact thresholds rather than paraphrasing.
- **create_article** (write) — after fielding the same data-residency question from three prospects, a RevOps analyst drafts a help-center article so AEs can link it instead of escalating to legal.
- **update_article** (write) — when the new pricing tiers ship, the analyst updates the plans-and-billing article so renewal conversations like Summit's reference the current numbers.
- **get_categories** (read) — reorganizing the help center before renewal season, a marketing ops teammate pulls the category tree to see where renewal and billing content is scattered.
- **create_collection** (write) — a RevOps analyst creates a "Renewals" collection grouping the playbook summaries, billing FAQs, and escalation paths CSMs need during Q4.
- **retrieve_collection** (read) — checking coverage before enablement week, the analyst retrieves the onboarding collection to see which articles new AEs actually get pointed to.
- **update_collection** (write) — after the CPQ policy revision, the analyst updates the deal-desk collection to swap in the new discount-approval articles and drop the superseded ones.
- **create_news_item** (write) — when the discount-approval threshold drops from 20% to 15%, a RevOps analyst posts a news item so every AE sees the CPQ policy change before quoting.
- **retrieve_news_item** (read) — an AE back from two weeks of PTO retrieves the pinned news item to catch the comp-plan clarification announced while they were out.
- **update_news_item** (write) — after finance corrects the effective date on the pricing change, the analyst updates the news item so nobody quotes Summit off the wrong cutover date.
- **create_content_import_source** (write) — migrating the old wiki's sales SOPs, a RevOps analyst creates a content import source pointed at the legacy export so the renewal playbook lands in the help center.
- **get_content_import_source** (read) — mid-migration, the analyst pulls the import source's record to see whether the lead-scoring policy batch finished syncing or stalled.
- **update_content_import_source** (write) — after the legacy wiki URL changes, the analyst updates the import source's endpoint so the nightly content sync stops failing.

## Workspace and platform admin

- **get_api_keys** (read) — before rotating credentials, a RevOps analyst lists the platform's API keys to find which one the pipeline-sync integration still uses.
- **create_api_keys** (write) — standing up the new forecast dashboard, the analyst creates a scoped read-only API key so the dashboard can pull opportunity data without write access.
- **patch_api_keys_api_key_id** (write) — after the quarterly security review, the analyst patches the aging integration key to narrow its scopes to the two endpoints the sync actually calls.
- **task_create** (write) — spotting that the Ironwood opportunity has no logged next step, a sales manager creates a task assigning the AE to book the pricing call by Friday.
- **task_get** (read) — before the 1:1, the manager pulls the specific overdue Riverside task to see what blocked it before asking the AE.
- **tasks_list** (read) — Mei starts her day by listing her open tasks to work the handoff follow-ups and call-backs in SLA order.

# stripe-billing scenarios

## stripe-billing — Stripe Billing (SIMULATED)

Stripe Billing is where the Morgan Stanley (SIMULATED) GTM org's subscription money actually moves: billing specialists run the dunning ladder against past-due subscriptions and stuck PaymentIntents, finance managers capture retainers and reconcile balances at month-end, deal desk mints the coupons and payment links that back approved concessions, CSMs watch subscription health (Ironwood past_due, Atlas flagged cancel_at_period_end) ahead of the renewal playbook's 120-day timeline, and RevOps analysts audit the event stream to keep CRM and billing in sync across the named accounts (Summit Group, Riverside, Meridian, Ironwood, Harborview, Atlas, Crestline).

- **get_customers** (read) — A RevOps analyst kicking off the renewal playbook's T-120 sweep lists the Stripe customer roster to match cus_ ids to Summit Group, Meridian, and the other CRM accounts before any renewal invoice goes out.
- **get_customers_customer** (read) — A billing specialist replying to an email from ap@summit-group.example retrieves Summit Group's customer object to verify the receipt email and default payment method on file before re-sending the renewal invoice.
- **post_customers** (write) — After Mei Huang's outbound sequence converts a new Crestline affiliate entity, the billing specialist creates its customer object with the finance contact's email so onboarding fees can be invoiced.
- **post_customers_customer** (write) — When the Summit renewal call series surfaces that Summit's AP contact changed, the billing specialist updates the customer's receipt email so dunning notices stop bouncing.
- **get_products** (read) — A deal desk analyst scoping the Summit 120-seat expansion bundle lists active products to confirm what is quotable and that the retired Legacy Advisory Desk is excluded.
- **post_products** (write) — Deal desk stands up a new "Renewal Success Package" service product ahead of the FY2027 renewal push so CSMs can attach it to save-play quotes.
- **get_prices** (read) — A deal desk analyst validating a Harborview seat quote lists active prices to make sure it uses the current Research seat monthly list, not the retired 2025 price.
- **post_prices** (write) — After finance approves an annual prepay tier for Crestline's post-trial conversion, deal desk creates a new yearly recurring price on the Compliance Reporting Suite product.
- **get_subscriptions** (read) — A CSM running the renewal playbook T-120 kickoff lists non-canceled subscriptions and immediately flags Ironwood's past_due compliance suite and Atlas's cancel_at_period_end execution API for the at-risk cadence.
- **get_subscriptions_subscription** (read) — Prepping the Ironwood renewal sync, the CSM retrieves sub_00000000000005 to confirm it is still past_due with the period ending 2026-08-10 before starting the dunning ladder outreach.
- **post_subscriptions** (write) — Once Summit Group signs the 120-seat expansion, the billing specialist creates the new research-seat subscription on Summit's customer so billing starts on the agreed date.
- **post_subscriptions_subscription** (write) — After the win-back call lands, the CSM has billing clear cancel_at_period_end on Atlas's execution API subscription sub_00000000000006 so it renews instead of lapsing at period end.
- **delete_subscriptions_subscription** (write) — When Atlas formally declines the win-back after all, the billing specialist cancels the execution API subscription immediately so the customer is not charged again.
- **get_payment_intents** (read) — Working the weekly dunning ladder run, the billing specialist lists PaymentIntents to find the ones stuck in requires_payment_method (Meridian's true-up) and requires_confirmation (Ironwood's saved card).
- **post_payment_intents** (write) — The billing specialist creates a manual-capture PaymentIntent for Summit Group's Q4 advisory retainer, mirroring the Q3 retainer's capture-on-approval flow.
- **post_payment_intents_intent_confirm** (write) — After Ironwood ops re-authorizes the saved card, the billing specialist confirms pi_00000000000011 so it transitions out of requires_confirmation toward succeeded.
- **post_payment_intents_intent_capture** (write) — The finance manager captures Summit Group's $12,500 requires_capture Q3 retainer (pi_00000000000001) before the 7-day uncaptured window cancels it.
- **get_refunds** (read) — Closing the month, the finance manager reviews recent refunds and spots Riverside's still-pending €34 refund (re_00000000000006) that must clear before reconciliation.
- **post_refunds** (write) — After dunning reconciliation confirms Riverside was double-charged, the billing specialist creates a refund against the duplicate charge so funds return to the original card.
- **get_payment_links** (read) — Mei Huang, the SDR, lists payment links to grab the active research-seat-expansion URL for her outbound follow-up to a warm Harborview contact.
- **post_payment_links** (write) — Deal desk creates a promotion-code-enabled payment link for the Q3 portal bundle campaign so mid-market prospects can self-serve at the approved 15% discount.
- **post_invoices** (write) — The billing specialist creates a draft invoice for Meridian's annual analytics true-up so pending invoice items can accumulate on it before anything is sent.
- **post_invoices_invoice_finalize** (write) — Once the true-up lines are staged, the billing specialist finalizes Meridian's draft invoice — pending invoice items attach, totals compute, and the invoice moves draft→open where the dunning ladder can pick it up if unpaid.
- **post_invoices_invoice_void** (write) — Discovering Riverside was invoiced twice during the duplicate-payment incident, the billing specialist voids the second finalized invoice, keeping the papertrail intact since voids cannot be undone.
- **post_invoices_invoice_pay** (write) — At dunning ladder step two for Ironwood, the billing specialist attempts collection on the past-due invoice out of the normal schedule before the account escalates to credit hold.
- **post_invoiceitems** (write) — The billing specialist records Atlas's trade execution API overage as a pending invoice item with no invoice specified, so it lands automatically on Atlas's next invoice.
- **get_coupons** (read) — Before approving a new Ironwood concession, deal desk lists coupons and confirms the one-shot Summit renewal concession is already exhausted (redeemed once, no longer valid).
- **post_coupons** (write) — Deal desk mints a single-redemption amount-off coupon for the Ironwood save play, sized within the approved discount bands and tagged with the approver in metadata.
- **get_balance** (read) — The finance manager retrieves the account balance to compare available versus pending amounts per currency before the month-end sweep to the operating account.
- **get_events** (read) — A RevOps analyst debugging a CRM sync gap lists the last 30 days of events to confirm invoice.finalized actually fired for Meridian's invoice before blaming the webhook consumer.
- **get_disputes** (read) — After the fraudulent-reason refund on Crestline's compliance charge, the billing specialist lists disputes to check whether a formal chargeback accompanies it.
- **get_charges** (read) — The billing specialist reconciling Stripe against the ERP pulls the charge list to match ch_ ids to Harborview's research terminal seat payments.
- **get_charges_charge_dispute** (read) — The billing specialist retrieves the dispute attached to Crestline's compliance-suite charge to review its reason and status before assembling evidence.
- **get_invoice_rendering_templates** (read) — Before re-issuing Summit Group's renewal invoice, the billing specialist checks the invoice rendering templates to confirm the one in use surfaces the PO number field Summit's AP portal requires.
- **get_invoices** (read) — Running the weekly dunning ladder, the billing specialist lists open invoices across accounts to build the outreach queue from oldest past-due to newest.
- **get_payment_intents_intent_amount_details_line_items** (read) — When Meridian's AP asks what makes up the $4,800 true-up, the finance manager pulls the PaymentIntent's amount-details line items to itemize the answer.
- **post_charges** (write) — For a one-off onboarding milestone that sits outside subscription billing, the billing specialist creates a direct charge on Summit Group's saved payment method.
- **post_charges_charge_dispute_close** (write) — After Atlas confirms in writing that it withdrew the chargeback on the execution-services charge, the billing specialist closes the dispute to release the held funds.

## sendgrid-email — SendGrid (SIMULATED)

The outbound email infrastructure: sequenced touches, templates, suppression compliance, and deliverability. SDRs send from it (via sequencing policy), marketing runs sends and stats, and RevOps owns the suppression/consent surface the outbound SOP mandates checking before every send.

- **post_mail_send** (write) — Mei Huang sends outbound sequence step 1 to the Summit CFO; the logged send (with suppression check) is what makes cadence compliance verifiable.
- **sg_mail_sends_list** (read) — the sales manager audits what actually went to Meridian contacts last week before the exec sync, catching a duplicate step-2 send.
- **sg_templates_list** (read) — an SDR browses approved templates before starting the Harborview re-engagement play instead of freelancing copy.
- **sg_templates_get** (read) — RevOps pulls the renewal-notice template to verify it cites the current 60-day notice window from the MSA before the Ironwood renewal wave.
- **sg_templates_create** (write) — marketing creates the "Q3 pricing update" template after the FY2026 rate card lands, so reps stop pasting stale numbers.
- **sg_templates_update** (write) — marketing fixes the broken merge field in the follow-up template that rendered "{{first_name}}" to three Atlas contacts.
- **sg_template_version_create** (write) — marketing versions the outbound step-1 template for an A/B subject-line test per the sequencing playbook.
- **sg_contacts_upsert** (write) — after the Summit discovery call, the SDR upserts the two new stakeholders captured in the transcript into the marketing contact store.
- **sg_contacts_search** (read) — marketing searches for all contacts at @summitgroup domains before the ABM send to avoid emailing the active deal's exec sponsor mid-negotiation.
- **sg_contacts_list** (read) — RevOps samples the contact store during the data-hygiene sweep to measure email-field completeness against the data-quality rules.
- **sg_lists_list** (read) — marketing confirms which nurture lists exist before enrolling the closed-lost Atlas contacts into the 90-day win-back track.
- **sg_lists_create** (write) — marketing creates the "FY26 renewal notices" list scoped to accounts entering the 120-day renewal window.
- **sg_list_add_contact** (write) — the CSM adds the new Riverside champion to the customer-newsletter list after kickoff (consent noted in the CRM activity).
- **sg_segments_list** (read) — marketing checks the "engaged-90d" segment definition before the SQL-handoff campaign so MQL scoring matches the lead-scoring policy.
- **sg_unsubscribe_groups_list** (read) — before any send, the SDR sequencing job reads suppression groups to honor the outbound SOP's consent rules.
- **sg_unsubscribe_groups_create** (write) — RevOps creates a "product-updates" unsubscribe group so transactional renewal notices and marketing sends suppress independently.
- **sg_suppressions_add** (write) — the compliance-mandated unsubscribe: a Meridian contact replies "remove me" and the rep adds them to the marketing suppression group same-day.
- **sg_suppressions_list** (read) — RevOps verifies the complaining Harborview contact is actually suppressed before replying to the deliverability escalation.
- **sg_global_suppressions_add** (write) — legal orders a global suppression for a contact who revoked all consent — stronger than any single group.
- **sg_global_suppressions_list** (read) — the pre-send validation gate cross-checks the Summit send list against global suppressions, per the outbound SOP.
- **sg_blocks_delete** (write) — after Summit's IT confirms the false-positive firewall block, RevOps clears the block entry so the renewal notice can retry.
- **sg_bounces_delete** (write) — the SDR clears the bounce for a Crestline contact whose mailbox was full, re-enabling the final sequence step.
- **sg_stats_get** (read) — the sales manager pulls send/open stats for the week to see whether the new subject-line variant moved reply rates.
- **sg_stats_by_category** (read) — marketing compares the renewal-notice category's engagement against outbound-sequence stats for the QBR deck.
- **sg_senders_list** (read) — RevOps confirms which verified sender identities exist before pointing the sequencing job at the new sales alias.
- **sg_senders_create** (write) — RevOps registers "renewals@morganstanleysimulated.com" as a sender before the renewal-notice wave starts.
- **sg_senders_get** (read) — the deliverability check verifies the outbound sender's reply-to routes to the shared SDR inbox, not a departed rep.
- **sg_domains_list** (read) — during the deliverability incident, RevOps checks which sending domains exist and their verification state.
- **sg_domain_authenticate** (write) — RevOps completes domain authentication for the new subdomain before warming it for outbound sequences.
- **sg_api_keys_list** (read) — the security review inventories which integrations hold mail-send keys after the Stripe-webhook incident postmortem.
- **get_categories_stats** (read) — marketing trends the outbound category's opens across the quarter for the funnel-conversion report.
- **organization_records_agent** (read) — a rep asks the org sub-agent which department owns a shared inbox before routing an inbound reply.
- **organization_workflow_agent** (write) — RevOps routes a staffing change through the org workflow agent so email ownership follows the new territory map.

## slack — Slack (SIMULATED)

Deal-room messaging is where approvals become observable: the CPQ policy's Deal Desk → Compliance → Finance sequence travels as channel messages, escalations get paged into #revops-alerts, and reps coordinate handoffs in per-deal channels like #deal-room-summit. AEs and deal desk live here during quarter-end; RevOps engineers watch the alert channels.

- **conversations_list** (read) — an AE back from vacation lists channels to find which deal rooms were spun up for the accounts they own.
- **conversations_info** (read) — the deal desk analyst checks #deal-room-summit's topic to confirm which renewal quote version is under review before posting an approval.
- **conversations_history** (read) — a sales manager reconstructs the Deal Desk → Compliance → Finance approval order for the Ironwood deal by reading the deal room's message history.
- **conversations_replies** (read) — an AE re-reads the thread under Compliance's question about the Summit discount before drafting the response.
- **conversations_members** (read) — RevOps verifies the Finance approver is actually in the Meridian deal room before the approval sequence starts.
- **conversations_join** (write) — the CSM taking over Riverside post-sale joins its deal room to inherit context before the kickoff call.
- **conversations_invite** (write) — the AE invites the compliance officer into #deal-room-harborview when the deal crosses the $100k VP-approval threshold.
- **conversations_archive** (write) — RevOps archives the Atlas deal room after closed-lost cleanup so stale channels stop polluting search.
- **conversations_set_topic** (write) — the deal desk sets the Summit room topic to "Renewal Q3 — 12% uplift pending Finance" so every approver sees deal state at a glance.
- **conversations_set_purpose** (write) — the AE sets the new Crestline room's purpose to the opportunity ID so tooling can join messages back to the CRM record.
- **chat_post_message** (write) — the deal desk posts "approved at 12%" into the Summit deal room — the message that makes the mandated approval order verifiable in state.
- **chat_update** (write) — the AE corrects the posted close date in the pinned summary message after Legal slips the countersign by two days.
- **chat_delete** (write) — RevOps deletes an accidental paste of the internal pricing floor from a customer-visible shared channel per the confidentiality SOP.
- **chat_schedule_message** (write) — Mei Huang schedules a Monday 8am reminder into the SDR channel to work the weekend's inbound queue within the 5-minute-touch SLA.
- **chat_scheduled_messages_list** (read) — the sales manager audits scheduled sends before quarter-end freeze so no automated nudges land during executive negotiations.
- **users_list** (read) — RevOps enumerates workspace members to reconcile Slack accounts against the employee roster before territory rollout.
- **users_info** (read) — the deal desk resolves U-id in an approval message to a named approver when reconstructing who approved the Ironwood discount.
- **users_lookup_by_email** (read) — the escalation runbook resolves the on-call finance partner's email to a Slack ID before paging them into the deal room.
- **users_set_presence** (write) — an AE flips to away before a customer onsite so the routing bot skips them for speed-to-lead assignments.
- **reactions_add** (write) — the Compliance officer stamps ✅ on the discount request message — the lightweight ack the deal desk watches for.
- **reactions_remove** (write) — Compliance retracts an accidental ✅ added to the wrong quote version before Finance acts on it.
- **reactions_get** (read) — the deal desk checks whether both required approvers have ✅'d the Summit uplift before advancing the opportunity stage.
- **pins_add** (write) — the AE pins the executed order form link in the deal room so nobody re-reviews a stale draft.
- **pins_list** (read) — a new CSM reads the Riverside room's pins to find the MSA, order form, and health-score doc in one pass.
- **pins_remove** (write) — the deal desk unpins the superseded quote after finalize so the room's pinned state matches the CRM.
- **search_messages** (read) — RevOps searches "Harborview discount" across channels to locate where an off-policy verbal commitment was made.
- **usergroups_list** (read) — the router checks @deal-desk membership before assigning the approval task for the Meridian expansion.
- **usergroups_create** (write) — RevOps creates @renewals-q3 grouping the CSMs on the 120-day renewal timeline for one-mention paging.
- **usergroups_update** (write) — after territory reassignment, RevOps updates @west-enterprise so escalations reach the new owner, not the departed rep.
- **team_info** (read) — an integration health-check reads workspace identity before the nightly CRM-Slack reconciliation job runs.
- **emoji_list** (read) — RevOps confirms the custom ✅-approved emoji referenced by the approval-detection rule still exists after a workspace cleanup.
- **admin_conversations_create** (write) — RevOps programmatically creates the private #deal-room-crestline channel when the opportunity enters Negotiation per the deal-room SOP.
- **admin_conversations_rename** (write) — RevOps renames the room after the Summit entity name correction so channel names keep matching CRM account names.
- **conversations_create** (write) — the AE spins up a public working channel for the Meridian onboarding cross-team before handoff to CS.

## google-calendar — Google Calendar (SIMULATED)

Scheduling under an SLA: speed-to-lead booking, the Summit renewal call series, deal-desk reviews, and EBR cadences all live on calendars, governed by the meeting-scheduling SLA and meeting-type duration policies.

- **calendar_events_list** (read) — Mei Huang lists this week's events on the SDR calendar to confirm the inbound-demo slots the router promised are actually free.
- **calendar_events_get** (read) — the AE opens the Summit renewal call event to check attendees before sending the agenda.
- **calendar_events_insert** (write) — after a positive reply, the SDR books the Meridian discovery call within the SLA's 5-business-day window.
- **calendar_events_update** (write) — the AE replaces the full event when the Ironwood onsite changes day, time, and room — PUT semantics clearing stale fields.
- **calendar_events_patch** (write) — the CSM only patches the video link on the EBR event without touching time or attendees.
- **calendar_events_delete** (write) — the SDR cancels the demo after the Crestline prospect disqualifies, freeing the round-robin slot.
- **calendar_events_move** (write) — RevOps moves the recurring deal-desk review from the departed rep's calendar to the team calendar.
- **calendar_events_quick_add** (write) — the AE quick-adds "Summit follow-up tomorrow 2pm" from the call wrap-up notes.
- **calendar_events_instances** (read) — the sales manager expands the weekly Summit deal-desk series to see which instance conflicts with QBR week.
- **calendar_freebusy_query** (read) — the booking flow checks the AE's busy blocks before offering the Meridian CFO three slots — the round-robin's core primitive.
- **calendar_acl_insert** (write) — RevOps grants the new CSM reader access to the renewals calendar during territory transition.
- **calendar_acl_delete** (write) — RevOps revokes the departed rep's writer access per the account-transfer protocol.
- **calendar_acl_list** (read) — the audit checks who can write the executive calendar after the confidentiality review.
- **calendar_calendars_update** (write) — RevOps renames the "West Enterprise Demos" calendar after the territory re-carve.
- **calendar_calendars_delete** (write) — RevOps deletes the orphaned calendar left from the retired round-robin pool.
- **calendar_calendars_get** (read) — the integration verifies the renewals calendar's timezone before writing the T-120 reminder series.
- **calendar_calendars_insert** (write) — RevOps creates the "FY26 Renewals" calendar that carries every notice-window deadline from the MSA terms.
- **calendar_calendar_list_list** (read) — the AE lists subscribed calendars to find the shared deal-desk calendar they were invited to.
- **calendar_calendar_list_get** (read) — the assistant checks the color/visibility settings of the exec calendar entry before the board-week freeze.
- **calendar_calendar_list_insert** (write) — the new CSM subscribes to the renewals calendar on day one of onboarding.
- **calendar_colors_get** (read) — the dashboard maps calendar color ids to the team legend before rendering the coverage view.
- **calendar_settings_list** (read) — the booking flow reads defaultEventLength before quick-adding calls so durations match the meeting-type policy.
- **calendar_agent** (write) — a rep asks the scheduling agent in natural language to "find 30 minutes with the Summit CFO next week" and it books within policy.
- **query_calendar_events** (read) — the verifier-facing free-text search finds every event mentioning "Meridian" when auditing meeting-prep tasks.
- **create_scheduled_run** (write) — RevOps schedules the nightly stale-opportunity sweep that flags 21-day-quiet deals per the forecast methodology.
- **list_scheduled_runs** (read) — RevOps confirms the renewal-reminder job is still scheduled after the calendar migration.

# netsuite-erp scenarios

## netsuite-erp — NetSuite ERP (SIMULATED)

NetSuite is the system of record where GTM revenue becomes accounting reality for Morgan Stanley (SIMULATED): deal desk works the sales-order approval queue, billing specialists turn fulfilled orders into AR invoices and apply customer payments, finance managers run the AP side — vendor bill approvals gated on three-way match (BILL-3006 ↔ purchase_order_004) — and police the dunning ladder that has Crestline on credit hold, while RevOps analysts normalize multi-currency, multi-subsidiary pipeline for forecasting and ops keeps DFA appliance inventory ahead of committed orders for Summit Group, Riverside, Meridian, Ironwood, Harborview, Atlas, and Crestline.

- **erp_sales_orders_list** (read) — A deal desk analyst starts the morning by listing sales orders filtered to pendingApproval, surfacing Meridian's new-logo order and the Atlas win-back for the approval queue.
- **erp_sales_order_get** (read) — When Summit Group asks whether its DR-site appliances shipped, the AE retrieves SO-2026-0108 and sees the DFA-200 HA pair still sits in pendingFulfillment.
- **erp_sales_order_create** (write) — After the Summit renewal call series locks FY2027 pricing, the AE creates the renewal sales order for Summit Group, which enters the workflow in pendingApproval.
- **erp_sales_order_update_status** (write) — Deal desk approves Meridian's €190,000 new-logo order by transitioning SO-2026-0103 from pendingApproval to pendingFulfillment, knowing the tool rejects any jump that skips the lifecycle.
- **erp_saved_search_run** (read) — A RevOps analyst answering "what's still open for Harborview?" runs a saved search on the keyword "Harborview" that LIKE-matches tranId, customer name, memo, and status in one shot.
- **erp_invoices_list** (read) — The finance manager runs the weekly dunning ladder review by listing open invoices, catching Crestline's overdue INV-1006 — the Q4 true-up already at dunning level 2 with the account on credit hold.
- **erp_invoice_get** (read) — Before Harborview's milestone-two wire lands, the billing specialist retrieves INV-1002 to confirm €57,810 remains outstanding against the €117,810 total.
- **erp_invoice_create** (write) — Once Riverside's L2 feed rollout ships, the billing specialist creates the invoice from SO-2026-0102 with created_from set, opening it with the full amount remaining.
- **erp_items_list** (read) — A deal desk analyst quoting a Crestline revision lists catalog items with is_inactive filtered off to make sure the retired Team License never lands on a quote.
- **erp_item_get** (read) — The AE pricing Riverside's second trading desk retrieves FEED-MKT-L2 to confirm the $42,000 depth-of-book list price before sending numbers.
- **erp_item_create** (write) — RevOps adds a new "Renewal Success Package" service item to the catalog, posting to 4030 Services Revenue, so the renewal playbook's paid engagement tier can be ordered.
- **erp_inventory_levels_list** (read) — Before promising Ironwood a ship date on its four DFA-100 edge appliances, the ops-minded CSM lists inventory levels per DC and sees Newark has 36 available.
- **erp_inventory_adjustment_create** (write) — After the Frankfurt cycle count finds a damaged DFA-200, ops posts a -1 adjustment (memo referencing the count), relying on the guard that rejects any adjustment that would drive stock negative.
- **erp_vendor_bills_list** (read) — The finance manager pulls vendor bills filtered to approval_status pendingApproval and finds BILL-3006 waiting on its three-way match sign-off alongside the colocation and staffing bills.
- **erp_vendor_bill_get** (read) — Working the match, the finance manager retrieves BILL-3006 and reads the memo — "Three-way match: purchase_order_004 received 2026-01-07" — before touching the approval.
- **erp_vendor_bill_create** (write) — The billing specialist re-enters the rejected Lakeshore bill (BILL-3005 bounced for a missing PO reference) as a fresh bill with the purchase_order id in the memo, and it routes as pendingApproval again.
- **erp_vendor_bill_approve** (write) — With PO, receipt, and the £40.02 bill all agreeing, the finance manager approves BILL-3006 to complete the three-way match, knowing the tool refuses bills already approved or still rejected.
- **erp_customer_payments_list** (read) — Chasing reconciliation breaks, the billing specialist lists customer payments and filters for empty applied_to, surfacing Riverside's €5,000 wire held for a missing remittance advice.
- **erp_customer_payment_create** (write) — The billing specialist applies Atlas's $15,000 check to INV-1004, letting the tool cut the invoice's amount remaining and trusting its guards against overpayment, voided invoices, and currency mismatch.
- **erp_credit_memos_list** (read) — Prepping the Harborview QBR, the CSM lists open credit memos to confirm the €5,000 SLA credit for the onboarding delay is still unapplied and can be shown as a goodwill line.
- **erp_credit_memo_create** (write) — After the 2026-01-03 feed-outage postmortem, the CSM issues Riverside a credit memo referencing INV-1007 so the outage credit nets against the December overage.
- **erp_currencies_list** (read) — A RevOps analyst building the forecast roll-up lists currencies to convert the GBP and EUR order book to USD at the stored exchange rates.
- **erp_subsidiaries_list** (read) — Booking a new Crestline order, the finance manager lists subsidiaries to confirm it posts to Morgan Stanley (SIMULATED) International Ltd (subsidiary 3) rather than the elimination entity.
- **lookup_sourcing_purchase_order_with_sourcing_vendors** (read) — Running the BILL-3006 three-way match, the finance manager looks up purchase_order_004 joined to its sourcing vendor to confirm Fairview Systems Vendor and the ordered amount line up with the bill.
- **purchase_order_create** (write) — With Frankfurt's DFA-200 availability at 2 units against a reorder point of 3, ops raises a replenishment purchase order to the appliance vendor before Ironwood's committed units ship.
- **purchase_order_get** (read) — The finance manager retrieves purchase_order_004 directly to compare its quantity and unit price against BILL-3006's £40.02 before signing off the match.
- **purchase_orders_list** (read) — A RevOps analyst sizing quarter-end vendor commitments lists open purchase orders to see what AP exposure is still in flight across subsidiaries.
- **query_sourcing_purchase_orders** (read) — Fixing the rejected BILL-3005, the billing specialist queries sourcing purchase orders for Lakeshore's facilities work to find the PO reference the resubmitted bill must cite.
- **update_sourcing_purchase_orders_status** (write) — Once the dock confirms delivery, ops updates purchase_order_004's status to received (2026-01-07), completing the receipt leg so the BILL-3006 three-way match can close.

## notion-docs — Notion (SIMULATED)

The knowledge base holding the SOP corpus: CPQ discount policy, renewal playbook, battlecards, meeting notes, and the tracker databases. Documents are this world's difficulty lever — agents must read the governing SOP before acting — so this vendor is both reference library and working surface.

- **notion_search** (read) — before quoting, the AE searches "discount" and finds the CPQ policy page with the 10/20/30 approval bands.
- **notion_page_get** (read) — the deal desk opens the renewal-playbook page to confirm the T-120 timeline step before the Ironwood kickoff.
- **notion_page_create** (write) — the CSM creates the Riverside save-plan page after the champion departs (the Red health trigger).
- **notion_page_update** (write) — the enablement lead updates the battlecard title after Harborview rebrands, keeping search hits current.
- **notion_page_archive** (write) — RevOps archives the superseded FY25 rate-card page so nobody quotes stale prices.
- **notion_page_properties_get** (read) — the tracker sync reads the renewal page's status property to mirror it into the CRM report.
- **notion_databases_list** (read) — a new AE lists databases to find the Renewal Tracker and Battlecards libraries on day one.
- **notion_database_get** (read) — RevOps checks the Renewal Tracker's schema before adding the uplift-percentage column to the sync job.
- **notion_database_create** (write) — the enablement lead creates the "Win/Loss Themes" database after the QBR mandates tracking loss reasons.
- **notion_database_query** (read) — the CSM queries the Renewal Tracker for status=Yellow rows to build this week's save-play list (Ironwood surfaces).
- **notion_database_row_create** (write) — the AE adds Crestline to the Renewal Tracker the day the opportunity closes-won, per the playbook.
- **notion_database_row_update** (write) — the CSM flips Meridian's tracker row to Green after the EBR lands the expansion commit.
- **notion_blocks_children_list** (read) — the agent reads the CPQ policy page block-by-block to extract the exact Deal Desk threshold sentence for the approval citation.
- **notion_blocks_append** (write) — the deal desk appends the "approved at 12%, Finance sign-off 8/12" line to the Summit deal notes page.
- **notion_block_get** (read) — the audit pulls the specific to-do block cited in the compliance review to verify its checked state.
- **notion_block_delete** (write) — the enablement lead deletes the outdated objection-handling bullet the Atlas loss review disproved.
- **notion_comments_list** (read) — the AE reads Legal's comments on the MSA clause page before the redline call.
- **notion_comment_create** (write) — Compliance comments the required change on the pricing page instead of editing it directly, per the review SOP.
- **notion_users_list** (read) — RevOps reconciles Notion members against the employee roster during the quarterly access review.
- **notion_user_get** (read) — the audit resolves the page editor's ID to a named employee when tracing who changed the discount table.
- **document_agent** (write) — a rep asks the doc agent to draft the Meridian onboarding one-pager from the kickoff-call transcript.
- **query_documents** (read) — the agent free-text searches the seeded 46-doc anchor corpus for the MQL-SQL handoff SLA before accepting the lead.
- **read_file** (read) — the agent opens the pricing rate-card artifact to cross-check the order form's unit prices.
- **draft_matter_document** (write) — legal ops drafts the Summit order-form amendment as a matter document for countersign routing.
- **read_matter_document** (read) — the deal desk reads the executed Ironwood MSA to extract the renewal notice window.
- **query_matter_documents** (read) — legal ops lists all matter documents tied to Summit before the renewal negotiation opens.

## github — GitHub (SIMULATED)

The RevOps engineering surface: the `revops/*` repos hold the CRM-sync jobs, billing-reconciliation scripts, and dashboard code the GTM stack runs on. RevOps engineers live here; sales managers and finance touch it through the sheets/exports tools when an ops fix gates a deal.

- **gh_repos_list** (read) — a new RevOps engineer lists the revops org's repos to find which one owns the failing Stripe webhook retries.
- **gh_repo_get** (read) — the on-call checks revops/stripe-webhooks' default branch and last-push before deciding whether the fix already shipped.
- **gh_issues_list** (read) — the RevOps lead triages open issues labeled `billing` after the Harborview reconciliation mismatch is reported.
- **gh_issue_get** (read) — the engineer reads the Summit dedupe-survivor bug's full report before touching the merge logic.
- **gh_issue_create** (write) — the deal desk files "quote totals drift from rate card v3" when the Ironwood order form disagrees with CPQ output.
- **gh_issue_update** (write) — the engineer closes the webhook-retry issue after the backoff fix verifies against the replayed events.
- **gh_issue_comment_create** (write) — the on-call comments the root cause (retry queue capped at 3) so finance knows why Atlas invoices lagged.
- **gh_issue_comments_list** (read) — the RevOps lead reads the thread on the seeding bug before the postmortem to attribute the timeline correctly.
- **gh_pulls_list** (read) — the lead reviews open PRs against revops/billing-reconciliation before the quarter-end code freeze.
- **gh_pull_get** (read) — the reviewer checks whether the dunning-ladder PR targets main or the release branch before approving.
- **gh_pull_create** (write) — the engineer opens the exponential-backoff PR referenced in the webhook incident's runbook follow-up.
- **gh_pull_update** (write) — the author retitles the PR to include the incident number so the audit trail links code to page.
- **gh_pull_merge** (write) — the lead merges the reconciliation fix — advancing main — so tonight's Stripe↔NetSuite job runs clean before invoicing.
- **gh_pull_files_list** (read) — the reviewer confirms the PR only touches retry.py and not the payout mapping before quarter-end.
- **gh_pull_reviews_list** (read) — the lead verifies two approvals exist on the billing change, per the change-management policy.
- **gh_pull_review_create** (write) — a second engineer approves the CRM-dedupe PR after checking the survivorship rules against the data-quality SOP.
- **gh_commits_list** (read) — the on-call scans recent commits on main to find what changed before the leaderboard dashboard broke.
- **gh_commit_get** (read) — the engineer inspects the suspect commit's message and sha before reverting the fiscal-quarter ranking change.
- **gh_branches_list** (read) — the lead checks for stale feature branches in revops/crm-sync during the pre-freeze cleanup.
- **gh_branch_get** (read) — the deploy script verifies the release branch head matches the sha that passed CI before shipping the billing job.
- **gh_workflow_runs_list** (read) — the on-call filters failed ci.yml runs to see when the reconciliation pipeline started red-lining.
- **gh_workflow_run_get** (read) — the engineer opens the failing run to read which step died before paging stops being justified.
- **gh_workflow_run_rerun** (write) — after the flaky fixture is fixed, the on-call reruns the queued deploy so invoices generate on schedule.
- **gh_releases_list** (read) — finance asks which release introduced the proration change; RevOps lists releases to date the behavior shift.
- **gh_release_create** (write) — the lead cuts the "reconciliation-hotfix" release after the merge so the incident ticket can reference an artifact.
- **gh_search_code** (read) — the engineer searches for the hardcoded rate-card path across repos before rotating to the FY2026 file.
- **gh_search_issues** (read) — the RevOps lead searches issues mentioning "Summit" to gather every ops defect tied to the account ahead of the QBR.
- **sheet_agent** (write) — the RevOps analyst writes the forecast rollup rows into the shared sheet the sales manager reads at Monday pipeline review.
- **finance_records_agent** (read) — the finance partner resolves an expense-report handle through the records sub-agent while auditing deal-desk travel.
- **finance_workflow_agent** (write) — finance routes the expense-approval state change through the workflow agent per the approval matrix.
- **lookup_finance_expense_report_with_employees** (read) — the auditor joins the disputed expense report to its submitting employee before escalating.
- **query_finance_expense_reports** (read) — finance pulls all pending expense reports for the quarter-close accrual.
- **update_finance_expense_reports_status** (write) — finance approves the batch of verified reports so accruals post before close.

# Jira scenarios

## jira — Atlassian Jira (SIMULATED)

In the Morgan Stanley (SIMULATED) GTM org, Jira is the work-tracking backbone for revenue engineering: the RECON, BILL, GTM, CRM, DESK, and SUPP projects carry billing reconciliation for the Summit Group and Riverside books, MQL routing, CRM data hygiene, deal desk CPQ tooling, and the support desk's SLA machinery. RevOps engineers and analysts live here daily, while deal desk staff, support leads, sales managers, and SDRs like Mei Huang file and follow the issues that block their accounts and quotas.

- **jira_search** (read) — A RevOps analyst prepping the Q3 close searches "reconciliation" scoped to project RECON to surface every open issue touching the Summit Group Stripe-to-NetSuite mismatch before the close review.
- **jira_issue_get** (read) — A sales manager waiting on Crestline paperwork pulls DESK-8 to check whether the quote-PDF renewal-term bug is still Blocked before promising legal a date.
- **jira_issue_create** (write) — SDR Mei Huang, whose queue keeps receiving sub-band leads, files a new GTM bug asking that MQL routing respect the AUM-band boundaries from the tiering standard instead of raw revenue.
- **jira_issue_update** (write) — A RevOps engineer raises RECON-104 to Highest priority and appends the q3-close label after finance confirms the Meridian void-and-reissue duplicate journal entries are inflating recognized revenue.
- **jira_issue_delete** (write) — A RevOps engineer deletes a CRM ticket that was accidentally filed twice for the same Summit/Atlas dedupe batch, after confirming the surviving issue carries all the comments.
- **jira_issue_assign** (write) — Deal desk lead Jordan Reyes reassigns the Ironwood co-sell overlap check (DESK-9) to Priya Natarajan so it lands with the engineer who owns the deal registration form.
- **jira_issue_transition** (write) — A deal desk engineer moves DESK-7 from In Progress to In Review via the Submit for Review transition (id 21) once the CPQ >20% discount routing matches policy thresholds, attaching a comment for the finance reviewers.
- **jira_transitions_list** (read) — Before unblocking DESK-8, the deal desk lead lists the transitions valid from Blocked to confirm Unblock (id 61) is the only legal move now that the PDF template vendor shipped its fix.
- **jira_comment_add** (write) — A CSM comments on SUPP-55 that a Harborview escalation was mis-flagged as an SLA breach by the runaway timer, so support leadership has the customer context.
- **jira_comments_list** (read) — An AE tracking the CRM-22 lead-source wipe reads the comment thread to see Mei Huang's repro on lead L-2214 before the campaign-attribution review.
- **jira_worklog_add** (write) — A RevOps engineer logs 3h against RECON-101 for tracing the dropped Stripe reversal webhook across the 2026-07-28 deploy window.
- **jira_worklogs_list** (read) — A RevOps analyst tallies the worklogs on RECON-101 to quantify how much engineering time the Summit Group reconciliation mismatch has burned for the close post-mortem.
- **jira_watchers_add** (write) — A sales manager adds themselves as a watcher on DESK-8 so they hear the moment the Crestline multi-year quote bug unblocks.
- **jira_watchers_list** (read) — Support lead Marcus Webb lists the watchers on SUPP-55 before posting a fix update, confirming reporter Sarah Kim will be notified.
- **jira_labels_list** (read) — A RevOps analyst pulls the distinct label list to confirm q3-close is the canonical close-week tag before building the sprint filter, not a q3close variant.
- **jira_projects_list** (read) — A RevOps engineer onboarding to the team lists the software projects to map which teams own RECON, BILL, DESK, and SUPP.
- **jira_project_get** (read) — A deal desk analyst pulls the DESK project record to grab lead Jordan Reyes' email before escalating the stalled CPQ approval-queue work.
- **jira_project_components_list** (read) — A RevOps engineer filing the Meridian journal bug lists RECON components so it lands against Ledger Sync (Daniel Osei's component) rather than the Recon Dashboard.
- **jira_project_versions_list** (read) — A RevOps analyst checks RECON versions to see whether recon-2026.08 (daily export automation) releases before the August 29 close.
- **jira_boards_list** (read) — A sales manager who wants the live support backlog lists boards filtered to kanban to find the SUPP support kanban.
- **jira_board_get** (read) — A RevOps engineer confirms board 1 is the RECON scrum board before pointing the weekly sprint-report script at it.
- **jira_sprints_list** (read) — Ahead of Monday planning, the RECON lead lists active sprints on board 1 to confirm Sprint 5 ("Automate the Summit and Riverside daily recon") is still open.
- **jira_sprint_get** (read) — A RevOps analyst pulls sprint 5's dates and goal to judge whether the Riverside export automation can land before the 2026-08-14 sprint end.
- **jira_sprint_issues_list** (read) — A sales manager reviewing close readiness lists sprint 5 issues still In Review to see what needs approval before the recon release ships.
- **jira_priorities_list** (read) — A deal desk analyst reads the priority scheme definitions to decide whether the Crestline quote bug merits Blocker or stays at Highest.
- **jira_statuses_list** (read) — A RevOps engineer building the stale-issue report reads the status catalog so In Review and Blocked both roll up under the In Progress category correctly.
- **jira_users_search** (read) — A deal desk coordinator searches "Mei" to grab SDR Mei Huang's account email before adding her as a watcher on the GTM routing fix.
- **customer_support_records_agent** (read) — A CSM asks the support records agent to summarize every open Harborview ticket before the renewal-playbook QBR call.
- **customer_support_workflow_agent** (write) — A support lead invokes the workflow agent to run the standard escalation workflow on a Summit Group P1 ticket per the support escalation SOP.
- **lookup_support_ticket_with_employees** (read) — A sales manager looks up a Riverside support ticket joined with its assigned employee record to know exactly who to loop into the account call.
- **query_support_tickets** (read) — A RevOps analyst queries open support tickets by account to check whether Atlas has unresolved issues before the upsell proposal goes out.
- **update_support_tickets_status** (write) — A support lead moves a Meridian ticket to resolved once the CRM sync backlog clears and the client confirms their data is current.

# PagerDuty scenarios

## pagerduty-support — PagerDuty (SIMULATED)

PagerDuty guards the revenue-critical plumbing behind the GTM motion: the Stripe webhook gateway, billing alerts pipeline, nightly reconciliation, CRM sync, warehouse ETL, revenue dashboard, SendGrid email delivery, and the customer support portal. RevOps engineers and support leads run the on-call rotations; RevOps analysts and account-facing staff read incident state whenever Summit Group invoices, Meridian and Ironwood sync lag, or Harborview renewal notices are on fire. The same server also fronts the support-case and billing-alert surface used by the support desk.

- **pd_incidents_list** (read) — RevOps analyst Aisha Bello lists triggered high-urgency incidents at Monday standup and sees the Stripe webhook failure spike (PT4KHLK) still open before certifying the ARR dashboard numbers.
- **pd_incident_get** (read) — The AE on Summit Group pulls incident PQR2M8N to understand the 47 unmatched Stripe charges from the 02:00 payout batch before the client's billing call.
- **pd_incident_create** (write) — A RevOps engineer who catches renewal notices silently failing opens a high-urgency incident on the Email Delivery (SendGrid) service and lets the level-1 platform on-call be auto-assigned.
- **pd_incident_manage** (write) — The billing on-call acknowledges the Stripe webhook incident PT4KHLK, escalates it to level 2 of the billing policy (reassigning to Elena Rodriguez and re-triggering) when the 502 rate keeps climbing, and later resolves it with a resolution note once retries drain.
- **pd_incident_notes_list** (read) — A RevOps analyst reads the notes on the Summit Group reconciliation incident to pick up Elena Rodriguez's finding that all 47 unmatched charges came from the same payout batch.
- **pd_incident_note_create** (write) — A support lead adds a note to the CRM sync incident (PW9XJ3D) recording that the Meridian and Ironwood account teams were told their records are stale until the worker pool scales.
- **pd_incident_log_entries_list** (read) — A support lead writing the ETL post-mortem lists log entries for PD6TQ4W to reconstruct the trigger, acknowledgement-timeout escalation, and resolve timeline.
- **pd_services_list** (read) — A RevOps engineer lists Billing Engineering's services (team PTBILL1) to check which of the webhook gateway, alerts pipeline, and reconciliation jobs are currently degraded.
- **pd_service_get** (read) — A deal desk analyst checks the Stripe Webhook Gateway service (PSTRWBH), sees it is in critical state, and holds off promising Atlas an invoice-timing answer.
- **pd_service_create** (write) — A RevOps engineer standing up the new CPQ discount-approval microservice creates a PagerDuty service for it tied to the Billing Pipeline Escalation policy so approval outages page billing engineering.
- **pd_service_update** (write) — After the endpoint secret rotation and event replay finish, a RevOps engineer flips the Stripe Webhook Gateway status from critical back to active.
- **pd_escalation_policies_list** (read) — A support lead audits escalation policies by team to verify the support portal has a two-level policy in place before the weekend attachment-storage migration.
- **pd_escalation_policy_get** (read) — A RevOps engineer pulls PEPBILL to confirm level 2 is the billing systems lead before deciding whether to escalate the stuck reconciliation incident.
- **pd_schedules_list** (read) — A RevOps analyst lists the on-call schedules to find which rotation covers the revenue dashboard ahead of the quarter-close reporting weekend.
- **pd_schedule_get** (read) — A sales manager checks the Billing Engineering On-Call schedule's time zone before booking a Summit Group billing bridge call with the on-call engineer.
- **pd_schedule_overrides_create** (write) — A support lead creates an override putting Priya Natarajan on the Support Engineering weekend rotation for Aug 22-25 while Owen Fitzgerald runs the attachment-storage migration.
- **pd_oncalls_list** (read) — During the webhook failure spike, a RevOps analyst lists on-calls for the billing escalation policy and sees Tom Nakamura at level 1 and Elena Rodriguez at level 2 before pinging anyone directly.
- **pd_users_list** (read) — A support lead lists Support Engineering (PTSUP01) users to pick a second responder for the portal attachment-upload 5xx errors.
- **pd_user_get** (read) — A RevOps engineer pulls Mei Huang's user record (PHUANG1) and, seeing her limited_user role, routes the acknowledgement to Revenue Operations instead of asking the SDR to work the incident.
- **pd_teams_list** (read) — A newly hired RevOps engineer lists teams to learn that Billing Engineering owns the Stripe integration while CRM Integrations owns the sync.
- **pd_team_get** (read) — A sales manager pulls the Revenue Operations team record to see who owns forecast data quality before chasing the stale Riverside ARR tile.
- **pd_maintenance_windows_list** (read) — A RevOps analyst checks upcoming windows on the billing alerts pipeline and finds the Aug 12 broker upgrade will delay alerts up to 30 minutes during Riverside invoicing.
- **pd_maintenance_window_create** (write) — A RevOps engineer schedules a maintenance window on the CRM Sync service for the next stage-gate schema migration so the latency monitor's alerts are suppressed during the planned pause.
- **pd_priorities_list** (read) — A support lead reviews the P1-P5 definitions to decide the duplicate Atlas billing alerts warrant P3 (workaround exists) rather than P2.
- **case_create** (write) — A CSM opens a support case for Harborview after renewal notices bounced, referencing the SendGrid incident so the billing follow-ups are tracked to closure.
- **cases_list** (read) — A support lead lists open cases each morning to see which accounts — Summit Group and Atlas among them — are still waiting on the webhook backlog before triaging the day.
- **get_billing_alerts** (read) — A RevOps analyst pulls the current billing alerts to see which accounts tripped usage thresholds while the consumer group was 10k messages behind.
- **get_billing_alerts_id** (read) — A deal desk analyst fetches a specific Atlas renewal billing alert by ID to verify it is a webhook-retry duplicate before issuing the account a credit.
- **post_billing_alerts** (write) — A RevOps engineer posts a manual billing alert for a Summit Group usage-threshold breach the pipeline missed during the broker-upgrade window.
