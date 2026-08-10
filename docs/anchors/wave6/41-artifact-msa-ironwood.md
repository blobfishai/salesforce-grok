# 41 — ARTIFACT: Executed MSA Summary Sheet — Ironwood Group

> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

## Document Control

| Field | Value |
|---|---|
| Agreement | Master Services Agreement (MSA) |
| MSA ID | MSA-2026-IWD-003 |
| Provider | Morgan Stanley (SIMULATED) ("Provider") |
| Customer | Ironwood Group ("Customer") |
| Effective date | 2026-03-01 |
| Status | Executed (CLM envelope ENV-2026-0219-114, opened 2026-02-20, completed within the 30-day envelope validity window) |
| Clause deviations from library | 2 (liability-cap carve-outs; SLA credit tiers). At the threshold, not above it — Compliance Officer review NOT triggered (trigger is >2 deviations). |

## Term and Renewal

- **Initial term:** 36 months, 2026-03-01 through 2029-02-28.
- **Auto-renewal:** successive 1-year terms unless either party gives 60-day written notice of non-renewal. Notice deadline for the initial term: **2028-12-30**.
- **Renewal operations:** per 14-renewal-playbook.md, the renewal opportunity auto-creates 120 days before contract end, on **2028-10-31**. Standard renewal uplift is 7% unless Deal Desk approves otherwise per 05-cpq-discount-policy.md and 06-deal-desk-charter.md.

## Key Clauses (summary)

1. **Payment terms — Net 30.** Invoices due 30 days from issue. Late invoices follow the standard dunning cadence: reminder at +7 days, escalation at +21 days, service-suspension flag plus Finance review at +45 days.
2. **Limitation of liability — 12 months of fees.** Each party's aggregate liability is capped at fees paid or payable by Customer in the 12 months preceding the claim. Carve-outs: breach of confidentiality and DPA obligations.
3. **SLA credits — 5/10/20 tiers.** Monthly uptime commitment 99.9% per subscribed service. Credits against that month's fees: 99.00–99.89% uptime -> 5% credit; 98.00–98.99% -> 10% credit; below 98.00% -> 20% credit. Credit claims must be filed within 30 days of the affected month; credits issue as credit memos, which require Deal Desk Manager approval. Chronic failure (three consecutive months below 98.00%) grants a termination right for the affected order form.
4. **Governing law — State of New York**, excluding conflict-of-law rules.
5. **Data Processing Addendum — attached as Exhibit B** and incorporated; suppression and data-subject requests are honored on the terms stated there (unsubscribe requests honored within 24 hours).
6. **Order forms incorporated by reference** (Exhibit C schedule). Each order form inherits these MSA terms unless the order form expressly overrides them; activation follows 09-order-activation-runbook.md. Regulated products on any order form require Compliance review per 07-compliance-review-checklist.md, and Finance sign-off applies only above $25M TCV per 08-finance-approval-thresholds.md.
7. **Support and service.** Cases are handled under the SLA matrix in 10-case-management-sla.md.

## Signature Record (customer-first per CLM policy)

| Order | Signatory | Role | Party | Date signed |
|---|---|---|---|---|
| 1 | Marcus Webb | Chief Operating Officer | Ironwood Group | 2026-02-24 |
| 2 | Elena Vasquez | Sales Manager (countersign) | Morgan Stanley (SIMULATED) | 2026-02-26 |

## Extraction-Ready Fields

| field | value |
|---|---|
| msa_id | MSA-2026-IWD-003 |
| customer | Ironwood Group |
| effective_date | 2026-03-01 |
| initial_term_months | 36 |
| renewal_date | 2029-02-28 |
| auto_renew | true |
| auto_renew_term_months | 12 |
| non_renewal_notice_days | 60 |
| non_renewal_notice_deadline | 2028-12-30 |
| payment_terms | Net30 |
| liability_cap | 12 months fees |
| sla_credit_tiers_pct | 5/10/20 |
| governing_law | New York |
| dpa_attached | true |
| order_forms_incorporated | true |
| clause_deviations | 2 |
| renewal_opportunity_create_date | 2028-10-31 |

Cross-references: 05-cpq-discount-policy.md, 06-deal-desk-charter.md, 07-compliance-review-checklist.md, 08-finance-approval-thresholds.md, 09-order-activation-runbook.md, 10-case-management-sla.md, 13-product-catalog.md, 14-renewal-playbook.md.