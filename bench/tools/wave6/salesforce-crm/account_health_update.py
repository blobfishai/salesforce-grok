def account_health_update(db_path='state.db', **kwargs):
    '''Re-score an account's health after a save play or usage change (PATCH /analytics/v1/accounts/health/{id}).'''
    _missing = [p for p in ['health_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "account_health" WHERE "id" = ?', [str(kwargs['health_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'account_health not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _sets, _args = [], []
        if kwargs.get('score') is not None:
            _sets.append('"score" = ?')
            _v = kwargs['score']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('band') is not None:
            _sets.append('"band" = ?')
            _v = kwargs['band']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('primary_risk') is not None:
            _sets.append('"primary_risk" = ?')
            _v = kwargs['primary_risk']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "account_health" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['health_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "account_health" WHERE "id" = ?', [str(kwargs['health_id'])]).fetchone()
        _r = dict(_row)
        _r['attributes'] = {'type': 'account_health', 'url': '/services/data/v62.0/sobjects/account_health/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_account_health_update = account_health_update
def _bf_friction_account_health_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_account_health_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "account_health_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_account_health_update(*_bf_args, **_bf_kwargs)
_bf_friction_account_health_update.blobfish_original = _bf_orig_account_health_update
account_health_update = _bf_friction_account_health_update
