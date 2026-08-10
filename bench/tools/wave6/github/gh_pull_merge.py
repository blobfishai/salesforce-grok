def gh_pull_merge(db_path='state.db', **kwargs):
    import sqlite3, datetime, hashlib
    repo = kwargs.get('repo')
    number = kwargs.get('pull_number')
    if not repo or number is None:
        return {'error': 'Validation Failed', 'status': 422, 'message': 'repo and pull_number are required'}
    try:
        number = int(number)
    except (TypeError, ValueError):
        return {'error': 'Validation Failed', 'status': 422, 'message': 'pull_number must be an integer'}
    merge_method = kwargs.get('merge_method') or 'merge'
    if merge_method not in ('merge', 'squash', 'rebase'):
        return {'error': 'Validation Failed', 'status': 422, 'message': 'merge_method must be one of: merge, squash, rebase'}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        pr = conn.execute('SELECT * FROM gh_pull_requests WHERE repo = ? AND number = ?', (repo, number)).fetchone()
        if pr is None:
            return {'error': 'Not Found', 'status': 404, 'message': 'Pull request #%s not found in %s' % (number, repo)}
        if pr['merged'] == 1:
            return {'error': 'Method Not Allowed', 'status': 405, 'message': 'Pull Request is not mergeable: already merged'}
        if pr['state'] != 'open':
            return {'error': 'Method Not Allowed', 'status': 405, 'message': 'Pull Request is not mergeable: not open'}
        now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        sha = hashlib.sha1(('%s#%d@%s' % (repo, number, now)).encode()).hexdigest()
        title = kwargs.get('commit_title') or ('Merge pull request #%d from %s/%s' % (number, repo.split('/')[0], pr['head']))
        conn.execute(
            'UPDATE gh_pull_requests SET state = ?, merged = 1, merged_at = ?, closed_at = ?, merge_commit_sha = ?, '
            'updated_at = ? WHERE repo = ? AND number = ?',
            ('closed', now, now, sha, now, repo, number))
        conn.execute(
            'INSERT INTO gh_commits (sha, repo, branch, message, author, author_email, date) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (sha, repo, pr['base'], title, pr['user'], 'noreply@morganstanleysimulated.com', now))
        conn.execute('UPDATE gh_branches SET sha = ? WHERE repo = ? AND name = ?', (sha, repo, pr['base']))
        conn.commit()
        return {'sha': sha, 'merged': True, 'message': 'Pull Request successfully merged'}
    finally:
        conn.close()

_env_orig_gh_pull_merge = gh_pull_merge
def _env_gh_pull_merge(db_path='state.db', **kwargs):
    _r = _env_orig_gh_pull_merge(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return _r['items']
    if 'error' in _r and _r.get('status') == 404:
        return {'message': 'Not Found', 'documentation_url': 'https://docs.github.com/rest', 'status': '404'}
    if 'error' in _r and _r.get('status') == 400:
        return {'message': 'Validation Failed', 'errors': [{'message': str(_r.get('error', ''))}], 'status': '422'}
    return _r
gh_pull_merge = _env_gh_pull_merge

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_gh_pull_merge = gh_pull_merge
def _bf_friction_gh_pull_merge(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_gh_pull_merge(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "gh_pull_merge|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_gh_pull_merge(*_bf_args, **_bf_kwargs)
_bf_friction_gh_pull_merge.blobfish_original = _bf_orig_gh_pull_merge
gh_pull_merge = _bf_friction_gh_pull_merge
