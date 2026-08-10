#!/usr/bin/env node
/**
 * Local task escalation — mirrors blobfish's calibrationCore.escalateTask levels 1-2:
 *   1) obscure_entity_reference: replace the explicit record handle in the prompt with a
 *      two-field description ("the <table> record whose <A> is "x" and whose <B> is "y"").
 *   2) add_distractor_rows: clone the pinned anchor row into near-identical distractors
 *      (same field A + same lifecycle status, suffixed field B). Verifiers stay UNCHANGED —
 *      the pre-existing no_collateral_<table> guard automatically punishes touching them.
 *
 * Produces a new runnable package: world/blobfish-wave3local/package/<id>/
 * Usage: node scripts/escalate-local.mjs [--level 2] [--tasks task_004,task_012 | default: all]
 */
import { readFileSync, writeFileSync, mkdirSync, cpSync, rmSync } from "node:fs";
import { execSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SRC = join(ROOT, "world", "blobfish", "package", "sbx_7d7d8fedcecb4458");
const OUT = join(ROOT, "world", "blobfish-wave3local", "package", "sbx_7d7d8fedcecb4458");
const argv = process.argv.slice(2);
const LEVEL = Number(argv.includes("--level") ? argv[argv.indexOf("--level") + 1] : 2);
const ONLY = argv.includes("--tasks") ? argv[argv.indexOf("--tasks") + 1].split(",") : null;

const SUFFIXES = LEVEL >= 2
  ? ["(archived)", "(duplicate)", "(transferred)", "(cancelled)"]
  : ["(archived)", "(duplicate)"];
const K = LEVEL >= 2 ? 3 : 2;

rmSync(join(ROOT, "world", "blobfish-wave3local"), { recursive: true, force: true });
mkdirSync(OUT, { recursive: true });
cpSync(SRC, OUT, { recursive: true });
rmSync(join(OUT, "state.db"), { force: true });
rmSync(join(OUT, "seed.db"), { force: true });
rmSync(join(OUT, ".sessions"), { recursive: true, force: true });
rmSync(join(OUT, "traces"), { recursive: true, force: true });

const worldPath = join(OUT, "world.json");
const raw = JSON.parse(readFileSync(worldPath, "utf8"));
const world = raw.world ?? raw;
const tableByName = Object.fromEntries((world.tables ?? []).map((t) => [t.name, t]));

const IDENT_FIELDS = ["number", "name", "title", "subject", "handle", "code", "company", "contact"];
const pickObscureFields = (cols, row, excludeField) => {
  const candidates = cols
    .map((c) => c.name)
    .filter((n) => n !== "id" && n !== excludeField && row[n] !== null && row[n] !== undefined && String(row[n]).length > 0);
  const labely = candidates.filter((n) => IDENT_FIELDS.some((k) => n.toLowerCase().includes(k)));
  const rest = candidates.filter((n) => !labely.includes(n));
  const picked = [...labely, ...rest];
  return [picked[0], picked[1] ?? picked[0]];
};

const escalated = [];
let distractorsAdded = 0;

for (const task of world.tasks ?? []) {
  if (ONLY && !ONLY.includes(task.task_id)) continue;
  const effects = task.expected_state_changes ?? [];
  const eff = effects.find((e) => e.table && (e.id !== undefined && e.id !== null));
  if (!eff) continue;
  const table = tableByName[eff.table];
  if (!table) continue;
  const rows = table.sample_rows ?? [];
  const anchor = rows.find((r) => String(r.id) === String(eff.id));
  if (!anchor) continue;
  const cols = table.columns ?? [];
  const [fA, fB] = pickObscureFields(cols, anchor, eff.field);
  if (!fA) continue;

  // ---- 1) obscure the entity reference in the prompt
  const handleCandidates = [anchor[fA], anchor[fB], anchor.company, anchor.contactname, anchor.name]
    .filter((v) => typeof v === "string" && v.length >= 4);
  let prompt = task.prompt ?? "";
  let obscured = false;
  for (const h of handleCandidates) {
    if (prompt.includes(h)) {
      prompt = prompt.split(h).join(`the ${eff.table} record whose ${fA} is "${anchor[fA]}" and whose ${fB} is "${anchor[fB]}"`);
      obscured = true;
      break;
    }
  }
  if (!obscured) {
    prompt += ` The target ${eff.table} record is the one whose ${fA} is "${anchor[fA]}" and whose ${fB} is "${anchor[fB]}".`;
  }
  task.prompt = prompt;

  // ---- 2) distractor rows: share field A and lifecycle status, vary field B
  const maxId = Math.max(0, ...rows.map((r) => Number(r.id)).filter(Number.isFinite));
  for (let n = 1; n <= K; n++) {
    const clone = structuredClone(anchor);
    clone.id = maxId + 100 + n;
    if (fB && fB !== fA) clone[fB] = `${anchor[fB]} ${SUFFIXES[(n - 1) % SUFFIXES.length]}`;
    // keep the same from-status so status-driven searches collide with the distractor
    rows.push(clone);
    distractorsAdded++;
  }
  table.sample_rows = rows;
  table.row_count = (table.row_count ?? rows.length - K) + K;

  escalated.push({ task: task.task_id, table: eff.table, anchorId: eff.id, obscured, fields: [fA, fB], distractors: K });
}

writeFileSync(worldPath, JSON.stringify(raw, null, 1));
writeFileSync(join(OUT, "tasks.jsonl"), (world.tasks ?? []).map((t) => JSON.stringify(t)).join("\n") + "\n");

// rebuild seed + state DBs from the patched world.json
execSync("python3 create_db.py", { cwd: OUT, stdio: "inherit" });
execSync("cp seed.db state.db", { cwd: OUT });

console.log(`escalated ${escalated.length} tasks (level ${LEVEL}), ${distractorsAdded} distractor rows added`);
for (const e of escalated.slice(0, 30)) {
  console.log(`  ${e.task}: ${e.table}#${e.anchorId} obscured=${e.obscured} via [${e.fields.join(", ")}] +${e.distractors} distractors`);
}
console.log(`package: ${OUT}`);
