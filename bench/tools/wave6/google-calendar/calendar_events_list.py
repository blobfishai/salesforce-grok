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
