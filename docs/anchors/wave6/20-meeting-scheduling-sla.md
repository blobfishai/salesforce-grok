# Meeting Scheduling SLA
> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

Scheduling runs through the routing platform; every booked meeting creates a Meeting activity per 11-activity-logging-standards.md and, once held, satisfies the Discovery gate in 04-opportunity-stage-gates.md.

## Meeting types and durations

| Type | Duration | Default attendees |
|---|---|---|
| Discovery | 30 min | booking rep + prospect |
| Demo | 60 min | AE + Sales Analyst |
| Executive Business Review (EBR) | 90 min | AE + Sales Manager |

Meetings book only inside the 08:00-18:00 account-local window, with a 15-minute minimum buffer between a rep's meetings. Demos require an open opportunity at Discovery or later; EBRs are reserved for Gold and Platinum accounts (03-account-tiering.md).

## Round-robin assignment
Inbound and SDR-booked meetings assign round-robin within the owning region team (AMER, EMEA, APAC per 15-territory-model.md), least-recently-assigned first. Reps who are OOO, over 6 booked meetings that day, or ineligible for the segment are skipped without losing queue position. Leads scored >=80 (02-lead-scoring-policy.md) bypass round-robin and route directly to the senior AE pool; Sovereign Wealth APAC leads always qualify. A meeting booked from an MQL (score >=60) counts as the SDR's SAL action and must be accepted or rejected within 4 business hours (01-lead-management-sop.md governs rejection reason codes).

## Booking-link policy
Personal links may be sent only to contacts on records the rep owns; shared team links serve inbound routing. Links expire after 30 days. No booking link may be sent to a suppressed contact — the suppression list is absolute — and scheduling emails count toward the 2-emails-per-week-per-contact cap. Every confirmation and reminder includes a reschedule link; reminders send at 24h and 1h before start.

## No-shows and reschedules
Mark no-shows within 24h. A no-show gets exactly 2 follow-ups (day +1 and day +3); if neither rebooks, the lead returns to nurture per 01-lead-management-sop.md and the related call disposition may not remain `meeting_set` (19-conversation-intelligence-standards.md). A meeting rescheduled more than 3 times is treated as a no-show and enters the same path. No-show and reschedule counts feed the MQL->SQL 35% conversion dashboard reviewed monthly.

## Pre-meeting brief
The booking rep attaches a brief to the calendar invite no later than 2 business hours before start. Required contents: account tier (03-account-tiering.md), lead score (02-lead-scoring-policy.md), open opportunities with stage (04-opportunity-stage-gates.md), open cases (10-case-management-sla.md), account health color, last 3 logged activities (11-activity-logging-standards.md), and any competitor-tracker hits from 19-conversation-intelligence-standards.md. Demo briefs additionally state quote status under 05-cpq-discount-policy.md. A meeting without a brief still runs, but the miss is logged and counts against the rep in the monthly scheduling-quality review.

## Handoff to AE
When an SDR books discovery, the AE is assigned by the same round-robin at booking time and must accept the handoff within 4 business hours; unaccepted meetings return to the round-robin pool and the Sales Manager is notified. A valid handoff requires an accepted SAL, the attached brief, and a logged Task naming both reps — e.g., "Ironwood Group — discovery handoff, Priya Raman -> Tomas Lindqvist". The SDR stays on the first meeting invite, then ownership is fully the AE's; subsequent conversion is measured against the SQL->opportunity 60% target.