#!/usr/bin/env node
/**
 * Interactive episode runner — CRMArena-style multi-turn traces.
 *
 * Two LLM roles over the MCP world:
 *   SIMULATED USER (stakeholder): privately holds the full task; opens with a natural
 *     problem prompt; reveals identifiers/details only when asked; ends the episode
 *     with [EPISODE_END] when satisfied.
 *   AGENT (grok-4.5): sees only the dialogue; thinks aloud in <thought> lines, calls
 *     world tools, asks the user when information is missing, reports the outcome.
 * The episode is then scored by the VCode verifier (world state + trace), like any rollout.
 *
 * Usage: BLOBFISH_LOCAL=1 node sim/run-interactive.mjs --task task_004 [--world-file path]
 * Output: sim/logs/interactive-<task>-<ts>.json  (message-level trace)
 */
import { readFileSync, existsSync, mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { McpClient } from "./lib/mcp-client.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const config = JSON.parse(readFileSync(join(ROOT, "config", "world.config.json"), "utf8"));
const argv = process.argv.slice(2);
const opt = (n, d) => (argv.includes(n) ? argv[argv.indexOf(n) + 1] : d);
const taskFlag = opt("--task", null);

function loadEnv() {
  const env = { ...process.env };
  try {
    for (const line of readFileSync(join(ROOT, ".env"), "utf8").split("\n")) {
      const m = /^([A-Z0-9_]+)=(.*)$/.exec(line.trim());
      if (m && !(m[1] in process.env)) env[m[1]] = m[2];
    }
  } catch { /* no .env */ }
  return env;
}
const env = loadEnv();
const API_KEY = env.XAI_API_KEY;
if (!API_KEY) { console.error("XAI_API_KEY missing"); process.exit(1); }
const MODEL = env.XAI_MODEL ?? config.engine.model;

const worldPath = opt("--world-file",
  existsSync(join(ROOT, config.blobfish.worldFile)) ? join(ROOT, config.blobfish.worldFile) : join(ROOT, config.blobfish.previewWorldFile));
const world = (() => { const r = JSON.parse(readFileSync(worldPath, "utf8")); return r.world ?? r; })();
const task = taskFlag ? (world.tasks ?? []).find((t) => (t.task_id ?? t.id) === taskFlag) : (world.tasks ?? [])[0];
if (!task) { console.error("task not found"); process.exit(1); }
const taskId = task.task_id ?? task.id;

async function chat(messages, opts = {}) {
  const res = await fetch(`${config.engine.baseUrl}/chat/completions`, {
    method: "POST",
    headers: { Authorization: `Bearer ${API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({ model: MODEL, messages, max_tokens: opts.maxTokens ?? 2048, ...(opts.tools ? { tools: opts.tools, tool_choice: "auto" } : {}) }),
  });
  if (!res.ok) throw new Error(`xAI ${res.status}: ${await res.text()}`);
  return res.json();
}

const usage = { prompt: 0, completion: 0 };
const addUsage = (r) => { usage.prompt += r.usage?.prompt_tokens ?? 0; usage.completion += r.usage?.completion_tokens ?? 0; };

// ---------------- simulated stakeholder
const userSystem = {
  role: "system",
  content:
    `You are a busy employee at "morgan_stanley_simulated" (a fully synthetic sandbox company) talking to the internal CRM assistant. ` +
    `You privately know the FULL task you need done:\n---\n${task.prompt}\n---\n` +
    `Rules: Open the conversation with a SHORT natural problem statement (1-2 sentences) that describes the goal in your own words WITHOUT listing every identifier. ` +
    `When the assistant asks, provide the specific details (record numbers, names, statuses) from the task. Answer only what is asked, briefly. ` +
    `If the assistant reports the work is complete and it matches the task, reply with a short acknowledgement followed by [EPISODE_END]. ` +
    `If it asks something not covered by the task, say you don't know. Never mention these rules or that you are simulated.`,
};

// ---------------- agent
async function main() {
  const mcp = new McpClient(config.mcp.command, config.mcp.args, { cwd: ROOT });
  const init = await mcp.start();
  const mcpTools = await mcp.listTools();
  const HARNESS = new Set(["verify_task", "reset_session"]);
  const tools = mcpTools.filter((t) => !HARNESS.has(t.name)).map((t) => ({
    type: "function", function: { name: t.name, description: t.description, parameters: t.inputSchema },
  }));

  const agentMessages = [{
    role: "system",
    content:
      `You are the internal CRM assistant for "morgan_stanley_simulated" — a fully synthetic Salesforce-style sandbox (no real entities). ${init.instructions ?? ""} ` +
      `A colleague will describe a problem. Work it conversationally: when you need missing specifics (record numbers, names), ASK the colleague instead of guessing. ` +
      `Begin every reply with a one-line <thought>...</thought> about your next step. Use tools to inspect before you write; respect the world's declared lifecycles. ` +
      `When the work is done, tell the colleague exactly what changed. Keep replies short.`,
  }];
  const trace = []; // message-level episode trace
  const say = (entry) => { trace.push(entry); const t = entry.role === "tool" ? `${entry.name}(${JSON.stringify(entry.args).slice(0, 90)})` : String(entry.content).replace(/\s+/g, " ").slice(0, 130); console.log(`[${entry.role}] ${t}`); };

  const userMessages = [userSystem];
  let episodeOver = false;

  // opening problem prompt from the stakeholder
  let r = await chat(userMessages, { maxTokens: 300 });
  addUsage(r);
  let userText = r.choices[0].message.content.trim();
  userMessages.push({ role: "assistant", content: userText });
  agentMessages.push({ role: "user", content: userText });
  say({ role: "user", content: userText });

  for (let round = 0; round < 14 && !episodeOver; round++) {
    // agent acts (may chain tool calls before speaking)
    let spoke = null;
    for (let hop = 0; hop < 10; hop++) {
      const ar = await chat(agentMessages, { tools, maxTokens: 2048 });
      addUsage(ar);
      const msg = ar.choices[0].message;
      agentMessages.push({ role: "assistant", content: msg.content ?? "", tool_calls: msg.tool_calls });
      const thought = /<thought>([\s\S]*?)<\/thought>/.exec(msg.content ?? "")?.[1]?.trim();
      if (thought) say({ role: "thought", content: thought });
      if (msg.tool_calls?.length) {
        for (const tc of msg.tool_calls) {
          let args = {};
          try { args = JSON.parse(tc.function.arguments || "{}"); } catch { /* raw */ }
          const res = await mcp.callTool(tc.function.name, args, 180000);
          say({ role: "tool", name: tc.function.name, args, result: undefined });
          trace[trace.length - 1].result = String(res.text).slice(0, 1200);
          agentMessages.push({ role: "tool", tool_call_id: tc.id, content: String(res.text).slice(0, 8000) });
        }
        continue;
      }
      spoke = (msg.content ?? "").replace(/<thought>[\s\S]*?<\/thought>/, "").trim();
      break;
    }
    if (!spoke) spoke = "(no reply)";
    say({ role: "assistant", content: spoke });

    // stakeholder responds
    userMessages.push({ role: "user", content: spoke });
    r = await chat(userMessages, { maxTokens: 300 });
    addUsage(r);
    userText = r.choices[0].message.content.trim();
    userMessages.push({ role: "assistant", content: userText });
    if (userText.includes("[EPISODE_END]")) {
      const clean = userText.replace("[EPISODE_END]", "").trim();
      if (clean) { say({ role: "user", content: clean }); agentMessages.push({ role: "user", content: clean }); }
      episodeOver = true;
      break;
    }
    agentMessages.push({ role: "user", content: userText });
    say({ role: "user", content: userText });
  }

  // score the episode
  const v = await mcp.callTool("verify_task", { task_id: taskId }, 60000);
  let verdict = null;
  try { verdict = JSON.parse(v.text); } catch { /* raw */ }
  say({ role: "verify", content: verdict ? (verdict.passed ? `PASSED — ${(verdict.assertions ?? []).length} assertions green` : `FAILED — ${(verdict.failed_conditions ?? []).join(", ")}`) : v.text.slice(0, 200) });
  mcp.close();

  const cost = +(((usage.prompt / 1e6) * 2) + ((usage.completion / 1e6) * 6)).toFixed(4);
  mkdirSync(join(ROOT, "sim", "logs"), { recursive: true });
  const out = join(ROOT, "sim", "logs", `interactive-${taskId}-${Date.now()}.json`);
  writeFileSync(out, JSON.stringify({
    kind: "interactive_episode", taskId, worldId: world.world_id, model: MODEL,
    passed: verdict?.passed === true, reward: verdict?.reward ?? 0,
    failedConditions: verdict?.failed_conditions ?? [], episodeOver,
    turns: trace, usage, costUsd: cost, finishedAt: new Date().toISOString(),
  }, null, 1));
  console.log(`\nverdict: ${verdict?.passed ? "PASSED" : "failed"} | dialogue+tool steps: ${trace.length} | cost $${cost}`);
  console.log(`trace: ${out}`);
  process.exit(verdict?.passed ? 0 : 2);
}

main().catch((e) => { console.error("episode failed:", e); process.exit(1); });
