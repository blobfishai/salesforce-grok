# grok-4.5 — Model Limits (measured live, 2026-08-09)

Queried directly from the xAI API with this project's key
(`GET /v1/models`, `GET /v1/language-models`, and rate-limit headers from a live
`POST /v1/chat/completions` probe). Snapshot stored in [`config/models.json`](../config/models.json).

## Headline limit

| Limit | Value |
|---|---|
| **Context window** | **500,000 tokens** |
| **Max tools per request** | **350** (measured 2026-08-10 — see below) |
| Long-context pricing threshold | 200,000 tokens (input above this bills at 2x) |
| Rate limit — requests (this key/team) | 7,200 requests/min |
| Rate limit — tokens (this key/team) | 50,000,000 tokens/min |

## Identity

| Field | Value |
|---|---|
| Model id | `grok-4.5` |
| Aliases | `grok-4.5-latest`, `grok-build-latest` |
| Fingerprint | `fp_d56666ca54` |
| Released (created ts) | 1782691200 (2026-06-29) |
| Type | Reasoning model (returns `reasoning_content`) |
| Modalities | text + image in, text out |

## Pricing (decoded from API tick values)

xAI reports prices in ticks (1 USD = 1e10 ticks); cross-checked against
`cost_in_usd_ticks` on the live probe call (7,520,000 ticks = $0.000752 for
734 prompt / 62 completion tokens — matches exactly).

| | ≤ 200k context | > 200k context |
|---|---|---|
| Input | $2.00 / M tokens | $4.00 / M tokens |
| Cached input | $0.30 / M tokens | $0.60 / M tokens |
| Output | $6.00 / M tokens | $12.00 / M tokens |

## Context-window comparison across current xAI models

| Model | Context window | Notes |
|---|---|---|
| grok-4.20 (reasoning / non-reasoning / multi-agent) | 1,000,000 | |
| grok-4.3 (`grok-latest`) | 1,000,000 | |
| **grok-4.5 (`grok-build-latest`)** | **500,000** | newest; premium pricing; coding/build flagship |
| grok-build-0.1 (`grok-code-fast-1`) | 256,000 | |

Notable: grok-4.5 is the newest and most expensive model but has **half** the
context window of grok-4.3/4.20 — the `grok-build-latest` alias signals it is
positioned as the build/agentic flagship rather than the long-context option.

## How the limit is wired into the simulation world

- `config/world.config.json` → `engine.contextWindowTokens: 500000`
- `sim/run-simulation.mjs` enforces a context guard at 90% (450,000 tokens):
  beyond it, oldest tool outputs are trimmed from the conversation.
- Probe latency for reference: TTFT 299 ms, e2e 1.58 s (`x-metrics-*` headers).

## Max tools per request — 350 (measured 2026-08-10)

Binary-searched with `scripts/probe-tool-limits.mjs` against the real wave-6
tool surface (MCP-normalized schemas, 1-token completions): **350 accepted, 351
rejected**, exactly. The API states the cap outright:

```
400 {"code":"invalid-argument",
     "error":"Maximum tools limit reached. 407 tools have been provided but the maximum is 350."}
```

`grok-4.3` enforces the identical 350 cap. Anthropic (`claude-sonnet-5`,
`claude-haiku-4-5`) and DeepSeek (`deepseek-v4-pro`, `deepseek-v4-flash`) accept
the full 407-tool surface.

### Consequence for this benchmark

The wave-6 densification (407 tools) puts the world **past xAI's ceiling**, so
grok cannot run it under either topology — the multi-server topology still
surfaces all 407 tools to the model in a single request. The attempted
grok-4.5 sweep failed 46/46 trials at $0 cost (no request reached the API);
that empty report was discarded rather than published as a result.

Getting grok onto the densified world requires cutting the per-request surface
below 350, and the choice changes what is measured:

| option | per-request tools | effect on the benchmark |
|---|---|---|
| Per-task vendor scoping (connect only the vendors a task needs) | ~30-150 | Lowers distractor pressure — the exact axis this world tests; not comparable to 407-tool runs by other models |
| Drop one vendor server for grok runs (e.g. revops-core's 104) | ~303 | Keeps pressure, changes coverage; cross-model comparison needs the same surface |
| Cap at the top-350 by relevance | 350 | Maximum pressure grok can take; needs a documented, stable ranking rule |
| Leave grok off the densified leaderboard | — | Preserves comparability of the remaining models; loses the frontier measurement |

Models whose ceiling is unknown above 407 should be re-probed before any
future densification wave.
