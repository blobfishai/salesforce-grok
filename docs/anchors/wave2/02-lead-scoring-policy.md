# Lead Scoring Policy
> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

Score = segment fit (0-40) + product interest strength (0-30) + region priority (0-30).
Segment fit: Sovereign Wealth 40, Pension 35, Hedge Fund 30, Insurance 25, Private
Equity 25, Family Office 20. Region priority follows 15-territory-model.md. Product
interest maps to the catalog in 13-product-catalog.md; regulated products add +10 but
trigger the Compliance pre-screen in 07-compliance-review-checklist.md at conversion.
Scores >= 80 route to a senior Account Executive; 60-79 standard queue; < 60 nurture.
