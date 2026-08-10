# 42 — ARTIFACT: Order Form — Summit Operations

> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

## Document Control

| Field | Value |
|---|---|
| Order form ID | OF-2026-SUM-041 |
| Order date | 2026-08-01 |
| Customer | Summit Operations |
| Governing agreement | MSA-2025-SUM-014 (order forms incorporated by reference) |
| Currency | USD |
| Account tier at order | Silver (newly converted, per 03-account-tiering.md) |
| AE of record | Aisha Delgado, Account Executive (AMER) — may not approve own discounts per 05-cpq-discount-policy.md |

## Line Items (list prices per 13-product-catalog.md)

| # | Product | Qty | List (USD/yr) | Discount | Net (USD/yr) |
|---|---|---|---|---|---|
| 1 | Treasury Settlement Suite (regulated) | 1 | $2,400,000 | 8% (approved) | $2,208,000 |
| 2 | ESG Analytics Add-on | 1 | $180,000 | 0% | $180,000 |
| | **Total Contract Value (TCV)** | | | | **$2,388,000** |

- **Term:** 12 months, 2026-09-01 through 2027-08-31. Activation per 09-order-activation-runbook.md.
- ACV equals TCV ($2,388,000) on this 12-month order.

## Approval Chain (strict order: Deal Desk -> Compliance -> Finance)

Silver-tier discount authority is 5%; the approved 8% discount on line 1 exceeds AE authority, routing the order to Deal Desk per 05-cpq-discount-policy.md and 06-deal-desk-charter.md. Line 1 is a regulated product, requiring Compliance review per 07-compliance-review-checklist.md. TCV of $2,388,000 is at or below $25M, so Finance sign-off is not required per 08-finance-approval-thresholds.md.

| Stage | Approver | Role | Date | Outcome |
|---|---|---|---|---|
| Deal Desk | Zoe Nakamura | Deal Desk Manager | 2026-07-30 | Approved — 8% discount on Treasury Settlement Suite |
| Compliance | Priya Raman | Compliance Officer | 2026-07-31 | Cleared — regulated-product checklist complete |
| Finance | — | Finance Controller | — | Not required (TCV <= $25M) |

## Billing

- **Payment terms:** Net 30, annual prepay. One invoice for $2,388,000 issued at activation; due 30 days from invoice date.
- **Dunning:** reminder at +7 days past due, escalation at +21 days, service-suspension flag plus Finance review at +45 days.
- Credit memos, if any, require Deal Desk Manager approval; refunds above $50,000 require the Finance Controller.

## Renewal Mechanics (per MSA and 14-renewal-playbook.md)

- Auto-renews for a 1-year term unless 60-day written notice; notice deadline **2027-07-02**.
- Renewal opportunity auto-creates 120 days before term end, on **2027-05-03**.
- Standard 7% uplift sets the renewal baseline at $2,555,160 before any approved concessions.

## Signature Blocks (customer-first per CLM policy; envelope voids after 30 days unsigned)

| Order | Signatory | Role | Party | Date signed |
|---|---|---|---|---|
| 1 | Nina Iyer | Chief Financial Officer | Summit Operations | 2026-08-01 |
| 2 | Tomas Lindqvist | Sales Manager (countersign) | Morgan Stanley (SIMULATED) | 2026-08-03 |

Zero clause deviations from the contract library on this order form; Compliance clause review not triggered (threshold is >2 deviations).

## Extraction-Ready Fields

| field | value |
|---|---|
| order_id | OF-2026-SUM-041 |
| customer | Summit Operations |
| order_date | 2026-08-01 |
| governing_msa | MSA-2025-SUM-014 |
| term_months | 12 |
| term_start | 2026-09-01 |
| term_end | 2027-08-31 |
| tcv_usd | 2388000 |
| line1_product | Treasury Settlement Suite |
| line1_discount_pct | 8 |
| line1_net_usd | 2208000 |
| line2_product | ESG Analytics Add-on |
| line2_discount_pct | 0 |
| line2_net_usd | 180000 |
| payment_terms | Net30 |
| billing_model | annual-prepay |
| deal_desk_approval | 2026-07-30 |
| compliance_approval | 2026-07-31 |
| finance_approval_required | false |
| auto_renew_notice_deadline | 2027-07-02 |

Cross-references: 03-account-tiering.md, 05-cpq-discount-policy.md, 06-deal-desk-charter.md, 07-compliance-review-checklist.md, 08-finance-approval-thresholds.md, 09-order-activation-runbook.md, 13-product-catalog.md, 14-renewal-playbook.md.