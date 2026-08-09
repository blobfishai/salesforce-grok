# Regulations & Compliance Regimes (Synthetic)

> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> All regime names are fictionalized for simulation; not legal guidance.

## Applicable regimes in the simulation
- **KYC/AML screening** — every newClient account completes identity and sanctions
  screening before quote approval (07-compliance-review-checklist.md).
- **Cross-border data terms** — APAC/EMEA accounts require regional data-residency
  clauses; the stricter region wins on cross-border deals (15-territory-model.md).
- **Suitability review** — Sovereign Wealth segment mandates a suitability memo
  before any regulated product quote (13-product-catalog.md).
- **Record retention** — approvals, activities, and case resolutions are retained
  7 simulated years; audit logs are append-only (16-data-quality-rules.md).
- **Fair-pricing review** — discounts above tier authority receive a documented
  rationale at Deal Desk (05-cpq-discount-policy.md, 06-deal-desk-charter.md).

## Regulatory escalation workflow
Sales quote flagged regulated -> Compliance pre-screen -> KYC/AML check ->
cross-border terms check -> suitability memo (if Sovereign Wealth) ->
Compliance decision recorded -> Finance notified for exposure review ->
audit log entry appended

Violations open a High-priority case (10-case-management-sla.md) assigned to the
Compliance Officer persona (personas_roles-crm-org.md) and freeze the related
quote until resolved.
