"""Executable CALENDAR tool module

Inspect each function: SQLite helpers are local fixtures; network-backed functions call their declared endpoint.
Tools: list_scheduled_runs, query_calendar_events, calendar_calendar_list_list, calendar_acl_list, calendar_calendar_list_get, calendar_calendars_get, calendar_agent, create_scheduled_run, calendar_calendar_list_insert, calendar_calendars_insert
Tables: agent_scheduled_runs, agent_events, calendar_lists, acls, calendar_list_entries, calendars
"""
import json, sqlite3
"""List agent_scheduled_runs records"""
import sqlite3

def list_scheduled_runs(db_path, limit=50, **kwargs):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute('SELECT * FROM agent_scheduled_runs ORDER BY id LIMIT ?', (min(int(limit), 200),)).fetchall()]
    conn.close()
    return {"table": "agent_scheduled_runs", "count": len(rows), "rows": rows}

"""Search agent_events records by free text"""
import sqlite3

def query_calendar_events(db_path, query=None, limit=50, **kwargs):
    try:
        bounded_limit = max(1, min(int(limit), 200))
    except (TypeError, ValueError):
        return {"error": "validation_error", "message": "limit must be an integer"}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    if query is None or not str(query).strip():
        rows = [dict(r) for r in conn.execute('SELECT * FROM agent_events ORDER BY id LIMIT ?', (bounded_limit,)).fetchall()]
    else:
        pattern = '%' + str(query).strip() + '%'
        rows = [dict(r) for r in conn.execute('SELECT * FROM agent_events WHERE title LIKE ? OR event_date LIKE ? ORDER BY id LIMIT ?', (pattern, pattern, bounded_limit)).fetchall()]
    conn.close()
    return {"table": "agent_events", "query": query, "count": len(rows), "rows": rows}

def calendar_calendar_list_list(db_path='state.db', **kwargs):
    '''Returns the calendars on the users calendar list. (GET /users/me/calendarList)'''
    if kwargs.get('minAccessRole') is not None and kwargs.get('minAccessRole') not in ['freeBusyReader', 'owner', 'reader', 'writer', 'writerWithoutPrivateAccess']:
        return {'error': 'invalid value for minAccessRole: %r. Accepted: %s' % (kwargs.get('minAccessRole'), ', '.join(['freeBusyReader', 'owner', 'reader', 'writer', 'writerWithoutPrivateAccess'])), 'status': 422, 'parameter': 'minAccessRole', 'accepted': ['freeBusyReader', 'owner', 'reader', 'writer', 'writerWithoutPrivateAccess']}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "calendar_lists"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        return {'items': _rows, 'count': len(_rows)}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_calendar_calendar_list_list = calendar_calendar_list_list
def _bf_friction_calendar_calendar_list_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_calendar_calendar_list_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "calendar_calendar_list_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_calendar_calendar_list_list(*_bf_args, **_bf_kwargs)
_bf_friction_calendar_calendar_list_list.blobfish_original = _bf_orig_calendar_calendar_list_list
calendar_calendar_list_list = _bf_friction_calendar_calendar_list_list

def calendar_acl_list(db_path='state.db', **kwargs):
    '''Returns the rules in the access control list for the calendar. (GET /calendars/{calendarId}/acl)'''
    _missing = [p for p in ['calendarId'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('calendarId') is not None:
            _where.append('"id" = ?')
            _args.append(str(kwargs['calendarId']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "acls"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        return {'items': _rows, 'count': len(_rows)}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_calendar_acl_list = calendar_acl_list
def _bf_friction_calendar_acl_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_calendar_acl_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "calendar_acl_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_calendar_acl_list(*_bf_args, **_bf_kwargs)
_bf_friction_calendar_acl_list.blobfish_original = _bf_orig_calendar_acl_list
calendar_acl_list = _bf_friction_calendar_acl_list

def calendar_calendar_list_get(db_path='state.db', **kwargs):
    '''Returns a calendar from the users calendar list. (GET /users/me/calendarList/{calendarId})'''
    _missing = [p for p in ['calendarId'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "calendar_list_entries" WHERE "id" = ?', [str(kwargs.get('calendarId'))]).fetchone()
        if _row is None:
            return {'error': 'calendar_list_entry not found', 'status': 404}
        _out = dict(_row)
        for _jc in ['conference_properties', 'notification_settings', 'default_reminders']:
            if isinstance(_out.get(_jc), str) and _out[_jc][:1] in ('[', '{'):
                try:
                    _out[_jc] = json.loads(_out[_jc])
                except Exception:
                    pass
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_calendar_calendar_list_get = calendar_calendar_list_get
def _bf_friction_calendar_calendar_list_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_calendar_calendar_list_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "calendar_calendar_list_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_calendar_calendar_list_get(*_bf_args, **_bf_kwargs)
_bf_friction_calendar_calendar_list_get.blobfish_original = _bf_orig_calendar_calendar_list_get
calendar_calendar_list_get = _bf_friction_calendar_calendar_list_get

def calendar_calendars_get(db_path='state.db', **kwargs):
    '''Returns metadata for a calendar. (GET /calendars/{calendarId})'''
    _missing = [p for p in ['calendarId'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "calendars" WHERE "id" = ?', [str(kwargs.get('calendarId'))]).fetchone()
        if _row is None:
            return {'error': 'calendar not found', 'status': 404}
        _out = dict(_row)
        for _jc in ['conference_properties', 'label_properties']:
            if isinstance(_out.get(_jc), str) and _out[_jc][:1] in ('[', '{'):
                try:
                    _out[_jc] = json.loads(_out[_jc])
                except Exception:
                    pass
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_calendar_calendars_get = calendar_calendars_get
def _bf_friction_calendar_calendars_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_calendar_calendars_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "calendar_calendars_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_calendar_calendars_get(*_bf_args, **_bf_kwargs)
_bf_friction_calendar_calendars_get.blobfish_original = _bf_orig_calendar_calendars_get
calendar_calendars_get = _bf_friction_calendar_calendars_get

"""Free-text scheduling sub-agent. Verbs: schedule "T" on YYYY-MM-DD · read events."""
import re, sqlite3

def calendar_agent(db_path, request=None, **kwargs):
    if not request or not str(request).strip():
        return {"error": "validation_error", "message": "request is required — describe the scheduling action"}
    req = str(request).strip()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        if re.search(r'^\s*read\s+events', req, re.I):
            rows = [dict(r) for r in conn.execute("SELECT * FROM agent_events ORDER BY event_date LIMIT 100").fetchall()]
            return {"count": len(rows), "rows": rows}
        m = re.search(r'^\s*(?:schedule|create\s+event)\s+"([^"]+)"(?:\s+on\s+(\d{4}-\d{2}-\d{2}))?', req, re.I)
        title = m.group(1).strip() if m else re.sub(r'\s+', ' ', req)[:80]
        event_date = (m.group(2) if m and m.group(2) else "")
        next_id = (conn.execute("SELECT MAX(id) FROM agent_events").fetchone()[0] or 0) + 1
        conn.execute("INSERT INTO agent_events (id, title, event_date, created_at) VALUES (?, ?, ?, datetime('now'))", (next_id, title, event_date))
        conn.commit()
        return {"status": "scheduled", "event": title, "event_id": next_id, "event_date": event_date or "unspecified"}
    finally:
        conn.close()

"""Insert one agent_scheduled_runs record"""
import sqlite3

def create_scheduled_run(db_path, name=None, schedule=None, playbook_name=None, **kwargs):
    if not name:
        return {"error": "validation_error", "message": "name is required"}
    if not schedule:
        return {"error": "validation_error", "message": "schedule is required"}
    conn = sqlite3.connect(db_path)
    next_id = (conn.execute("SELECT MAX(id) FROM agent_scheduled_runs").fetchone()[0] or 0) + 1
    conn.execute("INSERT INTO agent_scheduled_runs (id, name, schedule, playbook_name, status, created_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
                 (next_id, name, schedule, playbook_name, "scheduled"))
    conn.commit()
    conn.close()
    return {"status": "saved", "table": "agent_scheduled_runs", "id": next_id}

def calendar_calendar_list_insert(db_path='state.db', **kwargs):
    '''Inserts an existing calendar into the users calendar list. (POST /users/me/calendarList)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _n = cur.execute('SELECT COALESCE(MAX(rowid), 0) + 100 FROM "calendar_list_entries"').fetchone()[0] + 1
        _base = datetime.datetime(2026, 1, 5, 9, 0, 0)
        _ts = (_base + datetime.timedelta(minutes=_n)).strftime('%Y-%m-%dT%H:%M:%SZ')
        _cols = ['"id"']
        _vals = ['' + ('%x' % _n).zfill(20) + '']
        if kwargs.get('hidden') is not None:
            _cols.append('"hidden"')
            _vals.append((1 if kwargs['hidden'] in (True, 'true', 1, '1') else 0))
        if kwargs.get('primary') is not None:
            _cols.append('"primary"')
            _vals.append((1 if kwargs['primary'] in (True, 'true', 1, '1') else 0))
        if kwargs.get('auto_accept_invitations') is not None:
            _cols.append('"auto_accept_invitations"')
            _vals.append((1 if kwargs['auto_accept_invitations'] in (True, 'true', 1, '1') else 0))
        if kwargs.get('location') is not None:
            _cols.append('"location"')
            _vals.append(str(kwargs['location']))
        if kwargs.get('conference_properties') is not None:
            _cols.append('"conference_properties"')
            _vals.append(json.dumps(kwargs['conference_properties']) if not isinstance(kwargs['conference_properties'], str) else kwargs['conference_properties'])
        if kwargs.get('background_color') is not None:
            _cols.append('"background_color"')
            _vals.append(str(kwargs['background_color']))
        if kwargs.get('color_id') is not None:
            _cols.append('"color_id"')
            _vals.append(str(kwargs['color_id']))
        if kwargs.get('description') is not None:
            _cols.append('"description"')
            _vals.append(str(kwargs['description']))
        if kwargs.get('etag') is not None:
            _cols.append('"etag"')
            _vals.append(str(kwargs['etag']))
        if kwargs.get('selected') is not None:
            _cols.append('"selected"')
            _vals.append((1 if kwargs['selected'] in (True, 'true', 1, '1') else 0))
        if kwargs.get('access_role') is not None:
            _cols.append('"access_role"')
            _vals.append(str(kwargs['access_role']))
        if kwargs.get('summary') is not None:
            _cols.append('"summary"')
            _vals.append(str(kwargs['summary']))
        if kwargs.get('notification_settings') is not None:
            _cols.append('"notification_settings"')
            _vals.append(json.dumps(kwargs['notification_settings']) if not isinstance(kwargs['notification_settings'], str) else kwargs['notification_settings'])
        if kwargs.get('default_reminders') is not None:
            _cols.append('"default_reminders"')
            _vals.append(json.dumps(kwargs['default_reminders']) if not isinstance(kwargs['default_reminders'], str) else kwargs['default_reminders'])
        if kwargs.get('time_zone') is not None:
            _cols.append('"time_zone"')
            _vals.append(str(kwargs['time_zone']))
        if kwargs.get('kind') is not None:
            _cols.append('"kind"')
            _vals.append(str(kwargs['kind']))
        if kwargs.get('foreground_color') is not None:
            _cols.append('"foreground_color"')
            _vals.append(str(kwargs['foreground_color']))
        if kwargs.get('summary_override') is not None:
            _cols.append('"summary_override"')
            _vals.append(str(kwargs['summary_override']))
        if kwargs.get('data_owner') is not None:
            _cols.append('"data_owner"')
            _vals.append(str(kwargs['data_owner']))
        if kwargs.get('deleted') is not None:
            _cols.append('"deleted"')
            _vals.append((1 if kwargs['deleted'] in (True, 'true', 1, '1') else 0))
        _sql = 'INSERT INTO "calendar_list_entries" (' + ', '.join(_cols) + ') VALUES (' + ', '.join(['?'] * len(_vals)) + ')'
        try:
            cur.execute(_sql, _vals)
        except sqlite3.IntegrityError:
            conn.rollback()
            return {'error': 'conflict: duplicate key', 'status': 409}
        conn.commit()
        _row = cur.execute('SELECT * FROM "calendar_list_entries" WHERE "id" = ?', [_vals[0]]).fetchone()
        _out = dict(_row)
        for _jc in ['conference_properties', 'notification_settings', 'default_reminders']:
            if isinstance(_out.get(_jc), str) and _out[_jc][:1] in ('[', '{'):
                try:
                    _out[_jc] = json.loads(_out[_jc])
                except Exception:
                    pass
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_calendar_calendar_list_insert = calendar_calendar_list_insert
def _bf_friction_calendar_calendar_list_insert(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_calendar_calendar_list_insert(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "calendar_calendar_list_insert|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_calendar_calendar_list_insert(*_bf_args, **_bf_kwargs)
_bf_friction_calendar_calendar_list_insert.blobfish_original = _bf_orig_calendar_calendar_list_insert
calendar_calendar_list_insert = _bf_friction_calendar_calendar_list_insert

def calendar_calendars_insert(db_path='state.db', **kwargs):
    '''Creates a secondary calendar. The authenticated user for the request is made the data owner of the new calendar. Note: We recommend to auth… (POST /calendars)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _n = cur.execute('SELECT COALESCE(MAX(rowid), 0) + 100 FROM "calendars"').fetchone()[0] + 1
        _base = datetime.datetime(2026, 1, 5, 9, 0, 0)
        _ts = (_base + datetime.timedelta(minutes=_n)).strftime('%Y-%m-%dT%H:%M:%SZ')
        _cols = ['"id"']
        _vals = ['' + ('%x' % _n).zfill(20) + '']
        if kwargs.get('conference_properties') is not None:
            _cols.append('"conference_properties"')
            _vals.append(json.dumps(kwargs['conference_properties']) if not isinstance(kwargs['conference_properties'], str) else kwargs['conference_properties'])
        if kwargs.get('time_zone') is not None:
            _cols.append('"time_zone"')
            _vals.append(str(kwargs['time_zone']))
        if kwargs.get('kind') is not None:
            _cols.append('"kind"')
            _vals.append(str(kwargs['kind']))
        if kwargs.get('description') is not None:
            _cols.append('"description"')
            _vals.append(str(kwargs['description']))
        if kwargs.get('label_properties') is not None:
            _cols.append('"label_properties"')
            _vals.append(json.dumps(kwargs['label_properties']) if not isinstance(kwargs['label_properties'], str) else kwargs['label_properties'])
        if kwargs.get('data_owner') is not None:
            _cols.append('"data_owner"')
            _vals.append(str(kwargs['data_owner']))
        if kwargs.get('etag') is not None:
            _cols.append('"etag"')
            _vals.append(str(kwargs['etag']))
        if kwargs.get('auto_accept_invitations') is not None:
            _cols.append('"auto_accept_invitations"')
            _vals.append((1 if kwargs['auto_accept_invitations'] in (True, 'true', 1, '1') else 0))
        if kwargs.get('location') is not None:
            _cols.append('"location"')
            _vals.append(str(kwargs['location']))
        if kwargs.get('summary') is not None:
            _cols.append('"summary"')
            _vals.append(str(kwargs['summary']))
        _sql = 'INSERT INTO "calendars" (' + ', '.join(_cols) + ') VALUES (' + ', '.join(['?'] * len(_vals)) + ')'
        try:
            cur.execute(_sql, _vals)
        except sqlite3.IntegrityError:
            conn.rollback()
            return {'error': 'conflict: duplicate key', 'status': 409}
        conn.commit()
        _row = cur.execute('SELECT * FROM "calendars" WHERE "id" = ?', [_vals[0]]).fetchone()
        _out = dict(_row)
        for _jc in ['conference_properties', 'label_properties']:
            if isinstance(_out.get(_jc), str) and _out[_jc][:1] in ('[', '{'):
                try:
                    _out[_jc] = json.loads(_out[_jc])
                except Exception:
                    pass
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_calendar_calendars_insert = calendar_calendars_insert
def _bf_friction_calendar_calendars_insert(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_calendar_calendars_insert(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "calendar_calendars_insert|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_calendar_calendars_insert(*_bf_args, **_bf_kwargs)
_bf_friction_calendar_calendars_insert.blobfish_original = _bf_orig_calendar_calendars_insert
calendar_calendars_insert = _bf_friction_calendar_calendars_insert

