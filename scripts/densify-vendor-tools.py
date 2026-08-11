#!/usr/bin/env python3
"""Densify vendor MCP tool surfaces from world/blobfish-wave6/tool-specs/*.json.

Does three things in one deterministic, additive-except-prune pass:

1. PRUNE — removes the domain-irrelevant tools listed in PRUNED (cross-domain
   spec-mounting noise: Stripe Climate/Issuing/Identity/Connect, Slack EKM /
   emoji / invite / app admin, SendGrid IP administration, Intercom away-status).
   Every removal was verified reference-free against tasks, verifiers,
   reference_rollout and trajectories. Backing TABLES are kept — verifier
   baselines hash all tables. Ledger written to tool-specs/_pruned.json.

2. GENERATE — per-vendor specs (see tool-specs/SPEC-FORMAT.md) become
   param-respecting Python tool sources (parameterized SQL over SQLite) with the
   standard blobfish friction wrapper AND a 1:1 vendor response envelope:
   Stripe {"object":"list","data":[...]}, Slack {"ok":true,...}, Google
   {"kind":"calendar#..."}, PagerDuty {"incidents":[...],"more":false}, Notion
   {"object":"list","results":[...]}, GitHub bare arrays + {"message":"Not
   Found"}, NetSuite {"items":[...],"hasMore":false}, Jira {"values"/"issues"},
   SendGrid {"result":[...]}. Errors use each vendor's real error format.
   Custom sources pass through untouched unless they return the recognizable
   built-in shapes ({'items','count'} / {'error','status'}), which get enveloped.

   Idempotent: spec entries already present in world.json are skipped, so a new
   spec applies as a delta against an already-densified world.

3. MIRROR — patches world.json (package + top-level copy, byte-stable
   serialization), regenerates tools/<ns>.py + tools.py, updates
   mcp-assets.json tool_names/target_tables.

Modes:
  --check    regenerate mirrors from the CURRENT world.json only and diff
             against disk (validates byte-identical codegen; touches nothing)
  (default)  full run: prune + generate + mirror; refuses on validation errors
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, "world", "blobfish-wave6", "package", "sbx_291042075d7547f4")
TOP_WORLD = os.path.join(ROOT, "world", "blobfish-wave6", "world.json")
SPECS_DIR = os.path.join(ROOT, "world", "blobfish-wave6", "tool-specs")

IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
FRICTION_KEY = "3ba25889bd4c5d1d"

PRUNED = {
    "post_climate_orders": "Stripe Climate (carbon removal) — no GTM workflow",
    "get_issuing_authorizations": "Stripe Issuing (card platform) — no GTM workflow",
    "post_test_helpers_issuing_authorizations": "Stripe Issuing test helper — no GTM workflow",
    "post_identity_verification_sessions": "Stripe Identity (consumer KYC) — no SOP references it",
    "post_account_links": "Stripe Connect onboarding — marketplace infra, not B2B billing",
    "post_account_sessions": "Stripe Connect embedded sessions — marketplace infra",
    "get_accounts_account_capabilities": "Stripe Connect capabilities — marketplace infra",
    "get_customers_customer_bank_accounts": "Stripe customer bank accounts — no payment-method workflow",
    "get_application_fees": "Stripe Connect platform fees — marketplace infra",
    "admin_conversations_ekm_list_original_connected_channel_info": "Slack EKM key management — enterprise-security noise",
    "admin_conversations_restrict_access_list_groups": "Slack IDP group ACLs — enterprise-security noise",
    "admin_conversations_get_conversation_prefs": "Slack channel prefs — config noise (also the param-ignoring fidelity bug)",
    "admin_invite_requests_list": "Slack workspace invite admin — no GTM workflow",
    "admin_invite_requests_approved_list": "Slack workspace invite admin — no GTM workflow",
    "admin_invite_requests_denied_list": "Slack workspace invite admin — no GTM workflow",
    "admin_apps_approved_list": "Slack app management — no GTM workflow",
    "admin_apps_requests_list": "Slack app management — no GTM workflow",
    "admin_apps_restricted_list": "Slack app management — no GTM workflow",
    "admin_emoji_list": "Slack emoji admin (mounted on the ERP vendor!) — noise",
    "admin_emoji_add": "Slack emoji admin — noise",
    "admin_emoji_rename": "Slack emoji admin — noise",
    "get_ips_assigned": "SendGrid IP administration — deliverability config noise",
    "get_access_settings_activity": "SendGrid IP access audit log — security noise",
    "get_tracking_settings_click": "SendGrid click-tracking settings read — config noise",
    "list_away_status_reasons": "Intercom away-status config — no GTM workflow",
    "files_remote_add": "Slack files.remote registration — no workflow references it",
}

FRICTION = '''
# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig___NAME__ = __NAME__
def _bf_friction___NAME__(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig___NAME__(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "__NAME__|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("__KEY__|" + _bf_sig).encode("utf-8")).hexdigest()
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
    return _bf_orig___NAME__(*_bf_args, **_bf_kwargs)
_bf_friction___NAME__.blobfish_original = _bf_orig___NAME__
__NAME__ = _bf_friction___NAME__
'''.lstrip("\n")

# 1:1 response envelopes per namespace. Placeholders: {rk} response key,
# {sing} singular resource, {table}, {idp} id param, {idc} id column.
# 'single': None means the vendor returns the bare resource (pass-through).
ENVELOPES = {
    "stripe": {
        "list": "{{'object': 'list', 'url': '/v1/{table}', 'has_more': False, 'data': _r['items']}}",
        "nf": "{{'error': {{'type': 'invalid_request_error', 'code': 'resource_missing', 'message': str(_r.get('error', ''))}}}}",
        "mp": "{{'error': {{'type': 'invalid_request_error', 'code': 'parameter_missing', 'message': str(_r.get('error', ''))}}}}",
        "deleted": "{{'id': _r.get('{idc}'), 'object': '{sing}', 'deleted': True}}",
        "single": "_r['object'] = '{sing}'",
    },
    "slack": {
        "list": "{{'ok': True, '{rk}': _r['items'], 'response_metadata': {{'next_cursor': ''}}}}",
        "nf": "{{'ok': False, 'error': str(_r.get('error') or '{sing} not found').replace(' not found', '_not_found').replace(' ', '_')}}",
        "mp": "{{'ok': False, 'error': 'invalid_arguments', 'response_metadata': {{'messages': [str(_r.get('error', ''))]}}}}",
        "deleted": "{{'ok': True}}",
        "single": "_r = {{'ok': True, '{sing}': _r}}",
    },
    "email": {
        "list": "{{'result': _r['items'], '_metadata': {{'count': _r['count']}}}}",
        "nf": "{{'errors': [{{'message': str(_r.get('error', '')), 'field': None, 'help': None}}]}}",
        "mp": "{{'errors': [{{'message': str(_r.get('error', '')), 'field': None, 'help': None}}]}}",
        "deleted": "{{}}",
        "single": None,
    },
    "calendar": {
        "list": "{{'kind': 'calendar#{rk}', 'items': _r['items']}}",
        "nf": "{{'error': {{'errors': [{{'domain': 'global', 'reason': 'notFound', 'message': str(_r.get('error', ''))}}], 'code': 404, 'message': str(_r.get('error', ''))}}}}",
        "mp": "{{'error': {{'errors': [{{'domain': 'global', 'reason': 'required', 'message': str(_r.get('error', ''))}}], 'code': 400, 'message': str(_r.get('error', ''))}}}}",
        "deleted": "{{}}",
        "single": "_r['kind'] = 'calendar#{sing}'",
    },
    "erp": {
        "list": "{{'items': _r['items'], 'count': _r['count'], 'hasMore': False, 'totalResults': _r['count'], 'offset': 0}}",
        "nf": "{{'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.4', 'title': 'Not Found', 'status': 404, 'o:errorDetails': [{{'detail': str(_r.get('error', '')), 'o:errorCode': 'RCRD_DSNT_EXIST'}}]}}",
        "mp": "{{'type': 'https://www.rfc-editor.org/rfc/rfc7231#section-6.5.1', 'title': 'Bad Request', 'status': 400, 'o:errorDetails': [{{'detail': str(_r.get('error', '')), 'o:errorCode': 'USER_ERROR'}}]}}",
        "deleted": "{{}}",
        "single": "_r['links'] = []",
    },
    "jira": {
        "list": "{{'values': _r['items'], 'total': _r['count'], 'startAt': 0, 'maxResults': _r['count'], 'isLast': True}}",
        "list_issues": "{{'issues': _r['items'], 'total': _r['count'], 'startAt': 0, 'maxResults': _r['count']}}",
        "nf": "{{'errorMessages': [str(_r.get('error', ''))], 'errors': {{}}}}",
        "mp": "{{'errorMessages': [str(_r.get('error', ''))], 'errors': {{}}}}",
        "deleted": "{{}}",
        "single": None,
    },
    "pagerduty": {
        "list": "{{'{rk}': _r['items'], 'limit': _r['count'], 'offset': 0, 'more': False, 'total': _r['count']}}",
        "nf": "{{'error': {{'message': str(_r.get('error', '')), 'code': 2100}}}}",
        "mp": "{{'error': {{'message': str(_r.get('error', '')), 'code': 2001, 'errors': [str(_r.get('error', ''))]}}}}",
        "deleted": "{{}}",
        "single": "_r = {{'{sing}': _r}}",
    },
    "github": {
        "list": "_r['items']",
        "nf": "{{'message': 'Not Found', 'documentation_url': 'https://docs.github.com/rest', 'status': '404'}}",
        "mp": "{{'message': 'Validation Failed', 'errors': [{{'message': str(_r.get('error', ''))}}], 'status': '422'}}",
        "deleted": "{{}}",
        "single": None,
    },
    "salesforce": {
        # Salesforce REST: query results carry totalSize/done/records; sobject
        # reads return the bare record; errors are an array of {message,errorCode}.
        "list": "{{'totalSize': _r['count'], 'done': True, 'records': _r['items']}}",
        "nf": "[{{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}}]",
        "mp": "[{{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}}]",
        "deleted": "{{'id': _r.get('{idc}'), 'success': True, 'errors': []}}",
        "single": "_r['attributes'] = {{'type': '{sing}', 'url': '/services/data/v62.0/sobjects/{sing}/' + str(_r.get('{idc}', ''))}}",
    },
    "notion": {
        "list": "{{'object': 'list', 'results': _r['items'], 'next_cursor': None, 'has_more': False}}",
        "nf": "{{'object': 'error', 'status': 404, 'code': 'object_not_found', 'message': str(_r.get('error', ''))}}",
        "mp": "{{'object': 'error', 'status': 400, 'code': 'validation_error', 'message': str(_r.get('error', ''))}}",
        "deleted": "{{'object': '{sing}', 'id': _r.get('{idc}'), 'archived': True}}",
        "single": "_r['object'] = '{sing}'",
    },
}

PARAM_TYPE = {"string": "string", "integer": "integer", "number": "number",
              "boolean": "boolean", "object": "json", "array": "json"}
CREATE_STAMPS = ["created_at", "created", "created_time"]
UPDATE_STAMPS = ["updated_at", "updated", "last_edited_time"]


def die(msg):
    sys.stderr.write(f"ERROR: {msg}\n")
    sys.exit(1)


def esc_desc(desc):
    desc = desc.replace("\\", "\\\\").replace("'''", "'' '")
    return desc + " " if desc.endswith("'") else desc


def check_ident(name, what):
    if not IDENT.match(name or ""):
        die(f"{what} {name!r} is not a valid identifier")
    return name


def singular(word):
    return word[:-1] if word.endswith("s") else word


def response_key(t, ns):
    rk = t.get("response_key")
    if rk:
        return rk
    table = t["table"]
    for prefix in (ns + "_", "slack_", "pd_", "gh_", "jira_", "notion_", "erp_", "sg_", "cal_"):
        if table.startswith(prefix):
            return table[len(prefix):]
    return table


def env_exprs(t, ns):
    env = ENVELOPES.get(ns)
    if env is None:
        die(f"{t['name']}: no envelope config for namespace {ns!r}")
    rk = response_key(t, ns)
    subs = {"rk": rk, "sing": singular(rk), "table": t["table"],
            "idp": t.get("id_param", "id"), "idc": t.get("id_column", "id")}
    list_key = "list_issues" if (ns == "jira" and rk == "issues") else "list"
    out = {}
    for k in ("nf", "mp", "deleted"):
        out[k] = env[k].format(**subs)
    out["list"] = env[list_key].format(**subs)
    out["single"] = env["single"].format(**subs) if env["single"] else None
    return out


def missing_check(required, ns_mp):
    if not required:
        return ""
    plist = ", ".join(f"'{p}'" for p in required)
    return (f"    _missing = [p for p in [{plist}] if kwargs.get(p) is None]\n"
            "    if _missing:\n"
            "        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}\n"
            f"        return {ns_mp}\n")


def preamble(name, desc, required, ns_mp):
    return (f"def {name}(db_path='state.db', **kwargs):\n"
            f"    '''{esc_desc(desc)}'''\n"
            + missing_check(required, ns_mp)
            + "    import sqlite3, json, datetime, hashlib\n"
            "    conn = sqlite3.connect(db_path)\n"
            "    conn.row_factory = sqlite3.Row\n"
            "    cur = conn.cursor()\n"
            "    try:\n")


CLOSE = "    finally:\n        conn.close()\n"


def order_clause(cols, id_column):
    col = id_column if id_column in cols else ("id" if "id" in cols else None)
    return f' ORDER BY "{col}"' if col else " ORDER BY rowid"


def filters_block(t, cols):
    body = ""
    fmap = t.get("filter_map", {})
    for p in t.get("filters", []):
        col = check_ident(fmap.get(p, p), "filter column")
        if col not in cols:
            die(f"{t['name']}: filter column {col!r} not in table {t['table']!r}")
        body += (f"        if kwargs.get('{p}') is not None:\n"
                 f"            _where.append('\"{col}\" = ?')\n"
                 f"            _args.append(str(kwargs['{p}']))\n")
    return body


def gen_list(t, cols, env):
    body = preamble(t["name"], t["description"], t.get("required", []), env["mp"])
    body += "        _where, _args = [], []\n" + filters_block(t, cols)
    body += ("        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)\n"
             f"        _q = 'SELECT * FROM \"{t['table']}\"'\n"
             "        if _where:\n"
             "            _q += ' WHERE ' + ' AND '.join(_where)\n"
             f"        _q += '{order_clause(cols, t.get('id_column', 'id'))} LIMIT ?'\n"
             "        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]\n"
             "        _r = {'items': _rows, 'count': len(_rows)}\n"
             f"        return {env['list']}\n")
    return body + CLOSE


def not_found_block(t, env, ns):
    label = singular(response_key(t, ns))
    return ("        if _row is None:\n"
            f"            _r = {{'error': '{label} not found', 'status': 404}}\n"
            f"            return {env['nf']}\n")


def single_return(env):
    if env["single"] is None:
        return "        return _r\n"
    return f"        {env['single']}\n        return _r\n"


def gen_get(t, cols, env, ns):
    idp, idc = t["id_param"], t.get("id_column", "id")
    required = list(dict.fromkeys([idp] + t.get("required", [])))
    body = preamble(t["name"], t["description"], required, env["mp"])
    body += f"        _row = cur.execute('SELECT * FROM \"{t['table']}\" WHERE \"{idc}\" = ?', [str(kwargs['{idp}'])]).fetchone()\n"
    body += not_found_block(t, env, ns)
    body += "        _r = dict(_row)\n" + single_return(env)
    return body + CLOSE


def gen_create(t, cols, col_types, env):
    idc = t.get("id_column", "id")
    if idc not in cols:
        die(f"{t['name']}: id column {idc!r} not in table {t['table']!r}")
    numeric_id = "INT" in (col_types.get(idc) or "").upper()
    body = preamble(t["name"], t["description"], t.get("required", []), env["mp"])
    body += ("        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()\n"
             f"        _n = cur.execute('SELECT COUNT(*) FROM \"{t['table']}\"').fetchone()[0] + 1\n")
    mk = "_n" if numeric_id else f"'{t.get('id_prefix', '')}' + str(_n).zfill(4)"
    body += (f"        _id = {mk}\n"
             f"        while cur.execute('SELECT 1 FROM \"{t['table']}\" WHERE \"{idc}\" = ?', [_id]).fetchone() is not None:\n"
             "            _n += 1\n"
             f"            _id = {mk}\n"
             f"        _cols, _vals = ['{idc}'], [_id]\n")
    fmap = t.get("field_map", {})
    for p in t.get("fields", []):
        col = check_ident(fmap.get(p, p), "create column")
        if col not in cols:
            die(f"{t['name']}: create column {col!r} not in table {t['table']!r}")
        body += (f"        if kwargs.get('{p}') is not None:\n"
                 f"            _cols.append('{col}')\n"
                 f"            _v = kwargs['{p}']\n"
                 "            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)\n")
    for col, lit in (t.get("defaults") or {}).items():
        check_ident(col, "default column")
        if col not in cols:
            die(f"{t['name']}: default column {col!r} not in table {t['table']!r}")
        body += (f"        if '{col}' not in _cols:\n"
                 f"            _cols.append('{col}')\n"
                 f"            _vals.append({lit!r})\n")
    for col in CREATE_STAMPS + UPDATE_STAMPS:
        if col in cols and col not in t.get("fields", []) and col not in (t.get("defaults") or {}):
            body += (f"        if '{col}' not in _cols:\n"
                     f"            _cols.append('{col}')\n"
                     "            _vals.append(_now)\n")
    body += (f"        cur.execute('INSERT INTO \"{t['table']}\" (' + ', '.join('\"' + c + '\"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)\n"
             "        conn.commit()\n"
             f"        _row = cur.execute('SELECT * FROM \"{t['table']}\" WHERE \"{idc}\" = ?', [_id]).fetchone()\n"
             f"        _r = dict(_row) if _row else {{'{idc}': _id}}\n" + single_return(env))
    return body + CLOSE


def gen_update(t, cols, env, ns):
    idp, idc = t["id_param"], t.get("id_column", "id")
    required = list(dict.fromkeys([idp] + t.get("required", [])))
    body = preamble(t["name"], t["description"], required, env["mp"])
    body += f"        _row = cur.execute('SELECT * FROM \"{t['table']}\" WHERE \"{idc}\" = ?', [str(kwargs['{idp}'])]).fetchone()\n"
    body += not_found_block(t, env, ns)
    body += "        _sets, _args = [], []\n"
    fmap = t.get("field_map", {})
    for p in t.get("set_fields", []):
        col = check_ident(fmap.get(p, p), "update column")
        if col not in cols:
            die(f"{t['name']}: update column {col!r} not in table {t['table']!r}")
        body += (f"        if kwargs.get('{p}') is not None:\n"
                 f"            _sets.append('\"{col}\" = ?')\n"
                 f"            _v = kwargs['{p}']\n"
                 "            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)\n")
    for col in UPDATE_STAMPS:
        if col in cols and col not in t.get("set_fields", []):
            body += (f"        _sets.append('\"{col}\" = ?')\n"
                     "        _args.append(datetime.datetime.now(datetime.timezone.utc).isoformat())\n")
            break
    body += ("        if _sets:\n"
             f"            cur.execute('UPDATE \"{t['table']}\" SET ' + ', '.join(_sets) + ' WHERE \"{idc}\" = ?', _args + [str(kwargs['{idp}'])])\n"
             "            conn.commit()\n"
             f"        _row = cur.execute('SELECT * FROM \"{t['table']}\" WHERE \"{idc}\" = ?', [str(kwargs['{idp}'])]).fetchone()\n"
             "        _r = dict(_row)\n" + single_return(env))
    return body + CLOSE


def gen_delete(t, cols, env, ns):
    idp, idc = t["id_param"], t.get("id_column", "id")
    required = list(dict.fromkeys([idp] + t.get("required", [])))
    body = preamble(t["name"], t["description"], required, env["mp"])
    body += f"        _row = cur.execute('SELECT * FROM \"{t['table']}\" WHERE \"{idc}\" = ?', [str(kwargs['{idp}'])]).fetchone()\n"
    body += not_found_block(t, env, ns)
    body += (f"        cur.execute('DELETE FROM \"{t['table']}\" WHERE \"{idc}\" = ?', [str(kwargs['{idp}'])])\n"
             "        conn.commit()\n"
             f"        _r = {{'deleted': True, '{idc}': str(kwargs['{idp}'])}}\n"
             f"        return {env['deleted']}\n")
    return body + CLOSE


def gen_search(t, cols, env):
    qp = t.get("query_param", "query")
    required = list(dict.fromkeys([qp] + t.get("required", [])))
    scols = t.get("search_columns") or []
    for c in scols:
        check_ident(c, "search column")
        if c not in cols:
            die(f"{t['name']}: search column {c!r} not in table {t['table']!r}")
    if not scols:
        die(f"{t['name']}: search op needs search_columns")
    body = preamble(t["name"], t["description"], required, env["mp"])
    like = " OR ".join(f'\\"{c}\\" LIKE ?' for c in scols)
    body += (f"        _qv = '%' + str(kwargs['{qp}']) + '%'\n"
             f"        _where, _args = [\"({like})\"], [_qv] * {len(scols)}\n")
    body += filters_block(t, cols)
    body += ("        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)\n"
             f"        _q = 'SELECT * FROM \"{t['table']}\" WHERE ' + ' AND '.join(_where) + '{order_clause(cols, t.get('id_column', 'id'))} LIMIT ?'\n"
             "        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]\n"
             "        _r = {'items': _rows, 'count': len(_rows)}\n"
             f"        return {env['list']}\n")
    return body + CLOSE


def custom_envelope_wrapper(t, env):
    """Envelope customs ONLY when they return the recognizable built-in shapes;
    bespoke author-designed formats pass through untouched."""
    n = t["name"]
    return (f"_env_orig_{n} = {n}\n"
            f"def _env_{n}(db_path='state.db', **kwargs):\n"
            f"    _r = _env_orig_{n}(db_path, **kwargs)\n"
            "    if not isinstance(_r, dict):\n"
            "        return _r\n"
            "    if set(_r.keys()) == {'items', 'count'}:\n"
            f"        return {env['list']}\n"
            "    if 'error' in _r and _r.get('status') == 404:\n"
            f"        return {env['nf']}\n"
            "    if 'error' in _r and _r.get('status') == 400:\n"
            f"        return {env['mp']}\n"
            "    return _r\n"
            f"{n} = _env_{n}\n")


def generate_source(t, ns, table_cols, table_types):
    op = t["op"]
    env = env_exprs(t, ns)
    if op == "custom":
        src = t["custom_source"].rstrip("\n") + "\n"
        if f"def {t['name']}(db_path" not in src:
            die(f"{t['name']}: custom_source must define def {t['name']}(db_path='state.db', **kwargs)")
        src += "\n" + custom_envelope_wrapper(t, env)
    else:
        cols = table_cols.get(t["table"])
        if cols is None:
            die(f"{t['name']}: unknown table {t['table']!r}")
        if op == "list":
            src = gen_list(t, cols, env)
        elif op == "get":
            src = gen_get(t, cols, env, ns)
        elif op == "create":
            src = gen_create(t, cols, table_types.get(t["table"], {}), env)
        elif op == "update":
            src = gen_update(t, cols, env, ns)
        elif op == "delete":
            src = gen_delete(t, cols, env, ns)
        elif op == "search":
            src = gen_search(t, cols, env)
        else:
            die(f"{t['name']}: unknown op {op!r}")
    src += "\n" + FRICTION.replace("__NAME__", t["name"]).replace("__KEY__", FRICTION_KEY)
    try:
        compile(src, t["name"], "exec")
    except SyntaxError as e:
        die(f"{t['name']}: generated source does not compile: {e}\n---\n{src}")
    return src


def tool_entry(t, ns, src):
    op = t["op"]
    ttype = t.get("type") or ("write" if op in ("create", "update", "delete") else "read")
    if op == "custom" and "type" not in t:
        die(f"{t['name']}: custom op requires explicit type read|write")
    params, props = {}, {}
    for p, meta in t["params"].items():
        check_ident(p, "param")
        jtype = meta.get("type", "string")
        if jtype not in PARAM_TYPE:
            die(f"{t['name']}: param {p} has unknown type {jtype!r}")
        params[p] = PARAM_TYPE[jtype]
        props[p] = {"type": jtype, "description": meta.get("description", "")}
    schema = {"type": "object", "properties": props}
    required = list(t.get("required", []))
    if op in ("get", "update", "delete") and t.get("id_param"):
        required = list(dict.fromkeys([t["id_param"]] + required))
    if op == "search":
        required = list(dict.fromkeys([t.get("query_param", "query")] + required))
    for p in required:
        if p not in t["params"]:
            die(f"{t['name']}: required param {p!r} missing from params")
    if required:
        schema["required"] = required
    schema["additionalProperties"] = False
    tables = list(dict.fromkeys([t["table"]] + t.get("extra_tables", [])))
    return {"name": t["name"], "mcp_name": f"{ns}.{t['name']}", "asset_namespace": ns,
            "description": t["description"], "type": ttype, "target_tables": tables,
            "parameters": params, "input_schema": schema, "source": src}


def module_text(ns, tools):
    names = ", ".join(t["name"] for t in tools)
    tables = ", ".join(dict.fromkeys(tb for t in tools for tb in t.get("target_tables", [])))
    head = (f'"""Executable {ns.upper()} tool module\n\n'
            "Inspect each function: SQLite helpers are local fixtures; network-backed functions call their declared endpoint.\n"
            f"Tools: {names}\nTables: {tables}\n\"\"\"\nimport json, sqlite3\n")
    return head + "".join(t["source"].rstrip("\n") + "\n\n" for t in tools)


def router_text(world, module_order):
    by_ns = {}
    for t in world["tools"]:
        by_ns.setdefault(t["asset_namespace"], []).append(t)
    lines = ['"""Tool router — re-exports all per-asset tool modules."""', "import json, sqlite3", ""]
    for ns in module_order:
        names = ", ".join(t["name"] for t in by_ns.get(ns, []))
        if names:
            lines.append(f"from tools.{ns} import {names}")
    lines.append("")
    lines.append("TOOL_REGISTRY = {")
    for t in world["tools"]:
        lines.append(f'    "{t["name"]}": {t["name"]},')
    lines.append("}")
    lines.append("")
    return "\n".join(lines) + "\n"


def existing_module_order():
    order = []
    with open(os.path.join(PKG, "tools.py")) as f:
        for line in f:
            m = re.match(r"from tools\.(\w+) import ", line)
            if m:
                order.append(m.group(1))
    return order


def write_mirrors(world, check_only):
    module_order = existing_module_order()
    by_ns = {}
    for t in world["tools"]:
        by_ns.setdefault(t["asset_namespace"], []).append(t)
    results = {}
    for ns, tools in by_ns.items():
        path = os.path.join(PKG, "tools", f"{ns}.py")
        text = module_text(ns, tools)
        if check_only:
            on_disk = open(path).read() if os.path.exists(path) else None
            results[f"tools/{ns}.py"] = "IDENTICAL" if on_disk == text else "DIFFERS"
        else:
            open(path, "w").write(text)
    rtext = router_text(world, module_order)
    if check_only:
        results["tools.py"] = "IDENTICAL" if open(os.path.join(PKG, "tools.py")).read() == rtext else "DIFFERS"
    else:
        open(os.path.join(PKG, "tools.py"), "w").write(rtext)
    return results


def dump_matching(obj, original_raw):
    text = json.dumps(obj, indent=1, ensure_ascii=False)
    if original_raw.endswith("\n") and not text.endswith("\n"):
        text += "\n"
    return text


def main():
    check_only = "--check" in sys.argv
    world_raw = open(os.path.join(PKG, "world.json")).read()
    world = json.loads(world_raw)

    if check_only:
        results = write_mirrors(world, True)
        rt = dump_matching(world, world_raw)
        results["world.json round-trip"] = "IDENTICAL" if rt == world_raw else "DIFFERS"
        for k, v in sorted(results.items()):
            print(f"{v:9}  {k}")
        sys.exit(0 if all(v == "IDENTICAL" for v in results.values()) else 1)

    registry = json.load(open(os.path.join(ROOT, "config", "mcp-servers.json")))
    spec_files = sorted(f for f in os.listdir(SPECS_DIR) if f.endswith(".json") and not f.startswith("_"))
    if not spec_files:
        die("no specs found")

    # ---- prune ----
    present = {t["name"] for t in world["tools"]}
    missing = [n for n in PRUNED if n not in present]
    if missing and len(missing) != len(PRUNED):
        die(f"prune list partially applied? absent: {missing}")
    pruned_entries = [t for t in world["tools"] if t["name"] in PRUNED]
    world["tools"] = [t for t in world["tools"] if t["name"] not in PRUNED]
    ledger = [{"name": t["name"], "mcp_name": t["mcp_name"], "asset_namespace": t["asset_namespace"],
               "target_tables": t["target_tables"], "reason": PRUNED[t["name"]]}
              for t in pruned_entries]
    if ledger:
        with open(os.path.join(SPECS_DIR, "_pruned.json"), "w") as f:
            json.dump({"comment": "Tools removed as domain-irrelevant (verified reference-free in tasks/verifiers/trajectories). Tables kept — verifier baselines hash all tables.",
                       "pruned": ledger}, f, indent=1, ensure_ascii=False)

    table_cols = {tb["name"]: [c["name"] for c in tb["columns"]] for tb in world["tables"]}
    table_types = {tb["name"]: {c["name"]: c.get("type", "TEXT") for c in tb["columns"]} for tb in world["tables"]}
    taken_tools = {t["name"] for t in world["tools"]}
    taken_tables = set(table_cols)

    new_tools, new_tables, per_vendor = [], [], {}
    skipped_tools = skipped_tables = 0
    refreshed_tables = []
    for fname in spec_files:
        spec = json.load(open(os.path.join(SPECS_DIR, fname)))
        vendor, ns = spec["vendor"], spec["namespace"]
        vconf = registry["vendors"].get(vendor)
        if not vconf or ns not in vconf["namespaces"]:
            die(f"{fname}: vendor {vendor!r} / namespace {ns!r} not in config/mcp-servers.json")
        for tb in spec.get("tables", []):
            check_ident(tb["name"], "table")
            if tb["name"] in taken_tables:
                # The table exists, but the spec still OWNS its seed data: refresh
                # the rows so a data correction in the spec reaches the world.
                # (Schema changes are not migrated — those need a new table.)
                existing = next((x for x in world["tables"] if x["name"] == tb["name"]), None)
                if existing is not None and tb.get("sample_rows") and existing.get("sample_rows") != tb["sample_rows"]:
                    existing["sample_rows"] = tb["sample_rows"]
                    existing["row_count"] = len(tb["sample_rows"])
                    refreshed_tables.append(tb["name"])
                else:
                    skipped_tables += 1   # already applied: this pass is a delta
                continue
            for c in tb["columns"]:
                check_ident(c["name"], f"column in {tb['name']}")
            taken_tables.add(tb["name"])
            table_cols[tb["name"]] = [c["name"] for c in tb["columns"]]
            table_types[tb["name"]] = {c["name"]: c.get("type", "TEXT") for c in tb["columns"]}
            new_tables.append({"name": tb["name"],
                               "description": tb.get("description", f"{tb['name']} records for the {vendor} mock service"),
                               "columns": tb["columns"], "row_count": len(tb.get("sample_rows", [])),
                               "sample_rows": tb.get("sample_rows", [])})
        for t in spec["tools"]:
            check_ident(t["name"], "tool")
            if t["name"] in taken_tools:
                skipped_tools += 1    # already applied: this pass is a delta
                continue
            taken_tools.add(t["name"])
            src = generate_source(t, ns, table_cols, table_types)
            entry = tool_entry(t, ns, src)
            for tb in entry["target_tables"]:
                if tb not in taken_tables:
                    die(f"{fname}: tool {t['name']} targets unknown table {tb!r}")
            new_tools.append(entry)
            per_vendor[vendor] = per_vendor.get(vendor, 0) + 1

    world["tools"].extend(new_tools)
    world["tables"].extend(new_tables)

    text = dump_matching(world, world_raw)
    open(os.path.join(PKG, "world.json"), "w").write(text)
    open(TOP_WORLD, "w").write(text)

    write_mirrors(world, False)

    assets_path = os.path.join(PKG, "mcp-assets.json")
    assets_raw = open(assets_path).read()
    assets = json.loads(assets_raw)
    pruned_mcp = {f'{t["asset_namespace"]}.{t["name"]}' for t in pruned_entries}
    ns_new = {}
    for t in new_tools:
        ns_new.setdefault(t["asset_namespace"], []).append(t)
    for asset in assets["assets"]:
        asset["tool_names"] = [n for n in asset["tool_names"] if n not in pruned_mcp]
        adds = ns_new.get(asset["namespace"], [])
        if adds:
            asset["tool_names"].extend(f'{a["asset_namespace"]}.{a["name"]}' for a in adds)
            seen = dict.fromkeys(asset.get("target_tables", []))
            for a in adds:
                seen.update(dict.fromkeys(a["target_tables"]))
            asset["target_tables"] = list(seen)
    open(assets_path, "w").write(dump_matching(assets, assets_raw))

    print(f"pruned {len(pruned_entries)} tools; added {len(new_tools)} tools, {len(new_tables)} tables "
          f"(skipped {skipped_tools} tools / {skipped_tables} tables already applied"
          + (f", refreshed rows in {len(refreshed_tables)}: {', '.join(refreshed_tables)}" if refreshed_tables else "")
          + ") -> "
          f"{len(world['tools'])} tools, {len(world['tables'])} tables total")
    for vendor in sorted(per_vendor):
        print(f"  {vendor}: +{per_vendor[vendor]}")


if __name__ == "__main__":
    main()
