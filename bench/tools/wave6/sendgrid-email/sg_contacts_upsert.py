def sg_contacts_upsert(db_path='state.db', **kwargs):
    import sqlite3, hashlib, datetime
    email = kwargs.get('email')
    if not email:
        return {"errors": [{"field": "email", "message": "email is required for every contact; contacts are matched and upserted by email address."}]}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    fields = ['first_name', 'last_name', 'company', 'phone_number']
    existing = cur.execute("SELECT * FROM sg_contacts WHERE email = ?", (email,)).fetchone()
    if existing is not None:
        sets = ["updated_at = ?"]
        vals = [now]
        for f in fields:
            if kwargs.get(f) is not None:
                sets.append(f + " = ?")
                vals.append(kwargs.get(f))
        vals.append(email)
        cur.execute("UPDATE sg_contacts SET " + ", ".join(sets) + " WHERE email = ?", vals)
        conn.commit()
        status = 'updated'
        row = cur.execute("SELECT * FROM sg_contacts WHERE email = ?", (email,)).fetchone()
    else:
        h = hashlib.sha256(email.encode('utf-8')).hexdigest()
        contact_id = h[0:8] + '-' + h[8:12] + '-' + h[12:16] + '-' + h[16:20] + '-' + h[20:32]
        cur.execute(
            "INSERT INTO sg_contacts (id, email, first_name, last_name, company, phone_number, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (contact_id, email, kwargs.get('first_name'), kwargs.get('last_name'), kwargs.get('company'), kwargs.get('phone_number'), now, now))
        conn.commit()
        status = 'created'
        row = cur.execute("SELECT * FROM sg_contacts WHERE id = ?", (contact_id,)).fetchone()
    conn.close()
    jh = hashlib.sha256((email + '|' + now).encode('utf-8')).hexdigest()
    return {"job_id": jh[0:8] + '-' + jh[8:12] + '-' + jh[12:16] + '-' + jh[16:20] + '-' + jh[20:32], "status": status, "contact": dict(row)}

_env_orig_sg_contacts_upsert = sg_contacts_upsert
def _env_sg_contacts_upsert(db_path='state.db', **kwargs):
    _r = _env_orig_sg_contacts_upsert(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'result': _r['items'], '_metadata': {'count': _r['count']}}
    if 'error' in _r and _r.get('status') == 404:
        return {'errors': [{'message': str(_r.get('error', '')), 'field': None, 'help': None}]}
    if 'error' in _r and _r.get('status') == 400:
        return {'errors': [{'message': str(_r.get('error', '')), 'field': None, 'help': None}]}
    return _r
sg_contacts_upsert = _env_sg_contacts_upsert

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_sg_contacts_upsert = sg_contacts_upsert
def _bf_friction_sg_contacts_upsert(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_sg_contacts_upsert(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "sg_contacts_upsert|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_sg_contacts_upsert(*_bf_args, **_bf_kwargs)
_bf_friction_sg_contacts_upsert.blobfish_original = _bf_orig_sg_contacts_upsert
sg_contacts_upsert = _bf_friction_sg_contacts_upsert
