# Contract Lifecycle & Clause Library
> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

This policy governs contract documents from draft through executed storage. It applies to all client paper for products in 13-product-catalog.md and inherits the approval order Deal Desk -> Compliance -> Finance from 05-cpq-discount-policy.md and 06-deal-desk-charter.md.

## Document Types
- **MSA** — master terms; prerequisite for any Order Form. One active MSA per account.
- **Order Form** — commercial terms generated from the approved quote (05-cpq-discount-policy.md); TCV, discounts, and term must match the quote exactly or the envelope is invalid.
- **NDA** — mutual, 2-year term; required before any discovery data exchange.
- **DPA** — required whenever client personal data is processed; mandatory for all EMEA accounts (07-compliance-review-checklist.md).
- **SOW** — professional-services scope (e.g., Prime Brokerage Onboarding implementation); always attached to a parent MSA.

## Standard Clause Positions and Fallbacks
| Clause | Standard position | Allowed fallback | Fallback approver |
|---|---|---|---|
| Liability cap | 12 months of fees paid/payable | 18 months, Platinum accounts only (03-account-tiering.md) | Deal Desk Manager |
| SLA credits | 5% of monthly fee for uptime <99.5%; 10% for <99.0%; 20% for <98.0%; capped at 20%/month; claims within 30 days | 30-day claim window extended to 60 days | Deal Desk Manager |
| Renewal | 1-year auto-renew unless 60-day written notice; 7% standard uplift (14-renewal-playbook.md) | Uplift floor 4%, Platinum only | Deal Desk Manager |
| Governing law | State of New York | England & Wales, EMEA accounts only | Compliance Officer |
| Payment terms | Net 30 (24-billing-dunning-policy.md) | Net 45, Platinum only | Finance Controller |

Any position outside the fallback column is a non-standard deviation and always requires Compliance Officer review, regardless of count.

## Redline Escalation Rule
Each edited clause versus the library counts as one deviation. Deviations within fallback need only the listed approver. More than 2 clause deviations from the library on any document routes the entire package to Compliance Officer review (e.g., Elena Vasquez) before signature, in addition to any Deal Desk or Finance approvals already required. Redline turnaround SLA: Deal Desk 2 business days, Compliance 3 business days.

## Signature Order and Envelope Policy
Signature order is customer-first; the countersignature is executed by the Sales Manager. AEs may not countersign their own deals (mirrors the discount rule in 05-cpq-discount-policy.md). One envelope per document package; envelopes void automatically after 30 days unsigned. Re-issuing a voided envelope requires re-validation that all quote approvals are still current; any quote edit in the interim restarts the chain at Deal Desk per 08-finance-approval-thresholds.md.

## Executed-Contract Repository
The countersigned PDF of record is filed within 1 business day of execution, named `{Account}_{DocType}_{YYYY-MM-DD}` (e.g., `Meridian Holdings_MSA_2026-03-14`). Repository access: read-only for AEs and Sales Analysts; write for Deal Desk. Amendments and SOWs link to the parent MSA record. Retention: 7 years after contract termination. No executed contract may live only in email or local storage (16-data-quality-rules.md).

## Contract-Term Extraction Fields
Within 2 business days of filing, Deal Desk extracts: parties, effective date, term end date, auto-renew flag, notice period (60 days), governing law, liability cap multiplier, SLA credit tiers, payment terms, TCV, uplift %, DPA-attached flag, and deviation count. Term end date drives auto-creation of the renewal opportunity 120 days before contract end (14-renewal-playbook.md); TCV feeds tier reviews (03-account-tiering.md); payment terms feed invoicing in 24-billing-dunning-policy.md.