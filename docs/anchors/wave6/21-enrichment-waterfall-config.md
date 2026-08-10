# Enrichment Waterfall Configuration
> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

Every inbound or imported lead is enriched before scoring (02-lead-scoring-policy.md)
and before routing (22-inbound-routing-matrix.md). Target latency: 10 minutes from lead
creation. Bulk imports are quarantined until dedupe passes (16-data-quality-rules.md).
Config owner: Priya Raman, Sales Analyst lead, Revenue Operations.

## ICP definition
- **Segments** (fit values per 02-lead-scoring-policy.md): Sovereign Wealth 40, Pension 35,
  Hedge Fund 30, Insurance 25, Private Equity 25, Family Office 20.
- **AUM bands**: Band A >= $50B; Band B $10B–<$50B; Band C $1B–<$10B; Band D < $1B.
  ICP = Bands A–C in any listed segment. Band D sets `belowICP=true`; it does not alter
  the score, but is a valid `bad_fit` basis at the SAL gate in 22-inbound-routing-matrix.md.
- **Tech signals**: order/execution management system, portfolio accounting platform,
  market-data terminal, collateral management. Detected installs of Harborview Capital
  Systems (HCS), Atlas Prime Analytics, or Crestline Financial Cloud set
  `competitorInstall=true` — used for displacement plays and the `competitor` reject reason.

## Provider waterfall
Three simulated providers are queried in strict order; the first response with field-level
confidence >= 0.85 wins. Lower-confidence values are stored as candidates and never
overwrite an existing value. Providers: **Kestrel Data Labs** (firmographics), **Bluepeak
Signal** (contacts + email verification), **Wrenfield Intent Graph** (technographics + intent).

| Field | Primary | Secondary | Fallback |
|---|---|---|---|
| Company legal name | Kestrel Data Labs | Bluepeak Signal | manual research task |
| AUM band | Kestrel Data Labs | Wrenfield Intent Graph | manual research task |
| Segment | Kestrel Data Labs | — | manual research task |
| Employee count | Kestrel Data Labs | Bluepeak Signal | leave blank |
| Contact title / phone | Bluepeak Signal | Kestrel Data Labs | leave blank |
| Email + verification status | Bluepeak Signal (sole authority) | — | — |
| Tech signals / competitor installs | Wrenfield Intent Graph | Kestrel Data Labs | leave blank |
| Intent topics + surge score | Wrenfield Intent Graph (sole authority) | — | — |

If segment or AUM band remains unresolved after the waterfall, a manual research task is
assigned to a Sales Analyst with a 2-business-day SLA; the lead may not be scored until
segment is set.

## Email verification
Statuses: `valid | accept_all | risky | invalid | unknown`.
- **valid**: sequence-eligible under the standard cap of 2 emails/week/contact.
- **accept_all**: sequence-eligible, capped at 1 email/week/contact.
- **risky**: excluded from email steps; call and LinkedIn steps only; re-verify after 30 days.
- **invalid**: email field cleared and flagged per 16-data-quality-rules.md; the lead cannot
  pass the MQL gate until a `valid`/`accept_all` email or a verified phone exists.
- **unknown**: re-verify within 24 hours, max 3 attempts, then treat as `risky`.

The suppression list is absolute (GDPR/CAN-SPAM): suppressed addresses are never enriched
into sequences, and unsubscribes are honored within 24 hours.

## Intent signals
Topics map 1:1 to the families in 13-product-catalog.md: prime brokerage onboarding, FX
liquidity, treasury settlement, research platforms, ESG analytics, wealth advisory
platforms. Wrenfield computes a surge score 0–100 per account-topic weekly. Feeding the
product-interest component of 02-lead-scoring-policy.md: a declared interest in a catalog
product sets a baseline of 15; surge >= 85 adds +10; surge 60–84 adds +5; surge < 60 adds
nothing. The regulated +10 of 02-lead-scoring-policy.md applies after intent adjustments,
and the component is capped at 30. Surge >= 85 on a regulated topic pre-stages the
Compliance pre-screen of 07-compliance-review-checklist.md for use at conversion.

## Hygiene and refresh
Before any write, duplicates are matched on exact email OR fuzzy (company + last name);
merges keep the oldest record as primary (16-data-quality-rules.md). Accounts re-enrich
every 90 days, contacts every 180 days, intent weekly. Every record carries
`synthetic=true`.