#!/usr/bin/env node
/**
 * Re-score arena summaries from the saved per-episode logs against the CURRENT
 * ground truth in world/arena/arena-tasks.json — no model calls. Written for the
 * 2026-08-10 handle_time GT correction; safe to rerun any time GT changes.
 * Rewrites data/flake/lb-arena-<model>.json in place (episode files untouched).
 */
import { readFileSync, writeFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const spec = JSON.parse(readFileSync(join(ROOT, "world", "arena", "arena-tasks.json"), "utf8"));
const gtOf = Object.fromEntries(spec.tasks.map((t) => [t.id, t]));

// same matching rules as sim/run-arena.mjs
const norm = (s) => String(s ?? "").trim().toLowerCase().replace(/[.\s"']+$/g, "").replace(/^["']+/, "");
function score(metric, gt, answer) {
  const a = norm(answer);
  if (metric === "exact") return norm(gt) === a || a.endsWith(norm(gt)) || a.includes(norm(gt)) && norm(gt).length > 4 && a.length <= norm(gt).length + 12;
  if (metric === "fuzzy") return norm(gt).split(/\s+/).every((tok) => a.includes(tok));
  if (metric === "set") {
    const want = (Array.isArray(gt) ? gt : [gt]).map(norm).sort();
    const FACTORS = ["budget", "authority", "need", "timeline", "none"];
    const got = FACTORS.filter((f) => a.includes(f)).sort();
    return JSON.stringify(want) === JSON.stringify(got);
  }
  return false;
}

const dir = join(ROOT, "sim", "logs", "arena");
const byLabel = {};
for (const f of readdirSync(dir).filter((f) => f.startsWith("lb-arena-") && f.endsWith(".json"))) {
  const ep = JSON.parse(readFileSync(join(dir, f), "utf8"));
  const label = ep.label ?? f.replace(/-arena_[a-z_]+-t\d\.json$/, "");
  const t = gtOf[ep.taskId];
  if (!t) continue;
  const passed = ep.answer !== null && ep.answer !== undefined && score(t.metric, t.gt, ep.answer);
  const b = ((byLabel[label] ??= { model: ep.model, tasks: {}, costUsd: 0 }).tasks[ep.taskId] ??= { p: 0, n: 0 });
  b.n++; if (passed) b.p++;
  byLabel[label].costUsd += ep.costUsd ?? 0;
}

for (const [label, agg] of Object.entries(byLabel)) {
  const out = {
    label, level: spec.level, model: agg.model, finishedAt: new Date().toISOString(),
    rescoredAt: new Date().toISOString().slice(0, 10),
    rescoreNote: "re-scored from episode logs against corrected GT (handle_time audit 2026-08-10)",
    tasks: Object.entries(agg.tasks).map(([id, b]) => ({ taskId: id, passes: b.p, trials: b.n, passRate: b.p / b.n, class: b.p === b.n ? "pass" : b.p === 0 ? "fail" : "FLAKY" })),
    costUsd: +agg.costUsd.toFixed(2),
  };
  writeFileSync(join(ROOT, "data", "flake", `${label}.json`), JSON.stringify(out, null, 2));
  const p = out.tasks.reduce((s, t) => s + t.passes, 0), n = out.tasks.reduce((s, t) => s + t.trials, 0);
  console.log(`${label}: ${p}/${n} (${(p / n * 100).toFixed(1)}%)`);
}
