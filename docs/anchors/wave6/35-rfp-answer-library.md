# RFP & Security-Questionnaire Answer Library

> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

## Purpose and ownership

This library holds pre-approved answers for recurring RFP and security-questionnaire items so proposals stay fast and consistent. Security and compliance answers are owned by Priya Raman (Compliance Officer). Commercial answers are owned by Marcus Webb (Deal Desk Manager). Nina Iyer (Sales Analyst) administers versioning and the review calendar. Product and pricing facts must match 13-product-catalog.md; never restate them from memory.

## Canned answers (Q1–Q10)

Use verbatim. Each answer carries a version tag (e.g., Q1 v3.1) and an approval date.

1. **Uptime SLA.** Platform availability of 99.9% per calendar month, measured excluding scheduled maintenance announced at least 5 business days in advance. Service credits: 5% of the monthly fee per 0.1% shortfall, capped at 20% of the monthly fee.
2. **Data residency.** Client production data is stored and processed in-region: AMER data in AMER data centers, EMEA in EMEA, APAC in APAC. No cross-region replication of client data; support access follows the data's region.
3. **Encryption at rest.** AES-256 for all client data at rest, with HSM-backed key management and annual key rotation.
4. **Encryption in transit.** TLS 1.2 minimum on all external connections; TLS 1.3 preferred and enabled by default.
5. **SOC 2 Type II (SIMULATED).** A current SOC 2 Type II (SIMULATED) report covering Security and Availability is issued annually and available under NDA.
6. **Sub-processors.** Current list: Beaconline Hosting Services (cloud infrastructure), Lanternwave Communications (transactional email), Kestrel Identity Systems (authentication). Clients receive 30 days advance notice of additions or changes.
7. **Disaster recovery.** RTO 4 hours, RPO 15 minutes. Regional failover is exercised twice per year and results are summarized in the SOC 2 Type II (SIMULATED) report.
8. **Penetration testing.** Annual penetration test by an independent third party; executive summary available under NDA. Critical findings are remediated within 30 days.
9. **Access control.** SAML 2.0 SSO, MFA enforced for all users, role-based access mapped to defined personas, and quarterly access reviews.
10. **Data retention and deletion.** Client data is returned or deleted within 30 days of contract termination, with written certification on request. Exception: call recordings are retained 730 days under 11-activity-logging-standards.md.

## Answer-reuse and approval rules

- **Verbatim reuse is pre-approved.** Any AE or Sales Analyst may insert a current-version answer into a proposal without further sign-off.
- **Any edit is a deviation.** Edited security answers (Q2–Q10) require Compliance Officer approval; edited commercial answers (Q1, pricing language) require Deal Desk Manager approval. Where both apply, approvals run Deal Desk -> Compliance, consistent with the standard order in 06-deal-desk-charter.md and 07-compliance-review-checklist.md.
- **Never overcommit.** Do not offer values stronger than the canned answer (e.g., 99.95% uptime, RTO under 4 hours) without an approved deviation. Approved uplifts must be priced per 05-cpq-discount-policy.md and count toward Deal Desk thresholds.
- **Versioning and expiry.** Answers expire 12 months after approval and are re-certified at the quarterly library review; an expired answer is blocked from new proposals until re-certified.
- **Contract terms embedded in RFPs.** If an RFP requires contract redlines, more than 2 clause deviations from the clause library trigger Compliance Officer review under the CLM policy.
- **Out-of-library questions** (custom security addenda, audit rights, support commitments beyond 10-case-management-sla.md) route to the owning function; the accepted answer is nominated for the library.

## Proposal-generation workflow

1. **Intake.** The AE attaches the RFP to the opportunity (stage per 04-opportunity-stage-gates.md) and logs the submission deadline. Standard turnaround is 10 business days from receipt; anything shorter needs Sales Manager approval.
2. **First-pass mapping.** The Sales Analyst maps questions to library answers within 2 business days, targeting at least 80% coverage, and flags gaps.
3. **Gap drafting.** Subject-matter drafts are due within 3 business days and approved by the owning function before assembly.
4. **Pricing.** List prices come from 13-product-catalog.md; discounts follow tier authority in 03-account-tiering.md and 05-cpq-discount-policy.md. AEs may not approve their own discounts.
5. **Competitive review.** If the shortlist or incumbent includes Harborview Capital Systems (HCS), Atlas Prime Analytics, or Crestline Financial Cloud, the Sales Manager runs a competitive review before release.
6. **Sign-off and archive.** The Sales Manager gives final sign-off; the submitted proposal is archived to the opportunity and the outcome is recorded per 12-forecast-methodology.md.

Example: for the Riverside Partners questionnaire (EMEA, Treasury Settlement Suite), Q1–Q9 were reused verbatim; the client's 45-day deletion demand was logged as a deviation on Q10 and approved by Priya Raman before submission.