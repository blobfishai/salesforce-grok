def pd_incident_create(db_path='state.db', **kwargs):
    import sqlite3
    import datetime
    import hashlib
    title = kwargs.get('title')
    if not title:
        return {'error': {'status': 400, 'message': "Missing required parameter 'title'."}}
    service_id = kwargs.get('service_id')
    if not service_id:
        return {'error': {'status': 400, 'message': "Missing required parameter 'service_id'."}}
    urgency = kwargs.get('urgency') or 'high'
    if urgency not in ('high', 'low'):
        return {'error': {'status': 400, 'message': "Invalid urgency '%s'. Must be one of: high, low." % urgency}}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    svc = conn.execute('SELECT * FROM pd_services WHERE id = ?', (service_id,)).fetchone()
    if svc is None:
        conn.close()
        return {'error': {'status': 404, 'message': "Service '%s' not found." % service_id}}
    escalation_policy_id = kwargs.get('escalation_policy_id') or svc['escalation_policy_id']
    priority_id = kwargs.get('priority_id')
    if priority_id:
        if conn.execute('SELECT id FROM pd_priorities WHERE id = ?', (priority_id,)).fetchone() is None:
            conn.close()
            return {'error': {'status': 404, 'message': "Priority '%s' not found." % priority_id}}
    assignee = kwargs.get('assignee')
    if assignee:
        if conn.execute('SELECT id FROM pd_users WHERE id = ?', (assignee,)).fetchone() is None:
            conn.close()
            return {'error': {'status': 404, 'message': "User '%s' not found." % assignee}}
    else:
        oncall = conn.execute('SELECT user_id FROM pd_oncalls WHERE escalation_policy_id = ? AND escalation_level = 1 ORDER BY id LIMIT 1', (escalation_policy_id,)).fetchone()
        assignee = oncall['user_id'] if oncall else None
    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    number = conn.execute('SELECT COALESCE(MAX(incident_number), 0) + 1 AS n FROM pd_incidents').fetchone()['n']
    new_id = 'P' + hashlib.sha1((title + str(number) + str(datetime.datetime.utcnow().timestamp())).encode('utf-8')).hexdigest()[:6].upper()
    conn.execute('INSERT INTO pd_incidents (id, incident_number, title, description, status, urgency, priority_id, service_id, escalation_policy_id, assignee, created_at, resolved_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                 (new_id, number, title, kwargs.get('details'), 'triggered', urgency, priority_id, service_id, escalation_policy_id, assignee, now, None))
    log_id = 'R' + hashlib.sha1((new_id + 'trigger' + str(datetime.datetime.utcnow().timestamp())).encode('utf-8')).hexdigest()[:6].upper()
    conn.execute('INSERT INTO pd_log_entries (id, incident_id, type, agent_id, channel, summary, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                 (log_id, new_id, 'trigger_log_entry', None, 'api', 'Triggered through the API.', now))
    conn.commit()
    row = dict(conn.execute('SELECT * FROM pd_incidents WHERE id = ?', (new_id,)).fetchone())
    conn.close()
    return {'incident': row}

_env_orig_pd_incident_create = pd_incident_create
def _env_pd_incident_create(db_path='state.db', **kwargs):
    _r = _env_orig_pd_incident_create(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'incidents': _r['items'], 'limit': _r['count'], 'offset': 0, 'more': False, 'total': _r['count']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'message': str(_r.get('error', '')), 'code': 2100}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'message': str(_r.get('error', '')), 'code': 2001, 'errors': [str(_r.get('error', ''))]}}
    return _r
pd_incident_create = _env_pd_incident_create

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_incident_create = pd_incident_create
def _bf_friction_pd_incident_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_incident_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_incident_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_incident_create(*_bf_args, **_bf_kwargs)
_bf_friction_pd_incident_create.blobfish_original = _bf_orig_pd_incident_create
pd_incident_create = _bf_friction_pd_incident_create
