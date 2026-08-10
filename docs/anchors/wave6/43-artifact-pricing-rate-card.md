# ARTIFACT: FY2026 Pricing Rate Card
> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

Version 2026.1 — effective 2026-01-01 through 2026-12-31. Owner: Deal Desk
(Priya Raman, Deal Desk Manager). Approved: Priya Raman, Deal Desk Manager;
Tomas Lindqvist, Finance Controller. Reviewed quarterly; changes require Deal
Desk notice per 06-deal-desk-charter.md. List prices are canonical in
13-product-catalog.md; this rate card adds bands, terms, and currency rules.

## FY2026 list prices

| Product | Family | List (USD/yr) | Regulated |
|---|---|---|---|
| Prime Brokerage Onboarding | Institutional Securities | 1,200,000 | yes |
| FX Liquidity Access Tier-1 | Institutional Securities | 850,000 | yes |
| Treasury Settlement Suite | Institutional Securities | 2,400,000 | yes |
| Global Research Portal Seat Pack | Investment Management | 450,000 | no |
| ESG Analytics Add-on | Investment Management | 180,000 | no |
| Wealth Advisory Platform | Wealth Management | 640,000 | no |

## Volume bands

Banded pricing sets the effective list price. Tier discount authority
(05-cpq-discount-policy.md) applies on top of banded list, never on top of
un-banded list.

**Global Research Portal Seat Pack.** Base pack is 25 seats at $450,000/yr
($18,000/seat/yr). Per-seat banding across the whole order:

| Seats | USD/seat/yr | Band |
|---|---|---|
| 1–25 | 18,000 | list |
| 26–100 | 16,200 | 10% band |
| 101–250 | 15,300 | 15% band |
| 251+ | Deal Desk pricing | custom |

**Wealth Advisory Platform.** Annual platform fee banded by assets under
advisement (AUA) notional on the platform, measured at contract signature and
re-measured at each renewal (14-renewal-playbook.md):

| AUA notional | Platform fee (USD/yr) |
|---|---|
| ≤ $2.0B | 640,000 (list) |
| $2.0B–$5.0B | 880,000 |
| $5.0B–$10.0B | 1,150,000 |
| > $10.0B | Deal Desk pricing |

## Multi-year prepay discount — 3%

Contracts of 2+ years with the full term prepaid at signature receive 3% off
TCV. Applied after banded pricing and tier discounts; it is a standard
commercial term and does not consume tier discount authority. Finance
Controller confirms prepay receipt before activation
(09-order-activation-runbook.md). No other prepay percentage may be quoted
without Deal Desk approval.

## Regulated-product compliance surcharge

Each regulated product (Prime Brokerage Onboarding, FX Liquidity Access
Tier-1, Treasury Settlement Suite) carries a $25,000 one-time compliance
onboarding surcharge funding the review in 07-compliance-review-checklist.md.
The surcharge is non-discountable, appears as a separate order-form line, and
is excluded from TCV for the approval thresholds in 05-cpq-discount-policy.md
and 08-finance-approval-thresholds.md.

## Currency handling

All list prices are USD. Quotes may be presented in EUR or GBP converted at
the monthly WM/Refinitiv-style fix (SIMULATED), captured on the first business
day of the month and applied to all quotes issued that calendar month.
Illustrative fixes (SIMULATED): Jan 2026 — 0.9150 EUR/USD, 0.7880 GBP/USD.
If the fix moves more than 2% between quote issuance and countersignature, the
quote must be re-issued at the current fix; unsigned envelopes void after 30
days in any case. Contracts settle in USD unless the Finance Controller
approves local-currency invoicing in writing. Billing terms remain Net 30.

## Discount-authority reminder

| Tier | Qualification | Authority | Beyond authority |
|---|---|---|---|
| Platinum | ≥ $5M trailing TCV or sovereign mandate | 15% | Deal Desk |
| Gold | $1M–$5M trailing TCV | 10% | Deal Desk |
| Silver | < $1M or newly converted | 5% | Deal Desk |

Any quote with TCV > $5,000,000 requires Deal Desk approval regardless of
discount; TCV > $25,000,000 adds Finance sign-off. Approvals execute strictly
Deal Desk -> Compliance -> Finance (06-deal-desk-charter.md,
07-compliance-review-checklist.md, 08-finance-approval-thresholds.md). AEs may
not approve their own discounts. Renewals price from prior-year net with the
standard 7% uplift (14-renewal-playbook.md), not from this rate card.