#!/usr/bin/env node
/**
 * Simulation runner: drives the Morgan Stanley (SIMULATED) CRM world with a grok-4.5 agent.
 *
 * Modes:
 *   node sim/run-simulation.mjs [--task <task_id>]   blobfish mode (default): runs a task from
 *                                                    the blobfish world via the MCP bridge and
 *                                                    scores it with the VCode verifier.
 *   node sim/run-simulation.mjs --local [scenario]   local mode: runs the scripted quote-to-cash
 *                                                    scenario against the local mock CRM MCP.
 */
import { readFileSync, existsSync, mkdirSync, appendFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { McpClient } from "./lib/mcp-client.mjs";
import { resolveModel, costUsd, ToolNameCodec, mangleTools, chat as llmChat } from "./lib/llm-client.mjs";
import { WorldUpstream } from "../mcp/lib/world-upstream.mjs";
import { resolveTaskSeedPath, sessionDbPath, applyTaskSeed, dumpInitialState, bundleTables } from "./lib/task-seed.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const config = JSON.parse(readFileSync(join(ROOT, "config", "world.config.json"), "utf8"));

const argv = process.argv.slice(2);
const LOCAL = argv.includes("--local");
const taskFlag = argv.includes("--task") ? argv[argv.indexOf("--task") + 1] : null;
const jsonOutFlag = argv.includes("--json-out") ? argv[argv.indexOf("--json-out") + 1] : null;
const worldFileFlag = argv.includes("--world-file") ? argv[argv.indexOf("--world-file") + 1] : null;
const modelFlag = argv.includes("--model") ? argv[argv.indexOf("--model") + 1] : null;
const MULTI = argv.includes("--multi-server") || process.env.SIM_MULTI_SERVER === "1";
const APPLY_SEED = argv.includes("--apply-task-seed") || process.env.SIM_APPLY_TASK_SEED === "1";

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
let MODEL_INFO;
try {
  MODEL_INFO = resolveModel(ROOT, modelFlag ?? env.SIM_MODEL ?? env.XAI_MODEL ?? config.engine.model, env);
} catch (e) {
  console.error(String(e.message));
  process.exit(1);
}
const MODEL = MODEL_INFO.id;

const LOG_DIR = join(ROOT, "sim", "logs");
mkdirSync(LOG_DIR, { recursive: true });
const LOG = join(LOG_DIR, `run-${new Date().toISOString().replace(/[:.]/g, "-")}.jsonl`);
const log = (obj) => appendFileSync(LOG, JSON.stringify(obj) + "\n");

const TRUNCATE = 8000;
const clip = (s) => (s.length > TRUNCATE ? s.slice(0, TRUNCATE) + `\n…[truncated ${s.length - TRUNCATE} chars]` : s);

const chat = (messages, tools) => llmChat(MODEL_INFO, messages, tools, { maxTokens: config.engine.maxCompletionTokens });

/** Agentic loop: model <-> MCP tools until a final (non-tool) answer or turn cap.
 *  The cap is blobfish-style reference-relative when opts.maxTurns is supplied:
 *  a budget derived from the task's own reference walk length, so long-horizon
 *  tasks get proportionally long budgets and the cap never masquerades as a
 *  capability verdict. */
async function runAgent(mcp, llmTools, messages, opts = {}) {
  const maxTurns = opts.maxTurns ?? config.engine.maxAgentTurns;
  const usage = { prompt: 0, completion: 0, total: 0 };
  let toolCallCount = 0;
  let finalText = null;
  const guardTokens = Math.floor(MODEL_INFO.contextWindowTokens * config.engine.contextGuardRatio);

  for (let turn = 1; turn <= maxTurns; turn++) {
    const resp = await chat(messages, llmTools);
    const u = resp.usage ?? {};
    usage.prompt += u.prompt_tokens ?? 0;
    usage.completion += u.completion_tokens ?? 0;
    usage.total += u.total_tokens ?? 0;
    log({ type: "completion", turn, model: resp.model, usage: u });

    if ((u.prompt_tokens ?? 0) > guardTokens) {
      console.warn(`! Context guard: prompt ${u.prompt_tokens} > ${guardTokens} tokens (90% of ${MODEL_INFO.contextWindowTokens}); trimming oldest tool output`);
      const oldTool = messages.find((m) => m.role === "tool" && m.content !== "[trimmed]");
      if (oldTool) oldTool.content = "[trimmed]";
    }

    const msg = resp.choices[0].message;
    if (msg.reasoning_content) log({ type: "thinking", turn, content: String(msg.reasoning_content).slice(0, 4000) });
    messages.push({ role: "assistant", content: msg.content ?? "", tool_calls: msg.tool_calls });

    if (msg.tool_calls?.length) {
      for (const tc of msg.tool_calls) {
        let args = {};
        try { args = JSON.parse(tc.function.arguments || "{}"); } catch { /* leave empty */ }
        // Route: multi-server episodes map vendor__tool -> that vendor's client;
        // single-bridge episodes reverse the codec mangling.
        const target = opts.route
          ? (opts.route(tc.function.name) ?? { client: mcp, name: tc.function.name })
          : { client: mcp, name: opts.codec ? opts.codec.mcp(tc.function.name) : tc.function.name };
        // Multi-server logs the vendor__tool surface name; single-bridge keeps
        // the upstream dotted name (existing log/report format).
        const mcpName = opts.route ? tc.function.name : target.name;
        let resultText;
        try {
          const r = await target.client.callTool(target.name, args, 180000); // world sub-agent tools can be slow
          resultText = r.text;
          toolCallCount++;
          console.log(`[turn ${turn}] ${mcpName}(${clip(JSON.stringify(args)).slice(0, 200)}) -> ${r.ok ? "ok" : "ERROR"}`);
        } catch (e) {
          resultText = `ERROR: ${e.message}`;
          console.log(`[turn ${turn}] ${mcpName} -> transport error: ${e.message}`);
        }
        log({ type: "tool", turn, name: mcpName, args, result: resultText });
        messages.push({ role: "tool", tool_call_id: tc.id, content: clip(resultText) });
      }
      continue;
    }

    finalText = msg.content;
    console.log(`\n=== Agent final answer (turn ${turn}) ===\n${finalText}\n`);
    log({ type: "final", turn, content: finalText });
    break;
  }
  return { usage, toolCallCount, finalText };
}

function printStats(usage, toolCallCount) {
  const cost = costUsd(MODEL_INFO, usage); // per-model $/M from config/model-roster.json
  console.log(`=== Run stats ===`);
  console.log(`Model: ${MODEL} | tool calls: ${toolCallCount}`);
  console.log(`Tokens: prompt ${usage.prompt.toLocaleString()}, completion ${usage.completion.toLocaleString()} (context limit ${MODEL_INFO.contextWindowTokens.toLocaleString()})`);
  console.log(`Approx cost: ${cost === null ? "n/a (no pricing)" : "$" + cost.toFixed(4)} | transcript: ${LOG}`);
}

const taskField = (t, ...names) => names.map((n) => t[n]).find((v) => v !== undefined && v !== null);

async function mainBlobfish() {
  const worldPath = worldFileFlag
    ? worldFileFlag
    : existsSync(join(ROOT, config.blobfish.worldFile))
      ? join(ROOT, config.blobfish.worldFile)
      : join(ROOT, config.blobfish.previewWorldFile);
  if (!existsSync(worldPath)) {
    console.error(`No blobfish world file found (${config.blobfish.worldFile}). Run the generation job first, or use --local.`);
    process.exit(1);
  }
  const raw = JSON.parse(readFileSync(worldPath, "utf8"));
  const world = raw.world ?? raw;
  const tasks = world.tasks ?? [];
  if (!tasks.length) { console.error("World has no tasks."); process.exit(1); }

  const task = taskFlag ? tasks.find((t) => taskField(t, "task_id", "id") === taskFlag) : tasks[0];
  if (!task) { console.error(`Task '${taskFlag}' not found. Available: ${tasks.map((t) => taskField(t, "task_id", "id")).join(", ")}`); process.exit(1); }
  const taskId = taskField(task, "task_id", "id");
  const taskPrompt = taskField(task, "prompt", "instruction", "description", "goal") ?? JSON.stringify(task);
  const persona = taskField(task, "persona", "role");

  console.log(`=== Simulation (blobfish world): task ${taskId} ===`);
  console.log(`World file: ${worldPath}`);
  console.log(`Engine: ${MODEL} (context ${config.engine.contextWindowTokens.toLocaleString()} tokens)`);
  if (persona) console.log(`Persona: ${persona}`);

  // ---- MCP topology: one mega-bridge (legacy) or one server per vendor (realistic)
  let mcp, codec = null, route = null, llmTools, harnessClient, cleanupEpisode = async () => {};
  let envInstructions = "";
  if (MULTI) {
    const registry = JSON.parse(readFileSync(join(ROOT, "config", "mcp-servers.json"), "utf8"));
    const vendors = Object.keys(registry.vendors);
    // Runner owns the shared session + merged trace for the episode.
    const epDir = join(ROOT, "sim", "logs", ".mcp-episodes", `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`);
    mkdirSync(epDir, { recursive: true });
    const sessionFile = join(epDir, "session.json");
    const traceFile = join(epDir, "trace.jsonl");
    const up = new WorldUpstream({ clientName: "sim-runner" });
    await up.attachSession();
    writeFileSync(sessionFile, JSON.stringify({ session_id: up.session }));
    writeFileSync(traceFile, "");
    const childEnv = { BLOBFISH_SESSION_FILE: sessionFile, BLOBFISH_TRACE_FILE: traceFile };
    if (APPLY_SEED) childEnv.BLOBFISH_INITIAL_STATE_FILE = join(epDir, "initial-state.json");

    const clients = {};
    await Promise.all(vendors.map(async (v) => {
      const c = new McpClient("node", ["mcp/vendor-server.mjs", "--vendor", v], { cwd: ROOT, env: childEnv });
      await c.start();
      clients[v] = c;
    }));
    harnessClient = new McpClient("node", ["mcp/harness-server.mjs"], { cwd: ROOT, env: childEnv, verbose: true });
    await harnessClient.start();

    // Task-level fixtures: layer this task's seed bundle (rows, documents with
    // bodies) into the episode's copy-on-write session DB before the agent runs.
    if (APPLY_SEED) {
      const seedPath = resolveTaskSeedPath(ROOT, worldPath, taskId);
      if (seedPath && up.LOCAL) {
        try {
          const dbPath = sessionDbPath(ROOT, worldPath.startsWith(ROOT) ? worldPath.slice(ROOT.length + 1) : worldPath, world.world_id, up.session);
          const applied = applyTaskSeed(seedPath, dbPath);
          // Post-seed snapshot of the seed-touched tables = the per-table
          // verification baseline (fixtures are initial state, not agent
          // writes). Harness reads this path at verify time.
          dumpInitialState(dbPath, join(epDir, "initial-state.json"), bundleTables(seedPath));
          console.log(`Task seed applied: ${JSON.stringify(applied)} from ${seedPath.split("/").slice(-3).join("/")}`);
          log({ type: "task_seed", taskId, seedPath, applied });
        } catch (e) {
          console.warn(`! task seed skipped: ${e.message}`);
        }
      } else if (!seedPath) {
        console.warn(`! no seed bundle for ${taskId} (bench/tasks/*)`);
      }
    }

    const routing = new Map();
    llmTools = [];
    for (const v of vendors) {
      for (const t of await clients[v].listTools()) {
        const surface = `${v.replace(/-/g, "_")}__${t.name}`;
        routing.set(surface, { client: clients[v], name: t.name });
        llmTools.push({ type: "function", function: { name: surface, description: `[${registry.vendors[v].product}] ${t.description}`, parameters: t.inputSchema } });
      }
    }
    route = (n) => routing.get(n);
    mcp = harnessClient; // verify/reset go through the harness server
    envInstructions = `Your company runs ${vendors.length} connected systems, each exposed as its own MCP server: ` +
      vendors.map((v) => `${v} (${registry.vendors[v].product})`).join(", ") +
      `. Tool names are prefixed with the server they belong to.`;
    console.log(`MCP topology: ${vendors.length} vendor servers + harness (shared session ${up.session})`);
    console.log(`World tools exposed to agent: ${llmTools.length} across ${vendors.length} servers\n`);
    cleanupEpisode = async () => {
      for (const c of Object.values(clients)) c.close();
      harnessClient.close();
      await new Promise((r) => setTimeout(r, 300));
      await up.releaseSession();
    };
  } else {
    mcp = new McpClient(config.mcp.command, config.mcp.args, { cwd: ROOT, verbose: true });
    const init = await mcp.start();
    envInstructions = init.instructions ?? "";
    console.log(`MCP connected: ${init.serverInfo.name}`);
    const mcpTools = await mcp.listTools();
    const HARNESS = new Set(["verify_task", "reset_session"]);
    const agentTools = mcpTools.filter((t) => !HARNESS.has(t.name));
    codec = new ToolNameCodec(agentTools.map((t) => t.name));
    llmTools = mangleTools(agentTools, codec);
    console.log(`World tools exposed to agent: ${llmTools.length}\n`);
  }

  const messages = [
    {
      role: "system",
      content:
        `You are an agent operating inside a fully synthetic Salesforce-CRM-style simulation world ` +
        `("Morgan Stanley (SIMULATED)" scenario — no real entities). ${envInstructions} ` +
        (persona ? `You act in the persona: ${persona}. ` : "") +
        `Complete the task using the available tools. Be precise with ids and values. ` +
        `When the task is complete, reply with a final answer and no further tool calls.`,
    },
    { role: "user", content: typeof taskPrompt === "string" ? taskPrompt : JSON.stringify(taskPrompt) },
  ];

  // Reference-relative budget (blobfish calibrationBudgetCeiling-style): scale
  // the turn cap from the task's own reference walk length.
  const refWalk = Array.isArray(task.walk) ? task.walk.length : 0;
  const maxTurns = Math.max(config.engine.maxAgentTurns, refWalk * 3 + 6);
  const { usage, toolCallCount, finalText } = await runAgent(mcp, llmTools, messages, { maxTurns, codec, route });
  printStats(usage, toolCallCount);

  console.log(`\n=== Verifying task ${taskId} via blobfish VCode ===`);
  // Answer-graded tasks (the CRMArena clones) score the agent's final reply, so
  // it must reach the verifier as the trace's _final_answer step.
  const v = await mcp.callTool("verify_task", { task_id: taskId, final_answer: finalText ?? null }, 60000);
  console.log(v.text);
  log({ type: "verify", taskId, result: v.text });
  if (MULTI) await cleanupEpisode(); else mcp.close();
  const passed = v.data?.passed === true;
  console.log(passed ? "RESULT: PASSED" : "RESULT: NOT PASSED");
  if (jsonOutFlag) {
    writeFileSync(jsonOutFlag, JSON.stringify({
      mode: "blobfish",
      taskId,
      model: MODEL,
      passed,
      reward: v.data?.reward ?? 0,
      failedConditions: v.data?.failed_conditions ?? [],
      toolCalls: toolCallCount,
      usage,
      costUsd: costUsd(MODEL_INFO, usage) ?? 0,
      log: LOG,
      finishedAt: new Date().toISOString(),
    }, null, 2));
  }
  return passed ? 0 : 2;
}

async function mainLocal() {
  const scenarioPath = argv.find((a) => a.endsWith(".json")) ?? join(ROOT, "sim", "scenarios", "quote-to-cash.json");
  const scenario = JSON.parse(readFileSync(scenarioPath, "utf8"));
  console.log(`=== Simulation (local mock): ${scenario.name} ===`);
  console.log(`Engine: ${MODEL} (context ${config.engine.contextWindowTokens.toLocaleString()} tokens)`);

  const mcp = new McpClient(config.mcpLocalFallback.command, config.mcpLocalFallback.args, { cwd: ROOT });
  const init = await mcp.start();
  console.log(`MCP connected: ${init.serverInfo.name} v${init.serverInfo.version}`);
  const mcpTools = await mcp.listTools();
  const codec = new ToolNameCodec(mcpTools.map((t) => t.name));
  const llmTools = mangleTools(mcpTools, codec);
  console.log(`Tools exposed to agent: ${llmTools.length}\n`);

  const messages = [
    {
      role: "system",
      content:
        `You are a revenue-operations agent inside "${config.world}", a fully simulated Salesforce-style CRM for a fictional ` +
        `investment bank (Morgan Stanley (SIMULATED) — synthetic data only). ${init.instructions ?? ""} ` +
        `You may act as internal approver roles (Deal Desk, Compliance Officer, Finance) when processing approvals — this is a sandbox. ` +
        `Use tools precisely with exact ids. When the goal is complete, reply with a final summary and no further tool calls.`,
    },
    { role: "user", content: scenario.goal },
  ];

  const { usage, toolCallCount } = await runAgent(mcp, llmTools, messages, { codec });
  printStats(usage, toolCallCount);

  const finalState = await mcp.callTool("get_flow_state", { opportunityId: scenario.opportunityId });
  console.log(`Final flow stage for ${scenario.opportunityId}: ${finalState.data?.flowStage}`);
  mcp.close();
  return finalState.data?.flowStage === "Order activated" ? 0 : 2;
}

(LOCAL ? mainLocal() : mainBlobfish())
  .then((code) => process.exit(code))
  .catch((e) => { console.error("Simulation failed:", e); process.exit(1); });
