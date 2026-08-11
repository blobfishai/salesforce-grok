def signature_envelope_update(db_path='state.db', **kwargs):
    '''Advance an envelope's signature state (PUT /restapi/v2.1/accounts/{accountId}/envelopes/{envelopeId}).'''
    _missing = [p for p in ['envelope_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "signature_envelopes" WHERE "id" = ?', [str(kwargs['envelope_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'signature_envelope not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _sets, _args = [], []
        if kwargs.get('status') is not None:
            _sets.append('"status" = ?')
            _v = kwargs['status']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('customer_signed_at') is not None:
            _sets.append('"customer_signed_at" = ?')
            _v = kwargs['customer_signed_at']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('countersigned_at') is not None:
            _sets.append('"countersigned_at" = ?')
            _v = kwargs['countersigned_at']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "signature_envelopes" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['envelope_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "signature_envelopes" WHERE "id" = ?', [str(kwargs['envelope_id'])]).fetchone()
        _r = dict(_row)
        _r['attributes'] = {'type': 'signature_envelope', 'url': '/services/data/v62.0/sobjects/signature_envelope/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_signature_envelope_update = signature_envelope_update
def _bf_friction_signature_envelope_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_signature_envelope_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "signature_envelope_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_signature_envelope_update(*_bf_args, **_bf_kwargs)
_bf_friction_signature_envelope_update.blobfish_original = _bf_orig_signature_envelope_update
signature_envelope_update = _bf_friction_signature_envelope_update
