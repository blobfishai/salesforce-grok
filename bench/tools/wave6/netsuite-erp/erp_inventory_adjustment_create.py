def erp_inventory_adjustment_create(db_path='state.db', **kwargs):
    import sqlite3, datetime
    item = kwargs.get('item')
    location = kwargs.get('location')
    qty = kwargs.get('adjust_qty_by')
    if not item or not location or qty is None:
        return {'error': {'status': 400, 'name': 'USER_ERROR', 'message': "Params 'item', 'location' and 'adjust_qty_by' are required."}}
    try:
        qty = int(qty)
    except (TypeError, ValueError):
        return {'error': {'status': 400, 'name': 'USER_ERROR', 'message': "'adjust_qty_by' must be an integer (negative to decrease stock)."}}
    if qty == 0:
        return {'error': {'status': 400, 'name': 'USER_ERROR', 'message': "'adjust_qty_by' must be non-zero."}}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM erp_inventory_levels WHERE item = ? AND location = ?', (item, location)).fetchone()
    if row is None:
        conn.close()
        return {'error': {'status': 404, 'name': 'RCRD_DSNT_EXIST', 'message': "No inventory level exists for item '%s' at location '%s'." % (item, location)}}
    new_on_hand = row['quantity_on_hand'] + qty
    new_available = row['quantity_available'] + qty
    if new_on_hand < 0 or new_available < 0:
        conn.close()
        return {'error': {'status': 400, 'name': 'INVALID_QTY', 'message': 'Adjustment of %d would drive item %s at %s negative (on hand %d, available %d).' % (qty, item, location, row['quantity_on_hand'], row['quantity_available'])}}
    conn.execute('UPDATE erp_inventory_levels SET quantity_on_hand = ?, quantity_available = ? WHERE item = ? AND location = ?', (new_on_hand, new_available, item, location))
    conn.commit()
    updated = dict(conn.execute('SELECT * FROM erp_inventory_levels WHERE item = ? AND location = ?', (item, location)).fetchone())
    conn.close()
    now = datetime.datetime.utcnow().replace(microsecond=0)
    return {'inventory_adjustment': {'item': item, 'location': location, 'adjust_qty_by': qty, 'memo': kwargs.get('memo') or '', 'trandate': now.strftime('%Y-%m-%d')}, 'inventory_level': updated}

_env_orig_erp_inventory_adjustment_create = erp_inventory_adjustment_create
def _env_erp_inventory_adjustment_create(db_path='state.db', **kwargs):
    _r = _env_orig_erp_inventory_adjustment_create(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'items': _r['items'], 'count': _r['count'], 'hasMore': False, 'totalResults': _r['count'], 'offset': 0}
    if 'error' in _r and _r.get('status') == 404:
        return {'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.4', 'title': 'Not Found', 'status': 404, 'o:errorDetails': [{'detail': str(_r.get('error', '')), 'o:errorCode': 'RCRD_DSNT_EXIST'}]}
    if 'error' in _r and _r.get('status') == 400:
        return {'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.1', 'title': 'Bad Request', 'status': 400, 'o:errorDetails': [{'detail': str(_r.get('error', '')), 'o:errorCode': 'USER_ERROR'}]}
    return _r
erp_inventory_adjustment_create = _env_erp_inventory_adjustment_create

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_inventory_adjustment_create = erp_inventory_adjustment_create
def _bf_friction_erp_inventory_adjustment_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_inventory_adjustment_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_inventory_adjustment_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_inventory_adjustment_create(*_bf_args, **_bf_kwargs)
_bf_friction_erp_inventory_adjustment_create.blobfish_original = _bf_orig_erp_inventory_adjustment_create
erp_inventory_adjustment_create = _bf_friction_erp_inventory_adjustment_create
