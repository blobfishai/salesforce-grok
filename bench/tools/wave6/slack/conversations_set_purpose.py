def conversations_set_purpose(db_path='state.db', **kwargs):
    '''Sets the purpose for a conversation (POST /conversations.setPurpose)'''
    _missing = [p for p in ['channel', 'purpose'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "channels" WHERE "id" = ?', [str(kwargs['channel'])]).fetchone()
        if _row is None:
            _r = {'error': 'channel not found', 'status': 404}
            return {'ok': False, 'error': str(_r.get('error') or 'channel not found').replace(' not found', '_not_found').replace(' ', '_')}
        _sets, _args = [], []
        if kwargs.get('purpose') is not None:
            _sets.append('"purpose" = ?')
            _v = kwargs['purpose']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "channels" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['channel'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "channels" WHERE "id" = ?', [str(kwargs['channel'])]).fetchone()
        _r = dict(_row)
        _r = {'ok': True, 'channel': _r}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_conversations_set_purpose = conversations_set_purpose
def _bf_friction_conversations_set_purpose(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_conversations_set_purpose(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "conversations_set_purpose|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_conversations_set_purpose(*_bf_args, **_bf_kwargs)
_bf_friction_conversations_set_purpose.blobfish_original = _bf_orig_conversations_set_purpose
conversations_set_purpose = _bf_friction_conversations_set_purpose
