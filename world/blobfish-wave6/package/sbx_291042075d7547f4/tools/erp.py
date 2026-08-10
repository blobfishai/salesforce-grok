"""Executable ERP tool module

Inspect each function: SQLite helpers are local fixtures; network-backed functions call their declared endpoint.
Tools: admin_emoji_list, purchase_orders_list, purchase_order_get, query_sourcing_purchase_orders, lookup_sourcing_purchase_order_with_sourcing_vendors, purchase_order_create, update_sourcing_purchase_orders_status
Tables: admin_emojis, purchase_orders, sourcing_purchase_orders, sourcing_vendors
"""
import json, sqlite3
def admin_emoji_list(db_path='state.db', **kwargs):
    '''List emoji for an Enterprise Grid organization. (GET /admin.emoji.list)'''
    _missing = [p for p in ['token'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('token') is not None:
            _where.append('"token" = ?')
            _args.append(str(kwargs['token']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "admin_emojis"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        return {'items': _rows, 'count': len(_rows)}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_admin_emoji_list = admin_emoji_list
def _bf_friction_admin_emoji_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_admin_emoji_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "admin_emoji_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_admin_emoji_list(*_bf_args, **_bf_kwargs)
_bf_friction_admin_emoji_list.blobfish_original = _bf_orig_admin_emoji_list
admin_emoji_list = _bf_friction_admin_emoji_list

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

