# 39 — ARTIFACT: Discovery Call Transcript — Summit Operations (Treasury Settlement Suite)

> SIMULATION ONLY — synthetic corpus for the "Morgan Stanley (SIMULATED)" sandbox.
> Not affiliated with or representative of Morgan Stanley.

## Call Record

| Field | Value |
|---|---|
| Date / duration | 2026-07-14, 30-minute discovery (per scheduling standard) |
| Opportunity | Summit Operations — Treasury Settlement Suite, list $2,400,000/yr, regulated (13-product-catalog.md) |
| Participants | Priya Raman (Account Executive); Marcus Webb (CFO, Summit Operations); Elena Vasquez (Director of Operations, Summit Operations) |
| Disposition | connected |
| Talk ratio (AE) | 43% (target ≤45%) |
| Recording | Retained 730 days; activity logged per 11-activity-logging-standards.md |

## Transcript

**[00:00] Priya Raman (AE):** Marcus, Elena — thanks for the time. I have us for thirty minutes. My goal is to understand your settlement operation, what fixing it is worth, and how you would evaluate a fix. If it makes sense at the end, we agree concrete next steps. Fair?

**[00:41] Marcus Webb (CFO, Summit Operations):** Fair. Framing from my side: Elena's team surfaced this, but the spend decision sits with me. Anything at this size comes out of my budget and goes past our board.

**[01:20] Elena Vasquez (Director of Operations, Summit Operations):** Context first. Since the T+1 migration our fail rate on affirmed trades roughly tripled. We catch breaks after cutoff, not before, and my team runs manual repair every morning across three custodians.

**[02:28] Priya Raman (AE):** When you say fails — have you sized the annual impact in dollars?

**[03:02] Marcus Webb:** We have. Finance closed the number last quarter: eighteen million dollars a year, all-in — buy-ins, penalty interest, claims, plus the remediation headcount Elena carries. That is the number I take to the board.

**[03:44] Priya Raman (AE):** $18M annually. How does it split?

**[04:05] Elena Vasquez:** Roughly 60% penalty interest and buy-in cost, 40% people — twelve FTEs doing manual matching and repair that should not exist.

**[05:10] Priya Raman (AE):** What are you running today, and who else are you looking at?

**[05:38] Elena Vasquez:** In-house reconciliation plus a legacy matching tool. We took a first meeting with Harborview Capital Systems in June.

**[06:20] Marcus Webb:** HCS showed strong dashboards. Thin on exception automation, in my read — a lot of visibility, not much prevention.

**[07:05] Priya Raman (AE):** That distinction matters. Treasury Settlement Suite is built around a pre-settlement exception engine — it predicts likely fails before cutoff and routes them for repair, rather than reporting them after. Happy to prove that in a demo against your own fail patterns. Elena, what would you need to see?

**[08:30] Elena Vasquez:** Predicted-fail queue on a T+1 timeline, custodian and SWIFT connectivity, and how repairs get audited. If it kills the morning break report, my team will champion it internally — I already am.

**[09:40] Marcus Webb:** Before we go further: two things are non-negotiable in our evaluation. A contractual 99.9% uptime SLA — settlement infrastructure cannot be best-effort. And EMEA data residency; our regulator requires client settlement data hosted in the EU.

**[10:45] Priya Raman (AE):** Understood — 99.9% SLA and EMEA residency as hard decision criteria. Both are supportable; I will put the SLA schedule and the residency architecture in writing with the security package rather than hand-wave it here.

**[11:50] Marcus Webb:** Good. And what does this cost? Give me a number.

**[12:20] Priya Raman (AE):** I will get you a real number, but I would be doing you a disservice quoting one before we scope custodian count, volumes, and integration depth — a generic figure would be wrong in both directions. Let us run the demo and security review, then I bring a scoped proposal with exact commercials. You will have it before your board needs it.

**[13:30] Marcus Webb:** Fine — but I want the proposal well before Q4. Process on our side: Sofia Andersson's information-security team reviews first; nothing gets commercial until she clears it. Then it goes to the board in Q4 with my recommendation. I own the budget sign-off.

**[14:50] Priya Raman (AE):** Clear. So: security review, then board in Q4, with you as the economic decision-maker. On integrations, Elena — which custodians and what message flows?

**[15:35] Elena Vasquez:** Three custodians, MT535/MT548 inbound today, and we want ISO 20022 on the roadmap. Exception volumes peak Mondays.

**[16:40] Priya Raman (AE):** All standard for the Suite. Proposed next steps: I send your security questionnaire to Sofia's team by Friday the 17th, and we schedule a working demo — not a slideware demo — week of Monday 27 July, with the three of you: Marcus, Elena, and Sofia.

**[17:55] Marcus Webb:** Agreed. Send the questionnaire to Sofia directly, copy me. Demo that week works; Elena coordinates calendars.

**[18:40] Elena Vasquez:** I will send three slots by tomorrow.

**[19:20] Priya Raman (AE):** Recapping commitments: $18M annual settlement-failure cost is the business case; hard criteria are the 99.9% SLA and EMEA data residency; process is IT security review then Q4 board; security questionnaire out by 17 July; demo week of 27 July with all three stakeholders. Anything I missed?

**[20:10] Marcus Webb:** No. Move fast and this stays ahead of Harborview.

**[20:30] Priya Raman (AE):** Understood. Thank you both — you will have the questionnaire before end of week.

## MEDDIC Extraction (scorecard)

- **Metric:** $18M annual settlement-failure cost (60% penalties/buy-ins, 40% manual remediation, 12 FTEs).
- **Economic buyer:** Marcus Webb, CFO — owns budget sign-off.
- **Decision criteria:** contractual 99.9% uptime SLA; EMEA data residency.
- **Decision process:** IT security review (Sofia Andersson) → board approval in Q4.
- **Identify pain:** T+1 settlement failures; fail rate ~3x since migration.
- **Champion:** Elena Vasquez, Director of Operations.
- **Competition:** Harborview Capital Systems (HCS) — met June; positioned as visibility-only per battlecard; pricing question deflected pending scoping.
- **Next step:** security questionnaire by 2026-07-17; 60-minute demo week of 2026-07-27 with Webb, Vasquez, Andersson. Stage-gate evidence per 04-opportunity-stage-gates.md.
