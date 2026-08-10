# 40 — ARTIFACT: Renewal-Risk Call Transcript — Meridian Holdings (Wealth Advisory Platform)

> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

## Call Record

| Field | Value |
|---|---|
| Date | 2026-07-28 |
| Account | Meridian Holdings — Silver tier (03-account-tiering.md) |
| Contract | Wealth Advisory Platform, $640,000/yr list (13-product-catalog.md); term ends 2026-11-25; auto-renews 1 year unless written notice by 2026-09-26 |
| Renewal opportunity | Auto-created 2026-07-28, 120 days out, per 14-renewal-playbook.md |
| Participants | Tomas Lindqvist (Customer Success Manager); Rafael Ortiz (Head of Advisory Operations, Meridian Holdings) |
| Disposition | connected |
| Health score | 58 — Yellow, trending down |
| Recording | Retained 730 days; logged per 11-activity-logging-standards.md |

## Transcript

**[00:00] Tomas Lindqvist (CSM):** Rafael, thanks for taking this. Your renewal window opened today — we are 120 days from the November 25 end date — so I want an honest read on where things stand and what we fix before then.

**[00:48] Rafael Ortiz (Head of Advisory Operations, Meridian Holdings):** Honest read: mixed year, Tomas. I will not sugarcoat it.

**[01:15] Tomas Lindqvist:** Let me put my numbers on the table first. Seat utilization is at 55% of licensed seats, down from 78% in Q1. That is the biggest driver of your health score, and it worries me.

**[02:05] Rafael Ortiz:** Two causes. We lost advisors to attrition and did not backfill. And frankly, the two escalations burned confidence — the portfolio-sync latency case and the reporting-export failure. Advisors who hit those went back to spreadsheets.

**[03:10] Tomas Lindqvist:** Both cases are closed — the sync fix shipped in the June release and the export defect was patched under the escalation SLA in 10-case-management-sla.md — but closed tickets do not rebuild trust on their own. I own that gap.

**[04:05] Rafael Ortiz:** Appreciated. I also owe you transparency: procurement has us evaluating Crestline Financial Cloud. They came in with a lower sticker and migration credits, and our ops review in September will see a side-by-side.

**[05:00] Tomas Lindqvist:** Thank you for saying it plainly. What is Crestline actually pitching beyond price?

**[05:30] Rafael Ortiz:** Mostly price. Functionally it is a step down and my team knows it. But price talks when utilization is at 55%.

**[06:20] Tomas Lindqvist:** Then let me be equally plain about the mechanics. The contract auto-renews for one year unless we receive written notice by September 26. The standard renewal carries a 7% uplift — that is $684,800.

**[07:05] Rafael Ortiz:** A 7% increase on a platform half my people are not using is a non-starter. I would need flat — realistically, a reduction — to keep Crestline out of the final round.

**[08:00] Tomas Lindqvist:** Here is what I can and cannot do. I cannot approve pricing myself — that is policy, not preference. Meridian is a Silver-tier account, which caps standing discount authority at 5% under 05-cpq-discount-policy.md; anything past that goes to the Deal Desk under 06-deal-desk-charter.md. What I can build with you is a package inside those rails: right-size the seat count to real usage, look at the uplift, and pair it with an adoption plan that gets utilization back above 75%. Anything beyond 5% I have to sponsor through Deal Desk with your usage data as the justification.

**[09:40] Rafael Ortiz:** I need decision-ready numbers before the September ops review, not a promise of process.

**[10:10] Tomas Lindqvist:** Agreed. Next step: a 90-minute executive business review, week of Monday 10 August, with our Sales Manager Zoe Nakamura in the room — she carries the escalation path to Deal Desk. I bring the utilization remediation plan, post-mortems on both escalated cases, and a renewal structure we can defend. You bring whoever will sit in the Crestline comparison.

**[11:20] Rafael Ortiz:** Book it. If the EBR lands, we go into September with your proposal as the baseline.

**[11:45] Tomas Lindqvist:** You will have the invite today and the pre-read 48 hours before. Thank you, Rafael.

## Risk Notes (CSM post-call)

- Churn signals: utilization 55% of licensed seats (from 78% in Q1); two prior escalated cases; active Crestline Financial Cloud evaluation with September decision point.
- Health 58 (Yellow) and trending down on usage (40% weight) and engagement (20% weight); projected Red before renewal if utilization keeps sliding. Red triggers the churn playbook and CSM escalation within 2 business days.
- Commercial constraint: Silver tier = 5% discount authority; any deeper retention offer requires Deal Desk sponsorship ahead of the 2026-09-26 notice deadline.
- Committed next step: 90-minute EBR week of 2026-08-10 with Sales Manager Zoe Nakamura; renewal forecast held out of Commit per 12-forecast-methodology.md until health recovers.
