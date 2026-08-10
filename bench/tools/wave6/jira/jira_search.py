def jira_search(db_path='state.db', **kwargs):
    import sqlite3
    jql = kwargs.get('jql')
    if jql is None or str(jql).strip() == '':
        return {'error': 'jql is required', 'status': 400}
    try:
        max_results = int(kwargs.get('max_results', 50))
    except (TypeError, ValueError):
        max_results = 50
    try:
        start_at = int(kwargs.get('start_at', 0))
    except (TypeError, ValueError):
        start_at = 0
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    sql = 'SELECT * FROM jira_issues WHERE (summary LIKE ? OR description LIKE ?)'
    params = ['%' + str(jql) + '%', '%' + str(jql) + '%']
    if kwargs.get('project'):
        sql += ' AND project_key = ?'
        params.append(kwargs['project'])
    if kwargs.get('status'):
        sql += ' AND status = ?'
        params.append(kwargs['status'])
    if kwargs.get('assignee'):
        sql += ' AND (assignee = ? OR assignee_email = ?)'
        params.append(kwargs['assignee'])
        params.append(kwargs['assignee'])
    sql += ' ORDER BY updated DESC LIMIT ? OFFSET ?'
    params.append(max_results)
    params.append(start_at)
    issues = [dict(r) for r in conn.execute(sql, params).fetchall()]
    conn.close()
    return {'startAt': start_at, 'maxResults': max_results, 'total': len(issues), 'issues': issues}

_env_orig_jira_search = jira_search
def _env_jira_search(db_path='state.db', **kwargs):
    _r = _env_orig_jira_search(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'issues': _r['items'], 'total': _r['count'], 'startAt': 0, 'maxResults': _r['count']}
    if 'error' in _r and _r.get('status') == 404:
        return {'errorMessages': [str(_r.get('error', ''))], 'errors': {}}
    if 'error' in _r and _r.get('status') == 400:
        return {'errorMessages': [str(_r.get('error', ''))], 'errors': {}}
    return _r
jira_search = _env_jira_search

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_jira_search = jira_search
def _bf_friction_jira_search(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_jira_search(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "jira_search|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_jira_search(*_bf_args, **_bf_kwargs)
_bf_friction_jira_search.blobfish_original = _bf_orig_jira_search
jira_search = _bf_friction_jira_search
