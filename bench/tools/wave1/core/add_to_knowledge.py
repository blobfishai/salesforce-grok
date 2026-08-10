"""Insert one agent_knowledge record"""
import sqlite3

def add_to_knowledge(db_path, content=None, source=None, **kwargs):
    if not content:
        return {"error": "validation_error", "message": "content is required"}
    conn = sqlite3.connect(db_path)
    next_id = (conn.execute("SELECT MAX(id) FROM agent_knowledge").fetchone()[0] or 0) + 1
    conn.execute("INSERT INTO agent_knowledge (id, content, source, created_at) VALUES (?, ?, ?, datetime('now'))",
                 (next_id, content, source))
    conn.commit()
    conn.close()
    return {"status": "saved", "table": "agent_knowledge", "id": next_id}