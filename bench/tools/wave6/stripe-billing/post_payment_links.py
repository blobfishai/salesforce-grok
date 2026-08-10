def post_payment_links(db_path='state.db', **kwargs):
    import sqlite3, datetime, hashlib, json
    price = kwargs.get('price')
    if not price:
        return {"error": {"type": "invalid_request_error", "param": "line_items[0][price]", "message": "Missing required param: line_items[0][price]."}}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    prow = cur.execute("SELECT * FROM prices WHERE id = ?", (price,)).fetchone()
    if prow is None:
        conn.close()
        return {"error": {"type": "invalid_request_error", "code": "resource_missing", "message": "No such price: '%s'" % price}}
    quantity = kwargs.get('quantity')
    quantity = int(quantity) if quantity is not None else 1
    if quantity < 1:
        conn.close()
        return {"error": {"type": "invalid_request_error", "param": "line_items[0][quantity]", "message": "quantity must be a positive integer."}}
    allow_promotion_codes = 1 if kwargs.get('allow_promotion_codes') else 0
    n = cur.execute("SELECT COUNT(*) FROM payment_links").fetchone()[0]
    digest = hashlib.sha1(("%s|%s|%s" % (price, quantity, n)).encode()).hexdigest()[:14]
    link_id = "plink_" + digest
    url = "https://buy.stripe.com/test_" + digest
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    metadata = kwargs.get('metadata')
    metadata_json = json.dumps(metadata) if isinstance(metadata, dict) else metadata
    cur.execute(
        "INSERT INTO payment_links (id, object, active, url, price, quantity, currency, allow_promotion_codes, metadata, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (link_id, "payment_link", 1, url, price, quantity, prow["currency"], allow_promotion_codes, metadata_json, now),
    )
    conn.commit()
    created = cur.execute("SELECT * FROM payment_links WHERE id = ?", (link_id,)).fetchone()
    conn.close()
    return dict(created)

_env_orig_post_payment_links = post_payment_links
def _env_post_payment_links(db_path='state.db', **kwargs):
    _r = _env_orig_post_payment_links(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'object': 'list', 'url': '/v1/payment_links', 'has_more': False, 'data': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'type': 'invalid_request_error', 'code': 'resource_missing', 'message': str(_r.get('error', ''))}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    return _r
post_payment_links = _env_post_payment_links

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_payment_links = post_payment_links
def _bf_friction_post_payment_links(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_payment_links(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_payment_links|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_payment_links(*_bf_args, **_bf_kwargs)
_bf_friction_post_payment_links.blobfish_original = _bf_orig_post_payment_links
post_payment_links = _bf_friction_post_payment_links
