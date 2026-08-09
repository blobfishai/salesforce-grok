# Data Quality Rules
> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

Every record carries synthetic=true. Invariants: an order must reference an Approved
quote at conversion time (09-order-activation-runbook.md); Closed Won only via
conversion (04-opportunity-stage-gates.md); one onboarding case per activated order
(10-case-management-sla.md); every approval step has actor + rationale
(06-deal-desk-charter.md); lead conversion yields exactly one account, contact, and
opportunity (01-lead-management-sop.md). Records failing invariants are excluded from
forecasts (12-forecast-methodology.md) and flagged in the weekly ops review.
