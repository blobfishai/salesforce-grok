# Personas & Roles — Simulated CRM Organization

> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

## Personas
- **Account Executive (Sales rep)** — owns leads (01-lead-management-sop.md), opportunities,
  quotes; may not approve own discounts. Works stage gates per 04-opportunity-stage-gates.md.
- **Sales Analyst** — read-mostly persona; builds pipeline and weighted forecast reports
  (12-forecast-methodology.md), territory rollups (15-territory-model.md), and data-quality
  exception lists (16-data-quality-rules.md).
- **Deal Desk Manager** — first approver in the chain (06-deal-desk-charter.md).
- **Compliance Officer** — second approver; runs 07-compliance-review-checklist.md.
- **Finance Controller** — final approver above thresholds (08-finance-approval-thresholds.md);
  also reconciles billing records against activated orders.
- **Service Agent** — owns cases and SLAs (10-case-management-sla.md); opens onboarding
  cases after order activation (09-order-activation-runbook.md).
- **Sales Manager** — reassigns territories, reviews tier changes (03-account-tiering.md),
  and signs off renewal strategy (14-renewal-playbook.md).

## Role-scoped workflow (persona handoff chain)
Account Executive -> Deal Desk Manager -> Compliance Officer -> Finance Controller ->
Account Executive -> Service Agent -> Sales Analyst

Each handoff logs an Activity (11-activity-logging-standards.md) referencing the record
that moved and the persona that acted.
