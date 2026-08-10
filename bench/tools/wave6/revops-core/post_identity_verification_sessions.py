def post_identity_verification_sessions(db_path='state.db', **kwargs):
    '''Create a VerificationSession (POST /v1/identity/verification_sessions)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _n = cur.execute('SELECT COALESCE(MAX(rowid), 0) + 100 FROM "identity_verification_sessions"').fetchone()[0] + 1
        _base = datetime.datetime(2026, 1, 5, 9, 0, 0)
        _ts = (_base + datetime.timedelta(minutes=_n)).strftime('%Y-%m-%dT%H:%M:%SZ')
        _cols = ['"id"']
        _vals = ['identity_verification_session_' + str(_n).zfill(14) + '']
        if kwargs.get('client_reference_id') is not None:
            _cols.append('"client_reference_id"')
            _vals.append(str(kwargs['client_reference_id']))
        if kwargs.get('metadata') is not None:
            _cols.append('"metadata"')
            _vals.append(json.dumps(kwargs['metadata']) if not isinstance(kwargs['metadata'], str) else kwargs['metadata'])
        if kwargs.get('options') is not None:
            _cols.append('"options"')
            _vals.append(json.dumps(kwargs['options']) if not isinstance(kwargs['options'], str) else kwargs['options'])
        if kwargs.get('provided_details') is not None:
            _cols.append('"provided_details"')
            _vals.append(json.dumps(kwargs['provided_details']) if not isinstance(kwargs['provided_details'], str) else kwargs['provided_details'])
        if kwargs.get('related_customer') is not None:
            _cols.append('"related_customer"')
            _vals.append(str(kwargs['related_customer']))
        if kwargs.get('related_customer_account') is not None:
            _cols.append('"related_customer_account"')
            _vals.append(str(kwargs['related_customer_account']))
        if kwargs.get('related_person') is not None:
            _cols.append('"related_person"')
            _vals.append(json.dumps(kwargs['related_person']) if not isinstance(kwargs['related_person'], str) else kwargs['related_person'])
        if kwargs.get('type') is not None:
            _cols.append('"type"')
            _vals.append(str(kwargs['type']))
        if kwargs.get('verification_flow') is not None:
            _cols.append('"verification_flow"')
            _vals.append(str(kwargs['verification_flow']))
        if '"status"' not in _cols:
            _cols.append('"status"')
            _vals.append('open')
        _sql = 'INSERT INTO "identity_verification_sessions" (' + ', '.join(_cols) + ') VALUES (' + ', '.join(['?'] * len(_vals)) + ')'
        try:
            cur.execute(_sql, _vals)
        except sqlite3.IntegrityError:
            conn.rollback()
            return {'error': 'conflict: duplicate key', 'status': 409}
        conn.commit()
        _row = cur.execute('SELECT * FROM "identity_verification_sessions" WHERE "id" = ?', [_vals[0]]).fetchone()
        _out = dict(_row)
        for _jc in ['metadata', 'related_person']:
            if isinstance(_out.get(_jc), str) and _out[_jc][:1] in ('[', '{'):
                try:
                    _out[_jc] = json.loads(_out[_jc])
                except Exception:
                    pass
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_identity_verification_sessions = post_identity_verification_sessions
def _bf_friction_post_identity_verification_sessions(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_identity_verification_sessions(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_identity_verification_sessions|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
            _bf_kinds = ["service_unavailable","rate_limited","stale_reference","permission_denied"]
            _bf_messages = {"service_unavailable":"The service is temporarily unavailable (upstream timeout while processing the request). Please retry.","rate_limited":"Rate limit exceeded for this operation. Wait a moment and retry.","stale_reference":"The referenced record could not be loaded — the reference may be stale or recently changed. Re-fetch the latest data and retry.","permission_denied":"Permission denied for this operation — your access grant is still propagating. Retry, or use an alternative workflow if one is available."}
            _bf_kind = _bf_kinds[int(_bf_digest[8:12], 16) % len(_bf_kinds)]
            return {"success": False, "error": _bf_kind, "message": _bf_messages[_bf_kind], "retryable": True}
    return _bf_orig_post_identity_verification_sessions(*_bf_args, **_bf_kwargs)
_bf_friction_post_identity_verification_sessions.blobfish_original = _bf_orig_post_identity_verification_sessions
post_identity_verification_sessions = _bf_friction_post_identity_verification_sessions
