def sg_stats_by_category(db_path='state.db', **kwargs):
    import sqlite3, datetime
    categories = kwargs.get('categories')
    start_date = kwargs.get('start_date')
    end_date = kwargs.get('end_date')
    if not categories:
        return {"errors": [{"field": "categories", "message": "The categories to retrieve statistics for are required: a comma-separated list or an array of category names."}]}
    if not start_date:
        return {"errors": [{"field": "start_date", "message": "The starting date of the statistics to retrieve is required. Must follow format YYYY-MM-DD."}]}
    def _parse(value):
        try:
            return datetime.datetime.strptime(value, '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return None
    if _parse(start_date) is None:
        return {"errors": [{"field": "start_date", "message": "Date must follow format YYYY-MM-DD; got '%s'." % start_date}]}
    if end_date is None:
        end_date = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
    if _parse(end_date) is None:
        return {"errors": [{"field": "end_date", "message": "Date must follow format YYYY-MM-DD; got '%s'." % end_date}]}
    if isinstance(categories, str):
        cats = [c.strip() for c in categories.split(',') if c.strip()]
    elif isinstance(categories, list):
        cats = [str(c).strip() for c in categories if str(c).strip()]
    else:
        return {"errors": [{"field": "categories", "message": "categories must be a string or an array of category names."}]}
    if not cats:
        return {"errors": [{"field": "categories", "message": "No valid category names were provided."}]}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    buckets = {}
    for cat in cats:
        rows = cur.execute(
            "SELECT substr(sent_at, 1, 10) AS d, status FROM sg_mail_sends WHERE categories LIKE ? AND substr(sent_at, 1, 10) >= ? AND substr(sent_at, 1, 10) <= ?",
            ('%' + cat + '%', start_date, end_date)).fetchall()
        for r in rows:
            day = buckets.setdefault(r["d"], {})
            m = day.setdefault(cat, {"requests": 0, "delivered": 0, "drops": 0, "bounces": 0})
            m["requests"] = m["requests"] + 1
            if r["status"] == 'delivered':
                m["delivered"] = m["delivered"] + 1
            elif r["status"] == 'dropped':
                m["drops"] = m["drops"] + 1
            elif r["status"] == 'bounced':
                m["bounces"] = m["bounces"] + 1
    historical = cur.execute(
        "SELECT * FROM category_stats WHERE date >= ? AND date <= ?",
        (start_date, end_date)).fetchall()
    conn.close()
    result = []
    for day in sorted(buckets):
        stats = [{"type": "category", "name": cat, "metrics": buckets[day][cat]} for cat in sorted(buckets[day])]
        result.append({"date": day, "stats": stats})
    return {"start_date": start_date, "end_date": end_date, "result": result, "category_stat_records": [dict(h) for h in historical]}

_env_orig_sg_stats_by_category = sg_stats_by_category
def _env_sg_stats_by_category(db_path='state.db', **kwargs):
    _r = _env_orig_sg_stats_by_category(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'result': _r['items'], '_metadata': {'count': _r['count']}}
    if 'error' in _r and _r.get('status') == 404:
        return {'errors': [{'message': str(_r.get('error', '')), 'field': None, 'help': None}]}
    if 'error' in _r and _r.get('status') == 400:
        return {'errors': [{'message': str(_r.get('error', '')), 'field': None, 'help': None}]}
    return _r
sg_stats_by_category = _env_sg_stats_by_category

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_sg_stats_by_category = sg_stats_by_category
def _bf_friction_sg_stats_by_category(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_sg_stats_by_category(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "sg_stats_by_category|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_sg_stats_by_category(*_bf_args, **_bf_kwargs)
_bf_friction_sg_stats_by_category.blobfish_original = _bf_orig_sg_stats_by_category
sg_stats_by_category = _bf_friction_sg_stats_by_category
