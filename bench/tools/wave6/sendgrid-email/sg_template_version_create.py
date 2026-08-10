def sg_template_version_create(db_path='state.db', **kwargs):
    '''Create a new version of a transactional template. A version is the body/subject content of a template; only one version per template can be active. (POST /v3/templates/{template_id}/versions)'''
    _missing = [p for p in ['template_id', 'name', 'subject'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'errors': [{'message': str(_r.get('error', '')), 'field': None, 'help': None}]}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "sg_template_versions"').fetchone()[0] + 1
        _id = 'ver_' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "sg_template_versions" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'ver_' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('template_id') is not None:
            _cols.append('template_id')
            _v = kwargs['template_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('name') is not None:
            _cols.append('name')
            _v = kwargs['name']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('subject') is not None:
            _cols.append('subject')
            _v = kwargs['subject']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('html_content') is not None:
            _cols.append('html_content')
            _v = kwargs['html_content']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('plain_content') is not None:
            _cols.append('plain_content')
            _v = kwargs['plain_content']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('active') is not None:
            _cols.append('active')
            _v = kwargs['active']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('editor') is not None:
            _cols.append('editor')
            _v = kwargs['editor']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "sg_template_versions" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "sg_template_versions" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_sg_template_version_create = sg_template_version_create
def _bf_friction_sg_template_version_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_sg_template_version_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "sg_template_version_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_sg_template_version_create(*_bf_args, **_bf_kwargs)
_bf_friction_sg_template_version_create.blobfish_original = _bf_orig_sg_template_version_create
sg_template_version_create = _bf_friction_sg_template_version_create
