def get_invoices(db_path='state.db', **kwargs):
    '''List all invoices (GET /v1/invoices)'''
    if kwargs.get('collection_method') is not None and kwargs.get('collection_method') not in ['charge_automatically', 'send_invoice']:
        return {'error': 'invalid value for collection_method: %r. Accepted: %s' % (kwargs.get('collection_method'), ', '.join(['charge_automatically', 'send_invoice'])), 'status': 422, 'parameter': 'collection_method', 'accepted': ['charge_automatically', 'send_invoice']}
    if kwargs.get('status') is not None and kwargs.get('status') not in ['draft', 'open', 'paid', 'uncollectible', 'void']:
        return {'error': 'invalid value for status: %r. Accepted: %s' % (kwargs.get('status'), ', '.join(['draft', 'open', 'paid', 'uncollectible', 'void'])), 'status': 422, 'parameter': 'status', 'accepted': ['draft', 'open', 'paid', 'uncollectible', 'void']}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('collection_method') is not None:
            _where.append('"collection_method" = ?')
            _args.append(str(kwargs['collection_method']))
        if kwargs.get('created') is not None:
            _where.append('"created" = ?')
            _args.append(str(kwargs['created']))
        if kwargs.get('customer') is not None:
            _where.append('"customer" = ?')
            _args.append(str(kwargs['customer']))
        if kwargs.get('customer_account') is not None:
            _where.append('"customer_account" = ?')
            _args.append(str(kwargs['customer_account']))
        if kwargs.get('status') is not None:
            _where.append('"status" = ?')
            _args.append(str(kwargs['status']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "invoices"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        return {'items': _rows, 'count': len(_rows)}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_invoices = get_invoices
def _bf_friction_get_invoices(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_invoices(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_invoices|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_invoices(*_bf_args, **_bf_kwargs)
_bf_friction_get_invoices.blobfish_original = _bf_orig_get_invoices
get_invoices = _bf_friction_get_invoices
