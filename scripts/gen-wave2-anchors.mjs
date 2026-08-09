#!/usr/bin/env node
/**
 * Generate the wave-2 anchor corpus: 16 interlinked seed documents covering distinct
 * angles of the simulated Morgan Stanley CRM domain. Cross-references between docs are
 * deliberate — they give the world generator a denser workflow graph (more hops per
 * task) and satisfy blobfish's grounding gate (>=15 uploaded sources).
 *
 * Output: docs/anchors/wave2/*.md  (all synthetic)
 */
import { writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const OUT = join(ROOT, "docs", "anchors", "wave2");
mkdirSync(OUT, { recursive: true });

const HEADER = `> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.\n`;

const docs = {
  "01-lead-management-sop.md": `# Lead Management SOP
${HEADER}
Lifecycle: New -> Working -> Converted | Disqualified. Only New/Working leads may be
worked. Conversion (see 04-opportunity-stage-gates.md) creates Account + Contact +
Opportunity in one transaction; the account is flagged newClient=true for 12 months.
Leads sourced from events are scored per 02-lead-scoring-policy.md before first touch.
An SLA of 2 business days applies to first outreach on any lead scored >= 60; log the
touch per 11-activity-logging-standards.md. Disqualification requires a reason code
(no-budget, no-fit, competitor, unresponsive) recorded on the lead.`,

  "02-lead-scoring-policy.md": `# Lead Scoring Policy
${HEADER}
Score = segment fit (0-40) + product interest strength (0-30) + region priority (0-30).
Segment fit: Sovereign Wealth 40, Pension 35, Hedge Fund 30, Insurance 25, Private
Equity 25, Family Office 20. Region priority follows 15-territory-model.md. Product
interest maps to the catalog in 13-product-catalog.md; regulated products add +10 but
trigger the Compliance pre-screen in 07-compliance-review-checklist.md at conversion.
Scores >= 80 route to a senior Account Executive; 60-79 standard queue; < 60 nurture.`,

  "03-account-tiering.md": `# Account Tiering Standard
${HEADER}
Tiers: Platinum (>= $5M trailing TCV or sovereign mandate), Gold ($1M-$5M), Silver
(< $1M or newly converted). Tier drives discount authority in 05-cpq-discount-policy.md
and case SLA in 10-case-management-sla.md. Tier reviews run quarterly with inputs from
12-forecast-methodology.md; a two-tier jump requires Deal Desk sign-off per
06-deal-desk-charter.md. newClient accounts stay Silver until first order activates
(09-order-activation-runbook.md).`,

  "04-opportunity-stage-gates.md": `# Opportunity Stage Gates
${HEADER}
Stages: Qualification -> Discovery -> Proposal -> Negotiation -> Closed Won | Closed Lost.
Gate criteria: Discovery requires a logged Meeting (11-activity-logging-standards.md);
Proposal requires a generated quote (05-cpq-discount-policy.md); Negotiation requires
an approval-ready quote. Closed Won is ONLY reachable by converting a fully approved
quote to an order (09-order-activation-runbook.md) — never by direct stage edit.
Closed Lost requires a reason and a follow-up task dated within 90 days.`,

  "05-cpq-discount-policy.md": `# CPQ Discount Policy
${HEADER}
List prices come from 13-product-catalog.md. Discount authority by account tier
(03-account-tiering.md): Platinum up to 15%, Gold 10%, Silver 5% without escalation.
Any discount above authority, or quote TCV > $5,000,000, requires Deal Desk approval
(06-deal-desk-charter.md). New-client or regulated-product quotes add Compliance review
(07-compliance-review-checklist.md). TCV > $25,000,000 adds Finance sign-off
(08-finance-approval-thresholds.md). Approvals execute strictly in the order
Deal Desk -> Compliance -> Finance; any rejection halts the quote.`,

  "06-deal-desk-charter.md": `# Deal Desk Charter
${HEADER}
Deal Desk reviews pricing exceptions: over-authority discounts (05-cpq-discount-policy.md),
TCV > $5M, non-standard payment terms, and two-tier account upgrades (03-account-tiering.md).
Decision SLA: 1 business day. Every decision records actor, timestamp, and a one-line
rationale. Deal Desk may impose conditions (e.g., cap discount at 12%) which the owning
AE must apply before resubmission. Escalations beyond charter go to Finance per
08-finance-approval-thresholds.md.`,

  "07-compliance-review-checklist.md": `# Compliance Review Checklist
${HEADER}
Triggered when account.newClient = true or any quoted product is regulated
(13-product-catalog.md). Checklist: KYC file complete; sanctions screen clear;
cross-border data terms for APAC/EMEA accounts (15-territory-model.md); suitability
memo for Sovereign Wealth segment. Outcomes: Approve, Approve-with-conditions, Reject.
Rejections require remediation notes and block conversion per 04-opportunity-stage-gates.md.
Compliance decisions land after Deal Desk and before Finance (05-cpq-discount-policy.md).`,

  "08-finance-approval-thresholds.md": `# Finance Approval Thresholds
${HEADER}
Finance signs quotes with TCV > $25,000,000, multi-year commitments > 24 months, or
non-standard revenue terms. Finance validates rev-rec treatment and credit exposure
against the account tier (03-account-tiering.md). Finance is always the LAST approval
step (05-cpq-discount-policy.md). Approved-by-Finance quotes are locked: any edit
voids all approvals and restarts the chain at Deal Desk.`,

  "09-order-activation-runbook.md": `# Order Activation Runbook
${HEADER}
Preconditions: quote status Approved (05-cpq-discount-policy.md) and opportunity at
Negotiation (04-opportunity-stage-gates.md). Activation: create order at quote TCV,
stamp activation date, set opportunity Closed Won, then open the onboarding case per
10-case-management-sla.md within 1 business day and log a win Call activity
(11-activity-logging-standards.md). Activation lifts newClient Silver caps at next
tier review (03-account-tiering.md) and feeds the won column of 12-forecast-methodology.md.`,

  "10-case-management-sla.md": `# Case Management SLA
${HEADER}
Priorities: High (respond 4h, resolve 3 business days), Medium (8h / 5 days), Low
(24h / 10 days). Platinum accounts (03-account-tiering.md) get one priority uplift.
Onboarding cases from order activation (09-order-activation-runbook.md) open at High
for regulated products, else Medium. Closure requires a resolution note; reopened
cases keep their original id and escalate one priority level. Breached SLAs appear
in the weekly ops review (16-data-quality-rules.md governs the report's inputs).`,

  "11-activity-logging-standards.md": `# Activity Logging Standards
${HEADER}
Types: Call, Email, Meeting, Task. Every stage gate (04-opportunity-stage-gates.md),
approval decision (06-deal-desk-charter.md), and case touch (10-case-management-sla.md)
must be logged against the correct record id within 24h. Subjects follow
"<Account> — <what happened>". Meetings require notes; win calls after activation
(09-order-activation-runbook.md) summarize final TCV and the approval chain taken.`,

  "12-forecast-methodology.md": `# Forecast Methodology
${HEADER}
Weighted pipeline = sum(open opportunity amount x stage probability): Qualification
10%, Discovery 25%, Proposal 50%, Negotiation 75%. Grouped by close-date quarter.
Won amounts come from activated orders only (09-order-activation-runbook.md).
Forecast excludes opportunities failing data-quality checks (16-data-quality-rules.md).
Territory rollups follow 15-territory-model.md; tier mix feeds the quarterly account
review in 03-account-tiering.md.`,

  "13-product-catalog.md": `# Product Catalog (Synthetic)
${HEADER}
| Product | Family | List (USD/yr) | Regulated |
|---|---|---|---|
| Prime Brokerage Onboarding | Institutional Securities | 1,200,000 | yes |
| FX Liquidity Access Tier-1 | Institutional Securities | 850,000 | yes |
| Treasury Settlement Suite | Institutional Securities | 2,400,000 | yes |
| Global Research Portal Seat Pack | Investment Management | 450,000 | no |
| ESG Analytics Add-on | Investment Management | 180,000 | no |
| Wealth Advisory Platform | Wealth Management | 640,000 | no |
Regulated products trigger 07-compliance-review-checklist.md and score +10 in
02-lead-scoring-policy.md. Pricing changes require Deal Desk notice (06-deal-desk-charter.md).`,

  "14-renewal-playbook.md": `# Renewal Playbook
${HEADER}
Renewal opportunities open 120 days before order anniversary (09-order-activation-runbook.md)
at Proposal stage with last-signed pricing as the baseline (05-cpq-discount-policy.md).
Accounts with an SLA breach in the trailing two quarters (10-case-management-sla.md)
get an executive sponsor call logged per 11-activity-logging-standards.md before any
quote goes out. Renewal discounts above 5% incremental require Deal Desk review.
Renewals count in the weighted forecast at Negotiation probability (12-forecast-methodology.md).`,

  "15-territory-model.md": `# Territory Model
${HEADER}
Regions: AMER, EMEA, APAC. Region priority for scoring (02-lead-scoring-policy.md):
AMER 30, EMEA 25, APAC 20 — except Sovereign Wealth, where APAC scores 30. Cross-border
deals inherit the stricter region's compliance terms (07-compliance-review-checklist.md).
Each region owns a forecast rollup (12-forecast-methodology.md) and a case queue
(10-case-management-sla.md). Territory changes re-run lead routing but never reassign
open opportunities past Proposal (04-opportunity-stage-gates.md).`,

  "16-data-quality-rules.md": `# Data Quality Rules
${HEADER}
Every record carries synthetic=true. Invariants: an order must reference an Approved
quote at conversion time (09-order-activation-runbook.md); Closed Won only via
conversion (04-opportunity-stage-gates.md); one onboarding case per activated order
(10-case-management-sla.md); every approval step has actor + rationale
(06-deal-desk-charter.md); lead conversion yields exactly one account, contact, and
opportunity (01-lead-management-sop.md). Records failing invariants are excluded from
forecasts (12-forecast-methodology.md) and flagged in the weekly ops review.`,
};

let n = 0;
for (const [name, content] of Object.entries(docs)) {
  writeFileSync(join(OUT, name), content.trim() + "\n");
  n++;
}
console.log(`wrote ${n} wave-2 anchor docs to ${OUT}`);
