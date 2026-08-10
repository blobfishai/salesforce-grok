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
