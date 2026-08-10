def patch_marketing_singlesends_id(db_path='state.db', **kwargs):
    '''Update Single Send (PATCH /marketing/singlesends/{id})'''
    _missing = [p for p in ['id', 'name'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _sets, _args = [], []
        if kwargs.get('categories') is not None:
            _sets.append('"categories" = ?')
            _args.append(json.dumps(kwargs['categories']) if not isinstance(kwargs['categories'], str) else kwargs['categories'])
        if kwargs.get('email_config') is not None:
            _sets.append('"email_config" = ?')
            _args.append(json.dumps(kwargs['email_config']) if not isinstance(kwargs['email_config'], str) else kwargs['email_config'])
        if kwargs.get('name') is not None:
            _sets.append('"name" = ?')
            _args.append(str(kwargs['name']))
        if kwargs.get('send_at') is not None:
            _sets.append('"send_at" = ?')
            _args.append(str(kwargs['send_at']))
        if kwargs.get('send_to') is not None:
            _sets.append('"send_to" = ?')
            _args.append(json.dumps(kwargs['send_to']) if not isinstance(kwargs['send_to'], str) else kwargs['send_to'])
        if not _sets:
            return {'error': 'no updatable fields provided', 'status': 400}
        _n = cur.execute('SELECT COALESCE(MAX(rowid), 0) + 100 FROM "singlesends"').fetchone()[0] + 1
        _base = datetime.datetime(2026, 1, 5, 9, 0, 0)
        _ts = (_base + datetime.timedelta(minutes=_n)).strftime('%Y-%m-%dT%H:%M:%SZ')
        _sets.append('"updated_at" = ?')
        _args.append(_ts)
        _args.append(str(kwargs.get('id')))
        cur.execute('UPDATE "singlesends" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args)
        if cur.rowcount == 0:
            conn.rollback()
            return {'error': 'singlesend not found', 'status': 404}
        conn.commit()
        _row = cur.execute('SELECT * FROM "singlesends" WHERE "id" = ?', [str(kwargs.get('id'))]).fetchone()
        _out = dict(_row)
        for _jc in ['categories', 'email_config', 'send_to', 'warnings']:
            if isinstance(_out.get(_jc), str) and _out[_jc][:1] in ('[', '{'):
                try:
                    _out[_jc] = json.loads(_out[_jc])
                except Exception:
                    pass
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_patch_marketing_singlesends_id = patch_marketing_singlesends_id
def _bf_friction_patch_marketing_singlesends_id(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_patch_marketing_singlesends_id(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "patch_marketing_singlesends_id|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_patch_marketing_singlesends_id(*_bf_args, **_bf_kwargs)
_bf_friction_patch_marketing_singlesends_id.blobfish_original = _bf_orig_patch_marketing_singlesends_id
patch_marketing_singlesends_id = _bf_friction_patch_marketing_singlesends_id
