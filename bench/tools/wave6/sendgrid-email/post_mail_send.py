def post_mail_send(db_path='state.db', **kwargs):
    import sqlite3, hashlib, datetime
    to = kwargs.get('to')
    from_email = kwargs.get('from')
    subject = kwargs.get('subject')
    body = kwargs.get('body')
    template_id = kwargs.get('template_id')
    categories = kwargs.get('categories')
    if isinstance(categories, list):
        categories = ','.join(str(c) for c in categories)
    if not to:
        return {"errors": [{"field": "to", "message": "The to parameter is required and must be a valid email address."}]}
    if not from_email:
        return {"errors": [{"field": "from", "message": "The from email address is required for every send and should belong to a verified sender identity."}]}
    if not subject and not template_id:
        return {"errors": [{"field": "subject", "message": "The subject is required. You can get around this requirement if you use a template with a subject defined."}]}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if template_id:
        tpl = cur.execute("SELECT * FROM sg_templates WHERE id = ?", (template_id,)).fetchone()
        if tpl is None:
            conn.close()
            return {"errors": [{"field": "template_id", "message": "Template with id '%s' not found." % template_id}]}
        ver = cur.execute("SELECT * FROM sg_template_versions WHERE template_id = ? AND active = 1", (template_id,)).fetchone()
        if ver is not None:
            if not subject:
                subject = ver["subject"]
            if not body:
                body = ver["html_content"]
    suppressed = cur.execute("SELECT * FROM sg_global_suppressions WHERE email = ?", (to,)).fetchone()
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    msg_id = 'msg_' + hashlib.sha256((str(to) + '|' + str(subject) + '|' + now).encode('utf-8')).hexdigest()[:16]
    status = 'dropped' if suppressed is not None else 'delivered'
    cur.execute(
        "INSERT INTO sg_mail_sends (id, to_email, from_email, subject, body, template_id, categories, status, sent_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (msg_id, to, from_email, subject, body, template_id, categories, status, now))
    conn.commit()
    row = cur.execute("SELECT * FROM sg_mail_sends WHERE id = ?", (msg_id,)).fetchone()
    conn.close()
    result = dict(row)
    result["message_id"] = msg_id
    if status == 'dropped':
        result["drop_reason"] = "Recipient address is on the global unsubscribe list; message was logged as dropped and not delivered."
    return result

_env_orig_post_mail_send = post_mail_send
def _env_post_mail_send(db_path='state.db', **kwargs):
    _r = _env_orig_post_mail_send(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'result': _r['items'], '_metadata': {'count': _r['count']}}
    if 'error' in _r and _r.get('status') == 404:
        return {'errors': [{'message': str(_r.get('error', '')), 'field': None, 'help': None}]}
    if 'error' in _r and _r.get('status') == 400:
        return {'errors': [{'message': str(_r.get('error', '')), 'field': None, 'help': None}]}
    return _r
post_mail_send = _env_post_mail_send

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_mail_send = post_mail_send
def _bf_friction_post_mail_send(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_mail_send(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_mail_send|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_mail_send(*_bf_args, **_bf_kwargs)
_bf_friction_post_mail_send.blobfish_original = _bf_orig_post_mail_send
post_mail_send = _bf_friction_post_mail_send
