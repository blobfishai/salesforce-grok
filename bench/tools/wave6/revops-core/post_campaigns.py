def post_campaigns(db_path='state.db', **kwargs):
    '''Create a Campaign (POST /campaigns)'''
    _missing = [p for p in ['title'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _n = cur.execute('SELECT COALESCE(MAX(rowid), 0) + 100 FROM "campaigns"').fetchone()[0] + 1
        _base = datetime.datetime(2026, 1, 5, 9, 0, 0)
        _ts = (_base + datetime.timedelta(minutes=_n)).strftime('%Y-%m-%dT%H:%M:%SZ')
        _cols = ['"id"']
        _vals = [_n]
        if kwargs.get('categories') is not None:
            _cols.append('"categories"')
            _vals.append(json.dumps(kwargs['categories']) if not isinstance(kwargs['categories'], str) else kwargs['categories'])
        if kwargs.get('custom_unsubscribe_url') is not None:
            _cols.append('"custom_unsubscribe_url"')
            _vals.append(str(kwargs['custom_unsubscribe_url']))
        if kwargs.get('editor') is not None:
            _cols.append('"editor"')
            _vals.append(str(kwargs['editor']))
        if kwargs.get('html_content') is not None:
            _cols.append('"html_content"')
            _vals.append(str(kwargs['html_content']))
        if kwargs.get('ip_pool') is not None:
            _cols.append('"ip_pool"')
            _vals.append(str(kwargs['ip_pool']))
        if kwargs.get('list_ids') is not None:
            _cols.append('"list_ids"')
            _vals.append(json.dumps(kwargs['list_ids']) if not isinstance(kwargs['list_ids'], str) else kwargs['list_ids'])
        if kwargs.get('plain_content') is not None:
            _cols.append('"plain_content"')
            _vals.append(str(kwargs['plain_content']))
        if kwargs.get('segment_ids') is not None:
            _cols.append('"segment_ids"')
            _vals.append(json.dumps(kwargs['segment_ids']) if not isinstance(kwargs['segment_ids'], str) else kwargs['segment_ids'])
        if kwargs.get('sender_id') is not None:
            _cols.append('"sender_id"')
            _vals.append(int(kwargs['sender_id']))
        if kwargs.get('subject') is not None:
            _cols.append('"subject"')
            _vals.append(str(kwargs['subject']))
        if kwargs.get('suppression_group_id') is not None:
            _cols.append('"suppression_group_id"')
            _vals.append(int(kwargs['suppression_group_id']))
        if kwargs.get('title') is not None:
            _cols.append('"title"')
            _vals.append(str(kwargs['title']))
        _cols.append('"created_at"')
        _vals.append(_ts)
        if '"status"' not in _cols:
            _cols.append('"status"')
            _vals.append('open')
        _sql = 'INSERT INTO "campaigns" (' + ', '.join(_cols) + ') VALUES (' + ', '.join(['?'] * len(_vals)) + ')'
        try:
            cur.execute(_sql, _vals)
        except sqlite3.IntegrityError:
            conn.rollback()
            return {'error': 'conflict: duplicate key', 'status': 409}
        conn.commit()
        _row = cur.execute('SELECT * FROM "campaigns" WHERE "id" = ?', [_vals[0]]).fetchone()
        _out = dict(_row)
        for _jc in ['categories', 'list_ids', 'segment_ids']:
            if isinstance(_out.get(_jc), str) and _out[_jc][:1] in ('[', '{'):
                try:
                    _out[_jc] = json.loads(_out[_jc])
                except Exception:
                    pass
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_campaigns = post_campaigns
def _bf_friction_post_campaigns(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_campaigns(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_campaigns|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
            _bf_kinds = ["service_unavailable","rate_limited","stale_reference","permission_denied"]
            _bf_messages = {"service_unavailable":"The service is temporarily unavailable (upstream timeout while processing the request). Please retry.","rate_limited":"Rate limit exceeded for this operation. Wait a moment and retry.","stale_reference":"The referenced record could not be loaded — the reference may be stale or recently changed. Re-fetch the latest data and retry.","permission_denied":"Permission denied for this operation — your access grant is still propagating. Retry, or use an alternative workflow if one is available."}
            _bf_kind = _bf_kinds[int(_bf_digest[8:12], 16) % len(_bf_kinds)]
            return {"success": False, "error": _bf_kind, "message": _bf_messages[_bf_kind], "retryable": True}
    return _bf_orig_post_campaigns(*_bf_args, **_bf_kwargs)
_bf_friction_post_campaigns.blobfish_original = _bf_orig_post_campaigns
post_campaigns = _bf_friction_post_campaigns
