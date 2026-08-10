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
