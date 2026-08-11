# Thesis — what this sales world is, and why it is hard

> Written 2026-08-11 from the research corpus: 37 cloned repos
> (`research/repos/`, manifest + clone log), 185 practitioner skill definitions,
> 5 benchmark families, and ~25 dated web sources (`research/SOURCES.md`).
> Every claim below is traceable; unsourced judgment is marked *[judgment]*.

---

## 1. The framing

**Public sales/CRM evals test single-system competence. Real sales work is
multi-system reconciliation under policy, on dirty data, against a clock.**

The evidence for the first half is direct. CRMArena-Pro's 22 categories all run
against one Salesforce org, and only about four of them are true multi-step
mutations (`eval-task-census.md` §1). τ-bench's domains are one `db.json` each.
SCUBA is 300 tasks inside a single Salesforce UI. The Attio benchmark is eight
read queries. Nobody grades an agent on "the CRM says X and billing says Y."

The evidence for the second half is equally direct, and it comes from the people
doing the work rather than the people benchmarking it: 37 shipped HubSpot *admin*
skills exist to dedupe, backfill, suppress, and reassign; three independent GTM
repos encode the *same* enrichment-waterfall-with-a-budget pattern; the field
literature reports 15–25% duplicate rates, 76% of records under half complete,
14-day enrichment lag, and CRM deal amounts that *"rarely match recognized
revenue"* (`data-chaos-catalog.md`).

So the world's thesis is: **put the chaos in the middle of the task, not around
it.** Difficulty should come from the structure of the business — several
systems, several defensible answers, a policy that outranks the model's prior —
not from arbitrary hop counts.

## 2. Five findings that change the design

### F1 — The Rule-to-Action Gap is the single sharpest published failure mode
R2A-Sales measures models that *state* a policy correctly 89.9–99.1% of the time
but *act* on it only 3.0–17.3% of the time under goal-directed pressure — a gap
of 80–92 points across eight backbones. Their mechanism is a `pressure_schedule`
that escalates over turns while a policy atom stays constant.

*Implication:* our best tasks are not longer chains; they are chains where a
documented rule and a commercial incentive point in opposite directions. We
already found a weak version of this by accident in wave 5 (the model answers
from its CRM prior instead of looking the world's rule up). R2A says to build it
on purpose, with graded severity and hard-fail atoms.

### F2 — "Saying is not doing" needs to be a first-class verifier
R2A's sandbox states it plainly: a customer-visible sentence such as *"I sent the
PDF"* is not a tool event, and a claim with no matching successful call is a
**false-completion hard failure**. Our current verifiers score state deltas and
collateral, so an agent that narrates a completed workflow it never performed can
partially pass. That is a hole. *[judgment: this is likely to catch real grok
behavior at the 10+ call depth where we already see off-task writes.]*

### F3 — Checkpoints beat terminal assertions for long-horizon work
SCUBA reports *"fine-grained evaluation metrics to capture milestone progress"*
and shows demonstrations lifting success 39% → 50% while cutting time 13% and
cost 16%. A single terminal assertion throws away the signal about *where* a
25-call trajectory went wrong — which is exactly the signal a capability-frontier
program exists to collect.

### F4 — The documentation lies, and that is realistic
The Attio benchmark's compound-filter query failed twice on documented picklist
values (`501-1000`) that did not exist in the workspace (`5K-10K`, `10K-50K`, …),
then needed a schema-discovery call to recover. Our wave-5 "conflicting SOP
versions" trick is the same idea, independently arrived at. Convergent evidence
that *retrieval-of-the-actual-rule* is a real, gradeable skill.

### F5 — The admin/hygiene persona is the field's biggest un-benchmarked surface
SCUBA names a platform-administrator persona; the practitioner corpus supplies 37
concrete admin tasks with explicit acceptance criteria; no public *sales* eval
grades any of them. This is white space we can occupy credibly, and it is
naturally bulk-shaped — pinned target subsets with hard collateral guards, the
exact structure that already breaks grok-4.5 in our wave-1 scan.

## 3. What the world must contain (design consequences)

| Consequence | Because of | Concretely |
|---|---|---|
| **≥3 systems of record holding overlapping facts** | E1/E2, F-none-cover-it | CRM + billing + ERP + a *spreadsheet* + an engagement tool, seeded with deliberate, recorded divergence |
| **A spreadsheet as a first-class system** | shadow-sheet finding; `workflow/BraaMohammed__bricks` | sheet rows that are authoritative for some questions and stale for others |
| **Two providers for the same fact** | enrichment-waterfall pattern in 3 repos | provider A vs B disagree; credits/costs; partial success |
| **A policy layer with severity and hard-fail atoms** | F1 | port R2A's atom schema: applicability, required_behaviors, allowed/forbidden claims, escalate_when, source_evidence |
| **A pressure/incentive dimension** | F1 | interactive stakeholder who pushes back over turns while the rule holds |
| **Checkpoint scoring + false-completion detection** | F2, F3 | milestone assertions; claim-vs-tool-event cross-check |
| **A clock and a fiscal calendar** | cadence evidence; "this week" ambiguity | week/quarter boundaries, timezones, as-of snapshots |
| **A measured dirty-data baseline** | E5 | seed off-baseline at known rates with a ground-truth dirty set |
| **Three terminal outcomes, not two** | R2A | `success` / `safe_exit` (declined or escalated correctly) / `failure` |

## 4. The tool universe (what to mock next)

Evidence-backed verb surfaces are already extracted:
Attio 285 · Pipedrive 142 · HubSpot 112 (+68 distinct REST endpoint templates) ·
Close 94 · Twenty 31 · Salesforce 26+18 · multi-CRM 27 · Gong 22 · LinkedIn 14 ·
Apollo 7 (`research/tools/_extracted/INDEX.tsv`).

The point of holding *competing* CRMs is not breadth for its own sake — it is
that a real org mid-migration runs two, and the mapping between them is lossy
(54% of migrations delayed; 67% find data issues mid-migration). A HubSpot
account that is *also* a Salesforce account, with a partial field map, is the
most realistic hard object we can build. *[judgment]*

Next mocking pass, in priority order:
1. **HubSpot** (competitor CRM, 112 verbs + real endpoint templates) — enables the
   two-CRM migration scenario.
2. **Spreadsheet surface** with real range/formula semantics — enables shadow-sheet tasks.
3. **Enrichment providers ×2** (Apollo-shaped + a second) with credits and partial
   success — enables waterfall tasks.
4. **Attio or Pipedrive** as the third CRM flavor with a *different object model*
   (attributes vs fields) — enables schema-translation tasks.
5. **Gong** conversation intelligence — enables artifact→state tasks from transcripts.

## 5. The task program

Start from evidence, then escalate against measured difficulty:

**Seed set** — port every task type that already exists:
CRMArena-Pro's 22 (adapted to our schema), the hygiene 37, the GTM pipeline
stages, the deal-desk 8-step workflow, the six readings of "sales this week."

**Escalation ladder** (applied only to tasks the model *passes first try*):
1. more hops on the tool graph (existing lever);
2. **+1 system** — same question, answer now requires reconciling a second store;
3. **+ambiguity** — remove a disambiguator from the prompt so the model must ask
   or state an assumption;
4. **+policy conflict** — a documented rule that contradicts the CRM prior;
5. **+pressure** — an interactive stakeholder pushing for the non-compliant action;
6. **+restraint** — make the correct action "write nothing and explain."

**Retry protocol** (unchanged, and it is the right one): 3 straight failures ⇒
too hard, stop and record the failure mode; pass/fail mix ⇒ **flaky = the
frontier, keep and study**; pass first try ⇒ escalate one rung.

**Guard against ourselves:** a task that *every* model fails is a bug until
proven otherwise (`docs/CREATION-PROTOCOL.md`); τ²-bench-verified exists precisely
because a well-funded benchmark shipped defective tasks. Before any new task
family is admitted, an LLM judge must check that its premise cites a real source
in this corpus — see `docs/GROUNDING-JUDGE.md`.

## 6. Open questions blocking the next phase

- **A3** business-value metrics (quota, coverage, NRR bands) — needed to make
  analytics answers *matter* rather than merely compute.
- **D5** API failure semantics (429s, partial writes, idempotency, async bulk) —
  needed before the second CRM is mocked, or the migration scenario will be
  unrealistically clean.
- **F3** answer-grading policy (tolerance, units, required disclosures) — needed
  before any "what's the number" task is written.
- **C7** ambiguity variants — needed to build rung 3 of the ladder.
