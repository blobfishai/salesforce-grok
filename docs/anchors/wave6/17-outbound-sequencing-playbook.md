# Outbound Sequencing Playbook
> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

## Scope
Covers all SDR/AE outbound touch sequences on marketing-qualified leads. Enrollment
requires an MQL (score >= 60 per 02-lead-scoring-policy.md) that the SDR has accepted
at the SAL gate within 4 business hours; rejects use reasons bad_fit | no_budget |
competitor | duplicate | unresponsive. Sequences are the primary lever on the
MQL->SQL 35% conversion target (see 12-forecast-methodology.md for downstream funnel
assumptions: SQL->opportunity 60%, opportunity->win 25%).

## Sequence design rules
- Maximum 8 steps. Permitted step types: email | call | linkedin | task.
- Standard cadence (18 business days): S1 email (day 1), S2 call (day 2), S3 linkedin
  (day 4), S4 email (day 7), S5 call (day 9), S6 email (day 12), S7 call (day 15),
  S8 email — breakup (day 18).
- Emails send only 08:00–18:00 account-local; maximum 2 emails per week per contact,
  counting all sequences plus one-off sends.
- Email steps must use approved templates from 18-email-template-library.md; free-text
  cold email is prohibited.
- Calls are logged per 11-activity-logging-standards.md with disposition codes
  connected | voicemail | no_answer | wrong_number | meeting_set. A meeting_set
  disposition books a 30-minute discovery via the regional round-robin
  (15-territory-model.md).
- One active sequence per contact. Cross-region enrollment requires the owning team's
  Sales Manager approval.

## Enrollment / pause / exit
Enroll only when: the contact is not on the suppression list (absolute — GDPR/CAN-SPAM,
simulated); the record passes dedupe per 16-data-quality-rules.md; and the account has
no open opportunity past Discovery (04-opportunity-stage-gates.md) — those contacts
route to the owning AE instead.
Pause on: an OOO reply (auto-resume at stated return date + 1 business day; if no date,
10 business days); a Severity-1 case open on the account (10-case-management-sla.md);
or a deliverability breach (below).
Exit on: any classified reply, meeting_set, hard bounce (flag the record per
16-data-quality-rules.md), unsubscribe, or step 8 completing without reply — the lead
returns to nurture per 01-lead-management-sop.md.

## Reply classification
Every reply is classified within 4 business hours into exactly one of five classes:

| Class | Required next action |
|---|---|
| positive | Exit sequence; respond within 1 business day; book a 30-min discovery via round-robin; convert per 01-lead-management-sop.md. |
| objection | Pause; respond within 1 business day using an approved OBJ snippet (18-email-template-library.md). Competitor objections — Harborview Capital Systems (HCS), Atlas Prime Analytics, Crestline Financial Cloud — set the Competitor field. No traction after 2 exchanges: exit with reject reason competitor or no_budget. |
| OOO | Pause per the rules above; no sends before the resume date. |
| unsubscribe | Honor within 24 hours; add to suppression list; exit; never re-enroll. |
| referral | Thank the sender within 1 business day (snippet REF-01); create the referred contact after dedupe per 16-data-quality-rules.md; enroll the referred contact at S1; exit the original contact. |

## Deliverability & domain warm-up
SPF, DKIM, and DMARC must pass before a domain's first send. New sending domains warm
over 4 weeks: <= 20 emails/day week 1, <= 50 week 2, <= 100 week 3, <= 200 week 4.
Rolling 7-day thresholds: hard-bounce < 2%, spam-complaint < 0.1%. A bounce spike > 5%
in any 24-hour window auto-pauses all sequences on that domain pending Sales Manager
review. Cold steps (S1–S4) are plain-text, maximum 2 links, no attachments.

## A/B test policy
One variable per test (subject line, first sentence, or CTA). Minimum 200 sends per
variant; run to 95% significance or 14 calendar days, whichever comes first. The Sales
Manager approves promoting a winner; the losing variant is retired. Test results are
logged per 11-activity-logging-standards.md.

## Unsubscribe handling
Unsubscribes are honored within 24 hours and the suppression list is absolute: it
overrides every sequence, one-off send, and re-import (bulk imports stay quarantined
until dedupe passes per 16-data-quality-rules.md). A manual send to a suppressed
contact is a compliance violation escalated to the Compliance Officer
(07-compliance-review-checklist.md). Meeting no-shows get 2 follow-ups then return to
nurture; a contact may reschedule at most 3 times.
