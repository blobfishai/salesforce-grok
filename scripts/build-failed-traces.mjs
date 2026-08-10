#!/usr/bin/env node
/**
 * Turn-by-turn trace viewer for every FAILED wave-6 task (flash validation,
 * trial 1): the model's thinking, each tool call with args and observation,
 * the final answer, and the verifier's verdict with failed assertions.
 * Long episodes show the first 10 and last 4 turns with an elision marker.
 * -> dashboard/failed-traces.html
 */
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;");
const flash = JSON.parse(readFileSync(join(ROOT, "data", "flake", "w6-flash-validation.json"), "utf8"));
const w6 = (JSON.parse(readFileSync(join(ROOT, "world", "blobfish-wave6", "world.json"), "utf8"))).world
  ?? JSON.parse(readFileSync(join(ROOT, "world", "blobfish-wave6", "world.json"), "utf8"));
const taskById = Object.fromEntries(w6.tasks.map((t) => [t.task_id, t]));

const argv = process.argv.slice(2);
const opt = (n, d) => (argv.includes(n) ? argv[argv.indexOf(n) + 1] : d);
const FROM = Number(opt("--from", "0"));
const TO = Number(opt("--to", "999"));
const OUT = opt("--out", "failed-traces.html");
const failed = flash.tasks.filter((t) => t.class !== "pass").map((t) => t.taskId).sort().slice(FROM, TO);

function renderTrial(taskId) {
  const trial = JSON.parse(readFileSync(join(ROOT, "data", "flake", ".trials", `w6-flash-validation-${taskId}-t1.json`), "utf8"));
  if (!trial.log || !existsSync(trial.log)) return `<p>(no transcript for ${taskId})</p>`;
  const lines = readFileSync(trial.log, "utf8").trim().split("\n").map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);

  // group by turn
  const turns = new Map();
  let finalTxt = null, verify = null;
  for (const l of lines) {
    if (l.type === "final") { finalTxt = l.content; continue; }
    if (l.type === "verify") { verify = l.result; continue; }
    if (l.turn === undefined) continue;
    const t = turns.get(l.turn) ?? { thinking: null, tools: [] };
    if (l.type === "thinking") t.thinking = l.content;
    if (l.type === "tool") t.tools.push(l);
    turns.set(l.turn, t);
  }
  const turnNums = [...turns.keys()].sort((a, b) => a - b);
  const HEAD = 10, TAIL = 4;
  const shown = turnNums.length > HEAD + TAIL + 2
    ? [...turnNums.slice(0, HEAD), "…", ...turnNums.slice(-TAIL)]
    : turnNums;

  const task = taskById[taskId] ?? {};
  let html = `<div class="trace"><div class="thead"><span class="tid">${taskId}</span> · ${trial.toolCalls} tool calls · ${turnNums.length} turns · $${trial.costUsd} · <span class="fail">failed: ${(trial.failedConditions ?? []).join(", ")}</span></div>`;
  html += `<div class="prompt"><b>Task prompt:</b> ${esc((task.prompt ?? "").slice(0, 420))}</div>`;

  for (const tn of shown) {
    if (tn === "…") { html += `<div class="elide">… ${turnNums.length - HEAD - TAIL} turns elided (full transcript: ${esc(trial.log.split("/").pop())}) …</div>`; continue; }
    const t = turns.get(tn);
    html += `<div class="turn"><div class="tn">turn ${tn}</div>`;
    if (t.thinking) html += `<div class="think">🧠 ${esc(String(t.thinking).replace(/\s+/g, " ").slice(0, 300))}</div>`;
    for (const tc of t.tools) {
      html += `<div class="call">→ <b>${esc(tc.name)}</b>(${esc(JSON.stringify(tc.args).slice(0, 170))})</div>`;
      html += `<div class="obs">${esc(String(tc.result).replace(/\s+/g, " ").slice(0, 220))}</div>`;
    }
    html += `</div>`;
  }
  if (finalTxt) html += `<div class="final"><b>■ final answer:</b> ${esc(String(finalTxt).replace(/\s+/g, " ").slice(0, 400))}</div>`;

  // verifier verdict
  let v = null;
  try { v = typeof verify === "string" ? JSON.parse(verify) : verify; } catch { /* raw */ }
  if (v) {
    const failedAsserts = (v.assertions ?? []).filter((a) => a && a.passed === false);
    html += `<div class="verdict"><b>⚖ verifier:</b> ${v.passed ? "PASSED" : "FAILED"} — ${esc(String(v.explanation ?? "").slice(0, 200))}` +
      (failedAsserts.length ? `<ul>${failedAsserts.map((a) => `<li><span class="mono">${esc(a.name)}</span>: ${esc(String(a.details ?? a.detail ?? "").slice(0, 190))}</li>`).join("")}</ul>` : "") + `</div>`;
  }
  return html + `</div>`;
}

const body = failed.map(renderTrial).join("\n");

const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Failed traces, turn by turn — wave-6 flash validation</title>
<style>
body{font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;color:#0f172a;background:#f8fafc;margin:0;padding:28px;max-width:1120px;margin-inline:auto}
h1{font-size:23px;margin:0 0 4px}.sub{color:#64748b;font-size:12.5px;margin-bottom:18px}
.mono{font-family:ui-monospace,Menlo,monospace}
.trace{background:#fff;border:1px solid #e2e8f0;border-radius:10px;margin:22px 0;overflow:hidden}
.thead{background:#0f172a;color:#e2e8f0;padding:9px 16px;font-size:13px}
.tid{font-family:ui-monospace,Menlo,monospace;font-weight:700;font-size:14px}
.fail{color:#fda4af}
.prompt{padding:10px 16px;background:#f1f5f9;font-size:12.5px;border-bottom:1px solid #e2e8f0}
.turn{padding:8px 16px;border-bottom:1px dashed #e8edf3}
.tn{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#94a3b8;font-weight:700}
.think{color:#7c5bd6;font-size:12px;margin:3px 0;font-style:italic}
.call{font-family:ui-monospace,Menlo,monospace;font-size:12px;margin:4px 0 1px;color:#0f172a}
.obs{font-family:ui-monospace,Menlo,monospace;font-size:11.5px;color:#64748b;margin-left:14px}
.elide{text-align:center;color:#94a3b8;font-size:12px;padding:8px;background:#f8fafc}
.final{padding:10px 16px;background:#eff6ff;font-size:12.5px}
.verdict{padding:10px 16px;background:#fef2f2;font-size:12.5px}
.verdict ul{margin:6px 0 0;padding-left:18px}.verdict li{margin:2px 0;font-size:12px}
</style></head><body>
<h1>Failed traces, turn by turn</h1>
<div class="sub">Wave-6 world sbx_291042075d7547f4 · deepseek-v4-flash · trial 1 of each failed task · thinking → tool calls → observations → final → verifier verdict. Full transcripts: sim/logs/run-*.jsonl.</div>
${body}
</body></html>`;

writeFileSync(join(ROOT, "dashboard", OUT), html);
console.log(`${OUT}: ${failed.length} failed tasks rendered (${failed.join(", ")})`);
