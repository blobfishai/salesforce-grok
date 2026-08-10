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
