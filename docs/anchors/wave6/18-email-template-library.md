# Email Template Library
> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

## Merge-field conventions
- Merge fields use double braces with a mandatory pipe fallback:
  {{contact.first_name|there}}, {{contact.title|your team}}, {{account.name|your firm}},
  {{account.region|your region}}, {{meeting.link}}, {{unsubscribe.link}}. Sender fields
  ({{sender.name}}, {{sender.title}}) resolve from the enrolling rep's profile and need
  no fallback; any other unresolved field without a fallback blocks the send.
- Region tokens are AMER, EMEA, APAC; values resolve from CRM records validated by
  16-data-quality-rules.md.
- Subjects <= 60 characters; bodies <= 120 words; cold steps (S1–S4) are plain-text per
  17-outbound-sequencing-playbook.md.
- No list pricing in outbound email; pricing conversations are gated by
  05-cpq-discount-policy.md and 13-product-catalog.md.
- Competitor names (Harborview Capital Systems, Atlas Prime Analytics, Crestline
  Financial Cloud) may appear only in OBJ snippets, never in cold templates.
- Every send appends footer snippet FTR-01. Template IDs follow T-<segment>-<step>;
  steps refer to the standard cadence in 17-outbound-sequencing-playbook.md (email
  steps S1, S4, S6, S8). Segments map per 02-lead-scoring-policy.md (Sovereign Wealth
  40, Pension 35, Hedge Fund 30).
- Client references below (Meridian Holdings, Ironwood Group, Riverside Partners) are
  simulated proof points approved for outbound use.

## Templates

### T-SW-01 — Sovereign Wealth | Treasury Settlement Suite | Step S1
Subject: Settlement consolidation for {{account.name|your fund}}

Hi {{contact.first_name|there}} — sovereign funds running multi-custodian settlement
stacks typically lose basis points to reconciliation breaks. Treasury Settlement Suite
consolidates settlement, netting, and regulatory reporting on one regulated platform;
Meridian Holdings (simulated) cut manual breaks 40% in two quarters. Open to a
30-minute discovery? {{meeting.link}}
{{sender.name}}, {{sender.title}}

### T-SW-04 — Sovereign Wealth | FX Liquidity Access Tier-1 | Step S4
Subject: Tier-1 FX depth in {{account.region|your region}}

{{contact.first_name|Hello}} — following my earlier note: mandates with large currency
overlays gain most from Tier-1 liquidity access — firm pricing at size across 38
currency pairs, with full APAC and EMEA session coverage. If settlement wasn't the
priority, FX execution quality may be. Fifteen minutes to benchmark against your
current providers? {{meeting.link}}
{{sender.name}}, {{sender.title}}

### T-PN-01 — Pension | Global Research Portal Seat Pack | Step S1
Subject: Research coverage for {{account.name|your plan}}'s committee

Hi {{contact.first_name|there}} — pension investment committees tell us external
research is fragmented across a dozen logins. The Global Research Portal Seat Pack
gives your whole committee unified macro, credit, and equity coverage under one
entitlement. Ironwood Group (simulated) consolidated three vendor contracts into it
last year. Worth a 30-minute walkthrough? {{meeting.link}}
{{sender.name}}, {{sender.title}}

### T-PN-06 — Pension | ESG Analytics Add-on | Step S6
Subject: ESG reporting before your next board cycle

{{contact.first_name|Hello}} — many plans face stricter stewardship reporting this
cycle. The ESG Analytics Add-on layers portfolio-level ESG scoring and drift alerts
onto the Research Portal, so trustees see holdings-level exposure without new tooling.
If reporting deadlines are on your desk, I'll show you a sample board pack in 30
minutes. {{meeting.link}}
{{sender.name}}, {{sender.title}}

### T-HF-01 — Hedge Fund | Prime Brokerage Onboarding | Step S1
Subject: Prime onboarding in weeks, not quarters

Hi {{contact.first_name|there}} — launching or adding a prime shouldn't stall your
strategy. Prime Brokerage Onboarding runs legal, credit, and operational setup as one
managed program with a named onboarding lead. Riverside Partners (simulated) went live
in six weeks. If a faster path to prime coverage matters this quarter, grab time here:
{{meeting.link}}
{{sender.name}}, {{sender.title}}

### T-HF-08 — Hedge Fund | Breakup | Step S8
Subject: Closing the file on {{account.name|your firm}}?

{{contact.first_name|Hello}} — I've reached out a few times about prime and FX coverage
without connecting, so I'll close the file for now. If onboarding speed or Tier-1
liquidity becomes a priority, this link always works: {{meeting.link}}. Prefer no
further outreach? Reply "unsubscribe" and we suppress within 24 hours.
{{sender.name}}, {{sender.title}}

## Snippets
- FTR-01 (mandatory footer): "Morgan Stanley (SIMULATED) | 1 Exchange Court, New York,
  NY 10005 (fictional) | Unsubscribe: {{unsubscribe.link}} — honored within 24 hours."
  Sends without FTR-01 are blocked (CAN-SPAM, simulated).
- OBJ-COMP-01 (competitor objection): approved comparison language for Harborview
  Capital Systems (HCS), Atlas Prime Analytics, and Crestline Financial Cloud; leads
  with regulated-platform coverage and single-contract breadth; never disparages. Sets
  the Competitor field per 17-outbound-sequencing-playbook.md.
- OBJ-BUDGET-01 (budget objection): reframes to a phased start on a single product
  family and offers a Sales Analyst-built value model; no discounts may be offered in
  email (05-cpq-discount-policy.md).
- REF-01 (referral thank-you): thanks the referrer and confirms next steps for the
  referred contact; includes FTR-01.
- NOSHOW-01 (no-show follow-up): reschedule link; maximum 2 uses per contact, then the
  lead returns to nurture per 17-outbound-sequencing-playbook.md (max 3 reschedules).

## Governance
New or edited templates require Sales Manager approval; templates referencing regulated
products (Prime Brokerage Onboarding, FX Liquidity Access Tier-1, Treasury Settlement
Suite) also require Compliance Officer sign-off per 07-compliance-review-checklist.md.
A/B variants follow the test policy in 17-outbound-sequencing-playbook.md. Example
senders: Zoe Nakamura (Account Executive, AMER), Priya Raman (Account Executive, EMEA),
Nina Iyer (Account Executive, APAC) — territory alignment per 15-territory-model.md.
