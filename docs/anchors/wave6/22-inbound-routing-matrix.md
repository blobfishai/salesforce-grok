# Inbound Routing Matrix
> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

Governs identification, conversion, and routing of all inbound traffic. Enrichment per
21-enrichment-waterfall-config.md must complete before routing (target 10 minutes from
submit); lifecycle and outreach SLAs follow 01-lead-management-sop.md. Matrix owner:
Marcus Webb, Sales Manager, Revenue Operations.

## Visitor identification
Applied in order: (1) form-fill business-email domain exact-matched to an account domain;
(2) reverse-IP firmographic match at confidence >= 0.90 (identifies the account only, never
creates a contact); (3) chat-supplied business email. Free-mail domains never match to
accounts — those leads route on form data alone. If a domain matches 2+ accounts, resolve
with the fuzzy company + last name rule of 16-data-quality-rules.md; ties go to the oldest
account record.

## Web form definitions
| Form | Required fields | Default handling |
|---|---|---|
| Contact Sales | name, business email, company, segment, region | score per 02-lead-scoring-policy.md; route per matrix |
| Demo Request | Contact Sales fields + product interest | route per matrix; on acceptance book 60-min demo |
| Research Portal Trial | name, business email, company | records Global Research Portal Seat Pack interest (13-product-catalog.md) |
| Event / Webinar Registration | name, business email, company | nurture by default; re-score after attendance |
| ESG Whitepaper Download | name, business email | nurture; ESG Analytics Add-on interest recorded |

## Chat-to-lead conversion
A chat converts to a lead when the visitor supplies a business email plus company or
segment; source is set to `chat` and the transcript is logged per
11-activity-logging-standards.md. A meeting request from chat books a 30-minute discovery
via round-robin within the region team. Meeting durations everywhere: discovery 30 min,
demo 60 min, EBR 90 min; no-show -> 2 follow-ups then return to nurture; max 3 reschedules.

## Routing decision table
| Score band | Segment | Region | Routing |
|---|---|---|---|
| >= 80 | any | AMER / EMEA / APAC | senior AE round-robin within region (15-territory-model.md) |
| 60–79 | Sovereign Wealth or Pension | any | regional SDR queue with priority flag |
| 60–79 | all other | any | regional SDR queue |
| < 60 | any | any | nurture |

Score >= 60 is an MQL. **SAL gate**: the assigned SDR or senior AE must accept or reject
within 4 business hours. Reject reasons: `bad_fit | no_budget | competitor | duplicate |
unresponsive`. A `duplicate` reject triggers the merge rule of 16-data-quality-rules.md
(oldest record stays primary). Accepted leads then carry the 2-business-day first-outreach
SLA of 01-lead-management-sop.md.

## Round-robin fallback
Round-robin runs within the region team. If the SAL window lapses without accept/reject,
the lead re-routes to the next rep in the ring and the miss is logged; two consecutive
misses on one lead page the regional Sales Manager, who assigns manually. An empty ring
(coverage gap) routes directly to the regional Sales Manager.

## Named / Platinum escalation
Inbound from a Platinum account (03-account-tiering.md) or the named-account list bypasses
round-robin and routes to the account-owner AE with a 1-business-hour acceptance window;
the regional Sales Manager is notified simultaneously and reassigns on any lapse. Regulated
product interest on these leads follows the Compliance pre-screen of
07-compliance-review-checklist.md at conversion.

## Suppression and KPIs
Suppressed contacts (GDPR/CAN-SPAM) are never routed into sequences; unsubscribes are
honored within 24 hours. Routing performance is reviewed weekly by region against targets:
MQL->SQL 35%, SQL->opportunity 60%.