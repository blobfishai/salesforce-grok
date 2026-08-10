"""Look up marketing_content_asset with marketing_campaigns context"""
import sqlite3

def lookup_marketing_content_asset_with_marketing_campaigns(db_path: str, id: int) -> dict:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM marketing_content_assets WHERE id = ?", [id]).fetchone()
    if not row:
        conn.close()
        return {"error": f"marketing_content_asset {id} not found"}
    result = dict(row)
    parent = conn.execute("SELECT * FROM marketing_campaigns WHERE id = ?", [row["campaign_id"]]).fetchone()
    result["marketing_campaigns"] = dict(parent) if parent else None
    conn.close()
    return result

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_lookup_marketing_content_asset_with_marketing_campaigns = lookup_marketing_content_asset_with_marketing_campaigns
def _bf_friction_lookup_marketing_content_asset_with_marketing_campaigns(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_lookup_marketing_content_asset_with_marketing_campaigns(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "lookup_marketing_content_asset_with_marketing_campaigns|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("b4b1f3b12afc2250|" + _bf_sig).encode("utf-8")).hexdigest()
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
            _bf_kinds = ["service_unavailable","rate_limited","stale_reference"]
            _bf_messages = {"service_unavailable":"The service is temporarily unavailable (upstream timeout while processing the request). Please retry.","rate_limited":"Rate limit exceeded for this operation. Wait a moment and retry.","stale_reference":"The referenced record could not be loaded — the reference may be stale or recently changed. Re-fetch the latest data and retry."}
            _bf_kind = _bf_kinds[int(_bf_digest[8:12], 16) % len(_bf_kinds)]
            return {"success": False, "error": _bf_kind, "message": _bf_messages[_bf_kind], "retryable": True}
    return _bf_orig_lookup_marketing_content_asset_with_marketing_campaigns(*_bf_args, **_bf_kwargs)
_bf_friction_lookup_marketing_content_asset_with_marketing_campaigns.blobfish_original = _bf_orig_lookup_marketing_content_asset_with_marketing_campaigns
lookup_marketing_content_asset_with_marketing_campaigns = _bf_friction_lookup_marketing_content_asset_with_marketing_campaigns
