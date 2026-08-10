"""Search agent_knowledge records by free text"""
import sqlite3

def search_knowledge(db_path, query=None, limit=50, **kwargs):
    try:
        bounded_limit = max(1, min(int(limit), 200))
    except (TypeError, ValueError):
        return {"error": "validation_error", "message": "limit must be an integer"}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    if query is None or not str(query).strip():
        rows = [dict(r) for r in conn.execute('SELECT * FROM agent_knowledge ORDER BY id LIMIT ?', (bounded_limit,)).fetchall()]
    else:
        pattern = '%' + str(query).strip() + '%'
        rows = [dict(r) for r in conn.execute('SELECT * FROM agent_knowledge WHERE content LIKE ? OR source LIKE ? ORDER BY id LIMIT ?', (pattern, pattern, bounded_limit)).fetchall()]
    conn.close()
    return {"table": "agent_knowledge", "query": query, "count": len(rows), "rows": rows}