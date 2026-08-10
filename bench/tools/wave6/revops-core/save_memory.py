"""Insert one agent_memories record"""
import sqlite3

def save_memory(db_path, content=None, **kwargs):
    if not content:
        return {"error": "validation_error", "message": "content is required"}
    conn = sqlite3.connect(db_path)
    next_id = (conn.execute("SELECT MAX(id) FROM agent_memories").fetchone()[0] or 0) + 1
    conn.execute("INSERT INTO agent_memories (id, content, created_at) VALUES (?, ?, datetime('now'))",
                 (next_id, content))
    conn.commit()
    conn.close()
    return {"status": "saved", "table": "agent_memories", "id": next_id}