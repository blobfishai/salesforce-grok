"""Update company_finance_handoffs status with validation"""
import sqlite3

def update_company_finance_handoffs_status(db_path: str, id: int, new_status: str) -> dict:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM "company_finance_handoffs" WHERE "id" = ?', [id]).fetchone()
    if not row:
        conn.close()
        return {"error": f"company finance handoffs {id} not found"}
    valid = ["queued", "linked", "verified", "completed"]
    if valid and new_status not in valid:
        conn.close()
        return {"error": f"Invalid status '{new_status}'. Valid: {valid}"}
    old_status = row['status']
    conn.execute('UPDATE "company_finance_handoffs" SET "status" = ? WHERE "id" = ?', [new_status, id])
    conn.commit()
    conn.close()
    return {"updated": True, "id": id, "table": "company_finance_handoffs", "old_status": old_status, "new_status": new_status}

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_update_company_finance_handoffs_status = update_company_finance_handoffs_status
def _bf_friction_update_company_finance_handoffs_status(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_update_company_finance_handoffs_status(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "update_company_finance_handoffs_status|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_update_company_finance_handoffs_status(*_bf_args, **_bf_kwargs)
_bf_friction_update_company_finance_handoffs_status.blobfish_original = _bf_orig_update_company_finance_handoffs_status
update_company_finance_handoffs_status = _bf_friction_update_company_finance_handoffs_status
