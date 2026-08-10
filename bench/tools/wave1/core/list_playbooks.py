"""List agent_playbooks records"""
import sqlite3

def list_playbooks(db_path, limit=50, **kwargs):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute('SELECT * FROM agent_playbooks ORDER BY id LIMIT ?', (min(int(limit), 200),)).fetchall()]
    conn.close()
    return {"table": "agent_playbooks", "count": len(rows), "rows": rows}