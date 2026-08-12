"""Executable STRIPE tool module

Inspect each function: SQLite helpers are local fixtures; network-backed functions call their declared endpoint.
Tools: get_charges, get_charges_charge_dispute, get_invoices, get_invoice_rendering_templates, get_payment_intents_intent_amount_details_line_items, post_charges, post_charges_charge_dispute_close, get_customers, get_customers_customer, post_customers, post_customers_customer, get_products, post_products, get_prices, post_prices, get_subscriptions, get_subscriptions_subscription, post_subscriptions, post_subscriptions_subscription, delete_subscriptions_subscription, get_payment_intents, post_payment_intents, post_payment_intents_intent_confirm, post_payment_intents_intent_capture, get_refunds, post_refunds, get_payment_links, post_payment_links, post_invoices, post_invoices_invoice_finalize, post_invoices_invoice_void, post_invoices_invoice_pay, post_invoiceitems, get_coupons, post_coupons, get_balance, get_events, get_disputes, product_update, product_delete, products_search, customer_update, customer_delete, customers_search, subscription_update
Tables: charges, disputes, invoices, invoice_rendering_templates, amount_details_line_items, customers, products, prices, subscriptions, payment_intents, refunds, payment_links, invoiceitems, coupons, balance_transactions, stripe_events
"""
import json, sqlite3
def get_charges(db_path='state.db', **kwargs):
    '''List all charges (GET /v1/charges)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('created') is not None:
            _where.append('"created" = ?')
            _args.append(str(kwargs['created']))
        if kwargs.get('customer') is not None:
            _where.append('"customer" = ?')
            _args.append(str(kwargs['customer']))
        if kwargs.get('payment_intent') is not None:
            _where.append('"payment_intent" = ?')
            _args.append(str(kwargs['payment_intent']))
        if kwargs.get('transfer_group') is not None:
            _where.append('"transfer_group" = ?')
            _args.append(str(kwargs['transfer_group']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "charges"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        return {'items': _rows, 'count': len(_rows)}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_charges = get_charges
def _bf_friction_get_charges(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_charges(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_charges|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_charges(*_bf_args, **_bf_kwargs)
_bf_friction_get_charges.blobfish_original = _bf_orig_get_charges
get_charges = _bf_friction_get_charges

def get_charges_charge_dispute(db_path='state.db', **kwargs):
    '''<p>Retrieve a dispute for a specified charge.</p> (GET /v1/charges/{charge}/dispute)'''
    _missing = [p for p in ['charge'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('charge') is not None:
            _where.append('"charge" = ?')
            _args.append(str(kwargs['charge']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "disputes"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        return {'items': _rows, 'count': len(_rows)}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_charges_charge_dispute = get_charges_charge_dispute
def _bf_friction_get_charges_charge_dispute(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_charges_charge_dispute(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_charges_charge_dispute|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_charges_charge_dispute(*_bf_args, **_bf_kwargs)
_bf_friction_get_charges_charge_dispute.blobfish_original = _bf_orig_get_charges_charge_dispute
get_charges_charge_dispute = _bf_friction_get_charges_charge_dispute

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

def get_invoice_rendering_templates(db_path='state.db', **kwargs):
    '''List all invoice rendering templates (GET /v1/invoice_rendering_templates)'''
    if kwargs.get('status') is not None and kwargs.get('status') not in ['active', 'archived']:
        return {'error': 'invalid value for status: %r. Accepted: %s' % (kwargs.get('status'), ', '.join(['active', 'archived'])), 'status': 422, 'parameter': 'status', 'accepted': ['active', 'archived']}
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
        _q = 'SELECT * FROM "invoice_rendering_templates"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        return {'items': _rows, 'count': len(_rows)}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_invoice_rendering_templates = get_invoice_rendering_templates
def _bf_friction_get_invoice_rendering_templates(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_invoice_rendering_templates(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_invoice_rendering_templates|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_invoice_rendering_templates(*_bf_args, **_bf_kwargs)
_bf_friction_get_invoice_rendering_templates.blobfish_original = _bf_orig_get_invoice_rendering_templates
get_invoice_rendering_templates = _bf_friction_get_invoice_rendering_templates

def get_payment_intents_intent_amount_details_line_items(db_path='state.db', **kwargs):
    '''List all PaymentIntent LineItems (GET /v1/payment_intents/{intent}/amount_details_line_items)'''
    _missing = [p for p in ['intent'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "amount_details_line_items"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        return {'items': _rows, 'count': len(_rows)}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_payment_intents_intent_amount_details_line_items = get_payment_intents_intent_amount_details_line_items
def _bf_friction_get_payment_intents_intent_amount_details_line_items(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_payment_intents_intent_amount_details_line_items(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_payment_intents_intent_amount_details_line_items|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_payment_intents_intent_amount_details_line_items(*_bf_args, **_bf_kwargs)
_bf_friction_get_payment_intents_intent_amount_details_line_items.blobfish_original = _bf_orig_get_payment_intents_intent_amount_details_line_items
get_payment_intents_intent_amount_details_line_items = _bf_friction_get_payment_intents_intent_amount_details_line_items

def post_charges(db_path='state.db', **kwargs):
    '''<p>This method is no longer recommended—use the <a href="/docs/api/payment_intents">Payment Intents API</a> to initiate a new payment inste… (POST /v1/charges)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _n = cur.execute('SELECT COALESCE(MAX(rowid), 0) + 100 FROM "charges"').fetchone()[0] + 1
        _base = datetime.datetime(2026, 1, 5, 9, 0, 0)
        _ts = (_base + datetime.timedelta(minutes=_n)).strftime('%Y-%m-%dT%H:%M:%SZ')
        _cols = ['"id"']
        _vals = ['ch_' + str(_n).zfill(14) + '']
        if kwargs.get('amount') is not None:
            _cols.append('"amount"')
            _vals.append(int(kwargs['amount']))
        if kwargs.get('application_fee') is not None:
            _cols.append('"application_fee"')
            _vals.append(int(kwargs['application_fee']))
        if kwargs.get('application_fee_amount') is not None:
            _cols.append('"application_fee_amount"')
            _vals.append(int(kwargs['application_fee_amount']))
        if kwargs.get('currency') is not None:
            _cols.append('"currency"')
            _vals.append(str(kwargs['currency']))
        if kwargs.get('customer') is not None:
            _cols.append('"customer"')
            _vals.append(str(kwargs['customer']))
        if kwargs.get('description') is not None:
            _cols.append('"description"')
            _vals.append(str(kwargs['description']))
        if kwargs.get('metadata') is not None:
            _cols.append('"metadata"')
            _vals.append(str(kwargs['metadata']))
        if kwargs.get('on_behalf_of') is not None:
            _cols.append('"on_behalf_of"')
            _vals.append(str(kwargs['on_behalf_of']))
        if kwargs.get('radar_options') is not None:
            _cols.append('"radar_options"')
            _vals.append(json.dumps(kwargs['radar_options']) if not isinstance(kwargs['radar_options'], str) else kwargs['radar_options'])
        if kwargs.get('receipt_email') is not None:
            _cols.append('"receipt_email"')
            _vals.append(str(kwargs['receipt_email']))
        if kwargs.get('shipping') is not None:
            _cols.append('"shipping"')
            _vals.append(json.dumps(kwargs['shipping']) if not isinstance(kwargs['shipping'], str) else kwargs['shipping'])
        if kwargs.get('statement_descriptor') is not None:
            _cols.append('"statement_descriptor"')
            _vals.append(str(kwargs['statement_descriptor']))
        if kwargs.get('statement_descriptor_suffix') is not None:
            _cols.append('"statement_descriptor_suffix"')
            _vals.append(str(kwargs['statement_descriptor_suffix']))
        if kwargs.get('transfer_data') is not None:
            _cols.append('"transfer_data"')
            _vals.append(json.dumps(kwargs['transfer_data']) if not isinstance(kwargs['transfer_data'], str) else kwargs['transfer_data'])
        if kwargs.get('transfer_group') is not None:
            _cols.append('"transfer_group"')
            _vals.append(str(kwargs['transfer_group']))
        if '"status"' not in _cols:
            _cols.append('"status"')
            _vals.append('open')
        _sql = 'INSERT INTO "charges" (' + ', '.join(_cols) + ') VALUES (' + ', '.join(['?'] * len(_vals)) + ')'
        try:
            cur.execute(_sql, _vals)
        except sqlite3.IntegrityError:
            conn.rollback()
            return {'error': 'conflict: duplicate key', 'status': 409}
        conn.commit()
        _row = cur.execute('SELECT * FROM "charges" WHERE "id" = ?', [_vals[0]]).fetchone()
        _out = dict(_row)
        for _jc in ['billing_details', 'metadata', 'presentment_details', 'radar_options', 'refunds']:
            if isinstance(_out.get(_jc), str) and _out[_jc][:1] in ('[', '{'):
                try:
                    _out[_jc] = json.loads(_out[_jc])
                except Exception:
                    pass
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_charges = post_charges
def _bf_friction_post_charges(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_charges(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_charges|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_charges(*_bf_args, **_bf_kwargs)
_bf_friction_post_charges.blobfish_original = _bf_orig_post_charges
post_charges = _bf_friction_post_charges

def post_charges_charge_dispute_close(db_path='state.db', **kwargs):
    '''PostChargesChargeDisputeClose (POST /v1/charges/{charge}/dispute/close)'''
    _missing = [p for p in ['charge'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _n = cur.execute('SELECT COALESCE(MAX(rowid), 0) + 100 FROM "disputes"').fetchone()[0] + 1
        _base = datetime.datetime(2026, 1, 5, 9, 0, 0)
        _ts = (_base + datetime.timedelta(minutes=_n)).strftime('%Y-%m-%dT%H:%M:%SZ')
        _cols = ['"id"']
        _vals = ['dp_' + str(_n).zfill(14) + '']
        if kwargs.get('charge') is not None:
            _cols.append('"charge"')
            _vals.append(str(kwargs['charge']))
        if '"status"' not in _cols:
            _cols.append('"status"')
            _vals.append('open')
        _sql = 'INSERT INTO "disputes" (' + ', '.join(_cols) + ') VALUES (' + ', '.join(['?'] * len(_vals)) + ')'
        try:
            cur.execute(_sql, _vals)
        except sqlite3.IntegrityError:
            conn.rollback()
            return {'error': 'conflict: duplicate key', 'status': 409}
        conn.commit()
        _row = cur.execute('SELECT * FROM "disputes" WHERE "id" = ?', [_vals[0]]).fetchone()
        _out = dict(_row)
        for _jc in ['balance_transactions', 'enhanced_eligibility_types', 'evidence', 'evidence_details', 'metadata', 'payment_method_details']:
            if isinstance(_out.get(_jc), str) and _out[_jc][:1] in ('[', '{'):
                try:
                    _out[_jc] = json.loads(_out[_jc])
                except Exception:
                    pass
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_charges_charge_dispute_close = post_charges_charge_dispute_close
def _bf_friction_post_charges_charge_dispute_close(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_charges_charge_dispute_close(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_charges_charge_dispute_close|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_charges_charge_dispute_close(*_bf_args, **_bf_kwargs)
_bf_friction_post_charges_charge_dispute_close.blobfish_original = _bf_orig_post_charges_charge_dispute_close
post_charges_charge_dispute_close = _bf_friction_post_charges_charge_dispute_close

def get_customers(db_path='state.db', **kwargs):
    '''Returns a list of your customers; the customers are returned sorted by creation date, with the most recent customers appearing first. (GET /v1/customers)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('email') is not None:
            _where.append('"email" = ?')
            _args.append(str(kwargs['email']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "customers"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'object': 'list', 'url': '/v1/customers', 'has_more': False, 'data': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_customers = get_customers
def _bf_friction_get_customers(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_customers(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_customers|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_customers(*_bf_args, **_bf_kwargs)
_bf_friction_get_customers.blobfish_original = _bf_orig_get_customers
get_customers = _bf_friction_get_customers

def get_customers_customer(db_path='state.db', **kwargs):
    '''Retrieves a Customer object. (GET /v1/customers/{customer})'''
    _missing = [p for p in ['customer'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "customers" WHERE "id" = ?', [str(kwargs['customer'])]).fetchone()
        if _row is None:
            _r = {'error': 'customer not found', 'status': 404}
            return {'error': {'type': 'invalid_request_error', 'code': 'resource_missing', 'message': str(_r.get('error', ''))}}
        _r = dict(_row)
        _r['object'] = 'customer'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_customers_customer = get_customers_customer
def _bf_friction_get_customers_customer(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_customers_customer(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_customers_customer|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_customers_customer(*_bf_args, **_bf_kwargs)
_bf_friction_get_customers_customer.blobfish_original = _bf_orig_get_customers_customer
get_customers_customer = _bf_friction_get_customers_customer

def post_customers(db_path='state.db', **kwargs):
    '''Creates a new customer object. (POST /v1/customers)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "customers"').fetchone()[0] + 1
        _id = 'cus_' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "customers" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'cus_' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('name') is not None:
            _cols.append('name')
            _v = kwargs['name']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('email') is not None:
            _cols.append('email')
            _v = kwargs['email']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('balance') is not None:
            _cols.append('balance')
            _v = kwargs['balance']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'status' not in _cols:
            _cols.append('status')
            _vals.append('active')
        if 'currency' not in _cols:
            _cols.append('currency')
            _vals.append('usd')
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "customers" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "customers" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['object'] = 'customer'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_customers = post_customers
def _bf_friction_post_customers(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_customers(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_customers|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_customers(*_bf_args, **_bf_kwargs)
_bf_friction_post_customers.blobfish_original = _bf_orig_post_customers
post_customers = _bf_friction_post_customers

def post_customers_customer(db_path='state.db', **kwargs):
    '''Updates the specified customer by setting the values of the parameters passed; any parameters not provided will be left unchanged. (POST /v1/customers/{customer})'''
    _missing = [p for p in ['customer'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "customers" WHERE "id" = ?', [str(kwargs['customer'])]).fetchone()
        if _row is None:
            _r = {'error': 'customer not found', 'status': 404}
            return {'error': {'type': 'invalid_request_error', 'code': 'resource_missing', 'message': str(_r.get('error', ''))}}
        _sets, _args = [], []
        if kwargs.get('name') is not None:
            _sets.append('"name" = ?')
            _v = kwargs['name']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('email') is not None:
            _sets.append('"email" = ?')
            _v = kwargs['email']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('balance') is not None:
            _sets.append('"balance" = ?')
            _v = kwargs['balance']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "customers" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['customer'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "customers" WHERE "id" = ?', [str(kwargs['customer'])]).fetchone()
        _r = dict(_row)
        _r['object'] = 'customer'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_customers_customer = post_customers_customer
def _bf_friction_post_customers_customer(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_customers_customer(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_customers_customer|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_customers_customer(*_bf_args, **_bf_kwargs)
_bf_friction_post_customers_customer.blobfish_original = _bf_orig_post_customers_customer
post_customers_customer = _bf_friction_post_customers_customer

def get_products(db_path='state.db', **kwargs):
    '''Returns a list of your products; the products are returned sorted by creation date, with the most recently created products appearing first. (GET /v1/products)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('active') is not None:
            _where.append('"active" = ?')
            _args.append(str(kwargs['active']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "products"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'object': 'list', 'url': '/v1/products', 'has_more': False, 'data': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_products = get_products
def _bf_friction_get_products(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_products(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_products|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_products(*_bf_args, **_bf_kwargs)
_bf_friction_get_products.blobfish_original = _bf_orig_get_products
get_products = _bf_friction_get_products

def post_products(db_path='state.db', **kwargs):
    '''Creates a new product object. (POST /v1/products)'''
    _missing = [p for p in ['name'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "products"').fetchone()[0] + 1
        _id = 'prod_' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "products" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'prod_' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('name') is not None:
            _cols.append('name')
            _v = kwargs['name']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('description') is not None:
            _cols.append('description')
            _v = kwargs['description']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('active') is not None:
            _cols.append('active')
            _v = kwargs['active']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('url') is not None:
            _cols.append('url')
            _v = kwargs['url']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('metadata') is not None:
            _cols.append('metadata')
            _v = kwargs['metadata']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'object' not in _cols:
            _cols.append('object')
            _vals.append('product')
        if 'type' not in _cols:
            _cols.append('type')
            _vals.append('service')
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "products" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "products" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['object'] = 'product'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_products = post_products
def _bf_friction_post_products(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_products(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_products|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_products(*_bf_args, **_bf_kwargs)
_bf_friction_post_products.blobfish_original = _bf_orig_post_products
post_products = _bf_friction_post_products

def get_prices(db_path='state.db', **kwargs):
    '''Returns a list of your active prices. (GET /v1/prices)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('active') is not None:
            _where.append('"active" = ?')
            _args.append(str(kwargs['active']))
        if kwargs.get('currency') is not None:
            _where.append('"currency" = ?')
            _args.append(str(kwargs['currency']))
        if kwargs.get('product') is not None:
            _where.append('"product" = ?')
            _args.append(str(kwargs['product']))
        if kwargs.get('type') is not None:
            _where.append('"type" = ?')
            _args.append(str(kwargs['type']))
        if kwargs.get('lookup_key') is not None:
            _where.append('"lookup_key" = ?')
            _args.append(str(kwargs['lookup_key']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "prices"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'object': 'list', 'url': '/v1/prices', 'has_more': False, 'data': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_prices = get_prices
def _bf_friction_get_prices(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_prices(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_prices|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_prices(*_bf_args, **_bf_kwargs)
_bf_friction_get_prices.blobfish_original = _bf_orig_get_prices
get_prices = _bf_friction_get_prices

def post_prices(db_path='state.db', **kwargs):
    '''Creates a new price for an existing product; the price can be recurring or one-time. (POST /v1/prices)'''
    _missing = [p for p in ['currency', 'product', 'unit_amount'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "prices"').fetchone()[0] + 1
        _id = 'price_' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "prices" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'price_' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('currency') is not None:
            _cols.append('currency')
            _v = kwargs['currency']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('product') is not None:
            _cols.append('product')
            _v = kwargs['product']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('unit_amount') is not None:
            _cols.append('unit_amount')
            _v = kwargs['unit_amount']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('nickname') is not None:
            _cols.append('nickname')
            _v = kwargs['nickname']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('lookup_key') is not None:
            _cols.append('lookup_key')
            _v = kwargs['lookup_key']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('recurring_interval') is not None:
            _cols.append('recurring_interval')
            _v = kwargs['recurring_interval']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('type') is not None:
            _cols.append('type')
            _v = kwargs['type']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('metadata') is not None:
            _cols.append('metadata')
            _v = kwargs['metadata']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'object' not in _cols:
            _cols.append('object')
            _vals.append('price')
        if 'active' not in _cols:
            _cols.append('active')
            _vals.append(1)
        if 'billing_scheme' not in _cols:
            _cols.append('billing_scheme')
            _vals.append('per_unit')
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "prices" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "prices" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['object'] = 'price'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_prices = post_prices
def _bf_friction_post_prices(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_prices(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_prices|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_prices(*_bf_args, **_bf_kwargs)
_bf_friction_post_prices.blobfish_original = _bf_orig_post_prices
post_prices = _bf_friction_post_prices

def get_subscriptions(db_path='state.db', **kwargs):
    '''By default, returns a list of subscriptions that have not been canceled. (GET /v1/subscriptions)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('customer') is not None:
            _where.append('"customer" = ?')
            _args.append(str(kwargs['customer']))
        if kwargs.get('price') is not None:
            _where.append('"price" = ?')
            _args.append(str(kwargs['price']))
        if kwargs.get('status') is not None:
            _where.append('"status" = ?')
            _args.append(str(kwargs['status']))
        if kwargs.get('collection_method') is not None:
            _where.append('"collection_method" = ?')
            _args.append(str(kwargs['collection_method']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "subscriptions"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'object': 'list', 'url': '/v1/subscriptions', 'has_more': False, 'data': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_subscriptions = get_subscriptions
def _bf_friction_get_subscriptions(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_subscriptions(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_subscriptions|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_subscriptions(*_bf_args, **_bf_kwargs)
_bf_friction_get_subscriptions.blobfish_original = _bf_orig_get_subscriptions
get_subscriptions = _bf_friction_get_subscriptions

def get_subscriptions_subscription(db_path='state.db', **kwargs):
    '''Retrieves the subscription with the given ID. (GET /v1/subscriptions/{subscription})'''
    _missing = [p for p in ['subscription'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "subscriptions" WHERE "id" = ?', [str(kwargs['subscription'])]).fetchone()
        if _row is None:
            _r = {'error': 'subscription not found', 'status': 404}
            return {'error': {'type': 'invalid_request_error', 'code': 'resource_missing', 'message': str(_r.get('error', ''))}}
        _r = dict(_row)
        _r['object'] = 'subscription'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_subscriptions_subscription = get_subscriptions_subscription
def _bf_friction_get_subscriptions_subscription(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_subscriptions_subscription(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_subscriptions_subscription|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_subscriptions_subscription(*_bf_args, **_bf_kwargs)
_bf_friction_get_subscriptions_subscription.blobfish_original = _bf_orig_get_subscriptions_subscription
get_subscriptions_subscription = _bf_friction_get_subscriptions_subscription

def post_subscriptions(db_path='state.db', **kwargs):
    '''Creates a new subscription on an existing customer. (POST /v1/subscriptions)'''
    _missing = [p for p in ['customer', 'price'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "subscriptions"').fetchone()[0] + 1
        _id = 'sub_' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "subscriptions" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'sub_' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('customer') is not None:
            _cols.append('customer')
            _v = kwargs['customer']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('price') is not None:
            _cols.append('price')
            _v = kwargs['price']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('quantity') is not None:
            _cols.append('quantity')
            _v = kwargs['quantity']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('currency') is not None:
            _cols.append('currency')
            _v = kwargs['currency']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('collection_method') is not None:
            _cols.append('collection_method')
            _v = kwargs['collection_method']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('default_payment_method') is not None:
            _cols.append('default_payment_method')
            _v = kwargs['default_payment_method']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('metadata') is not None:
            _cols.append('metadata')
            _v = kwargs['metadata']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'object' not in _cols:
            _cols.append('object')
            _vals.append('subscription')
        if 'status' not in _cols:
            _cols.append('status')
            _vals.append('active')
        if 'cancel_at_period_end' not in _cols:
            _cols.append('cancel_at_period_end')
            _vals.append(0)
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "subscriptions" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "subscriptions" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['object'] = 'subscription'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_subscriptions = post_subscriptions
def _bf_friction_post_subscriptions(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_subscriptions(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_subscriptions|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_subscriptions(*_bf_args, **_bf_kwargs)
_bf_friction_post_subscriptions.blobfish_original = _bf_orig_post_subscriptions
post_subscriptions = _bf_friction_post_subscriptions

def post_subscriptions_subscription(db_path='state.db', **kwargs):
    '''Updates an existing subscription to match the specified parameters; for example, set cancel_at_period_end to schedule a cancellation at the end of the current billing period. (POST /v1/subscriptions/{subscription})'''
    _missing = [p for p in ['subscription'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "subscriptions" WHERE "id" = ?', [str(kwargs['subscription'])]).fetchone()
        if _row is None:
            _r = {'error': 'subscription not found', 'status': 404}
            return {'error': {'type': 'invalid_request_error', 'code': 'resource_missing', 'message': str(_r.get('error', ''))}}
        _sets, _args = [], []
        if kwargs.get('cancel_at_period_end') is not None:
            _sets.append('"cancel_at_period_end" = ?')
            _v = kwargs['cancel_at_period_end']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('price') is not None:
            _sets.append('"price" = ?')
            _v = kwargs['price']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('quantity') is not None:
            _sets.append('"quantity" = ?')
            _v = kwargs['quantity']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('collection_method') is not None:
            _sets.append('"collection_method" = ?')
            _v = kwargs['collection_method']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('default_payment_method') is not None:
            _sets.append('"default_payment_method" = ?')
            _v = kwargs['default_payment_method']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('metadata') is not None:
            _sets.append('"metadata" = ?')
            _v = kwargs['metadata']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "subscriptions" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['subscription'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "subscriptions" WHERE "id" = ?', [str(kwargs['subscription'])]).fetchone()
        _r = dict(_row)
        _r['object'] = 'subscription'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_subscriptions_subscription = post_subscriptions_subscription
def _bf_friction_post_subscriptions_subscription(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_subscriptions_subscription(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_subscriptions_subscription|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_subscriptions_subscription(*_bf_args, **_bf_kwargs)
_bf_friction_post_subscriptions_subscription.blobfish_original = _bf_orig_post_subscriptions_subscription
post_subscriptions_subscription = _bf_friction_post_subscriptions_subscription

def delete_subscriptions_subscription(db_path='state.db', **kwargs):
    import sqlite3, datetime
    subscription = kwargs.get('subscription')
    if not subscription:
        return {"error": {"type": "invalid_request_error", "message": "Missing required param: subscription."}}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM subscriptions WHERE id = ?", (subscription,)).fetchone()
    if row is None:
        conn.close()
        return {"error": {"type": "invalid_request_error", "code": "resource_missing", "message": "No such subscription: '%s'" % subscription}}
    if row["status"] == "canceled":
        conn.close()
        return {"error": {"type": "invalid_request_error", "message": "Subscription %s is already canceled; a canceled subscription can no longer be canceled." % subscription}}
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    cur.execute("UPDATE subscriptions SET status = 'canceled', canceled_at = ?, cancel_at_period_end = 0 WHERE id = ?", (now, subscription))
    conn.commit()
    updated = cur.execute("SELECT * FROM subscriptions WHERE id = ?", (subscription,)).fetchone()
    conn.close()
    return dict(updated)

_env_orig_delete_subscriptions_subscription = delete_subscriptions_subscription
def _env_delete_subscriptions_subscription(db_path='state.db', **kwargs):
    _r = _env_orig_delete_subscriptions_subscription(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'object': 'list', 'url': '/v1/subscriptions', 'has_more': False, 'data': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'type': 'invalid_request_error', 'code': 'resource_missing', 'message': str(_r.get('error', ''))}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    return _r
delete_subscriptions_subscription = _env_delete_subscriptions_subscription

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_delete_subscriptions_subscription = delete_subscriptions_subscription
def _bf_friction_delete_subscriptions_subscription(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_delete_subscriptions_subscription(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "delete_subscriptions_subscription|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_delete_subscriptions_subscription(*_bf_args, **_bf_kwargs)
_bf_friction_delete_subscriptions_subscription.blobfish_original = _bf_orig_delete_subscriptions_subscription
delete_subscriptions_subscription = _bf_friction_delete_subscriptions_subscription

def get_payment_intents(db_path='state.db', **kwargs):
    '''Returns a list of PaymentIntents. (GET /v1/payment_intents)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('customer') is not None:
            _where.append('"customer" = ?')
            _args.append(str(kwargs['customer']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "payment_intents"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'object': 'list', 'url': '/v1/payment_intents', 'has_more': False, 'data': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_payment_intents = get_payment_intents
def _bf_friction_get_payment_intents(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_payment_intents(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_payment_intents|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_payment_intents(*_bf_args, **_bf_kwargs)
_bf_friction_get_payment_intents.blobfish_original = _bf_orig_get_payment_intents
get_payment_intents = _bf_friction_get_payment_intents

def post_payment_intents(db_path='state.db', **kwargs):
    '''Creates a PaymentIntent object. (POST /v1/payment_intents)'''
    _missing = [p for p in ['amount', 'currency'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "payment_intents"').fetchone()[0] + 1
        _id = 'pi_' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "payment_intents" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'pi_' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('amount') is not None:
            _cols.append('amount')
            _v = kwargs['amount']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('currency') is not None:
            _cols.append('currency')
            _v = kwargs['currency']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('customer') is not None:
            _cols.append('customer')
            _v = kwargs['customer']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('description') is not None:
            _cols.append('description')
            _v = kwargs['description']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('payment_method') is not None:
            _cols.append('payment_method')
            _v = kwargs['payment_method']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('receipt_email') is not None:
            _cols.append('receipt_email')
            _v = kwargs['receipt_email']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('capture_method') is not None:
            _cols.append('capture_method')
            _v = kwargs['capture_method']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('statement_descriptor') is not None:
            _cols.append('statement_descriptor')
            _v = kwargs['statement_descriptor']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('metadata') is not None:
            _cols.append('metadata')
            _v = kwargs['metadata']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'object' not in _cols:
            _cols.append('object')
            _vals.append('payment_intent')
        if 'status' not in _cols:
            _cols.append('status')
            _vals.append('requires_payment_method')
        if 'amount_capturable' not in _cols:
            _cols.append('amount_capturable')
            _vals.append(0)
        if 'amount_received' not in _cols:
            _cols.append('amount_received')
            _vals.append(0)
        if 'confirmation_method' not in _cols:
            _cols.append('confirmation_method')
            _vals.append('automatic')
        if 'livemode' not in _cols:
            _cols.append('livemode')
            _vals.append(0)
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "payment_intents" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "payment_intents" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['object'] = 'payment_intent'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_payment_intents = post_payment_intents
def _bf_friction_post_payment_intents(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_payment_intents(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_payment_intents|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_payment_intents(*_bf_args, **_bf_kwargs)
_bf_friction_post_payment_intents.blobfish_original = _bf_orig_post_payment_intents
post_payment_intents = _bf_friction_post_payment_intents

def post_payment_intents_intent_confirm(db_path='state.db', **kwargs):
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
    if row["status"] not in ("requires_payment_method", "requires_confirmation"):
        conn.close()
        return {"error": {"type": "invalid_request_error", "message": "You cannot confirm this PaymentIntent because it has a status of %s; only a PaymentIntent with one of the following statuses may be confirmed: requires_payment_method, requires_confirmation." % row["status"]}}
    payment_method = kwargs.get('payment_method') or row["payment_method"]
    if not payment_method:
        conn.close()
        return {"error": {"type": "invalid_request_error", "message": "You cannot confirm this PaymentIntent because it's missing a payment method. Provide a payment_method or attach one to the PaymentIntent first."}}
    amount = row["amount"] or 0
    if row["capture_method"] == "manual":
        cur.execute("UPDATE payment_intents SET status = 'requires_capture', payment_method = ?, amount_capturable = ?, amount_received = 0 WHERE id = ?", (payment_method, amount, intent))
    else:
        cur.execute("UPDATE payment_intents SET status = 'succeeded', payment_method = ?, amount_capturable = 0, amount_received = ? WHERE id = ?", (payment_method, amount, intent))
    conn.commit()
    updated = cur.execute("SELECT * FROM payment_intents WHERE id = ?", (intent,)).fetchone()
    conn.close()
    return dict(updated)

_env_orig_post_payment_intents_intent_confirm = post_payment_intents_intent_confirm
def _env_post_payment_intents_intent_confirm(db_path='state.db', **kwargs):
    _r = _env_orig_post_payment_intents_intent_confirm(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'object': 'list', 'url': '/v1/payment_intents', 'has_more': False, 'data': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'type': 'invalid_request_error', 'code': 'resource_missing', 'message': str(_r.get('error', ''))}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    return _r
post_payment_intents_intent_confirm = _env_post_payment_intents_intent_confirm

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_payment_intents_intent_confirm = post_payment_intents_intent_confirm
def _bf_friction_post_payment_intents_intent_confirm(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_payment_intents_intent_confirm(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_payment_intents_intent_confirm|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_payment_intents_intent_confirm(*_bf_args, **_bf_kwargs)
_bf_friction_post_payment_intents_intent_confirm.blobfish_original = _bf_orig_post_payment_intents_intent_confirm
post_payment_intents_intent_confirm = _bf_friction_post_payment_intents_intent_confirm

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

def get_refunds(db_path='state.db', **kwargs):
    '''Returns a list of all refunds you created; refunds are returned in sorted order, with the most recent refunds appearing first. (GET /v1/refunds)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('charge') is not None:
            _where.append('"charge" = ?')
            _args.append(str(kwargs['charge']))
        if kwargs.get('payment_intent') is not None:
            _where.append('"payment_intent" = ?')
            _args.append(str(kwargs['payment_intent']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "refunds"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'object': 'list', 'url': '/v1/refunds', 'has_more': False, 'data': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_refunds = get_refunds
def _bf_friction_get_refunds(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_refunds(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_refunds|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_refunds(*_bf_args, **_bf_kwargs)
_bf_friction_get_refunds.blobfish_original = _bf_orig_get_refunds
get_refunds = _bf_friction_get_refunds

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

def get_payment_links(db_path='state.db', **kwargs):
    '''Returns a list of your payment links. (GET /v1/payment_links)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('active') is not None:
            _where.append('"active" = ?')
            _args.append(str(kwargs['active']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "payment_links"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'object': 'list', 'url': '/v1/payment_links', 'has_more': False, 'data': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_payment_links = get_payment_links
def _bf_friction_get_payment_links(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_payment_links(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_payment_links|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_payment_links(*_bf_args, **_bf_kwargs)
_bf_friction_get_payment_links.blobfish_original = _bf_orig_get_payment_links
get_payment_links = _bf_friction_get_payment_links

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

def post_invoices(db_path='state.db', **kwargs):
    '''This endpoint creates a draft invoice for a given customer; the draft invoice remains a draft until you finalize it. (POST /v1/invoices)'''
    _missing = [p for p in ['customer'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "invoices"').fetchone()[0] + 1
        _id = 'in_' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "invoices" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'in_' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('customer') is not None:
            _cols.append('customer')
            _v = kwargs['customer']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('currency') is not None:
            _cols.append('currency')
            _v = kwargs['currency']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('collection_method') is not None:
            _cols.append('collection_method')
            _v = kwargs['collection_method']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('auto_advance') is not None:
            _cols.append('auto_advance')
            _v = kwargs['auto_advance']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'object' not in _cols:
            _cols.append('object')
            _vals.append('invoice')
        if 'status' not in _cols:
            _cols.append('status')
            _vals.append('draft')
        if 'billing_reason' not in _cols:
            _cols.append('billing_reason')
            _vals.append('manual')
        if 'amount_due' not in _cols:
            _cols.append('amount_due')
            _vals.append(0)
        if 'amount_paid' not in _cols:
            _cols.append('amount_paid')
            _vals.append(0)
        if 'amount_remaining' not in _cols:
            _cols.append('amount_remaining')
            _vals.append(0)
        if 'subtotal' not in _cols:
            _cols.append('subtotal')
            _vals.append(0)
        if 'total' not in _cols:
            _cols.append('total')
            _vals.append(0)
        if 'attempted' not in _cols:
            _cols.append('attempted')
            _vals.append(0)
        if 'attempt_count' not in _cols:
            _cols.append('attempt_count')
            _vals.append(0)
        if 'livemode' not in _cols:
            _cols.append('livemode')
            _vals.append(0)
        if 'created' not in _cols:
            _cols.append('created')
            _vals.append(_now)
        cur.execute('INSERT INTO "invoices" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "invoices" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['object'] = 'invoice'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_invoices = post_invoices
def _bf_friction_post_invoices(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_invoices(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_invoices|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_invoices(*_bf_args, **_bf_kwargs)
_bf_friction_post_invoices.blobfish_original = _bf_orig_post_invoices
post_invoices = _bf_friction_post_invoices

def post_invoices_invoice_finalize(db_path='state.db', **kwargs):
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
    if row["status"] != "draft":
        conn.close()
        return {"error": {"type": "invalid_request_error", "message": "This invoice can't be finalized because it has a status of %s; only draft invoices can be finalized." % row["status"]}}
    cur.execute("UPDATE invoiceitems SET invoice = ? WHERE customer = ? AND (invoice IS NULL OR invoice = '')", (invoice, row["customer"]))
    total = cur.execute("SELECT COALESCE(SUM(COALESCE(amount, COALESCE(unit_amount, 0) * COALESCE(quantity, 1))), 0) FROM invoiceitems WHERE invoice = ?", (invoice,)).fetchone()[0]
    if total == 0:
        total = row["total"] or 0
    auto_advance = kwargs.get('auto_advance')
    if auto_advance is None:
        cur.execute("UPDATE invoices SET status = 'open', subtotal = ?, total = ?, amount_due = ?, amount_remaining = ? WHERE id = ?", (total, total, total, total, invoice))
    else:
        cur.execute("UPDATE invoices SET status = 'open', subtotal = ?, total = ?, amount_due = ?, amount_remaining = ?, auto_advance = ? WHERE id = ?", (total, total, total, total, 1 if auto_advance else 0, invoice))
    conn.commit()
    updated = cur.execute("SELECT * FROM invoices WHERE id = ?", (invoice,)).fetchone()
    conn.close()
    return dict(updated)

_env_orig_post_invoices_invoice_finalize = post_invoices_invoice_finalize
def _env_post_invoices_invoice_finalize(db_path='state.db', **kwargs):
    _r = _env_orig_post_invoices_invoice_finalize(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'object': 'list', 'url': '/v1/invoices', 'has_more': False, 'data': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'type': 'invalid_request_error', 'code': 'resource_missing', 'message': str(_r.get('error', ''))}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    return _r
post_invoices_invoice_finalize = _env_post_invoices_invoice_finalize

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_invoices_invoice_finalize = post_invoices_invoice_finalize
def _bf_friction_post_invoices_invoice_finalize(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_invoices_invoice_finalize(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_invoices_invoice_finalize|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_invoices_invoice_finalize(*_bf_args, **_bf_kwargs)
_bf_friction_post_invoices_invoice_finalize.blobfish_original = _bf_orig_post_invoices_invoice_finalize
post_invoices_invoice_finalize = _bf_friction_post_invoices_invoice_finalize

def post_invoices_invoice_void(db_path='state.db', **kwargs):
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
    if row["status"] not in ("open", "uncollectible"):
        conn.close()
        return {"error": {"type": "invalid_request_error", "message": "This invoice can't be voided because it has a status of %s; only open or uncollectible invoices can be voided." % row["status"]}}
    cur.execute("UPDATE invoices SET status = 'void', amount_remaining = 0, auto_advance = 0 WHERE id = ?", (invoice,))
    conn.commit()
    updated = cur.execute("SELECT * FROM invoices WHERE id = ?", (invoice,)).fetchone()
    conn.close()
    return dict(updated)

_env_orig_post_invoices_invoice_void = post_invoices_invoice_void
def _env_post_invoices_invoice_void(db_path='state.db', **kwargs):
    _r = _env_orig_post_invoices_invoice_void(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'object': 'list', 'url': '/v1/invoices', 'has_more': False, 'data': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'type': 'invalid_request_error', 'code': 'resource_missing', 'message': str(_r.get('error', ''))}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    return _r
post_invoices_invoice_void = _env_post_invoices_invoice_void

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_invoices_invoice_void = post_invoices_invoice_void
def _bf_friction_post_invoices_invoice_void(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_invoices_invoice_void(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_invoices_invoice_void|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_invoices_invoice_void(*_bf_args, **_bf_kwargs)
_bf_friction_post_invoices_invoice_void.blobfish_original = _bf_orig_post_invoices_invoice_void
post_invoices_invoice_void = _bf_friction_post_invoices_invoice_void

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

def post_invoiceitems(db_path='state.db', **kwargs):
    '''Creates an item to be added to a draft invoice (up to 250 items per invoice); if no invoice is specified, the item will be on the next invoice created for the customer specified. (POST /v1/invoiceitems)'''
    _missing = [p for p in ['customer'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "invoiceitems"').fetchone()[0] + 1
        _id = 'ii_' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "invoiceitems" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'ii_' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('customer') is not None:
            _cols.append('customer')
            _v = kwargs['customer']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('amount') is not None:
            _cols.append('amount')
            _v = kwargs['amount']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('currency') is not None:
            _cols.append('currency')
            _v = kwargs['currency']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('description') is not None:
            _cols.append('description')
            _v = kwargs['description']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('invoice') is not None:
            _cols.append('invoice')
            _v = kwargs['invoice']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('price') is not None:
            _cols.append('price')
            _v = kwargs['price']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('quantity') is not None:
            _cols.append('quantity')
            _v = kwargs['quantity']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('unit_amount') is not None:
            _cols.append('unit_amount')
            _v = kwargs['unit_amount']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('metadata') is not None:
            _cols.append('metadata')
            _v = kwargs['metadata']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'object' not in _cols:
            _cols.append('object')
            _vals.append('invoiceitem')
        if 'proration' not in _cols:
            _cols.append('proration')
            _vals.append(0)
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "invoiceitems" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "invoiceitems" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['object'] = 'invoiceitem'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_invoiceitems = post_invoiceitems
def _bf_friction_post_invoiceitems(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_invoiceitems(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_invoiceitems|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_invoiceitems(*_bf_args, **_bf_kwargs)
_bf_friction_post_invoiceitems.blobfish_original = _bf_orig_post_invoiceitems
post_invoiceitems = _bf_friction_post_invoiceitems

def get_coupons(db_path='state.db', **kwargs):
    '''Returns a list of your coupons. (GET /v1/coupons)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "coupons"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'object': 'list', 'url': '/v1/coupons', 'has_more': False, 'data': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_coupons = get_coupons
def _bf_friction_get_coupons(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_coupons(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_coupons|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_coupons(*_bf_args, **_bf_kwargs)
_bf_friction_get_coupons.blobfish_original = _bf_orig_get_coupons
get_coupons = _bf_friction_get_coupons

def post_coupons(db_path='state.db', **kwargs):
    '''You can create coupons easily via the coupon management page of the Stripe dashboard; coupon creation is also available with the API if you need to create coupons on the fly. (POST /v1/coupons)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "coupons"').fetchone()[0] + 1
        _id = 'coupon_' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "coupons" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'coupon_' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('duration') is not None:
            _cols.append('duration')
            _v = kwargs['duration']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('amount_off') is not None:
            _cols.append('amount_off')
            _v = kwargs['amount_off']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('percent_off') is not None:
            _cols.append('percent_off')
            _v = kwargs['percent_off']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('currency') is not None:
            _cols.append('currency')
            _v = kwargs['currency']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('duration_in_months') is not None:
            _cols.append('duration_in_months')
            _v = kwargs['duration_in_months']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('max_redemptions') is not None:
            _cols.append('max_redemptions')
            _v = kwargs['max_redemptions']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('name') is not None:
            _cols.append('name')
            _v = kwargs['name']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('metadata') is not None:
            _cols.append('metadata')
            _v = kwargs['metadata']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'object' not in _cols:
            _cols.append('object')
            _vals.append('coupon')
        if 'valid' not in _cols:
            _cols.append('valid')
            _vals.append(1)
        if 'times_redeemed' not in _cols:
            _cols.append('times_redeemed')
            _vals.append(0)
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "coupons" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "coupons" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['object'] = 'coupon'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_coupons = post_coupons
def _bf_friction_post_coupons(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_coupons(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_coupons|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_coupons(*_bf_args, **_bf_kwargs)
_bf_friction_post_coupons.blobfish_original = _bf_orig_post_coupons
post_coupons = _bf_friction_post_coupons

def get_balance(db_path='state.db', **kwargs):
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    available = {}
    pending = {}
    for row in cur.execute("SELECT currency, status, net FROM balance_transactions"):
        currency = (row["currency"] or "usd").lower()
        bucket = pending if row["status"] == "pending" else available
        bucket[currency] = bucket.get(currency, 0) + (row["net"] or 0)
    conn.close()
    return {
        "object": "balance",
        "livemode": False,
        "available": [{"amount": amount, "currency": currency, "source_types": {"card": amount}} for currency, amount in sorted(available.items())],
        "pending": [{"amount": amount, "currency": currency, "source_types": {"card": amount}} for currency, amount in sorted(pending.items())],
    }

_env_orig_get_balance = get_balance
def _env_get_balance(db_path='state.db', **kwargs):
    _r = _env_orig_get_balance(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'object': 'list', 'url': '/v1/balance_transactions', 'has_more': False, 'data': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'type': 'invalid_request_error', 'code': 'resource_missing', 'message': str(_r.get('error', ''))}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    return _r
get_balance = _env_get_balance

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_balance = get_balance
def _bf_friction_get_balance(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_balance(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_balance|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_balance(*_bf_args, **_bf_kwargs)
_bf_friction_get_balance.blobfish_original = _bf_orig_get_balance
get_balance = _bf_friction_get_balance

def get_events(db_path='state.db', **kwargs):
    '''List events, going back up to 30 days; each event data is rendered according to Stripe API version at its creation time. (GET /v1/events)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('type') is not None:
            _where.append('"type" = ?')
            _args.append(str(kwargs['type']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "stripe_events"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'object': 'list', 'url': '/v1/stripe_events', 'has_more': False, 'data': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_events = get_events
def _bf_friction_get_events(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_events(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_events|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_events(*_bf_args, **_bf_kwargs)
_bf_friction_get_events.blobfish_original = _bf_orig_get_events
get_events = _bf_friction_get_events

def get_disputes(db_path='state.db', **kwargs):
    '''Returns a list of your disputes. (GET /v1/disputes)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('charge') is not None:
            _where.append('"charge" = ?')
            _args.append(str(kwargs['charge']))
        if kwargs.get('payment_intent') is not None:
            _where.append('"payment_intent" = ?')
            _args.append(str(kwargs['payment_intent']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "disputes"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'object': 'list', 'url': '/v1/disputes', 'has_more': False, 'data': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_disputes = get_disputes
def _bf_friction_get_disputes(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_disputes(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_disputes|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_disputes(*_bf_args, **_bf_kwargs)
_bf_friction_get_disputes.blobfish_original = _bf_orig_get_disputes
get_disputes = _bf_friction_get_disputes

def product_update(db_path='state.db', **kwargs):
    '''Update a product (POST /v1/products/{id}).'''
    _missing = [p for p in ['product_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "products" WHERE "id" = ?', [str(kwargs['product_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'product not found', 'status': 404}
            return {'error': {'type': 'invalid_request_error', 'code': 'resource_missing', 'message': str(_r.get('error', ''))}}
        _sets, _args = [], []
        if kwargs.get('name') is not None:
            _sets.append('"name" = ?')
            _v = kwargs['name']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('description') is not None:
            _sets.append('"description" = ?')
            _v = kwargs['description']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('active') is not None:
            _sets.append('"active" = ?')
            _v = kwargs['active']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('default_price') is not None:
            _sets.append('"default_price" = ?')
            _v = kwargs['default_price']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('type') is not None:
            _sets.append('"type" = ?')
            _v = kwargs['type']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('url') is not None:
            _sets.append('"url" = ?')
            _v = kwargs['url']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('metadata') is not None:
            _sets.append('"metadata" = ?')
            _v = kwargs['metadata']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "products" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['product_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "products" WHERE "id" = ?', [str(kwargs['product_id'])]).fetchone()
        _r = dict(_row)
        _r['object'] = 'product'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_product_update = product_update
def _bf_friction_product_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_product_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "product_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_product_update(*_bf_args, **_bf_kwargs)
_bf_friction_product_update.blobfish_original = _bf_orig_product_update
product_update = _bf_friction_product_update

def product_delete(db_path='state.db', **kwargs):
    '''Delete a product (DELETE /v1/products/{id}).'''
    _missing = [p for p in ['product_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "products" WHERE "id" = ?', [str(kwargs['product_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'product not found', 'status': 404}
            return {'error': {'type': 'invalid_request_error', 'code': 'resource_missing', 'message': str(_r.get('error', ''))}}
        cur.execute('DELETE FROM "products" WHERE "id" = ?', [str(kwargs['product_id'])])
        conn.commit()
        _r = {'deleted': True, 'id': str(kwargs['product_id'])}
        return {'id': _r.get('id'), 'object': 'product', 'deleted': True}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_product_delete = product_delete
def _bf_friction_product_delete(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_product_delete(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "product_delete|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_product_delete(*_bf_args, **_bf_kwargs)
_bf_friction_product_delete.blobfish_original = _bf_orig_product_delete
product_delete = _bf_friction_product_delete

def products_search(db_path='state.db', **kwargs):
    '''Search products by name or description (GET /v1/products/search).'''
    _missing = [p for p in ['query'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _qv = '%' + str(kwargs['query']) + '%'
        _where, _args = ["(\"name\" LIKE ? OR \"description\" LIKE ?)"], [_qv] * 2
        if kwargs.get('active') is not None:
            _where.append('"active" = ?')
            _args.append(str(kwargs['active']))
        if kwargs.get('type') is not None:
            _where.append('"type" = ?')
            _args.append(str(kwargs['type']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "products" WHERE ' + ' AND '.join(_where) + ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'object': 'list', 'url': '/v1/products', 'has_more': False, 'data': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_products_search = products_search
def _bf_friction_products_search(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_products_search(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "products_search|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_products_search(*_bf_args, **_bf_kwargs)
_bf_friction_products_search.blobfish_original = _bf_orig_products_search
products_search = _bf_friction_products_search

def customer_update(db_path='state.db', **kwargs):
    '''Update a customer (POST /v1/customers/{id}).'''
    _missing = [p for p in ['customer_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "customers" WHERE "id" = ?', [str(kwargs['customer_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'customer not found', 'status': 404}
            return {'error': {'type': 'invalid_request_error', 'code': 'resource_missing', 'message': str(_r.get('error', ''))}}
        _sets, _args = [], []
        if kwargs.get('name') is not None:
            _sets.append('"name" = ?')
            _v = kwargs['name']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('email') is not None:
            _sets.append('"email" = ?')
            _v = kwargs['email']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('status') is not None:
            _sets.append('"status" = ?')
            _v = kwargs['status']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('currency') is not None:
            _sets.append('"currency" = ?')
            _v = kwargs['currency']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('balance') is not None:
            _sets.append('"balance" = ?')
            _v = kwargs['balance']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "customers" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['customer_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "customers" WHERE "id" = ?', [str(kwargs['customer_id'])]).fetchone()
        _r = dict(_row)
        _r['object'] = 'customer'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_customer_update = customer_update
def _bf_friction_customer_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_customer_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "customer_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_customer_update(*_bf_args, **_bf_kwargs)
_bf_friction_customer_update.blobfish_original = _bf_orig_customer_update
customer_update = _bf_friction_customer_update

def customer_delete(db_path='state.db', **kwargs):
    '''Delete a customer (DELETE /v1/customers/{id}).'''
    _missing = [p for p in ['customer_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "customers" WHERE "id" = ?', [str(kwargs['customer_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'customer not found', 'status': 404}
            return {'error': {'type': 'invalid_request_error', 'code': 'resource_missing', 'message': str(_r.get('error', ''))}}
        cur.execute('DELETE FROM "customers" WHERE "id" = ?', [str(kwargs['customer_id'])])
        conn.commit()
        _r = {'deleted': True, 'id': str(kwargs['customer_id'])}
        return {'id': _r.get('id'), 'object': 'customer', 'deleted': True}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_customer_delete = customer_delete
def _bf_friction_customer_delete(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_customer_delete(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "customer_delete|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_customer_delete(*_bf_args, **_bf_kwargs)
_bf_friction_customer_delete.blobfish_original = _bf_orig_customer_delete
customer_delete = _bf_friction_customer_delete

def customers_search(db_path='state.db', **kwargs):
    '''Search customers by name or email (GET /v1/customers/search).'''
    _missing = [p for p in ['query'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _qv = '%' + str(kwargs['query']) + '%'
        _where, _args = ["(\"name\" LIKE ? OR \"email\" LIKE ?)"], [_qv] * 2
        if kwargs.get('status') is not None:
            _where.append('"status" = ?')
            _args.append(str(kwargs['status']))
        if kwargs.get('currency') is not None:
            _where.append('"currency" = ?')
            _args.append(str(kwargs['currency']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "customers" WHERE ' + ' AND '.join(_where) + ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'object': 'list', 'url': '/v1/customers', 'has_more': False, 'data': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_customers_search = customers_search
def _bf_friction_customers_search(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_customers_search(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "customers_search|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_customers_search(*_bf_args, **_bf_kwargs)
_bf_friction_customers_search.blobfish_original = _bf_orig_customers_search
customers_search = _bf_friction_customers_search

def subscription_update(db_path='state.db', **kwargs):
    '''Update a subscription (POST /v1/subscriptions/{id}).'''
    _missing = [p for p in ['subscription_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "subscriptions" WHERE "id" = ?', [str(kwargs['subscription_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'subscription not found', 'status': 404}
            return {'error': {'type': 'invalid_request_error', 'code': 'resource_missing', 'message': str(_r.get('error', ''))}}
        _sets, _args = [], []
        if kwargs.get('status') is not None:
            _sets.append('"status" = ?')
            _v = kwargs['status']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('quantity') is not None:
            _sets.append('"quantity" = ?')
            _v = kwargs['quantity']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('price') is not None:
            _sets.append('"price" = ?')
            _v = kwargs['price']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('collection_method') is not None:
            _sets.append('"collection_method" = ?')
            _v = kwargs['collection_method']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('cancel_at_period_end') is not None:
            _sets.append('"cancel_at_period_end" = ?')
            _v = kwargs['cancel_at_period_end']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('current_period_end') is not None:
            _sets.append('"current_period_end" = ?')
            _v = kwargs['current_period_end']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "subscriptions" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['subscription_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "subscriptions" WHERE "id" = ?', [str(kwargs['subscription_id'])]).fetchone()
        _r = dict(_row)
        _r['object'] = 'subscription'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_subscription_update = subscription_update
def _bf_friction_subscription_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_subscription_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "subscription_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_subscription_update(*_bf_args, **_bf_kwargs)
_bf_friction_subscription_update.blobfish_original = _bf_orig_subscription_update
subscription_update = _bf_friction_subscription_update

