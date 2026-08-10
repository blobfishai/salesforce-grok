#!/usr/bin/env node
/**
 * Build dashboard/input-docs.html — the INPUT SIDE of the eval:
 *   1. seeded task documents inside the world (routing policy, KB articles, lead notes)
 *      with the tasks each one grounds;
 *   2. the anchor files uploaded to the blobfish API that generated the world;
 *   3. how the world deepened wave over wave.
 */
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

const spec = JSON.parse(readFileSync(join(ROOT, "world", "arena", "arena-tasks.json"), "utf8"));
const arenaWorld = (() => { const r = JSON.parse(readFileSync(join(ROOT, "world", "arena", "world.json"), "utf8")); return r.world ?? r; })();
const docsRows = (arenaWorld.tables ?? []).find((t) => t.name === "agent_documents")?.sample_rows ?? [];
const seededTitles = new Set(spec.seededDocs);
const usedBy = {};
for (const t of spec.tasks) for (const d of t.docs ?? []) (usedBy[d] ??= []).push(t.id);

const docCard = (d) => `
  <div class="doc">
    <div class="dhead"><span class="dtitle">${esc(d.title)}</span><span class="dmeta">agent_documents · id ${d.id} · ${esc(String(d.updated_at).slice(0, 10))}</span></div>
    <div class="dbody">${esc(d.body)}</div>
    ${usedBy[d.title]?.length ? `<div class="dused">grounds: ${usedBy[d.title].map((t) => `<span class="chip blue mono">${esc(t)}</span>`).join(" ")}</div>` : ""}
  </div>`;
const seededCards = docsRows.filter((d) => seededTitles.has(d.title)).map(docCard).join("");

const anchorDir = join(ROOT, "docs", "anchors", "wave2");
const anchors = readdirSync(anchorDir).filter((f) => f.endsWith(".md")).sort().map((f) => {
  const body = readFileSync(join(anchorDir, f), "utf8");
  const firstHeading = (body.match(/^# (.+)$/m) ?? [null, f])[1];
  const excerpt = body.split("\n").filter((l) => l.trim() && !l.startsWith("#") && !l.startsWith(">")).slice(0, 2).join(" ");
  return { f, firstHeading, excerpt, bytes: body.length };
});
const anchorRows = anchors.map((a) => `
  <tr><td class="mono">${esc(a.f)}</td><td>${esc(a.firstHeading)}</td><td class="cond">${esc(a.excerpt.slice(0, 130))}…</td><td class="num">${(a.bytes / 1024).toFixed(1)}k</td></tr>`).join("");

const EVOLUTION = [
  ["wave 1", "1 anchor PRD → POST /api/v1/sandbox/jobs", "33 tables · 104 tools · 27 tasks · walks ≤6 hops · 2,377 rows"],
  ["wave 2", "18 anchor docs (12 grounding angles) + mock_services salesforce/stripe → same API", "49 tables · 171 tools · 28 tasks · walks to 13 hops · 2,553 rows"],
  ["wave 4", "+15 seeded SOP documents inside the world (per passing task)", "same schema; doc-retrieval hop added — grok still 15/15"],
  ["wave 5", "+conflicting SOP revisions, conditional rules, record collisions, decoy docs", "frontier found: task_003 50% · task_018 0/6 · cliff at ~11 calls"],
  ["arena L1", "+real-eval task suite (CRMArena task types) grounded in routing policy, KB articles, lead notes", `${spec.tasks.length} answer-matched tasks with computed ground truth`],
  ["arena L2", "+policy revisions, near-tie data, decoy KBs, superseding notes, extra name collisions", "the hardening rung applied only to tasks grok passes"],
];
const evoRows = EVOLUTION.map(([w, inp, out]) => `<tr><td><b>${esc(w)}</b></td><td class="cond">${esc(inp)}</td><td class="cond">${esc(out)}</td></tr>`).join("");

const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Input documents & world evolution — arena eval</title><style>
  :root { color-scheme: dark; --page:#0d0d0d; --surface-1:#1a1a19; --ink:#fff; --ink-2:#c3c2b7; --muted:#898781;
    --grid:#2c2c2a; --border:rgba(255,255,255,.10); --series-1:#3987e5; --crit:#d03b3b; }
  * { box-sizing:border-box; margin:0; }
  body { background:var(--page); color:var(--ink); font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif; padding:24px; }
  .wrap { max-width:1180px; margin:0 auto; }
  header { display:flex; flex-wrap:wrap; align-items:baseline; gap:10px 14px; }
  h1 { font-size:20px; font-weight:650; }
  .badge { font-size:11px; font-weight:600; color:var(--crit); border:1px solid currentColor; border-radius:999px; padding:2px 9px; }
  .sub { color:var(--ink-2); margin:4px 0 16px; }
  .panel { background:var(--surface-1); border:1px solid var(--border); border-radius:12px; padding:16px; margin-bottom:14px; }
  .panel h2 { font-size:14.5px; font-weight:650; margin-bottom:4px; }
  .note { color:var(--ink-2); font-size:12.5px; margin-bottom:12px; }
  .doc { border:1px solid var(--grid); border-radius:10px; padding:12px 14px; margin-bottom:10px; }
  .dhead { display:flex; justify-content:space-between; flex-wrap:wrap; gap:6px; margin-bottom:6px; }
  .dtitle { font-weight:650; font-size:13.5px; }
  .dmeta { color:var(--muted); font-size:11px; }
  .dbody { color:var(--ink-2); font-size:12.5px; font-family: Georgia, "Times New Roman", serif; background:var(--page); border:1px solid var(--grid); border-radius:8px; padding:10px 12px; }
  .dused { margin-top:8px; font-size:11.5px; color:var(--muted); }
  .chip { font-size:10.5px; border-radius:999px; padding:1px 8px; border:1px solid var(--grid); color:var(--ink-2); }
  .chip.blue { color:var(--series-1); border-color:var(--series-1); }
  .mono { font-family:ui-monospace,Menlo,monospace; }
  table { width:100%; border-collapse:collapse; }
  th { text-align:left; color:var(--muted); font-size:11.5px; padding:6px 8px; border-bottom:1px solid var(--grid); }
  td { padding:6px 8px; border-bottom:1px solid var(--grid); vertical-align:top; }
  td.num { text-align:right; } td.cond { color:var(--ink-2); font-size:12.5px; }
  footer { color:var(--muted); font-size:12px; margin-top:14px; }
</style></head><body><div class="wrap">
  <header><h1>Input documents — what the tasks are anchored to</h1><span class="badge">SIMULATED · SYNTHETIC</span></header>
  <div class="sub">Arena level ${spec.level} · every task's ground truth is computed from these documents + the world's own records, then scored CRMArena-style (exact / fuzzy / set match).</div>

  <div class="panel">
    <h2>Seeded task documents (inside the world's document store)</h2>
    <div class="note">The agent must retrieve and reason over these — the answers live nowhere else.</div>
    ${seededCards}
  </div>

  <div class="panel">
    <h2>World-generation input files (anchor corpus → blobfish API)</h2>
    <div class="note">Uploaded as <span class="mono">anchor_files</span> to <span class="mono">POST /api/v1/sandbox/jobs</span>; filename tokens map to research angles; workflow chains become graph walks.</div>
    <table><thead><tr><th>file</th><th>document</th><th>excerpt</th><th>size</th></tr></thead><tbody>${anchorRows}</tbody></table>
  </div>

  <div class="panel">
    <h2>How the world deepened, wave over wave</h2>
    <div class="note">Each iteration adds input documents, tools, hops, or ambiguity — then re-measures grok-4.5.</div>
    <table><thead><tr><th>wave</th><th>inputs added</th><th>world / result</th></tr></thead><tbody>${evoRows}</tbody></table>
  </div>
  <footer>Simulation only — synthetic data; not affiliated with Morgan Stanley or Salesforce.</footer>
</div></body></html>`;

writeFileSync(join(ROOT, "dashboard", "input-docs.html"), html);
console.log(`input-docs.html — ${docsRows.filter((d) => seededTitles.has(d.title)).length} seeded docs, ${anchors.length} anchor files`);
