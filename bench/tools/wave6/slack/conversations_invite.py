def conversations_invite(db_path='state.db', **kwargs):
    import sqlite3, hashlib, datetime
    channel = kwargs.get('channel')
    users = kwargs.get('users')
    if not channel or not users:
        return {'ok': False, 'error': 'channel and users are required', 'status': 400}
    ids = [u.strip() for u in str(users).split(',') if u.strip()]
    if not ids:
        return {'ok': False, 'error': 'no_users_provided', 'status': 400}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    ch = conn.execute('SELECT * FROM channels WHERE id = ?', (str(channel),)).fetchone()
    if ch is None:
        ch = conn.execute('SELECT * FROM channels WHERE name = ? ORDER BY id LIMIT 1', (str(channel).lstrip('#'),)).fetchone()
    if ch is None:
        conn.close()
        return {'ok': False, 'error': 'channel_not_found', 'status': 404}
    if ch['is_archived']:
        conn.close()
        return {'ok': False, 'error': 'is_archived', 'status': 400}
    missing = [u for u in ids if conn.execute('SELECT 1 FROM slack_users WHERE id = ?', (u,)).fetchone() is None]
    if missing:
        conn.close()
        return {'ok': False, 'error': 'users_not_found', 'users': missing, 'status': 404}
    now = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    invited, already = [], []
    for u in ids:
        if conn.execute('SELECT 1 FROM slack_channel_members WHERE channel = ? AND user = ?', (ch['id'], u)).fetchone() is not None:
            already.append(u)
            continue
        mid = 'M' + hashlib.md5((ch['id'] + ':' + u).encode('utf-8')).hexdigest()[:7].upper()
        conn.execute('INSERT INTO slack_channel_members (id, channel, user, date_joined) VALUES (?, ?, ?, ?)', (mid, ch['id'], u, now))
        invited.append(u)
    if invited:
        conn.execute('UPDATE channels SET num_members = COALESCE(num_members, 0) + ? WHERE id = ?', (len(invited), ch['id']))
    conn.commit()
    conn.close()
    return {'ok': True, 'channel': {'id': ch['id'], 'name': ch['name']}, 'invited': invited, 'already_in_channel': already}

_env_orig_conversations_invite = conversations_invite
def _env_conversations_invite(db_path='state.db', **kwargs):
    _r = _env_orig_conversations_invite(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'ok': True, 'channel_members': _r['items'], 'response_metadata': {'next_cursor': ''}}
    if 'error' in _r and _r.get('status') == 404:
        return {'ok': False, 'error': str(_r.get('error') or 'channel_member not found').replace(' not found', '_not_found').replace(' ', '_')}
    if 'error' in _r and _r.get('status') == 400:
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    return _r
conversations_invite = _env_conversations_invite

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_conversations_invite = conversations_invite
def _bf_friction_conversations_invite(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_conversations_invite(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "conversations_invite|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_conversations_invite(*_bf_args, **_bf_kwargs)
_bf_friction_conversations_invite.blobfish_original = _bf_orig_conversations_invite
conversations_invite = _bf_friction_conversations_invite
