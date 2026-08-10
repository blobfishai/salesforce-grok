def pd_incident_manage(db_path='state.db', **kwargs):
    import sqlite3
    import datetime
    import hashlib
    incident_id = kwargs.get('id')
    if not incident_id:
        return {'error': {'status': 400, 'message': "Missing required parameter 'id'."}}
    status = kwargs.get('status')
    escalation_level = kwargs.get('escalation_level')
    if status is None and escalation_level is None:
        return {'error': {'status': 400, 'message': "Nothing to update: provide 'status' (acknowledged or resolved) and/or 'escalation_level'."}}
    if status is not None and status not in ('acknowledged', 'resolved'):
        return {'error': {'status': 400, 'message': "Invalid status '%s'. Must be one of: acknowledged, resolved." % status}}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM pd_incidents WHERE id = ?', (incident_id,)).fetchone()
    if row is None:
        conn.close()
        return {'error': {'status': 404, 'message': "Incident '%s' not found." % incident_id}}
    if row['status'] == 'resolved':
        conn.close()
        return {'error': {'status': 400, 'message': "Incident '%s' is already resolved; resolved incidents cannot be modified." % incident_id}}
    agent_id = None
    from_email = kwargs.get('from')
    if from_email:
        user = conn.execute('SELECT id FROM pd_users WHERE email = ?', (from_email,)).fetchone()
        if user is None:
            conn.close()
            return {'error': {'status': 404, 'message': "No user found with email '%s' (From header)." % from_email}}
        agent_id = user['id']
    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    def _log(entry_type, summary):
        log_id = 'R' + hashlib.sha1((incident_id + entry_type + str(datetime.datetime.utcnow().timestamp())).encode('utf-8')).hexdigest()[:6].upper()
        conn.execute('INSERT INTO pd_log_entries (id, incident_id, type, agent_id, channel, summary, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (log_id, incident_id, entry_type, agent_id, 'api', summary, now))

    if escalation_level is not None:
        try:
            level = int(escalation_level)
        except (TypeError, ValueError):
            conn.close()
            return {'error': {'status': 400, 'message': "Invalid escalation_level '%s': must be an integer." % escalation_level}}
        oncall = conn.execute('SELECT user_id FROM pd_oncalls WHERE escalation_policy_id = ? AND escalation_level = ? ORDER BY id LIMIT 1', (row['escalation_policy_id'], level)).fetchone()
        if oncall is None:
            conn.close()
            return {'error': {'status': 400, 'message': "No on-call target at escalation level %d on escalation policy '%s'." % (level, row['escalation_policy_id'])}}
        conn.execute('UPDATE pd_incidents SET status = ?, assignee = ? WHERE id = ?', ('triggered', oncall['user_id'], incident_id))
        _log('escalate_log_entry', 'Escalated to level %d of escalation policy %s; assigned to %s.' % (level, row['escalation_policy_id'], oncall['user_id']))
    if status == 'acknowledged':
        conn.execute('UPDATE pd_incidents SET status = ? WHERE id = ?', ('acknowledged', incident_id))
        _log('acknowledge_log_entry', 'Acknowledged by %s.' % (agent_id or 'API'))
    elif status == 'resolved':
        conn.execute('UPDATE pd_incidents SET status = ?, resolved_at = ? WHERE id = ?', ('resolved', now, incident_id))
        _log('resolve_log_entry', 'Resolved by %s.' % (agent_id or 'API'))
        resolution = kwargs.get('resolution')
        if resolution:
            note_id = 'P' + hashlib.sha1((incident_id + resolution + str(datetime.datetime.utcnow().timestamp())).encode('utf-8')).hexdigest()[:6].upper()
            conn.execute('INSERT INTO pd_incident_notes (id, incident_id, user_id, content, created_at) VALUES (?, ?, ?, ?, ?)',
                         (note_id, incident_id, agent_id, resolution, now))
    conn.commit()
    updated = dict(conn.execute('SELECT * FROM pd_incidents WHERE id = ?', (incident_id,)).fetchone())
    conn.close()
    return {'incident': updated}

_env_orig_pd_incident_manage = pd_incident_manage
def _env_pd_incident_manage(db_path='state.db', **kwargs):
    _r = _env_orig_pd_incident_manage(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'incidents': _r['items'], 'limit': _r['count'], 'offset': 0, 'more': False, 'total': _r['count']}
    if 'error' in _r and _r.get('status') == 404:
        return {'error': {'message': str(_r.get('error', '')), 'code': 2100}}
    if 'error' in _r and _r.get('status') == 400:
        return {'error': {'message': str(_r.get('error', '')), 'code': 2001, 'errors': [str(_r.get('error', ''))]}}
    return _r
pd_incident_manage = _env_pd_incident_manage

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pd_incident_manage = pd_incident_manage
def _bf_friction_pd_incident_manage(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pd_incident_manage(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pd_incident_manage|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pd_incident_manage(*_bf_args, **_bf_kwargs)
_bf_friction_pd_incident_manage.blobfish_original = _bf_orig_pd_incident_manage
pd_incident_manage = _bf_friction_pd_incident_manage
