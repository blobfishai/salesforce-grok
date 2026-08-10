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
