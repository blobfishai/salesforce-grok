# salesforce-grok — Morgan Stanley (SIMULATED) CRM Simulation World

> **Simulation only.** Every account, contact, deal, and figure in this repo is
> synthetic test data. This project is not affiliated with, endorsed by, or
> representative of Morgan Stanley; the name marks a fictional scenario the way
> sample CRM data names a well-known company.

A CRMArena-style simulation world for a Salesforce-CRM enterprise flow
(lead → opportunity → CPQ quote → approval chain → order/Closed Won → service
case), generated **via the [blobfish.ai](https://blobfish.ai/api-docs) API**,
exposed over **MCP**, and driven/evaluated with an **xAI grok-4.5** agent.

## Architecture

```
                       ┌────────────────────────────────────────────────┐
  xAI API (grok-4.5)   │                sim/run-simulation.mjs          │
  500k-token context ◄─┤  agent loop · context guard · task selection   │
                       └───────────────┬────────────────────────────────┘
                                       │ MCP (stdio, JSON-RPC)
                 ┌─────────────────────┴──────────────────────┐
                 ▼ default                                     ▼ --local
  ┌───────────────────────────────┐            ┌───────────────────────────────┐
  │ mcp/blobfish-crm-bridge.mjs   │            │ mcp/salesforce-crm-server.mjs │
  │ stdio ⇄ MCP-over-HTTP proxy   │            │ zero-dep mock Salesforce CRM  │
  │ + verify_task / reset_session │            │ 17 tools, policy guards       │
  └───────────────┬───────────────┘            └───────────────┬───────────────┘
                  │ Mcp-Session-Id                             │
                  ▼                                            ▼
  ┌───────────────────────────────┐            ┌───────────────────────────────┐
  │ blobfish.ai hosted world      │            │ data/seed/world-seed.json     │
  │ tables · tools · tasks ·      │            │ synthetic MS (SIMULATED) org  │
  │ VCode verifiers · sessions    │            └───────────────────────────────┘
  └───────────────────────────────┘
```

- **The world is blobfish-generated** (tables, tools, tasks, verifiers) and hosted
  by blobfish; the bridge proxies its native MCP endpoint
  (`/api/v1/sandbox/worlds/{id}/mcp`) to stdio and adds harness tools.
- The **local mock** is an offline fallback implementing the same enterprise flow
  with hard policy guards (approval sequencing, Closed-Won-only-via-order).

## Worlds

| World | id | Provenance |
|---|---|---|
| **Canonical (deep)** | `sbx_7d7d8fedcecb4458` | research-backed job `job_f214127215c947495a0e86dd` (target failure rate 0.5, anchored to `docs/anchors/ms-crm-anchor.md`) — **33 tables · 104 tools · 27 calibrated tasks/verifiers · 2,377 seeded rows**, mean discrimination 0.93, 0 degenerate tasks |
| Preview (CRM) | `sbx_70c53d3467d54e5b` | quick preview; 32 tables / 121 tools / 20 tasks; created anonymously → hosted `/verify` cannot score it |
| Preview (ERP, first iteration) | `sbx_8a6d6c92f5a64425` | pre-correction ERP-flavored world; superseded |

Downloaded artifacts: `world/blobfish/world.json`, `world/blobfish/quality.json`,
and the **self-contained runnable package** `world/blobfish/package/sbx_7d7d8fedcecb4458/`
(SQLite seed, `server.py` world server, namespaced tools incl. `tools/salesforce.py`,
tasks.jsonl, VCode verifiers, calibration trajectories, Dockerfile, RL training kit).
Blobfish's `training_ready` stamp is false only because its release gate wants ≥15
grounding sources (we anchored one PRD); the sandbox itself passed 27/27 calibration
trajectories.

Depth vs CRMArena for reference: CRMArena ~16 objects / 9 task types, CRMArena-Pro
~25 objects / 19 task types — this world: 33 tables / 27 verifier-backed tasks.

## grok-4.5 model limits (measured live)

**Context window: 500,000 tokens** — with long-context pricing above 200k, and
this key's rate limits at 7,200 requests/min and 50M tokens/min.
Full findings incl. decoded pricing ($2 in / $0.30 cached / $6 out per M tokens)
and cross-model comparison: [`docs/GROK-4.5-LIMITS.md`](docs/GROK-4.5-LIMITS.md).
Wired into the world at `config/world.config.json` (`engine.*`) with a 90%
context guard in the runner.

## Quickstart

```bash
cp .env.example .env       # set XAI_API_KEY (and BLOBFISH_API_KEY for hosted mode)
npm test                   # offline smoke test of the mock CRM MCP (20 checks)
npm run sim:local          # grok-4.5 runs the lead-to-order flow on the local mock

npm run world:serve        # serve the downloaded blobfish world locally (port 8971)
BLOBFISH_LOCAL=1 npm run sim -- --task task_004   # scored rollout + VCode verify

npm run sim -- --task task_004   # same against the blobfish-hosted world (rollout
                                 # works; hosted /verify has a session-scoping gap —
                                 # use local mode for scoring)
npm run mcp                # stdio MCP server for any MCP client (blobfish bridge;
                           # honors BLOBFISH_LOCAL=1)
npm run mcp:local          # stdio MCP server (local mock)
```

## Enterprise flow (both worlds, anchored spec)

Anchor: [`docs/anchors/ms-crm-anchor.md`](docs/anchors/ms-crm-anchor.md) —
object schemas (Lead/Account/Contact/Opportunity/Quote/Order/Case/Activity),
the lead-to-order SOP, and the CPQ approval matrix:

| Step | Approver | Trigger |
|---|---|---|
| 1 | Deal Desk | discount > 15% OR TCV > $5M |
| 2 | Compliance Officer | new client OR regulated product |
| 3 | Finance | TCV > $25M |

## Results

- **Smoke test (local mock): 20/20 pass** — flow guards, SOQL subset, forecast math.
- **Live sim (local mock, grok-4.5):** full lead-to-order close in 14 tool calls,
  correct approval-chain reasoning, ~$0.11 API cost, exit green.
- **Scored eval (canonical deep world, local server, VCode verifiers):**

  | Task | What it tests | grok-4.5 result |
  |---|---|---|
  | task_004 (hard) | find lead "Riverside Contact", verify Working, advance status | **PASSED** — minimal read→write trajectory, all 11 assertions green |
  | task_024 | bulk lead status sweep with pinned target subset | failed only `no_collateral_lead` (updated distractor rows) |
  | task_026 | bulk quote status sweep with pinned target subset | failed only `no_collateral_quote` (updated distractor rows) |

  1/3 solved with two near-misses on the strictest guard — consistent with the
  requested `target_failure_rate: 0.5` (every task has `reference_reward: 1` and
  `discrimination: 1`, so the sweeps are solvable-but-tricky by design).
  Transcripts: `sim/logs/*.jsonl`.

## Capability-frontier program (waves)

Goal: iterate world difficulty via the blobfish API until tasks sit at grok-4.5's
edge — *flaky* tasks (sometimes pass, sometimes fail) mark the frontier where
longer tool-chains push the model off-distribution.

**Wave 1 (baseline, 84 trials, $16):** 16 solid-pass · **1 flaky (task_012, 75%
pass @ ~8 calls)** · 10 solid-fail. Pass rate by interaction depth: **69% at 1–5
tool calls → 28% at 6–10 → 0% at 21+** — grok-4.5 degrades sharply as chains
lengthen, exactly the off-distribution effect the program probes. Failure
taxonomy: collateral-damage guards (literal bulk sweeps over pinned target
subsets) and wrong-lifecycle-transition writes (the world's declared status
graph defies CRM priors; the model answers from its training prior instead of
taking the extra hop to look the rule up). Data: `data/flake/wave1*.json`;
scanner: `sim/run-flake-scan.mjs`.

**Difficulty mechanics (from the blobfish-0 source), reproducible via API:**
- Tasks are random walks on a tool graph (nodes = tools, edges = produce /
  inspect / fk / workflow); **walk depth is capped by graph size**
  (`min(20, tool nodes)`), so `mock_services` (e.g. stripe: 587 ops) is the
  dominant depth lever — not the failure-rate knob.
- `target_failure_rate ≥ 0.6` selects longer walks ({3,5} steps) and 500-row
  table volume (more distractor mass).
- Anchor filenames map to research "angles"; ≥15 uploaded sources + all 12
  angles covered clears the grounding gate (`docs/anchors/wave2/` supplies 18,
  incl. `personas_roles-*` and `regulations-*`).
- `requested_task_count` triggers a DeepSeek release evaluation whose
  `pre_model_context_routing_receipts` check killed wave 1's job — omit it.
- Post-build hardening endpoints: `POST /worlds/{id}/regenerate`
  (`difficulty: {lowMaxSteps, mediumMaxSteps ≤ 10}` — direct hop control),
  `POST /worlds/{id}/calibrate` (`escalate: true` → scrubbed tool names,
  obscured entity references, distractor rows), `POST /worlds/{id}/reanchor`
  (new seed docs + new `target_failure_rate`, same lineage).
- Same `company_instance_key` + `fresh: true` **evolves** the same company
  (expansion directives, prior-task carry-forward) rather than regenerating.

**Wave 2 (API-evolved world `sbx_36847f702cef4cb4`):** 49 tables · 171 tools ·
28 tasks with 5–13-hop walks, built in 15.6 min from 18 seeded anchor docs
(salesforce+stripe forge; `target_failure_rate 0.58`; no task count — the
budget/eval traps from waves 2a/2b documented above). Scan: 15 pass (≤5 calls)
/ 13 deterministic fails — `required_workflow_path` verifiers mandate an exact
tool procedure (`list → create → get → update_status`); grok-4.5 reaches
outcomes but will not follow procedure mandates (0/26 trials, stable across
retrials). `/regenerate` (walk bounds 5–9) applied via API on the owned world.

**Wave 4 (targeted hardening, passing tasks only):** seeded SOP documents
carrying the target transition + attribute-based record references. Result:
**15/15 still pass** — naming the SOP in the prompt made retrieval a one-hop
giveaway. Negative result, kept: it separates *retrieval difficulty* from
*decision difficulty*.

**Wave 5 (the sharper ratchet):** conflicting SOP versions (an outdated
procedure prescribing a plausible wrong target), conditional rules (the correct
transition depends on the record's own attributes), identification collisions,
decoy documents. Result: **frontier found** —
- `task_003` **flaky at 50%** (3/6, ~10–15 calls) — the model's limit, embodied;
- `task_018` one notch past it (0/6 at 17–25 calls, wrong branch + off-task writes);
- the 13 survivors stretched from 3–4 to 6–9.3-call chains, all still passing;
- depth curve across the wave-2 family: **~100% ≤10 calls → 0% at 11+** — the
  degradation cliff, sharply localized. Failure signature at the cliff:
  `no_offtask_table_changes` / `no_undeclared_rows_created` — the model starts
  writing where it shouldn't once the chain exceeds its horizon.

Interactive episodes (`sim/run-interactive.mjs`) make traces CRMArena-comparable:
a simulated stakeholder opens with a problem prompt and reveals details only on
request; grok works it conversationally (`<thought>` → clarify → tools → report);
VCode scores the end state. See `dashboard/traces.html` for the side-by-side with
CRMArena's published GPT-4o ReAct trajectories.

## UI evidence (`screenshots/`)

- `blobfish-hosted-viewer.png` + `hosted-band-*.png` — blobfish.ai's own world
  viewer (`/w/sbx_70c53d3467d54e5b`): prompt→world trace, thesis, anchoring
  chips, persona role clusters, task list, and the **task dependency DAG**
  (121 tools · 186 edges · "20 grounded paths from random walks").
- `blobfish-cli-dashboard.png` — Blobfish Gym (the CLI's local dashboard,
  exported from blobfish-0) reading our downloaded deep world package.
- `dashboard-wave1-merged.png` — this repo's own dashboard
  (`scripts/build-dashboard.mjs` → `dashboard/index.html`): world stats,
  depth curve, failure taxonomy, scoreboard, verified live rollout.

## Repo layout

```
config/            world.config.json (engine/MCP wiring) · models.json (xAI snapshot)
data/seed/         synthetic seed for the local mock
docs/              GROK-4.5-LIMITS.md · anchors/ (world-generation anchor PRDs)
mcp/               blobfish-crm-bridge.mjs · salesforce-crm-server.mjs
sim/               run-simulation.mjs · lib/mcp-client.mjs · scenarios/
test/              smoke.mjs
world/             downloaded blobfish world artifacts
```

## Notes & gotchas

- Secrets live in `.env` (gitignored). The blobfish key was registered with the
  repo owner's email; the xAI key was provided for this project — rotate it if
  it was ever shared more broadly than intended.
- blobfish docs drift: the documented `POST …/tools/{name}` path 404s — use the
  session's `mcp_url` (MCP-over-HTTP) with `Mcp-Session-Id`, as the bridge does.
- Hosted `/verify` does not see session-scoped rollout state; the downloaded
  package's own `server.py` (same endpoints) verifies correctly when the bridge
  posts the rollout trace to `POST /verify/{task_id}` — so scoring runs locally.
- MCP tool names are namespaced (`salesforce.list_lead`) but VCode verifiers
  match bare names — the bridge records `tool` (bare) + `requested_tool`
  (namespaced) in the trace, matching blobfish's own trace format.
