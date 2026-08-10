# Renewal & Expansion Runbook
> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

Extends 14-renewal-playbook.md. The renewal opportunity is auto-created 120 days before
contract end at Proposal stage with last-signed pricing as baseline
(05-cpq-discount-policy.md). T = contract end date.

## 120-day timeline
- **Week 1 (T-120 to T-114)**: opportunity auto-creates; AE owns it; CSM attaches the
  health snapshot (27-customer-success-health-model.md). If an SLA breach occurred in the
  trailing two quarters (10-case-management-sla.md), the executive sponsor call is logged
  before any quote (14-renewal-playbook.md, 11-activity-logging-standards.md).
- **Week 2 (T-113 to T-107)**: account review — health band, seat utilization, open cases,
  billing/dunning status. Expansion qualification check (below); qualified accounts get a
  separate expansion opportunity.
- **Weeks 3-4 (T-106 to T-93)**: renewal EBR (90 minutes; counts toward the tier cadence
  in 27-customer-success-health-model.md). Transactional NPS send at T-90.
- **Week 5 (T-92 to T-86)**: quote issues at T-90 with the standard 7% uplift. Discount
  authority by tier per 05-cpq-discount-policy.md (Platinum 15% / Gold 10% / Silver 5%);
  incremental renewal discounts above 5% require Deal Desk review
  (14-renewal-playbook.md); TCV > $5M routes to Deal Desk regardless and TCV > $25M adds
  Finance sign-off (08-finance-approval-thresholds.md). Approval order is strictly Deal
  Desk → Compliance → Finance.
- **Weeks 6-8 (T-85 to T-65)**: negotiation. Stale-opportunity rules apply: no activity
  for 21 days → flag; 45 days → Sales Manager review (12-forecast-methodology.md).
  Renewals forecast at Negotiation probability.
- **Week 9 (T-64 to T-58)**: T-60 notice deadline (mechanics below). No written notice by
  T-60 locks the 1-year auto-renewal.
- **Weeks 10-12 (T-57 to T-37)**: contracting. Signature order customer-first, countersign
  by the Sales Manager; more than 2 clause deviations from the library → Compliance
  Officer review (07-compliance-review-checklist.md); envelopes void after 30 days
  unsigned.
- **Weeks 13-16 (T-36 to T-8)**: countersign, booking, Finance Controller reconciliation,
  activation per 09-order-activation-runbook.md. Expansion orders co-term to the renewed
  contract.
- **Week 17 (T-7 to T-0)**: CSM confirms activation and opens the onboarding playbook for
  any newly licensed modules.

## Uplift policy and exceptions
Standard uplift is 7% on last-signed net price. Exceptions: (a) SLA breach in the trailing
two quarters caps uplift at 3%; (b) accounts in the churn playbook (Red, per
27-customer-success-health-model.md) may take 0% uplift with Deal Desk Manager approval;
(c) two-year renewals prepaid annually fix uplift at 4% per year at signature. Any
effective price below the 7%-uplifted baseline counts as incremental discount against tier
authority; above 5% incremental goes to Deal Desk. AEs may not approve their own
discounts.

## Expansion qualification
Qualify when health is Green (≥75) AND seat utilization exceeds 80% of licensed seats for
30 consecutive days. The expansion opportunity is separate from the renewal, works
04-opportunity-stage-gates.md, and prices from 13-product-catalog.md list. Yellow or Red
health blocks the expansion motion; Yellow accounts re-check after two consecutive Green
weeks. Commission: 8% of first-year ACV on expansion, 4% on renewal ACV; deal splits max
2 reps, min 20% each.

## Auto-renew and notice mechanics
Contracts auto-renew for 1 year unless written notice of non-renewal is received 60 days
before contract end. Notice must be written from a named account contact; the AE logs
receipt within 1 business day (11-activity-logging-standards.md) and the Sales Manager is
notified the same day; the churn playbook opens if not already active. When auto-renewal
fires, the order books per 09-order-activation-runbook.md at the approved uplift, invoiced
Net 30 with dunning at +7 / +21 / +45 days.

## Lost-renewal post-mortem
Mandatory within 10 business days of Closed Lost. The Sales Manager chairs; the AE and CSM
attend; the Deal Desk Manager joins when pricing was a factor. The record captures: root
cause (competitor | price | product_gap | service | budget | other) — competitor losses
must name Harborview Capital Systems (HCS), Atlas Prime Analytics, or Crestline Financial
Cloud; the health trajectory over the last two quarters; and missed signals. Findings log
per 11-activity-logging-standards.md; the Sales Analyst folds them into the win-rate KPI
(opportunity→win target 25%). Example: Elena Vasquez (Sales Manager) chaired the Ironwood
Group post-mortem with Zoe Nakamura (AE) and Marcus Webb (CSM) after a loss to Atlas Prime
Analytics; the review flagged a missed Red-band escalation at T-75. Any resulting credit
memo requires the Deal Desk Manager; refunds over $50k require the Finance Controller.