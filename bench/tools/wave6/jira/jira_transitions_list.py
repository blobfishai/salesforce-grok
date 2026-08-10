def jira_transitions_list(db_path='state.db', **kwargs):
    import sqlite3
    issue_key = kwargs.get('issue_key')
    if not issue_key:
        return {'error': 'issue_key is required', 'status': 400}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    issue = conn.execute('SELECT * FROM jira_issues WHERE key = ?', (issue_key,)).fetchone()
    if issue is None:
        conn.close()
        return {'error': 'Issue ' + str(issue_key) + ' not found', 'status': 404}
    transitions = [dict(r) for r in conn.execute('SELECT * FROM jira_transitions WHERE from_status = ? ORDER BY CAST(id AS INTEGER)', (issue['status'],)).fetchall()]
    conn.close()
    return {'issue_key': issue_key, 'current_status': issue['status'], 'transitions': transitions}

_env_orig_jira_transitions_list = jira_transitions_list
def _env_jira_transitions_list(db_path='state.db', **kwargs):
    _r = _env_orig_jira_transitions_list(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'values': _r['items'], 'total': _r['count'], 'startAt': 0, 'maxResults': _r['count'], 'isLast': True}
    if 'error' in _r and _r.get('status') == 404:
        return {'errorMessages': [str(_r.get('error', ''))], 'errors': {}}
    if 'error' in _r and _r.get('status') == 400:
        return {'errorMessages': [str(_r.get('error', ''))], 'errors': {}}
    return _r
jira_transitions_list = _env_jira_transitions_list

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_jira_transitions_list = jira_transitions_list
def _bf_friction_jira_transitions_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_jira_transitions_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "jira_transitions_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_jira_transitions_list(*_bf_args, **_bf_kwargs)
_bf_friction_jira_transitions_list.blobfish_original = _bf_orig_jira_transitions_list
jira_transitions_list = _bf_friction_jira_transitions_list
