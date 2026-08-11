# bench/ — the benchmark as files

Regenerate with `node scripts/build-bench-folders.mjs` (idempotent; sources:
world/*/world.json, data/flake/.trials/, sim/logs/).

| folder | contents | files |
|---|---|---|
| tasks/ | every task definition by world (wave5, wave6, wave1, arena) + per-task `*.seed.json` fixture bundles (rows, documents, input documents, per-vendor MCP seeding) | 234 |
| tools/ | every MCP tool by world → vendor server: schema (.json) + generated Python implementation (.py) + INDEX.md | 1439 |
| verifiers/ | VCode verifier source (.py) + assertions metadata (.meta.json) | 228 |
| traces/ | every full run transcript, grouped world → model | 881 |
| failed-traces/ | the failing subset, same layout | 247 |
| reports/ | per-model failure report across all sweeps | 8 |

Trace filename: `<sweep-label>--<task>-t<trial>.jsonl` — turn-tagged records
(completion/thinking/tool/final/verify). Arena traces are self-contained episode
JSONs. Classifications in reports follow the audit protocol (env-bug exclusions:
wave5 task_008; wave6 task_001/task_002; undocumented-order = artifact).
