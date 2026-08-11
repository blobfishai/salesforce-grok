
def lead_merge(db_path='state.db', **kwargs):
    '''Merge a duplicate lead into a master lead, re-parenting child records and
    deleting the loser (POST /services/data/v62.0/composite/sobjects/Lead/merge).'''
    import sqlite3, datetime
    master = kwargs.get('master_lead_id')
    victim = kwargs.get('duplicate_lead_id')
    if not master or not victim:
        return [{'message': 'missing required parameters: master_lead_id, duplicate_lead_id',
                 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    if str(master) == str(victim):
        return [{'message': 'a lead cannot be merged into itself', 'errorCode': 'INVALID_CROSS_REFERENCE_KEY'}]
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        m = conn.execute('SELECT * FROM sales_leads WHERE id = ?', (str(master),)).fetchone()
        v = conn.execute('SELECT * FROM sales_leads WHERE id = ?', (str(victim),)).fetchone()
        if m is None or v is None:
            return [{'message': 'lead not found', 'errorCode': 'NOT_FOUND'}]
        m, v = dict(m), dict(v)
        # survivorship: master wins on conflict, but fills its blanks from the victim
        updates, filled = [], []
        for key, val in v.items():
            if key in ('id', 'lead_number'):
                continue
            if (m.get(key) in (None, '', 0)) and val not in (None, ''):
                updates.append(key)
                filled.append((key, val))
        if updates:
            conn.execute('UPDATE sales_leads SET ' + ', '.join('"' + k + '" = ?' for k in updates) +
                         ' WHERE id = ?', [val for _, val in filled] + [str(master)])
        # re-parent children before the delete so nothing is orphaned
        reparented = conn.execute('UPDATE sales_opportunities SET lead_id = ? WHERE lead_id = ?',
                                  (str(master), str(victim))).rowcount
        conn.execute('DELETE FROM sales_leads WHERE id = ?', (str(victim),))
        conn.execute('INSERT INTO lead_merge_log (id, master_lead_id, duplicate_lead_id, fields_filled, '
                     'children_reparented, merged_at) VALUES (?, ?, ?, ?, ?, ?)',
                     ('mrg_' + str(master) + '_' + str(victim), str(master), str(victim),
                      ','.join(k for k, _ in filled), reparented,
                      datetime.datetime.now(datetime.timezone.utc).isoformat()))
        conn.commit()
        row = dict(conn.execute('SELECT * FROM sales_leads WHERE id = ?', (str(master),)).fetchone())
        row['merged'] = {'duplicate_lead_id': str(victim), 'fields_filled': [k for k, _ in filled],
                         'children_reparented': reparented}
        return row
    finally:
        conn.close()

_env_orig_lead_merge = lead_merge
def _env_lead_merge(db_path='state.db', **kwargs):
    _r = _env_orig_lead_merge(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
    if 'error' in _r and _r.get('status') == 400:
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    return _r
lead_merge = _env_lead_merge

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_lead_merge = lead_merge
def _bf_friction_lead_merge(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_lead_merge(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "lead_merge|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_lead_merge(*_bf_args, **_bf_kwargs)
_bf_friction_lead_merge.blobfish_original = _bf_orig_lead_merge
lead_merge = _bf_friction_lead_merge
