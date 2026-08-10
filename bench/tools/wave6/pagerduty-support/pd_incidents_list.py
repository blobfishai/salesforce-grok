def pd_incidents_list(db_path='state.db', **kwargs):
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    where = []
    args = []
    status = kwargs.get('status')
    if status:
        if status not in ('triggered', 'acknowledged', 'resolved'):
            conn.close()
            return {'error': {'status': 400, 'message': "Invalid status '%s'. Must be one of: triggered, acknowledged, resolved." % status}}
        where.append('status = ?')
        args.append(status)
    service_id = kwargs.get('service_id')
    if service_id:
        where.append('service_id = ?')
        args.append(service_id)
    urgency = kwargs.get('urgency')
    if urgency:
        if urgency not in ('high', 'low'):
            conn.close()
            return {'error': {'status': 400, 'message': "Invalid urgency '%s'. Must be one of: high, low." % urgency}}
        where.append('urgency = ?')
        args.append(urgency)
    since = kwargs.get('since')
    if since:
        where.append('created_at >= ?')
        args.append(since)
    until = kwargs.get('until')
    if until:
        where.append('created_at <= ?')
        args.append(until)
    try:
        limit = int(kwargs.get('limit') or 30)
    except (TypeError, ValueError):
        limit = 30
    sql = 'SELECT * FROM pd_incidents'
    if where:
        sql += ' WHERE ' + ' AND '.join(where)
    sql += ' ORDER BY created_at DESC LIMIT ?'
    args.append(limit)
    rows = [dict(r) for r in conn.execute(sql, args).fetchall()]
    conn.close()
    return {'incidents': rows, 'total': len(rows)}

_env_orig_pd_incidents_list = pd_incidents_list
def _env_pd_incidents_list(db_path='state.db', **kwargs):
    _r = _env_orig_pd_incidents_list(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'incidents': _r['items'], 'limit': _r['count'], 'offset': 0, 'more': False, 'total': _r['count']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'message': str(_r.get('error', '')), 'code': 2100}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'message': str(_r.get('error', '')), 'code': 2001, 'errors': [str(_r.get('error', ''))]}}
    return _r
pd_incidents_list = _env_pd_incidents_list

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_incidents_list = pd_incidents_list
def _bf_friction_pd_incidents_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_incidents_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_incidents_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_incidents_list(*_bf_args, **_bf_kwargs)
_bf_friction_pd_incidents_list.blobfish_original = _bf_orig_pd_incidents_list
pd_incidents_list = _bf_friction_pd_incidents_list
