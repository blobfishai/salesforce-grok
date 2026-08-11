# Stakeholders — who acts, what they touch, and what "done" means

> Answers QUESTIONS.md **B1–B6** (definitions of done are inline here rather than
> in a separate file). Sources: `research/SOURCES.md` §5 (roles, deal desk) and
> the 185 practitioner skills in `research/answers/_data/workflow-skills.tsv`.
> Compiled 2026-08-11.

## The roster

| Role | Owns | Daily loop (what they do 20× a day) | Systems touched |
|---|---|---|---|
| **SDR/BDR** | qualified meetings booked | qualify overnight inbound; 2–3 h outbound across LinkedIn/email/phone over a 100–150-account ICP list; log activity; hand off | engagement tool, enrichment, CRM, calendar, LinkedIn |
| **AE** | revenue quota, pipeline 4–6× quarterly target | discovery calls & demos; manage 20–40 active opps; push proposals; self-source; forecast call | CRM, CI (Gong), quoting/CPQ, e-sign, email, Slack |
| **Sales Engineer** | technical win | demo builds, security questionnaires, RFP answers | knowledge base, RFP library, CRM |
| **Sales Manager** | team forecast | pipeline inspection, deal reviews, commit calls | CRM dashboards, forecast tool, sheets |
| **Deal Desk** | non-standard deals | intake → review → **counter-structure** → decide within SLA → document exception on the opp | CPQ, CRM, approval workflow |
| **Finance / Rev Rec** | margin, revenue recognition | approve margin & payment-term thresholds; invoice; reconcile | ERP/GL, billing, CRM |
| **Legal / CLM** | contract risk | clause deviations, redlines, countersign order | CLM, e-sign |
| **RevOps** | *truth across the stack* | routing rules, data hygiene, reporting, tool admin, handoff SLAs | everything; SQL; sheets |
| **Marketing Ops** | lead flow | scoring, lists, suppression, campaign attribution | marketing automation, CRM |
| **AM / CSM** | retention & expansion | health checks, renewals, expansion plays | CRM, CS platform, billing |
| **Partner Manager** | sourced/influenced pipeline | deal registration, conflict resolution | PRM, CRM |

Grounding notes: the SDR/AE daily-loop shape (overnight inbound first, then
outbound blocks, then CRM hygiene) and the 4–6× coverage norm come from the
syncgtm / salesscreen / gangly role guides; RevOps is described as necessary
precisely *"when definitions and data drift between teams"* — i.e. RevOps exists
because of §E chaos.

## Deal Desk in detail (the best-documented workflow)

Source: b2bprocess.com/deal-desk (fetched 2026-08-11).

**Workflow (8 steps):** define standard pricing/terms so "non-standard" has
meaning → set an approval matrix mapping deviation → approver + SLA → intake
through a single channel (CPQ or structured form) → review economics/risk/precedent
→ **counter-structure rather than approve/deny** → decide within SLA → document
every exception on the opportunity → analyze quarterly to shrink exception surface.

**Triggers:** non-standard discounts, custom payment schedules, atypical contract
language, unusual product bundles, ramped pricing, strategic exceptions.

**Approvers by concern:** Deal Desk (intake/review/documentation) · Finance
(margin, payment terms, rev rec) · Legal (clause deviations) · Sales leadership
(top-tier strategic exceptions) · Product/Delivery (promised functionality).

**SLAs & targets:** standard same/next business day; complex multi-approver 2–3
business days; **first-pass approval rate >70%**; quarter-end turnaround
**≤1.5×** mid-quarter baseline; exception rate declining over time.

**Why this is a great task family:** it has an explicit rule matrix (gradeable),
an explicit SLA clock (time semantics), a documented "counter-structure" behavior
(not binary), and a required artifact (exception documented on the opportunity) —
so a task can fail for reaching the right decision the wrong way, or for reaching
it without recording it.

## Definition of done, by task shape (B3, B6)

| Shape | Done means | Verifier style |
|---|---|---|
| **State mutation** (advance stage, reassign owner, merge dupes) | target rows changed to the specified values **and** the collateral set unchanged | state delta + collateral guard |
| **Bulk hygiene** | exactly the pinned target subset changed; audit artifact produced where the SOP requires one | pinned-subset delta + `no_offtask_table_changes` |
| **Analytics answer** | number within tolerance **plus** stated definition, window, and sources; conflicts disclosed | answer match + transcript assertions (see `data-chaos-catalog.md` §3) |
| **Approval / policy judgment** | correct decision, correct approver sequence, exception documented on the record | ordered-event assertions |
| **Communication / drafting** | artifact exists, addressed to the right party, contains required disclosures, omits forbidden claims | LLM-judge rubric (ai_sales_eval_arena pattern) + forbidden-claim check |
| **Restraint** | **no writes**, plus an explicit statement of why and what is needed to proceed | negative state assertion + transcript assertion |
| **Multi-system reconciliation** | the authoritative copy is named, the discrepancy is quantified, and the fix (or the escalation) matches policy | checkpoint scoring |

Two verification principles imported from R2A-Sales
(`eval/qinyh10300__R2A-Sales-Benchmark/docs/TOOL_SANDBOX.md`):

1. **Saying is not doing.** *"A customer-visible sentence such as 'I sent the PDF'
   is not a tool event."* A claimed action with no matching successful tool event
   is a **false-completion hard failure**, not a partial pass.
2. **Terminal conditions come in three flavors** — `success`, `safe_exit`
   (correctly declined / escalated), `failure` — so declining well scores as well
   as succeeding, which is exactly what a restraint pack needs.

## Authority and refusals (B5)

The agent must *refuse or escalate*, not merely fail to act, when:

- the action requires an approval the actor does not hold (discount beyond
  threshold, contract clause deviation) → escalate to the mapped approver;
- consent state forbids it (opted-out contact, unsubscribed email) — R2A models
  this as a `hard_fail: true` critical atom (`policy_atoms/opt-out.yaml`:
  `stop_sales_pressure_after_clear_decline`);
- the record identity is ambiguous (two plausible matches) — the hygiene skills'
  own answer is to export an audit list for human review before merging;
- the request touches confidential material (CRMArena-Pro's three confidentiality
  categories: private customer information, internal operation data, confidential
  company knowledge).
