def post_payment_intents_intent_capture(db_path='state.db', **kwargs):
    import sqlite3
    intent = kwargs.get('intent')
    if not intent:
        return {"error": {"type": "invalid_request_error", "message": "Missing required param: intent."}}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM payment_intents WHERE id = ?", (intent,)).fetchone()
    if row is None:
        conn.close()
        return {"error": {"type": "invalid_request_error", "code": "resource_missing", "message": "No such payment_intent: '%s'" % intent}}
    if row["status"] != "requires_capture":
        conn.close()
        return {"error": {"type": "invalid_request_error", "message": "PaymentIntent %s could not be captured because it has a status of %s; only a PaymentIntent with status requires_capture may be captured." % (intent, row["status"])}}
    capturable = row["amount_capturable"] if row["amount_capturable"] else (row["amount"] or 0)
    amount_to_capture = kwargs.get('amount_to_capture')
    if amount_to_capture is None:
        amount_to_capture = capturable
    amount_to_capture = int(amount_to_capture)
    if amount_to_capture < 1 or amount_to_capture > capturable:
        conn.close()
        return {"error": {"type": "invalid_request_error", "message": "amount_to_capture must be a positive integer less than or equal to amount_capturable (%s)." % capturable}}
    cur.execute("UPDATE payment_intents SET status = 'succeeded', amount_received = ?, amount_capturable = 0 WHERE id = ?", (amount_to_capture, intent))
    conn.commit()
    updated = cur.execute("SELECT * FROM payment_intents WHERE id = ?", (intent,)).fetchone()
    conn.close()
    return dict(updated)

_env_orig_post_payment_intents_intent_capture = post_payment_intents_intent_capture
def _env_post_payment_intents_intent_capture(db_path='state.db', **kwargs):
    _r = _env_orig_post_payment_intents_intent_capture(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'object': 'list', 'url': '/v1/payment_intents', 'has_more': False, 'data': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'type': 'invalid_request_error', 'code': 'resource_missing', 'message': str(_r.get('error', ''))}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    return _r
post_payment_intents_intent_capture = _env_post_payment_intents_intent_capture

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_payment_intents_intent_capture = post_payment_intents_intent_capture
def _bf_friction_post_payment_intents_intent_capture(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_payment_intents_intent_capture(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_payment_intents_intent_capture|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_payment_intents_intent_capture(*_bf_args, **_bf_kwargs)
_bf_friction_post_payment_intents_intent_capture.blobfish_original = _bf_orig_post_payment_intents_intent_capture
post_payment_intents_intent_capture = _bf_friction_post_payment_intents_intent_capture
