#!/usr/bin/env node
/**
 * Seed the wave-6 world's document store with the anchor corpus.
 *
 * Coverage-audit finding (2026-08-10): the wave-6 build materialized the 46
 * anchor docs as table SCHEMAS (meddic_*, suppression_*, renewal_* ...) but the
 * readable policy text itself did not survive — agent_documents has 2 rows vs
 * wave-5's 38. Document-grounded evals (knowledge QA, policy compliance,
 * battlecard objection handling, contract-term extraction, transcript mining)
 * need the text in-world. This script inserts every anchor doc into
 * agent_documents in world.json AND the packaged seed, then rebuilds state.db.
 *
 * Idempotent: re-running replaces previously seeded rows (title-keyed).
 */
import { readFileSync, writeFileSync, readdirSync, existsSync } from "node:fs";
import { execSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const WORLD_DIR = join(ROOT, "world", "blobfish-wave6");
const PKG = join(WORLD_DIR, "package", "sbx_291042075d7547f4");

const corpus = [];
for (const dir of ["wave2", "wave6"]) {
  const d = join(ROOT, "docs", "anchors", dir);
  for (const f of readdirSync(d).filter((x) => x.endsWith(".md")).sort()) {
    const content = readFileSync(join(d, f), "utf8");
    const title = (content.match(/^#\s+(.+)$/m)?.[1] ?? f.replace(/\.md$/, "")).trim();
    corpus.push({ file: f, title, body: content });
  }
}

for (const worldPath of [join(WORLD_DIR, "world.json"), join(PKG, "world.json")].filter(existsSync)) {
  const raw = JSON.parse(readFileSync(worldPath, "utf8"));
  const world = raw.world ?? raw;
  const docs = world.tables.find((t) => t.name === "agent_documents");
  if (!docs) throw new Error(`no agent_documents table in ${worldPath}`);
  docs.sample_rows ??= [];
  // drop rows we seeded before (marker in updated_at), keep organic rows
  docs.sample_rows = docs.sample_rows.filter((r) => r.updated_at !== "2026-08-10T12:00:00Z");
  let id = Math.max(0, ...docs.sample_rows.map((r) => Number(r.id) || 0));
  for (const doc of corpus) {
    docs.sample_rows.push({ id: ++id, title: doc.title, body: doc.body, updated_at: "2026-08-10T12:00:00Z" });
  }
  docs.row_count = docs.sample_rows.length;
  writeFileSync(worldPath, JSON.stringify(raw, null, 1));
  console.log(`${worldPath}: agent_documents -> ${docs.row_count} rows (+${corpus.length} anchors)`);
}

// rebuild the packaged DBs from the updated world.json
execSync("python3 create_db.py && cp seed.db state.db", { cwd: PKG, stdio: "inherit" });
console.log("package seed.db/state.db rebuilt — restart the server to serve the new corpus");
