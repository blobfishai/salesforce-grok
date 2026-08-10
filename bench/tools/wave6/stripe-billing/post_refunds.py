def post_refunds(db_path='state.db', **kwargs):
    import sqlite3, datetime, hashlib, json
    charge_id = kwargs.get('charge')
    payment_intent = kwargs.get('payment_intent')
    if not charge_id and not payment_intent:
        return {"error": {"type": "invalid_request_error", "message": "One of the following params must be provided: charge, payment_intent."}}
    reason = kwargs.get('reason')
    if reason is not None and reason not in ("duplicate", "fraudulent", "requested_by_customer"):
        return {"error": {"type": "invalid_request_error", "param": "reason", "message": "Invalid reason: must be one of duplicate, fraudulent, or requested_by_customer."}}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if charge_id:
        row = cur.execute("SELECT * FROM charges WHERE id = ?", (charge_id,)).fetchone()
        if row is None:
            conn.close()
            return {"error": {"type": "invalid_request_error", "code": "resource_missing", "message": "No such charge: '%s'" % charge_id}}
    else:
        row = cur.execute("SELECT * FROM charges WHERE payment_intent = ? ORDER BY created DESC, id DESC LIMIT 1", (payment_intent,)).fetchone()
        if row is None:
            conn.close()
            return {"error": {"type": "invalid_request_error", "code": "resource_missing", "message": "No such payment_intent, or no charge found for PaymentIntent: '%s'" % payment_intent}}
    charge_id = row["id"]
    payment_intent = row["payment_intent"]
    already = row["amount_refunded"] or 0
    total = row["amount"] or 0
    remaining = total - already
    if remaining <= 0:
        conn.close()
        return {"error": {"type": "invalid_request_error", "code": "charge_already_refunded", "message": "Charge %s has already been refunded." % charge_id}}
    amount = kwargs.get('amount')
    if amount is None:
        amount = remaining
    amount = int(amount)
    if amount < 1 or amount > remaining:
        conn.close()
        return {"error": {"type": "invalid_request_error", "param": "amount", "message": "Refund amount (%s) is greater than unrefunded amount on charge (%s)." % (amount, remaining)}}
    n = cur.execute("SELECT COUNT(*) FROM refunds").fetchone()[0]
    refund_id = "re_" + hashlib.sha1(("%s|%s|%s" % (charge_id, amount, n)).encode()).hexdigest()[:14]
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    metadata = kwargs.get('metadata')
    metadata_json = json.dumps(metadata) if isinstance(metadata, dict) else metadata
    cur.execute(
        "INSERT INTO refunds (id, object, amount, charge, payment_intent, currency, reason, status, balance_transaction, receipt_number, metadata, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (refund_id, "refund", amount, charge_id, payment_intent, row["currency"], reason, "succeeded", None, None, metadata_json, now),
    )
    new_refunded = already + amount
    fully = 1 if new_refunded >= total else (row["refunded"] or 0)
    cur.execute("UPDATE charges SET amount_refunded = ?, refunded = ? WHERE id = ?", (new_refunded, fully, charge_id))
    conn.commit()
    created = cur.execute("SELECT * FROM refunds WHERE id = ?", (refund_id,)).fetchone()
    conn.close()
    return dict(created)

_env_orig_post_refunds = post_refunds
def _env_post_refunds(db_path='state.db', **kwargs):
    _r = _env_orig_post_refunds(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'object': 'list', 'url': '/v1/refunds', 'has_more': False, 'data': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'type': 'invalid_request_error', 'code': 'resource_missing', 'message': str(_r.get('error', ''))}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    return _r
post_refunds = _env_post_refunds

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_refunds = post_refunds
def _bf_friction_post_refunds(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_refunds(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_refunds|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_refunds(*_bf_args, **_bf_kwargs)
_bf_friction_post_refunds.blobfish_original = _bf_orig_post_refunds
post_refunds = _bf_friction_post_refunds
