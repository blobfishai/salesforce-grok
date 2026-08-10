# MQL/SQL Handoff SLA (Marketing–Sales)
> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

This SLA governs the handoff between marketing automation and the CRM sales funnel. It
binds marketing, SDRs, and Sales Managers; disputes escalate to the region Sales Manager.

## MQL definition
A lead becomes an MQL the moment its score reaches >= 60 under 02-lead-scoring-policy.md
(segment fit 0-40 + product interest 0-30 with +10 for regulated products + region 0-30).
The MQL timestamp is system-stamped and immutable. Leads scoring >= 80 route to the
senior AE queue; 60-79 to the standard queue; < 60 enter nurture (below). The 2-business-day
first-touch SLA of 01-lead-management-sop.md starts at SAL acceptance, not at MQL stamp.

## SAL gate
The assigned SDR must accept or reject every MQL within 4 business hours. Accept converts
the MQL to a SAL and starts outreach per 01-lead-management-sop.md and
11-activity-logging-standards.md. Reject requires exactly one reason:

| Reason | Disposition |
|---|---|
| bad_fit | Disqualify per 01-lead-management-sop.md (maps to no-fit) |
| no_budget | Recycle to nurture; re-MQL eligible after 90 days |
| competitor | Log competitor (Harborview Capital Systems, Atlas Prime Analytics, or Crestline Financial Cloud); nurture |
| duplicate | Merge per 16-data-quality-rules.md; oldest record survives as primary |
| unresponsive | Return to nurture after sequence exhaustion |

MQLs unactioned at 4 business hours page the Sales Manager; at 8 business hours they
auto-route round-robin to the region team. SAL rejection rates > 30% per SDR per month
trigger a scoring-calibration review with marketing ops.

## Nurture program — 3 tracks by segment
All nurture sequences follow sequencing rules: max 8 steps (email|call|linkedin|task),
max 2 emails/week/contact, sends 08:00-18:00 account-local. Crossing 60 points re-MQLs
the lead and re-opens the SAL gate.

1. **Track A — Institutional Mandates** (Sovereign Wealth, Pension): 6 steps over 90 days;
   Treasury Settlement Suite and Prime Brokerage Onboarding content, regulatory briefings.
2. **Track B — Alternatives & Insurance** (Hedge Fund, PE, Insurance): 8 steps over 60 days;
   FX Liquidity Access Tier-1, Prime Brokerage Onboarding, ESG Analytics Add-on content.
3. **Track C — Private Wealth** (Family Office): 5 steps over 120 days; Wealth Advisory
   Platform and Global Research Portal Seat Pack content.

## Suppression and consent (absolute)
The suppression list is absolute under GDPR and CAN-SPAM: no send, sequence step, or
campaign membership may target a suppressed contact, and no persona may override it.
Unsubscribes (including the unsubscribe reply class) are honored within 24 hours across
all channels and halt active sequences immediately. EMEA contacts require a recorded
lawful basis before any send; purchased or imported lists may not enter sequences without
a verified consent flag. Re-permission requires a documented opt-in event.

## Attribution model
Opportunity credit splits first-touch 40% / multi-touch 40% / last-touch 20%. Qualifying
touches are campaign responses within 180 days before opportunity creation; the
multi-touch 40% divides evenly across all touches between first and last. A single-touch
journey takes 100%. Attribution feeds marketing-sourced pipeline reporting against KPI
targets: MQL->SQL 35%, SQL->opportunity 60%, opportunity->win 25%.

## Campaign-to-CRM sync and dedupe
The marketing platform syncs bidirectionally with the CRM every 4 hours. Campaign member
statuses: Sent -> Responded -> MQL -> SAL -> Recycled. On sync, inbound records dedupe on
exact email OR fuzzy match (company + last name); merges keep the oldest record as primary
per 16-data-quality-rules.md. Bulk imports are quarantined until dedupe passes. Records
with missing or malformed UTM values (32-campaign-catalog.md) land in a quarantine queue
that marketing ops must clear within 2 business days.