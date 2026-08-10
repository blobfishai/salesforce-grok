#!/usr/bin/env node
/**
 * Arena runner — CRMArena-style Q&A tasks over the MCP world with answer matching.
 * Captures grok-4.5's THINKING (reasoning_content) every turn, the tool trace, the
 * final answer, and scores it against the computed ground truth (exact/fuzzy/set).
 *
 * Usage: node sim/run-arena.mjs [--task arena_case_routing] [--trials 1] [--label arena-l1]
 * Requires the arena world server: cd world/arena/package/<id> && PORT=8978 python3 server.py
 */
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { McpClient } from "./lib/mcp-client.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const config = JSON.parse(readFileSync(join(ROOT, "config", "world.config.json"), "utf8"));
const argv = process.argv.slice(2);
const opt = (n, d) => (argv.includes(n) ? argv[argv.indexOf(n) + 1] : d);
const TRIALS = Number(opt("--trials", "1"));
const LABEL = opt("--label", "arena");
const only = opt("--task", null);

const spec = JSON.parse(readFileSync(join(ROOT, "world", "arena", "arena-tasks.json"), "utf8"));
const tasks = spec.tasks.filter((t) => !only || t.id === only);

function loadEnv() {
  const env = { ...process.env };
  try { for (const line of readFileSync(join(ROOT, ".env"), "utf8").split("\n")) { const m = /^([A-Z0-9_]+)=(.*)$/.exec(line.trim()); if (m && !(m[1] in process.env)) env[m[1]] = m[2]; } } catch { /* none */ }
  return env;
}
const env = loadEnv();
const API_KEY = env.XAI_API_KEY;
const MODEL = env.XAI_MODEL ?? config.engine.model;

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

async function chat(messages, tools) {
  const res = await fetch(`${config.engine.baseUrl}/chat/completions`, {
    method: "POST", headers: { Authorization: `Bearer ${API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({ model: MODEL, messages, tools, tool_choice: "auto", max_tokens: 3000 }),
  });
  if (!res.ok) throw new Error(`xAI ${res.status}: ${await res.text()}`);
  return res.json();
}

async function runEpisode(task, trial) {
  const mcp = new McpClient(config.mcp.command, config.mcp.args, { cwd: ROOT });
  const init = await mcp.start();
  const HARNESS = new Set(["verify_task", "reset_session"]);
  const tools = (await mcp.listTools()).filter((t) => !HARNESS.has(t.name)).map((t) => ({ type: "function", function: { name: t.name, description: t.description, parameters: t.inputSchema } }));
  const messages = [
    { role: "system", content: `You are a CRM analyst at morgan_stanley_simulated (a fully synthetic sandbox). ${init.instructions ?? ""} Investigate with the available tools — consult the document store when a task references policies or notes. When you are confident, reply with exactly one line: FINAL ANSWER: <answer>` },
    { role: "user", content: task.prompt },
  ];
  const episode = { label: LABEL, level: spec.level, taskId: task.id, type: task.type, trial, prompt: task.prompt, gt: task.gt, metric: task.metric, docs: task.docs, steps: [], usage: { prompt: 0, completion: 0 } };
  let answer = null;
  for (let turn = 1; turn <= 16 && answer === null; turn++) {
    const r = await chat(messages, tools);
    episode.usage.prompt += r.usage?.prompt_tokens ?? 0;
    episode.usage.completion += r.usage?.completion_tokens ?? 0;
    const msg = r.choices[0].message;
    if (msg.reasoning_content) episode.steps.push({ k: "thinking", text: String(msg.reasoning_content).slice(0, 3000) });
    messages.push({ role: "assistant", content: msg.content ?? "", tool_calls: msg.tool_calls });
    if (msg.tool_calls?.length) {
      for (const tc of msg.tool_calls) {
        let args = {}; try { args = JSON.parse(tc.function.arguments || "{}"); } catch { /* raw */ }
        const res = await mcp.callTool(tc.function.name, args, 120000);
        episode.steps.push({ k: "tool", name: tc.function.name, args, result: String(res.text).slice(0, 900) });
        messages.push({ role: "tool", tool_call_id: tc.id, content: String(res.text).slice(0, 8000) });
      }
      continue;
    }
    const m = /FINAL ANSWER:\s*(.+)/is.exec(msg.content ?? "");
    answer = m ? m[1].trim() : (msg.content ?? "").trim();
    episode.steps.push({ k: "answer", text: answer });
  }
  mcp.close();
  episode.answer = answer;
  episode.passed = answer !== null && score(task.metric, task.gt, answer);
  episode.costUsd = +(((episode.usage.prompt / 1e6) * 2) + ((episode.usage.completion / 1e6) * 6)).toFixed(4);
  return episode;
}

mkdirSync(join(ROOT, "sim", "logs", "arena"), { recursive: true });
const results = [];
for (const task of tasks) {
  for (let trial = 1; trial <= TRIALS; trial++) {
    const ep = await runEpisode(task, trial).catch((e) => ({ taskId: task.id, trial, error: String(e.message), passed: false, steps: [], costUsd: 0 }));
    results.push(ep);
    writeFileSync(join(ROOT, "sim", "logs", "arena", `${LABEL}-${task.id}-t${trial}.json`), JSON.stringify(ep, null, 1));
    console.log(`${ep.passed ? "PASS " : "fail "} ${task.id} trial ${trial} | answer=${String(JSON.stringify(ep.answer ?? ep.error ?? null)).slice(0, 70)} | gt=${JSON.stringify(task.gt)} | $${ep.costUsd}`);
  }
}
const byTask = {};
for (const r of results) { const b = (byTask[r.taskId] ??= { p: 0, n: 0 }); b.n++; if (r.passed) b.p++; }
const summary = {
  label: LABEL, level: spec.level, model: MODEL, finishedAt: new Date().toISOString(),
  tasks: Object.entries(byTask).map(([id, b]) => ({ taskId: id, passes: b.p, trials: b.n, passRate: b.p / b.n, class: b.p === b.n ? "pass" : b.p === 0 ? "fail" : "FLAKY" })),
  costUsd: +results.reduce((a, r) => a + (r.costUsd ?? 0), 0).toFixed(2),
};
writeFileSync(join(ROOT, "data", "flake", `${LABEL}.json`), JSON.stringify(summary, null, 2));
console.log("\n=== " + LABEL + " ===");
for (const t of summary.tasks) console.log(`${t.class.padEnd(6)} ${t.passes}/${t.trials}  ${t.taskId}`);
console.log(`cost: $${summary.costUsd}`);
