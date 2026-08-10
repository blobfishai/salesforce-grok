def sg_list_add_contact(db_path='state.db', **kwargs):
    import sqlite3, hashlib, datetime
    list_id = kwargs.get('list_id')
    contact_id = kwargs.get('contact_id')
    if not list_id:
        return {"errors": [{"field": "list_id", "message": "list_id is required."}]}
    if not contact_id:
        return {"errors": [{"field": "contact_id", "message": "contact_id is required."}]}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    lst = cur.execute("SELECT * FROM sg_lists WHERE id = ?", (list_id,)).fetchone()
    if lst is None:
        conn.close()
        return {"errors": [{"field": "list_id", "message": "List with id '%s' not found." % list_id}]}
    contact = cur.execute("SELECT * FROM sg_contacts WHERE id = ?", (contact_id,)).fetchone()
    if contact is None:
        conn.close()
        return {"errors": [{"field": "contact_id", "message": "Contact with id '%s' not found." % contact_id}]}
    member = cur.execute("SELECT * FROM sg_list_members WHERE list_id = ? AND contact_id = ?", (list_id, contact_id)).fetchone()
    if member is not None:
        conn.close()
        result = dict(member)
        result["already_member"] = True
        return result
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    mem_id = 'mem_' + hashlib.sha256((str(list_id) + '|' + str(contact_id)).encode('utf-8')).hexdigest()[:12]
    cur.execute("INSERT INTO sg_list_members (id, list_id, contact_id, created_at) VALUES (?, ?, ?, ?)", (mem_id, list_id, contact_id, now))
    cur.execute("UPDATE sg_lists SET contact_count = COALESCE(contact_count, 0) + 1 WHERE id = ?", (list_id,))
    conn.commit()
    row = cur.execute("SELECT * FROM sg_list_members WHERE id = ?", (mem_id,)).fetchone()
    count = cur.execute("SELECT contact_count FROM sg_lists WHERE id = ?", (list_id,)).fetchone()
    conn.close()
    result = dict(row)
    result["already_member"] = False
    result["list_contact_count"] = count["contact_count"]
    return result

_env_orig_sg_list_add_contact = sg_list_add_contact
def _env_sg_list_add_contact(db_path='state.db', **kwargs):
    _r = _env_orig_sg_list_add_contact(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'result': _r['items'], '_metadata': {'count': _r['count']}}
    if 'error' in _r and _r.get('status') == 404:
        return {'errors': [{'message': str(_r.get('error', '')), 'field': None, 'help': None}]}
    if 'error' in _r and _r.get('status') == 400:
        return {'errors': [{'message': str(_r.get('error', '')), 'field': None, 'help': None}]}
    return _r
sg_list_add_contact = _env_sg_list_add_contact

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_sg_list_add_contact = sg_list_add_contact
def _bf_friction_sg_list_add_contact(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_sg_list_add_contact(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "sg_list_add_contact|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_sg_list_add_contact(*_bf_args, **_bf_kwargs)
_bf_friction_sg_list_add_contact.blobfish_original = _bf_orig_sg_list_add_contact
sg_list_add_contact = _bf_friction_sg_list_add_contact
