"""Executable NOTION tool module

Inspect each function: SQLite helpers are local fixtures; network-backed functions call their declared endpoint.
Tools: read_file, query_documents, document_agent, read_matter_document, draft_matter_document, query_matter_documents, notion_search, notion_page_get, notion_page_create, notion_page_update, notion_page_archive, notion_databases_list, notion_page_properties_get, notion_database_get, notion_database_create, notion_database_query, notion_database_row_create, notion_database_row_update, notion_blocks_children_list, notion_blocks_append, notion_block_get, notion_block_delete, notion_comments_list, notion_comment_create, notion_users_list, notion_user_get
Tables: agent_files, agent_documents, matter_documents, notion_pages, notion_databases, notion_database_rows, notion_blocks, notion_comments, notion_users
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

def notion_search(db_path='state.db', **kwargs):
    import sqlite3, json
    query = kwargs.get('query')
    if query is None:
        return {"object": "error", "status": 400, "code": "validation_error",
                "message": "body failed validation: body.query should be defined."}
    flt = kwargs.get('filter') or {}
    if isinstance(flt, str):
        try:
            flt = json.loads(flt)
        except Exception:
            flt = {}
    value = flt.get('value') if isinstance(flt, dict) else None
    sort = kwargs.get('sort') or {}
    if isinstance(sort, str):
        try:
            sort = json.loads(sort)
        except Exception:
            sort = {}
    direction = sort.get('direction', 'descending') if isinstance(sort, dict) else 'descending'
    try:
        offset = int(kwargs.get('start_cursor') or 0)
    except (TypeError, ValueError):
        offset = 0
    try:
        page_size = min(int(kwargs.get('page_size') or 30), 100)
    except (TypeError, ValueError):
        page_size = 30
    like = '%' + str(query) + '%'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    results = []
    if value in (None, 'page'):
        for r in conn.execute("SELECT * FROM notion_pages WHERE archived = 0 AND title LIKE ?", (like,)):
            d = dict(r)
            d['object'] = 'page'
            results.append(d)
    if value in (None, 'database'):
        for r in conn.execute("SELECT * FROM notion_databases WHERE title LIKE ? OR description LIKE ?", (like, like)):
            d = dict(r)
            d['object'] = 'database'
            results.append(d)
    conn.close()
    results.sort(key=lambda d: d.get('last_edited_time') or '', reverse=(direction != 'ascending'))
    window = results[offset:offset + page_size]
    has_more = offset + page_size < len(results)
    return {"object": "list", "results": window, "has_more": has_more,
            "next_cursor": str(offset + page_size) if has_more else None,
            "type": "page_or_database"}

_env_orig_notion_search = notion_search
def _env_notion_search(db_path='state.db', **kwargs):
    _r = _env_orig_notion_search(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'object': 'list', 'results': _r['items'], 'next_cursor': None, 'has_more': False}
    if 'error' in _r and _r.get('status') == 404:
        return {'object': 'error', 'status': 404, 'code': 'object_not_found', 'message': str(_r.get('error', ''))}
    if 'error' in _r and _r.get('status') == 400:
        return {'object': 'error', 'status': 400, 'code': 'validation_error', 'message': str(_r.get('error', ''))}
    return _r
notion_search = _env_notion_search

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notion_search = notion_search
def _bf_friction_notion_search(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notion_search(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notion_search|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notion_search(*_bf_args, **_bf_kwargs)
_bf_friction_notion_search.blobfish_original = _bf_orig_notion_search
notion_search = _bf_friction_notion_search

def notion_page_get(db_path='state.db', **kwargs):
    '''Retrieve a Notion page object using the ID specified (GET /v1/pages/{page_id})'''
    _missing = [p for p in ['page_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'object': 'error', 'status': 400, 'code': 'validation_error', 'message': str(_r.get('error', ''))}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "notion_pages" WHERE "id" = ?', [str(kwargs['page_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'page not found', 'status': 404}
            return {'object': 'error', 'status': 404, 'code': 'object_not_found', 'message': str(_r.get('error', ''))}
        _r = dict(_row)
        _r['object'] = 'page'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notion_page_get = notion_page_get
def _bf_friction_notion_page_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notion_page_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notion_page_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notion_page_get(*_bf_args, **_bf_kwargs)
_bf_friction_notion_page_get.blobfish_original = _bf_orig_notion_page_get
notion_page_get = _bf_friction_notion_page_get

def notion_page_create(db_path='state.db', **kwargs):
    '''Create a new page as a child of an existing page (POST /v1/pages)'''
    _missing = [p for p in ['title'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'object': 'error', 'status': 400, 'code': 'validation_error', 'message': str(_r.get('error', ''))}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "notion_pages"').fetchone()[0] + 1
        _id = 'pg-' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "notion_pages" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'pg-' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('parent_id') is not None:
            _cols.append('parent_id')
            _v = kwargs['parent_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('title') is not None:
            _cols.append('title')
            _v = kwargs['title']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'archived' not in _cols:
            _cols.append('archived')
            _vals.append(0)
        if 'created_by' not in _cols:
            _cols.append('created_by')
            _vals.append('9081a2b3-c4d5-4e67-8192-a3b4c5d6e508')
        if 'created_time' not in _cols:
            _cols.append('created_time')
            _vals.append('2026-08-10T09:00:00.000Z')
        if 'last_edited_time' not in _cols:
            _cols.append('last_edited_time')
            _vals.append('2026-08-10T09:00:00.000Z')
        cur.execute('INSERT INTO "notion_pages" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "notion_pages" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['object'] = 'page'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notion_page_create = notion_page_create
def _bf_friction_notion_page_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notion_page_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notion_page_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notion_page_create(*_bf_args, **_bf_kwargs)
_bf_friction_notion_page_create.blobfish_original = _bf_orig_notion_page_create
notion_page_create = _bf_friction_notion_page_create

def notion_page_update(db_path='state.db', **kwargs):
    '''Update page property values or the archived status for the specified page (PATCH /v1/pages/{page_id})'''
    _missing = [p for p in ['page_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'object': 'error', 'status': 400, 'code': 'validation_error', 'message': str(_r.get('error', ''))}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "notion_pages" WHERE "id" = ?', [str(kwargs['page_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'page not found', 'status': 404}
            return {'object': 'error', 'status': 404, 'code': 'object_not_found', 'message': str(_r.get('error', ''))}
        _sets, _args = [], []
        if kwargs.get('title') is not None:
            _sets.append('"title" = ?')
            _v = kwargs['title']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('archived') is not None:
            _sets.append('"archived" = ?')
            _v = kwargs['archived']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        _sets.append('"last_edited_time" = ?')
        _args.append(datetime.datetime.now(datetime.timezone.utc).isoformat())
        if _sets:
            cur.execute('UPDATE "notion_pages" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['page_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "notion_pages" WHERE "id" = ?', [str(kwargs['page_id'])]).fetchone()
        _r = dict(_row)
        _r['object'] = 'page'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notion_page_update = notion_page_update
def _bf_friction_notion_page_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notion_page_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notion_page_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notion_page_update(*_bf_args, **_bf_kwargs)
_bf_friction_notion_page_update.blobfish_original = _bf_orig_notion_page_update
notion_page_update = _bf_friction_notion_page_update

def notion_page_archive(db_path='state.db', **kwargs):
    '''Archive (move to trash) or restore a page by setting the archived flag (PATCH /v1/pages/{page_id})'''
    _missing = [p for p in ['page_id', 'archived'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'object': 'error', 'status': 400, 'code': 'validation_error', 'message': str(_r.get('error', ''))}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "notion_pages" WHERE "id" = ?', [str(kwargs['page_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'page not found', 'status': 404}
            return {'object': 'error', 'status': 404, 'code': 'object_not_found', 'message': str(_r.get('error', ''))}
        _sets, _args = [], []
        if kwargs.get('archived') is not None:
            _sets.append('"archived" = ?')
            _v = kwargs['archived']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        _sets.append('"last_edited_time" = ?')
        _args.append(datetime.datetime.now(datetime.timezone.utc).isoformat())
        if _sets:
            cur.execute('UPDATE "notion_pages" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['page_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "notion_pages" WHERE "id" = ?', [str(kwargs['page_id'])]).fetchone()
        _r = dict(_row)
        _r['object'] = 'page'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notion_page_archive = notion_page_archive
def _bf_friction_notion_page_archive(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notion_page_archive(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notion_page_archive|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notion_page_archive(*_bf_args, **_bf_kwargs)
_bf_friction_notion_page_archive.blobfish_original = _bf_orig_notion_page_archive
notion_page_archive = _bf_friction_notion_page_archive

def notion_databases_list(db_path='state.db', **kwargs):
    '''List all databases shared with the integration (GET /v1/databases)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "notion_databases"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'object': 'list', 'results': _r['items'], 'next_cursor': None, 'has_more': False}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notion_databases_list = notion_databases_list
def _bf_friction_notion_databases_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notion_databases_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notion_databases_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notion_databases_list(*_bf_args, **_bf_kwargs)
_bf_friction_notion_databases_list.blobfish_original = _bf_orig_notion_databases_list
notion_databases_list = _bf_friction_notion_databases_list

def notion_page_properties_get(db_path='state.db', **kwargs):
    import sqlite3, json
    page_id = kwargs.get('page_id')
    if not page_id:
        return {"object": "error", "status": 400, "code": "validation_error",
                "message": "path failed validation: path.page_id should be defined."}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM notion_database_rows WHERE id = ?", (page_id,)).fetchone()
    conn.close()
    if row is None:
        return {"object": "error", "status": 404, "code": "object_not_found",
                "message": "Could not find page with ID: " + str(page_id) + "."}
    d = dict(row)
    try:
        props = json.loads(d.get('properties') or '{}')
    except Exception:
        props = {}
    property_id = kwargs.get('property_id')
    if property_id is not None:
        if property_id not in props:
            return {"object": "error", "status": 404, "code": "object_not_found",
                    "message": "Could not find property with id or name: " + str(property_id) + "."}
        return {"object": "property_item", "id": property_id, "page_id": page_id,
                "value": props[property_id]}
    return {"object": "page", "id": page_id,
            "parent": {"type": "database_id", "database_id": d.get('database_id')},
            "created_time": d.get('created_time'), "last_edited_time": d.get('last_edited_time'),
            "archived": bool(d.get('archived')), "properties": props}

_env_orig_notion_page_properties_get = notion_page_properties_get
def _env_notion_page_properties_get(db_path='state.db', **kwargs):
    _r = _env_orig_notion_page_properties_get(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'object': 'list', 'results': _r['items'], 'next_cursor': None, 'has_more': False}
    if 'error' in _r and _r.get('status') == 404:
        return {'object': 'error', 'status': 404, 'code': 'object_not_found', 'message': str(_r.get('error', ''))}
    if 'error' in _r and _r.get('status') == 400:
        return {'object': 'error', 'status': 400, 'code': 'validation_error', 'message': str(_r.get('error', ''))}
    return _r
notion_page_properties_get = _env_notion_page_properties_get

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notion_page_properties_get = notion_page_properties_get
def _bf_friction_notion_page_properties_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notion_page_properties_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notion_page_properties_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notion_page_properties_get(*_bf_args, **_bf_kwargs)
_bf_friction_notion_page_properties_get.blobfish_original = _bf_orig_notion_page_properties_get
notion_page_properties_get = _bf_friction_notion_page_properties_get

def notion_database_get(db_path='state.db', **kwargs):
    '''Retrieve a database object, including its property schema, for the provided ID (GET /v1/databases/{database_id})'''
    _missing = [p for p in ['database_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'object': 'error', 'status': 400, 'code': 'validation_error', 'message': str(_r.get('error', ''))}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "notion_databases" WHERE "id" = ?', [str(kwargs['database_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'database not found', 'status': 404}
            return {'object': 'error', 'status': 404, 'code': 'object_not_found', 'message': str(_r.get('error', ''))}
        _r = dict(_row)
        _r['object'] = 'database'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notion_database_get = notion_database_get
def _bf_friction_notion_database_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notion_database_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notion_database_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notion_database_get(*_bf_args, **_bf_kwargs)
_bf_friction_notion_database_get.blobfish_original = _bf_orig_notion_database_get
notion_database_get = _bf_friction_notion_database_get

def notion_database_create(db_path='state.db', **kwargs):
    '''Create a database as a subpage in the specified parent page, with the defined property schema (POST /v1/databases)'''
    _missing = [p for p in ['title', 'properties'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'object': 'error', 'status': 400, 'code': 'validation_error', 'message': str(_r.get('error', ''))}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "notion_databases"').fetchone()[0] + 1
        _id = 'db-' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "notion_databases" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'db-' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('parent_id') is not None:
            _cols.append('parent_id')
            _v = kwargs['parent_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('title') is not None:
            _cols.append('title')
            _v = kwargs['title']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('description') is not None:
            _cols.append('description')
            _v = kwargs['description']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('properties') is not None:
            _cols.append('properties')
            _v = kwargs['properties']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'created_time' not in _cols:
            _cols.append('created_time')
            _vals.append('2026-08-10T09:00:00.000Z')
        if 'last_edited_time' not in _cols:
            _cols.append('last_edited_time')
            _vals.append('2026-08-10T09:00:00.000Z')
        cur.execute('INSERT INTO "notion_databases" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "notion_databases" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['object'] = 'database'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notion_database_create = notion_database_create
def _bf_friction_notion_database_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notion_database_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notion_database_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notion_database_create(*_bf_args, **_bf_kwargs)
_bf_friction_notion_database_create.blobfish_original = _bf_orig_notion_database_create
notion_database_create = _bf_friction_notion_database_create

def notion_database_query(db_path='state.db', **kwargs):
    import sqlite3, json
    database_id = kwargs.get('database_id')
    if not database_id:
        return {"object": "error", "status": 400, "code": "validation_error",
                "message": "path failed validation: path.database_id should be defined."}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    db_row = conn.execute("SELECT id FROM notion_databases WHERE id = ?", (database_id,)).fetchone()
    if db_row is None:
        conn.close()
        return {"object": "error", "status": 404, "code": "object_not_found",
                "message": "Could not find database with ID: " + str(database_id) + "."}
    flt = kwargs.get('filter')
    if isinstance(flt, str):
        try:
            flt = json.loads(flt)
        except Exception:
            flt = None

    def leaf_match(props, cond):
        prop = cond.get('property')
        if prop is None:
            return True
        val = props.get(prop)
        if isinstance(val, list):
            sval = ' '.join(str(v) for v in val)
        else:
            sval = '' if val is None else str(val)
        body = None
        for k, v in cond.items():
            if k != 'property' and isinstance(v, dict):
                body = v
        if body is None:
            body = dict((k, v) for k, v in cond.items() if k != 'property')
        for op, target in body.items():
            t = str(target)
            if op == 'equals' and sval != t:
                return False
            if op == 'does_not_equal' and sval == t:
                return False
            if op == 'contains' and t.lower() not in sval.lower():
                return False
            if op == 'does_not_contain' and t.lower() in sval.lower():
                return False
        return True

    def match(props, f):
        if not isinstance(f, dict) or not f:
            return True
        if 'and' in f:
            return all(match(props, c) for c in f['and'])
        if 'or' in f:
            return any(match(props, c) for c in f['or'])
        return leaf_match(props, f)

    rows = []
    for r in conn.execute("SELECT * FROM notion_database_rows WHERE database_id = ? AND archived = 0", (database_id,)):
        d = dict(r)
        try:
            props = json.loads(d.get('properties') or '{}')
        except Exception:
            props = {}
        if match(props, flt):
            d['object'] = 'page'
            d['parent'] = {"type": "database_id", "database_id": database_id}
            rows.append(d)
    conn.close()
    sorts = kwargs.get('sorts')
    if isinstance(sorts, str):
        try:
            sorts = json.loads(sorts)
        except Exception:
            sorts = None
    if isinstance(sorts, dict):
        sorts = [sorts]
    if isinstance(sorts, list):
        for s in reversed([s for s in sorts if isinstance(s, dict)]):
            prop = s.get('property')
            ts = s.get('timestamp')
            rev = s.get('direction') == 'descending'
            if ts in ('created_time', 'last_edited_time'):
                rows.sort(key=lambda d: d.get(ts) or '', reverse=rev)
            elif prop:
                def sort_key(d, prop=prop):
                    try:
                        v = json.loads(d.get('properties') or '{}').get(prop)
                    except Exception:
                        v = None
                    return '' if v is None else str(v)
                rows.sort(key=sort_key, reverse=rev)
    try:
        offset = int(kwargs.get('start_cursor') or 0)
    except (TypeError, ValueError):
        offset = 0
    try:
        page_size = min(int(kwargs.get('page_size') or 30), 100)
    except (TypeError, ValueError):
        page_size = 30
    window = rows[offset:offset + page_size]
    has_more = offset + page_size < len(rows)
    return {"object": "list", "results": window, "has_more": has_more,
            "next_cursor": str(offset + page_size) if has_more else None, "type": "page"}

_env_orig_notion_database_query = notion_database_query
def _env_notion_database_query(db_path='state.db', **kwargs):
    _r = _env_orig_notion_database_query(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'object': 'list', 'results': _r['items'], 'next_cursor': None, 'has_more': False}
    if 'error' in _r and _r.get('status') == 404:
        return {'object': 'error', 'status': 404, 'code': 'object_not_found', 'message': str(_r.get('error', ''))}
    if 'error' in _r and _r.get('status') == 400:
        return {'object': 'error', 'status': 400, 'code': 'validation_error', 'message': str(_r.get('error', ''))}
    return _r
notion_database_query = _env_notion_database_query

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notion_database_query = notion_database_query
def _bf_friction_notion_database_query(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notion_database_query(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notion_database_query|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notion_database_query(*_bf_args, **_bf_kwargs)
_bf_friction_notion_database_query.blobfish_original = _bf_orig_notion_database_query
notion_database_query = _bf_friction_notion_database_query

def notion_database_row_create(db_path='state.db', **kwargs):
    '''Create a new page (row) in the specified database with the given property values (POST /v1/pages with parent.database_id)'''
    _missing = [p for p in ['database_id', 'properties'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'object': 'error', 'status': 400, 'code': 'validation_error', 'message': str(_r.get('error', ''))}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "notion_database_rows"').fetchone()[0] + 1
        _id = 'row-' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "notion_database_rows" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'row-' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('database_id') is not None:
            _cols.append('database_id')
            _v = kwargs['database_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('properties') is not None:
            _cols.append('properties')
            _v = kwargs['properties']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'archived' not in _cols:
            _cols.append('archived')
            _vals.append(0)
        if 'created_by' not in _cols:
            _cols.append('created_by')
            _vals.append('9081a2b3-c4d5-4e67-8192-a3b4c5d6e508')
        if 'created_time' not in _cols:
            _cols.append('created_time')
            _vals.append('2026-08-10T09:00:00.000Z')
        if 'last_edited_time' not in _cols:
            _cols.append('last_edited_time')
            _vals.append('2026-08-10T09:00:00.000Z')
        cur.execute('INSERT INTO "notion_database_rows" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "notion_database_rows" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['object'] = 'database_row'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notion_database_row_create = notion_database_row_create
def _bf_friction_notion_database_row_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notion_database_row_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notion_database_row_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notion_database_row_create(*_bf_args, **_bf_kwargs)
_bf_friction_notion_database_row_create.blobfish_original = _bf_orig_notion_database_row_create
notion_database_row_create = _bf_friction_notion_database_row_create

def notion_database_row_update(db_path='state.db', **kwargs):
    '''Update property values or the archived status of a database page (row) (PATCH /v1/pages/{page_id})'''
    _missing = [p for p in ['page_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'object': 'error', 'status': 400, 'code': 'validation_error', 'message': str(_r.get('error', ''))}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "notion_database_rows" WHERE "id" = ?', [str(kwargs['page_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'database_row not found', 'status': 404}
            return {'object': 'error', 'status': 404, 'code': 'object_not_found', 'message': str(_r.get('error', ''))}
        _sets, _args = [], []
        if kwargs.get('properties') is not None:
            _sets.append('"properties" = ?')
            _v = kwargs['properties']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('archived') is not None:
            _sets.append('"archived" = ?')
            _v = kwargs['archived']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        _sets.append('"last_edited_time" = ?')
        _args.append(datetime.datetime.now(datetime.timezone.utc).isoformat())
        if _sets:
            cur.execute('UPDATE "notion_database_rows" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['page_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "notion_database_rows" WHERE "id" = ?', [str(kwargs['page_id'])]).fetchone()
        _r = dict(_row)
        _r['object'] = 'database_row'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notion_database_row_update = notion_database_row_update
def _bf_friction_notion_database_row_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notion_database_row_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notion_database_row_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notion_database_row_update(*_bf_args, **_bf_kwargs)
_bf_friction_notion_database_row_update.blobfish_original = _bf_orig_notion_database_row_update
notion_database_row_update = _bf_friction_notion_database_row_update

def notion_blocks_children_list(db_path='state.db', **kwargs):
    '''Return a paginated array of child block objects contained in the block (page) specified (GET /v1/blocks/{block_id}/children)'''
    _missing = [p for p in ['block_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'object': 'error', 'status': 400, 'code': 'validation_error', 'message': str(_r.get('error', ''))}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('block_id') is not None:
            _where.append('"page_id" = ?')
            _args.append(str(kwargs['block_id']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "notion_blocks"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'object': 'list', 'results': _r['items'], 'next_cursor': None, 'has_more': False}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notion_blocks_children_list = notion_blocks_children_list
def _bf_friction_notion_blocks_children_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notion_blocks_children_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notion_blocks_children_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notion_blocks_children_list(*_bf_args, **_bf_kwargs)
_bf_friction_notion_blocks_children_list.blobfish_original = _bf_orig_notion_blocks_children_list
notion_blocks_children_list = _bf_friction_notion_blocks_children_list

def notion_blocks_append(db_path='state.db', **kwargs):
    import sqlite3, json, hashlib, datetime
    block_id = kwargs.get('block_id')
    children = kwargs.get('children')
    if not block_id or children is None:
        return {"object": "error", "status": 400, "code": "validation_error",
                "message": "body failed validation: path.block_id and body.children should be defined."}
    if isinstance(children, str):
        try:
            children = json.loads(children)
        except Exception:
            return {"object": "error", "status": 400, "code": "validation_error",
                    "message": "body.children failed validation: value is not valid JSON."}
    if isinstance(children, dict):
        children = [children]
    if not isinstance(children, list):
        return {"object": "error", "status": 400, "code": "validation_error",
                "message": "body.children failed validation: should be an array of block objects."}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    parent = conn.execute("SELECT id FROM notion_pages WHERE id = ?", (block_id,)).fetchone()
    if parent is None:
        parent = conn.execute("SELECT page_id AS id FROM notion_blocks WHERE id = ?", (block_id,)).fetchone()
    if parent is None:
        conn.close()
        return {"object": "error", "status": 404, "code": "object_not_found",
                "message": "Could not find block with ID: " + str(block_id) + "."}
    page_id = parent['id']
    row = conn.execute("SELECT COALESCE(MAX(sort_order), 0) AS m FROM notion_blocks WHERE page_id = ?", (page_id,)).fetchone()
    order = row['m']
    now = datetime.datetime(2026, 8, 10, 9, 0, 0).isoformat() + '.000Z'
    supported = ('paragraph', 'heading_1', 'heading_2', 'heading_3',
                 'bulleted_list_item', 'numbered_list_item', 'to_do', 'quote', 'callout')
    created = []
    for child in children:
        if not isinstance(child, dict):
            continue
        btype = child.get('type')
        if btype is None:
            for k in child:
                if k in supported:
                    btype = k
                    break
        if btype not in supported:
            btype = 'paragraph'
        body = child.get(btype) if isinstance(child.get(btype), dict) else {}
        text = child.get('text')
        if text is None:
            parts = []
            for rt in (body.get('rich_text') or []):
                if isinstance(rt, dict):
                    parts.append(((rt.get('text') or {}).get('content')) or rt.get('plain_text') or '')
            text = ''.join(parts)
        checked = 1 if (body.get('checked') or child.get('checked')) else 0
        order += 1
        bid = 'blk-' + hashlib.sha1((str(page_id) + '|' + str(order) + '|' + str(text)).encode('utf-8')).hexdigest()[:12]
        conn.execute("INSERT INTO notion_blocks (id, page_id, type, text, checked, sort_order) VALUES (?, ?, ?, ?, ?, ?)",
                     (bid, page_id, btype, text or '', checked, order))
        created.append({"object": "block", "id": bid, "type": btype, "text": text or '',
                        "checked": checked, "sort_order": order,
                        "parent": {"type": "page_id", "page_id": page_id}})
    conn.execute("UPDATE notion_pages SET last_edited_time = ? WHERE id = ?", (now, page_id))
    conn.commit()
    conn.close()
    return {"object": "list", "results": created, "has_more": False, "next_cursor": None, "type": "block"}

_env_orig_notion_blocks_append = notion_blocks_append
def _env_notion_blocks_append(db_path='state.db', **kwargs):
    _r = _env_orig_notion_blocks_append(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'object': 'list', 'results': _r['items'], 'next_cursor': None, 'has_more': False}
    if 'error' in _r and _r.get('status') == 404:
        return {'object': 'error', 'status': 404, 'code': 'object_not_found', 'message': str(_r.get('error', ''))}
    if 'error' in _r and _r.get('status') == 400:
        return {'object': 'error', 'status': 400, 'code': 'validation_error', 'message': str(_r.get('error', ''))}
    return _r
notion_blocks_append = _env_notion_blocks_append

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notion_blocks_append = notion_blocks_append
def _bf_friction_notion_blocks_append(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notion_blocks_append(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notion_blocks_append|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notion_blocks_append(*_bf_args, **_bf_kwargs)
_bf_friction_notion_blocks_append.blobfish_original = _bf_orig_notion_blocks_append
notion_blocks_append = _bf_friction_notion_blocks_append

def notion_block_get(db_path='state.db', **kwargs):
    '''Retrieve a block object using the ID specified (GET /v1/blocks/{block_id})'''
    _missing = [p for p in ['block_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'object': 'error', 'status': 400, 'code': 'validation_error', 'message': str(_r.get('error', ''))}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "notion_blocks" WHERE "id" = ?', [str(kwargs['block_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'block not found', 'status': 404}
            return {'object': 'error', 'status': 404, 'code': 'object_not_found', 'message': str(_r.get('error', ''))}
        _r = dict(_row)
        _r['object'] = 'block'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notion_block_get = notion_block_get
def _bf_friction_notion_block_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notion_block_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notion_block_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notion_block_get(*_bf_args, **_bf_kwargs)
_bf_friction_notion_block_get.blobfish_original = _bf_orig_notion_block_get
notion_block_get = _bf_friction_notion_block_get

def notion_block_delete(db_path='state.db', **kwargs):
    '''Set a block object to archived: true using the ID specified; the block is moved to trash (DELETE /v1/blocks/{block_id})'''
    _missing = [p for p in ['block_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'object': 'error', 'status': 400, 'code': 'validation_error', 'message': str(_r.get('error', ''))}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "notion_blocks" WHERE "id" = ?', [str(kwargs['block_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'block not found', 'status': 404}
            return {'object': 'error', 'status': 404, 'code': 'object_not_found', 'message': str(_r.get('error', ''))}
        cur.execute('DELETE FROM "notion_blocks" WHERE "id" = ?', [str(kwargs['block_id'])])
        conn.commit()
        _r = {'deleted': True, 'id': str(kwargs['block_id'])}
        return {'object': 'block', 'id': _r.get('id'), 'archived': True}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notion_block_delete = notion_block_delete
def _bf_friction_notion_block_delete(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notion_block_delete(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notion_block_delete|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notion_block_delete(*_bf_args, **_bf_kwargs)
_bf_friction_notion_block_delete.blobfish_original = _bf_orig_notion_block_delete
notion_block_delete = _bf_friction_notion_block_delete

def notion_comments_list(db_path='state.db', **kwargs):
    '''Retrieve a list of un-resolved comment objects from the specified page or block (GET /v1/comments)'''
    _missing = [p for p in ['block_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'object': 'error', 'status': 400, 'code': 'validation_error', 'message': str(_r.get('error', ''))}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('block_id') is not None:
            _where.append('"parent_id" = ?')
            _args.append(str(kwargs['block_id']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "notion_comments"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'object': 'list', 'results': _r['items'], 'next_cursor': None, 'has_more': False}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notion_comments_list = notion_comments_list
def _bf_friction_notion_comments_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notion_comments_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notion_comments_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notion_comments_list(*_bf_args, **_bf_kwargs)
_bf_friction_notion_comments_list.blobfish_original = _bf_orig_notion_comments_list
notion_comments_list = _bf_friction_notion_comments_list

def notion_comment_create(db_path='state.db', **kwargs):
    '''Create a comment in a page or existing discussion thread (POST /v1/comments)'''
    _missing = [p for p in ['rich_text'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'object': 'error', 'status': 400, 'code': 'validation_error', 'message': str(_r.get('error', ''))}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "notion_comments"').fetchone()[0] + 1
        _id = 'cmt-' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "notion_comments" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'cmt-' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('parent_id') is not None:
            _cols.append('parent_id')
            _v = kwargs['parent_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('discussion_id') is not None:
            _cols.append('discussion_id')
            _v = kwargs['discussion_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('rich_text') is not None:
            _cols.append('rich_text')
            _v = kwargs['rich_text']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'resolved' not in _cols:
            _cols.append('resolved')
            _vals.append(0)
        if 'created_by' not in _cols:
            _cols.append('created_by')
            _vals.append('9081a2b3-c4d5-4e67-8192-a3b4c5d6e508')
        if 'created_time' not in _cols:
            _cols.append('created_time')
            _vals.append('2026-08-10T09:00:00.000Z')
        cur.execute('INSERT INTO "notion_comments" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "notion_comments" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['object'] = 'comment'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notion_comment_create = notion_comment_create
def _bf_friction_notion_comment_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notion_comment_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notion_comment_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notion_comment_create(*_bf_args, **_bf_kwargs)
_bf_friction_notion_comment_create.blobfish_original = _bf_orig_notion_comment_create
notion_comment_create = _bf_friction_notion_comment_create

def notion_users_list(db_path='state.db', **kwargs):
    '''Return a paginated list of users for the workspace (GET /v1/users)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "notion_users"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'object': 'list', 'results': _r['items'], 'next_cursor': None, 'has_more': False}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notion_users_list = notion_users_list
def _bf_friction_notion_users_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notion_users_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notion_users_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notion_users_list(*_bf_args, **_bf_kwargs)
_bf_friction_notion_users_list.blobfish_original = _bf_orig_notion_users_list
notion_users_list = _bf_friction_notion_users_list

def notion_user_get(db_path='state.db', **kwargs):
    '''Retrieve a user object using the ID specified (GET /v1/users/{user_id})'''
    _missing = [p for p in ['user_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'object': 'error', 'status': 400, 'code': 'validation_error', 'message': str(_r.get('error', ''))}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "notion_users" WHERE "id" = ?', [str(kwargs['user_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'user not found', 'status': 404}
            return {'object': 'error', 'status': 404, 'code': 'object_not_found', 'message': str(_r.get('error', ''))}
        _r = dict(_row)
        _r['object'] = 'user'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notion_user_get = notion_user_get
def _bf_friction_notion_user_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notion_user_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notion_user_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notion_user_get(*_bf_args, **_bf_kwargs)
_bf_friction_notion_user_get.blobfish_original = _bf_orig_notion_user_get
notion_user_get = _bf_friction_notion_user_get

