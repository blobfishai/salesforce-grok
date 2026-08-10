# Customer Success Health Model
> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

Every active account carries a health score (0-100) recomputed nightly by the Customer
Success Manager (CSM) function — the customer-success specialization of the Service Agent
persona (personas_roles-crm-org.md). The score gates forecasting (12-forecast-methodology.md:
Commit requires account health not Red) and expansion (28-renewal-expansion-runbook.md).

## Weighted inputs and formulas
Composite = 0.40 × Usage + 0.25 × Support + 0.20 × Engagement + 0.15 × Billing, each input
scored 0-100, result rounded to the nearest integer.

- **Usage (40%)** = 0.6 × seat utilization + 0.4 × feature adoption. Seat utilization =
  active users trailing 30 days ÷ licensed seats × 100, capped at 100. Feature adoption =
  licensed modules (13-product-catalog.md) with ≥1 weekly active session ÷ licensed
  modules × 100. Seat utilization >80% is the usage gate for expansion qualification.
- **Support (25%)**: start at 100; deduct 20 per SLA breach in the trailing two quarters
  (10-case-management-sla.md), 15 per open High case, 5 per open Medium case; floor 0.
  Low-priority cases do not deduct.
- **Engagement (20%)**: start at 100; deduct 25 if no logged activity in 30 days
  (11-activity-logging-standards.md); deduct 25 if the last EBR is overdue against the
  tier cadence below; apply the most recent NPS response as +10 (promoter 9-10) or −20
  (detractor 0-6); clamp to 0-100.
- **Billing (15%)**: 100 if current on Net 30 terms; 75 at the +7-day dunning reminder;
  50 at the +21-day escalation; 0 at the +45-day service-suspension flag / Finance review.

Worked example — Meridian Holdings (Gold): seat utilization 68, feature adoption 75 →
Usage 70.8; one open Medium case → Support 95; activity current, EBR on cadence, promoter
→ Engagement 100; invoices current → Billing 100. Composite = 28.32 + 23.75 + 20 + 15 =
87 → Green.

## Bands
Green ≥75, Yellow 40-74, Red <40. Red triggers the churn-risk playbook and CSM escalation
within 2 business days, and blocks both Commit forecasting and expansion.

## Playbooks
- **Churn-risk** (trigger: score drops below 40). 1) CSM opens a High-priority churn case
  within 2 business days (10-case-management-sla.md). 2) CSM completes root-cause within
  5 business days. 3) Sales Manager approves a save plan; uplift relief follows
  28-renewal-expansion-runbook.md. 4) AE logs an executive sponsor call
  (11-activity-logging-standards.md). 5) CSM reviews weekly until the score holds ≥40 for
  two consecutive weeks.
- **Onboarding** (trigger: order activation, 09-order-activation-runbook.md). 1) CSM
  kickoff within 5 business days. 2) Service Agent verifies seat provisioning by day 30.
  3) CSM drives seat utilization to ≥50% by day 60. 4) First EBR within 90 days. 5) CSM
  closes the onboarding case with a resolution note.
- **Expansion** (trigger: Green AND seat utilization >80% for 30 consecutive days). CSM
  flags the account; AE opens a separate expansion opportunity and runs it per
  28-renewal-expansion-runbook.md and 04-opportunity-stage-gates.md.

## EBR cadence by tier
Platinum quarterly, Gold semi-annual, Silver annual (tiers per 03-account-tiering.md).
EBRs run 90 minutes, scheduled round-robin within the region team; max 3 reschedules;
no-show → 2 follow-ups then return to nurture scheduling. CSM prepares the health and
usage readout; AE co-presents commercial items; notes logged per
11-activity-logging-standards.md.

## NPS capture
Survey waves run semi-annually, plus transactional sends 30 days after onboarding closes
and at T-90 of the renewal window (28-renewal-expansion-runbook.md). Max 2 surveys per
contact per year; the suppression list is absolute (GDPR/CAN-SPAM). Detractors get a CSM
callback within 2 business days; promoters are flagged to the AE for the reference
program. The most recent response feeds the Engagement input above.