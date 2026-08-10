"""Free-text document sub-agent. Verbs: create doc "T": <body> · append to "T": <text> · read "T"."""
import hashlib, re, sqlite3

_AMBIGUOUS_PCT = 15

def _ambiguous(req, pct):
    if pct <= 0:
        return False
    digest = int(hashlib.sha256(req.encode('utf-8', 'ignore')).hexdigest()[:8], 16)
    return (digest % 100) < pct

def _doc_by_title(conn, title):
    return conn.execute("SELECT * FROM agent_documents WHERE title = ?", (title,)).fetchone()

def document_agent(db_path, request=None, **kwargs):
    if not request or not str(request).strip():
        return {"error": "validation_error", "message": "request is required — describe what the document agent should do"}
    req = str(request).strip()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        m = re.search(r'^\s*create\s+(?:a\s+)?doc(?:ument)?\s+"([^"]+)"\s*:?\s*(.*)$', req, re.I | re.S)
        if m:
            title, body = m.group(1).strip(), m.group(2).strip()
            if _doc_by_title(conn, title):
                return {"error": "already_exists", "message": "document %r already exists — use append" % title}
            next_id = (conn.execute("SELECT MAX(id) FROM agent_documents").fetchone()[0] or 0) + 1
            conn.execute("INSERT INTO agent_documents (id, title, body, updated_at) VALUES (?, ?, ?, datetime('now'))", (next_id, title, body))
            conn.commit()
            if _ambiguous(req, _AMBIGUOUS_PCT):
                return {"output": None}
            return {"status": "created", "doc": title, "doc_id": next_id, "chars": len(body)}
        m = re.search(r'^\s*append\s+to\s+"([^"]+)"\s*:?\s*(.+)$', req, re.I | re.S)
        if m:
            title, text = m.group(1).strip(), m.group(2).strip()
            doc = _doc_by_title(conn, title)
            if doc is None:
                return {"error": "not_found", "message": "no document titled %r" % title}
            body = (doc["body"] or "") + "\n" + text
            conn.execute("UPDATE agent_documents SET body = ?, updated_at = datetime('now') WHERE id = ?", (body, doc["id"]))
            conn.commit()
            if _ambiguous(req, _AMBIGUOUS_PCT):
                return {"output": None}
            return {"status": "appended", "doc": title, "chars": len(body)}
        m = re.search(r'^\s*read\s+"([^"]+)"', req, re.I)
        if m:
            doc = _doc_by_title(conn, m.group(1).strip())
            if doc is None:
                return {"error": "not_found", "message": "no document titled %r" % m.group(1).strip()}
            return {"doc": doc["title"], "body": doc["body"], "updated_at": doc["updated_at"]}
        # Loose interpretation: draft a new document from the request text.
        title = re.sub(r"\s+", " ", req)[:80]
        if _doc_by_title(conn, title):
            return {"status": "already_exists", "doc": title}
        next_id = (conn.execute("SELECT MAX(id) FROM agent_documents").fetchone()[0] or 0) + 1
        conn.execute("INSERT INTO agent_documents (id, title, body, updated_at) VALUES (?, ?, ?, datetime('now'))", (next_id, title, req))
        conn.commit()
        return {"status": "created", "doc": title, "doc_id": next_id,
                "hint": "verbs: create doc \"T\": <body> · append to \"T\": <text> · read \"T\""}
    finally:
        conn.close()