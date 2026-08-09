# Forecast Methodology
> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

Weighted pipeline = sum(open opportunity amount x stage probability): Qualification
10%, Discovery 25%, Proposal 50%, Negotiation 75%. Grouped by close-date quarter.
Won amounts come from activated orders only (09-order-activation-runbook.md).
Forecast excludes opportunities failing data-quality checks (16-data-quality-rules.md).
Territory rollups follow 15-territory-model.md; tier mix feeds the quarterly account
review in 03-account-tiering.md.
