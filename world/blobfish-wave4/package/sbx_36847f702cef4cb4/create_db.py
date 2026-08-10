import sqlite3, json, os, sys

def create_seed_db(db_path: str, world: dict) -> None:
    conn = sqlite3.connect(db_path)
    for table in world.get('tables', []):
        cols = table.get('columns', [])
        col_defs = []
        for c in cols:
            parts = [f'"{c["name"]}"', c.get("type", "TEXT")]
            if c.get("pk"): parts.append("PRIMARY KEY")
            col_defs.append(' '.join(parts))
        ddl = f'CREATE TABLE IF NOT EXISTS "{table["name"]}" ({", ".join(col_defs)})'
        conn.execute(ddl)
        for row in table.get('sample_rows', []):
            names = [c['name'] for c in cols if c['name'] in row]
            placeholders = ', '.join(['?'] * len(names))
            col_names = ', '.join([f'"' + n + '"' for n in names])
            vals = [row.get(n) for n in names]
            try:
                conn.execute(f'INSERT OR IGNORE INTO "{table["name"]}" ({col_names}) VALUES ({placeholders})', [json.dumps(v) if isinstance(v, (dict,list)) else v for v in vals])
            except Exception:
                pass
    conn.execute('CREATE TABLE IF NOT EXISTS "_forge_actions" ("id" TEXT PRIMARY KEY, "operation" TEXT NOT NULL, "action" TEXT NOT NULL, "target" TEXT, "payload" TEXT, "created_at" TEXT NOT NULL)')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    import shutil
    world_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "world.json")
    with open(world_path) as f: world = json.load(f)
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seed.db")
    if os.path.exists(db_path): os.remove(db_path)
    create_seed_db(db_path, world)
    shutil.copy2(db_path, os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.db"))
    print(f"Created seed.db with {len(world.get('tables', []))} tables")
