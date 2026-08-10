#!/usr/bin/env node
/**
 * Build dashboard/failures.html — two views:
 *   1) Frontier traces: the SAME task (task_003) passing and failing side by side,
 *      plus task_018's wrong-branch failure — flakiness made visible.
 *   2) Failure-mode report: named modes across all 300 trials with real evidence.
 * Open with #failures to render only the report section (for screenshots).
 */
import { readFileSync, writeFileSync, readdirSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const clip = (s, n) => { s = String(s ?? "").replace(/\s+/g, " ").trim(); return s.length > n ? s.slice(0, n) + "…" : s; };

const LOGS = join(ROOT, "sim", "logs");
const readLog = (name) => readFileSync(join(LOGS, name), "utf8").trim().split("\n").map((l) => JSON.parse(l));
const steps = (name) => readLog(name).filter((e) => e.type === "tool").map((e) => ({ name: e.name, args: e.args, result: e.result }));
const verdictOf = (name) => { const v = readLog(name).find((e) => e.type === "verify"); try { return JSON.parse(v.result); } catch { return null; } };

// all trials across every scan (for prevalence counts)
const allTrials = readdirSync(join(ROOT, "data", "flake")).filter((f) => f.endsWith(".json"))
  .flatMap((f) => (JSON.parse(readFileSync(join(ROOT, "data", "flake", f), "utf8")).trialsRaw ?? []))
  .filter((t) => !t.infraError);
const withCond = (pred) => allTrials.filter((t) => (t.failedConditions ?? []).some(pred));

const stepHtml = (s, hot = false) => `
  <div class="step ${hot ? "hot" : ""}"><span class="lbl">${esc(s.name.split(".").pop())}</span>
  <div class="tx">${esc(clip(JSON.stringify(s.args), 120))}<span class="res"> → ${esc(clip(s.result, 110))}</span></div></div>`;

function traceCard(title, meta, passed, list, hotFrom = null, max = 14) {
  const body = list.slice(0, max).map((s, i) => stepHtml(s, hotFrom !== null && i >= hotFrom)).join("");
  return `<div class="card"><div class="ehead ${passed ? "ok" : "bad"}"><span>${passed ? "✓ PASSED" : "✗ FAILED"}</span><span class="meta">${esc(title)}</span></div>
    <div class="emeta">${esc(meta)}</div>${body}${list.length > max ? `<div class="more">… ${list.length - max} more tool calls</div>` : ""}</div>`;
}

// ---- frontier exemplars (wave-5)
const p003 = steps("run-2026-08-10T00-48-42-677Z.jsonl");
const f003 = steps("run-2026-08-10T00-53-31-000Z.jsonl");
const f018 = steps("run-2026-08-10T00-49-45-363Z.jsonl");
const v003f = verdictOf("run-2026-08-10T00-53-31-000Z.jsonl");
const hot003 = f003.findIndex((s) => /create_|add_|update/.test(s.name) && !/hr_leave_requests/.test(s.name));
const hot018 = f018.findIndex((s) => /update.*hr_leave/.test(s.name));

// ---- failure-mode evidence
const ev007 = steps("run-2026-08-10T00-36-02-225Z.jsonl");
const ev024 = steps("run-2026-08-09T22-52-57-676Z.jsonl");
const ev011 = steps("run-2026-08-09T22-50-47-054Z.jsonl");
const ev001 = steps("run-2026-08-09T22-48-00-084Z.jsonl");

const modes = [
  {
    name: "1 · Horizon overrun → off-task writes",
    sig: "no_offtask_table_changes · no_undeclared_rows_created",
    n: withCond((c) => c === "no_offtask_table_changes" || c === "no_undeclared_rows_created").length,
    mech: "Past ~11 tool calls the model loses the thread and starts writing outside the task's scope — creating undeclared rows and mutating unrelated tables. The depth cliff's signature: chains ≤10 calls pass ~100%, ≥11 fail. Extreme case: wave-1 task_001 spiraled to 108–130 calls.",
    tasks: "task_003 (fail trials), task_018, task_001, wave-2