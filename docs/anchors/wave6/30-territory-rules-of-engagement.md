# Territory Rules of Engagement
> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

This document extends 15-territory-model.md. Regions remain AMER, EMEA, APAC; cross-border
deals inherit the stricter region's compliance terms (07-compliance-review-checklist.md).

## Named accounts vs geo carve
Platinum accounts and sovereign mandates (03-account-tiering.md) sit on named-account
lists assigned to individual senior AEs — maximum 20 named accounts per senior AE,
reviewed quarterly by the regional Sales Manager. All other accounts fall into the geo
carve: ownership follows the account's region per 15-territory-model.md, and inbound
leads route per 01-lead-management-sop.md. A named-account assignment always overrides
the geo carve.

## Ownership-conflict resolution (in order)
1. Named-account list wins over any geo-carve claim.
2. A valid partner deal registration inside its 90-day conflict window wins over a competing geo claim (see Partner interaction below).
3. Otherwise, the rep with the first qualifying logged activity (11-activity-logging-standards.md) within the last 21 days holds the claim; activity older than 21 days establishes no claim, matching the stale-opportunity flag threshold.
4. Conflicts unresolved after 5 business days escalate to the regional Sales Manager, whose decision is final and logged as an Activity. An AE may not rule on a conflict involving their own claim. Example: Nina Iyer and Tomas Lindqvist both claiming Ironwood Group resolves at step 3 on activity recency before reaching step 4.

## Account-transfer protocol on rep departure
- Day 0: open leads return to routing per 01-lead-management-sop.md; the suppression list carries over untouched.
- Within 2 business days: all accounts and open opportunities move to the regional Sales Manager as interim owner.
- Within 10 business days: permanent reassignment. Platinum accounts go only to senior AEs; transferred records pass 16-data-quality-rules.md checks before reassignment completes, and duplicates merge keeping the oldest record as primary.
- Open opportunities keep their stage, close date, and forecast category (12-forecast-methodology.md); no stage regression on transfer. Renewal opportunities auto-created 120 days before contract end (14-renewal-playbook.md) transfer with the account.
- Every handoff logs an Activity naming the outgoing owner, interim owner, and permanent owner.

## Holdover commissions (90 days)
When an account transfers — departure, internal move, or quarterly re-carve — the prior
owner retains full commission credit on any opportunity at Negotiation or later
(04-opportunity-stage-gates.md) as of the transfer date that activates
(09-order-activation-runbook.md) within 90 days. The receiving rep earns quota credit
but no commission during holdover; holdover is not a deal split and does not count
against the 2-rep split limit in 29-quota-comp-plan.md. From day 91, all credit belongs
to the new owner. Holdover payments to departed employees require Finance Controller
approval and remain subject to the 6-month churn clawback in 29-quota-comp-plan.md.

## Partner deal-registration interaction
An approved partner registration is protected for a 90-day conflict window. Inside the
window, the registering partner earns 15% margin on the closed deal; unregistered
partner-sourced deals earn 8%. The direct AE keeps CRM record ownership and full quota
credit in both cases. An active registration blocks competing registrations on the same
opportunity; expired registrations revert to the 8% unregistered margin with no
re-registration grace. Registration against a named Platinum account requires Sales
Manager approval before acceptance. All partner-versus-rep and partner-versus-partner
conflicts are resolved by the Sales Manager, logged per 11-activity-logging-standards.md.