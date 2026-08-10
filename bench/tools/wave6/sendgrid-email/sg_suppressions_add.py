def sg_suppressions_add(db_path='state.db', **kwargs):
    import sqlite3, hashlib, datetime
    group_id = kwargs.get('group_id')
    email = kwargs.get('email')
    if group_id is None:
        return {"errors": [{"field": "group_id", "message": "The id of the unsubscribe group is required."}]}
    if not email:
        return {"errors": [{"field": "email", "message": "The email address to add to the unsubscribe group is required."}]}
    try:
        gid = float(group_id)
    except (TypeError, ValueError):
        gid = group_id
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    group = cur.execute("SELECT * FROM suppression_groups WHERE id = ?", (gid,)).fetchone()
    if group is None:
        conn.close()
        return {"errors": [{"field": "group_id", "message": "Unsubscribe group with id '%s' not found." % group_id}]}
    existing = cur.execute("SELECT * FROM sg_suppressions WHERE group_id = ? AND email = ?", (gid, email)).fetchone()
    if existing is not None:
        conn.close()
        result = dict(existing)
        result["already_suppressed"] = True
        return result
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    sup_id = 'sup_' + hashlib.sha256((str(gid) + '|' + email).encode('utf-8')).hexdigest()[:12]
    cur.execute("INSERT INTO sg_suppressions (id, group_id, email, created_at) VALUES (?, ?, ?, ?)", (sup_id, gid, email, now))
    cur.execute("UPDATE suppression_groups SET unsubscribes = COALESCE(unsubscribes, 0) + 1 WHERE id = ?", (gid,))
    conn.commit()
    row = cur.execute("SELECT * FROM sg_suppressions WHERE id = ?", (sup_id,)).fetchone()
    conn.close()
    result = dict(row)
    result["already_suppressed"] = False
    return result

_env_orig_sg_suppressions_add = sg_suppressions_add
def _env_sg_suppressions_add(db_path='state.db', **kwargs):
    _r = _env_orig_sg_suppressions_add(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'result': _r['items'], '_metadata': {'count': _r['count']}}
    if 'error' in _r and _r.get('status') == 404:
        return {'errors': [{'message': str(_r.get('error', '')), 'field': None, 'help': None}]}
    if 'error' in _r and _r.get('status') == 400:
        return {'errors': [{'message': str(_r.get('error', '')), 'field': None, 'help': None}]}
    return _r
sg_suppressions_add = _env_sg_suppressions_add

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_sg_suppressions_add = sg_suppressions_add
def _bf_friction_sg_suppressions_add(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_sg_suppressions_add(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "sg_suppressions_add|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_sg_suppressions_add(*_bf_args, **_bf_kwargs)
_bf_friction_sg_suppressions_add.blobfish_original = _bf_orig_sg_suppressions_add
sg_suppressions_add = _bf_friction_sg_suppressions_add
