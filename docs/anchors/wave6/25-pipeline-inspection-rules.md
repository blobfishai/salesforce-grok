# Pipeline Inspection Rules
> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

Applies to every open opportunity governed by 04-opportunity-stage-gates.md. The Sales Analyst publishes a pipeline snapshot every Monday 08:00 region-local; all deltas below are measured against that snapshot.

## Deal-Health Score
Each open opportunity carries a deal-health score (0-100), recomputed nightly and banded like account health: Green >=75, Yellow 40-74, Red <40. Inputs and weights:
- **MEDDIC completeness — 30%.** Scorecard fields populated from logged call outcomes (disposition codes connected|voicemail|no_answer|wrong_number|meeting_set).
- **Activity recency — 25%.** Full credit for a logged activity (11-activity-logging-standards.md) within 7 days; linear decay to zero at 21 days.
- **Stage-gate integrity — 20%.** Gates of 04-opportunity-stage-gates.md satisfied: logged Meeting for Discovery, generated quote for Proposal (05-cpq-discount-policy.md), approval-ready quote for Negotiation.
- **Account health — 15%.** A Red account (score <40; weights usage 40% / support 25% / engagement 20% / billing 15%) caps deal health at Yellow.
- **Close-date stability — 10%.** Full credit at zero slips this quarter; zero credit at 2+ slips.

Red deal health bars the opportunity from Commit (26-forecast-commit-standards.md).

## Stale-Opportunity Ladder
- **Day 21, no logged activity:** system flags stale, AE notified, recency input zeroes.
- **Day 45:** mandatory Sales Manager review. The manager must record a dated next step, push the close date with written justification, or move the deal to Closed Lost (reason plus follow-up task within 90 days per 04-opportunity-stage-gates.md).
- **Day 59 (14 days after review, still no activity):** the opportunity enters the manager's close-out queue and may not appear in Commit or Best Case until the Sales Manager reactivates it.

## Coverage Ratio
Coverage = open pipeline (Qualification through Negotiation, close date in current quarter, passing 16-data-quality-rules.md) / (quarterly quota - closed-won QTD). Won amounts come from activated orders only (09-order-activation-runbook.md). Target: 3.0x. Senior AE quotas (annual / quarterly) and start-of-quarter pipeline floors:
- AMER: $12M / $3.0M — floor $9.0M
- EMEA: $9M / $2.25M — floor $6.75M
- APAC: $7.5M / $1.875M — floor $5.625M

Example: Priya Raman (senior AE, AMER) with $2.1M closed-won QTD has $0.9M remaining quota and needs >=$2.7M open in-quarter pipeline to hold 3.0x. Coverage below 2.0x on two consecutive snapshots triggers a pipeline-generation plan with the SDR team (01-lead-management-sop.md, 02-lead-scoring-policy.md). Territory rollups follow 15-territory-model.md.

## Slipped / Pulled-In / Lost
- **Slipped:** close date moved from inside the current quarter to a later quarter after the Monday snapshot. Two slips in one quarter zero close-date stability and bar the deal from Commit for the remainder of the quarter.
- **Pulled-in:** close date moved from a later quarter into the current quarter. Pulled-in deals >$1M require Sales Manager confirmation that all stage gates are genuinely met before the snapshot counts them.
- **Lost:** stage set to Closed Lost with reason code and 90-day follow-up task (04-opportunity-stage-gates.md). Competitor losses must name Harborview Capital Systems (HCS), Atlas Prime Analytics, or Crestline Financial Cloud.

## Weekly Pipeline Review
Monday 09:30 region-local, chaired by the Sales Manager. Fixed agenda:
1. Coverage vs 3.0x, per AE.
2. Day-21 stale flags and day-45 reviews due this week.
3. Slipped and pulled-in deltas since last snapshot.
4. Red deal-health and Red account-health opportunities (Red account health triggers the churn playbook and CSM escalation within 2 business days).
5. Commit and Best Case scrub ahead of the Thursday 17:00 region-local forecast submission (26-forecast-commit-standards.md).

Required actions: every flagged item leaves the meeting with a named owner and a dated task logged per 11-activity-logging-standards.md. Items unresolved for two consecutive reviews move to the top of the next agenda and are noted in the region roll-up.