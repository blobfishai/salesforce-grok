"""List agent_scheduled_runs records"""
import sqlite3

def list_scheduled_runs(db_path, limit=50, **kwargs):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute('SELECT * FROM agent_scheduled_runs ORDER BY id LIMIT ?', (min(int(limit), 200),)).fetchall()]
    conn.close()
    return {"table": "agent_scheduled_runs", "count": len(rows), "rows": rows}