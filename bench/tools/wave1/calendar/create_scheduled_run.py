"""Insert one agent_scheduled_runs record"""
import sqlite3

def create_scheduled_run(db_path, name=None, schedule=None, playbook_name=None, **kwargs):
    if not name:
        return {"error": "validation_error", "message": "name is required"}
    if not schedule:
        return {"error": "validation_error", "message": "schedule is required"}
    conn = sqlite3.connect(db_path)
    next_id = (conn.execute("SELECT MAX(id) FROM agent_scheduled_runs").fetchone()[0] or 0) + 1
    conn.execute("INSERT INTO agent_scheduled_runs (id, name, schedule, playbook_name, status, created_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
                 (next_id, name, schedule, playbook_name, "scheduled"))
    conn.commit()
    conn.close()
    return {"status": "saved", "table": "agent_scheduled_runs", "id": next_id}