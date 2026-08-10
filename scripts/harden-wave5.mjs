#!/usr/bin/env node
/**
 * Wave-5 hardening — the sharper ratchet after wave-4's 15/15 pass:
 *   - conflicting SOP versions: outdated v1 prescribes a WRONG (plausible) target;
 *     current v2 prescribes a conditional rule that evaluates to the correct target.
 *     The prompt names NO document ("follow the CURRENT applicable SOP").
 *   - conditional rule: the correct transition depends on the record's own attributes.
 *   - identification collisions: a distractor record shares the first reference attribute.
 *   - decoy SOPs for unrelated tables pollute retrieval.
 * Original VCode verifiers stay unchanged — only the right doc + right branch passes.
 *
 * Input:  world/blobfish-wave4/package/<id> (wave-4 base)  Output: world/blobfish-wave5/...
 */
import { readFileSync, writeFileSync, mkdirSync, cpSync, rmSync } from "node:fs";
import { execSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SRC_ID = "sbx_36847f702cef4cb4";
const SRC = join(ROOT, "world", "blobfish-wave2", "package", SRC_ID); // start from clean wave-2 base
const OUT = join(ROOT, "world", "blobfish-wave5", "package", SRC_ID);

const flake = JSON.parse(readFileSync(join(ROOT, "data", "flake", "wave2.json"), "utf8"));
const passing = new Set(flake.tasks.filter((t) => t.class === "pass").map((t) => t.taskId));

rmSync(join(ROOT, "world", "blobfish-wave5"), { recursive: true, force: true });
mkdirSync(OUT, { recursive: true });
cpSync(SRC, OUT, { recursive: true });
for (const f of ["state.db", "seed.db"]) rmSync(join(OUT, f), { force: true });
rmSync(join(OUT, ".sessions"), { recursive: true, force: true });
rmSync(join(OUT, "traces"), { recursive: true, force: true });

const raw = JSON.parse(readFileSync(join(OUT, "world.json"), "utf8"));
const world = raw.world ?? raw;
const tableByName = Object.fromEntries((world.tables ?? []).map((t) => [t.name, t]));

// lifecycle enums from the world's update tools -> plausible wrong targets
const lifecycleFor = (table) => {
  for (const t of world.tools ?? []) {
    const s = t.input_schema ?? t.parameters ?? {};
    const en = s?.properties?.status?.enum ?? s?.properties?.[Object.keys(s.properties ?? {}).find((k) => k.includes("status")) ?? ""]?.enum;
    if (en && (t.target_tables ?? []).includes(table) && /update/.test(t.name)) return en;
  }
  return null;
};

const docTable = tableByName["agent_documents"] ?? tableByName["matter_documents"];
const docCols = (docTable.columns ?? []).map((c) => c.name);
const F_TITLE = ["title", "name", "subject"].find((n) => docCols.includes(n)) ?? "title";
const F_BODY = ["content", "body", "text", "notes"].find((n) => docCols.includes(n)) ?? "content";
const F_DATE = docCols.find((n) => n.includes("_at") || n.includes("date")) ?? null;
let docMaxId = Math.max(0, ...(docTable.sample_rows ?? []).map((r) => Number(r.id)).filter(Number.isFinite));
const addDoc = (title, body, date) => {
  const doc = { id: ++docMaxId };
  doc[F_TITLE] = title; doc[F_BODY] = body;
  if (F_DATE) doc[F_DATE] = date;
  for (const c of docCols) if (!(c in doc)) doc[c] = c.includes("status") ? "active" : null;
  (docTable.sample_rows ??= []).push(doc);
  docTable.row_count = (docTable.row_count ?? 0) + 1;
};

const IDENT = ["number", "name", "title", "code", "company", "contact", "period", "category", "owner"];
const pickAttrs = (cols, row, exclude) => {
  const cands = cols.map((c) => c.name).filter((n) => !["id", exclude].includes(n) && row[n] != null && String(row[n]) !== "");
  const labely = cands.filter((n) => IDENT.some((k) => n.toLowerCase().includes(k)));
  return [...labely, ...cands.filter((n) => !labely.includes(n))].slice(0, 3);
};

const hardened = [];
for (const task of world.tasks ?? []) {
  if (!passing.has(task.task_id)) continue;
  const eff = (task.expected_state_changes ?? []).find((e) => e.table && e.id !== undefined && e.field && e.to !== undefined);
  if (!eff) continue;
  const table = tableByName[eff.table];
  const rows = table?.sample_rows ?? [];
  const row = rows.find((r) => String(r.id) === String(eff.id));
  if (!table || !row) continue;

  const lifecycle = lifecycleFor(eff.table) ?? [];
  const wrong = lifecycle.find((s) => s !== eff.to && s !== eff.from) ?? lifecycle.find((s) => s !== eff.to) ?? "cancelled";

  // conditional attribute: pick a non-status attribute present on the row
  const attrs = pickAttrs(table.columns ?? [], row, eff.field);
  const condAttr = attrs[2] ?? attrs[1] ?? attrs[0];
  const condVal = row[condAttr];
  const label = eff.table.replace(/_/g, " ");

  // v1 (outdated, wrong target) + v2 (current, conditional -> correct)
  addDoc(
    `${label} handling procedure`,
    `[SUPERSEDED 2025] ${label} records verified in ${eff.field} "${eff.from}" must be moved to ${eff.field} "${wrong}". This document may be outdated.`,
    "2025-02-11"
  );
  addDoc(
    `${label} handling procedure (rev. 2)`,
    `[CURRENT — effective 2026-06-01, supersedes all prior versions] For ${label} records verified in ${eff.field} "${eff.from}": ` +
    `if the record's ${condAttr} is "${condVal}", move it to ${eff.field} "${eff.to}"; otherwise move it to ${eff.field} "${wrong}". Apply exactly one transition.`,
    "2026-06-01"
  );

  // identification collision: distractor sharing attr1, varying attr2, same from-status
  const [a1, a2] = attrs;
  const maxId = Math.max(0, ...rows.map((r) => Number(r.id)).filter(Number.isFinite));
  const clone = structuredClone(row);
  clone.id = maxId + 500;
  if (a2 && a2 !== a1) clone[a2] = `${row[a2]}-B`;
  rows.push(clone);
  table.row_count = (table.row_count ?? rows.length - 1) + 1;

  const ref = a2 && a2 !== a1
    ? `the ${label} record whose ${a1} is "${row[a1]}" and whose ${a2} is exactly "${row[a2]}"`
    : `the ${label} record whose ${a1} is "${row[a1]}"`;
  task.prompt =
    `In the morgan_stanley_simulated world: locate ${ref} and process it according to the CURRENT ${label} handling procedure ` +
    `in the document store. Be careful: multiple versions of the procedure exist and some are outdated, and the current procedure's ` +
    `outcome depends on the record's own attributes. Verify the record first, apply exactly one correct transition, change nothing else, and report what you did.`;
  hardened.push({ task: task.task_id, table: eff.table, cond: `${condAttr}="${condVal}" → ${eff.to} else ${wrong}`, wrongDoc: wrong });
}

// decoy SOPs for unrelated tables
for (const name of ["support_tickets", "marketing_content_assets", "sourcing_vendors", "finance_budgets", "hr_performance_reviews", "employees"]) {
  if (!tableByName[name]) continue;
  addDoc(`${name.replace(/_/g, " ")} handling procedure`, `[CURRENT] Routine guidance for ${name.replace(/_/g, " ")} records; no transitions are mandated by this document.`, "2026-05-15");
}

writeFileSync(join(OUT, "world.json"), JSON.stringify(raw, null, 1));
writeFileSync(join(OUT, "tasks.jsonl"), (world.tasks ?? []).map((t) => JSON.stringify(t)).join("\n") + "\n");
execSync("python3 create_db.py", { cwd: OUT, stdio: "inherit" });
execSync("cp seed.db state.db", { cwd: OUT });
cpSync(join(OUT, "world.json"), join(ROOT, "world", "blobfish-wave5", "world.json"));

console.log(`wave-5 hardened ${hardened.length} tasks (conflicting SOP versions + conditional rules + collisions + decoys)`);
for (const h of hardened) console.log(`  ${h.task}: ${h.table} | current rule: ${h.cond} | outdated doc says: ${h.wrongDoc}`);
