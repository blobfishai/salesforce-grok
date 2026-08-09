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
