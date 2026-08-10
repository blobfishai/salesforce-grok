"""Executable PAGERDUTY tool module

Inspect each function: SQLite helpers are local fixtures; network-backed functions call their declared endpoint.
Tools: cases_list, get_billing_alerts_id, get_billing_alerts, case_create, post_billing_alerts
Tables: cases, billing_alerts, alerts
"""
import json, sqlite3
def cases_list(db_path='state.db', **kwargs):
    '''List cases with bounded lifecycle filtering. (GET /services/data/v1/cases)'''
    if kwargs.get('status') is not None and kwargs.get('status') not in ['new', 'working', 'waiting_customer', 'escalated', 'closed']:
        return {'error': 'invalid value for status: %r. Accepted: %s' % (kwargs.get('status'), ', '.join(['new', 'working', 'waiting_customer', 'escalated', 'closed'])), 'status': 422, 'parameter': 'status', 'accepted': ['new', 'working', 'waiting_customer', 'escalated', 'closed']}
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
        _q = 'SELECT * FROM "cases"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        return {'items': _rows, 'count': len(_rows)}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_cases_list = cases_list
def _bf_friction_cases_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_cases_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "cases_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_cases_list(*_bf_args, **_bf_kwargs)
_bf_friction_cases_list.blobfish_original = _bf_orig_cases_list
cases_list = _bf_friction_cases_list

def get_billing_alerts_id(db_path='state.db', **kwargs):
    '''Retrieve a billing alert (GET /v1/billing/alerts/{id})'''
    _missing = [p for p in ['id'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "billing_alerts" WHERE "id" = ?', [str(kwargs.get('id'))]).fetchone()
        if _row is None:
            return {'error': 'billing_alert not found', 'status': 404}
        _out = dict(_row)
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_billing_alerts_id = get_billing_alerts_id
def _bf_friction_get_billing_alerts_id(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_billing_alerts_id(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_billing_alerts_id|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_billing_alerts_id(*_bf_args, **_bf_kwargs)
_bf_friction_get_billing_alerts_id.blobfish_original = _bf_orig_get_billing_alerts_id
get_billing_alerts_id = _bf_friction_get_billing_alerts_id

def get_billing_alerts(db_path='state.db', **kwargs):
    '''List billing alerts (GET /v1/billing/alerts)'''
    if kwargs.get('alert_type') is not None and kwargs.get('alert_type') not in ['usage_threshold']:
        return {'error': 'invalid value for alert_type: %r. Accepted: %s' % (kwargs.get('alert_type'), ', '.join(['usage_threshold'])), 'status': 422, 'parameter': 'alert_type', 'accepted': ['usage_threshold']}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "alerts"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        return {'items': _rows, 'count': len(_rows)}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_billing_alerts = get_billing_alerts
def _bf_friction_get_billing_alerts(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_billing_alerts(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_billing_alerts|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_billing_alerts(*_bf_args, **_bf_kwargs)
_bf_friction_get_billing_alerts.blobfish_original = _bf_orig_get_billing_alerts
get_billing_alerts = _bf_friction_get_billing_alerts

def case_create(db_path='state.db', **kwargs):
    '''Create one tenant-scoped case. (POST /services/data/v1/cases)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _n = cur.execute('SELECT COALESCE(MAX(rowid), 0) + 100 FROM "cases"').fetchone()[0] + 1
        _base = datetime.datetime(2026, 1, 5, 9, 0, 0)
        _ts = (_base + datetime.timedelta(minutes=_n)).strftime('%Y-%m-%dT%H:%M:%SZ')
        _cols = ['"id"']
        _vals = ['case_%03d' % _n]
        if kwargs.get('account_id') is not None:
            _cols.append('"account_id"')
            _vals.append(str(kwargs['account_id']))
        if kwargs.get('contact_id') is not None:
            _cols.append('"contact_id"')
            _vals.append(str(kwargs['contact_id']))
        if kwargs.get('subject') is not None:
            _cols.append('"subject"')
            _vals.append(str(kwargs['subject']))
        if kwargs.get('status') is not None:
            _cols.append('"status"')
            _vals.append(str(kwargs['status']))
        if kwargs.get('priority') is not None:
            _cols.append('"priority"')
            _vals.append(str(kwargs['priority']))
        if kwargs.get('owner_id') is not None:
            _cols.append('"owner_id"')
            _vals.append(str(kwargs['owner_id']))
        if kwargs.get('description') is not None:
            _cols.append('"description"')
            _vals.append(str(kwargs['description']))
        _cols.append('"created_at"')
        _vals.append(_ts)
        if '"status"' not in _cols:
            _cols.append('"status"')
            _vals.append('open')
        _sql = 'INSERT INTO "cases" (' + ', '.join(_cols) + ') VALUES (' + ', '.join(['?'] * len(_vals)) + ')'
        try:
            cur.execute(_sql, _vals)
        except sqlite3.IntegrityError:
            conn.rollback()
            return {'error': 'conflict: duplicate key', 'status': 409}
        conn.commit()
        _row = cur.execute('SELECT * FROM "cases" WHERE "id" = ?', [_vals[0]]).fetchone()
        _out = dict(_row)
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_case_create = case_create
def _bf_friction_case_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_case_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "case_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_case_create(*_bf_args, **_bf_kwargs)
_bf_friction_case_create.blobfish_original = _bf_orig_case_create
case_create = _bf_friction_case_create

def post_billing_alerts(db_path='state.db', **kwargs):
    '''Create a billing alert (POST /v1/billing/alerts)'''
    _missing = [p for p in ['alert_type', 'title'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _n = cur.execute('SELECT COALESCE(MAX(rowid), 0) + 100 FROM "billing_alerts"').fetchone()[0] + 1
        _base = datetime.datetime(2026, 1, 5, 9, 0, 0)
        _ts = (_base + datetime.timedelta(minutes=_n)).strftime('%Y-%m-%dT%H:%M:%SZ')
        _cols = ['"id"']
        _vals = ['billing_alert_' + str(_n).zfill(14) + '']
        if kwargs.get('alert_type') is not None:
            _cols.append('"alert_type"')
            _vals.append(str(kwargs['alert_type']))
        if kwargs.get('title') is not None:
            _cols.append('"title"')
            _vals.append(str(kwargs['title']))
        if kwargs.get('usage_threshold') is not None:
            _cols.append('"usage_threshold"')
            _vals.append(json.dumps(kwargs['usage_threshold']) if not isinstance(kwargs['usage_threshold'], str) else kwargs['usage_threshold'])
        if '"status"' not in _cols:
            _cols.append('"status"')
            _vals.append('open')
        _sql = 'INSERT INTO "billing_alerts" (' + ', '.join(_cols) + ') VALUES (' + ', '.join(['?'] * len(_vals)) + ')'
        try:
            cur.execute(_sql, _vals)
        except sqlite3.IntegrityError:
            conn.rollback()
            return {'error': 'conflict: duplicate key', 'status': 409}
        conn.commit()
        _row = cur.execute('SELECT * FROM "billing_alerts" WHERE "id" = ?', [_vals[0]]).fetchone()
        _out = dict(_row)
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_billing_alerts = post_billing_alerts
def _bf_friction_post_billing_alerts(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_billing_alerts(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_billing_alerts|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_billing_alerts(*_bf_args, **_bf_kwargs)
_bf_friction_post_billing_alerts.blobfish_original = _bf_orig_post_billing_alerts
post_billing_alerts = _bf_friction_post_billing_alerts

