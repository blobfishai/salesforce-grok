def post_invoices_invoice_pay(db_path='state.db', **kwargs):
    import sqlite3
    invoice = kwargs.get('invoice')
    if not invoice:
        return {"error": {"type": "invalid_request_error", "message": "Missing required param: invoice."}}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM invoices WHERE id = ?", (invoice,)).fetchone()
    if row is None:
        conn.close()
        return {"error": {"type": "invalid_request_error", "code": "resource_missing", "message": "No such invoice: '%s'" % invoice}}
    if row["status"] == "paid":
        conn.close()
        return {"error": {"type": "invalid_request_error", "code": "invoice_already_paid", "message": "Invoice %s is already paid." % invoice}}
    if row["status"] != "open":
        conn.close()
        return {"error": {"type": "invalid_request_error", "message": "This invoice can't be paid because it has a status of %s; only open invoices can be paid." % row["status"]}}
    amount_due = row["amount_due"] or 0
    attempt_count = (row["attempt_count"] or 0) + 1
    if kwargs.get('paid_out_of_band'):
        cur.execute("UPDATE invoices SET status = 'paid', amount_paid = ?, amount_paid_off_stripe = ?, amount_remaining = 0, attempted = 1, attempt_count = ? WHERE id = ?", (amount_due, amount_due, attempt_count, invoice))
    else:
        cur.execute("UPDATE invoices SET status = 'paid', amount_paid = ?, amount_remaining = 0, attempted = 1, attempt_count = ? WHERE id = ?", (amount_due, attempt_count, invoice))
    conn.commit()
    updated = cur.execute("SELECT * FROM invoices WHERE id = ?", (invoice,)).fetchone()
    conn.close()
    return dict(updated)

_env_orig_post_invoices_invoice_pay = post_invoices_invoice_pay
def _env_post_invoices_invoice_pay(db_path='state.db', **kwargs):
    _r = _env_orig_post_invoices_invoice_pay(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'object': 'list', 'url': '/v1/invoices', 'has_more': False, 'data': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'type': 'invalid_request_error', 'code': 'resource_missing', 'message': str(_r.get('error', ''))}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    return _r
post_invoices_invoice_pay = _env_post_invoices_invoice_pay

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_invoices_invoice_pay = post_invoices_invoice_pay
def _bf_friction_post_invoices_invoice_pay(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_invoices_invoice_pay(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_invoices_invoice_pay|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_invoices_invoice_pay(*_bf_args, **_bf_kwargs)
_bf_friction_post_invoices_invoice_pay.blobfish_original = _bf_orig_post_invoices_invoice_pay
post_invoices_invoice_pay = _bf_friction_post_invoices_invoice_pay
