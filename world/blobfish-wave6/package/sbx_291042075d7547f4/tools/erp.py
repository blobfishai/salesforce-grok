"""Executable ERP tool module

Inspect each function: SQLite helpers are local fixtures; network-backed functions call their declared endpoint.
Tools: purchase_orders_list, purchase_order_get, query_sourcing_purchase_orders, lookup_sourcing_purchase_order_with_sourcing_vendors, purchase_order_create, update_sourcing_purchase_orders_status, erp_sales_orders_list, erp_sales_order_get, erp_sales_order_create, erp_sales_order_update_status, erp_saved_search_run, erp_invoices_list, erp_invoice_get, erp_invoice_create, erp_items_list, erp_item_get, erp_item_create, erp_inventory_levels_list, erp_inventory_adjustment_create, erp_vendor_bills_list, erp_vendor_bill_get, erp_vendor_bill_create, erp_vendor_bill_approve, erp_customer_payments_list, erp_customer_payment_create, erp_credit_memos_list, erp_credit_memo_create, erp_currencies_list, erp_subsidiaries_list
Tables: purchase_orders, sourcing_purchase_orders, sourcing_vendors, erp_sales_orders, erp_invoices, erp_items, erp_inventory_levels, erp_vendor_bills, erp_customer_payments, erp_credit_memos, erp_currencies, erp_subsidiaries
"""
import json, sqlite3
def purchase_orders_list(db_path='state.db', **kwargs):
    '''List purchase_orders with bounded lifecycle filtering. (GET /services/data/v1/purchase_orders)'''
    if kwargs.get('status') is not None and kwargs.get('status') not in ['draft', 'pending_approval', 'approved', 'received', 'closed', 'cancelled']:
        return {'error': 'invalid value for status: %r. Accepted: %s' % (kwargs.get('status'), ', '.join(['draft', 'pending_approval', 'approved', 'received', 'closed', 'cancelled'])), 'status': 422, 'parameter': 'status', 'accepted': ['draft', 'pending_approval', 'approved', 'received', 'closed', 'cancelled']}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('status') is not None:
            _where.append('"status" = ?')
            _args.append(str(kwargs['status']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "purchase_orders"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        return {'items': _rows, 'count': len(_rows)}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_purchase_orders_list = purchase_orders_list
def _bf_friction_purchase_orders_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_purchase_orders_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "purchase_orders_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_purchase_orders_list(*_bf_args, **_bf_kwargs)
_bf_friction_purchase_orders_list.blobfish_original = _bf_orig_purchase_orders_list
purchase_orders_list = _bf_friction_purchase_orders_list

def purchase_order_get(db_path='state.db', **kwargs):
    '''Get one purchase_order by id. (GET /services/data/v1/purchase_orders/{id})'''
    _missing = [p for p in ['id'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "purchase_orders" WHERE "id" = ?', [str(kwargs.get('id'))]).fetchone()
        if _row is None:
            return {'error': 'purchase_order not found', 'status': 404}
        _out = dict(_row)
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_purchase_order_get = purchase_order_get
def _bf_friction_purchase_order_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_purchase_order_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "purchase_order_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
            _bf_kinds = ["service_unavailable","rate_limited","stale_reference"]
            _bf_messages = {"service_unavailable":"The service is temporarily unavailable (upstream timeout while processing the request). Please retry.","rate_limited":"Rate limit exceeded for this operation. Wait a moment and retry.","stale_reference":"The referenced record could not be loaded — the reference may be stale or recently changed. Re-fetch the latest data and retry."}
            _bf_kind = _bf_kinds[int(_bf_digest[8:12], 16) % len(_bf_kinds)]
            return {"success": False, "error": _bf_kind, "message": _bf_messages[_bf_kind], "retryable": True}
    return _bf_orig_purchase_order_get(*_bf_args, **_bf_kwargs)
_bf_friction_purchase_order_get.blobfish_original = _bf_orig_purchase_order_get
purchase_order_get = _bf_friction_purchase_order_get

"""Query sourcing_purchase_orders"""
import sqlite3

def query_sourcing_purchase_orders(db_path: str, **filters) -> dict:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row_limit = min(int(filters.pop("limit", 100)), 500)
    sql = 'SELECT * FROM "sourcing_purchase_orders" WHERE 1=1'
    params = []
    valid_cols = {c[1] for c in conn.execute('PRAGMA table_info("sourcing_purchase_orders")').fetchall()}
    for k, v in filters.items():
        if k in valid_cols:
            quoted_k = '"' + k.replace('"', '""') + '"'
            sql += f" AND {quoted_k} = ?"
            params.append(v)
    sql += " LIMIT ?"
    params.append(row_limit)
    rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
    conn.close()
    return {"table": "sourcing_purchase_orders", "count": len(rows), "rows": rows}

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_query_sourcing_purchase_orders = query_sourcing_purchase_orders
def _bf_friction_query_sourcing_purchase_orders(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_query_sourcing_purchase_orders(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "query_sourcing_purchase_orders|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
            _bf_kinds = ["service_unavailable","rate_limited","stale_reference"]
            _bf_messages = {"service_unavailable":"The service is temporarily unavailable (upstream timeout while processing the request). Please retry.","rate_limited":"Rate limit exceeded for this operation. Wait a moment and retry.","stale_reference":"The referenced record could not be loaded — the reference may be stale or recently changed. Re-fetch the latest data and retry."}
            _bf_kind = _bf_kinds[int(_bf_digest[8:12], 16) % len(_bf_kinds)]
            return {"success": False, "error": _bf_kind, "message": _bf_messages[_bf_kind], "retryable": True}
    return _bf_orig_query_sourcing_purchase_orders(*_bf_args, **_bf_kwargs)
_bf_friction_query_sourcing_purchase_orders.blobfish_original = _bf_orig_query_sourcing_purchase_orders
query_sourcing_purchase_orders = _bf_friction_query_sourcing_purchase_orders

"""Look up sourcing_purchase_order with sourcing_vendors context"""
import sqlite3

def lookup_sourcing_purchase_order_with_sourcing_vendors(db_path: str, id: int) -> dict:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM sourcing_purchase_orders WHERE id = ?", [id]).fetchone()
    if not row:
        conn.close()
        return {"error": f"sourcing_purchase_order {id} not found"}
    result = dict(row)
    parent = conn.execute("SELECT * FROM sourcing_vendors WHERE id = ?", [row["vendor_id"]]).fetchone()
    result["sourcing_vendors"] = dict(parent) if parent else None
    conn.close()
    return result

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_lookup_sourcing_purchase_order_with_sourcing_vendors = lookup_sourcing_purchase_order_with_sourcing_vendors
def _bf_friction_lookup_sourcing_purchase_order_with_sourcing_vendors(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_lookup_sourcing_purchase_order_with_sourcing_vendors(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "lookup_sourcing_purchase_order_with_sourcing_vendors|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
            _bf_kinds = ["service_unavailable","rate_limited","stale_reference"]
            _bf_messages = {"service_unavailable":"The service is temporarily unavailable (upstream timeout while processing the request). Please retry.","rate_limited":"Rate limit exceeded for this operation. Wait a moment and retry.","stale_reference":"The referenced record could not be loaded — the reference may be stale or recently changed. Re-fetch the latest data and retry."}
            _bf_kind = _bf_kinds[int(_bf_digest[8:12], 16) % len(_bf_kinds)]
            return {"success": False, "error": _bf_kind, "message": _bf_messages[_bf_kind], "retryable": True}
    return _bf_orig_lookup_sourcing_purchase_order_with_sourcing_vendors(*_bf_args, **_bf_kwargs)
_bf_friction_lookup_sourcing_purchase_order_with_sourcing_vendors.blobfish_original = _bf_orig_lookup_sourcing_purchase_order_with_sourcing_vendors
lookup_sourcing_purchase_order_with_sourcing_vendors = _bf_friction_lookup_sourcing_purchase_order_with_sourcing_vendors

def purchase_order_create(db_path='state.db', **kwargs):
    '''Create one tenant-scoped purchase_order. (POST /services/data/v1/purchase_orders)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _n = cur.execute('SELECT COALESCE(MAX(rowid), 0) + 100 FROM "purchase_orders"').fetchone()[0] + 1
        _base = datetime.datetime(2026, 1, 5, 9, 0, 0)
        _ts = (_base + datetime.timedelta(minutes=_n)).strftime('%Y-%m-%dT%H:%M:%SZ')
        _cols = ['"id"']
        _vals = ['purchase_order_%03d' % _n]
        if kwargs.get('vendor_id') is not None:
            _cols.append('"vendor_id"')
            _vals.append(str(kwargs['vendor_id']))
        if kwargs.get('status') is not None:
            _cols.append('"status"')
            _vals.append(str(kwargs['status']))
        if kwargs.get('amount') is not None:
            _cols.append('"amount"')
            _vals.append(float(kwargs['amount']))
        if kwargs.get('currency') is not None:
            _cols.append('"currency"')
            _vals.append(str(kwargs['currency']))
        if kwargs.get('owner_id') is not None:
            _cols.append('"owner_id"')
            _vals.append(str(kwargs['owner_id']))
        _cols.append('"created_at"')
        _vals.append(_ts)
        if '"status"' not in _cols:
            _cols.append('"status"')
            _vals.append('open')
        _sql = 'INSERT INTO "purchase_orders" (' + ', '.join(_cols) + ') VALUES (' + ', '.join(['?'] * len(_vals)) + ')'
        try:
            cur.execute(_sql, _vals)
        except sqlite3.IntegrityError:
            conn.rollback()
            return {'error': 'conflict: duplicate key', 'status': 409}
        conn.commit()
        _row = cur.execute('SELECT * FROM "purchase_orders" WHERE "id" = ?', [_vals[0]]).fetchone()
        _out = dict(_row)
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_purchase_order_create = purchase_order_create
def _bf_friction_purchase_order_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_purchase_order_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "purchase_order_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_purchase_order_create(*_bf_args, **_bf_kwargs)
_bf_friction_purchase_order_create.blobfish_original = _bf_orig_purchase_order_create
purchase_order_create = _bf_friction_purchase_order_create

"""Update sourcing_purchase_orders status with validation"""
import sqlite3

def update_sourcing_purchase_orders_status(db_path: str, id: int, new_status: str) -> dict:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM "sourcing_purchase_orders" WHERE "id" = ?', [id]).fetchone()
    if not row:
        conn.close()
        return {"error": f"sourcing purchase orders {id} not found"}
    valid = ["draft", "submitted", "approved", "received", "closed"]
    if valid and new_status not in valid:
        conn.close()
        return {"error": f"Invalid status '{new_status}'. Valid: {valid}"}
    old_status = row['status']
    conn.execute('UPDATE "sourcing_purchase_orders" SET "status" = ? WHERE "id" = ?', [new_status, id])
    conn.commit()
    conn.close()
    return {"updated": True, "id": id, "table": "sourcing_purchase_orders", "old_status": old_status, "new_status": new_status}

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_update_sourcing_purchase_orders_status = update_sourcing_purchase_orders_status
def _bf_friction_update_sourcing_purchase_orders_status(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_update_sourcing_purchase_orders_status(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "update_sourcing_purchase_orders_status|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_update_sourcing_purchase_orders_status(*_bf_args, **_bf_kwargs)
_bf_friction_update_sourcing_purchase_orders_status.blobfish_original = _bf_orig_update_sourcing_purchase_orders_status
update_sourcing_purchase_orders_status = _bf_friction_update_sourcing_purchase_orders_status

def erp_sales_orders_list(db_path='state.db', **kwargs):
    '''List sales order transactions, optionally filtered by status or customer entity (GET /services/rest/record/v1/salesOrder)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('status') is not None:
            _where.append('"status" = ?')
            _args.append(str(kwargs['status']))
        if kwargs.get('entity') is not None:
            _where.append('"entity" = ?')
            _args.append(str(kwargs['entity']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "erp_sales_orders"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'items': _r['items'], 'count': _r['count'], 'hasMore': False, 'totalResults': _r['count'], 'offset': 0}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_sales_orders_list = erp_sales_orders_list
def _bf_friction_erp_sales_orders_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_sales_orders_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_sales_orders_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_sales_orders_list(*_bf_args, **_bf_kwargs)
_bf_friction_erp_sales_orders_list.blobfish_original = _bf_orig_erp_sales_orders_list
erp_sales_orders_list = _bf_friction_erp_sales_orders_list

def erp_sales_order_get(db_path='state.db', **kwargs):
    '''Retrieve a single sales order by its tranId-style internal identifier (GET /services/rest/record/v1/salesOrder/{id})'''
    _missing = [p for p in ['id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.1', 'title': 'Bad Request', 'status': 400, 'o:errorDetails': [{'detail': str(_r.get('error', '')), 'o:errorCode': 'USER_ERROR'}]}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "erp_sales_orders" WHERE "id" = ?', [str(kwargs['id'])]).fetchone()
        if _row is None:
            _r = {'error': 'sales_order not found', 'status': 404}
            return {'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.4', 'title': 'Not Found', 'status': 404, 'o:errorDetails': [{'detail': str(_r.get('error', '')), 'o:errorCode': 'RCRD_DSNT_EXIST'}]}
        _r = dict(_row)
        _r['links'] = []
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_sales_order_get = erp_sales_order_get
def _bf_friction_erp_sales_order_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_sales_order_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_sales_order_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_sales_order_get(*_bf_args, **_bf_kwargs)
_bf_friction_erp_sales_order_get.blobfish_original = _bf_orig_erp_sales_order_get
erp_sales_order_get = _bf_friction_erp_sales_order_get

def erp_sales_order_create(db_path='state.db', **kwargs):
    '''Create a sales order for a customer; new orders start in pendingApproval (POST /services/rest/record/v1/salesOrder)'''
    _missing = [p for p in ['entity', 'total'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.1', 'title': 'Bad Request', 'status': 400, 'o:errorDetails': [{'detail': str(_r.get('error', '')), 'o:errorCode': 'USER_ERROR'}]}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "erp_sales_orders"').fetchone()[0] + 1
        _id = 'SO-2026-' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "erp_sales_orders" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'SO-2026-' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('entity') is not None:
            _cols.append('entity')
            _v = kwargs['entity']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('entity_name') is not None:
            _cols.append('entity_name')
            _v = kwargs['entity_name']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('trandate') is not None:
            _cols.append('trandate')
            _v = kwargs['trandate']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('memo') is not None:
            _cols.append('memo')
            _v = kwargs['memo']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('subsidiary') is not None:
            _cols.append('subsidiary')
            _v = kwargs['subsidiary']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('currency') is not None:
            _cols.append('currency')
            _v = kwargs['currency']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('total') is not None:
            _cols.append('total')
            _v = kwargs['total']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'status' not in _cols:
            _cols.append('status')
            _vals.append('pendingApproval')
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "erp_sales_orders" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "erp_sales_orders" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['links'] = []
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_sales_order_create = erp_sales_order_create
def _bf_friction_erp_sales_order_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_sales_order_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_sales_order_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_sales_order_create(*_bf_args, **_bf_kwargs)
_bf_friction_erp_sales_order_create.blobfish_original = _bf_orig_erp_sales_order_create
erp_sales_order_create = _bf_friction_erp_sales_order_create

def erp_sales_order_update_status(db_path='state.db', **kwargs):
    import sqlite3
    so_id = kwargs.get('id')
    new_status = kwargs.get('status')
    if not so_id or not new_status:
        return {'error': {'status': 400, 'name': 'USER_ERROR', 'message': "Params 'id' and 'status' are required."}}
    transitions = {
        'pendingApproval': ['pendingFulfillment', 'cancelled'],
        'pendingFulfillment': ['billed', 'cancelled'],
        'billed': [],
        'cancelled': []
    }
    if new_status not in transitions:
        return {'error': {'status': 400, 'name': 'INVALID_ORDER_STATUS', 'message': "Unknown status '%s'. Valid statuses: pendingApproval, pendingFulfillment, billed, cancelled." % new_status}}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM erp_sales_orders WHERE id = ?', (so_id,)).fetchone()
    if row is None:
        conn.close()
        return {'error': {'status': 404, 'name': 'RCRD_DSNT_EXIST', 'message': "Sales order '%s' does not exist." % so_id}}
    current = row['status']
    allowed = transitions.get(current, [])
    if new_status not in allowed:
        conn.close()
        return {'error': {'status': 400, 'name': 'INVALID_STATUS_TRANSITION', 'message': "Cannot move sales order %s from '%s' to '%s'. Allowed next statuses: %s." % (so_id, current, new_status, ', '.join(allowed) if allowed else 'none (terminal status)')}}
    conn.execute('UPDATE erp_sales_orders SET status = ? WHERE id = ?', (new_status, so_id))
    conn.commit()
    updated = dict(conn.execute('SELECT * FROM erp_sales_orders WHERE id = ?', (so_id,)).fetchone())
    conn.close()
    return updated

_env_orig_erp_sales_order_update_status = erp_sales_order_update_status
def _env_erp_sales_order_update_status(db_path='state.db', **kwargs):
    _r = _env_orig_erp_sales_order_update_status(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'items': _r['items'], 'count': _r['count'], 'hasMore': False, 'totalResults': _r['count'], 'offset': 0}
    if 'error' in _r and _r.get('status') == 404:
        return {'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.4', 'title': 'Not Found', 'status': 404, 'o:errorDetails': [{'detail': str(_r.get('error', '')), 'o:errorCode': 'RCRD_DSNT_EXIST'}]}
    if 'error' in _r and _r.get('status') == 400:
        return {'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.1', 'title': 'Bad Request', 'status': 400, 'o:errorDetails': [{'detail': str(_r.get('error', '')), 'o:errorCode': 'USER_ERROR'}]}
    return _r
erp_sales_order_update_status = _env_erp_sales_order_update_status

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_sales_order_update_status = erp_sales_order_update_status
def _bf_friction_erp_sales_order_update_status(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_sales_order_update_status(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_sales_order_update_status|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_sales_order_update_status(*_bf_args, **_bf_kwargs)
_bf_friction_erp_sales_order_update_status.blobfish_original = _bf_orig_erp_sales_order_update_status
erp_sales_order_update_status = _bf_friction_erp_sales_order_update_status

def erp_saved_search_run(db_path='state.db', **kwargs):
    '''Run a simplified transaction saved search over sales orders; keywords LIKE-match against tranId, customer name, memo and status (POST /services/rest/query/v1/suiteql)'''
    _missing = [p for p in ['query'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.1', 'title': 'Bad Request', 'status': 400, 'o:errorDetails': [{'detail': str(_r.get('error', '')), 'o:errorCode': 'USER_ERROR'}]}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _qv = '%' + str(kwargs['query']) + '%'
        _where, _args = ["(\"id\" LIKE ? OR \"entity_name\" LIKE ? OR \"memo\" LIKE ? OR \"status\" LIKE ?)"], [_qv] * 4
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "erp_sales_orders" WHERE ' + ' AND '.join(_where) + ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'items': _r['items'], 'count': _r['count'], 'hasMore': False, 'totalResults': _r['count'], 'offset': 0}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_saved_search_run = erp_saved_search_run
def _bf_friction_erp_saved_search_run(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_saved_search_run(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_saved_search_run|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_saved_search_run(*_bf_args, **_bf_kwargs)
_bf_friction_erp_saved_search_run.blobfish_original = _bf_orig_erp_saved_search_run
erp_saved_search_run = _bf_friction_erp_saved_search_run

def erp_invoices_list(db_path='state.db', **kwargs):
    '''List invoice transactions (AR), optionally filtered by status, customer entity or originating sales order (GET /services/rest/record/v1/invoice)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('status') is not None:
            _where.append('"status" = ?')
            _args.append(str(kwargs['status']))
        if kwargs.get('entity') is not None:
            _where.append('"entity" = ?')
            _args.append(str(kwargs['entity']))
        if kwargs.get('created_from') is not None:
            _where.append('"created_from" = ?')
            _args.append(str(kwargs['created_from']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "erp_invoices"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'items': _r['items'], 'count': _r['count'], 'hasMore': False, 'totalResults': _r['count'], 'offset': 0}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_invoices_list = erp_invoices_list
def _bf_friction_erp_invoices_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_invoices_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_invoices_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_invoices_list(*_bf_args, **_bf_kwargs)
_bf_friction_erp_invoices_list.blobfish_original = _bf_orig_erp_invoices_list
erp_invoices_list = _bf_friction_erp_invoices_list

def erp_invoice_get(db_path='state.db', **kwargs):
    '''Retrieve a single invoice with totals and amount remaining (GET /services/rest/record/v1/invoice/{id})'''
    _missing = [p for p in ['id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.1', 'title': 'Bad Request', 'status': 400, 'o:errorDetails': [{'detail': str(_r.get('error', '')), 'o:errorCode': 'USER_ERROR'}]}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "erp_invoices" WHERE "id" = ?', [str(kwargs['id'])]).fetchone()
        if _row is None:
            _r = {'error': 'invoice not found', 'status': 404}
            return {'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.4', 'title': 'Not Found', 'status': 404, 'o:errorDetails': [{'detail': str(_r.get('error', '')), 'o:errorCode': 'RCRD_DSNT_EXIST'}]}
        _r = dict(_row)
        _r['links'] = []
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_invoice_get = erp_invoice_get
def _bf_friction_erp_invoice_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_invoice_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_invoice_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_invoice_get(*_bf_args, **_bf_kwargs)
_bf_friction_erp_invoice_get.blobfish_original = _bf_orig_erp_invoice_get
erp_invoice_get = _bf_friction_erp_invoice_get

def erp_invoice_create(db_path='state.db', **kwargs):
    '''Create a standalone or order-billed invoice; new invoices open with the full amount remaining (POST /services/rest/record/v1/invoice)'''
    _missing = [p for p in ['entity', 'total'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.1', 'title': 'Bad Request', 'status': 400, 'o:errorDetails': [{'detail': str(_r.get('error', '')), 'o:errorCode': 'USER_ERROR'}]}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "erp_invoices"').fetchone()[0] + 1
        _id = 'INV-' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "erp_invoices" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'INV-' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('entity') is not None:
            _cols.append('entity')
            _v = kwargs['entity']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('entity_name') is not None:
            _cols.append('entity_name')
            _v = kwargs['entity_name']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('created_from') is not None:
            _cols.append('created_from')
            _v = kwargs['created_from']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('trandate') is not None:
            _cols.append('trandate')
            _v = kwargs['trandate']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('due_date') is not None:
            _cols.append('due_date')
            _v = kwargs['due_date']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('memo') is not None:
            _cols.append('memo')
            _v = kwargs['memo']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('subsidiary') is not None:
            _cols.append('subsidiary')
            _v = kwargs['subsidiary']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('currency') is not None:
            _cols.append('currency')
            _v = kwargs['currency']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('subtotal') is not None:
            _cols.append('subtotal')
            _v = kwargs['subtotal']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('tax_total') is not None:
            _cols.append('tax_total')
            _v = kwargs['tax_total']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('total') is not None:
            _cols.append('total')
            _v = kwargs['total']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'status' not in _cols:
            _cols.append('status')
            _vals.append('open')
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "erp_invoices" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "erp_invoices" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['links'] = []
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_invoice_create = erp_invoice_create
def _bf_friction_erp_invoice_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_invoice_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_invoice_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_invoice_create(*_bf_args, **_bf_kwargs)
_bf_friction_erp_invoice_create.blobfish_original = _bf_orig_erp_invoice_create
erp_invoice_create = _bf_friction_erp_invoice_create

def erp_items_list(db_path='state.db', **kwargs):
    '''List items in the GTM catalog (licenses, data feeds, services, appliances), optionally filtered by item type or inactive flag (GET /services/rest/record/v1/serviceItem, also inventoryItem/nonInventoryItem)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('type') is not None:
            _where.append('"type" = ?')
            _args.append(str(kwargs['type']))
        if kwargs.get('is_inactive') is not None:
            _where.append('"is_inactive" = ?')
            _args.append(str(kwargs['is_inactive']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "erp_items"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'items': _r['items'], 'count': _r['count'], 'hasMore': False, 'totalResults': _r['count'], 'offset': 0}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_items_list = erp_items_list
def _bf_friction_erp_items_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_items_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_items_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_items_list(*_bf_args, **_bf_kwargs)
_bf_friction_erp_items_list.blobfish_original = _bf_orig_erp_items_list
erp_items_list = _bf_friction_erp_items_list

def erp_item_get(db_path='state.db', **kwargs):
    '''Retrieve a single item record by its itemId/SKU (GET /services/rest/record/v1/serviceItem/{id})'''
    _missing = [p for p in ['id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.1', 'title': 'Bad Request', 'status': 400, 'o:errorDetails': [{'detail': str(_r.get('error', '')), 'o:errorCode': 'USER_ERROR'}]}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "erp_items" WHERE "id" = ?', [str(kwargs['id'])]).fetchone()
        if _row is None:
            _r = {'error': 'item not found', 'status': 404}
            return {'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.4', 'title': 'Not Found', 'status': 404, 'o:errorDetails': [{'detail': str(_r.get('error', '')), 'o:errorCode': 'RCRD_DSNT_EXIST'}]}
        _r = dict(_row)
        _r['links'] = []
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_item_get = erp_item_get
def _bf_friction_erp_item_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_item_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_item_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_item_get(*_bf_args, **_bf_kwargs)
_bf_friction_erp_item_get.blobfish_original = _bf_orig_erp_item_get
erp_item_get = _bf_friction_erp_item_get

def erp_item_create(db_path='state.db', **kwargs):
    '''Create a new item in the catalog (POST /services/rest/record/v1/serviceItem)'''
    _missing = [p for p in ['display_name', 'type', 'base_price'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.1', 'title': 'Bad Request', 'status': 400, 'o:errorDetails': [{'detail': str(_r.get('error', '')), 'o:errorCode': 'USER_ERROR'}]}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "erp_items"').fetchone()[0] + 1
        _id = 'ITEM-' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "erp_items" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'ITEM-' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('display_name') is not None:
            _cols.append('display_name')
            _v = kwargs['display_name']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('type') is not None:
            _cols.append('type')
            _v = kwargs['type']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('base_price') is not None:
            _cols.append('base_price')
            _v = kwargs['base_price']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('currency') is not None:
            _cols.append('currency')
            _v = kwargs['currency']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('income_account') is not None:
            _cols.append('income_account')
            _v = kwargs['income_account']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'is_inactive' not in _cols:
            _cols.append('is_inactive')
            _vals.append(0)
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "erp_items" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "erp_items" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['links'] = []
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_item_create = erp_item_create
def _bf_friction_erp_item_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_item_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_item_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_item_create(*_bf_args, **_bf_kwargs)
_bf_friction_erp_item_create.blobfish_original = _bf_orig_erp_item_create
erp_item_create = _bf_friction_erp_item_create

def erp_inventory_levels_list(db_path='state.db', **kwargs):
    '''List per-location inventory balances for stocked items, optionally filtered by item or location (POST /services/rest/query/v1/suiteql - inventorybalance)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('item') is not None:
            _where.append('"item" = ?')
            _args.append(str(kwargs['item']))
        if kwargs.get('location') is not None:
            _where.append('"location" = ?')
            _args.append(str(kwargs['location']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "erp_inventory_levels"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'items': _r['items'], 'count': _r['count'], 'hasMore': False, 'totalResults': _r['count'], 'offset': 0}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_inventory_levels_list = erp_inventory_levels_list
def _bf_friction_erp_inventory_levels_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_inventory_levels_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_inventory_levels_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_inventory_levels_list(*_bf_args, **_bf_kwargs)
_bf_friction_erp_inventory_levels_list.blobfish_original = _bf_orig_erp_inventory_levels_list
erp_inventory_levels_list = _bf_friction_erp_inventory_levels_list

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

def erp_vendor_bills_list(db_path='state.db', **kwargs):
    '''List vendor bill transactions (AP), optionally filtered by payment status, approval status or vendor entity (GET /services/rest/record/v1/vendorBill)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('status') is not None:
            _where.append('"status" = ?')
            _args.append(str(kwargs['status']))
        if kwargs.get('approval_status') is not None:
            _where.append('"approval_status" = ?')
            _args.append(str(kwargs['approval_status']))
        if kwargs.get('entity') is not None:
            _where.append('"entity" = ?')
            _args.append(str(kwargs['entity']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "erp_vendor_bills"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'items': _r['items'], 'count': _r['count'], 'hasMore': False, 'totalResults': _r['count'], 'offset': 0}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_vendor_bills_list = erp_vendor_bills_list
def _bf_friction_erp_vendor_bills_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_vendor_bills_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_vendor_bills_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_vendor_bills_list(*_bf_args, **_bf_kwargs)
_bf_friction_erp_vendor_bills_list.blobfish_original = _bf_orig_erp_vendor_bills_list
erp_vendor_bills_list = _bf_friction_erp_vendor_bills_list

def erp_vendor_bill_get(db_path='state.db', **kwargs):
    '''Retrieve a single vendor bill by its tranId-style identifier (GET /services/rest/record/v1/vendorBill/{id})'''
    _missing = [p for p in ['id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.1', 'title': 'Bad Request', 'status': 400, 'o:errorDetails': [{'detail': str(_r.get('error', '')), 'o:errorCode': 'USER_ERROR'}]}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "erp_vendor_bills" WHERE "id" = ?', [str(kwargs['id'])]).fetchone()
        if _row is None:
            _r = {'error': 'vendor_bill not found', 'status': 404}
            return {'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.4', 'title': 'Not Found', 'status': 404, 'o:errorDetails': [{'detail': str(_r.get('error', '')), 'o:errorCode': 'RCRD_DSNT_EXIST'}]}
        _r = dict(_row)
        _r['links'] = []
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_vendor_bill_get = erp_vendor_bill_get
def _bf_friction_erp_vendor_bill_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_vendor_bill_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_vendor_bill_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_vendor_bill_get(*_bf_args, **_bf_kwargs)
_bf_friction_erp_vendor_bill_get.blobfish_original = _bf_orig_erp_vendor_bill_get
erp_vendor_bill_get = _bf_friction_erp_vendor_bill_get

def erp_vendor_bill_create(db_path='state.db', **kwargs):
    '''Enter a vendor bill; new bills are open and route as pendingApproval (POST /services/rest/record/v1/vendorBill)'''
    _missing = [p for p in ['entity', 'amount'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.1', 'title': 'Bad Request', 'status': 400, 'o:errorDetails': [{'detail': str(_r.get('error', '')), 'o:errorCode': 'USER_ERROR'}]}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "erp_vendor_bills"').fetchone()[0] + 1
        _id = 'BILL-' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "erp_vendor_bills" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'BILL-' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('entity') is not None:
            _cols.append('entity')
            _v = kwargs['entity']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('entity_name') is not None:
            _cols.append('entity_name')
            _v = kwargs['entity_name']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('trandate') is not None:
            _cols.append('trandate')
            _v = kwargs['trandate']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('due_date') is not None:
            _cols.append('due_date')
            _v = kwargs['due_date']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('memo') is not None:
            _cols.append('memo')
            _v = kwargs['memo']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('subsidiary') is not None:
            _cols.append('subsidiary')
            _v = kwargs['subsidiary']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('currency') is not None:
            _cols.append('currency')
            _v = kwargs['currency']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('amount') is not None:
            _cols.append('amount')
            _v = kwargs['amount']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'approval_status' not in _cols:
            _cols.append('approval_status')
            _vals.append('pendingApproval')
        if 'status' not in _cols:
            _cols.append('status')
            _vals.append('open')
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "erp_vendor_bills" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "erp_vendor_bills" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['links'] = []
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_vendor_bill_create = erp_vendor_bill_create
def _bf_friction_erp_vendor_bill_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_vendor_bill_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_vendor_bill_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_vendor_bill_create(*_bf_args, **_bf_kwargs)
_bf_friction_erp_vendor_bill_create.blobfish_original = _bf_orig_erp_vendor_bill_create
erp_vendor_bill_create = _bf_friction_erp_vendor_bill_create

def erp_vendor_bill_approve(db_path='state.db', **kwargs):
    import sqlite3
    bill_id = kwargs.get('id')
    if not bill_id:
        return {'error': {'status': 400, 'name': 'USER_ERROR', 'message': "Param 'id' is required."}}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM erp_vendor_bills WHERE id = ?', (bill_id,)).fetchone()
    if row is None:
        conn.close()
        return {'error': {'status': 404, 'name': 'RCRD_DSNT_EXIST', 'message': "Vendor bill '%s' does not exist." % bill_id}}
    current = row['approval_status']
    if current == 'approved':
        conn.close()
        return {'error': {'status': 400, 'name': 'INVALID_STATUS_TRANSITION', 'message': 'Vendor bill %s is already approved.' % bill_id}}
    if current == 'rejected':
        conn.close()
        return {'error': {'status': 400, 'name': 'INVALID_STATUS_TRANSITION', 'message': 'Vendor bill %s was rejected; it must be corrected and resubmitted before it can be approved.' % bill_id}}
    conn.execute("UPDATE erp_vendor_bills SET approval_status = 'approved' WHERE id = ?", (bill_id,))
    conn.commit()
    updated = dict(conn.execute('SELECT * FROM erp_vendor_bills WHERE id = ?', (bill_id,)).fetchone())
    conn.close()
    return updated

_env_orig_erp_vendor_bill_approve = erp_vendor_bill_approve
def _env_erp_vendor_bill_approve(db_path='state.db', **kwargs):
    _r = _env_orig_erp_vendor_bill_approve(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'items': _r['items'], 'count': _r['count'], 'hasMore': False, 'totalResults': _r['count'], 'offset': 0}
    if 'error' in _r and _r.get('status') == 404:
        return {'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.4', 'title': 'Not Found', 'status': 404, 'o:errorDetails': [{'detail': str(_r.get('error', '')), 'o:errorCode': 'RCRD_DSNT_EXIST'}]}
    if 'error' in _r and _r.get('status') == 400:
        return {'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.1', 'title': 'Bad Request', 'status': 400, 'o:errorDetails': [{'detail': str(_r.get('error', '')), 'o:errorCode': 'USER_ERROR'}]}
    return _r
erp_vendor_bill_approve = _env_erp_vendor_bill_approve

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_vendor_bill_approve = erp_vendor_bill_approve
def _bf_friction_erp_vendor_bill_approve(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_vendor_bill_approve(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_vendor_bill_approve|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_vendor_bill_approve(*_bf_args, **_bf_kwargs)
_bf_friction_erp_vendor_bill_approve.blobfish_original = _bf_orig_erp_vendor_bill_approve
erp_vendor_bill_approve = _bf_friction_erp_vendor_bill_approve

def erp_customer_payments_list(db_path='state.db', **kwargs):
    '''List customer payment transactions, optionally filtered by customer entity or the invoice they were applied to (GET /services/rest/record/v1/customerPayment)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('entity') is not None:
            _where.append('"entity" = ?')
            _args.append(str(kwargs['entity']))
        if kwargs.get('applied_to') is not None:
            _where.append('"applied_to" = ?')
            _args.append(str(kwargs['applied_to']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "erp_customer_payments"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'items': _r['items'], 'count': _r['count'], 'hasMore': False, 'totalResults': _r['count'], 'offset': 0}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_customer_payments_list = erp_customer_payments_list
def _bf_friction_erp_customer_payments_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_customer_payments_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_customer_payments_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_customer_payments_list(*_bf_args, **_bf_kwargs)
_bf_friction_erp_customer_payments_list.blobfish_original = _bf_orig_erp_customer_payments_list
erp_customer_payments_list = _bf_friction_erp_customer_payments_list

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

def erp_credit_memos_list(db_path='state.db', **kwargs):
    '''List credit memo transactions, optionally filtered by status or customer entity (GET /services/rest/record/v1/creditMemo)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('status') is not None:
            _where.append('"status" = ?')
            _args.append(str(kwargs['status']))
        if kwargs.get('entity') is not None:
            _where.append('"entity" = ?')
            _args.append(str(kwargs['entity']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "erp_credit_memos"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'items': _r['items'], 'count': _r['count'], 'hasMore': False, 'totalResults': _r['count'], 'offset': 0}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_credit_memos_list = erp_credit_memos_list
def _bf_friction_erp_credit_memos_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_credit_memos_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_credit_memos_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_credit_memos_list(*_bf_args, **_bf_kwargs)
_bf_friction_erp_credit_memos_list.blobfish_original = _bf_orig_erp_credit_memos_list
erp_credit_memos_list = _bf_friction_erp_credit_memos_list

def erp_credit_memo_create(db_path='state.db', **kwargs):
    '''Issue a credit memo to a customer, optionally referencing the invoice it credits (POST /services/rest/record/v1/creditMemo)'''
    _missing = [p for p in ['entity', 'total'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.1', 'title': 'Bad Request', 'status': 400, 'o:errorDetails': [{'detail': str(_r.get('error', '')), 'o:errorCode': 'USER_ERROR'}]}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "erp_credit_memos"').fetchone()[0] + 1
        _id = 'CM-' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "erp_credit_memos" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'CM-' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('entity') is not None:
            _cols.append('entity')
            _v = kwargs['entity']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('entity_name') is not None:
            _cols.append('entity_name')
            _v = kwargs['entity_name']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('created_from') is not None:
            _cols.append('created_from')
            _v = kwargs['created_from']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('trandate') is not None:
            _cols.append('trandate')
            _v = kwargs['trandate']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('memo') is not None:
            _cols.append('memo')
            _v = kwargs['memo']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('currency') is not None:
            _cols.append('currency')
            _v = kwargs['currency']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('total') is not None:
            _cols.append('total')
            _v = kwargs['total']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'status' not in _cols:
            _cols.append('status')
            _vals.append('open')
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "erp_credit_memos" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "erp_credit_memos" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['links'] = []
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_credit_memo_create = erp_credit_memo_create
def _bf_friction_erp_credit_memo_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_credit_memo_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_credit_memo_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_credit_memo_create(*_bf_args, **_bf_kwargs)
_bf_friction_erp_credit_memo_create.blobfish_original = _bf_orig_erp_credit_memo_create
erp_credit_memo_create = _bf_friction_erp_credit_memo_create

def erp_currencies_list(db_path='state.db', **kwargs):
    '''List currency records with ISO symbol and exchange rate to the base currency (GET /services/rest/record/v1/currency)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "erp_currencies"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'items': _r['items'], 'count': _r['count'], 'hasMore': False, 'totalResults': _r['count'], 'offset': 0}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_currencies_list = erp_currencies_list
def _bf_friction_erp_currencies_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_currencies_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_currencies_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_currencies_list(*_bf_args, **_bf_kwargs)
_bf_friction_erp_currencies_list.blobfish_original = _bf_orig_erp_currencies_list
erp_currencies_list = _bf_friction_erp_currencies_list

def erp_subsidiaries_list(db_path='state.db', **kwargs):
    '''List subsidiaries in the corporate hierarchy, including the consolidation elimination subsidiary (GET /services/rest/record/v1/subsidiary)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "erp_subsidiaries"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'items': _r['items'], 'count': _r['count'], 'hasMore': False, 'totalResults': _r['count'], 'offset': 0}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_erp_subsidiaries_list = erp_subsidiaries_list
def _bf_friction_erp_subsidiaries_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_erp_subsidiaries_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "erp_subsidiaries_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_erp_subsidiaries_list(*_bf_args, **_bf_kwargs)
_bf_friction_erp_subsidiaries_list.blobfish_original = _bf_orig_erp_subsidiaries_list
erp_subsidiaries_list = _bf_friction_erp_subsidiaries_list

