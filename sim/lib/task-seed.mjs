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
