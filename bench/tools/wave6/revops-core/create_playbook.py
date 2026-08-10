"""Insert one agent_playbooks record"""
import sqlite3

def create_playbook(db_path, name=None, steps=None, **kwargs):
    if not name:
        return {"error": "validation_error", "message": "name is required"}
    if not steps:
        return {"error": "validation_error", "message": "steps is required"}
    conn = sqlite3.connect(db_path)
    next_id = (conn.execute("SELECT MAX(id) FROM agent_playbooks").fetchone()[0] or 0) + 1
    conn.execute("INSERT INTO agent_playbooks (id, name, steps, created_at) VALUES (?, ?, ?, datetime('now'))",
                 (next_id, name, steps))
    conn.commit()
    conn.close()
    return {"status": "saved", "table": "agent_playbooks", "id": next_id}