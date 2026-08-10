def post_test_helpers_issuing_authorizations(db_path='state.db', **kwargs):
    '''Create a test-mode authorization (POST /v1/test_helpers/issuing/authorizations)'''
    _missing = [p for p in ['card'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _n = cur.execute('SELECT COALESCE(MAX(rowid), 0) + 100 FROM "issuing_authorizations"').fetchone()[0] + 1
        _base = datetime.datetime(2026, 1, 5, 9, 0, 0)
        _ts = (_base + datetime.timedelta(minutes=_n)).strftime('%Y-%m-%dT%H:%M:%SZ')
        _cols = ['"id"']
        _vals = ['issuing_authorization_' + str(_n).zfill(14) + '']
        if kwargs.get('amount') is not None:
            _cols.append('"amount"')
            _vals.append(int(kwargs['amount']))
        if kwargs.get('amount_details') is not None:
            _cols.append('"amount_details"')
            _vals.append(json.dumps(kwargs['amount_details']) if not isinstance(kwargs['amount_details'], str) else kwargs['amount_details'])
        if kwargs.get('authorization_method') is not None:
            _cols.append('"authorization_method"')
            _vals.append(str(kwargs['authorization_method']))
        if kwargs.get('card') is not None:
            _cols.append('"card"')
            _vals.append(str(kwargs['card']))
        if kwargs.get('currency') is not None:
            _cols.append('"currency"')
            _vals.append(str(kwargs['currency']))
        if kwargs.get('fleet') is not None:
            _cols.append('"fleet"')
            _vals.append(json.dumps(kwargs['fleet']) if not isinstance(kwargs['fleet'], str) else kwargs['fleet'])
        if kwargs.get('fuel') is not None:
            _cols.append('"fuel"')
            _vals.append(json.dumps(kwargs['fuel']) if not isinstance(kwargs['fuel'], str) else kwargs['fuel'])
        if kwargs.get('merchant_amount') is not None:
            _cols.append('"merchant_amount"')
            _vals.append(int(kwargs['merchant_amount']))
        if kwargs.get('merchant_currency') is not None:
            _cols.append('"merchant_currency"')
            _vals.append(str(kwargs['merchant_currency']))
        if kwargs.get('merchant_data') is not None:
            _cols.append('"merchant_data"')
            _vals.append(json.dumps(kwargs['merchant_data']) if not isinstance(kwargs['merchant_data'], str) else kwargs['merchant_data'])
        if kwargs.get('network_data') is not None:
            _cols.append('"network_data"')
            _vals.append(json.dumps(kwargs['network_data']) if not isinstance(kwargs['network_data'], str) else kwargs['network_data'])
        if kwargs.get('verification_data') is not None:
            _cols.append('"verification_data"')
            _vals.append(json.dumps(kwargs['verification_data']) if not isinstance(kwargs['verification_data'], str) else kwargs['verification_data'])
        if kwargs.get('wallet') is not None:
            _cols.append('"wallet"')
            _vals.append(str(kwargs['wallet']))
        if '"status"' not in _cols:
            _cols.append('"status"')
            _vals.append('open')
        _sql = 'INSERT INTO "issuing_authorizations" (' + ', '.join(_cols) + ') VALUES (' + ', '.join(['?'] * len(_vals)) + ')'
        try:
            cur.execute(_sql, _vals)
        except sqlite3.IntegrityError:
            conn.rollback()
            return {'error': 'conflict: duplicate key', 'status': 409}
        conn.commit()
        _row = cur.execute('SELECT * FROM "issuing_authorizations" WHERE "id" = ?', [_vals[0]]).fetchone()
        _out = dict(_row)
        for _jc in ['balance_transactions', 'card', 'merchant_data', 'metadata', 'request_history', 'transactions', 'verification_data', 'fraud_challenges']:
            if isinstance(_out.get(_jc), str) and _out[_jc][:1] in ('[', '{'):
                try:
                    _out[_jc] = json.loads(_out[_jc])
                except Exception:
                    pass
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_test_helpers_issuing_authorizations = post_test_helpers_issuing_authorizations
def _bf_friction_post_test_helpers_issuing_authorizations(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_test_helpers_issuing_authorizations(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_test_helpers_issuing_authorizations|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_test_helpers_issuing_authorizations(*_bf_args, **_bf_kwargs)
_bf_friction_post_test_helpers_issuing_authorizations.blobfish_original = _bf_orig_post_test_helpers_issuing_authorizations
post_test_helpers_issuing_authorizations = _bf_friction_post_test_helpers_issuing_authorizations
