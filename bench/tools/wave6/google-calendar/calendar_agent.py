"""Free-text scheduling sub-agent. Verbs: schedule "T" on YYYY-MM-DD · read events."""
import re, sqlite3

def calendar_agent(db_path, request=None, **kwargs):
    if not request or not str(request).strip():
        return {"error": "validation_error", "message": "request is required — describe the scheduling action"}
    req = str(request).strip()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        if re.search(r'^\s*read\s+events', req, re.I):
            rows = [dict(r) for r in conn.execute("SELECT * FROM agent_events ORDER BY event_date LIMIT 100").fetchall()]
            return {"count": len(rows), "rows": rows}
        m = re.search(r'^\s*(?:schedule|create\s+event)\s+"([^"]+)"(?:\s+on\s+(\d{4}-\d{2}-\d{2}))?', req, re.I)
        title = m.group(1).strip() if m else re.sub(r'\s+', ' ', req)[:80]
        event_date = (m.group(2) if m and m.group(2) else "")
        next_id = (conn.execute("SELECT MAX(id) FROM agent_events").fetchone()[0] or 0) + 1
        conn.execute("INSERT INTO agent_events (id, title, event_date, created_at) VALUES (?, ?, ?, datetime('now'))", (next_id, title, event_date))
        conn.commit()
        return {"status": "scheduled", "event": title, "event_id": next_id, "event_date": event_date or "unspecified"}
    finally:
        conn.close()