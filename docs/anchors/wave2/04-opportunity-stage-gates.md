# Opportunity Stage Gates
> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

Stages: Qualification -> Discovery -> Proposal -> Negotiation -> Closed Won | Closed Lost.
Gate criteria: Discovery requires a logged Meeting (11-activity-logging-standards.md);
Proposal requires a generated quote (05-cpq-discount-policy.md); Negotiation requires
an approval-ready quote. Closed Won is ONLY reachable by converting a fully approved
quote to an order (09-order-activation-runbook.md) — never by direct stage edit.
Closed Lost requires a reason and a follow-up task dated within 90 days.
