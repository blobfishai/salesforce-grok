#!/usr/bin/env node
/**
 * Materialize the benchmark as browsable folders under bench/:
 *
 *   bench/tasks/<world>/task_XXX.json         every task definition (incl. arena)
 *   bench/verifiers/<world>/task_XXX.py       the VCode verifier source
 *   bench/verifiers/<world>/task_XXX.meta.json  assertions + expected state changes
 *   bench/traces/<world>/<model>/<label>--task_XXX-tN.jsonl   every full transcript
 *   bench/failed-traces/<world>/<model>/...   copies of the failing ones
 *   bench/reports/<model>.md                  per-model failure report across sweeps
 *
 * Idempotent: wipes and regenerates bench/ from world/*.json, data/flake/*, and
 * sim/logs transcripts. Legacy pre-multimodel sweeps (wave1..wave5b) are grok-4.5.
 */
import { readFileSync, writeFileSync, mkdirSync, rmSync, readdirSync, existsSync, copyFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, basename } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const BENCH = join(ROOT, "bench");
rmSync(BENCH, { recursive: true, force: true });

const WORLDS = {
  wave5: "world/blobfish-wave5/world.json",
  wave6: "world/blobfish-wave6/world.json",
  wave1: "world/blobfish/world.json",
};
const LABEL_WORLD = [
  [/^lb-w5-/, "wave5"], [/^grok420-probes$/, "wave5"], [/^wave4$/, "wave5"], [/^wave5b?$/, "wave5"],
  [/^w6-/, "wave6"],
  // wave-6 world packs: CRMArena clone, the wave-7 workflow pack and their re-runs
  [/^crma-/, "wave6"], [/^wave7-/, "wave6"], [/^realism-/, "wave6"], [/^restraint-/, "wave6"], [/^wave8-/, "wave6"],
  [/^wave1b?$/, "wave1"], [/^wave3-local$/, "wave1"],
  [/^wave2/, "wave5"], // wave2 world == wave5 world id (pre-hardening variant)
];
const worldOf = (label) => (LABEL_WORLD.find(([re]) => re.test(label)) ?? [null, "other"])[1];

// ---------------------------------------------------------------- tasks + verifiers + per-task seeds
const DOC_STORES = ["agent_documents", "agent_knowledge", "agent_playbooks", "matter_documents", "agent_files"];
function extractTaskSeed(world, t) {
  const tables = Object.fromEntries((world.tables ?? []).map((x) => [x.name, x]));
  const seed = { schema: "task-seed.v1", task_id: t.task_id, rows: {}, documents: [], input_documents: [], mcp_seeding: {} };
  // rows the task explicitly touches (relevant_data pins + expected state changes)
  const wants = [];
  for (const rd of t.relevant_data ?? []) if (rd.table && rd.id !== undefined) wants.push([rd.table, rd.id]);
  for (const sc of t.expected_state_changes ?? []) if (sc.table && sc.id !== undefined) wants.push([sc.table, sc.id]);
  for (const [tn, id] of wants) {
    const row = (tables[tn]?.sample_rows ?? []).find((r) => String(r.id) === String(id));
    if (row) (seed.rows[tn] ??= []).push(row);
  }
  // documents whose title tokens appear in the prompt (input docs) or whose store
  // the task's tables reference (context docs)
  const prompt = (t.prompt ?? "").toLowerCase();
  for (const store of DOC_STORES) {
    for (const r of tables[store]?.sample_rows ?? []) {
      const title = String(r.title ?? r.name ?? "").toLowerCase();
      if (!title) continue;
      const tokens = title.split(/[^a-z0-9]+/).filter((x) => x.length > 4);
      const hits = tokens.filter((tok) => prompt.includes(tok)).length;
      if (hits >= 2 || (hits >= 1 && (t.tables_affected ?? []).some((tb) => title.includes(String(tb).replace(/_/g, " ").slice(0, 12))))) {
        const entry = { store, id: r.id, title: r.title ?? r.name ?? "" };
        if (prompt.includes("document") && store === "matter_documents") seed.input_documents.push(entry);
        else seed.documents.push(entry);
      }
    }
  }
  // per-vendor MCP seeding: which vendor namespaces the reference walk exercises
  const nsOf = Object.fromEntries((world.tools ?? []).map((x) => [x.name, x.asset_namespace ?? "core"]));
  for (const step of t.walk ?? []) {
    const ns = nsOf[step];
    if (ns) (seed.mcp_seeding[ns] ??= []).push(step);
  }
  return seed;
}

for (const [w, rel] of Object.entries(WORLDS)) {
  const raw = JSON.parse(readFileSync(join(ROOT, rel), "utf8"));
  const world = raw.world ?? raw;
  const tdir = join(BENCH, "tasks", w);
  const vdir = join(BENCH, "verifiers", w);
  mkdirSync(tdir, { recursive: true });
  mkdirSync(vdir, { recursive: true });
  for (const t of world.tasks ?? []) {
    writeFileSync(join(tdir, `${t.task_id}.json`), JSON.stringify(t, null, 1));
    writeFileSync(join(tdir, `${t.task_id}.seed.json`), JSON.stringify(extractTaskSeed(world, t), null, 1));
  }
  for (const v of world.verifiers ?? []) {
    if (v.vcode) writeFileSync(join(vdir, `${v.task_id}.py`), v.vcode);
    const { vcode, ...meta } = v;
    writeFileSync(join(vdir, `${v.task_id}.meta.json`), JSON.stringify(meta, null, 1));
  }
}
// arena tasks (answer-matched; no vcode)
{
  const spec = JSON.parse(readFileSync(join(ROOT, "world", "arena", "arena-tasks.json"), "utf8"));
  const tdir = join(BENCH, "tasks", "arena");
  mkdirSync(tdir, { recursive: true });
  for (const t of spec.tasks) writeFileSync(join(tdir, `${t.id}.json`), JSON.stringify({ level: spec.level, ...t }, null, 1));
}

// ---------------------------------------------------------------- mcp tools
// Every tool the worlds expose, browsable: bench/tools/<world>/<vendor>/<name>.json
// (schema, type, target tables, MCP name) + <name>.py (the actual generated
// implementation the packaged server executes).
const vendorReg = JSON.parse(readFileSync(join(ROOT, "config", "mcp-servers.json"), "utf8")).vendors;
const nsToVendor = {};
for (const [v, spec] of Object.entries(vendorReg)) for (const ns of spec.namespaces) nsToVendor[ns] = v;
for (const [w, rel] of Object.entries(WORLDS)) {
  const world = (JSON.parse(readFileSync(join(ROOT, rel), "utf8"))).world ?? JSON.parse(readFileSync(join(ROOT, rel), "utf8"));
  const index = [];
  for (const t of world.tools ?? []) {
    const ns = t.asset_namespace ?? (t.mcp_name?.includes(".") ? t.mcp_name.split(".")[0] : "core");
    const vendor = w === "wave6" ? (nsToVendor[ns] ?? ns) : ns;
    const dir = join(BENCH, "tools", w, vendor);
    mkdirSync(dir, { recursive: true });
    const { source, ...meta } = t;
    writeFileSync(join(dir, `${t.name}.json`), JSON.stringify(meta, null, 1));
    if (source) writeFileSync(join(dir, `${t.name}.py`), source);
    index.push({ vendor, name: t.name, mcp: t.mcp_name, type: t.type, tables: t.target_tables ?? [] });
  }
  index.sort((a, b) => a.vendor.localeCompare(b.vendor) || a.name.localeCompare(b.name));
  writeFileSync(join(BENCH, "tools", w, "INDEX.md"),
    `# ${w} — ${index.length} MCP tools\n\n| vendor server | tool | type | target tables |\n|---|---|---|---|\n` +
    index.map((i) => `| ${i.vendor} | \`${i.name}\` | ${i.type ?? ""} | ${(i.tables ?? []).slice(0, 3).join(", ")} |`).join("\n") + "\n");
}

// ---------------------------------------------------------------- traces
const trialDir = join(ROOT, "data", "flake", ".trials");
const copied = { traces: 0, failed: 0, missing: 0 };
const modelSweeps = {}; // model -> label -> {trials:[], world}
for (const f of readdirSync(trialDir).filter((x) => x.endsWith(".json"))) {
  let rec;
  try { rec = JSON.parse(readFileSync(join(trialDir, f), "utf8")); } catch { continue; }
  // task ids are no longer only `task_NNN`: the CRMArena clone uses `crma_NNN`
  // and the workflow pack `wf_NNN`, so match any <prefix>_<digits> id.
  const m = /^(.*)-([a-z][a-z0-9]*_\d+)-t(\d+)\.json$/.exec(f);
  if (!m) continue;
  const [, label, taskId, trial] = m;
  const model = rec.model ?? "grok-4.5"; // legacy sweeps predate the multi-model harness
  const w = worldOf(label);
  ((modelSweeps[model] ??= {})[label] ??= { trials: [], world: w }).trials.push({ ...rec, taskId, trial: Number(trial) });
  if (!rec.log || !existsSync(rec.log)) { copied.missing++; continue; }
  const dest = join(BENCH, "traces", w, model);
  mkdirSync(dest, { recursive: true });
  const name = `${label}--${taskId}-t${trial}.jsonl`;
  copyFileSync(rec.log, join(dest, name));
  copied.traces++;
  if (!rec.passed && !rec.infraError) {
    const fdest = join(BENCH, "failed-traces", w, model);
    mkdirSync(fdest, { recursive: true });
    copyFileSync(rec.log, join(fdest, name));
    copied.failed++;
  }
}
// arena episodes (self-contained episode JSONs, steps embedded)
for (const f of readdirSync(join(ROOT, "sim", "logs", "arena")).filter((x) => x.endsWith(".json"))) {
  let ep;
  try { ep = JSON.parse(readFileSync(join(ROOT, "sim", "logs", "arena", f), "utf8")); } catch { continue; }
  const model = ep.model ?? "grok-4.5";
  const dest = join(BENCH, "traces", "arena", model);
  mkdirSync(dest, { recursive: true });
  copyFileSync(join(ROOT, "sim", "logs", "arena", f), join(dest, f));
  copied.traces++;
  if (ep.passed === false) {
    const fdest = join(BENCH, "failed-traces", "arena", model);
    mkdirSync(fdest, { recursive: true });
    copyFileSync(join(ROOT, "sim", "logs", "arena", f), join(fdest, f));
    copied.failed++;
  }
}

// ---------------------------------------------------------------- per-model reports
const ENV_BUGS = { wave6: new Set(["task_001", "task_002"]), wave5: new Set(["task_008"]) };
const MODES = [
  ["missing_creation", (c) => c.startsWith("rows_inserted_into")],
  ["collateral_writes", (c) => c === "no_offtask_table_changes" || c === "no_undeclared_rows_created" || c.startsWith("no_collateral")],
  ["wrong_end_state", (c) => /_status_is_|^state_changed$/.test(c)],
  ["shortcutting", (c) => c === "reads_before_writes" || c === "no_shortcut_direct_update"],
  ["unrecovered_tool_errors", (c) => c === "all_tools_succeeded"],
  ["undocumented_order_artifact", (c) => c === "required_workflow_path"],
];
mkdirSync(join(BENCH, "reports"), { recursive: true });
for (const [model, sweeps] of Object.entries(modelSweeps)) {
  let md = `# Failure report — ${model}\n\n> Generated by scripts/build-bench-folders.mjs. Classifications follow the audit protocol: environment-bug tasks are excluded from "real" counts; the undocumented-order assertion is an environment artifact, listed separately.\n`;
  for (const [label, s] of Object.entries(sweeps).sort()) {
    const clean = s.trials.filter((t) => !t.infraError);
    const failed = clean.filter((t) => !t.passed);
    const real = failed.filter((t) => {
      if (ENV_BUGS[s.world]?.has(t.taskId)) return false;
      const fc = t.failedConditions ?? [];
      return !fc.every((c) => c === "required_workflow_path");
    });
    md += `\n## Sweep \`${label}\` (world ${s.world})\n\n`;
    md += `- trials ${clean.length} · passed ${clean.length - failed.length} · failed ${failed.length} · env-bug ${failed.length - real.length - failed.filter((t) => !ENV_BUGS[s.world]?.has(t.taskId) && (t.failedConditions ?? []).every((c) => c === "required_workflow_path")).length ? failed.filter((t) => ENV_BUGS[s.world]?.has(t.taskId)).length : failed.filter((t) => ENV_BUGS[s.world]?.has(t.taskId)).length} · artifact-only ${failed.filter((t) => !ENV_BUGS[s.world]?.has(t.taskId) && (t.failedConditions ?? []).length > 0 && (t.failedConditions ?? []).every((c) => c === "required_workflow_path")).length} · **real ${real.length}**\n`;
    const modeCounts = {};
    for (const t of real) for (const [k, match] of MODES) if ((t.failedConditions ?? []).some(match)) modeCounts[k] = (modeCounts[k] ?? 0) + 1;
    if (Object.keys(modeCounts).length) {
      md += `- real failure modes: ${Object.entries(modeCounts).map(([k, n]) => `${k} ×${n}`).join(", ")}\n`;
    }
    if (failed.length) {
      md += `\n| task | trial | calls | classification | failed assertions | trace |\n|---|---|---|---|---|---|\n`;
      for (const t of failed.sort((a, b) => a.taskId.localeCompare(b.taskId) || a.trial - b.trial)) {
        const cls = ENV_BUGS[s.world]?.has(t.taskId) ? "ENV BUG" : (t.failedConditions ?? []).every((c) => c === "required_workflow_path") ? "artifact-only" : "real";
        const trace = t.log && existsSync(t.log) ? `[jsonl](../failed-traces/${s.world}/${model}/${label}--${t.taskId}-t${t.trial}.jsonl)` : "—";
        md += `| ${t.taskId} | ${t.trial} | ${t.toolCalls ?? "—"} | ${cls} | ${(t.failedConditions ?? []).slice(0, 4).join(", ")} | ${trace} |\n`;
      }
    }
  }
  writeFileSync(join(BENCH, "reports", `${model}.md`), md);
}

// ---------------------------------------------------------------- index
const counts = (dir) => existsSync(dir) ? readdirSync(dir, { recursive: true }).filter((f) => /\.(json|jsonl|py|md)$/.test(String(f))).length : 0;
writeFileSync(join(BENCH, "README.md"), `# bench/ — the benchmark as files

Regenerate with \`node scripts/build-bench-folders.mjs\` (idempotent; sources:
world/*/world.json, data/flake/.trials/, sim/logs/).

| folder | contents | files |
|---|---|---|
| tasks/ | every task definition by world (wave5, wave6, wave1, arena) + per-task \`*.seed.json\` fixture bundles (rows, documents, input documents, per-vendor MCP seeding) | ${counts(join(BENCH, "tasks"))} |
| tools/ | every MCP tool by world → vendor server: schema (.json) + generated Python implementation (.py) + INDEX.md | ${counts(join(BENCH, "tools"))} |
| verifiers/ | VCode verifier source (.py) + assertions metadata (.meta.json) | ${counts(join(BENCH, "verifiers"))} |
| traces/ | every full run transcript, grouped world → model | ${counts(join(BENCH, "traces"))} |
| failed-traces/ | the failing subset, same layout | ${counts(join(BENCH, "failed-traces"))} |
| reports/ | per-model failure report across all sweeps | ${counts(join(BENCH, "reports"))} |

Trace filename: \`<sweep-label>--<task>-t<trial>.jsonl\` — turn-tagged records
(completion/thinking/tool/final/verify). Arena traces are self-contained episode
JSONs. Classifications in reports follow the audit protocol (env-bug exclusions:
wave5 task_008; wave6 task_001/task_002; undocumented-order = artifact).
`);
console.log(`bench/ built: ${copied.traces} traces (${copied.failed} failed copies, ${copied.missing} transcripts missing), reports for ${Object.keys(modelSweeps).length} models`);
