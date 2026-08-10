# blobfish.ai Studio — critical generation QA

> 2026-08-10. Evidence-based audit of the generator/studio against the 7 checks.
> Interactive chat-UI flows could not be driven this session (browser extension not
> connected; studio requires an authenticated session — headless capture only, see
> `screenshots/studio-home.png`, `screenshots/studio-viewer-w6.png`). Everything
> else is tested at the API/SSE/artifact level, where this session has deep evidence.

## Verdict table

| # | Check | Verdict | Evidence |
|---|---|---|---|
| 1 | Happy path works | ⚠️ **Fragile** | Deep job succeeded once (13.5 min, r3) after two platform-side failures: SSE-reconnect executor race ("changed in another process"), then a 25-min `assemble_calibrate` budget kill on a 12-service mount. Preview path currently returns **HTTP 500** on its own acceptance gate (below). Studio page renders (screenshot). |
| 2 | Creation/thesis/mock data not hardcoded | ⚠️ **Partly template-driven** | Same 12-bucket namespace skeleton in every world (`calendar core email erp github jira notion pagerduty salesforce slack stripe`); same agent-substrate tables; task prompts reuse fixed skeletons across domains — wave-6 has 8× "Find the X, verify status is S, then set its status to T" and 4× "the operations queue has …"; the accounting attempt died with the same `required_workflow_path` scaffold in a different domain. Content (tables/rows/docs) IS prompt-derived; the *skeletons* are not. |
| 3 | Tasks relevant to the company domain | ⚠️ **Leaks** | A SALES world shipped HR tasks (task_002/012/013 operate `hr_leave_requests`) and admin-surface tools (Slack EKM/IDP, calendar ACLs, `admin_emoji_list` under `erp`). Accounting attempt's content was domain-true (bank_accounts, bank_transactions) — relevance of *data* is good; relevance of *tools/tasks mix* is not enforced. |
| 4 | Richer than open-source evals | ✅ **Yes** | 214 tables / 205 executable tools / state-diff verifiers / conflicting-SOP documents / measured depth frontier (both grok-4.5 and v4-flash die at 21+ calls). CRMArena tops out at read-only answer-matching; see docs/COMPARISON.md + bench/. |
| 5 | Interruption/feedback doesn't restart the world; updates incrementally | ⚠️ **Half-true** | Evolution exists and works: same `company_instance_key` + `fresh:true` carries tasks forward (wave-1→2 lineage; `/experiments` + `/evolve` close the loop). But every evolution is a **full rebuild** under the same 25-min budget — not an in-place update — and a dropped/reconnected SSE stream can spawn a second executor that **kills the build mid-flight** (r1 failure). Interruption is currently dangerous, not safe. |
| 6 | Other domains stay clean (accounting test) | ❌ **Blocked by a worse bug** | The anchored accounting preview **failed generation entirely**: `HTTP 500 — "Resolution top-up re-proof failed"`: the generator's own reference walks scored 0/1 on its own VCode (needs ≥60%), failing `required_workflow_path`, `bank_transactions_2_amount_is_null` (null seeded data), and `reference_tool_failed:update_*` (generated tools crash on the generator's own replay). No cross-domain leakage was observable in the gate output — but "thoughtfully generated" fails when the generator can't solve its own tasks. |
| 7 | Chat narrates progress/thinking/plan per stage | ❌ **No** | The SSE stream emits only coarse stage keys + heartbeats (`creating_world` → `stage` → `done`; 30s heartbeats — see wave6_stream.log). No thinking traces, no per-stage task breakdown, no plan updates, no evidence links during generation. |

## The systemic bug that ties it together

The **preview path hard-fails** worlds whose reference walks can't pass their own
verifiers (good gate, brutal UX). The **deep path skips that same gate** when its
budget runs out — wave-6 tasks shipped with `solvability: {measured:false, reason:
"budget_exhausted" / "not_sampled"}` — which is exactly how task_001 (unexpanded
`{name}`, nonexistent "Kofi") and task_002 (verifier pinned to a row the prompt
never names) reached production. One gate, inconsistently applied, is the root of
most downstream damage.

## Bug ledger (this session, all evidenced in repo history)

1. SSE reconnect spawns a second executor → "sandbox world changed in another process" build death (r1).
2. 25-minute end-to-end `assemble_calibrate` budget kills large multi-service mounts (r2); no partial-progress resume.
3. Preview endpoint drift: prompt-only generation removed (400 "anchor_files are required") — undocumented.
4. Preview acceptance gate returns raw internals in HTTP 500; no world id, no retry guidance.
5. Deep path ships tasks with solvability sampling skipped (budget_exhausted) — broken tasks reach users.
6. `required_workflow_path` demands orders documented nowhere (failed by 7/7 models AND by the generator's own accounting reference walk).
7. Unexpanded `{name}` template + referenced person absent from every table (wave-6 task_001).
8. Verifier row mispinning: prompt names LEAVE-243410 (row 224), verifier pins row 8 (task_002).
9. Null seeded fields the verifier then asserts on (`bank_transactions_2_amount_is_null`).
10. Generated tool implementations fail on the generator's own replay (`reference_tool_failed:update_*`).
11. Duplicate entries in tool schema `required` arrays → DeepSeek/Anthropic reject entire requests.
12. Fixed 12-bucket namespace skeleton regardless of domain; mounted services scattered across wrong buckets (Intercom→pagerduty/jira, sheets→github, NetSuite emoji contamination).
13. Distiller picks admin surfaces over workflow verbs (Slack EKM/IDP instead of post_message; calendar ACLs instead of booking; deprecated `post_charges`).
14. Anchor document TEXT dropped during ingestion (2 docs survived from 46; schemas kept) — repaired locally by seed-wave6-documents.mjs.
15. Session capacity 256 with no idle reaping → sweeps die mid-run (repaired locally: bridge releases sessions).
16. Hosted `/verify` remains session-blind (long-standing; local package verify is the only sound path).
17. Off-domain task mix in-world (HR leave tasks inside a sales world).
18. arena builder-class risk generalizes: GTs computed before later data mutations go stale (our own arena bug was the same class the generator risks with top-up passes).

## What "shippable" requires (priority order)

1. Apply the solvability gate uniformly (deep path must not ship unsampled tasks); on gate failure, **repair** (re-anchor row pins, expand templates) instead of 500.
2. Kill or document-in-world `required_workflow_path`.
3. Domain-filter the namespace skeleton and re-curate distillation toward workflow verbs (the sales world needs `post_message`/`book_meeting`/`create_subscription`, not EKM/ACL/emoji).
4. Preserve anchor document text as in-world readable documents.
5. Single-executor job locking (SSE reconnects must be safe); resumable builds beyond 25 min.
6. Stream real progress: stage plan, per-stage artifacts, thinking traces, task list as generated.
