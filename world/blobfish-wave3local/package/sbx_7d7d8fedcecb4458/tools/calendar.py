"""Executable CALENDAR tool module

Inspect each function: SQLite helpers are local fixtures; network-backed functions call their declared endpoint.
Tools: list_scheduled_runs, query_calendar_events, calendar_agent, create_scheduled_run
Tables: agent_scheduled_runs, agent_events
"""
import json, sqlite3
"""List agent_scheduled_runs records"""
import sqlite3

def list_scheduled_runs(db_path, limit=50, **kwargs):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute('SELECT * FROM agent_scheduled_runs ORDER BY id LIMIT ?', (min(int(limit), 200),)).fetchall()]
    conn.close()
    return {"table": "agent_scheduled_runs", "count": len(rows), "rows": rows}

"""Search agent_events records by free text"""
import sqlite3

def query_calendar_events(db_path, query=None, limit=50, **kwargs):
    try:
        bounded_limit = max(1, min(int(limit), 200))
    except (TypeError, ValueError):
        return {"error": "validation_error", "message": "limit must be an integer"}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    if query is None or not str(query).strip():
        rows = [dict(r) for r in conn.execute('SELECT * FROM agent_events ORDER BY id LIMIT ?', (bounded_limit,)).fetchall()]
    else:
        pattern = '%' + str(query).strip() + '%'
        rows = [dict(r) for r in conn.execute('SELECT * FROM agent_events WHERE title LIKE ? OR event_date LIKE ? ORDER BY id LIMIT ?', (pattern, pattern, bounded_limit)).fetchall()]
    conn.close()
    return {"table": "agent_events", "query": query, "count": len(rows), "rows": rows}

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

