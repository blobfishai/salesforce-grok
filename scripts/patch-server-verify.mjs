#!/usr/bin/env node
/**
 * Patch a packaged world server so /verify/{task_id} accepts an
 * `initial_state` override in the POST body — the post-task-seed, pre-agent
 * snapshot of the session DB. Without this, per-task fixtures (task-seed.v1
 * bundles) would read as undeclared agent writes, because the stock server
 * always diffs against the static SEED_DB baseline.
 *
 * Idempotent; safe to rerun after re-downloading a package.
 * Usage: node scripts/patch-server-verify.mjs world/blobfish-wave6/package/<id>/server.py
 */
import { readFileSync, writeFileSync } from "node:fs";

const target = process.argv[2];
if (!target) { console.error("usage: patch-server-verify.mjs <path/to/server.py>"); process.exit(1); }
let src = readFileSync(target, "utf8");

const patchedV2 = `            initial = snapshot(SEED_DB) if os.path.exists(SEED_DB) else {}
            # BF_TASK_SEED_PATCH_V2: harness may supply per-table post-task-seed
            # baselines ("initial_state": {table: {rowid -> row}} — only the
            # tables the seed touched, keeping the body small). Each supplied
            # table REPLACES that table's SEED_DB view, so fixtures are initial
            # state, not agent writes. JSON string keys coerce back to int.
            _override = body.get("initial_state") if isinstance(body, dict) else None
            if isinstance(_override, dict) and _override:
                for _t, _rows in _override.items():
                    if isinstance(_rows, dict):
                        initial[_t] = {int(_k): _v for _k, _v in _rows.items()}
            final = snapshot(current_state_db())`;

if (src.includes("BF_TASK_SEED_PATCH_V2")) { console.log("already patched (v2)"); process.exit(0); }

const V1_RE = /            initial = snapshot\(SEED_DB\) if os\.path\.exists\(SEED_DB\) else \{\}\n            # BF_TASK_SEED_PATCH:[\s\S]*?final = snapshot\(current_state_db\(\)\)/;
const anchor = `            initial = snapshot(SEED_DB) if os.path.exists(SEED_DB) else {}
            final = snapshot(current_state_db())`;

if (V1_RE.test(src)) src = src.replace(V1_RE, patchedV2);
else if (src.includes(anchor)) src = src.replace(anchor, patchedV2);
else { console.error("anchor not found — server.py layout changed; patch manually"); process.exit(1); }

writeFileSync(target, src);
console.log(`patched ${target} (v2)`);
