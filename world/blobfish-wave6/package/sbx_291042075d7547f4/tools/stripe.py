"""Executable STRIPE tool module

Inspect each function: SQLite helpers are local fixtures; network-backed functions call their declared endpoint.
Tools: get_charges, get_charges_charge_dispute, get_invoices, get_invoice_rendering_templates, get_payment_intents_intent_amount_details_line_items, post_charges, post_charges_charge_dispute_close
Tables: charges, disputes, invoices, invoice_rendering_templates, amount_details_line_items
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

