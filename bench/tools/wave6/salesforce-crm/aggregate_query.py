
def aggregate_query(db_path='state.db', **kwargs):
    '''Run a SOQL-style aggregate over one object: COUNT/SUM/AVG/MIN/MAX with an
    optional GROUP BY and equality filter (GET /services/data/v62.0/query?q=SELECT+COUNT(Id)+FROM+X+GROUP+BY+Y).'''
    import sqlite3
    sobject = kwargs.get('sobject')
    func = str(kwargs.get('function') or 'COUNT').upper()
    if not sobject:
        return [{'message': 'missing required parameters: sobject', 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    if func not in ('COUNT', 'SUM', 'AVG', 'MIN', 'MAX'):
        return [{'message': 'function must be one of COUNT, SUM, AVG, MIN, MAX', 'errorCode': 'INVALID_TYPE'}]
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        names = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]
        if sobject not in names:
            return [{'message': "sObject type '" + str(sobject) + "' is not supported",
                     'errorCode': 'INVALID_TYPE'}]
        cols = [r[1] for r in conn.execute('PRAGMA table_info("' + sobject + '")').fetchall()]
        field = kwargs.get('field')
        group_by = kwargs.get('group_by')
        bucket = str(kwargs.get('group_by_function') or '').upper()
        where_field = kwargs.get('where_field')
        for label, ident in (('field', field), ('group_by', group_by), ('where_field', where_field)):
            if ident is not None and ident not in cols:
                return [{'message': "No such column '" + str(ident) + "' on entity '" + str(sobject) + "'",
                         'errorCode': 'INVALID_FIELD'}]
        if func != 'COUNT' and not field:
            return [{'message': func + ' requires a numeric field', 'errorCode': 'REQUIRED_FIELD_MISSING'}]
        expr = 'COUNT(*)' if func == 'COUNT' else func + '("' + field + '")'
        # SOQL date functions: bucket a timestamp column instead of grouping on
        # the raw value (CALENDAR_MONTH -> YYYY-MM, CALENDAR_YEAR -> YYYY, DAY_ONLY -> YYYY-MM-DD)
        _widths = {'CALENDAR_MONTH': 7, 'CALENDAR_YEAR': 4, 'DAY_ONLY': 10}
        if bucket and bucket not in _widths:
            return [{'message': 'group_by_function must be CALENDAR_MONTH, CALENDAR_YEAR or DAY_ONLY',
                     'errorCode': 'INVALID_TYPE'}]
        if group_by:
            group_expr = ('substr("' + group_by + '", 1, ' + str(_widths[bucket]) + ')') if bucket else ('"' + group_by + '"')
        else:
            group_expr = None
        sql = 'SELECT ' + ((group_expr + ' AS grouping, ') if group_expr else '') + expr + ' AS value FROM "' + sobject + '"'
        args = []
        if where_field is not None and kwargs.get('where_value') is not None:
            sql += ' WHERE "' + where_field + '" = ?'
            args.append(str(kwargs['where_value']))
        if group_expr:
            sql += ' GROUP BY ' + group_expr
        order = str(kwargs.get('order_by') or 'value').lower()
        direction = 'ASC' if str(kwargs.get('direction') or 'desc').lower() == 'asc' else 'DESC'
        sql += ' ORDER BY ' + ('grouping' if (order == 'grouping' and group_by) else 'value') + ' ' + direction
        limit = int(kwargs.get('limit') or 200)
        sql += ' LIMIT ?'
        args.append(limit)
        rows = []
        for r in conn.execute(sql, args).fetchall():
            d = dict(r)
            if isinstance(d.get('value'), float):
                d['value'] = round(d['value'], 2)
            rows.append(d)
        return {'totalSize': len(rows), 'done': True, 'records': rows}
    finally:
        conn.close()

_env_orig_aggregate_query = aggregate_query
def _env_aggregate_query(db_path='state.db', **kwargs):
    _r = _env_orig_aggregate_query(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
    if 'error' in _r and _r.get('status') == 400:
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    return _r
aggregate_query = _env_aggregate_query

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_aggregate_query = aggregate_query
def _bf_friction_aggregate_query(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_aggregate_query(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "aggregate_query|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_aggregate_query(*_bf_args, **_bf_kwargs)
_bf_friction_aggregate_query.blobfish_original = _bf_orig_aggregate_query
aggregate_query = _bf_friction_aggregate_query
