def conversations_list(db_path='state.db', **kwargs):
    import sqlite3
    try:
        limit = int(kwargs.get('limit', 100))
    except (TypeError, ValueError):
        limit = 100
    types = str(kwargs.get('types') or 'public_channel')
    type_conds = []
    for t in [part.strip() for part in types.split(',') if part.strip()]:
        if t == 'public_channel':
            type_conds.append('(is_private = 0 AND is_mpim = 0)')
        elif t == 'private_channel':
            type_conds.append('(is_private = 1 AND is_mpim = 0)')
        elif t == 'mpim':
            type_conds.append('(is_mpim = 1)')
        else:
            return {'ok': False, 'error': 'invalid_types', 'status': 400, 'detail': 'types must be a comma-separated mix of public_channel, private_channel, mpim'}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    sql = 'SELECT id, name, is_channel, is_private, is_archived, is_general, is_mpim, is_shared, is_org_shared, num_members, topic, purpose, created FROM channels WHERE (' + ' OR '.join(type_conds) + ')'
    if kwargs.get('exclude_archived') in (True, 1, '1', 'true', 'True'):
        sql += ' AND is_archived = 0'
    sql += ' ORDER BY id LIMIT ?'
    rows = [dict(r) for r in conn.execute(sql, (limit,)).fetchall()]
    conn.close()
    return {'ok': True, 'channels': rows, 'response_metadata': {'next_cursor': ''}}

_env_orig_conversations_list = conversations_list
def _env_conversations_list(db_path='state.db', **kwargs):
    _r = _env_orig_conversations_list(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'ok': True, 'channels': _r['items'], 'response_metadata': {'next_cursor': ''}}
    if 'error' in _r and _r.get('status') == 404:
        return {'ok': False, 'error': str(_r.get('error') or 'channel not found').replace(' not found', '_not_found').replace(' ', '_')}
    if 'error' in _r and _r.get('status') == 400:
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    return _r
conversations_list = _env_conversations_list

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_conversations_list = conversations_list
def _bf_friction_conversations_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_conversations_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "conversations_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_conversations_list(*_bf_args, **_bf_kwargs)
_bf_friction_conversations_list.blobfish_original = _bf_orig_conversations_list
conversations_list = _bf_friction_conversations_list
