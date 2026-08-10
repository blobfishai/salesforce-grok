# Conversation Intelligence Standards
> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

All external sales calls and video meetings run through the conversation-intelligence platform and are recorded where consent rules permit; cross-border consent follows the stricter region's terms (15-territory-model.md, 07-compliance-review-checklist.md). Recordings, transcripts, and scorecards attach to the call activity logged per 11-activity-logging-standards.md.

## Disposition codes
Every dialed call receives exactly one disposition within 24h: `connected` | `voicemail` | `no_answer` | `wrong_number` | `meeting_set`. `meeting_set` is valid only when a meeting is actually booked under 20-meeting-scheduling-sla.md. `wrong_number` opens a data-quality correction on the contact record (16-data-quality-rules.md). Three consecutive `no_answer`/`voicemail` dispositions on a lead below score 60 route it back to nurture (01-lead-management-sop.md).

## MEDDIC scorecard
Each connected discovery or demo call updates the opportunity's MEDDIC scorecard. Six fields, each scored 0-5 (max 30):

| Field | 0 | 3 | 5 |
|---|---|---|---|
| Metrics | none captured | prospect states a target metric | metric quantified in dollars/basis points and confirmed in writing |
| Economic buyer | unknown | named and title-verified | attended a logged Meeting (11-activity-logging-standards.md) |
| Decision criteria | unknown | criteria documented | criteria confirmed by prospect and mapped to catalog products (13-product-catalog.md) |
| Decision process | unknown | steps and owners mapped | full paper process incl. procurement/compliance steps with dates |
| Identify pain | none | pain articulated by prospect | pain quantified and tied to a specific product gap |
| Champion | none | supportive contact identified | champion has tested access to the economic buyer and sells internally |

An opportunity may not enter Negotiation (04-opportunity-stage-gates.md) with any field at 0. A Commit-category opportunity (12-forecast-methodology.md) scoring below 24 total is flagged for Sales Manager review at the next forecast call; the flag does not change the category, the Sales Manager does.

## Talk ratio
Target rep talk time is <=45% on discovery and demo calls. Two consecutive calls above 60% trigger a mandatory coaching session within 5 business days.

## Tracker keywords
The platform tracks three groups. Competitors: Harborview Capital Systems (HCS), Atlas Prime Analytics, Crestline Financial Cloud — a hit auto-stamps the competitor field on the open opportunity. Pricing: "discount", "list price", "uplift", "price match" — hits above 10% discount discussion route the transcript excerpt to Deal Desk (05-cpq-discount-policy.md, 06-deal-desk-charter.md). Churn: "cancel", "non-renew", "notice", "switching" — a churn hit on an account within 120 days of contract end alerts the renewal owner same day (14-renewal-playbook.md).

## Snippets and retention
Snippets are capped at 5 minutes, internal-only, and never leave the platform via email or file export. Sharing beyond the deal team requires Sales Manager approval; snippets containing pricing terms are restricted to Deal Desk and Finance viewers. Recordings retain for 730 days from call date, then auto-purge; legal hold overrides purge, and GDPR deletion requests are executed by the Compliance Officer within 30 days (07-compliance-review-checklist.md).

## Coaching cadence
Sales Managers score at least 2 recorded calls per rep per week against the MEDDIC rubric; scorecard disputes are settled by the Sales Manager (AEs never approve their own scores, mirroring the discount rule in 05-cpq-discount-policy.md). Each region team holds a monthly calibration session — e.g., Marcus Webb (AMER) and Nina Iyer (EMEA) rotate hosting — and quarterly reviews of talk-ratio and tracker-hit trends feed the territory review in 15-territory-model.md.