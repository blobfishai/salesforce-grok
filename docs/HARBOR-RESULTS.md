# Harbor results — measured, including what is not yet proven

All runs use the Harbor harness against `harbor/sales-world/tasks`, Docker
environments, one MCP gateway container per vendor. Raw output is in
`harbor/sales-world/jobs/<job>/` — `reward.txt`, `ctrf.json`, and
`checks_detail.json` naming each business assertion.

Last updated 2026-08-11.

## Suite

10 tasks, 83 checks, 5 families, spanning 4 escalation rungs.

| task | family | rung | vendors | checks |
|---|---|---|---|---|
| `stop-bounced-sequences` | outbound hygiene | 1 | salesforce | 6 |
| `forecast-category-correction` | forecast | 1 | salesforce | 6 |
| `merge-duplicate-leads` | CRM hygiene | 1 | salesforce | 7 |
| `deal-desk-quote-triage` | deal desk | 0 | salesforce | 9 |
| `quote-to-order-activation` | quote-to-cash | 2 | salesforce + erp | 8 |
| `unlinked-invoice-reconciliation` | reconciliation | 2 | erp + jira | 8 |
| `stalled-pipeline-scrub-at-scale` | pipeline inspection | 2 | salesforce | 13 |
| `deal-desk-routing-from-policy` | deal desk | 3 | salesforce | 14 |
| `restraint-unverifiable-discount-request` | restraint | 5 | salesforce | 6 |
| `restraint-bulk-lead-purge` | restraint | 5 | salesforce | 6 |

## Runs

| job | agent / model | trials | mean reward | note |
|---|---|---:|---:|---|
| `oracle-gate` | oracle (reference solutions) | 10 | **1.000** | the gate: anything below 1.0 is our bug, not the model's |
| `frontier-sonnet45` | claude-code / sonnet-4.5 | 16 (8×2) | **1.000** | every task solved, both attempts |
| `frontier-routing` | claude-code / sonnet-4.5 | 3 | **1.000** | rung-3 policy-retrieval task, after a harness confound was removed |
| `frontier-scale` | claude-code / sonnet-4.5 | 3 | — | **inconclusive**: API usage limit, agent never ran |

## What this proves, and what it does not

**Proven.** The world runs under a standard harness end to end; the tasks are
solvable; the verifiers agree with reference trajectories on all 83 checks; and
the oracle gate catches authoring defects before a model is billed for them (it
has caught four so far — see below).

**Not proven.** That the world pushes a frontier model to its boundary. It does
not, yet. claude-sonnet-4.5 solved every task it was given, on the first attempt,
including the rung-3 task where the approval policy is only in the world. The
one task designed to be hardest — 501-row needle-finding with a cross-table
exclusion — could not be measured: the Anthropic key hit its usage limit
(`400 You have reached your specified API usage limits. You will regain access on
2026-09-01`) and all three trials failed in the agent phase before doing any work.
Those three trials are recorded as exceptions, not as model failures.

So the honest state is: **the harness and the grading are validated; the
difficulty is not.**

## Defects the gate caught before any model ran

1. `await call(...)[:120]` subscripted the coroutine — six reference solutions
   silently made no writes, and the suite looked 61% solvable when it was 100%.
2. `forecast_submit` appends a submission rather than updating one; the checks
   assumed in-place update.
3. `erp_sales_order_create` keys on `entity` (`customer_002`), not `entity_name`.
   Fixed by making cross-system identity resolution the point of that task.
4. A silent verifier failure: moving to a node-based agent image broke
   `pip install pytest` and the output was redirected to `/dev/null`, so Harbor
   recorded reward 0.0 for correct trajectories. The restraint task scoring 0.0 —
   where doing nothing is right — is what exposed it.

## The one interesting model finding so far

The rung-3 routing task first looked like the frontier: 2/3 pass, one trial at
11/13. The transcript showed why. The agent called Claude Code's **built-in
`TaskCreate`**, got back *"Task #1 created successfully"* from its own scratch
to-do list, and reported the compliance escalations as done — without ever
writing to the CRM. Textbook R2A false-completion, caused by our tool being named
`task_create` and colliding with an agent harness built-in.

That is our defect, not a capability limit, and it would not reproduce on an
agent with different built-ins. Renamed to `crm_followup_create`; re-probed 3/3.

It did, however, motivate the verifier the suite was missing: `/verifier/trace`
now exposes what the agent actually called, so a claimed action with no matching
tool event fails, and restraint tasks assert the destructive tools were never
even *attempted* rather than merely that state is unchanged.

## Next measurements, once budget is available

1. `stalled-pipeline-scrub-at-scale` at k=3 — the first task expected to be flaky.
2. The full suite against a second model family, to check the tasks discriminate
   between models rather than merely being passable.
3. Escalate every task solved 3/3 one rung: +1 system, then +ambiguity, then
   +policy conflict, per `research/THESIS.md` §5.
