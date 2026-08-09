# grok-4.5 — Model Limits (measured live, 2026-08-09)

Queried directly from the xAI API with this project's key
(`GET /v1/models`, `GET /v1/language-models`, and rate-limit headers from a live
`POST /v1/chat/completions` probe). Snapshot stored in [`config/models.json`](../config/models.json).

## Headline limit

| Limit | Value |
|---|---|
| **Context window** | **500,000 tokens** |
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
