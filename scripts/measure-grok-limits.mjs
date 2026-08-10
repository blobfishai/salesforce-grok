#!/usr/bin/env node
/**
 * MEASURED grok-4.5 limits — live probes against api.x.ai, not doc regurgitation.
 * Emits JSON to stdout; docs/GROK-4.5-LIMITS.md is rewritten from these results.
 * Probes: header capture, latency, context acceptance at ~150k/~215k/~495k/~520k
 * tokens (calibrated by a token-ratio probe), output-cap probe, 500-tool probe.
 * Est. spend: ~$3-4 (the big-context probes are the cost).
 */
import { readFileSync } from "node:fs";

const env = Object.fromEntries(readFileSync(new URL("../.env", import.meta.url), "utf8")
  .split("\n").filter((l) => /^[A-Z0-9_]+=/.test(l)).map((l) => [l.slice(0, l.indexOf("=")), l.slice(l.indexOf("=") + 1)]));
const KEY = env.XAI_API_KEY;
const MODEL = "grok-4.5";

async function call(body, { timeoutMs = 300000 } = {}) {
  const t0 = Date.now();
  const res = await fetch("https://api.x.ai/v1/chat/completions", {
    method: "POST",
    headers: { Authorization: `Bearer ${KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({ model: MODEL, ...body }),
    signal: AbortSignal.timeout(timeoutMs),
  });
  const ms = Date.now() - t0;
  const headers = {};
  for (const [k, v] of res.headers) if (/ratelimit|request-id|region/i.test(k)) headers[k] = v;
  let json = null, text = "";
  try { text = await res.text(); json = JSON.parse(text); } catch { /* raw */ }
  return { status: res.status, ms, headers, usage: json?.usage ?? null, error: json?.error ?? (res.ok ? null : text.slice(0, 300)), id: json?.id ?? null };
}

const out = { model: MODEL, measuredAt: new Date().toISOString(), probes: {} };
const msg = (content) => ({ messages: [{ role: "user", content }], max_tokens: 16 });

// 1. baseline: headers + latency + token-ratio calibration
const calibN = 10000;
const calib = await call(msg("Reply 'ok'. " + "ok ".repeat(calibN)));
out.probes.baseline = calib;
const ratio = calib.usage ? calib.usage.prompt_tokens / calibN : 1; // tokens per "ok " unit
out.tokenRatio = +ratio.toFixed(4);
const units = (targetTokens) => Math.floor(targetTokens / ratio);

// 2-5. context acceptance ladder
for (const target of [150000, 215000, 495000, 520000]) {
  const r = await call(msg("Reply 'ok'. " + "ok ".repeat(units(target))), { timeoutMs: 420000 });
  out.probes[`ctx_${target}`] = { status: r.status, ms: r.ms, prompt_tokens: r.usage?.prompt_tokens ?? null, error: r.error ? String(r.error?.message ?? r.error).slice(0, 220) : null };
  console.error(`ctx ${target}: status=${r.status} tokens=${r.usage?.prompt_tokens ?? "-"} ms=${r.ms}`);
}

// 6. output cap probe: absurd max_tokens on tiny prompt
const cap = await call({ messages: [{ role: "user", content: "Say hi." }], max_tokens: 300000 });
out.probes.output_cap = { status: cap.status, error: cap.error ? String(cap.error?.message ?? cap.error).slice(0, 260) : null, usage: cap.usage };

// 7. tool-count probe: 500 dummy tools
const tools = Array.from({ length: 500 }, (_, i) => ({ type: "function", function: { name: `dummy_tool_${i}`, description: `dummy ${i}`, parameters: { type: "object", properties: { x: { type: "string" } } } } }));
const tp = await call({ messages: [{ role: "user", content: "Just reply 'ok', do not call tools." }], max_tokens: 16, tools });
out.probes.tools_500 = { status: tp.status, ms: tp.ms, prompt_tokens: tp.usage?.prompt_tokens ?? null, error: tp.error ? String(tp.error?.message ?? tp.error).slice(0, 200) : null };

// 8. small-call latency distribution (5 samples)
const lat = [];
for (let i = 0; i < 5; i++) lat.push((await call(msg("Reply 'ok'."))).ms);
out.probes.latency_small_ms = lat;

console.log(JSON.stringify(out, null, 1));
