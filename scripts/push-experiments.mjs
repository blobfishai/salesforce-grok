#!/usr/bin/env node
/**
 * Push this repo's experiment results into a blobfish world's /experiments endpoint,
 * then (optionally) ask the world to /evolve from them — closing the results-driven
 * build loop:  run trials -> push results -> evolve -> re-download -> run again.
 *
 * Usage:
 *   node scripts/push-experiments.mjs --world sbx_36847f702cef4cb4 \
 *        --files wave2.json,wave2-nearmiss.json --label wave2-grok45 [--evolve] [--dry-run]
 *   [--base https://blobfish.ai/api/v1]   (or a local dev server base)
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const argv = process.argv.slice(2);
const opt = (n, d) => (argv.includes(n) ? argv[argv.indexOf(n) + 1] : d);
const WORLD = opt("--world", null);
const FILES = (opt("--files", "") || "").split(",").filter(Boolean);
const LABEL = opt("--label", "external-grok45");
const BASE = opt("--base", "https://blobfish.ai/api/v1");
const EVOLVE = argv.includes("--evolve");
const DRY = argv.includes("--dry-run");
if (!WORLD || FILES.length === 0) {
  console.error("usage: --world <sbx_...> --files a.json,b.json [--label L] [--evolve] [--dry-run] [--base URL]");
  process.exit(1);
}
const KEY = (readFileSync(join(ROOT, ".env"), "utf8").match(/^BLOBFISH_API_KEY=(.+)$/m) ?? [])[1];

const trials = [];
for (const f of FILES) {
  const data = JSON.parse(readFileSync(join(ROOT, "data", "flake", f), "utf8"));
  for (const t of data.trialsRaw ?? []) {
    if (t.infraError) continue;
    trials.push({
      task_id: t.taskId,
      passed: !!t.passed,
      failed_conditions: t.failedConditions ?? [],
      tool_calls: t.toolCalls ?? undefined,
      cost_usd: t.costUsd ?? undefined,
    });
  }
  // arena-style summaries carry per-task aggregates only; expand to pseudo-trials
  if (!data.trialsRaw && Array.isArray(data.tasks)) {
    for (const t of data.tasks) {
      for (let i = 0; i < t.trials; i++) trials.push({ task_id: t.taskId, passed: i < t.passes });
    }
  }
}
console.log(`pushing ${trials.length} trials from ${FILES.length} file(s) to ${WORLD} as "${LABEL}"`);

const headers = { "Content-Type": "application/json", ...(KEY ? { "X-API-Key": KEY } : {}) };
const post = async (path, body) => {
  const res = await fetch(`${BASE}/sandbox/worlds/${WORLD}${path}`, { method: "POST", headers, body: JSON.stringify(body) });
  const text = await res.text();
  let json; try { json = JSON.parse(text); } catch { json = { raw: text.slice(0, 300) }; }
  return { status: res.status, json };
};

const ing = await post("/experiments", { label: LABEL, model: "grok-4.5", trials });
console.log(`/experiments -> ${ing.status}`);
console.log(JSON.stringify({ trials_recorded: ing.json.trials_recorded, frontier: ing.json.frontier, classes: (ing.json.tasks ?? []).reduce((a, t) => { a[t.class] = (a[t.class] ?? 0) + 1; return a; }, {}) }, null, 1));

if (EVOLVE && ing.status < 300) {
  const ev = await post("/evolve", { label: LABEL, model: "grok-4.5", dry_run: DRY });
  console.log(`/evolve${DRY ? " (dry run)" : ""} -> ${ev.status}`);
  console.log(JSON.stringify({ status: ev.json.status, escalated: ev.json.escalated?.length, frozen_flaky: ev.json.frozen_flaky, too_hard: (ev.json.too_hard ?? []).map((t) => t.task_id), undersampled: ev.json.undersampled }, null, 1));
}
