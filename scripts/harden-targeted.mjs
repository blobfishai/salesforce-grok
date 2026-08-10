#!/usr/bin/env node
/**
 * Wave-4 targeted hardening — push each SOLID-PASS task toward the model's limit
 * without touching failing tasks (per-task frontier search, not aggregate tuning).
 *
 * Axes applied per passing task (verifiers stay unchanged and valid):
 *   - seeded difficult document: an SOP row in the document store now carries the
 *     required target transition; the prompt no longer states it.
 *   - ambiguous prompt: record handles replaced with attribute-based references.
 *   - longer horizon: doc retrieval + attribute resolution become mandatory hops.
 *
 * Input:  world/blobfish-wave2/package/<id>  + data/flake/wave2.json
 * Output: world/blobfish-wave4/package/<id>  (patched world.json + rebuilt seed.db)
 */
import { readFileSync, writeFileSync, mkdirSync, cpSync, rmSync } from "node:fs";
import { execSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SRC_ID = "sbx_36847f702cef4cb4";
const SRC = join(ROOT, "world", "blobfish-wave2", "package", SRC_ID);
const OUT = join(ROOT, "world", "blobfish-wave4", "package", SRC_ID);

const flake = JSON.parse(readFileSync(join(ROOT, "data", "flake", "wave2.json"), "utf8"));
const passing = new Set(flake.tasks.filter((t) => t.class === "pass").map((t) => t.taskId));

rmSync(join(ROOT, "world", "blobfish-wave4"), { recursive: true, force: true });
mkdirSync(OUT, { recursive: true });
cpSync(SRC, OUT, { recursive: true });
for (const f of ["state.db", "seed.db"]) rmSync(join(OUT, f), { force: true });
rmSync(join(OUT, ".sessions"), { recursive: true, force: true });
rmSync(join(OUT, "traces"), { recursive: true, force: true });

const raw = JSON.parse(readFileSync(join(OUT, "world.json"), "utf8"));
const world = raw.world ?? raw;
const tableByName = Object.fromEntries((world.tables ?? []).map((t) => [t.name, t]));

// document store table: prefer agent_documents, else create-compatible fallback
const docTable = tableByName["agent_documents"] ?? tableByName["matter_documents"];
if (!docTable) { console.error("no document table found"); process.exit(1); }
const docCols = (docTable.columns ?? []).map((c) => c.name);
const docField = (names, dflt) => names.find((n) => docCols.includes(n)) ?? dflt;
const F_TITLE = docField(["title", "name", "subject"], "title");
const F_BODY = docField(["content", "body", "text", "notes"], "content");
let docMaxId = Math.max(0, ...(docTable.sample_rows ?? []).map((r) => Number(r.id)).filter(Number.isFinite));

const IDENT = ["number", "name", "title", "code", "company", "contact", "period", "category", "owner"];
const pickAttrs = (cols, row, excludeField) => {
  const cands = cols.map((c) => c.name).filter((n) => !["id", excludeField].includes(n) && row[n] !== null && row[n] !== undefined && String(row[n]) !== "");
  const labely = cands.filter((n) => IDENT.some((k) => n.toLowerCase().includes(k)));
  return [...labely, ...cands.filter((n) => !labely.includes(n))].slice(0, 2);
};

const hardened = [];
for (const task of world.tasks ?? []) {
  if (!passing.has(task.task_id)) continue;
  const eff = (task.expected_state_changes ?? []).find((e) => e.table && e.id !== undefined && e.field && e.to !== undefined);
  if (!eff) continue;
  const table = tableByName[eff.table];
  const row = (table?.sample_rows ?? []).find((r) => String(r.id) === String(eff.id));
  if (!table || !row) continue;

  // 1) seeded SOP document carrying the transition rule (the ONLY place the target now appears)
  const sopTitle = `SOP ${task.task_id.toUpperCase().replace("TASK_", "OPS-")}: ${eff.table.replace(/_/g, " ")} handling`;
  const doc = { id: ++docMaxId };
  if (docCols.includes("title") || F_TITLE) doc[F_TITLE] = sopTitle;
  doc[F_BODY] = `Procedure for ${eff.table.replace(/_/g, " ")} records: any record currently in ${eff.field} "${eff.from}" that has been verified must be moved to ${eff.field} "${eff.to}". Apply no other transition. Log nothing else.`;
  for (const c of docCols) if (!(c in doc)) doc[c] = c.includes("status") ? "active" : c.includes("_at") || c.includes("date") ? "2026-08-01" : c.includes("id") && c !== "id" ? null : (doc[c] ?? null);
  (docTable.sample_rows ??= []).push(doc);
  docTable.row_count = (docTable.row_count ?? docTable.sample_rows.length - 1) + 1;

  // 2) ambiguate: replace the record handle with an attribute-based reference
  const [a1, a2] = pickAttrs(table.columns ?? [], row, eff.field);
  const ref = a2 && a2 !== a1
    ? `the ${eff.table.replace(/_/g, " ")} record whose ${a1} is "${row[a1]}" and whose ${a2} is "${row[a2]}"`
    : `the ${eff.table.replace(/_/g, " ")} record whose ${a1} is "${row[a1]}"`;
  // strip any literal handles/status targets from the original prompt; rebuild it
  task.prompt =
    `In the morgan_stanley_simulated world: locate ${ref}. ` +
    `Consult the document store for the procedure titled "${sopTitle}" and apply EXACTLY the transition it specifies to that record — ` +
    `the correct target ${eff.field} is defined only there. Confirm the record's current ${eff.field} first, change nothing else, and report what you did.`;
  hardened.push({ task: task.task_id, table: eff.table, row: eff.id, attrs: [a1, a2], sop: sopTitle });
}

writeFileSync(join(OUT, "world.json"), JSON.stringify(raw, null, 1));
writeFileSync(join(OUT, "tasks.jsonl"), (world.tasks ?? []).map((t) => JSON.stringify(t)).join("\n") + "\n");
execSync("python3 create_db.py", { cwd: OUT, stdio: "inherit" });
execSync("cp seed.db state.db", { cwd: OUT });
cpSync(join(OUT, "world.json"), join(ROOT, "world", "blobfish-wave4", "world.json"));

console.log(`hardened ${hardened.length} passing tasks (fails untouched; verifiers unchanged)`);
for (const h of hardened) console.log(`  ${h.task}: ${h.table}#${h.row} via [${h.attrs.join(", ")}] · doc "${h.sop}"`);
console.log(`package: ${OUT}`);
