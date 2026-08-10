"""Executable NOTION tool module

Inspect each function: SQLite helpers are local fixtures; network-backed functions call their declared endpoint.
Tools: read_file, query_documents, document_agent, read_matter_document, draft_matter_document, query_matter_documents
Tables: agent_files, agent_documents, matter_documents
"""
import json, sqlite3
"""Read a seeded document fixture (CSV/TSV) by filename"""
import sqlite3

def read_file(db_path, filename=None, **kwargs):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    if not filename:
        names = [r["filename"] for r in conn.execute("SELECT filename FROM agent_files ORDER BY id").fetchall()]
        conn.close()
        return {"error": "validation_error", "message": "filename is required; available files: %r" % names}
    row = conn.execute("SELECT * FROM agent_files WHERE filename = ?", (filename,)).fetchone()
    if row is None:
        names = [r["filename"] for r in conn.execute("SELECT filename FROM agent_files ORDER BY id").fetchall()]
        conn.close()
        return {"error": "not_found", "message": "no file named %r; available files: %r" % (filename, names)}
    conn.close()
    return {"filename": row["filename"], "content_type": row["content_type"], "content": row["content"], "rows": [dict(row)]}

"""Search agent_documents records by free text"""
import sqlite3

def query_documents(db_path, query=None, limit=50, **kwargs):
    try:
        bounded_limit = max(1, min(int(limit), 200))
    except (TypeError, ValueError):
        return {"error": "validation_error", "message": "limit must be an integer"}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    if query is None or not str(query).strip():
        rows = [dict(r) for r in conn.execute('SELECT * FROM agent_documents ORDER BY id LIMIT ?', (bounded_limit,)).fetchall()]
    else:
        pattern = '%' + str(query).strip() + '%'
        rows = [dict(r) for r in conn.execute('SELECT * FROM agent_documents WHERE title LIKE ? OR body LIKE ? ORDER BY id LIMIT ?', (pattern, pattern, bounded_limit)).fetchall()]
    conn.close()
    return {"table": "agent_documents", "query": query, "count": len(rows), "rows": rows}

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

def read_matter_document(db_path, id):
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM matter_documents WHERE id = ?', (id,)).fetchone()
    conn.close()
    return dict(row) if row else None

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_read_matter_document = read_matter_document
def _bf_friction_read_matter_document(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_read_matter_document(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "read_matter_document|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("3ba25889bd4c5d1d|" + _bf_sig).encode("utf-8")).hexdigest()
    if int(_bf_digest[:8], 16) / 4294967296.0 < 0.03:
        _bf_conn = _bf_sqlite3.connect(_bf_db + ".bf-friction")
        try:
            _bf_conn.execute('CREATE TABLE IF NOT EXISTS attempts (sig TEXT PRIMARY KEY, n INTEGER NOT NULL)')
            _bf_conn.execute('INSERT INTO attempts (sig, n) VALUES (?, 1) ON CONFLICT(sig) DO UPDATE SET n = n + 1', (_bf_sig,))
            _bf_conn.commit()
            _bf_n = _bf_conn.execute('SELECT n FROM attempts WHERE sig = ?', (_bf_sig,)).fetchone()[0]
        finally:
            _bf_conn.close()
        if _bf_n == 1:
            _bf_kinds = ["service_unavailable","rate_limited","stale_reference"]
            _bf_messages = {"service_unavailable":"The service is temporarily unavailable (upstream timeout while processing the request). Please retry.","rate_limited":"Rate limit exceeded for this operation. Wait a moment and retry.","stale_reference":"The referenced record could not be loaded — the reference may be stale or recently changed. Re-fetch the latest data and retry."}
            _bf_kind = _bf_kinds[int(_bf_digest[8:12], 16) % len(_bf_kinds)]
            return {"success": False, "error": _bf_kind, "message": _bf_messages[_bf_kind], "retryable": True}
    return _bf_orig_read_matter_document(*_bf_args, **_bf_kwargs)
_bf_friction_read_matter_document.blobfish_original = _bf_orig_read_matter_document
read_matter_document = _bf_friction_read_matter_document

def draft_matter_document(db_path, title, doc_type, body):
    import sqlite3
    conn = sqlite3.connect(db_path)
    cur = conn.execute('INSERT INTO matter_documents (title, doc_type, related_shape, body) VALUES (?, ?, ?, ?)', (title, doc_type, 'deliverable', body))
    conn.commit()
    conn.close()
    return {'id': cur.lastrowid, 'title': title, 'doc_type': doc_type}

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_draft_matter_document = draft_matter_document
def _bf_friction_draft_matter_document(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_draft_matter_document(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "draft_matter_document|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("3ba25889bd4c5d1d|" + _bf_sig).encode("utf-8")).hexdigest()
    if int(_bf_digest[:8], 16) / 4294967296.0 < 0.03:
        _bf_conn = _bf_sqlite3.connect(_bf_db + ".bf-friction")
        try:
            _bf_conn.execute('CREATE TABLE IF NOT EXISTS attempts (sig TEXT PRIMARY KEY, n INTEGER NOT NULL)')
            _bf_conn.execute('INSERT INTO attempts (sig, n) VALUES (?, 1) ON CONFLICT(sig) DO UPDATE SET n = n + 1', (_bf_sig,))
            _bf_conn.commit()
            _bf_n = _bf_conn.execute('SELECT n FROM attempts WHERE sig = ?', (_bf_sig,)).fetchone()[0]
        finally:
            _bf_conn.close()
        if _bf_n == 1:
            _bf_kinds = ["service_unavailable","rate_limited","stale_reference"]
            _bf_messages = {"service_unavailable":"The service is temporarily unavailable (upstream timeout while processing the request). Please retry.","rate_limited":"Rate limit exceeded for this operation. Wait a moment and retry.","stale_reference":"The referenced record could not be loaded — the reference may be stale or recently changed. Re-fetch the latest data and retry."}
            _bf_kind = _bf_kinds[int(_bf_digest[8:12], 16) % len(_bf_kinds)]
            return {"success": False, "error": _bf_kind, "message": _bf_messages[_bf_kind], "retryable": True}
    return _bf_orig_draft_matter_document(*_bf_args, **_bf_kwargs)
_bf_friction_draft_matter_document.blobfish_original = _bf_orig_draft_matter_document
draft_matter_document = _bf_friction_draft_matter_document

def query_matter_documents(db_path, title=None, doc_type=None, related_shape=None, limit=20):
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    clauses, params = [], []
    if title:
        clauses.append('title LIKE ?'); params.append('%' + str(title) + '%')
    if doc_type:
        clauses.append('doc_type = ?'); params.append(doc_type)
    if related_shape:
        clauses.append('related_shape LIKE ?'); params.append('%' + str(related_shape) + '%')
    where = (' WHERE ' + ' AND '.join(clauses)) if clauses else ''
    rows = conn.execute('SELECT id, title, doc_type, related_shape FROM matter_documents' + where + ' ORDER BY id LIMIT ?', (*params, int(limit))).fetchall()
    conn.close()
    return {'table': 'matter_documents', 'count': len(rows), 'rows': [dict(r) for r in rows]}

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_query_matter_documents = query_matter_documents
def _bf_friction_query_matter_documents(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_query_matter_documents(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "query_matter_documents|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("3ba25889bd4c5d1d|" + _bf_sig).encode("utf-8")).hexdigest()
    if int(_bf_digest[:8], 16) / 4294967296.0 < 0.03:
        _bf_conn = _bf_sqlite3.connect(_bf_db + ".bf-friction")
        try:
            _bf_conn.execute('CREATE TABLE IF NOT EXISTS attempts (sig TEXT PRIMARY KEY, n INTEGER NOT NULL)')
            _bf_conn.execute('INSERT INTO attempts (sig, n) VALUES (?, 1) ON CONFLICT(sig) DO UPDATE SET n = n + 1', (_bf_sig,))
            _bf_conn.commit()
            _bf_n = _bf_conn.execute('SELECT n FROM attempts WHERE sig = ?', (_bf_sig,)).fetchone()[0]
        finally:
            _bf_conn.close()
        if _bf_n == 1:
            _bf_kinds = ["service_unavailable","rate_limited"]
            _bf_messages = {"service_unavailable":"The service is temporarily unavailable (upstream timeout while processing the request). Please retry.","rate_limited":"Rate limit exceeded for this operation. Wait a moment and retry."}
            _bf_kind = _bf_kinds[int(_bf_digest[8:12], 16) % len(_bf_kinds)]
            return {"success": False, "error": _bf_kind, "message": _bf_messages[_bf_kind], "retryable": True}
    return _bf_orig_query_matter_documents(*_bf_args, **_bf_kwargs)
_bf_friction_query_matter_documents.blobfish_original = _bf_orig_query_matter_documents
query_matter_documents = _bf_friction_query_matter_documents

