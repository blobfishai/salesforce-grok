# Lead Management SOP
> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

Lifecycle: New -> Working -> Converted | Disqualified. Only New/Working leads may be
worked. Conversion (see 04-opportunity-stage-gates.md) creates Account + Contact +
Opportunity in one transaction; the account is flagged newClient=true for 12 months.
Leads sourced from events are scored per 02-lead-scoring-policy.md before first touch.
An SLA of 2 business days applies to first outreach on any lead scored >= 60; log the
touch per 11-activity-logging-standards.md. Disqualification requires a reason code
(no-budget, no-fit, competitor, unresponsive) recorded on the lead.
