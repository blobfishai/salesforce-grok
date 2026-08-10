# Campaign Catalog (Synthetic, FY2026)
> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

All campaigns below are fictional and exist only inside the sandbox. Every campaign
must carry compliant UTMs (below), sync to the CRM per 31-mql-sql-handoff-sla.md, and
feed exactly one nurture track. Expected MQLs use the >= 60 threshold of
02-lead-scoring-policy.md; conversion is measured against KPI targets (MQL->SQL 35%,
SQL->opportunity 60%, opportunity->win 25%).

## FY2026 campaigns

| # | Campaign | Type | Budget (USD) | Dates (2026) | Target segment / region | Expected MQLs | Nurture track |
|---|---|---|---|---|---|---|---|
| 1 | Sovereign Horizons Webinar Series | Webinar (4-part) | 180,000 | Jan 22 – Apr 16 | Sovereign Wealth / APAC | 90 | Track A |
| 2 | Settlement Forward Roadshow | Field event (5 cities) | 320,000 | Mar 2 – Mar 27 | Pension, Insurance / EMEA | 120 | Track A |
| 3 | Prime Edge Digital | Paid digital + content syndication | 250,000 | Apr 6 – Sep 25 | Hedge Fund / AMER | 200 | Track B |
| 4 | Signal: ESG Launch | Email + gated content | 75,000 | Feb 9 – May 29 | Insurance, PE / all regions | 80 | Track B |
| 5 | Northlight Dinner Series | Executive dinners (6 events) | 140,000 | Sep 10 – Nov 19 | Family Office / AMER | 45 | Track C |
| 6 | Switch to Certainty | ABM displacement | 200,000 | Jun 1 – Oct 30 | Hedge Fund, PE on Harborview Capital Systems or Atlas Prime Analytics; watchlist for Crestline Financial Cloud / all regions | 60 | Track B |

Totals: budget $1,165,000; expected 595 MQLs (blended $1,958/MQL). Owners: Zoe Nakamura
(#1, APAC), Tomas Lindqvist (#2, EMEA), Marcus Webb (#3, #5, AMER), Nina Iyer (#4,
global), Elena Vasquez (#6, global). Priya Raman (marketing ops) owns sync health and
the UTM quarantine queue.

Campaign notes:
- **Sovereign Horizons** promotes Treasury Settlement Suite and Prime Brokerage
  Onboarding; APAC Sovereign Wealth leads score region 30 (not 20) per
  02-lead-scoring-policy.md, so webinar attendees frequently clear 80 and route senior AE.
- **Settlement Forward** is anchored on Treasury Settlement Suite (regulated, +10 product
  interest); event scans sync within 24 hours of each city stop.
- **Prime Edge** targets Prime Brokerage Onboarding and FX Liquidity Access Tier-1
  buyers; syndicated leads are bulk imports and quarantine until dedupe passes
  (16-data-quality-rules.md).
- **Signal: ESG** promotes the ESG Analytics Add-on as an attach motion on renewal
  accounts (14-renewal-playbook.md).
- **Northlight** feeds Wealth Advisory Platform pipeline; dinner invitations respect the
  max-3-reschedule and no-show rules of the scheduling policy.
- **Switch to Certainty** targets named accounts on competitor platforms; competitor must
  be logged on the lead, and any partner-registered account inside the 90-day deal
  registration conflict window is excluded (conflicts resolved by the Sales Manager).

## UTM conventions
Lowercase, hyphen-delimited, no spaces. Required on every tracked link: utm_source,
utm_medium, utm_campaign. Optional: utm_content (asset variant), utm_term.

- utm_source: webinar | event | paid | email | abm | partner
- utm_medium: live | onsite | cpc | syndication | newsletter | direct
- utm_campaign: `fy26-{region}-{segment}-{shortname}` where region is amer|emea|apac|glbl
  and segment is sw|pen|hf|ins|pe|fo. Examples: `fy26-apac-sw-sovereign-horizons`,
  `fy26-emea-pen-settlement-forward`, `fy26-amer-hf-prime-edge`,
  `fy26-glbl-ins-signal-esg`, `fy26-amer-fo-northlight`, `fy26-glbl-hf-switch-certainty`.

Links with missing or malformed UTMs route to the quarantine queue per
31-mql-sql-handoff-sla.md (cleared within 2 business days). Campaigns may not launch
without UTM sign-off from marketing ops, and all sends obey the suppression-list
absolutes and the 08:00-18:00 account-local send window.