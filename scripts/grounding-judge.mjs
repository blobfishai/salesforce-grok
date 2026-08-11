#!/usr/bin/env node
/**
 * Grounding judge — verify that every proposed task/tool/table/chaos-pattern is
 * actually supported by the source it cites in the research corpus.
 *
 *   node scripts/grounding-judge.mjs --input bench/proposals/wave9.jsonl \
 *        --out bench/reports/wave9-grounding.json [--model grok-4.5]
 *
 * Contract (docs/GROUNDING-JUDGE.md): the judge sees ONLY the claim and the
 * excerpt resolved from the citation. It must return a verdict plus a verbatim
 * quote from the excerpt; a verdict without a locatable quote is downgraded to
 * UNSUPPORTED, which catches a judge that rubber-stamps as well as an author who
 * cites something that does not say what they think it says.
 */
import { readFileSync, writeFileSync, existsSync, mkdirSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { resolveModel, chat, costUsd } from "../sim/lib/llm-client.mjs";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const MAX_EXCERPT = 6000; // characters shown to the judge per citation

function loadEnv() {
  const env = { ...process.env };
  const p = join(ROOT, ".env");
  if (existsSync(p)) {
    for (const line of readFileSync(p, "utf8").split("\n")) {
      const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
      if (m && !env[m[1]]) env[m[1]] = m[2].replace(/^["']|["']$/g, "");
    }
  }
  return env;
}

function args() {
  const a = process.argv.slice(2);
  const get = (flag, dflt) => {
    const i = a.indexOf(flag);
    return i >= 0 && a[i + 1] ? a[i + 1] : dflt;
  };
  return {
    input: get("--input"),
    out: get("--out", join(ROOT, "bench", "reports", "grounding.json")),
    model: get("--model", null),
  };
}

/**
 * Resolve a citation to an excerpt. Citations are repo-relative paths, optionally
 * with a `#hint` fragment used to pick the most relevant window of a large file.
 */
function resolveCitation(citation) {
  const [rawPath, hint] = citation.split("#");
  const path = join(ROOT, rawPath.trim());
  if (!existsSync(path)) return { ok: false, excerpt: "", note: `citation does not resolve: ${rawPath}` };
  if (statSync(path).isDirectory()) return { ok: false, excerpt: "", note: `citation is a directory: ${rawPath}` };

  const text = readFileSync(path, "utf8");
  if (text.length <= MAX_EXCERPT) return { ok: true, excerpt: text, note: "whole file" };

  if (hint) {
    // Score paragraphs by hint-term overlap and keep the best contiguous window.
    const terms = hint.toLowerCase().split(/[^a-z0-9]+/).filter((t) => t.length > 2);
    const paras = text.split(/\n{2,}/);
    const scored = paras.map((p, i) => {
      const low = p.toLowerCase();
      return { i, score: terms.reduce((s, t) => s + (low.includes(t) ? 1 : 0), 0) };
    }).sort((a, b) => b.score - a.score);
    if (scored[0]?.score > 0) {
      const center = scored[0].i;
      let out = "";
      for (let i = Math.max(0, center - 2); i < paras.length && out.length < MAX_EXCERPT; i++) out += paras[i] + "\n\n";
      return { ok: true, excerpt: out, note: `window around "${hint}"` };
    }
  }
  return { ok: true, excerpt: text.slice(0, MAX_EXCERPT), note: "head of file (truncated)" };
}

const SYSTEM = `You are a grounding auditor for an agent-benchmark world.

You are given ONE claim and the excerpt(s) it cites. Decide whether the excerpt
actually supports the claim.

Verdicts:
- GROUNDED: the excerpt states or directly implies the claim.
- PARTIAL: the excerpt supports the general shape but not the specific details
  (exact numbers, thresholds, field names) asserted in the claim.
- UNSUPPORTED: the excerpt does not support the claim, or is about something else.

Rules:
- Judge ONLY against the excerpt shown. Your own knowledge of CRMs is irrelevant
  and must not be used as support.
- You MUST include "quote": a verbatim span copied from the excerpt that carries
  the support. For UNSUPPORTED, set quote to "".
- Be strict. Plausible-but-absent is UNSUPPORTED, not PARTIAL.

Reply with JSON only:
{"verdict":"GROUNDED|PARTIAL|UNSUPPORTED","quote":"...","unsupported_specifics":["..."],"reason":"one sentence"}`;

function parseJson(text) {
  const fenced = text.match(/```(?:json)?\s*([\s\S]*?)```/);
  const body = fenced ? fenced[1] : text;
  const start = body.indexOf("{");
  const end = body.lastIndexOf("}");
  if (start < 0 || end < 0) return null;
  try { return JSON.parse(body.slice(start, end + 1)); } catch { return null; }
}

/** Normalize whitespace so a quote that differs only in wrapping still matches. */
const flat = (s) => s.replace(/\s+/g, " ").trim().toLowerCase();

async function judge(model, proposal) {
  const cites = proposal.citations ?? [];
  if (cites.length === 0) {
    return { ...proposal, verdict: "UNSUPPORTED", reason: "no citations supplied", quote: "", notes: [] };
  }
  const resolved = cites.map((c) => ({ citation: c, ...resolveCitation(c) }));
  const usable = resolved.filter((r) => r.ok);
  if (usable.length === 0) {
    return { ...proposal, verdict: "UNSUPPORTED", reason: resolved.map((r) => r.note).join("; "), quote: "", notes: resolved.map((r) => r.note) };
  }

  const evidence = usable
    .map((r, i) => `--- SOURCE ${i + 1}: ${r.citation} (${r.note}) ---\n${r.excerpt}`)
    .join("\n\n");
  const user = `CLAIM (${proposal.kind ?? "artifact"} ${proposal.id ?? "?"}):\n${proposal.claim}\n\nEVIDENCE:\n${evidence}`;

  const res = await chat(model, [
    { role: "system", content: SYSTEM },
    { role: "user", content: user },
  ], null, { temperature: 0 });

  const text = res?.choices?.[0]?.message?.content ?? "";
  const parsed = parseJson(text);
  if (!parsed) {
    return { ...proposal, verdict: "UNSUPPORTED", reason: "judge returned unparseable output", quote: "", usage: res?.usage };
  }

  // The anti-rubber-stamp check: a supporting verdict needs a quote that is
  // actually present in the excerpt we showed.
  let verdict = String(parsed.verdict || "").toUpperCase();
  const quote = String(parsed.quote || "");
  const haystack = flat(usable.map((r) => r.excerpt).join("\n"));
  const quoteFound = quote.length >= 12 && haystack.includes(flat(quote));
  let downgraded = null;
  if ((verdict === "GROUNDED" || verdict === "PARTIAL") && !quoteFound) {
    downgraded = `${verdict} -> UNSUPPORTED (quote not found verbatim in cited excerpt)`;
    verdict = "UNSUPPORTED";
  }

  return {
    ...proposal,
    verdict,
    quote,
    quote_verified: quoteFound,
    downgraded,
    unsupported_specifics: parsed.unsupported_specifics ?? [],
    reason: parsed.reason ?? "",
    sources_resolved: resolved.map((r) => ({ citation: r.citation, ok: r.ok, note: r.note })),
    usage: res?.usage ?? null,
  };
}

async function main() {
  const { input, out, model: modelId } = args();
  if (!input) {
    console.error("usage: grounding-judge.mjs --input <proposals.jsonl> [--out report.json] [--model id]");
    process.exit(2);
  }
  const env = loadEnv();
  const model = resolveModel(ROOT, modelId, env);

  const proposals = readFileSync(join(ROOT, input.replace(/^\.\//, "")), "utf8")
    .split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));

  const results = [];
  let spend = 0;
  for (const p of proposals) {
    const r = await judge(model, p);
    if (r.usage) spend += costUsd(model, { prompt: r.usage.prompt_tokens ?? 0, completion: r.usage.completion_tokens ?? 0 }) ?? 0;
    results.push(r);
    const mark = { GROUNDED: "✓", PARTIAL: "~", UNSUPPORTED: "✗" }[r.verdict] ?? "?";
    console.log(`${mark} ${r.verdict.padEnd(11)} ${r.id ?? "(no id)"}  ${r.reason}`);
    if (r.downgraded) console.log(`     downgrade: ${r.downgraded}`);
  }

  const tally = results.reduce((acc, r) => ((acc[r.verdict] = (acc[r.verdict] ?? 0) + 1), acc), {});
  const report = {
    generated_at: new Date().toISOString(),
    model: model.id,
    input,
    tally,
    gate_passed: (tally.UNSUPPORTED ?? 0) === 0,
    approx_cost_usd: +spend.toFixed(4),
    results,
  };
  mkdirSync(dirname(join(ROOT, out)), { recursive: true });
  writeFileSync(join(ROOT, out), JSON.stringify(report, null, 2));

  console.log(`\n${JSON.stringify(tally)}  gate ${report.gate_passed ? "PASSED" : "FAILED"} -> ${out}`);
  process.exit(report.gate_passed ? 0 : 1);
}

main().catch((e) => { console.error(e); process.exit(1); });
