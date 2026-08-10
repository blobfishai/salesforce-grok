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
