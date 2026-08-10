# How this world differs from CRMArena, MCPEval, and ai_sales_eval_arena

> Evidence gathered 2026-08-09 from the upstream repos, arXiv papers (2411.02305,
> 2505.18878, 2507.12806), and artificialanalysis.ai. Honest-comparison style: each
> section ends with what the other benchmark still does better.

## TL;DR table

| Dimension | CRMArena / -Pro | MCPEval | ai_sales_eval_arena | **This world (blobfish)** |
|---|---|---|---|---|
| What the agent does | Query a Salesforce org, return an answer (ID/number/text) | Execute auto-generated tasks on one MCP server | Nothing — LLM judges static pitch transcripts | Execute multi-step business workflows that **mutate** world state |
| Success criterion | Exact match / token-F1 on the answer | Tool-call similarity to one frontier reference trajectory + LLM judge rubric | LLM pairwise judgment | **Deterministic VCode program** checks final DB state + trace (state deltas, policy order, no collateral writes) |
| State mutation verified | No — routing tasks return a queue ID, nothing is re-assigned | No — success never inspects end-state | No state at all | **Yes — the core of every verifier** |
| Cross-app workflows | No (SOQL/SOSL onto one org) | No (per-server isolation; MCP-Bench was built on this critique) | No | **Yes** — CRM + billing + messaging (+ wave-6: 12 mocked services) |
| Documents as difficulty | None (no attachments/PDFs/policies to read) | None | The transcript *is* the input | **SOP corpus with conflicting versions/decoys the agent must read to act correctly** |
| Judge in the loop | LLM judge only for confidentiality track | LLM judge for half the score | Judge is the whole benchmark | **No LLM judge anywhere in scoring** |
| Multi-model leaderboard | Paper tables | Repo dashboard | Tournament standings of transcripts | `dashboard/leaderboard.html` (AA-style strict/lenient dual metric, cost axis) |
| Difficulty adaptation | Static templates | Capped at what the generator model can solve | n/a | **Frontier-driven evolution**: hardening waves until tasks flicker for the measured model |

## vs CRMArena / CRMArena-Pro (Salesforce AI Research)

What they are: 9 (Arena) / 19 (Pro) answer-oriented task types over live hosted
Salesforce orgs with LLM-generated data; agents issue SOQL/SOSL or 27 read/calc
function wrappers and return an answer scored by exact match / F1. Best models:
o1 64.3% (Arena, function calling), gemini-2.5-pro 54-58% single-turn, ~30-35%
multi-turn (Pro).

Where this world is materially harder / different:

1. **Writes, not answers.** CRMArena's "New Case Routing" is solved by *naming* a
   queue ID. Here the equivalent task only passes if the case row actually ends in
   the right state, the mandated approval order (Deal Desk → Compliance → Finance)
   appears in the trace, audit logs stayed append-only, and **nothing else changed**
   (`no_offtask_table_changes`, `no_undeclared_rows_created`). Our measured failure
   signature — off-task/undeclared writes at ≥11 tool calls — is a failure class
   CRMArena cannot observe by construction.
2. **Documents are the difficulty lever.** CRMArena has no attachments, policies or
   artifacts. Here wave-4 proved that *naming* the governing SOP is a giveaway
   (15/15 pass); wave-5's conflicting SOP versions + conditional rules produced a
   real frontier (task_003 flaky at 50%, depth cliff at 11+ calls).
3. **Cross-system invariants.** Closed-won opportunity ⇒ executed order form ⇒
   activated order ⇒ subscription ⇒ invoice — verifiable chains across mocked
   Salesforce/Stripe/Slack (wave 6 extends to a 12-service GTM stack). CRMArena-Pro
   stays inside one org schema.
4. **No judge stochasticity.** Pro's confidentiality track and multi-turn answers
   route through gpt-4o judging / answer extraction; our verifiers are pure Python
   over SQLite state.
5. **Difficulty is measured, not assumed.** Tasks carry measured solvability
   (provider runs at build time) and are escalated wave-over-wave against the
   *actual* frontier model until they flicker — vs. static templates whose top tasks
   saturate (Top Issue Identification: 99.2%).

Where CRMArena still wins, honestly: 1,170-4,280 query instances vs our tens of
tasks (statistical power per task type); a genuinely hosted Salesforce org with real
API friction; expert human validation of task templates; a published confidentiality
/ PII-awareness track we don't attempt; simulated-user multi-turn at scale.

## vs MCPEval (Salesforce AI Research)

What it is: auto-generates tasks from any MCP server's tool specs, verifies them by
having a frontier agent execute them, then scores target models by tool-call
similarity to that reference trajectory (name/param/order match) plus an LLM-judge
rubric. 4,973 tasks over 5 mostly read-only public-API domains, 4-11 tools each.

Differences that matter:

1. **Reference-trajectory scoring penalizes valid alternatives and caps difficulty.**
   MCPEval's ground truth is *one* frontier agent's path; tasks that agent cannot
   solve are rewritten or dropped, so the benchmark cannot be harder than its
   generator. Our verifiers assert *outcomes* (any tool path that produces the right
   final state without collateral damage passes; the only path-shaped assertion,
   `required_workflow_path`, exists where a written SOP mandates the procedure).
   That is why our wave program could push *past* grok-4.5's frontier instead of
   being bounded by it.
2. **Persistent stateful world vs read-only APIs.** MCPEval's paper domains are
   drug lookups, stock quotes, park info — no business end-state to grade. Ours is
   copy-on-write SQLite per session with 49 tables (500-row distractor mass) and
   deliberately counter-prior lifecycle graphs.
3. **Scale of tool surface.** 4-11 tools per server vs 171 (wave 5) → 400+ (wave 6)
   namespaced tools across mocked vendors — tool *selection* under distractor
   pressure is itself part of the eval.
4. **No LLM judge.** Half of MCPEval's score is a GPT-family rubric judge; ours is
   deterministic.

Where MCPEval still wins: task volume through automation (thousands vs dozens);
plug-and-play onto arbitrary third-party MCP servers; bootstrap CIs and paired
significance tests in its dashboard; a shipping React replay UI.

## vs ai_sales_eval_arena (Rperry2174)

Not actually an agent benchmark: it LLM-judges ~50 static, AI-written sales-pitch
monologue transcripts for one product in head-to-head tournaments (and despite the
name, contains no ELO — standings are win counts). No tools, no CRM, no dialogue,
no state; quality tiers leak through participant filenames into the judge prompt.
There is no overlap with evaluating *agents doing sales work*; it evaluates
*content*. The one idea worth keeping — tournament-style pairwise comparison — is
orthogonal and could someday rank *trajectories*, but its own implementation
(positional-bias fallback bug, single judge, no significance) is not the reference.

## vs the Harvey LAB-AA leaderboard (presentation, not competition)

Artificial Analysis's Harvey legal benchmark page is the presentation target, not a
CRM competitor: 120 private long-horizon tasks, deliverable graded criterion-by-
criterion by a single LLM judge (Gemini 3.1 Pro), dual lenient/strict metric
(criterion pass rate 93-95% vs all-pass rate ≤14.2%), accuracy-vs-cost scatters,
token-level cost decomposition, example task cards. Our leaderboard copies the
page grammar (strict/lenient toggle, cost scatter, per-task matrix, explicit
methodology) while replacing the LLM judge with deterministic state verification —
and adds the failure-mode taxonomy AA itself lacks (their pages show *scores*, not
*why* models fail).

## The one-sentence answer

CRMArena asks agents to *look things up*, MCPEval asks agents to *imitate a
reference trajectory*, ai_sales_eval_arena doesn't test agents at all — this world
is the only one of the four that grades an agent on whether it can *change a
business system's state correctly under written policy constraints, across mocked
vendor systems, with documents it must read and distractors it must ignore*, scored
by deterministic program verification and hardened wave-over-wave against the
measured frontier of the model under test.
