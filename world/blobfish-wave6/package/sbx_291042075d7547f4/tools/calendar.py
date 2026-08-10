"""Executable CALENDAR tool module

Inspect each function: SQLite helpers are local fixtures; network-backed functions call their declared endpoint.
Tools: list_scheduled_runs, query_calendar_events, calendar_calendar_list_list, calendar_acl_list, calendar_calendar_list_get, calendar_calendars_get, calendar_agent, create_scheduled_run, calendar_calendar_list_insert, calendar_calendars_insert, calendar_events_list, calendar_events_get, calendar_events_insert, calendar_events_update, calendar_events_patch, calendar_events_delete, calendar_events_move, calendar_events_quick_add, calendar_events_instances, calendar_freebusy_query, calendar_acl_insert, calendar_acl_delete, calendar_calendars_update, calendar_calendars_delete, calendar_colors_get, calendar_settings_list
Tables: agent_scheduled_runs, agent_events, calendar_lists, acls, calendar_list_entries, calendars, cal_event_details, cal_event_attendees, cal_settings, colors
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

def calendar_events_list(db_path='state.db', **kwargs):
    """Returns events on the specified calendar. (GET /calendars/{calendarId}/events)"""
    _missing = [p for p in ['calendar_id'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib

    def _ts(v):
        if v is None:
            return None
        s = str(v).strip()
        if len(s) == 10:
            s = s + 'T00:00:00+00:00'
        s = s.replace('Z', '+00:00')
        try:
            dt = datetime.datetime.fromisoformat(s)
        except ValueError:
            return None
        if dt.tzinfo is not None:
            dt = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        return dt

    def _iso(dt):
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    def _expand(start_dt, end_dt, rrule, cap=60):
        rule = {}
        for part in str(rrule).split(':', 1)[-1].split(';'):
            if '=' in part:
                k, v = part.split('=', 1)
                rule[k.upper()] = v
        freq = rule.get('FREQ', '').upper()
        if freq not in ('DAILY', 'WEEKLY', 'MONTHLY'):
            return [(start_dt, end_dt)]
        try:
            interval = max(1, int(rule.get('INTERVAL', 1)))
        except ValueError:
            interval = 1
        count = None
        if rule.get('COUNT'):
            try:
                count = int(rule['COUNT'])
            except ValueError:
                count = None
        until = _ts(rule.get('UNTIL', '').replace('T', 'T')[:8] + 'T23:59:59Z') if rule.get('UNTIL') else None
        dur = end_dt - start_dt
        out = []
        i = 0
        while len(out) < cap:
            if freq == 'DAILY':
                s = start_dt + datetime.timedelta(days=i * interval)
            elif freq == 'WEEKLY':
                s = start_dt + datetime.timedelta(weeks=i * interval)
            else:
                m = start_dt.month - 1 + i * interval
                y = start_dt.year + m // 12
                m = m % 12 + 1
                dim = [31, 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
                s = start_dt.replace(year=y, month=m, day=min(start_dt.day, dim))
            if count is not None and i >= count:
                break
            if until is not None and s > until:
                break
            out.append((s, s + dur))
            i += 1
            if count is None and until is None and i >= cap:
                break
        return out

    def _ev_out(row, att_rows, start=None, end=None, inst_id=None):
        d = {
            'kind': 'calendar#event',
            'id': inst_id if inst_id is not None else row['id'],
            'status': row['status'],
            'summary': row['title'],
            'description': row['description'],
            'location': row['location'],
            'color_id': row['color_id'],
            'transparency': row['transparency'],
            'visibility': row['visibility'],
            'organizer': {'email': row['organizer_email']},
            'start': {'date_time': start if start is not None else row['start_datetime'], 'time_zone': row['time_zone']},
            'end': {'date_time': end if end is not None else row['end_datetime'], 'time_zone': row['time_zone']},
            'created': row['created_at'],
            'updated': row['updated'],
            'attendees': [
                {'email': a['email'], 'display_name': a['display_name'], 'response_status': a['response_status'],
                 'optional': bool(a['optional']), 'organizer': bool(a['organizer'])}
                for a in att_rows
            ],
        }
        if row['recurrence']:
            if inst_id is not None:
                d['recurring_event_id'] = row['id']
            else:
                d['recurrence'] = [row['recurrence']]
        return d

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        if cur.execute('SELECT 1 FROM "calendars" WHERE "id" = ?', [str(kwargs['calendar_id'])]).fetchone() is None:
            return {'error': 'calendar not found', 'status': 404}
        rows = cur.execute(
            'SELECT e."id", e."title", e."event_date", e."created_at", d.* FROM "agent_events" e '
            'JOIN "cal_event_details" d ON d."event_id" = e."id" WHERE d."calendar_id" = ? ORDER BY d."start_datetime"',
            [str(kwargs['calendar_id'])]).fetchall()
        show_deleted = bool(kwargs.get('show_deleted'))
        single_events = bool(kwargs.get('single_events'))
        tmin = _ts(kwargs.get('time_min'))
        tmax = _ts(kwargs.get('time_max'))
        q = str(kwargs['q']).lower() if kwargs.get('q') is not None else None
        limit = int(kwargs.get('max_results') or 30)
        items = []
        for row in rows:
            if not show_deleted and row['status'] == 'cancelled':
                continue
            att = cur.execute('SELECT * FROM "cal_event_attendees" WHERE "event_id" = ? ORDER BY "id"', [row['id']]).fetchall()
            if q is not None:
                hay = ' '.join([str(row['title'] or ''), str(row['description'] or ''), str(row['location'] or '')] +
                               [str(a['email'] or '') + ' ' + str(a['display_name'] or '') for a in att]).lower()
                if q not in hay:
                    continue
            s0, e0 = _ts(row['start_datetime']), _ts(row['end_datetime'])
            if row['recurrence'] and single_events:
                for s, e in _expand(s0, e0, row['recurrence']):
                    if tmin is not None and e <= tmin:
                        continue
                    if tmax is not None and s >= tmax:
                        continue
                    items.append(_ev_out(row, att, start=_iso(s), end=_iso(e),
                                         inst_id='%s_%s' % (row['id'], s.strftime('%Y%m%dT%H%M%SZ'))))
            else:
                occs = _expand(s0, e0, row['recurrence']) if row['recurrence'] else [(s0, e0)]
                if tmin is not None and all(e <= tmin for s, e in occs):
                    continue
                if tmax is not None and all(s >= tmax for s, e in occs):
                    continue
                items.append(_ev_out(row, att))
        items = items[:max(1, limit)]
        return {'kind': 'calendar#events', 'items': items, 'count': len(items)}
    finally:
        conn.close()

_env_orig_calendar_events_list = calendar_events_list
def _env_calendar_events_list(db_path='state.db', **kwargs):
    _r = _env_orig_calendar_events_list(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'kind': 'calendar#agent_events', 'items': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'errors': [{'domain': 'global', 'reason': 'notFound', 'message': str(_r.get('error', ''))}], 'code': 404, 'message': str(_r.get('error', ''))}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'errors': [{'domain': 'global', 'reason': 'required', 'message': str(_r.get('error', ''))}], 'code': 400, 'message': str(_r.get('error', ''))}}
    return _r
calendar_events_list = _env_calendar_events_list

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_calendar_events_list = calendar_events_list
def _bf_friction_calendar_events_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_calendar_events_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "calendar_events_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_calendar_events_list(*_bf_args, **_bf_kwargs)
_bf_friction_calendar_events_list.blobfish_original = _bf_orig_calendar_events_list
calendar_events_list = _bf_friction_calendar_events_list

def calendar_events_get(db_path='state.db', **kwargs):
    """Returns an event based on its Google Calendar ID. (GET /calendars/{calendarId}/events/{eventId})"""
    _missing = [p for p in ['calendar_id', 'event_id'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    try:
        _eid = int(kwargs['event_id'])
    except (TypeError, ValueError):
        return {'error': 'invalid event_id: %r' % (kwargs.get('event_id'),), 'status': 400}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        row = cur.execute(
            'SELECT e."id", e."title", e."event_date", e."created_at", d.* FROM "agent_events" e '
            'JOIN "cal_event_details" d ON d."event_id" = e."id" WHERE e."id" = ? AND d."calendar_id" = ?',
            [_eid, str(kwargs['calendar_id'])]).fetchone()
        if row is None:
            return {'error': 'event not found', 'status': 404}
        att = cur.execute('SELECT * FROM "cal_event_attendees" WHERE "event_id" = ? ORDER BY "id"', [_eid]).fetchall()
        out = {
            'kind': 'calendar#event',
            'id': row['id'],
            'status': row['status'],
            'summary': row['title'],
            'description': row['description'],
            'location': row['location'],
            'color_id': row['color_id'],
            'transparency': row['transparency'],
            'visibility': row['visibility'],
            'organizer': {'email': row['organizer_email']},
            'start': {'date_time': row['start_datetime'], 'time_zone': row['time_zone']},
            'end': {'date_time': row['end_datetime'], 'time_zone': row['time_zone']},
            'created': row['created_at'],
            'updated': row['updated'],
            'attendees': [
                {'email': a['email'], 'display_name': a['display_name'], 'response_status': a['response_status'],
                 'optional': bool(a['optional']), 'organizer': bool(a['organizer'])}
                for a in att
            ],
        }
        if row['recurrence']:
            out['recurrence'] = [row['recurrence']]
        return out
    finally:
        conn.close()

_env_orig_calendar_events_get = calendar_events_get
def _env_calendar_events_get(db_path='state.db', **kwargs):
    _r = _env_orig_calendar_events_get(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'kind': 'calendar#agent_events', 'items': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'errors': [{'domain': 'global', 'reason': 'notFound', 'message': str(_r.get('error', ''))}], 'code': 404, 'message': str(_r.get('error', ''))}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'errors': [{'domain': 'global', 'reason': 'required', 'message': str(_r.get('error', ''))}], 'code': 400, 'message': str(_r.get('error', ''))}}
    return _r
calendar_events_get = _env_calendar_events_get

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_calendar_events_get = calendar_events_get
def _bf_friction_calendar_events_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_calendar_events_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "calendar_events_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_calendar_events_get(*_bf_args, **_bf_kwargs)
_bf_friction_calendar_events_get.blobfish_original = _bf_orig_calendar_events_get
calendar_events_get = _bf_friction_calendar_events_get

def calendar_events_insert(db_path='state.db', **kwargs):
    """Creates an event. (POST /calendars/{calendarId}/events)"""
    _missing = [p for p in ['calendar_id', 'start', 'end'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    if kwargs.get('send_updates') is not None and kwargs.get('send_updates') not in ['all', 'externalOnly', 'none']:
        return {'error': 'invalid value for send_updates: %r. Accepted: all, externalOnly, none' % (kwargs.get('send_updates'),),
                'status': 422, 'parameter': 'send_updates', 'accepted': ['all', 'externalOnly', 'none']}

    def _edge(v):
        if isinstance(v, str) and v[:1] in ('{', '['):
            try:
                v = json.loads(v)
            except ValueError:
                pass
        if isinstance(v, dict):
            return v.get('date_time') or v.get('date'), v.get('time_zone')
        return str(v), None

    def _norm(s):
        s = str(s).strip()
        if len(s) == 10:
            return s + 'T00:00:00Z', s
        return s, s[:10]

    start_raw, tz1 = _edge(kwargs['start'])
    end_raw, tz2 = _edge(kwargs['end'])
    if not start_raw or not end_raw:
        return {'error': "invalid start/end: expected an object with 'date_time' (RFC3339) or 'date' (YYYY-MM-DD)", 'status': 400}
    start_dtstr, event_date = _norm(start_raw)
    end_dtstr, _ = _norm(end_raw)
    tz = tz1 or tz2 or 'America/New_York'
    attendees = kwargs.get('attendees')
    if isinstance(attendees, str):
        try:
            attendees = json.loads(attendees)
        except ValueError:
            attendees = [{'email': attendees}]
    if isinstance(attendees, dict):
        attendees = [attendees]
    attendees = attendees or []
    recurrence = kwargs.get('recurrence')
    if isinstance(recurrence, str) and recurrence[:1] == '[':
        try:
            recurrence = json.loads(recurrence)
        except ValueError:
            pass
    if isinstance(recurrence, list):
        recurrence = recurrence[0] if recurrence else None
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        if cur.execute('SELECT 1 FROM "calendars" WHERE "id" = ?', [str(kwargs['calendar_id'])]).fetchone() is None:
            return {'error': 'calendar not found', 'status': 404}
        next_id = max(
            cur.execute('SELECT COALESCE(MAX("id"), 0) FROM "agent_events"').fetchone()[0],
            cur.execute('SELECT COALESCE(MAX("event_id"), 0) FROM "cal_event_details"').fetchone()[0]) + 1
        cur.execute('INSERT INTO "agent_events" ("id", "title", "event_date", "created_at") VALUES (?, ?, ?, ?)',
                    [next_id, kwargs.get('summary') or '(No title)', event_date, now])
        cur.execute(
            'INSERT OR REPLACE INTO "cal_event_details" ("event_id", "calendar_id", "status", "start_datetime", "end_datetime", '
            '"time_zone", "location", "description", "organizer_email", "recurrence", "color_id", "transparency", "visibility", "updated") '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            [next_id, str(kwargs['calendar_id']), 'confirmed', start_dtstr, end_dtstr, tz,
             kwargs.get('location'), kwargs.get('description'), 'contact77709@morganstanleysimulated.com',
             recurrence, kwargs.get('color_id'), kwargs.get('transparency') or 'opaque',
             kwargs.get('visibility') or 'default', now])
        cur.execute('DELETE FROM "cal_event_attendees" WHERE "event_id" = ?', [next_id])
        att_out = []
        for a in attendees:
            if not isinstance(a, dict) or not a.get('email'):
                continue
            aid = cur.execute('SELECT COALESCE(MAX("id"), 0) FROM "cal_event_attendees"').fetchone()[0] + 1
            cur.execute('INSERT INTO "cal_event_attendees" ("id", "event_id", "email", "display_name", "response_status", "optional", "organizer") VALUES (?, ?, ?, ?, ?, ?, ?)',
                        [aid, next_id, str(a['email']), a.get('display_name'), a.get('response_status') or 'needsAction',
                         1 if a.get('optional') else 0, 1 if a.get('organizer') else 0])
            att_out.append({'email': str(a['email']), 'display_name': a.get('display_name'),
                            'response_status': a.get('response_status') or 'needsAction',
                            'optional': bool(a.get('optional')), 'organizer': bool(a.get('organizer'))})
        conn.commit()
        out = {
            'kind': 'calendar#event', 'id': next_id, 'status': 'confirmed',
            'summary': kwargs.get('summary') or '(No title)',
            'description': kwargs.get('description'), 'location': kwargs.get('location'),
            'color_id': kwargs.get('color_id'), 'transparency': kwargs.get('transparency') or 'opaque',
            'visibility': kwargs.get('visibility') or 'default',
            'organizer': {'email': 'contact77709@morganstanleysimulated.com'},
            'start': {'date_time': start_dtstr, 'time_zone': tz},
            'end': {'date_time': end_dtstr, 'time_zone': tz},
            'created': now, 'updated': now, 'attendees': att_out,
        }
        if recurrence:
            out['recurrence'] = [recurrence]
        return out
    finally:
        conn.close()

_env_orig_calendar_events_insert = calendar_events_insert
def _env_calendar_events_insert(db_path='state.db', **kwargs):
    _r = _env_orig_calendar_events_insert(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'kind': 'calendar#agent_events', 'items': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'errors': [{'domain': 'global', 'reason': 'notFound', 'message': str(_r.get('error', ''))}], 'code': 404, 'message': str(_r.get('error', ''))}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'errors': [{'domain': 'global', 'reason': 'required', 'message': str(_r.get('error', ''))}], 'code': 400, 'message': str(_r.get('error', ''))}}
    return _r
calendar_events_insert = _env_calendar_events_insert

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_calendar_events_insert = calendar_events_insert
def _bf_friction_calendar_events_insert(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_calendar_events_insert(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "calendar_events_insert|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_calendar_events_insert(*_bf_args, **_bf_kwargs)
_bf_friction_calendar_events_insert.blobfish_original = _bf_orig_calendar_events_insert
calendar_events_insert = _bf_friction_calendar_events_insert

def calendar_events_update(db_path='state.db', **kwargs):
    """Updates an event; does not support patch semantics — omitted writable fields are cleared. (PUT /calendars/{calendarId}/events/{eventId})"""
    _missing = [p for p in ['calendar_id', 'event_id', 'start', 'end'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    try:
        _eid = int(kwargs['event_id'])
    except (TypeError, ValueError):
        return {'error': 'invalid event_id: %r' % (kwargs.get('event_id'),), 'status': 400}
    if kwargs.get('send_updates') is not None and kwargs.get('send_updates') not in ['all', 'externalOnly', 'none']:
        return {'error': 'invalid value for send_updates: %r. Accepted: all, externalOnly, none' % (kwargs.get('send_updates'),),
                'status': 422, 'parameter': 'send_updates', 'accepted': ['all', 'externalOnly', 'none']}
    if kwargs.get('status') is not None and kwargs.get('status') not in ['confirmed', 'tentative', 'cancelled']:
        return {'error': 'invalid value for status: %r. Accepted: confirmed, tentative, cancelled' % (kwargs.get('status'),),
                'status': 422, 'parameter': 'status', 'accepted': ['confirmed', 'tentative', 'cancelled']}

    def _edge(v):
        if isinstance(v, str) and v[:1] in ('{', '['):
            try:
                v = json.loads(v)
            except ValueError:
                pass
        if isinstance(v, dict):
            return v.get('date_time') or v.get('date'), v.get('time_zone')
        return str(v), None

    def _norm(s):
        s = str(s).strip()
        if len(s) == 10:
            return s + 'T00:00:00Z', s
        return s, s[:10]

    start_raw, tz1 = _edge(kwargs['start'])
    end_raw, tz2 = _edge(kwargs['end'])
    if not start_raw or not end_raw:
        return {'error': "invalid start/end: expected an object with 'date_time' (RFC3339) or 'date' (YYYY-MM-DD)", 'status': 400}
    start_dtstr, event_date = _norm(start_raw)
    end_dtstr, _ = _norm(end_raw)
    attendees = kwargs.get('attendees')
    if isinstance(attendees, str):
        try:
            attendees = json.loads(attendees)
        except ValueError:
            attendees = [{'email': attendees}]
    if isinstance(attendees, dict):
        attendees = [attendees]
    attendees = attendees or []
    recurrence = kwargs.get('recurrence')
    if isinstance(recurrence, str) and recurrence[:1] == '[':
        try:
            recurrence = json.loads(recurrence)
        except ValueError:
            pass
    if isinstance(recurrence, list):
        recurrence = recurrence[0] if recurrence else None
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        row = cur.execute('SELECT * FROM "cal_event_details" WHERE "event_id" = ? AND "calendar_id" = ?',
                          [_eid, str(kwargs['calendar_id'])]).fetchone()
        if row is None:
            return {'error': 'event not found', 'status': 404}
        tz = tz1 or tz2 or row['time_zone']
        cur.execute('UPDATE "agent_events" SET "title" = ?, "event_date" = ? WHERE "id" = ?',
                    [kwargs.get('summary') or '(No title)', event_date, _eid])
        cur.execute(
            'UPDATE "cal_event_details" SET "status" = ?, "start_datetime" = ?, "end_datetime" = ?, "time_zone" = ?, '
            '"location" = ?, "description" = ?, "recurrence" = ?, "color_id" = ?, "transparency" = ?, "visibility" = ?, "updated" = ? '
            'WHERE "event_id" = ?',
            [kwargs.get('status') or 'confirmed', start_dtstr, end_dtstr, tz,
             kwargs.get('location'), kwargs.get('description'), recurrence, kwargs.get('color_id'),
             kwargs.get('transparency') or 'opaque', kwargs.get('visibility') or 'default', now, _eid])
        cur.execute('DELETE FROM "cal_event_attendees" WHERE "event_id" = ?', [_eid])
        att_out = []
        for a in attendees:
            if not isinstance(a, dict) or not a.get('email'):
                continue
            aid = cur.execute('SELECT COALESCE(MAX("id"), 0) FROM "cal_event_attendees"').fetchone()[0] + 1
            cur.execute('INSERT INTO "cal_event_attendees" ("id", "event_id", "email", "display_name", "response_status", "optional", "organizer") VALUES (?, ?, ?, ?, ?, ?, ?)',
                        [aid, _eid, str(a['email']), a.get('display_name'), a.get('response_status') or 'needsAction',
                         1 if a.get('optional') else 0, 1 if a.get('organizer') else 0])
            att_out.append({'email': str(a['email']), 'display_name': a.get('display_name'),
                            'response_status': a.get('response_status') or 'needsAction',
                            'optional': bool(a.get('optional')), 'organizer': bool(a.get('organizer'))})
        conn.commit()
        out = {
            'kind': 'calendar#event', 'id': _eid, 'status': kwargs.get('status') or 'confirmed',
            'summary': kwargs.get('summary') or '(No title)',
            'description': kwargs.get('description'), 'location': kwargs.get('location'),
            'color_id': kwargs.get('color_id'), 'transparency': kwargs.get('transparency') or 'opaque',
            'visibility': kwargs.get('visibility') or 'default',
            'organizer': {'email': row['organizer_email']},
            'start': {'date_time': start_dtstr, 'time_zone': tz},
            'end': {'date_time': end_dtstr, 'time_zone': tz},
            'updated': now, 'attendees': att_out,
        }
        if recurrence:
            out['recurrence'] = [recurrence]
        return out
    finally:
        conn.close()

_env_orig_calendar_events_update = calendar_events_update
def _env_calendar_events_update(db_path='state.db', **kwargs):
    _r = _env_orig_calendar_events_update(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'kind': 'calendar#agent_events', 'items': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'errors': [{'domain': 'global', 'reason': 'notFound', 'message': str(_r.get('error', ''))}], 'code': 404, 'message': str(_r.get('error', ''))}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'errors': [{'domain': 'global', 'reason': 'required', 'message': str(_r.get('error', ''))}], 'code': 400, 'message': str(_r.get('error', ''))}}
    return _r
calendar_events_update = _env_calendar_events_update

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_calendar_events_update = calendar_events_update
def _bf_friction_calendar_events_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_calendar_events_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "calendar_events_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_calendar_events_update(*_bf_args, **_bf_kwargs)
_bf_friction_calendar_events_update.blobfish_original = _bf_orig_calendar_events_update
calendar_events_update = _bf_friction_calendar_events_update

def calendar_events_patch(db_path='state.db', **kwargs):
    """Updates an event; supports patch semantics — only the fields provided are changed. (PATCH /calendars/{calendarId}/events/{eventId})"""
    _missing = [p for p in ['calendar_id', 'event_id'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    try:
        _eid = int(kwargs['event_id'])
    except (TypeError, ValueError):
        return {'error': 'invalid event_id: %r' % (kwargs.get('event_id'),), 'status': 400}
    if kwargs.get('send_updates') is not None and kwargs.get('send_updates') not in ['all', 'externalOnly', 'none']:
        return {'error': 'invalid value for send_updates: %r. Accepted: all, externalOnly, none' % (kwargs.get('send_updates'),),
                'status': 422, 'parameter': 'send_updates', 'accepted': ['all', 'externalOnly', 'none']}
    if kwargs.get('status') is not None and kwargs.get('status') not in ['confirmed', 'tentative', 'cancelled']:
        return {'error': 'invalid value for status: %r. Accepted: confirmed, tentative, cancelled' % (kwargs.get('status'),),
                'status': 422, 'parameter': 'status', 'accepted': ['confirmed', 'tentative', 'cancelled']}

    def _edge(v):
        if isinstance(v, str) and v[:1] in ('{', '['):
            try:
                v = json.loads(v)
            except ValueError:
                pass
        if isinstance(v, dict):
            return v.get('date_time') or v.get('date'), v.get('time_zone')
        return str(v), None

    def _norm(s):
        s = str(s).strip()
        if len(s) == 10:
            return s + 'T00:00:00Z', s
        return s, s[:10]

    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        row = cur.execute('SELECT * FROM "cal_event_details" WHERE "event_id" = ? AND "calendar_id" = ?',
                          [_eid, str(kwargs['calendar_id'])]).fetchone()
        if row is None:
            return {'error': 'event not found', 'status': 404}
        if kwargs.get('summary') is not None:
            cur.execute('UPDATE "agent_events" SET "title" = ? WHERE "id" = ?', [str(kwargs['summary']), _eid])
        det_sets, det_args = [], []
        if kwargs.get('start') is not None:
            start_raw, tz1 = _edge(kwargs['start'])
            if not start_raw:
                return {'error': "invalid start: expected an object with 'date_time' (RFC3339) or 'date' (YYYY-MM-DD)", 'status': 400}
            start_dtstr, event_date = _norm(start_raw)
            det_sets.append('"start_datetime" = ?'); det_args.append(start_dtstr)
            if tz1:
                det_sets.append('"time_zone" = ?'); det_args.append(tz1)
            cur.execute('UPDATE "agent_events" SET "event_date" = ? WHERE "id" = ?', [event_date, _eid])
        if kwargs.get('end') is not None:
            end_raw, tz2 = _edge(kwargs['end'])
            if not end_raw:
                return {'error': "invalid end: expected an object with 'date_time' (RFC3339) or 'date' (YYYY-MM-DD)", 'status': 400}
            end_dtstr, _ = _norm(end_raw)
            det_sets.append('"end_datetime" = ?'); det_args.append(end_dtstr)
        for param, col in [('description', 'description'), ('location', 'location'), ('status', 'status'),
                           ('color_id', 'color_id'), ('transparency', 'transparency'), ('visibility', 'visibility')]:
            if kwargs.get(param) is not None:
                det_sets.append('"%s" = ?' % col); det_args.append(str(kwargs[param]))
        recurrence = kwargs.get('recurrence')
        if recurrence is not None:
            if isinstance(recurrence, str) and recurrence[:1] == '[':
                try:
                    recurrence = json.loads(recurrence)
                except ValueError:
                    pass
            if isinstance(recurrence, list):
                recurrence = recurrence[0] if recurrence else None
            det_sets.append('"recurrence" = ?'); det_args.append(recurrence)
        det_sets.append('"updated" = ?'); det_args.append(now)
        cur.execute('UPDATE "cal_event_details" SET ' + ', '.join(det_sets) + ' WHERE "event_id" = ?', det_args + [_eid])
        attendees = kwargs.get('attendees')
        if attendees is not None:
            if isinstance(attendees, str):
                try:
                    attendees = json.loads(attendees)
                except ValueError:
                    attendees = [{'email': attendees}]
            if isinstance(attendees, dict):
                attendees = [attendees]
            cur.execute('DELETE FROM "cal_event_attendees" WHERE "event_id" = ?', [_eid])
            for a in attendees or []:
                if not isinstance(a, dict) or not a.get('email'):
                    continue
                aid = cur.execute('SELECT COALESCE(MAX("id"), 0) FROM "cal_event_attendees"').fetchone()[0] + 1
                cur.execute('INSERT INTO "cal_event_attendees" ("id", "event_id", "email", "display_name", "response_status", "optional", "organizer") VALUES (?, ?, ?, ?, ?, ?, ?)',
                            [aid, _eid, str(a['email']), a.get('display_name'), a.get('response_status') or 'needsAction',
                             1 if a.get('optional') else 0, 1 if a.get('organizer') else 0])
        conn.commit()
        row = cur.execute(
            'SELECT e."id", e."title", e."event_date", e."created_at", d.* FROM "agent_events" e '
            'JOIN "cal_event_details" d ON d."event_id" = e."id" WHERE e."id" = ?', [_eid]).fetchone()
        att = cur.execute('SELECT * FROM "cal_event_attendees" WHERE "event_id" = ? ORDER BY "id"', [_eid]).fetchall()
        out = {
            'kind': 'calendar#event', 'id': row['id'], 'status': row['status'], 'summary': row['title'],
            'description': row['description'], 'location': row['location'], 'color_id': row['color_id'],
            'transparency': row['transparency'], 'visibility': row['visibility'],
            'organizer': {'email': row['organizer_email']},
            'start': {'date_time': row['start_datetime'], 'time_zone': row['time_zone']},
            'end': {'date_time': row['end_datetime'], 'time_zone': row['time_zone']},
            'created': row['created_at'], 'updated': row['updated'],
            'attendees': [
                {'email': a['email'], 'display_name': a['display_name'], 'response_status': a['response_status'],
                 'optional': bool(a['optional']), 'organizer': bool(a['organizer'])}
                for a in att
            ],
        }
        if row['recurrence']:
            out['recurrence'] = [row['recurrence']]
        return out
    finally:
        conn.close()

_env_orig_calendar_events_patch = calendar_events_patch
def _env_calendar_events_patch(db_path='state.db', **kwargs):
    _r = _env_orig_calendar_events_patch(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'kind': 'calendar#agent_events', 'items': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'errors': [{'domain': 'global', 'reason': 'notFound', 'message': str(_r.get('error', ''))}], 'code': 404, 'message': str(_r.get('error', ''))}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'errors': [{'domain': 'global', 'reason': 'required', 'message': str(_r.get('error', ''))}], 'code': 400, 'message': str(_r.get('error', ''))}}
    return _r
calendar_events_patch = _env_calendar_events_patch

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_calendar_events_patch = calendar_events_patch
def _bf_friction_calendar_events_patch(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_calendar_events_patch(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "calendar_events_patch|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_calendar_events_patch(*_bf_args, **_bf_kwargs)
_bf_friction_calendar_events_patch.blobfish_original = _bf_orig_calendar_events_patch
calendar_events_patch = _bf_friction_calendar_events_patch

def calendar_events_delete(db_path='state.db', **kwargs):
    '''Deletes an event. (DELETE /calendars/{calendarId}/events/{eventId})'''
    _missing = [p for p in ['event_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'errors': [{'domain': 'global', 'reason': 'required', 'message': str(_r.get('error', ''))}], 'code': 400, 'message': str(_r.get('error', ''))}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "agent_events" WHERE "id" = ?', [str(kwargs['event_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'agent_event not found', 'status': 404}
            return {'error': {'errors': [{'domain': 'global', 'reason': 'notFound', 'message': str(_r.get('error', ''))}], 'code': 404, 'message': str(_r.get('error', ''))}}
        cur.execute('DELETE FROM "agent_events" WHERE "id" = ?', [str(kwargs['event_id'])])
        conn.commit()
        _r = {'deleted': True, 'id': str(kwargs['event_id'])}
        return {}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_calendar_events_delete = calendar_events_delete
def _bf_friction_calendar_events_delete(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_calendar_events_delete(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "calendar_events_delete|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_calendar_events_delete(*_bf_args, **_bf_kwargs)
_bf_friction_calendar_events_delete.blobfish_original = _bf_orig_calendar_events_delete
calendar_events_delete = _bf_friction_calendar_events_delete

def calendar_events_move(db_path='state.db', **kwargs):
    """Moves an event to another calendar, i.e. changes an event's organizer calendar. (POST /calendars/{calendarId}/events/{eventId}/move)"""
    _missing = [p for p in ['calendar_id', 'event_id', 'destination'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    try:
        _eid = int(kwargs['event_id'])
    except (TypeError, ValueError):
        return {'error': 'invalid event_id: %r' % (kwargs.get('event_id'),), 'status': 400}
    if kwargs.get('send_updates') is not None and kwargs.get('send_updates') not in ['all', 'externalOnly', 'none']:
        return {'error': 'invalid value for send_updates: %r. Accepted: all, externalOnly, none' % (kwargs.get('send_updates'),),
                'status': 422, 'parameter': 'send_updates', 'accepted': ['all', 'externalOnly', 'none']}
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        row = cur.execute('SELECT * FROM "cal_event_details" WHERE "event_id" = ? AND "calendar_id" = ?',
                          [_eid, str(kwargs['calendar_id'])]).fetchone()
        if row is None:
            return {'error': 'event not found', 'status': 404}
        if cur.execute('SELECT 1 FROM "calendars" WHERE "id" = ?', [str(kwargs['destination'])]).fetchone() is None:
            return {'error': 'destination calendar not found', 'status': 404}
        cur.execute('UPDATE "cal_event_details" SET "calendar_id" = ?, "updated" = ? WHERE "event_id" = ?',
                    [str(kwargs['destination']), now, _eid])
        conn.commit()
        ev = cur.execute(
            'SELECT e."id", e."title", e."event_date", d.* FROM "agent_events" e '
            'JOIN "cal_event_details" d ON d."event_id" = e."id" WHERE e."id" = ?', [_eid]).fetchone()
        return {
            'kind': 'calendar#event', 'id': ev['id'], 'status': ev['status'], 'summary': ev['title'],
            'calendar_id': ev['calendar_id'],
            'organizer': {'email': ev['organizer_email']},
            'start': {'date_time': ev['start_datetime'], 'time_zone': ev['time_zone']},
            'end': {'date_time': ev['end_datetime'], 'time_zone': ev['time_zone']},
            'updated': ev['updated'],
        }
    finally:
        conn.close()

_env_orig_calendar_events_move = calendar_events_move
def _env_calendar_events_move(db_path='state.db', **kwargs):
    _r = _env_orig_calendar_events_move(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'kind': 'calendar#event_details', 'items': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'errors': [{'domain': 'global', 'reason': 'notFound', 'message': str(_r.get('error', ''))}], 'code': 404, 'message': str(_r.get('error', ''))}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'errors': [{'domain': 'global', 'reason': 'required', 'message': str(_r.get('error', ''))}], 'code': 400, 'message': str(_r.get('error', ''))}}
    return _r
calendar_events_move = _env_calendar_events_move

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_calendar_events_move = calendar_events_move
def _bf_friction_calendar_events_move(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_calendar_events_move(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "calendar_events_move|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_calendar_events_move(*_bf_args, **_bf_kwargs)
_bf_friction_calendar_events_move.blobfish_original = _bf_orig_calendar_events_move
calendar_events_move = _bf_friction_calendar_events_move

def calendar_events_quick_add(db_path='state.db', **kwargs):
    """Creates an event based on a simple text string, parsing out an ISO date (YYYY-MM-DD), a time (HH:MM), and 'today'/'tomorrow'. (POST /calendars/{calendarId}/events/quickAdd)"""
    _missing = [p for p in ['calendar_id', 'text'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    if kwargs.get('send_updates') is not None and kwargs.get('send_updates') not in ['all', 'externalOnly', 'none']:
        return {'error': 'invalid value for send_updates: %r. Accepted: all, externalOnly, none' % (kwargs.get('send_updates'),),
                'status': 422, 'parameter': 'send_updates', 'accepted': ['all', 'externalOnly', 'none']}
    text = str(kwargs['text']).strip()
    if not text:
        return {'error': 'text must be a non-empty string', 'status': 400}
    today = datetime.date(2026, 1, 15)
    date_val, time_val, title_tokens = None, None, []
    for tok in text.split():
        bare = tok.strip('.,;()')
        parsed = False
        if date_val is None:
            try:
                date_val = datetime.datetime.strptime(bare, '%Y-%m-%d').date()
                parsed = True
            except ValueError:
                if bare.lower() == 'today':
                    date_val = today
                    parsed = True
                elif bare.lower() == 'tomorrow':
                    date_val = today + datetime.timedelta(days=1)
                    parsed = True
        if not parsed and time_val is None:
            for fmt in ('%H:%M', '%I:%M%p', '%I%p'):
                try:
                    time_val = datetime.datetime.strptime(bare.lower(), fmt.lower() if '%p' in fmt else fmt).time()
                    parsed = True
                    break
                except ValueError:
                    continue
        if not parsed:
            title_tokens.append(tok)
    while title_tokens and title_tokens[-1].lower().strip('.,;') in ('on', 'at', 'from'):
        title_tokens.pop()
    title = ' '.join(title_tokens).strip() or text
    if date_val is None:
        date_val = today
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        if cur.execute('SELECT 1 FROM "calendars" WHERE "id" = ?', [str(kwargs['calendar_id'])]).fetchone() is None:
            return {'error': 'calendar not found', 'status': 404}
        try:
            default_len = int((cur.execute('SELECT "value" FROM "cal_settings" WHERE "id" = ?', ['defaultEventLength']).fetchone() or ['30'])[0])
        except (ValueError, TypeError):
            default_len = 30
        start_dt = datetime.datetime.combine(date_val, time_val or datetime.time(9, 0))
        end_dt = start_dt + datetime.timedelta(minutes=default_len)
        start_s = start_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_s = end_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        next_id = max(
            cur.execute('SELECT COALESCE(MAX("id"), 0) FROM "agent_events"').fetchone()[0],
            cur.execute('SELECT COALESCE(MAX("event_id"), 0) FROM "cal_event_details"').fetchone()[0]) + 1
        cur.execute('INSERT INTO "agent_events" ("id", "title", "event_date", "created_at") VALUES (?, ?, ?, ?)',
                    [next_id, title, date_val.strftime('%Y-%m-%d'), now])
        cur.execute(
            'INSERT OR REPLACE INTO "cal_event_details" ("event_id", "calendar_id", "status", "start_datetime", "end_datetime", '
            '"time_zone", "location", "description", "organizer_email", "recurrence", "color_id", "transparency", "visibility", "updated") '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            [next_id, str(kwargs['calendar_id']), 'confirmed', start_s, end_s, 'America/New_York',
             None, None, 'contact77709@morganstanleysimulated.com', None, None, 'opaque', 'default', now])
        conn.commit()
        return {
            'kind': 'calendar#event', 'id': next_id, 'status': 'confirmed', 'summary': title,
            'start': {'date_time': start_s, 'time_zone': 'America/New_York'},
            'end': {'date_time': end_s, 'time_zone': 'America/New_York'},
            'organizer': {'email': 'contact77709@morganstanleysimulated.com'},
            'created': now, 'updated': now,
        }
    finally:
        conn.close()

_env_orig_calendar_events_quick_add = calendar_events_quick_add
def _env_calendar_events_quick_add(db_path='state.db', **kwargs):
    _r = _env_orig_calendar_events_quick_add(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'kind': 'calendar#agent_events', 'items': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'errors': [{'domain': 'global', 'reason': 'notFound', 'message': str(_r.get('error', ''))}], 'code': 404, 'message': str(_r.get('error', ''))}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'errors': [{'domain': 'global', 'reason': 'required', 'message': str(_r.get('error', ''))}], 'code': 400, 'message': str(_r.get('error', ''))}}
    return _r
calendar_events_quick_add = _env_calendar_events_quick_add

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_calendar_events_quick_add = calendar_events_quick_add
def _bf_friction_calendar_events_quick_add(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_calendar_events_quick_add(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "calendar_events_quick_add|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_calendar_events_quick_add(*_bf_args, **_bf_kwargs)
_bf_friction_calendar_events_quick_add.blobfish_original = _bf_orig_calendar_events_quick_add
calendar_events_quick_add = _bf_friction_calendar_events_quick_add

def calendar_events_instances(db_path='state.db', **kwargs):
    """Returns instances of the specified recurring event. (GET /calendars/{calendarId}/events/{eventId}/instances)"""
    _missing = [p for p in ['calendar_id', 'event_id'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    try:
        _eid = int(kwargs['event_id'])
    except (TypeError, ValueError):
        return {'error': 'invalid event_id: %r' % (kwargs.get('event_id'),), 'status': 400}

    def _ts(v):
        if v is None:
            return None
        s = str(v).strip()
        if len(s) == 10:
            s = s + 'T00:00:00+00:00'
        s = s.replace('Z', '+00:00')
        try:
            dt = datetime.datetime.fromisoformat(s)
        except ValueError:
            return None
        if dt.tzinfo is not None:
            dt = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        return dt

    def _iso(dt):
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    def _expand(start_dt, end_dt, rrule, cap=60):
        rule = {}
        for part in str(rrule).split(':', 1)[-1].split(';'):
            if '=' in part:
                k, v = part.split('=', 1)
                rule[k.upper()] = v
        freq = rule.get('FREQ', '').upper()
        if freq not in ('DAILY', 'WEEKLY', 'MONTHLY'):
            return [(start_dt, end_dt)]
        try:
            interval = max(1, int(rule.get('INTERVAL', 1)))
        except ValueError:
            interval = 1
        count = None
        if rule.get('COUNT'):
            try:
                count = int(rule['COUNT'])
            except ValueError:
                count = None
        until = _ts(rule['UNTIL'][:8] + 'T23:59:59Z') if rule.get('UNTIL') else None
        dur = end_dt - start_dt
        out = []
        i = 0
        while len(out) < cap:
            if freq == 'DAILY':
                s = start_dt + datetime.timedelta(days=i * interval)
            elif freq == 'WEEKLY':
                s = start_dt + datetime.timedelta(weeks=i * interval)
            else:
                m = start_dt.month - 1 + i * interval
                y = start_dt.year + m // 12
                m = m % 12 + 1
                dim = [31, 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
                s = start_dt.replace(year=y, month=m, day=min(start_dt.day, dim))
            if count is not None and i >= count:
                break
            if until is not None and s > until:
                break
            out.append((s, s + dur))
            i += 1
            if count is None and until is None and i >= cap:
                break
        return out

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        row = cur.execute(
            'SELECT e."id", e."title", e."created_at", d.* FROM "agent_events" e '
            'JOIN "cal_event_details" d ON d."event_id" = e."id" WHERE e."id" = ? AND d."calendar_id" = ?',
            [_eid, str(kwargs['calendar_id'])]).fetchone()
        if row is None:
            return {'error': 'event not found', 'status': 404}
        s0, e0 = _ts(row['start_datetime']), _ts(row['end_datetime'])
        occs = _expand(s0, e0, row['recurrence']) if row['recurrence'] else [(s0, e0)]
        tmin = _ts(kwargs.get('time_min'))
        tmax = _ts(kwargs.get('time_max'))
        limit = int(kwargs.get('max_results') or 30)
        items = []
        for s, e in occs:
            if tmin is not None and e <= tmin:
                continue
            if tmax is not None and s >= tmax:
                continue
            items.append({
                'kind': 'calendar#event',
                'id': '%s_%s' % (row['id'], s.strftime('%Y%m%dT%H%M%SZ')),
                'recurring_event_id': row['id'],
                'status': row['status'], 'summary': row['title'],
                'location': row['location'], 'description': row['description'],
                'organizer': {'email': row['organizer_email']},
                'start': {'date_time': _iso(s), 'time_zone': row['time_zone']},
                'end': {'date_time': _iso(e), 'time_zone': row['time_zone']},
            })
            if len(items) >= max(1, limit):
                break
        return {'kind': 'calendar#events', 'items': items, 'count': len(items)}
    finally:
        conn.close()

_env_orig_calendar_events_instances = calendar_events_instances
def _env_calendar_events_instances(db_path='state.db', **kwargs):
    _r = _env_orig_calendar_events_instances(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'kind': 'calendar#agent_events', 'items': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'errors': [{'domain': 'global', 'reason': 'notFound', 'message': str(_r.get('error', ''))}], 'code': 404, 'message': str(_r.get('error', ''))}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'errors': [{'domain': 'global', 'reason': 'required', 'message': str(_r.get('error', ''))}], 'code': 400, 'message': str(_r.get('error', ''))}}
    return _r
calendar_events_instances = _env_calendar_events_instances

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_calendar_events_instances = calendar_events_instances
def _bf_friction_calendar_events_instances(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_calendar_events_instances(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "calendar_events_instances|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_calendar_events_instances(*_bf_args, **_bf_kwargs)
_bf_friction_calendar_events_instances.blobfish_original = _bf_orig_calendar_events_instances
calendar_events_instances = _bf_friction_calendar_events_instances

def calendar_freebusy_query(db_path='state.db', **kwargs):
    """Returns free/busy information for a set of calendars. (POST /freeBusy)"""
    _missing = [p for p in ['time_min', 'time_max', 'items'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib

    def _ts(v):
        if v is None:
            return None
        s = str(v).strip()
        if len(s) == 10:
            s = s + 'T00:00:00+00:00'
        s = s.replace('Z', '+00:00')
        try:
            dt = datetime.datetime.fromisoformat(s)
        except ValueError:
            return None
        if dt.tzinfo is not None:
            dt = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        return dt

    def _iso(dt):
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    def _expand(start_dt, end_dt, rrule, cap=60):
        rule = {}
        for part in str(rrule).split(':', 1)[-1].split(';'):
            if '=' in part:
                k, v = part.split('=', 1)
                rule[k.upper()] = v
        freq = rule.get('FREQ', '').upper()
        if freq not in ('DAILY', 'WEEKLY', 'MONTHLY'):
            return [(start_dt, end_dt)]
        try:
            interval = max(1, int(rule.get('INTERVAL', 1)))
        except ValueError:
            interval = 1
        count = None
        if rule.get('COUNT'):
            try:
                count = int(rule['COUNT'])
            except ValueError:
                count = None
        until = _ts(rule['UNTIL'][:8] + 'T23:59:59Z') if rule.get('UNTIL') else None
        dur = end_dt - start_dt
        out = []
        i = 0
        while len(out) < cap:
            if freq == 'DAILY':
                s = start_dt + datetime.timedelta(days=i * interval)
            elif freq == 'WEEKLY':
                s = start_dt + datetime.timedelta(weeks=i * interval)
            else:
                m = start_dt.month - 1 + i * interval
                y = start_dt.year + m // 12
                m = m % 12 + 1
                dim = [31, 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
                s = start_dt.replace(year=y, month=m, day=min(start_dt.day, dim))
            if count is not None and i >= count:
                break
            if until is not None and s > until:
                break
            out.append((s, s + dur))
            i += 1
            if count is None and until is None and i >= cap:
                break
        return out

    tmin = _ts(kwargs['time_min'])
    tmax = _ts(kwargs['time_max'])
    if tmin is None or tmax is None:
        return {'error': 'time_min and time_max must be RFC3339 timestamps, e.g. 2026-01-19T00:00:00Z', 'status': 400}
    items = kwargs['items']
    if isinstance(items, str):
        try:
            items = json.loads(items)
        except ValueError:
            items = [{'id': items}]
    if isinstance(items, dict):
        items = [items]
    cal_ids = []
    for it in items or []:
        if isinstance(it, dict) and it.get('id') is not None:
            cal_ids.append(str(it['id']))
        elif isinstance(it, str):
            cal_ids.append(it)
    if not cal_ids:
        return {'error': "items must be a list of calendar objects with an 'id' field", 'status': 400}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        calendars = {}
        for cal_id in cal_ids:
            if cur.execute('SELECT 1 FROM "calendars" WHERE "id" = ?', [cal_id]).fetchone() is None:
                calendars[cal_id] = {'errors': [{'domain': 'global', 'reason': 'notFound'}]}
                continue
            busy = []
            rows = cur.execute(
                'SELECT d.* FROM "cal_event_details" d JOIN "agent_events" e ON e."id" = d."event_id" '
                'WHERE d."calendar_id" = ? AND d."status" != ? AND d."transparency" != ?',
                [cal_id, 'cancelled', 'transparent']).fetchall()
            for row in rows:
                s0, e0 = _ts(row['start_datetime']), _ts(row['end_datetime'])
                if s0 is None or e0 is None:
                    continue
                occs = _expand(s0, e0, row['recurrence']) if row['recurrence'] else [(s0, e0)]
                for s, e in occs:
                    if e <= tmin or s >= tmax:
                        continue
                    busy.append({'start': _iso(s), 'end': _iso(e)})
            busy.sort(key=lambda b: b['start'])
            calendars[cal_id] = {'busy': busy}
        return {'kind': 'calendar#freeBusy', 'time_min': str(kwargs['time_min']),
                'time_max': str(kwargs['time_max']), 'calendars': calendars}
    finally:
        conn.close()

_env_orig_calendar_freebusy_query = calendar_freebusy_query
def _env_calendar_freebusy_query(db_path='state.db', **kwargs):
    _r = _env_orig_calendar_freebusy_query(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'kind': 'calendar#event_details', 'items': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'errors': [{'domain': 'global', 'reason': 'notFound', 'message': str(_r.get('error', ''))}], 'code': 404, 'message': str(_r.get('error', ''))}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'errors': [{'domain': 'global', 'reason': 'required', 'message': str(_r.get('error', ''))}], 'code': 400, 'message': str(_r.get('error', ''))}}
    return _r
calendar_freebusy_query = _env_calendar_freebusy_query

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_calendar_freebusy_query = calendar_freebusy_query
def _bf_friction_calendar_freebusy_query(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_calendar_freebusy_query(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "calendar_freebusy_query|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_calendar_freebusy_query(*_bf_args, **_bf_kwargs)
_bf_friction_calendar_freebusy_query.blobfish_original = _bf_orig_calendar_freebusy_query
calendar_freebusy_query = _bf_friction_calendar_freebusy_query

def calendar_acl_insert(db_path='state.db', **kwargs):
    """Creates an access control rule on a calendar's ACL collection. (POST /calendars/{calendarId}/acl)"""
    _missing = [p for p in ['calendar_id', 'role', 'scope'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    _roles = ['none', 'freeBusyReader', 'reader', 'writer', 'owner']
    if kwargs['role'] not in _roles:
        return {'error': 'invalid value for role: %r. Accepted: %s' % (kwargs['role'], ', '.join(_roles)),
                'status': 422, 'parameter': 'role', 'accepted': _roles}
    scope = kwargs['scope']
    if isinstance(scope, str):
        try:
            scope = json.loads(scope)
        except ValueError:
            scope = {'type': 'user', 'value': scope}
    if not isinstance(scope, dict) or scope.get('type') not in ['default', 'user', 'group', 'domain']:
        return {'error': "invalid scope: expected an object with 'type' in default, user, group, domain and (except for 'default') a 'value'",
                'status': 422, 'parameter': 'scope', 'accepted_types': ['default', 'user', 'group', 'domain']}
    if scope.get('type') != 'default' and not scope.get('value'):
        return {'error': "scope.value is required for scope type %r" % (scope.get('type'),), 'status': 422, 'parameter': 'scope'}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        row = cur.execute('SELECT * FROM "acls" WHERE "id" = ?', [str(kwargs['calendar_id'])]).fetchone()
        if row is None:
            return {'error': 'calendar acl collection not found', 'status': 404}
        try:
            rules = json.loads(row['items']) if row['items'] else []
        except ValueError:
            rules = []
        if not isinstance(rules, list):
            rules = []
        rule_id = scope['type'] if scope['type'] == 'default' else '%s:%s' % (scope['type'], scope['value'])
        etag = hashlib.sha256(('%s|%s|%s' % (kwargs['calendar_id'], rule_id, kwargs['role'])).encode('utf-8')).hexdigest()[:12]
        rule = {'kind': 'calendar#aclRule', 'id': rule_id, 'etag': etag, 'role': kwargs['role'],
                'scope': {'type': scope['type'], 'value': scope.get('value')}}
        rules = [r for r in rules if not (isinstance(r, dict) and r.get('id') == rule_id)]
        rules.append(rule)
        cur.execute('UPDATE "acls" SET "items" = ? WHERE "id" = ?', [json.dumps(rules), str(kwargs['calendar_id'])])
        conn.commit()
        return rule
    finally:
        conn.close()

_env_orig_calendar_acl_insert = calendar_acl_insert
def _env_calendar_acl_insert(db_path='state.db', **kwargs):
    _r = _env_orig_calendar_acl_insert(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'kind': 'calendar#acls', 'items': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'errors': [{'domain': 'global', 'reason': 'notFound', 'message': str(_r.get('error', ''))}], 'code': 404, 'message': str(_r.get('error', ''))}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'errors': [{'domain': 'global', 'reason': 'required', 'message': str(_r.get('error', ''))}], 'code': 400, 'message': str(_r.get('error', ''))}}
    return _r
calendar_acl_insert = _env_calendar_acl_insert

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_calendar_acl_insert = calendar_acl_insert
def _bf_friction_calendar_acl_insert(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_calendar_acl_insert(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "calendar_acl_insert|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_calendar_acl_insert(*_bf_args, **_bf_kwargs)
_bf_friction_calendar_acl_insert.blobfish_original = _bf_orig_calendar_acl_insert
calendar_acl_insert = _bf_friction_calendar_acl_insert

def calendar_acl_delete(db_path='state.db', **kwargs):
    """Deletes an access control rule from a calendar's ACL collection. (DELETE /calendars/{calendarId}/acl/{ruleId})"""
    _missing = [p for p in ['calendar_id', 'rule_id'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        row = cur.execute('SELECT * FROM "acls" WHERE "id" = ?', [str(kwargs['calendar_id'])]).fetchone()
        if row is None:
            return {'error': 'calendar acl collection not found', 'status': 404}
        try:
            rules = json.loads(row['items']) if row['items'] else []
        except ValueError:
            rules = []
        if not isinstance(rules, list):
            rules = []
        kept = [r for r in rules if not (isinstance(r, dict) and r.get('id') == str(kwargs['rule_id']))]
        if len(kept) == len(rules):
            return {'error': 'acl rule not found', 'status': 404}
        cur.execute('UPDATE "acls" SET "items" = ? WHERE "id" = ?', [json.dumps(kept), str(kwargs['calendar_id'])])
        conn.commit()
        return {'success': True, 'deleted': str(kwargs['rule_id']), 'calendar_id': str(kwargs['calendar_id'])}
    finally:
        conn.close()

_env_orig_calendar_acl_delete = calendar_acl_delete
def _env_calendar_acl_delete(db_path='state.db', **kwargs):
    _r = _env_orig_calendar_acl_delete(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'kind': 'calendar#acls', 'items': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'errors': [{'domain': 'global', 'reason': 'notFound', 'message': str(_r.get('error', ''))}], 'code': 404, 'message': str(_r.get('error', ''))}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'errors': [{'domain': 'global', 'reason': 'required', 'message': str(_r.get('error', ''))}], 'code': 400, 'message': str(_r.get('error', ''))}}
    return _r
calendar_acl_delete = _env_calendar_acl_delete

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_calendar_acl_delete = calendar_acl_delete
def _bf_friction_calendar_acl_delete(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_calendar_acl_delete(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "calendar_acl_delete|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_calendar_acl_delete(*_bf_args, **_bf_kwargs)
_bf_friction_calendar_acl_delete.blobfish_original = _bf_orig_calendar_acl_delete
calendar_acl_delete = _bf_friction_calendar_acl_delete

def calendar_calendars_update(db_path='state.db', **kwargs):
    '''Updates metadata for a calendar. (PUT /calendars/{calendarId})'''
    _missing = [p for p in ['calendar_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'errors': [{'domain': 'global', 'reason': 'required', 'message': str(_r.get('error', ''))}], 'code': 400, 'message': str(_r.get('error', ''))}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "calendars" WHERE "id" = ?', [str(kwargs['calendar_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'calendar not found', 'status': 404}
            return {'error': {'errors': [{'domain': 'global', 'reason': 'notFound', 'message': str(_r.get('error', ''))}], 'code': 404, 'message': str(_r.get('error', ''))}}
        _sets, _args = [], []
        if kwargs.get('summary') is not None:
            _sets.append('"summary" = ?')
            _v = kwargs['summary']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('description') is not None:
            _sets.append('"description" = ?')
            _v = kwargs['description']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('location') is not None:
            _sets.append('"location" = ?')
            _v = kwargs['location']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('time_zone') is not None:
            _sets.append('"time_zone" = ?')
            _v = kwargs['time_zone']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "calendars" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['calendar_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "calendars" WHERE "id" = ?', [str(kwargs['calendar_id'])]).fetchone()
        _r = dict(_row)
        _r['kind'] = 'calendar#calendar'
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_calendar_calendars_update = calendar_calendars_update
def _bf_friction_calendar_calendars_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_calendar_calendars_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "calendar_calendars_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_calendar_calendars_update(*_bf_args, **_bf_kwargs)
_bf_friction_calendar_calendars_update.blobfish_original = _bf_orig_calendar_calendars_update
calendar_calendars_update = _bf_friction_calendar_calendars_update

def calendar_calendars_delete(db_path='state.db', **kwargs):
    '''Deletes a secondary calendar. Use calendars.clear for clearing all events on primary calendars. (DELETE /calendars/{calendarId})'''
    _missing = [p for p in ['calendar_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'error': {'errors': [{'domain': 'global', 'reason': 'required', 'message': str(_r.get('error', ''))}], 'code': 400, 'message': str(_r.get('error', ''))}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "calendars" WHERE "id" = ?', [str(kwargs['calendar_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'calendar not found', 'status': 404}
            return {'error': {'errors': [{'domain': 'global', 'reason': 'notFound', 'message': str(_r.get('error', ''))}], 'code': 404, 'message': str(_r.get('error', ''))}}
        cur.execute('DELETE FROM "calendars" WHERE "id" = ?', [str(kwargs['calendar_id'])])
        conn.commit()
        _r = {'deleted': True, 'id': str(kwargs['calendar_id'])}
        return {}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_calendar_calendars_delete = calendar_calendars_delete
def _bf_friction_calendar_calendars_delete(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_calendar_calendars_delete(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "calendar_calendars_delete|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_calendar_calendars_delete(*_bf_args, **_bf_kwargs)
_bf_friction_calendar_calendars_delete.blobfish_original = _bf_orig_calendar_calendars_delete
calendar_calendars_delete = _bf_friction_calendar_calendars_delete

def calendar_colors_get(db_path='state.db', **kwargs):
    '''Returns the color definitions for calendars and events. (GET /colors)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "colors"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'kind': 'calendar#colors', 'items': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_calendar_colors_get = calendar_colors_get
def _bf_friction_calendar_colors_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_calendar_colors_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "calendar_colors_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_calendar_colors_get(*_bf_args, **_bf_kwargs)
_bf_friction_calendar_colors_get.blobfish_original = _bf_orig_calendar_colors_get
calendar_colors_get = _bf_friction_calendar_colors_get

def calendar_settings_list(db_path='state.db', **kwargs):
    '''Returns all user settings for the authenticated user. (GET /users/me/settings)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "cal_settings"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'kind': 'calendar#settings', 'items': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_calendar_settings_list = calendar_settings_list
def _bf_friction_calendar_settings_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_calendar_settings_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "calendar_settings_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_calendar_settings_list(*_bf_args, **_bf_kwargs)
_bf_friction_calendar_settings_list.blobfish_original = _bf_orig_calendar_settings_list
calendar_settings_list = _bf_friction_calendar_settings_list

