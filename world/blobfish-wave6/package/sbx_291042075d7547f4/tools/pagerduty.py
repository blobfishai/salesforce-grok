"""Executable PAGERDUTY tool module

Inspect each function: SQLite helpers are local fixtures; network-backed functions call their declared endpoint.
Tools: cases_list, get_billing_alerts_id, get_billing_alerts, case_create, post_billing_alerts, pd_incidents_list, pd_incident_get, pd_incident_create, pd_incident_manage, pd_incident_notes_list, pd_incident_note_create, pd_incident_log_entries_list, pd_services_list, pd_service_get, pd_service_create, pd_service_update, pd_escalation_policies_list, pd_escalation_policy_get, pd_schedules_list, pd_schedule_get, pd_schedule_overrides_create, pd_oncalls_list, pd_users_list, pd_user_get, pd_teams_list, pd_team_get, pd_maintenance_windows_list, pd_maintenance_window_create, pd_priorities_list
Tables: cases, billing_alerts, alerts, pd_incidents, pd_services, pd_priorities, pd_users, pd_oncalls, pd_log_entries, pd_incident_notes, pd_escalation_policies, pd_schedules, pd_schedule_overrides, pd_teams, pd_maintenance_windows
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

def pd_incidents_list(db_path='state.db', **kwargs):
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    where = []
    args = []
    status = kwargs.get('status')
    if status:
        if status not in ('triggered', 'acknowledged', 'resolved'):
            conn.close()
            return {'error': {'status': 400, 'message': "Invalid status '%s'. Must be one of: triggered, acknowledged, resolved." % status}}
        where.append('status = ?')
        args.append(status)
    service_id = kwargs.get('service_id')
    if service_id:
        where.append('service_id = ?')
        args.append(service_id)
    urgency = kwargs.get('urgency')
    if urgency:
        if urgency not in ('high', 'low'):
            conn.close()
            return {'error': {'status': 400, 'message': "Invalid urgency '%s'. Must be one of: high, low." % urgency}}
        where.append('urgency = ?')
        args.append(urgency)
    since = kwargs.get('since')
    if since:
        where.append('created_at >= ?')
        args.append(since)
    until = kwargs.get('until')
    if until:
        where.append('created_at <= ?')
        args.append(until)
    try:
        limit = int(kwargs.get('limit') or 30)
    except (TypeError, ValueError):
        limit = 30
    sql = 'SELECT * FROM pd_incidents'
    if where:
        sql += ' WHERE ' + ' AND '.join(where)
    sql += ' ORDER BY created_at DESC LIMIT ?'
    args.append(limit)
    rows = [dict(r) for r in conn.execute(sql, args).fetchall()]
    conn.close()
    return {'incidents': rows, 'total': len(rows)}

_env_orig_pd_incidents_list = pd_incidents_list
def _env_pd_incidents_list(db_path='state.db', **kwargs):
    _r = _env_orig_pd_incidents_list(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'incidents': _r['items'], 'limit': _r['count'], 'offset': 0, 'more': False, 'total': _r['count']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'message': str(_r.get('error', '')), 'code': 2100}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'message': str(_r.get('error', '')), 'code': 2001, 'errors': [str(_r.get('error', ''))]}}
    return _r
pd_incidents_list = _env_pd_incidents_list

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_incidents_list = pd_incidents_list
def _bf_friction_pd_incidents_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_incidents_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_incidents_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_incidents_list(*_bf_args, **_bf_kwargs)
_bf_friction_pd_incidents_list.blobfish_original = _bf_orig_pd_incidents_list
pd_incidents_list = _bf_friction_pd_incidents_list

def pd_incident_get(db_path='state.db', **kwargs):
    '''Show detailed information about an incident (GET /incidents/{id})'''
    _missing = [p for p in ['id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'message': str(_r.get('error', '')), 'code': 2001, 'errors': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "pd_incidents" WHERE "id" = ?', [str(kwargs['id'])]).fetchone()
        if _row is None:
            _r = {'error': 'incident not found', 'status': 404}
            return {'error': {'message': str(_r.get('error', '')), 'code': 2100}}
        _r = dict(_row)
        _r = {'incident': _r}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_incident_get = pd_incident_get
def _bf_friction_pd_incident_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_incident_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_incident_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_incident_get(*_bf_args, **_bf_kwargs)
_bf_friction_pd_incident_get.blobfish_original = _bf_orig_pd_incident_get
pd_incident_get = _bf_friction_pd_incident_get

def pd_incident_create(db_path='state.db', **kwargs):
    import sqlite3
    import datetime
    import hashlib
    title = kwargs.get('title')
    if not title:
        return {'error': {'status': 400, 'message': "Missing required parameter 'title'."}}
    service_id = kwargs.get('service_id')
    if not service_id:
        return {'error': {'status': 400, 'message': "Missing required parameter 'service_id'."}}
    urgency = kwargs.get('urgency') or 'high'
    if urgency not in ('high', 'low'):
        return {'error': {'status': 400, 'message': "Invalid urgency '%s'. Must be one of: high, low." % urgency}}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    svc = conn.execute('SELECT * FROM pd_services WHERE id = ?', (service_id,)).fetchone()
    if svc is None:
        conn.close()
        return {'error': {'status': 404, 'message': "Service '%s' not found." % service_id}}
    escalation_policy_id = kwargs.get('escalation_policy_id') or svc['escalation_policy_id']
    priority_id = kwargs.get('priority_id')
    if priority_id:
        if conn.execute('SELECT id FROM pd_priorities WHERE id = ?', (priority_id,)).fetchone() is None:
            conn.close()
            return {'error': {'status': 404, 'message': "Priority '%s' not found." % priority_id}}
    assignee = kwargs.get('assignee')
    if assignee:
        if conn.execute('SELECT id FROM pd_users WHERE id = ?', (assignee,)).fetchone() is None:
            conn.close()
            return {'error': {'status': 404, 'message': "User '%s' not found." % assignee}}
    else:
        oncall = conn.execute('SELECT user_id FROM pd_oncalls WHERE escalation_policy_id = ? AND escalation_level = 1 ORDER BY id LIMIT 1', (escalation_policy_id,)).fetchone()
        assignee = oncall['user_id'] if oncall else None
    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    number = conn.execute('SELECT COALESCE(MAX(incident_number), 0) + 1 AS n FROM pd_incidents').fetchone()['n']
    new_id = 'P' + hashlib.sha1((title + str(number) + str(datetime.datetime.utcnow().timestamp())).encode('utf-8')).hexdigest()[:6].upper()
    conn.execute('INSERT INTO pd_incidents (id, incident_number, title, description, status, urgency, priority_id, service_id, escalation_policy_id, assignee, created_at, resolved_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                 (new_id, number, title, kwargs.get('details'), 'triggered', urgency, priority_id, service_id, escalation_policy_id, assignee, now, None))
    log_id = 'R' + hashlib.sha1((new_id + 'trigger' + str(datetime.datetime.utcnow().timestamp())).encode('utf-8')).hexdigest()[:6].upper()
    conn.execute('INSERT INTO pd_log_entries (id, incident_id, type, agent_id, channel, summary, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                 (log_id, new_id, 'trigger_log_entry', None, 'api', 'Triggered through the API.', now))
    conn.commit()
    row = dict(conn.execute('SELECT * FROM pd_incidents WHERE id = ?', (new_id,)).fetchone())
    conn.close()
    return {'incident': row}

_env_orig_pd_incident_create = pd_incident_create
def _env_pd_incident_create(db_path='state.db', **kwargs):
    _r = _env_orig_pd_incident_create(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'incidents': _r['items'], 'limit': _r['count'], 'offset': 0, 'more': False, 'total': _r['count']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'message': str(_r.get('error', '')), 'code': 2100}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'message': str(_r.get('error', '')), 'code': 2001, 'errors': [str(_r.get('error', ''))]}}
    return _r
pd_incident_create = _env_pd_incident_create

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_incident_create = pd_incident_create
def _bf_friction_pd_incident_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_incident_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_incident_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_incident_create(*_bf_args, **_bf_kwargs)
_bf_friction_pd_incident_create.blobfish_original = _bf_orig_pd_incident_create
pd_incident_create = _bf_friction_pd_incident_create

def pd_incident_manage(db_path='state.db', **kwargs):
    import sqlite3
    import datetime
    import hashlib
    incident_id = kwargs.get('id')
    if not incident_id:
        return {'error': {'status': 400, 'message': "Missing required parameter 'id'."}}
    status = kwargs.get('status')
    escalation_level = kwargs.get('escalation_level')
    if status is None and escalation_level is None:
        return {'error': {'status': 400, 'message': "Nothing to update: provide 'status' (acknowledged or resolved) and/or 'escalation_level'."}}
    if status is not None and status not in ('acknowledged', 'resolved'):
        return {'error': {'status': 400, 'message': "Invalid status '%s'. Must be one of: acknowledged, resolved." % status}}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM pd_incidents WHERE id = ?', (incident_id,)).fetchone()
    if row is None:
        conn.close()
        return {'error': {'status': 404, 'message': "Incident '%s' not found." % incident_id}}
    if row['status'] == 'resolved':
        conn.close()
        return {'error': {'status': 400, 'message': "Incident '%s' is already resolved; resolved incidents cannot be modified." % incident_id}}
    agent_id = None
    from_email = kwargs.get('from')
    if from_email:
        user = conn.execute('SELECT id FROM pd_users WHERE email = ?', (from_email,)).fetchone()
        if user is None:
            conn.close()
            return {'error': {'status': 404, 'message': "No user found with email '%s' (From header)." % from_email}}
        agent_id = user['id']
    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    def _log(entry_type, summary):
        log_id = 'R' + hashlib.sha1((incident_id + entry_type + str(datetime.datetime.utcnow().timestamp())).encode('utf-8')).hexdigest()[:6].upper()
        conn.execute('INSERT INTO pd_log_entries (id, incident_id, type, agent_id, channel, summary, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (log_id, incident_id, entry_type, agent_id, 'api', summary, now))

    if escalation_level is not None:
        try:
            level = int(escalation_level)
        except (TypeError, ValueError):
            conn.close()
            return {'error': {'status': 400, 'message': "Invalid escalation_level '%s': must be an integer." % escalation_level}}
        oncall = conn.execute('SELECT user_id FROM pd_oncalls WHERE escalation_policy_id = ? AND escalation_level = ? ORDER BY id LIMIT 1', (row['escalation_policy_id'], level)).fetchone()
        if oncall is None:
            conn.close()
            return {'error': {'status': 400, 'message': "No on-call target at escalation level %d on escalation policy '%s'." % (level, row['escalation_policy_id'])}}
        conn.execute('UPDATE pd_incidents SET status = ?, assignee = ? WHERE id = ?', ('triggered', oncall['user_id'], incident_id))
        _log('escalate_log_entry', 'Escalated to level %d of escalation policy %s; assigned to %s.' % (level, row['escalation_policy_id'], oncall['user_id']))
    if status == 'acknowledged':
        conn.execute('UPDATE pd_incidents SET status = ? WHERE id = ?', ('acknowledged', incident_id))
        _log('acknowledge_log_entry', 'Acknowledged by %s.' % (agent_id or 'API'))
    elif status == 'resolved':
        conn.execute('UPDATE pd_incidents SET status = ?, resolved_at = ? WHERE id = ?', ('resolved', now, incident_id))
        _log('resolve_log_entry', 'Resolved by %s.' % (agent_id or 'API'))
        resolution = kwargs.get('resolution')
        if resolution:
            note_id = 'P' + hashlib.sha1((incident_id + resolution + str(datetime.datetime.utcnow().timestamp())).encode('utf-8')).hexdigest()[:6].upper()
            conn.execute('INSERT INTO pd_incident_notes (id, incident_id, user_id, content, created_at) VALUES (?, ?, ?, ?, ?)',
                         (note_id, incident_id, agent_id, resolution, now))
    conn.commit()
    updated = dict(conn.execute('SELECT * FROM pd_incidents WHERE id = ?', (incident_id,)).fetchone())
    conn.close()
    return {'incident': updated}

_env_orig_pd_incident_manage = pd_incident_manage
def _env_pd_incident_manage(db_path='state.db', **kwargs):
    _r = _env_orig_pd_incident_manage(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'incidents': _r['items'], 'limit': _r['count'], 'offset': 0, 'more': False, 'total': _r['count']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'message': str(_r.get('error', '')), 'code': 2100}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'message': str(_r.get('error', '')), 'code': 2001, 'errors': [str(_r.get('error', ''))]}}
    return _r
pd_incident_manage = _env_pd_incident_manage

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_incident_manage = pd_incident_manage
def _bf_friction_pd_incident_manage(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_incident_manage(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_incident_manage|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_incident_manage(*_bf_args, **_bf_kwargs)
_bf_friction_pd_incident_manage.blobfish_original = _bf_orig_pd_incident_manage
pd_incident_manage = _bf_friction_pd_incident_manage

def pd_incident_notes_list(db_path='state.db', **kwargs):
    '''List existing notes for the specified incident (GET /incidents/{id}/notes)'''
    _missing = [p for p in ['incident_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'message': str(_r.get('error', '')), 'code': 2001, 'errors': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('incident_id') is not None:
            _where.append('"incident_id" = ?')
            _args.append(str(kwargs['incident_id']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "pd_incident_notes"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'incident_notes': _r['items'], 'limit': _r['count'], 'offset': 0, 'more': False, 'total': _r['count']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_incident_notes_list = pd_incident_notes_list
def _bf_friction_pd_incident_notes_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_incident_notes_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_incident_notes_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_incident_notes_list(*_bf_args, **_bf_kwargs)
_bf_friction_pd_incident_notes_list.blobfish_original = _bf_orig_pd_incident_notes_list
pd_incident_notes_list = _bf_friction_pd_incident_notes_list

def pd_incident_note_create(db_path='state.db', **kwargs):
    import sqlite3
    import datetime
    import hashlib
    incident_id = kwargs.get('incident_id')
    if not incident_id:
        return {'error': {'status': 400, 'message': "Missing required parameter 'incident_id'."}}
    content = kwargs.get('content')
    if not content:
        return {'error': {'status': 400, 'message': "Missing required parameter 'content'."}}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    if conn.execute('SELECT id FROM pd_incidents WHERE id = ?', (incident_id,)).fetchone() is None:
        conn.close()
        return {'error': {'status': 404, 'message': "Incident '%s' not found." % incident_id}}
    user_id = None
    from_email = kwargs.get('from')
    if from_email:
        user = conn.execute('SELECT id FROM pd_users WHERE email = ?', (from_email,)).fetchone()
        if user is None:
            conn.close()
            return {'error': {'status': 404, 'message': "No user found with email '%s' (From header)." % from_email}}
        user_id = user['id']
    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    note_id = 'P' + hashlib.sha1((incident_id + content + str(datetime.datetime.utcnow().timestamp())).encode('utf-8')).hexdigest()[:6].upper()
    conn.execute('INSERT INTO pd_incident_notes (id, incident_id, user_id, content, created_at) VALUES (?, ?, ?, ?, ?)',
                 (note_id, incident_id, user_id, content, now))
    log_id = 'R' + hashlib.sha1((incident_id + 'annotate' + str(datetime.datetime.utcnow().timestamp())).encode('utf-8')).hexdigest()[:6].upper()
    conn.execute('INSERT INTO pd_log_entries (id, incident_id, type, agent_id, channel, summary, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                 (log_id, incident_id, 'annotate_log_entry', user_id, 'api', 'Note added to the incident.', now))
    conn.commit()
    row = dict(conn.execute('SELECT * FROM pd_incident_notes WHERE id = ?', (note_id,)).fetchone())
    conn.close()
    return {'note': row}

_env_orig_pd_incident_note_create = pd_incident_note_create
def _env_pd_incident_note_create(db_path='state.db', **kwargs):
    _r = _env_orig_pd_incident_note_create(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'incident_notes': _r['items'], 'limit': _r['count'], 'offset': 0, 'more': False, 'total': _r['count']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'message': str(_r.get('error', '')), 'code': 2100}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'message': str(_r.get('error', '')), 'code': 2001, 'errors': [str(_r.get('error', ''))]}}
    return _r
pd_incident_note_create = _env_pd_incident_note_create

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_incident_note_create = pd_incident_note_create
def _bf_friction_pd_incident_note_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_incident_note_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_incident_note_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_incident_note_create(*_bf_args, **_bf_kwargs)
_bf_friction_pd_incident_note_create.blobfish_original = _bf_orig_pd_incident_note_create
pd_incident_note_create = _bf_friction_pd_incident_note_create

def pd_incident_log_entries_list(db_path='state.db', **kwargs):
    '''List log entries (trigger, acknowledge, escalate, resolve, annotate) for the specified incident (GET /incidents/{id}/log_entries)'''
    _missing = [p for p in ['incident_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'message': str(_r.get('error', '')), 'code': 2001, 'errors': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('incident_id') is not None:
            _where.append('"incident_id" = ?')
            _args.append(str(kwargs['incident_id']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "pd_log_entries"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'log_entries': _r['items'], 'limit': _r['count'], 'offset': 0, 'more': False, 'total': _r['count']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_incident_log_entries_list = pd_incident_log_entries_list
def _bf_friction_pd_incident_log_entries_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_incident_log_entries_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_incident_log_entries_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_incident_log_entries_list(*_bf_args, **_bf_kwargs)
_bf_friction_pd_incident_log_entries_list.blobfish_original = _bf_orig_pd_incident_log_entries_list
pd_incident_log_entries_list = _bf_friction_pd_incident_log_entries_list

def pd_services_list(db_path='state.db', **kwargs):
    '''List existing services, optionally filtered by team (GET /services)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('team_id') is not None:
            _where.append('"team_id" = ?')
            _args.append(str(kwargs['team_id']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "pd_services"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'services': _r['items'], 'limit': _r['count'], 'offset': 0, 'more': False, 'total': _r['count']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_services_list = pd_services_list
def _bf_friction_pd_services_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_services_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_services_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_services_list(*_bf_args, **_bf_kwargs)
_bf_friction_pd_services_list.blobfish_original = _bf_orig_pd_services_list
pd_services_list = _bf_friction_pd_services_list

def pd_service_get(db_path='state.db', **kwargs):
    '''Get details about an existing service (GET /services/{id})'''
    _missing = [p for p in ['id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'message': str(_r.get('error', '')), 'code': 2001, 'errors': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "pd_services" WHERE "id" = ?', [str(kwargs['id'])]).fetchone()
        if _row is None:
            _r = {'error': 'service not found', 'status': 404}
            return {'error': {'message': str(_r.get('error', '')), 'code': 2100}}
        _r = dict(_row)
        _r = {'service': _r}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_service_get = pd_service_get
def _bf_friction_pd_service_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_service_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_service_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_service_get(*_bf_args, **_bf_kwargs)
_bf_friction_pd_service_get.blobfish_original = _bf_orig_pd_service_get
pd_service_get = _bf_friction_pd_service_get

def pd_service_create(db_path='state.db', **kwargs):
    '''Create a new service tied to an escalation policy (POST /services)'''
    _missing = [p for p in ['name', 'escalation_policy_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'message': str(_r.get('error', '')), 'code': 2001, 'errors': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "pd_services"').fetchone()[0] + 1
        _id = 'P' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "pd_services" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'P' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('name') is not None:
            _cols.append('name')
            _v = kwargs['name']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('description') is not None:
            _cols.append('description')
            _v = kwargs['description']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('escalation_policy_id') is not None:
            _cols.append('escalation_policy_id')
            _v = kwargs['escalation_policy_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('team_id') is not None:
            _cols.append('team_id')
            _v = kwargs['team_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'status' not in _cols:
            _cols.append('status')
            _vals.append('active')
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "pd_services" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "pd_services" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r = {'service': _r}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_service_create = pd_service_create
def _bf_friction_pd_service_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_service_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_service_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_service_create(*_bf_args, **_bf_kwargs)
_bf_friction_pd_service_create.blobfish_original = _bf_orig_pd_service_create
pd_service_create = _bf_friction_pd_service_create

def pd_service_update(db_path='state.db', **kwargs):
    '''Update an existing service's name, description, state, or escalation policy (PUT /services/{id})'''
    _missing = [p for p in ['id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'message': str(_r.get('error', '')), 'code': 2001, 'errors': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "pd_services" WHERE "id" = ?', [str(kwargs['id'])]).fetchone()
        if _row is None:
            _r = {'error': 'service not found', 'status': 404}
            return {'error': {'message': str(_r.get('error', '')), 'code': 2100}}
        _sets, _args = [], []
        if kwargs.get('name') is not None:
            _sets.append('"name" = ?')
            _v = kwargs['name']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('description') is not None:
            _sets.append('"description" = ?')
            _v = kwargs['description']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('status') is not None:
            _sets.append('"status" = ?')
            _v = kwargs['status']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('escalation_policy_id') is not None:
            _sets.append('"escalation_policy_id" = ?')
            _v = kwargs['escalation_policy_id']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "pd_services" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "pd_services" WHERE "id" = ?', [str(kwargs['id'])]).fetchone()
        _r = dict(_row)
        _r = {'service': _r}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_service_update = pd_service_update
def _bf_friction_pd_service_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_service_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_service_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_service_update(*_bf_args, **_bf_kwargs)
_bf_friction_pd_service_update.blobfish_original = _bf_orig_pd_service_update
pd_service_update = _bf_friction_pd_service_update

def pd_escalation_policies_list(db_path='state.db', **kwargs):
    '''List all of the existing escalation policies, optionally filtered by team (GET /escalation_policies)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('team_id') is not None:
            _where.append('"team_id" = ?')
            _args.append(str(kwargs['team_id']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "pd_escalation_policies"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'escalation_policies': _r['items'], 'limit': _r['count'], 'offset': 0, 'more': False, 'total': _r['count']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_escalation_policies_list = pd_escalation_policies_list
def _bf_friction_pd_escalation_policies_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_escalation_policies_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_escalation_policies_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_escalation_policies_list(*_bf_args, **_bf_kwargs)
_bf_friction_pd_escalation_policies_list.blobfish_original = _bf_orig_pd_escalation_policies_list
pd_escalation_policies_list = _bf_friction_pd_escalation_policies_list

def pd_escalation_policy_get(db_path='state.db', **kwargs):
    '''Get information about an existing escalation policy and its rules (GET /escalation_policies/{id})'''
    _missing = [p for p in ['id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'message': str(_r.get('error', '')), 'code': 2001, 'errors': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "pd_escalation_policies" WHERE "id" = ?', [str(kwargs['id'])]).fetchone()
        if _row is None:
            _r = {'error': 'escalation_policie not found', 'status': 404}
            return {'error': {'message': str(_r.get('error', '')), 'code': 2100}}
        _r = dict(_row)
        _r = {'escalation_policie': _r}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_escalation_policy_get = pd_escalation_policy_get
def _bf_friction_pd_escalation_policy_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_escalation_policy_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_escalation_policy_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_escalation_policy_get(*_bf_args, **_bf_kwargs)
_bf_friction_pd_escalation_policy_get.blobfish_original = _bf_orig_pd_escalation_policy_get
pd_escalation_policy_get = _bf_friction_pd_escalation_policy_get

def pd_schedules_list(db_path='state.db', **kwargs):
    '''List the on-call schedules configured in the account (GET /schedules)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "pd_schedules"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'schedules': _r['items'], 'limit': _r['count'], 'offset': 0, 'more': False, 'total': _r['count']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_schedules_list = pd_schedules_list
def _bf_friction_pd_schedules_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_schedules_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_schedules_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_schedules_list(*_bf_args, **_bf_kwargs)
_bf_friction_pd_schedules_list.blobfish_original = _bf_orig_pd_schedules_list
pd_schedules_list = _bf_friction_pd_schedules_list

def pd_schedule_get(db_path='state.db', **kwargs):
    '''Show detailed information about a schedule, including its time zone (GET /schedules/{id})'''
    _missing = [p for p in ['id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'message': str(_r.get('error', '')), 'code': 2001, 'errors': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "pd_schedules" WHERE "id" = ?', [str(kwargs['id'])]).fetchone()
        if _row is None:
            _r = {'error': 'schedule not found', 'status': 404}
            return {'error': {'message': str(_r.get('error', '')), 'code': 2100}}
        _r = dict(_row)
        _r = {'schedule': _r}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_schedule_get = pd_schedule_get
def _bf_friction_pd_schedule_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_schedule_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_schedule_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_schedule_get(*_bf_args, **_bf_kwargs)
_bf_friction_pd_schedule_get.blobfish_original = _bf_orig_pd_schedule_get
pd_schedule_get = _bf_friction_pd_schedule_get

def pd_schedule_overrides_create(db_path='state.db', **kwargs):
    '''Create an override for a specific user covering the specified time range on a schedule (POST /schedules/{id}/overrides)'''
    _missing = [p for p in ['schedule_id', 'user_id', 'start', 'end_time'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'message': str(_r.get('error', '')), 'code': 2001, 'errors': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "pd_schedule_overrides"').fetchone()[0] + 1
        _id = 'P' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "pd_schedule_overrides" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'P' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('schedule_id') is not None:
            _cols.append('schedule_id')
            _v = kwargs['schedule_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('user_id') is not None:
            _cols.append('user_id')
            _v = kwargs['user_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('start') is not None:
            _cols.append('start')
            _v = kwargs['start']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('end_time') is not None:
            _cols.append('end_time')
            _v = kwargs['end_time']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "pd_schedule_overrides" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "pd_schedule_overrides" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r = {'schedule_override': _r}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_schedule_overrides_create = pd_schedule_overrides_create
def _bf_friction_pd_schedule_overrides_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_schedule_overrides_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_schedule_overrides_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_schedule_overrides_create(*_bf_args, **_bf_kwargs)
_bf_friction_pd_schedule_overrides_create.blobfish_original = _bf_orig_pd_schedule_overrides_create
pd_schedule_overrides_create = _bf_friction_pd_schedule_overrides_create

def pd_oncalls_list(db_path='state.db', **kwargs):
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    where = []
    args = []
    for param, column in (('schedule_id', 'o.schedule_id'), ('escalation_policy_id', 'o.escalation_policy_id'), ('user_id', 'o.user_id')):
        value = kwargs.get(param)
        if value:
            where.append(column + ' = ?')
            args.append(value)
    try:
        limit = int(kwargs.get('limit') or 30)
    except (TypeError, ValueError):
        limit = 30
    sql = ('SELECT o.id, o.escalation_policy_id, ep.name AS escalation_policy_name, '
           'o.schedule_id, s.name AS schedule_name, o.user_id, u.name AS user_name, '
           'u.email AS user_email, o.escalation_level, o.start, o.end_time AS "end" '
           'FROM pd_oncalls o '
           'LEFT JOIN pd_users u ON u.id = o.user_id '
           'LEFT JOIN pd_schedules s ON s.id = o.schedule_id '
           'LEFT JOIN pd_escalation_policies ep ON ep.id = o.escalation_policy_id')
    if where:
        sql += ' WHERE ' + ' AND '.join(where)
    sql += ' ORDER BY o.escalation_policy_id, o.escalation_level LIMIT ?'
    args.append(limit)
    rows = [dict(r) for r in conn.execute(sql, args).fetchall()]
    conn.close()
    return {'oncalls': rows, 'total': len(rows)}

_env_orig_pd_oncalls_list = pd_oncalls_list
def _env_pd_oncalls_list(db_path='state.db', **kwargs):
    _r = _env_orig_pd_oncalls_list(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'oncalls': _r['items'], 'limit': _r['count'], 'offset': 0, 'more': False, 'total': _r['count']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'message': str(_r.get('error', '')), 'code': 2100}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'message': str(_r.get('error', '')), 'code': 2001, 'errors': [str(_r.get('error', ''))]}}
    return _r
pd_oncalls_list = _env_pd_oncalls_list

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_oncalls_list = pd_oncalls_list
def _bf_friction_pd_oncalls_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_oncalls_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_oncalls_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_oncalls_list(*_bf_args, **_bf_kwargs)
_bf_friction_pd_oncalls_list.blobfish_original = _bf_orig_pd_oncalls_list
pd_oncalls_list = _bf_friction_pd_oncalls_list

def pd_users_list(db_path='state.db', **kwargs):
    '''List users of the PagerDuty account, optionally filtered by team (GET /users)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('team_id') is not None:
            _where.append('"team_id" = ?')
            _args.append(str(kwargs['team_id']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "pd_users"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'users': _r['items'], 'limit': _r['count'], 'offset': 0, 'more': False, 'total': _r['count']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_users_list = pd_users_list
def _bf_friction_pd_users_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_users_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_users_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_users_list(*_bf_args, **_bf_kwargs)
_bf_friction_pd_users_list.blobfish_original = _bf_orig_pd_users_list
pd_users_list = _bf_friction_pd_users_list

def pd_user_get(db_path='state.db', **kwargs):
    '''Get details about an existing user (GET /users/{id})'''
    _missing = [p for p in ['id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'message': str(_r.get('error', '')), 'code': 2001, 'errors': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "pd_users" WHERE "id" = ?', [str(kwargs['id'])]).fetchone()
        if _row is None:
            _r = {'error': 'user not found', 'status': 404}
            return {'error': {'message': str(_r.get('error', '')), 'code': 2100}}
        _r = dict(_row)
        _r = {'user': _r}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_user_get = pd_user_get
def _bf_friction_pd_user_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_user_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_user_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_user_get(*_bf_args, **_bf_kwargs)
_bf_friction_pd_user_get.blobfish_original = _bf_orig_pd_user_get
pd_user_get = _bf_friction_pd_user_get

def pd_teams_list(db_path='state.db', **kwargs):
    '''List teams of the PagerDuty account (GET /teams)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "pd_teams"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'teams': _r['items'], 'limit': _r['count'], 'offset': 0, 'more': False, 'total': _r['count']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_teams_list = pd_teams_list
def _bf_friction_pd_teams_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_teams_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_teams_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_teams_list(*_bf_args, **_bf_kwargs)
_bf_friction_pd_teams_list.blobfish_original = _bf_orig_pd_teams_list
pd_teams_list = _bf_friction_pd_teams_list

def pd_team_get(db_path='state.db', **kwargs):
    '''Get details about an existing team (GET /teams/{id})'''
    _missing = [p for p in ['id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'message': str(_r.get('error', '')), 'code': 2001, 'errors': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "pd_teams" WHERE "id" = ?', [str(kwargs['id'])]).fetchone()
        if _row is None:
            _r = {'error': 'team not found', 'status': 404}
            return {'error': {'message': str(_r.get('error', '')), 'code': 2100}}
        _r = dict(_row)
        _r = {'team': _r}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_team_get = pd_team_get
def _bf_friction_pd_team_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_team_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_team_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_team_get(*_bf_args, **_bf_kwargs)
_bf_friction_pd_team_get.blobfish_original = _bf_orig_pd_team_get
pd_team_get = _bf_friction_pd_team_get

def pd_maintenance_windows_list(db_path='state.db', **kwargs):
    '''List existing maintenance windows, optionally filtered by service (GET /maintenance_windows)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('service_id') is not None:
            _where.append('"service_id" = ?')
            _args.append(str(kwargs['service_id']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "pd_maintenance_windows"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'maintenance_windows': _r['items'], 'limit': _r['count'], 'offset': 0, 'more': False, 'total': _r['count']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_maintenance_windows_list = pd_maintenance_windows_list
def _bf_friction_pd_maintenance_windows_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_maintenance_windows_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_maintenance_windows_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_maintenance_windows_list(*_bf_args, **_bf_kwargs)
_bf_friction_pd_maintenance_windows_list.blobfish_original = _bf_orig_pd_maintenance_windows_list
pd_maintenance_windows_list = _bf_friction_pd_maintenance_windows_list

def pd_maintenance_window_create(db_path='state.db', **kwargs):
    '''Create a new maintenance window for a service; alerts are suppressed while the window is active (POST /maintenance_windows)'''
    _missing = [p for p in ['service_id', 'start_time', 'end_time'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'message': str(_r.get('error', '')), 'code': 2001, 'errors': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "pd_maintenance_windows"').fetchone()[0] + 1
        _id = 'P' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "pd_maintenance_windows" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'P' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('service_id') is not None:
            _cols.append('service_id')
            _v = kwargs['service_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('start_time') is not None:
            _cols.append('start_time')
            _v = kwargs['start_time']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('end_time') is not None:
            _cols.append('end_time')
            _v = kwargs['end_time']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('description') is not None:
            _cols.append('description')
            _v = kwargs['description']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('created_by') is not None:
            _cols.append('created_by')
            _v = kwargs['created_by']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "pd_maintenance_windows" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "pd_maintenance_windows" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r = {'maintenance_window': _r}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_maintenance_window_create = pd_maintenance_window_create
def _bf_friction_pd_maintenance_window_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_maintenance_window_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_maintenance_window_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_maintenance_window_create(*_bf_args, **_bf_kwargs)
_bf_friction_pd_maintenance_window_create.blobfish_original = _bf_orig_pd_maintenance_window_create
pd_maintenance_window_create = _bf_friction_pd_maintenance_window_create

def pd_priorities_list(db_path='state.db', **kwargs):
    '''List existing priority levels (P1 through P5) configured for the account (GET /priorities)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "pd_priorities"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'priorities': _r['items'], 'limit': _r['count'], 'offset': 0, 'more': False, 'total': _r['count']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_priorities_list = pd_priorities_list
def _bf_friction_pd_priorities_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_priorities_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_priorities_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_priorities_list(*_bf_args, **_bf_kwargs)
_bf_friction_pd_priorities_list.blobfish_original = _bf_orig_pd_priorities_list
pd_priorities_list = _bf_friction_pd_priorities_list

