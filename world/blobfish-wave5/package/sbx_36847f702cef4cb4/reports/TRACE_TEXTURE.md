# Trace texture — morgan_stanley_simulated

How closely this world's tasks and calibration traces match the texture of
REAL production agent traces. The reference column comes from a checked-in
fixture distilled from a production corpus — **statistics only** (histograms
and ratios); no user content, user ids, or entity strings ever left the
source corpus.

Enforcement boundary: `answer_leak_rate` and the resolution-share floor are
gated at generation time on newly built worlds. Every other row is
report-only evidence. Worlds generated before the scorecard existed are
grandfathered and report "not measured".

## Scorecard

Computed 2026-08-10T00:31:28.065Z over 28 task(s), 25 mutation-graded.

| Metric | This world | Production reference | Status |
|--------|-----------|----------------------|--------|
| Answer-leak rate (prompt names graded pk AND target value) | 0.000 | 0 — real requests never name a numeric pk (0.000) | PASS (enforced = 0) |
| Resolution-class share (over 25 resolvable task(s)) | 1.000 | entity resolution is the norm in production requests | PASS (enforced ≥ 0.3) |
| Session-task share (scripted mid-episode user turns) | 0.321 | multi-turn sessions dominate production (generated-world floor ≥ 0.3) | PASS (enforced ≥ 0.3) |
| Free-text delegated task share | unavailable | call-level production reference is reported below | customer-release gate basis |
| Free-text arg ratio (≥80-char NL strings in tool args) | unavailable — calibration rollouts persist tool names, not arguments | 0.4023 | report-only |
| Step-histogram distance to production (0 = identical) | — | production long tail spans 1–11+ steps | report-only |
| Reference pass rate vs discriminative band [0.4, 0.9] | 0.720 (budget_pressure_proxy) | a saturated pass rate is a red flag, not a win | n/a — no real-model rate (policy proxies are never presented as model rates) |
| Environment tool-failure rate (injected + organic) | 0.029 | ~0.02–0.073 of production calls fail environment-side (fixture step_error_rate 0.023) | ENFORCED in [0.02, 0.073] (deterministic injection, seed-keyed, always recoverable) |
| Failure→recovery arcs | 3/3 exact-call recoveries (rate 1.000); 0/3 produced the blocked state effect (rate 0.000); 3 incidental/unproven; median 1 step(s) | production models recover from environment failures over subsequent steps | report |

### Step-count histogram (calibration rollouts)

| Steps | Rollouts |
|-------|----------|
| 1 | 27 |
| 2 | 70 |
| 3 | 23 |
| 4 | 18 |
| 5 | 2 |
| 6 | 1 |
| 7 | 1 |
| 9 | 3 |
| 10 | 1 |
| 11 | 2 |
| 13 | 2 |

## Friction spec

The world was generated under these friction parameters (WS5); they are
part of the world spec, not runtime randomness:

- `delegation_write_cap`: 50 — max rows a delegation sub-agent writes per call; larger imports require chunked repeat calls.
- `ambiguous_ack_rate`: 0.15 — fraction of delegation writes that APPLY but return an ambiguous acknowledgment (production retry pairs show null first-call output).
- `cross_table_ambiguous_labels`: 2 — business labels duplicated across tables so resolution genuinely requires disambiguation.
- `tool_failure_signature_rate`: 0.03 — fraction of unique (tool, args) signatures whose FIRST call fails with a deterministic, recoverable environment error (seed `b4b1f3b12afc2250`); an identical retry always succeeds.

## Reference provenance

- Policy: stats only; no user content, user ids, or entity strings
- Source (stats only): `nario/.blobfish/appsnapshot_full/traces/{mongo_production,mongo_conversations,dataflywheel_line_turns,dataflywheel_platform_turns}.jsonl`
- Source (stats only): `dev/dataflywheel_{turns_500,frustration_200,bot_failures_200,zh_vi_200,frustration_high}.json`
