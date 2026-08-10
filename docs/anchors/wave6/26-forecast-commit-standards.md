# Forecast Commit Standards
> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

Extends 12-forecast-methodology.md. The weighted pipeline (Qualification 10%, Discovery 25%, Proposal 50%, Negotiation 75%, grouped by close-date quarter) remains the analytic baseline; this standard adds the judgment overlay of forecast categories submitted weekly. Opportunities failing data-quality checks (16-data-quality-rules.md) are excluded from every category, and won amounts come from activated orders only (09-order-activation-runbook.md).

## Categories and Entry Rules
Every open opportunity sits in exactly one category:
- **Commit** — the AE will defend it as closing this quarter. Entry rules, all required: stage >= Negotiation with an approval-ready quote (04-opportunity-stage-gates.md, 05-cpq-discount-policy.md); account health not Red (<40); deal health not Red (25-pipeline-inspection-rules.md); close date inside the quarter; no more than one slip this quarter; any required approvals progressing in the strict Deal Desk -> Compliance -> Finance order (06-deal-desk-charter.md, 07-compliance-review-checklist.md, 08-finance-approval-thresholds.md).
- **Best Case** — realistic upside: stage >= Proposal with a generated quote, close date inside the quarter, account health Green or Yellow.
- **Pipeline** — every other open, data-quality-passing opportunity with a close date in the period. No health exclusions.

Example: a $2.4M Treasury Settlement Suite opportunity at Meridian Holdings in Negotiation, account health Yellow, one slip — Commit-eligible. After a second slip it drops to Best Case at most for the rest of the quarter.

## Submission Deadline and Roll-Up Hierarchy
Weekly submission deadline: **Thursday 17:00 region-local**. Roll-up runs AE -> Sales Manager -> region (AMER / EMEA / APAC):
1. AEs submit opportunity-level categories by Thursday 17:00.
2. Sales Managers reconcile against the Monday pipeline review (25-pipeline-inspection-rules.md) and may add a documented manager-judgment adjustment line — they may never silently edit an AE's opportunity categories.
3. Region roll-ups are due Friday 12:00 region-local and feed the quarterly account review in 03-account-tiering.md via 15-territory-model.md.

A missed deadline carries the prior week's numbers forward, flagged as stale in the roll-up.

## Variance-Explanation Requirement
Any week-over-week change greater than 10% in Commit at any roll-up level requires a written explanation attached to the submission: AEs name the specific opportunities; Sales Managers and regions name the top 3 driving deals. The same rule applies retrospectively when quarter-end actuals land more than 10% off final-week Commit — the owning level files the explanation within 5 business days of quarter close. Example: Sales Manager Elena Vasquez's team Commit moving from $6.0M to $4.9M (-18.3%) requires a filed explanation before the Friday 12:00 region roll-up.

## Sandbagging Red Flags
Sales Managers screen weekly for deliberate under-forecasting:
- A deal closing Won directly from Pipeline or Best Case without ever appearing in Commit (more than 1 per AE per quarter).
- An AE finishing above 120% of final-week Commit in 2 consecutive quarters (healthy accuracy band: 90-110%).
- Commit rising more than 25% in the final week of the quarter.
- A Negotiation-stage, non-Red deal held in Pipeline for more than 2 consecutive weeks.
- Close dates habitually set to the first week of the next quarter, then pulled in late.

Confirmed sandbagging is a coaching action recorded per 11-activity-logging-standards.md; a repeat within two quarters escalates to the region Sales Manager review. Accuracy patterns feed pipeline-review agenda item 5 in 25-pipeline-inspection-rules.md.