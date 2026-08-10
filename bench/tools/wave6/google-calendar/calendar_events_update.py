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
