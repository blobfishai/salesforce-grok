# RevOps Integration Map

> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

## 1. Scope

This map fixes system-of-record boundaries, sync order, the webhook catalog, and failure semantics across the four core systems: **CRM** (identity and pipeline), **Billing** (Stripe-style objects), **Marketing** (consent and sequences), and **Support** (cases). It governs every automated flow referenced in 09-order-activation-runbook.md and 16-data-quality-rules.md.

## 2. Source of Truth per Object

| Object | System of record | Notes |
|---|---|---|
| Accounts, Contacts, Leads | CRM | Identity master; merges originate here only (16-data-quality-rules.md) |
| Opportunities, Quotes | CRM | Stage gates per 04-opportunity-stage-gates.md; discounts per 05-cpq-discount-policy.md |
| Contracts, envelopes | CLM (mirrored to CRM) | Countersign by Sales Manager; envelopes void after 30 days unsigned |
| Invoices, PaymentIntents, CreditNotes, Refunds | Billing | Net 30; dunning at +7 / +21 / +45 days |
| Consent, subscription status | Marketing | Suppression list absolute (GDPR/CAN-SPAM); unsubscribes honored within 24h |
| Cases | Support | SLAs per 10-case-management-sla.md |
| Health score | CRM (computed) | Weights: usage 40% / support 25% / engagement 20% / billing 15% |

No system writes to an object it does not own; all cross-system updates flow through the event bus in Section 6.

## 3. Billing Object Mapping (Stripe-style)

- CRM Account maps 1:1 to a billing **Customer**. Every Customer carries `crm_account_id`; Billing never originates Customers — creation without the key is rejected.
- Closed-won order maps to a **Subscription**: 1-year term, auto-renews unless 60-day written notice; standard uplift 7% (14-renewal-playbook.md). The renewal opportunity is auto-created in CRM 120 days before `current_period_end`.
- **Invoice**: Net 30 from issue date. Dunning: +7 days reminder, +21 escalation, +45 service-suspension flag plus Finance review (08-finance-approval-thresholds.md).
- **CreditNote** requires Deal Desk Manager approval (Zoe Nakamura); **Refund** above $50,000 requires the Finance Controller (Marcus Webb).

## 4. Deal-Room Channels (Slack-style)

- A channel `#deal-{account-slug}-{opp-id}` (e.g., `#deal-meridian-holdings-opp-4183`) is auto-created when an opportunity reaches Negotiation or TCV >= $1M, whichever comes first.
- Members: owning AE, Sales Manager, Deal Desk Manager. The Compliance Officer (Nina Iyer) is auto-added when any regulated product from 13-product-catalog.md is on the quote.
- Catalog events 4, 5, 6, and 9 post bot messages to the deal room. Channel messages are advisory: AEs may not approve their own discounts in-channel or anywhere else (05-cpq-discount-policy.md), and the approval order stays strictly Deal Desk -> Compliance -> Finance (06-deal-desk-charter.md).
- Channels archive 30 days after Closed Won/Lost; transcripts retained per 11-activity-logging-standards.md.

## 5. Sync Order and Timing

Order within every cycle is fixed to prevent orphaned child records:

1. Consent (Marketing -> CRM) — every 15 min; unsubscribe propagation target 15 min, hard ceiling 24h.
2. Identity: accounts/contacts including merges (CRM -> Billing, Marketing, Support) — every 15 min.
3. Opportunities and quotes (CRM -> Billing staging, deal rooms) — hourly at :15.
4. Contracts (CLM -> CRM, Billing) — hourly at :30.
5. Invoices and payments (Billing -> CRM) — hourly at :45.
6. Cases and health inputs (Support -> CRM) — every 15 min; health score recomputed nightly at 01:00 ET.

Nightly full reconciliation runs at 02:00 ET; the variance report posts to `#revops-integrations`. Webhooks deliver near-real-time (<60s target) ahead of batch; batch is the authoritative backstop.

## 6. Webhook Event Catalog

All events share the envelope `{event_id (UUID), occurred_at (UTC), sequence, producer}`. Consumers must be idempotent on `event_id`.

| # | Event | Producer -> Consumers | Event-specific payload |
|---|---|---|---|
| 1 | `lead.scored` | Marketing -> CRM | `{lead_id, score, band, segment, region}` (bands per 02-lead-scoring-policy.md) |
| 2 | `lead.mql_created` | CRM -> Marketing, SDR queue | `{lead_id, score, sal_deadline}` — accept/reject within 4 business hours (01-lead-management-sop.md) |
| 3 | `account.merged` | CRM -> Billing, Marketing, Support | `{primary_id, merged_id, survivor_rule: "oldest"}` |
| 4 | `opportunity.stage_changed` | CRM -> deal room, forecast | `{opp_id, account_id, from_stage, to_stage, tcv_usd, forecast_category}` |
| 5 | `opportunity.closed_won` | CRM -> Billing, deal room | `{opp_id, account_id, tcv_usd, products[], discount_pct}` — triggers 09-order-activation-runbook.md |
| 6 | `quote.approved` | CRM -> deal room, Billing staging | `{quote_id, opp_id, chain: ["deal_desk", "compliance", "finance"]}` — order strict |
| 7 | `contract.executed` | CLM -> CRM, Billing | `{contract_id, account_id, start_date, end_date, auto_renew: true, notice_days: 60}` |
| 8 | `invoice.created` | Billing -> CRM | `{invoice_id, customer_id, amount_due_usd, due_date}` (Net 30) |
| 9 | `invoice.payment_failed` | Billing -> CRM, deal room | `{invoice_id, days_past_due, dunning_stage: reminder / escalation / suspension_flag}` |
| 10 | `invoice.paid` | Billing -> CRM | `{invoice_id, amount_paid_usd, paid_at}` — clears the billing penalty in the health score |
| 11 | `consent.updated` | Marketing -> all senders | `{contact_id, channel, status: subscribed / unsubscribed, effective_by}` — effective within 24h |
| 12 | `case.sla_breached` | Support -> CRM | `{case_id, account_id, severity, breached_at}` — feeds the support component (25%) of the health score |

## 7. Dedupe Race Handling

Match rules follow 16-data-quality-rules.md: exact email OR fuzzy (company + last name).

- **Simultaneous CRM creations** (manual entry vs. bulk import): bulk imports are quarantined until dedupe passes, so interactive records land first. If two records still collide, the older `created_at` survives as primary; ties break on the lower record ID.
- **Cross-system races** cannot produce billing duplicates because Billing never originates Customers (Section 3); Marketing-created leads enter CRM quarantine and dedupe before promotion.
- After `account.merged` (event 3), consumers re-point invoices, consent records, and cases to the primary within one sync cycle. The merged ID is kept as an alias for 365 days so late-arriving events still resolve.

## 8. Failure and Retry Semantics

- Delivery is **at-least-once**. Consumers dedupe on `event_id` and enforce per-object ordering via `sequence` (drop any event with sequence <= last applied).
- Retry schedule on non-2xx: 1 min, 5 min, 30 min, 2h, 12h (5 retries, ~14.6h total). Exhausted events move to the dead-letter queue.
- DLQ triage SLA: replay or resolve within 4 business hours; events older than 72h require manual reconciliation against the nightly report. Three failed replays mark an event poison and page the integration on-call.
- Consent is exempt from any relaxation: while a `consent.updated` delivery is failing, all outbound sends to that contact are blocked. Suppression is absolute.

## 9. Ownership

Priya Raman (Sales Analyst, RevOps) owns this map, the event schemas, and `#revops-integrations`. Schemas are versioned; producers dual-publish old and new versions for 30 days after any change. KPI definitions computed on top of these flows live in 38-analytics-kpi-definitions.md.
