# Analytics & KPI Definitions

> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

## 1. Scope

Canonical formulas for funnel conversion, cycle time, win rate, and revenue metrics. Any dashboard computing these differently is wrong. Underlying data flows and system-of-record rules are governed by 37-revops-integration-map.md.

## 2. Funnel Conversion Rates

Funnel metrics are cohort-based on the month the entering record was created. Contacts suppressed for consent are removed from numerator and denominator.

- **MQL -> SQL — target 35%.** MQL = lead reaching score >= 60 (02-lead-scoring-policy.md). SQL = MQL accepted by the SDR at the SAL gate (accept/reject within 4 business hours; reject reasons bad_fit, no_budget, competitor, duplicate, unresponsive per 01-lead-management-sop.md). Formula: `SQLs from cohort / MQLs created in cohort month`, measured at 30 days. Rejected and expired MQLs remain in the denominator.
- **SQL -> Opportunity — target 60%.** Formula: `opportunities created and linked to the SQL within 60 days / SQLs in cohort`. An opportunity counts once even when multiple contacts converted.
- **Opportunity -> Win — target 25%.** Computed under the win-rate rules in Section 4 (close-date basis, disqualified excluded).
- **Funnel yield** (compound check): 0.35 x 0.60 x 0.25 = 5.25% MQL-to-win. Report it; deviations localize which stage broke.

## 3. Cycle-Time Definitions

Cycle time = calendar days from opportunity created date to close date (won or lost). Report the **median**, never the mean — sovereign mandates distort means. Segment targets:

| Segment | Target median (days) |
|---|---|
| Sovereign Wealth | 180 |
| Pension | 150 |
| Insurance | 120 |
| Private Equity | 105 |
| Hedge Fund | 90 |
| Family Office | 75 |

Add 30 days to the target when any regulated product is on the quote (07-compliance-review-checklist.md). Stage-age hygiene stays per 12-forecast-methodology.md: no activity for 21 days -> flag; 45 days -> Sales Manager review.

## 4. Win-Rate Calculation Rules

- Population: opportunities with a close date inside the reporting period.
- Formula: `Closed Won / (Closed Won + Closed Lost)`.
- **Excluded from numerator and denominator**: close reason `disqualified` (sub-reasons bad_fit, duplicate, data_error, test_record). Disqualification is pipeline hygiene, not a selling outcome.
- Competitive losses must be tagged with the competitor: Harborview Capital Systems (HCS), Atlas Prime Analytics, or Crestline Financial Cloud. Untagged competitor losses fail the checks in 16-data-quality-rules.md.
- Count-based win rate is canonical (target 25%); TCV-weighted win rate is reported alongside but never substituted.

## 5. Revenue Metric Definitions

- **MRR** = sum of active Subscription annualized value / 12, as of month end. Only recurring subscription fees for products in 13-product-catalog.md count; one-time credits and refunds are excluded.
- **ARR** = MRR x 12.
- **GRR** (12-month) = `(cohort ARR 12 months ago - churn - downgrades) / cohort ARR 12 months ago`. Expansion excluded; capped at 100%. Target >= 92%.
- **NRR** (12-month) = `current ARR of the cohort active 12 months ago (including expansion and the 7% standard renewal uplift) / cohort ARR 12 months ago`. Target >= 108%.
- Cohort = accounts holding at least one active Subscription at the anchor date. Accounts merged during the window roll into the surviving primary per 37-revops-integration-map.md Section 7.

## 6. Standard Report Catalog

| # | Report | Owner | Refresh | Notes |
|---|---|---|---|---|
| 1 | Pipeline Coverage by Region | Elena Vasquez (Sales Manager) | Daily 06:00 local | Open pipeline / remaining quota; target 3x. Senior AE quotas: AMER $12M, EMEA $9M, APAC $7.5M (15-territory-model.md) |
| 2 | Forecast Snapshot | Sales Manager | Weekly, Mon 08:00 ET | Commit / Best Case / Pipeline; Commit requires stage >= Negotiation and account health not Red (12-forecast-methodology.md) |
| 3 | Funnel Conversion Dashboard | Priya Raman (Sales Analyst) | Weekly, Mon 09:00 ET | Section 2 metrics vs 35% / 60% / 25% targets |
| 4 | Stale Opportunity Report | Sales Analyst | Daily 07:00 ET | 21-day flags and 45-day Sales Manager review queue |
| 5 | Discount & Approval Audit | Zoe Nakamura (Deal Desk Manager) | Weekly, Fri 16:00 ET | Tier authority 15% / 10% / 5%; chain strictly Deal Desk -> Compliance -> Finance (05-cpq-discount-policy.md, 06-deal-desk-charter.md) |
| 6 | Renewal & NRR Outlook | Sales Analyst | Weekly, Wed 09:00 ET | 120-day renewal window, 7% uplift assumption (14-renewal-playbook.md) |
| 7 | AR Aging & Dunning | Marcus Webb (Finance Controller) | Daily 07:30 ET | Net 30; +7 / +21 / +45 stages; suspension flags routed to Finance review (08-finance-approval-thresholds.md) |
| 8 | Account Health & Churn Risk | Tomas Lindqvist (Service Agent, CS lead) | Daily 08:00 ET | Green >= 75 / Yellow 40-74 / Red < 40; Red triggers churn playbook + CSM escalation within 2 business days |

## 7. Board-Pack Metrics

Produced quarterly by the Sales Analyst, signed off by the Finance Controller:

- ARR and net-new ARR; NRR vs 108% and GRR vs 92%
- Count-based win rate vs 25%; competitive win rate vs HCS, Atlas Prime Analytics, Crestline Financial Cloud
- Pipeline coverage vs 3x; quota attainment by region ($12M / $9M / $7.5M)
- Forecast accuracy = actual closed-won TCV / final-week Commit; target 95-105%
- Funnel conversions vs 35% / 60% / 25%; funnel yield vs 5.25%
- Median cycle time by segment vs Section 3 targets
- Health distribution (% Green / Yellow / Red); renewal rate and uplift realized vs the 7% standard

## 8. Governance

Metric definitions live here and only here. Changes require RevOps review and a versioned entry; dashboards must cite this document's section numbers. Data lineage, dedupe, and merge behavior: 37-revops-integration-map.md and 16-data-quality-rules.md.
