def gh_pull_create(db_path='state.db', **kwargs):
    import sqlite3, datetime, hashlib
    repo = kwargs.get('repo')
    title = kwargs.get('title')
    head = kwargs.get('head')
    if not repo or not title or not head:
        return {'error': 'Validation Failed', 'status': 422, 'message': 'repo, title and head are required'}
    base = kwargs.get('base') or 'main'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        if conn.execute('SELECT 1 FROM gh_repos WHERE full_name = ?', (repo,)).fetchone() is None:
            return {'error': 'Not Found', 'status': 404, 'message': 'Repository %s not found' % repo}
        if conn.execute('SELECT 1 FROM gh_branches WHERE repo = ? AND name = ?', (repo, head)).fetchone() is None:
            return {'error': 'Validation Failed', 'status': 422,
                    'message': 'Validation Failed', 'errors': [{'resource': 'PullRequest', 'field': 'head', 'code': 'invalid'}]}
        max_issue = conn.execute('SELECT COALESCE(MAX(number), 0) FROM gh_issues WHERE repo = ?', (repo,)).fetchone()[0]
        max_pull = conn.execute('SELECT COALESCE(MAX(number), 0) FROM gh_pull_requests WHERE repo = ?', (repo,)).fetchone()[0]
        number = max(max_issue, max_pull) + 1
        now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        pr_id = 'ghpr-' + hashlib.sha1(('%s#%d' % (repo, number)).encode()).hexdigest()[:8]
        draft = 1 if kwargs.get('draft') in (True, 1, 'true', 'True') else 0
        conn.execute(
            'INSERT INTO gh_pull_requests (id, repo, number, title, body, state, "user", head, base, draft, merged, '
            'merged_at, merge_commit_sha, created_at, updated_at, closed_at) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, NULL, NULL, ?, ?, NULL)',
            (pr_id, repo, number, title, kwargs.get('body'), 'open',
             kwargs.get('user') or 'revops-bot', head, base, draft, now, now))
        conn.commit()
        return dict(conn.execute('SELECT * FROM gh_pull_requests WHERE id = ?', (pr_id,)).fetchone())
    finally:
        conn.close()

_env_orig_gh_pull_create = gh_pull_create
def _env_gh_pull_create(db_path='state.db', **kwargs):
    _r = _env_orig_gh_pull_create(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return _r['items']
    if 'error' in _r and _r.get('status') == 404:
        return {'message': 'Not Found', 'documentation_url': 'https://docs.github.com/rest', 'status': '404'}
    if 'error' in _r and _r.get('status') == 400:
        return {'message': 'Validation Failed', 'errors': [{'message': str(_r.get('error', ''))}], 'status': '422'}
    return _r
gh_pull_create = _env_gh_pull_create

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_gh_pull_create = gh_pull_create
def _bf_friction_gh_pull_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_gh_pull_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "gh_pull_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_gh_pull_create(*_bf_args, **_bf_kwargs)
_bf_friction_gh_pull_create.blobfish_original = _bf_orig_gh_pull_create
gh_pull_create = _bf_friction_gh_pull_create
