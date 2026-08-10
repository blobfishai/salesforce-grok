def jira_issue_transition(db_path='state.db', **kwargs):
    import sqlite3, datetime, hashlib
    issue_key = kwargs.get('issue_key')
    transition_id = kwargs.get('transition_id')
    if not issue_key or transition_id is None:
        return {'error': 'issue_key and transition_id are required', 'status': 400}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    issue = conn.execute('SELECT * FROM jira_issues WHERE key = ?', (issue_key,)).fetchone()
    if issue is None:
        conn.close()
        return {'error': 'Issue ' + str(issue_key) + ' not found', 'status': 404}
    tr = conn.execute('SELECT * FROM jira_transitions WHERE id = ?', (str(transition_id),)).fetchone()
    if tr is None:
        conn.close()
        return {'error': 'Transition ' + str(transition_id) + ' not found', 'status': 404}
    if tr['from_status'] != issue['status']:
        conn.close()
        return {'error': 'Transition ' + tr['name'] + ' (' + tr['from_status'] + ' -> ' + tr['to_status'] + ') is not valid for an issue in status ' + issue['status'], 'status': 400}
    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000+0000')
    conn.execute('UPDATE jira_issues SET status = ?, updated = ? WHERE key = ?', (tr['to_status'], now, issue_key))
    comment = kwargs.get('comment')
    if comment:
        cid = 'jcm-' + hashlib.sha1((str(issue_key) + now + str(comment)).encode('utf-8')).hexdigest()[:8]
        conn.execute('INSERT INTO jira_comments (id, issue_key, author, author_email, body, created) VALUES (?, ?, ?, ?, ?, ?)', (cid, issue_key, 'Automation for Jira', 'jira-automation@morganstanleysimulated.com', comment, now))
    conn.commit()
    updated = dict(conn.execute('SELECT * FROM jira_issues WHERE key = ?', (issue_key,)).fetchone())
    conn.close()
    return {'issue': updated, 'transition': {'id': tr['id'], 'name': tr['name'], 'from_status': tr['from_status'], 'to_status': tr['to_status']}}

_env_orig_jira_issue_transition = jira_issue_transition
def _env_jira_issue_transition(db_path='state.db', **kwargs):
    _r = _env_orig_jira_issue_transition(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'issues': _r['items'], 'total': _r['count'], 'startAt': 0, 'maxResults': _r['count']}
    if 'error' in _r and _r.get('status') == 404:
        return {'errorMessages': [str(_r.get('error', ''))], 'errors': {}}
    if 'error' in _r and _r.get('status') == 400:
        return {'errorMessages': [str(_r.get('error', ''))], 'errors': {}}
    return _r
jira_issue_transition = _env_jira_issue_transition

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_jira_issue_transition = jira_issue_transition
def _bf_friction_jira_issue_transition(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_jira_issue_transition(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "jira_issue_transition|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_jira_issue_transition(*_bf_args, **_bf_kwargs)
_bf_friction_jira_issue_transition.blobfish_original = _bf_orig_jira_issue_transition
jira_issue_transition = _bf_friction_jira_issue_transition
