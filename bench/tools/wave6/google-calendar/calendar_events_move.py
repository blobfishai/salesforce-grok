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
