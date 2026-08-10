/**
 * Shared multi-provider LLM client for all runners.
 *
 * Every provider in the roster speaks the OpenAI /chat/completions dialect
 * (xAI natively; Anthropic via its OpenAI-compat endpoint; DeepSeek natively),
 * so one code path covers the whole leaderboard roster.
 *
 * Anthropic and DeepSeek reject tool names outside ^[a-zA-Z0-9_-]+$, while
 * blobfish MCP names are dotted (salesforce.list_lead) — mangleTools/ToolNameCodec
 * translate at the API boundary and reverse-map on each tool call.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";

export function loadRoster(ROOT) {
  return JSON.parse(readFileSync(join(ROOT, "config", "model-roster.json"), "utf8"));
}

/** Resolve a model id to { id, provider, baseUrl, apiKey, pricing, contextWindowTokens, ... }. */
export function resolveModel(ROOT, modelId, env) {
  const roster = loadRoster(ROOT);
  const id = modelId ?? roster.defaultModel;
  const m = roster.models[id];
  if (!m) throw new Error(`Model '${id}' not in config/model-roster.json (have: ${Object.keys(roster.models).join(", ")})`);
  const p = roster.providers[m.provider];
  if (!p) throw new Error(`Provider '${m.provider}' not in roster.providers`);
  const apiKey = env[p.envKey];
  if (!apiKey) throw new Error(`${p.envKey} missing from environment/.env (needed for model '${id}')`);
  return {
    id,
    provider: m.provider,
    baseUrl: p.baseUrl,
    apiKey,
    pricing: m.pricing ?? null,
    contextWindowTokens: m.contextWindowTokens ?? 128000,
    maxCompletionTokens: m.maxCompletionTokens ?? 4096,
    displayName: m.displayName ?? id,
  };
}

export function costUsd(model, usage) {
  if (!model.pricing) return null;
  return +(((usage.prompt / 1e6) * model.pricing.input) + ((usage.completion / 1e6) * model.pricing.output)).toFixed(4);
}

/** Bidirectional tool-name codec: dotted MCP names <-> API-safe names. */
export class ToolNameCodec {
  constructor(mcpNames) {
    this.toApi = new Map();
    this.toMcp = new Map();
    for (const name of mcpNames) {
      const api = name.replace(/[^a-zA-Z0-9_-]/g, "__");
      this.toApi.set(name, api);
      this.toMcp.set(api, name);
    }
  }
  api(mcpName) { return this.toApi.get(mcpName) ?? mcpName; }
  mcp(apiName) { return this.toMcp.get(apiName) ?? apiName; }
}

/** Build OpenAI-style tool specs from MCP tool list, with API-safe names. */
export function mangleTools(mcpTools, codec) {
  return mcpTools.map((t) => ({
    type: "function",
    function: { name: codec.api(t.name), description: t.description, parameters: t.inputSchema },
  }));
}

const RETRYABLE = new Set([408, 409, 429, 500, 502, 503, 504, 529]);

/** One chat completion with retry/backoff. Returns the parsed response body. */
export async function chat(model, messages, tools, opts = {}) {
  const maxTokens = opts.maxTokens ?? model.maxCompletionTokens;
  const retries = opts.retries ?? 4;
  const body = JSON.stringify({
    model: model.id,
    messages,
    ...(tools?.length ? { tools, tool_choice: "auto" } : {}),
    max_tokens: maxTokens,
  });
  let lastErr;
  for (let attempt = 0; attempt <= retries; attempt++) {
    if (attempt > 0) await new Promise((r) => setTimeout(r, Math.min(30000, 1500 * 2 ** attempt) + Math.random() * 1000));
    try {
      const res = await fetch(`${model.baseUrl}/chat/completions`, {
        method: "POST",
        headers: { Authorization: `Bearer ${model.apiKey}`, "Content-Type": "application/json" },
        body,
        signal: AbortSignal.timeout(opts.timeoutMs ?? 300000),
      });
      if (!res.ok) {
        const text = await res.text();
        if (RETRYABLE.has(res.status) && attempt < retries) { lastErr = new Error(`${model.provider} ${res.status}: ${text.slice(0, 300)}`); continue; }
        throw new Error(`${model.provider} API ${res.status}: ${text.slice(0, 2000)}`);
      }
      return await res.json();
    } catch (e) {
      if (e.name === "TimeoutError" || e.name === "AbortError" || /fetch failed|ECONNRESET|ETIMEDOUT|socket/i.test(String(e.message))) {
        lastErr = e;
        if (attempt < retries) continue;
      }
      throw e;
    }
  }
  throw lastErr ?? new Error("chat: retries exhausted");
}
