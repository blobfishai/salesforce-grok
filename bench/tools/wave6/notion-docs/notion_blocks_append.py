def notion_blocks_append(db_path='state.db', **kwargs):
    import sqlite3, json, hashlib, datetime
    block_id = kwargs.get('block_id')
    children = kwargs.get('children')
    if not block_id or children is None:
        return {"object": "error", "status": 400, "code": "validation_error",
                "message": "body failed validation: path.block_id and body.children should be defined."}
    if isinstance(children, str):
        try:
            children = json.loads(children)
        except Exception:
            return {"object": "error", "status": 400, "code": "validation_error",
                    "message": "body.children failed validation: value is not valid JSON."}
    if isinstance(children, dict):
        children = [children]
    if not isinstance(children, list):
        return {"object": "error", "status": 400, "code": "validation_error",
                "message": "body.children failed validation: should be an array of block objects."}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    parent = conn.execute("SELECT id FROM notion_pages WHERE id = ?", (block_id,)).fetchone()
    if parent is None:
        parent = conn.execute("SELECT page_id AS id FROM notion_blocks WHERE id = ?", (block_id,)).fetchone()
    if parent is None:
        conn.close()
        return {"object": "error", "status": 404, "code": "object_not_found",
                "message": "Could not find block with ID: " + str(block_id) + "."}
    page_id = parent['id']
    row = conn.execute("SELECT COALESCE(MAX(sort_order), 0) AS m FROM notion_blocks WHERE page_id = ?", (page_id,)).fetchone()
    order = row['m']
    now = datetime.datetime(2026, 8, 10, 9, 0, 0).isoformat() + '.000Z'
    supported = ('paragraph', 'heading_1', 'heading_2', 'heading_3',
                 'bulleted_list_item', 'numbered_list_item', 'to_do', 'quote', 'callout')
    created = []
    for child in children:
        if not isinstance(child, dict):
            continue
        btype = child.get('type')
        if btype is None:
            for k in child:
                if k in supported:
                    btype = k
                    break
        if btype not in supported:
            btype = 'paragraph'
        body = child.get(btype) if isinstance(child.get(btype), dict) else {}
        text = child.get('text')
        if text is None:
            parts = []
            for rt in (body.get('rich_text') or []):
                if isinstance(rt, dict):
                    parts.append(((rt.get('text') or {}).get('content')) or rt.get('plain_text') or '')
            text = ''.join(parts)
        checked = 1 if (body.get('checked') or child.get('checked')) else 0
        order += 1
        bid = 'blk-' + hashlib.sha1((str(page_id) + '|' + str(order) + '|' + str(text)).encode('utf-8')).hexdigest()[:12]
        conn.execute("INSERT INTO notion_blocks (id, page_id, type, text, checked, sort_order) VALUES (?, ?, ?, ?, ?, ?)",
                     (bid, page_id, btype, text or '', checked, order))
        created.append({"object": "block", "id": bid, "type": btype, "text": text or '',
                        "checked": checked, "sort_order": order,
                        "parent": {"type": "page_id", "page_id": page_id}})
    conn.execute("UPDATE notion_pages SET last_edited_time = ? WHERE id = ?", (now, page_id))
    conn.commit()
    conn.close()
    return {"object": "list", "results": created, "has_more": False, "next_cursor": None, "type": "block"}

_env_orig_notion_blocks_append = notion_blocks_append
def _env_notion_blocks_append(db_path='state.db', **kwargs):
    _r = _env_orig_notion_blocks_append(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'object': 'list', 'results': _r['items'], 'next_cursor': None, 'has_more': False}
    if 'error' in _r and _r.get('status') == 404:
        return {'object': 'error', 'status': 404, 'code': 'object_not_found', 'message': str(_r.get('error', ''))}
    if 'error' in _r and _r.get('status') == 400:
        return {'object': 'error', 'status': 400, 'code': 'validation_error', 'message': str(_r.get('error', ''))}
    return _r
notion_blocks_append = _env_notion_blocks_append

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notion_blocks_append = notion_blocks_append
def _bf_friction_notion_blocks_append(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notion_blocks_append(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notion_blocks_append|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notion_blocks_append(*_bf_args, **_bf_kwargs)
_bf_friction_notion_blocks_append.blobfish_original = _bf_orig_notion_blocks_append
notion_blocks_append = _bf_friction_notion_blocks_append
