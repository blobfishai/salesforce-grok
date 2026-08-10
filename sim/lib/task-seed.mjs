/**
 * Task-level seed applier (local multi-server mode).
 *
 * A task's fixture bundle (bench/tasks/<world>/<task>.seed.json, schema
 * task-seed.v1) can carry:
 *   rows:            {table: [full row objects]}      -> INSERT OR REPLACE
 *   documents:       [{store, id?, title, body?}]     -> upserted IF body present
 *   input_documents: same shape                        (pointer-only entries are
 *                                                       provenance, skipped)
 *   mcp_seeding:     {namespace: [tool names]}         (informational)
 *
 * Applied directly to the episode's copy-on-write session DB BEFORE the agent
 * starts, so per-task fixtures layer over the world without touching the shared
 * seed. Uses python3+sqlite3 (the package runtime's own stack; node:sqlite is
 * still experimental).
 */
import { existsSync, readFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { join, dirname, basename } from "node:path";

/** bench/tasks/<worldKey>/<taskId>.seed.json for a given world file path. */
export function resolveTaskSeedPath(ROOT, worldFilePath, taskId) {
  const dir = basename(dirname(worldFilePath));           // e.g. blobfish-wave6
  const key = dir.replace(/^blobfish-?/, "") || "wave1";  // -> wave6 ('' for canonical)
  const p = join(ROOT, "bench", "tasks", key === "" ? "wave1" : key, `${taskId}.seed.json`);
  return existsSync(p) ? p : null;
}

/** The session's copy-on-write sqlite file inside the world package. */
export function sessionDbPath(ROOT, worldFilePath, worldId, sessionId) {
  return join(dirname(join(ROOT, worldFilePath)), "package", worldId, ".sessions", `${sessionId}.db`);
}

const PY = `
import json, sqlite3, sys
bundle = json.load(sys.stdin)
db = sys.argv[1]
conn = sqlite3.connect(db)
cur = conn.cursor()
applied = {"rows": 0, "documents": 0, "skipped": 0}
def upsert(table, row):
    cols = list(row.keys())
    try:
        cur.execute(f'INSERT OR REPLACE INTO "{table}" ({",".join(chr(34)+c+chr(34) for c in cols)}) VALUES ({",".join("?"*len(cols))})',
                    [json.dumps(v) if isinstance(v,(dict,list)) else v for v in row.values()])
        return True
    except Exception as e:
        print(f"skip {table}: {e}", file=sys.stderr)
        return False
for table, rows in (bundle.get("rows") or {}).items():
    for row in rows:
        applied["rows" if upsert(table, row) else "skipped"] += 1
for key in ("documents", "input_documents"):
    for d in (bundle.get(key) or []):
        if not d.get("body"):
            applied["skipped"] += 1
            continue
        row = {"title": d.get("title", ""), "body": d["body"]}
        if d.get("id") is not None: row["id"] = d["id"]
        store = d.get("store", "agent_documents")
        applied["documents" if upsert(store, row) else "skipped"] += 1
conn.commit()
print(json.dumps(applied))
`;

/** Apply a bundle to a session DB. Returns {rows, documents, skipped} or throws. */
export function applyTaskSeed(bundlePath, dbPath) {
  if (!existsSync(dbPath)) throw new Error(`session db not found: ${dbPath}`);
  const bundle = readFileSync(bundlePath, "utf8");
  const r = spawnSync("python3", ["-c", PY, dbPath], { input: bundle, encoding: "utf8", timeout: 30000 });
  if (r.status !== 0) throw new Error(`task-seed apply failed: ${r.stderr?.slice(0, 400)}`);
  return JSON.parse(r.stdout.trim().split("\n").pop());
}

const SNAP_PY = `
import json, sqlite3, sys
conn = sqlite3.connect(sys.argv[1]); conn.row_factory = sqlite3.Row
only = set(json.loads(sys.argv[3])) if len(sys.argv) > 3 and sys.argv[3] else None
out = {}
for (name,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall():
    if only is not None and name not in only: continue
    rows = {}
    for row in conn.execute(f'SELECT rowid AS _r_, * FROM "{name}"'):
        d = dict(row); rid = d.pop("_r_"); rows[rid] = d
    out[name] = rows
json.dump(out, open(sys.argv[2], "w"), default=str)
print("ok")
`;

/** Tables a bundle touches (rows tables + document stores with bodies). */
export function bundleTables(bundlePath) {
  const b = JSON.parse(readFileSync(bundlePath, "utf8"));
  const t = new Set(Object.keys(b.rows ?? {}));
  for (const key of ["documents", "input_documents"]) {
    for (const d of b[key] ?? []) if (d.body) t.add(d.store ?? "agent_documents");
  }
  return [...t];
}

/** Snapshot the post-seed session DB (optionally only the seed-touched tables) —
 *  the per-table verification baseline. Shape matches server snapshot(). */
export function dumpInitialState(dbPath, outPath, onlyTables = null) {
  const args = ["-c", SNAP_PY, dbPath, outPath];
  if (onlyTables) args.push(JSON.stringify(onlyTables));
  const r = spawnSync("python3", args, { encoding: "utf8", timeout: 60000 });
  if (r.status !== 0) throw new Error(`initial-state dump failed: ${r.stderr?.slice(0, 300)}`);
}
