def erp_customer_payment_create(db_path='state.db', **kwargs):
    import sqlite3, datetime
    inv_id = kwargs.get('applied_to')
    payment = kwargs.get('payment')
    if not inv_id or payment is None:
        return {'error': {'status': 400, 'name': 'USER_ERROR', 'message': "Params 'applied_to' (invoice id) and 'payment' (amount) are required."}}
    try:
        payment = round(float(payment), 2)
    except (TypeError, ValueError):
        return {'error': {'status': 400, 'name': 'USER_ERROR', 'message': "'payment' must be a number."}}
    if payment <= 0:
        return {'error': {'status': 400, 'name': 'USER_ERROR', 'message': "'payment' must be greater than zero."}}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    inv = conn.execute('SELECT * FROM erp_invoices WHERE id = ?', (inv_id,)).fetchone()
    if inv is None:
        conn.close()
        return {'error': {'status': 404, 'name': 'RCRD_DSNT_EXIST', 'message': "Invoice '%s' does not exist." % inv_id}}
    if inv['status'] == 'voided':
        conn.close()
        return {'error': {'status': 400, 'name': 'TRANS_VOIDED', 'message': 'Invoice %s is voided and cannot accept payments.' % inv_id}}
    currency = kwargs.get('currency') or inv['currency']
    if currency != inv['currency']:
        conn.close()
        return {'error': {'status': 400, 'name': 'CURRENCY_MISMATCH', 'message': "Payment currency '%s' does not match invoice currency '%s'." % (currency, inv['currency'])}}
    remaining = inv['amount_remaining'] if inv['amount_remaining'] is not None else inv['total']
    if payment > remaining + 1e-09:
        conn.close()
        return {'error': {'status': 400, 'name': 'PAYMENT_EXCEEDS_REMAINING', 'message': 'Payment %.2f exceeds amount remaining %.2f on invoice %s.' % (payment, remaining, inv_id)}}
    n = conn.execute('SELECT COUNT(*) FROM erp_customer_payments').fetchone()[0]
    pid = 'PMT-%04d' % (5001 + n)
    while conn.execute('SELECT 1 FROM erp_customer_payments WHERE id = ?', (pid,)).fetchone() is not None:
        n += 1
        pid = 'PMT-%04d' % (5001 + n)
    now = datetime.datetime.utcnow().replace(microsecond=0)
    trandate = kwargs.get('trandate') or now.strftime('%Y-%m-%d')
    entity = kwargs.get('entity') or inv['entity']
    conn.execute(
        'INSERT INTO erp_customer_payments (id, entity, applied_to, trandate, payment_method, memo, currency, payment_amount, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (pid, entity, inv_id, trandate, kwargs.get('payment_method') or 'wire', kwargs.get('memo') or '', currency, payment, 'undeposited', now.isoformat() + 'Z'))
    new_remaining = round(remaining - payment, 2)
    new_status = 'paid' if new_remaining <= 0 else inv['status']
    conn.execute('UPDATE erp_invoices SET amount_remaining = ?, status = ? WHERE id = ?', (new_remaining, new_status, inv_id))
    conn.commit()
    pay_row = dict(conn.execute('SELECT * FROM erp_customer_payments WHERE id = ?', (pid,)).fetchone())
    inv_row = dict(conn.execute('SELECT * FROM erp_invoices WHERE id = ?', (inv_id,)).fetchone())
    conn.close()
    return {'customer_payment': pay_row, 'applied_to_invoice': inv_row}

_env_orig_erp_customer_payment_create = erp_customer_payment_create
def _env_erp_customer_payment_create(db_path='state.db', **kwargs):
    _r = _env_orig_erp_customer_payment_create(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'items': _r['items'], 'count': _r['count'], 'hasMore': False, 'totalResults': _r['count'], 'offset': 0}
    if 'error' in _r and _r.get('status') == 404:
        return {'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.4', 'title': 'Not Found', 'status': 404, 'o:errorDetails': [{'detail': str(_r.get('error', '')), 'o:errorCode': 'RCRD_DSNT_EXIST'}]}
    if 'error' in _r and _r.get('status') == 400:
        return {'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.1', 'title': 'Bad Request', 'status': 400, 'o:errorDetails': [{'detail': str(_r.get('error', '')), 'o:errorCode': 'USER_ERROR'}]}
    return _r
erp_customer_payment_create = _env_erp_customer_payment_create

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_customer_payment_create = erp_customer_payment_create
def _bf_friction_erp_customer_payment_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_customer_payment_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_customer_payment_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_customer_payment_create(*_bf_args, **_bf_kwargs)
_bf_friction_erp_customer_payment_create.blobfish_original = _bf_orig_erp_customer_payment_create
erp_customer_payment_create = _bf_friction_erp_customer_payment_create
