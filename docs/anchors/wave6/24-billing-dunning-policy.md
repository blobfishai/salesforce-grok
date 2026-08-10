# Billing & Dunning Policy
> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

Billing begins at order activation (09-order-activation-runbook.md). Every activated order creates a subscription; every subscription generates invoices on a fixed schedule. Amounts always derive from the approved quote (05-cpq-discount-policy.md) — billing never re-prices.

## Invoicing Rules
- Terms are Net 30 from invoice date. Net 45 is permitted only as a contract fallback approved by the Finance Controller (23-clm-clause-library.md).
- Subscriptions bill annually in advance on the activation-date anniversary.
- **PO capture:** if the account is flagged PO-required, a valid PO number must be on the subscription before the first invoice issues; invoicing is blocked until captured. Missing-PO blocks older than 5 business days escalate to the Sales Manager.
- **Multi-year prepay discount:** 3% off the prepaid amount when 24+ months are paid at signing. Applied after CPQ/tier discounts and does NOT count against AE discount authority (05-cpq-discount-policy.md).

## Payment Methods
Wire transfer (preferred), ACH direct debit (AMER), SEPA direct debit (EMEA). Corporate card accepted only for invoices <= $50,000. No cash or cheque.

## Dunning Ladder
| Days past due | Action |
|---|---|
| +7 | Automated reminder to billing contact; AE cc'd. |
| +21 | Escalation notice; Sales Manager and Finance notified; account flagged Billing Watch (degrades the billing component of the account health score). |
| +45 | Service-suspension flag set + Finance review; new orders and quotes blocked for the account; renewal processing (14-renewal-playbook.md) frozen until resolved. |

A disputed invoice pauses the dunning clock only if a billing case is opened per 10-case-management-sla.md before the next ladder step. Payment in full clears all flags within 1 business day. Write-offs require Finance Controller approval and end revenue recognition on the affected schedule.

## Refund / Credit Approval Matrix
| Instrument | Amount | Approver |
|---|---|---|
| Refund | <= $50,000 | Finance (standard queue) |
| Refund | > $50,000 | Finance Controller |
| Credit memo | <= $50,000 | Deal Desk Manager |
| Credit memo | > $50,000 | Deal Desk Manager + Finance Controller |

No self-approval: the requesting rep or agent may never approve their own refund or credit (same principle as discount authority in 05-cpq-discount-policy.md). All refunds and credits are logged as activities per 11-activity-logging-standards.md.

## Proration on Mid-Term Upgrades
Mid-term upgrades co-terminate with the existing contract end date. Prorated charge = discounted annual price x remaining days / 365, invoiced immediately at Net 30. The upgrade inherits the contract's existing approved discounts; new or deeper discounts re-enter the approval chain (05-cpq-discount-policy.md). Downgrades are never prorated mid-term — they take effect at renewal. Example: Northgate Associates adds an ESG Analytics Add-on ($180,000 list) with 200 days remaining at a 10% Gold discount: $162,000 x 200/365 = $88,767.12 invoiced on activation of the add-on order.

## Revenue Schedules
On activation (09-order-activation-runbook.md), the subscription is stamped with start date, term, and TCV from the quote. Two schedules generate: (1) the invoice schedule (annual in advance per the rules above) and (2) a straight-line monthly revenue schedule across the term. Invoices link to their subscription and originating order so cash, billing, and recognition reconcile per account. Finance validates rev-rec treatment for any deal with TCV > $25,000,000 or non-standard revenue terms before activation (08-finance-approval-thresholds.md). Suspension flags stop future invoicing but not recognition; only a Finance-Controller-approved write-off stops recognition.