# Quota & Compensation Plan
> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

Compensation follows a 50/50 base/variable pay mix at 100% attainment. Variable pay is
commission on credited ACV: 8% on first-year ACV, 4% on renewal ACV (renewals per
14-renewal-playbook.md, standard 7% uplift). Commission accrues only when the order
activates (09-order-activation-runbook.md) — the same basis as won amounts in
12-forecast-methodology.md. Pipeline coverage target is 3x of quota, tracked in the
regional rollups of 15-territory-model.md.

## Quota table (annual, by region and role)
| Role | AMER | EMEA | APAC |
|---|---|---|---|
| Senior Account Executive | $12M | $9M | $7.5M |
| Account Executive | $7.2M | $5.4M | $4.5M |
| Sales Manager | Sum of direct reports' quotas | Sum of direct reports' quotas | Sum of direct reports' quotas |
| Sales Development Rep | 12 accepted leads/month | 12 accepted leads/month | 12 accepted leads/month |

Quota credit and commission credit always move together except during holdover
(30-territory-rules-of-engagement.md).

## Accelerator
Once cumulative annual attainment crosses 100% of quota, a 1.5x accelerator applies to
all further credited ACV: effective rates become 12% first-year and 6% renewal.
Attainment is measured on credited ACV against the annual quota above; no decelerators.

## Deal splits
Maximum 2 reps per opportunity; minimum 20% per rep; splits must total exactly 100% and
be set before the opportunity reaches Proposal (04-opportunity-stage-gates.md). Sales
Manager approval is required; an AE may not approve a split involving themselves.
Example: Marcus Webb 70% / Priya Raman 30% on the Meridian Holdings Treasury Settlement
Suite deal ($2.4M list, 13-product-catalog.md) retires quota and pays commission at
those percentages.

## SPIF policy
SPIFs run quarterly with a maximum pool of $25k per region per quarter. The regional
Sales Manager proposes; the Finance Controller approves before quarter start
(08-finance-approval-thresholds.md governs any exception). SPIFs pay only on orders
activated within the SPIF quarter, do not count toward quota attainment or accelerators,
and no single rep may draw more than 40% ($10k) of a regional pool. Example: a $500
SPIF per competitive-displacement win against Harborview Capital Systems (HCS), Atlas
Prime Analytics, or Crestline Financial Cloud.

## Clawback
If a customer churns within 6 months of order activation — contract terminated, or the
receivable written off after the +45-day dunning stage's service-suspension flag and
Finance review — 100% of the commission paid on the churned ACV is clawed back. SPIF
amounts tied to the churned order claw back in full. Clawbacks deduct from the next
monthly statement; balances that exceed one statement carry forward. The Finance
Controller administers all clawbacks; disputes route Sales Manager first, Finance
Controller final.

## Commission statement fields
Each monthly statement (Xactly-style) carries: rep name and ID; role and region; plan
year and period; annual quota; period and cumulative credited ACV; cumulative attainment
%; accelerator tier in effect; per-deal lines (opportunity ID, account name, product,
ACV type first-year/renewal, split %, credited ACV, rate applied, commission earned);
SPIF payouts; clawbacks; prior-period adjustments; net payout.

## Monthly timeline (business days)
- BD 1-3: Sales Analyst reconciles activated orders against CRM (16-data-quality-rules.md exceptions excluded).
- BD 5: draft statements issued to reps.
- BD 5-10: dispute window; disputes go to the Sales Manager, then the Finance Controller, whose ruling is final.
- BD 12: Finance Controller approves the run.
- BD 15: payout with monthly payroll.

All approvals and disputes are logged as Activities per 11-activity-logging-standards.md.