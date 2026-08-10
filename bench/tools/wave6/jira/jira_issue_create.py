def jira_issue_create(db_path='state.db', **kwargs):
    import sqlite3, datetime
    project_key = kwargs.get('project_key')
    summary = kwargs.get('summary')
    if not project_key or not summary:
        return {'error': 'project_key and summary are required', 'status': 400}
    issue_type = kwargs.get('issue_type') or 'Task'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    proj = conn.execute('SELECT * FROM jira_projects WHERE key = ?', (project_key,)).fetchone()
    if proj is None:
        conn.close()
        return {'error': 'Project ' + str(project_key) + ' not found', 'status': 404}
    row = conn.execute('SELECT MAX(CAST(substr(key, length(?) + 2) AS INTEGER)) AS n FROM jira_issues WHERE project_key = ?', (project_key, project_key)).fetchone()
    next_num = (row['n'] or 100) + 1
    new_key = str(project_key) + '-' + str(next_num)
    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000+0000')
    conn.execute('INSERT INTO jira_issues (key, summary, description, issue_type, status, priority, assignee, assignee_email, reporter, reporter_email, project_key, sprint_id, labels, created, updated) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (new_key, summary, kwargs.get('description') or '', issue_type, 'To Do', kwargs.get('priority') or 'Medium', kwargs.get('assignee'), kwargs.get('assignee_email'), kwargs.get('reporter'), kwargs.get('reporter_email'), project_key, kwargs.get('sprint_id'), kwargs.get('labels') or '', now, now))
    conn.commit()
    created = dict(conn.execute('SELECT * FROM jira_issues WHERE key = ?', (new_key,)).fetchone())
    conn.close()
    return created

_env_orig_jira_issue_create = jira_issue_create
def _env_jira_issue_create(db_path='state.db', **kwargs):
    _r = _env_orig_jira_issue_create(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'issues': _r['items'], 'total': _r['count'], 'startAt': 0, 'maxResults': _r['count']}
    if 'error' in _r and _r.get('status') == 404:
        return {'errorMessages': [str(_r.get('error', ''))], 'errors': {}}
    if 'error' in _r and _r.get('status') == 400:
        return {'errorMessages': [str(_r.get('error', ''))], 'errors': {}}
    return _r
jira_issue_create = _env_jira_issue_create

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_jira_issue_create = jira_issue_create
def _bf_friction_jira_issue_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_jira_issue_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "jira_issue_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_jira_issue_create(*_bf_args, **_bf_kwargs)
_bf_friction_jira_issue_create.blobfish_original = _bf_orig_jira_issue_create
jira_issue_create = _bf_friction_jira_issue_create
