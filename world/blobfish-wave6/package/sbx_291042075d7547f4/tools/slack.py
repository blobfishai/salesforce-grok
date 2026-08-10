"""Executable SLACK tool module

Inspect each function: SQLite helpers are local fixtures; network-backed functions call their declared endpoint.
Tools: chat_scheduled_messages_list, admin_conversations_rename, admin_conversations_create, conversations_create, conversations_list, conversations_info, conversations_history, conversations_replies, conversations_members, conversations_join, conversations_invite, conversations_archive, conversations_set_topic, conversations_set_purpose, chat_post_message, chat_update, chat_delete, chat_schedule_message, users_list, users_info, users_lookup_by_email, users_set_presence, reactions_add, reactions_remove, reactions_get, pins_add, pins_list, pins_remove, search_messages, usergroups_list, usergroups_create, usergroups_update, team_info, emoji_list
Tables: messages, admin_conversations, channels, slack_channel_members, slack_users, slack_scheduled_messages, slack_reactions, slack_pins, slack_usergroups, slack_team, admin_emojis
"""
import json, sqlite3
def chat_scheduled_messages_list(db_path='state.db', **kwargs):
    '''Returns a list of scheduled messages. (GET /chat.scheduledMessages.list)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "messages"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "bot_id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        return {'items': _rows, 'count': len(_rows)}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_chat_scheduled_messages_list = chat_scheduled_messages_list
def _bf_friction_chat_scheduled_messages_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_chat_scheduled_messages_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "chat_scheduled_messages_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_chat_scheduled_messages_list(*_bf_args, **_bf_kwargs)
_bf_friction_chat_scheduled_messages_list.blobfish_original = _bf_orig_chat_scheduled_messages_list
chat_scheduled_messages_list = _bf_friction_chat_scheduled_messages_list

def admin_conversations_rename(db_path='state.db', **kwargs):
    '''Rename a public or private channel. (POST /admin.conversations.rename)'''
    _missing = [p for p in ['channel_id', 'name'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _sets, _args = [], []
        if kwargs.get('name') is not None:
            _sets.append('"name" = ?')
            _args.append(str(kwargs['name']))
        if not _sets:
            return {'error': 'no updatable fields provided', 'status': 400}
        _args.append(str(kwargs.get('channel_id')))
        cur.execute('UPDATE "admin_conversations" SET ' + ', '.join(_sets) + ' WHERE "channel_id" = ?', _args)
        if cur.rowcount == 0:
            conn.rollback()
            return {'error': 'admin_conversation not found', 'status': 404}
        conn.commit()
        _row = cur.execute('SELECT * FROM "admin_conversations" WHERE "channel_id" = ?', [str(kwargs.get('channel_id'))]).fetchone()
        _out = dict(_row)
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_admin_conversations_rename = admin_conversations_rename
def _bf_friction_admin_conversations_rename(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_admin_conversations_rename(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "admin_conversations_rename|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_admin_conversations_rename(*_bf_args, **_bf_kwargs)
_bf_friction_admin_conversations_rename.blobfish_original = _bf_orig_admin_conversations_rename
admin_conversations_rename = _bf_friction_admin_conversations_rename

def admin_conversations_create(db_path='state.db', **kwargs):
    '''Create a public or private channel-based conversation. (POST /admin.conversations.create)'''
    _missing = [p for p in ['name', 'is_private'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _n = cur.execute('SELECT COALESCE(MAX(rowid), 0) + 100 FROM "admin_conversations"').fetchone()[0] + 1
        _base = datetime.datetime(2026, 1, 5, 9, 0, 0)
        _ts = (_base + datetime.timedelta(minutes=_n)).strftime('%Y-%m-%dT%H:%M:%SZ')
        _cols = ['"id"']
        _vals = [_n]
        if kwargs.get('name') is not None:
            _cols.append('"name"')
            _vals.append(str(kwargs['name']))
        if kwargs.get('description') is not None:
            _cols.append('"description"')
            _vals.append(str(kwargs['description']))
        if kwargs.get('is_private') is not None:
            _cols.append('"is_private"')
            _vals.append((1 if kwargs['is_private'] in (True, 'true', 1, '1') else 0))
        if kwargs.get('org_wide') is not None:
            _cols.append('"org_wide"')
            _vals.append((1 if kwargs['org_wide'] in (True, 'true', 1, '1') else 0))
        if kwargs.get('team_id') is not None:
            _cols.append('"team_id"')
            _vals.append(str(kwargs['team_id']))
        _cols.append('"created_at"')
        _vals.append(_ts)
        _sql = 'INSERT INTO "admin_conversations" (' + ', '.join(_cols) + ') VALUES (' + ', '.join(['?'] * len(_vals)) + ')'
        try:
            cur.execute(_sql, _vals)
        except sqlite3.IntegrityError:
            conn.rollback()
            return {'error': 'conflict: duplicate key', 'status': 409}
        conn.commit()
        _row = cur.execute('SELECT * FROM "admin_conversations" WHERE "id" = ?', [_vals[0]]).fetchone()
        _out = dict(_row)
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_admin_conversations_create = admin_conversations_create
def _bf_friction_admin_conversations_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_admin_conversations_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "admin_conversations_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_admin_conversations_create(*_bf_args, **_bf_kwargs)
_bf_friction_admin_conversations_create.blobfish_original = _bf_orig_admin_conversations_create
admin_conversations_create = _bf_friction_admin_conversations_create

def conversations_create(db_path='state.db', **kwargs):
    '''Initiates a public or private channel-based conversation (POST /conversations.create)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _n = cur.execute('SELECT COALESCE(MAX(rowid), 0) + 100 FROM "channels"').fetchone()[0] + 1
        _base = datetime.datetime(2026, 1, 5, 9, 0, 0)
        _ts = (_base + datetime.timedelta(minutes=_n)).strftime('%Y-%m-%dT%H:%M:%SZ')
        _cols = ['"id"']
        _vals = ['C' + str(_n).zfill(7) + '']
        if kwargs.get('name') is not None:
            _cols.append('"name"')
            _vals.append(str(kwargs['name']))
        if kwargs.get('is_private') is not None:
            _cols.append('"is_private"')
            _vals.append((1 if kwargs['is_private'] in (True, 'true', 1, '1') else 0))
        _sql = 'INSERT INTO "channels" (' + ', '.join(_cols) + ') VALUES (' + ', '.join(['?'] * len(_vals)) + ')'
        try:
            cur.execute(_sql, _vals)
        except sqlite3.IntegrityError:
            conn.rollback()
            return {'error': 'conflict: duplicate key', 'status': 409}
        conn.commit()
        _row = cur.execute('SELECT * FROM "channels" WHERE "id" = ?', [_vals[0]]).fetchone()
        _out = dict(_row)
        for _jc in ['accepted_user', 'creator', 'id', 'last_read', 'members', 'pending_shared', 'previous_names', 'purpose', 'topic']:
            if isinstance(_out.get(_jc), str) and _out[_jc][:1] in ('[', '{'):
                try:
                    _out[_jc] = json.loads(_out[_jc])
                except Exception:
                    pass
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_conversations_create = conversations_create
def _bf_friction_conversations_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_conversations_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "conversations_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
            _bf_kinds = ["service_unavailable","rate_limited","stale_reference"]
            _bf_messages = {"service_unavailable":"The service is temporarily unavailable (upstream timeout while processing the request). Please retry.","rate_limited":"Rate limit exceeded for this operation. Wait a moment and retry.","stale_reference":"The referenced record could not be loaded — the reference may be stale or recently changed. Re-fetch the latest data and retry."}
            _bf_kind = _bf_kinds[int(_bf_digest[8:12], 16) % len(_bf_kinds)]
            return {"success": False, "error": _bf_kind, "message": _bf_messages[_bf_kind], "retryable": True}
    return _bf_orig_conversations_create(*_bf_args, **_bf_kwargs)
_bf_friction_conversations_create.blobfish_original = _bf_orig_conversations_create
conversations_create = _bf_friction_conversations_create

def conversations_list(db_path='state.db', **kwargs):
    import sqlite3
    try:
        limit = int(kwargs.get('limit', 100))
    except (TypeError, ValueError):
        limit = 100
    types = str(kwargs.get('types') or 'public_channel')
    type_conds = []
    for t in [part.strip() for part in types.split(',') if part.strip()]:
        if t == 'public_channel':
            type_conds.append('(is_private = 0 AND is_mpim = 0)')
        elif t == 'private_channel':
            type_conds.append('(is_private = 1 AND is_mpim = 0)')
        elif t == 'mpim':
            type_conds.append('(is_mpim = 1)')
        else:
            return {'ok': False, 'error': 'invalid_types', 'status': 400, 'detail': 'types must be a comma-separated mix of public_channel, private_channel, mpim'}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    sql = 'SELECT id, name, is_channel, is_private, is_archived, is_general, is_mpim, is_shared, is_org_shared, num_members, topic, purpose, created FROM channels WHERE (' + ' OR '.join(type_conds) + ')'
    if kwargs.get('exclude_archived') in (True, 1, '1', 'true', 'True'):
        sql += ' AND is_archived = 0'
    sql += ' ORDER BY id LIMIT ?'
    rows = [dict(r) for r in conn.execute(sql, (limit,)).fetchall()]
    conn.close()
    return {'ok': True, 'channels': rows, 'response_metadata': {'next_cursor': ''}}

_env_orig_conversations_list = conversations_list
def _env_conversations_list(db_path='state.db', **kwargs):
    _r = _env_orig_conversations_list(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'ok': True, 'channels': _r['items'], 'response_metadata': {'next_cursor': ''}}
    if 'error' in _r and _r.get('status') == 404:
        return {'ok': False, 'error': str(_r.get('error') or 'channel not found').replace(' not found', '_not_found').replace(' ', '_')}
    if 'error' in _r and _r.get('status') == 400:
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    return _r
conversations_list = _env_conversations_list

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_conversations_list = conversations_list
def _bf_friction_conversations_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_conversations_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "conversations_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_conversations_list(*_bf_args, **_bf_kwargs)
_bf_friction_conversations_list.blobfish_original = _bf_orig_conversations_list
conversations_list = _bf_friction_conversations_list

def conversations_info(db_path='state.db', **kwargs):
    '''Retrieve information about a conversation (GET /conversations.info)'''
    _missing = [p for p in ['channel'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "channels" WHERE "id" = ?', [str(kwargs['channel'])]).fetchone()
        if _row is None:
            _r = {'error': 'channel not found', 'status': 404}
            return {'ok': False, 'error': str(_r.get('error') or 'channel not found').replace(' not found', '_not_found').replace(' ', '_')}
        _r = dict(_row)
        _r = {'ok': True, 'channel': _r}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_conversations_info = conversations_info
def _bf_friction_conversations_info(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_conversations_info(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "conversations_info|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_conversations_info(*_bf_args, **_bf_kwargs)
_bf_friction_conversations_info.blobfish_original = _bf_orig_conversations_info
conversations_info = _bf_friction_conversations_info

def conversations_history(db_path='state.db', **kwargs):
    import sqlite3
    channel = kwargs.get('channel')
    if not channel:
        return {'ok': False, 'error': 'channel is required', 'status': 400}
    try:
        limit = int(kwargs.get('limit', 100))
    except (TypeError, ValueError):
        limit = 100
    inclusive = kwargs.get('inclusive') in (True, 1, '1', 'true', 'True')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    ch = conn.execute('SELECT * FROM channels WHERE id = ?', (str(channel),)).fetchone()
    if ch is None:
        ch = conn.execute('SELECT * FROM channels WHERE name = ? ORDER BY id LIMIT 1', (str(channel).lstrip('#'),)).fetchone()
    if ch is None:
        conn.close()
        return {'ok': False, 'error': 'channel_not_found', 'status': 404}
    sql = 'SELECT type, subtype, ts, thread_ts, user, username, bot_id, text, reply_count, reply_users_count, latest_reply, permalink, team FROM messages WHERE name = ?'
    args = [ch['name']]
    for bound, op_inc, op_exc in (('oldest', '>=', '>'), ('latest', '<=', '<')):
        if kwargs.get(bound) is not None:
            try:
                val = float(kwargs[bound])
            except (TypeError, ValueError):
                conn.close()
                return {'ok': False, 'error': 'invalid_ts_' + bound, 'status': 400}
            sql += ' AND ts IS NOT NULL AND CAST(ts AS REAL) ' + (op_inc if inclusive else op_exc) + ' ?'
            args.append(val)
    sql += ' ORDER BY (ts IS NULL) ASC, CAST(ts AS REAL) DESC LIMIT ?'
    args.append(limit)
    msgs = [dict(r) for r in conn.execute(sql, args).fetchall()]
    conn.close()
    return {'ok': True, 'channel': ch['id'], 'messages': msgs, 'has_more': len(msgs) == limit}

_env_orig_conversations_history = conversations_history
def _env_conversations_history(db_path='state.db', **kwargs):
    _r = _env_orig_conversations_history(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'ok': True, 'messages': _r['items'], 'response_metadata': {'next_cursor': ''}}
    if 'error' in _r and _r.get('status') == 404:
        return {'ok': False, 'error': str(_r.get('error') or 'message not found').replace(' not found', '_not_found').replace(' ', '_')}
    if 'error' in _r and _r.get('status') == 400:
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    return _r
conversations_history = _env_conversations_history

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_conversations_history = conversations_history
def _bf_friction_conversations_history(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_conversations_history(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "conversations_history|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_conversations_history(*_bf_args, **_bf_kwargs)
_bf_friction_conversations_history.blobfish_original = _bf_orig_conversations_history
conversations_history = _bf_friction_conversations_history

def conversations_replies(db_path='state.db', **kwargs):
    import sqlite3
    channel = kwargs.get('channel')
    ts = kwargs.get('ts')
    if not channel or ts is None:
        return {'ok': False, 'error': 'channel and ts are required', 'status': 400}
    try:
        limit = int(kwargs.get('limit', 100))
    except (TypeError, ValueError):
        limit = 100
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    ch = conn.execute('SELECT * FROM channels WHERE id = ?', (str(channel),)).fetchone()
    if ch is None:
        ch = conn.execute('SELECT * FROM channels WHERE name = ? ORDER BY id LIMIT 1', (str(channel).lstrip('#'),)).fetchone()
    if ch is None:
        conn.close()
        return {'ok': False, 'error': 'channel_not_found', 'status': 404}
    cols = 'type, subtype, ts, thread_ts, user, username, bot_id, text, reply_count, reply_users_count, latest_reply, permalink, team'
    parent = conn.execute('SELECT ' + cols + ' FROM messages WHERE name = ? AND ts = ?', (ch['name'], str(ts))).fetchone()
    if parent is None:
        conn.close()
        return {'ok': False, 'error': 'thread_not_found', 'status': 404}
    replies = [dict(r) for r in conn.execute('SELECT ' + cols + ' FROM messages WHERE name = ? AND thread_ts = ? AND ts <> ? ORDER BY CAST(ts AS REAL) ASC LIMIT ?', (ch['name'], str(ts), str(ts), limit)).fetchall()]
    conn.close()
    return {'ok': True, 'channel': ch['id'], 'messages': [dict(parent)] + replies, 'has_more': False}

_env_orig_conversations_replies = conversations_replies
def _env_conversations_replies(db_path='state.db', **kwargs):
    _r = _env_orig_conversations_replies(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'ok': True, 'messages': _r['items'], 'response_metadata': {'next_cursor': ''}}
    if 'error' in _r and _r.get('status') == 404:
        return {'ok': False, 'error': str(_r.get('error') or 'message not found').replace(' not found', '_not_found').replace(' ', '_')}
    if 'error' in _r and _r.get('status') == 400:
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    return _r
conversations_replies = _env_conversations_replies

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_conversations_replies = conversations_replies
def _bf_friction_conversations_replies(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_conversations_replies(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "conversations_replies|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_conversations_replies(*_bf_args, **_bf_kwargs)
_bf_friction_conversations_replies.blobfish_original = _bf_orig_conversations_replies
conversations_replies = _bf_friction_conversations_replies

def conversations_members(db_path='state.db', **kwargs):
    '''Retrieve members of a conversation (GET /conversations.members)'''
    _missing = [p for p in ['channel'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('channel') is not None:
            _where.append('"channel" = ?')
            _args.append(str(kwargs['channel']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "slack_channel_members"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'ok': True, 'members': _r['items'], 'response_metadata': {'next_cursor': ''}}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_conversations_members = conversations_members
def _bf_friction_conversations_members(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_conversations_members(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "conversations_members|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_conversations_members(*_bf_args, **_bf_kwargs)
_bf_friction_conversations_members.blobfish_original = _bf_orig_conversations_members
conversations_members = _bf_friction_conversations_members

def conversations_join(db_path='state.db', **kwargs):
    import sqlite3, hashlib, datetime
    channel = kwargs.get('channel')
    if not channel:
        return {'ok': False, 'error': 'channel is required', 'status': 400}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    ch = conn.execute('SELECT * FROM channels WHERE id = ?', (str(channel),)).fetchone()
    if ch is None:
        ch = conn.execute('SELECT * FROM channels WHERE name = ? ORDER BY id LIMIT 1', (str(channel).lstrip('#'),)).fetchone()
    if ch is None:
        conn.close()
        return {'ok': False, 'error': 'channel_not_found', 'status': 404}
    if ch['is_archived']:
        conn.close()
        return {'ok': False, 'error': 'is_archived', 'status': 400}
    bot = 'U0000099'
    existing = conn.execute('SELECT id FROM slack_channel_members WHERE channel = ? AND user = ?', (ch['id'], bot)).fetchone()
    summary = {'id': ch['id'], 'name': ch['name'], 'is_private': ch['is_private'], 'is_archived': ch['is_archived'], 'num_members': ch['num_members']}
    if existing is not None:
        conn.close()
        return {'ok': True, 'already_in_channel': True, 'channel': summary}
    mid = 'M' + hashlib.md5((ch['id'] + ':' + bot).encode('utf-8')).hexdigest()[:7].upper()
    now = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    conn.execute('INSERT INTO slack_channel_members (id, channel, user, date_joined) VALUES (?, ?, ?, ?)', (mid, ch['id'], bot, now))
    conn.execute('UPDATE channels SET is_member = 1, num_members = COALESCE(num_members, 0) + 1 WHERE id = ?', (ch['id'],))
    conn.commit()
    summary['num_members'] = (ch['num_members'] or 0) + 1
    conn.close()
    return {'ok': True, 'channel': summary}

_env_orig_conversations_join = conversations_join
def _env_conversations_join(db_path='state.db', **kwargs):
    _r = _env_orig_conversations_join(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'ok': True, 'channel_members': _r['items'], 'response_metadata': {'next_cursor': ''}}
    if 'error' in _r and _r.get('status') == 404:
        return {'ok': False, 'error': str(_r.get('error') or 'channel_member not found').replace(' not found', '_not_found').replace(' ', '_')}
    if 'error' in _r and _r.get('status') == 400:
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    return _r
conversations_join = _env_conversations_join

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_conversations_join = conversations_join
def _bf_friction_conversations_join(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_conversations_join(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "conversations_join|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_conversations_join(*_bf_args, **_bf_kwargs)
_bf_friction_conversations_join.blobfish_original = _bf_orig_conversations_join
conversations_join = _bf_friction_conversations_join

def conversations_invite(db_path='state.db', **kwargs):
    import sqlite3, hashlib, datetime
    channel = kwargs.get('channel')
    users = kwargs.get('users')
    if not channel or not users:
        return {'ok': False, 'error': 'channel and users are required', 'status': 400}
    ids = [u.strip() for u in str(users).split(',') if u.strip()]
    if not ids:
        return {'ok': False, 'error': 'no_users_provided', 'status': 400}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    ch = conn.execute('SELECT * FROM channels WHERE id = ?', (str(channel),)).fetchone()
    if ch is None:
        ch = conn.execute('SELECT * FROM channels WHERE name = ? ORDER BY id LIMIT 1', (str(channel).lstrip('#'),)).fetchone()
    if ch is None:
        conn.close()
        return {'ok': False, 'error': 'channel_not_found', 'status': 404}
    if ch['is_archived']:
        conn.close()
        return {'ok': False, 'error': 'is_archived', 'status': 400}
    missing = [u for u in ids if conn.execute('SELECT 1 FROM slack_users WHERE id = ?', (u,)).fetchone() is None]
    if missing:
        conn.close()
        return {'ok': False, 'error': 'users_not_found', 'users': missing, 'status': 404}
    now = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    invited, already = [], []
    for u in ids:
        if conn.execute('SELECT 1 FROM slack_channel_members WHERE channel = ? AND user = ?', (ch['id'], u)).fetchone() is not None:
            already.append(u)
            continue
        mid = 'M' + hashlib.md5((ch['id'] + ':' + u).encode('utf-8')).hexdigest()[:7].upper()
        conn.execute('INSERT INTO slack_channel_members (id, channel, user, date_joined) VALUES (?, ?, ?, ?)', (mid, ch['id'], u, now))
        invited.append(u)
    if invited:
        conn.execute('UPDATE channels SET num_members = COALESCE(num_members, 0) + ? WHERE id = ?', (len(invited), ch['id']))
    conn.commit()
    conn.close()
    return {'ok': True, 'channel': {'id': ch['id'], 'name': ch['name']}, 'invited': invited, 'already_in_channel': already}

_env_orig_conversations_invite = conversations_invite
def _env_conversations_invite(db_path='state.db', **kwargs):
    _r = _env_orig_conversations_invite(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'ok': True, 'channel_members': _r['items'], 'response_metadata': {'next_cursor': ''}}
    if 'error' in _r and _r.get('status') == 404:
        return {'ok': False, 'error': str(_r.get('error') or 'channel_member not found').replace(' not found', '_not_found').replace(' ', '_')}
    if 'error' in _r and _r.get('status') == 400:
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    return _r
conversations_invite = _env_conversations_invite

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_conversations_invite = conversations_invite
def _bf_friction_conversations_invite(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_conversations_invite(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "conversations_invite|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_conversations_invite(*_bf_args, **_bf_kwargs)
_bf_friction_conversations_invite.blobfish_original = _bf_orig_conversations_invite
conversations_invite = _bf_friction_conversations_invite

def conversations_archive(db_path='state.db', **kwargs):
    import sqlite3
    channel = kwargs.get('channel')
    if not channel:
        return {'ok': False, 'error': 'channel is required', 'status': 400}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    ch = conn.execute('SELECT * FROM channels WHERE id = ?', (str(channel),)).fetchone()
    if ch is None:
        ch = conn.execute('SELECT * FROM channels WHERE name = ? ORDER BY id LIMIT 1', (str(channel).lstrip('#'),)).fetchone()
    if ch is None:
        conn.close()
        return {'ok': False, 'error': 'channel_not_found', 'status': 404}
    if ch['is_archived']:
        conn.close()
        return {'ok': False, 'error': 'already_archived', 'status': 400}
    conn.execute('UPDATE channels SET is_archived = 1 WHERE id = ?', (ch['id'],))
    conn.commit()
    conn.close()
    return {'ok': True}

_env_orig_conversations_archive = conversations_archive
def _env_conversations_archive(db_path='state.db', **kwargs):
    _r = _env_orig_conversations_archive(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'ok': True, 'channels': _r['items'], 'response_metadata': {'next_cursor': ''}}
    if 'error' in _r and _r.get('status') == 404:
        return {'ok': False, 'error': str(_r.get('error') or 'channel not found').replace(' not found', '_not_found').replace(' ', '_')}
    if 'error' in _r and _r.get('status') == 400:
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    return _r
conversations_archive = _env_conversations_archive

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_conversations_archive = conversations_archive
def _bf_friction_conversations_archive(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_conversations_archive(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "conversations_archive|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_conversations_archive(*_bf_args, **_bf_kwargs)
_bf_friction_conversations_archive.blobfish_original = _bf_orig_conversations_archive
conversations_archive = _bf_friction_conversations_archive

def conversations_set_topic(db_path='state.db', **kwargs):
    '''Sets the topic for a conversation (POST /conversations.setTopic)'''
    _missing = [p for p in ['channel', 'topic'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "channels" WHERE "id" = ?', [str(kwargs['channel'])]).fetchone()
        if _row is None:
            _r = {'error': 'channel not found', 'status': 404}
            return {'ok': False, 'error': str(_r.get('error') or 'channel not found').replace(' not found', '_not_found').replace(' ', '_')}
        _sets, _args = [], []
        if kwargs.get('topic') is not None:
            _sets.append('"topic" = ?')
            _v = kwargs['topic']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "channels" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['channel'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "channels" WHERE "id" = ?', [str(kwargs['channel'])]).fetchone()
        _r = dict(_row)
        _r = {'ok': True, 'channel': _r}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_conversations_set_topic = conversations_set_topic
def _bf_friction_conversations_set_topic(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_conversations_set_topic(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "conversations_set_topic|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_conversations_set_topic(*_bf_args, **_bf_kwargs)
_bf_friction_conversations_set_topic.blobfish_original = _bf_orig_conversations_set_topic
conversations_set_topic = _bf_friction_conversations_set_topic

def conversations_set_purpose(db_path='state.db', **kwargs):
    '''Sets the purpose for a conversation (POST /conversations.setPurpose)'''
    _missing = [p for p in ['channel', 'purpose'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "channels" WHERE "id" = ?', [str(kwargs['channel'])]).fetchone()
        if _row is None:
            _r = {'error': 'channel not found', 'status': 404}
            return {'ok': False, 'error': str(_r.get('error') or 'channel not found').replace(' not found', '_not_found').replace(' ', '_')}
        _sets, _args = [], []
        if kwargs.get('purpose') is not None:
            _sets.append('"purpose" = ?')
            _v = kwargs['purpose']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "channels" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['channel'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "channels" WHERE "id" = ?', [str(kwargs['channel'])]).fetchone()
        _r = dict(_row)
        _r = {'ok': True, 'channel': _r}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_conversations_set_purpose = conversations_set_purpose
def _bf_friction_conversations_set_purpose(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_conversations_set_purpose(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "conversations_set_purpose|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_conversations_set_purpose(*_bf_args, **_bf_kwargs)
_bf_friction_conversations_set_purpose.blobfish_original = _bf_orig_conversations_set_purpose
conversations_set_purpose = _bf_friction_conversations_set_purpose

def chat_post_message(db_path='state.db', **kwargs):
    import sqlite3, hashlib, datetime
    channel = kwargs.get('channel')
    text = kwargs.get('text')
    if not channel or text is None or str(text) == '':
        return {'ok': False, 'error': 'channel and text are required', 'status': 400}
    thread_ts = kwargs.get('thread_ts')
    username = kwargs.get('username')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    ch = conn.execute('SELECT * FROM channels WHERE id = ?', (str(channel),)).fetchone()
    if ch is None:
        ch = conn.execute('SELECT * FROM channels WHERE name = ? ORDER BY id LIMIT 1', (str(channel).lstrip('#'),)).fetchone()
    if ch is None:
        conn.close()
        return {'ok': False, 'error': 'channel_not_found', 'status': 404}
    if ch['is_archived']:
        conn.close()
        return {'ok': False, 'error': 'is_archived', 'status': 400}
    if thread_ts is not None:
        parent = conn.execute('SELECT ts FROM messages WHERE name = ? AND ts = ?', (ch['name'], str(thread_ts))).fetchone()
        if parent is None:
            conn.close()
            return {'ok': False, 'error': 'message_not_found', 'status': 404, 'detail': 'thread_ts does not match any message in the channel'}
    now = datetime.datetime.now(datetime.timezone.utc)
    seq = conn.execute('SELECT COUNT(*) FROM messages').fetchone()[0]
    ts = '%d.%06d' % (int(now.timestamp()), 100000 + seq)
    permalink = 'https://morganstanleysimulated.slack.com/archives/%s/p%s' % (ch['id'], ts.replace('.', ''))
    client_msg_id = 'CLI-' + hashlib.md5(ts.encode('utf-8')).hexdigest()[:7].upper()
    conn.execute('INSERT INTO messages (name, text, ts, thread_ts, user, username, bot_id, type, subtype, team, client_msg_id, permalink, reply_count, reply_users_count, is_starred, upload) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0)',
                 (ch['name'], str(text), ts, (str(thread_ts) if thread_ts is not None else None), 'U0000099', (str(username) if username else 'ms-crm-agent'), 'B0000099', 'message', 'bot_message', 'T0000001', client_msg_id, permalink))
    if thread_ts is not None:
        conn.execute('UPDATE messages SET reply_count = COALESCE(reply_count, 0) + 1, latest_reply = ? WHERE name = ? AND ts = ?', (ts, ch['name'], str(thread_ts)))
    conn.execute('UPDATE channels SET latest = ? WHERE id = ?', (str(text), ch['id']))
    conn.commit()
    conn.close()
    message = {'type': 'message', 'subtype': 'bot_message', 'text': str(text), 'ts': ts, 'thread_ts': (str(thread_ts) if thread_ts is not None else None), 'user': 'U0000099', 'username': (str(username) if username else 'ms-crm-agent'), 'bot_id': 'B0000099', 'team': 'T0000001', 'permalink': permalink}
    return {'ok': True, 'channel': ch['id'], 'ts': ts, 'message': message}

_env_orig_chat_post_message = chat_post_message
def _env_chat_post_message(db_path='state.db', **kwargs):
    _r = _env_orig_chat_post_message(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'ok': True, 'messages': _r['items'], 'response_metadata': {'next_cursor': ''}}
    if 'error' in _r and _r.get('status') == 404:
        return {'ok': False, 'error': str(_r.get('error') or 'message not found').replace(' not found', '_not_found').replace(' ', '_')}
    if 'error' in _r and _r.get('status') == 400:
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    return _r
chat_post_message = _env_chat_post_message

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_chat_post_message = chat_post_message
def _bf_friction_chat_post_message(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_chat_post_message(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "chat_post_message|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_chat_post_message(*_bf_args, **_bf_kwargs)
_bf_friction_chat_post_message.blobfish_original = _bf_orig_chat_post_message
chat_post_message = _bf_friction_chat_post_message

def chat_update(db_path='state.db', **kwargs):
    import sqlite3
    channel = kwargs.get('channel')
    ts = kwargs.get('ts')
    text = kwargs.get('text')
    if not channel or ts is None or text is None:
        return {'ok': False, 'error': 'channel, ts and text are required', 'status': 400}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    ch = conn.execute('SELECT * FROM channels WHERE id = ?', (str(channel),)).fetchone()
    if ch is None:
        ch = conn.execute('SELECT * FROM channels WHERE name = ? ORDER BY id LIMIT 1', (str(channel).lstrip('#'),)).fetchone()
    if ch is None:
        conn.close()
        return {'ok': False, 'error': 'channel_not_found', 'status': 404}
    cur = conn.execute('UPDATE messages SET text = ? WHERE name = ? AND ts = ?', (str(text), ch['name'], str(ts)))
    if cur.rowcount == 0:
        conn.close()
        return {'ok': False, 'error': 'message_not_found', 'status': 404}
    conn.commit()
    conn.close()
    return {'ok': True, 'channel': ch['id'], 'ts': str(ts), 'text': str(text)}

_env_orig_chat_update = chat_update
def _env_chat_update(db_path='state.db', **kwargs):
    _r = _env_orig_chat_update(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'ok': True, 'messages': _r['items'], 'response_metadata': {'next_cursor': ''}}
    if 'error' in _r and _r.get('status') == 404:
        return {'ok': False, 'error': str(_r.get('error') or 'message not found').replace(' not found', '_not_found').replace(' ', '_')}
    if 'error' in _r and _r.get('status') == 400:
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    return _r
chat_update = _env_chat_update

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_chat_update = chat_update
def _bf_friction_chat_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_chat_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "chat_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_chat_update(*_bf_args, **_bf_kwargs)
_bf_friction_chat_update.blobfish_original = _bf_orig_chat_update
chat_update = _bf_friction_chat_update

def chat_delete(db_path='state.db', **kwargs):
    import sqlite3
    channel = kwargs.get('channel')
    ts = kwargs.get('ts')
    if not channel or ts is None:
        return {'ok': False, 'error': 'channel and ts are required', 'status': 400}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    ch = conn.execute('SELECT * FROM channels WHERE id = ?', (str(channel),)).fetchone()
    if ch is None:
        ch = conn.execute('SELECT * FROM channels WHERE name = ? ORDER BY id LIMIT 1', (str(channel).lstrip('#'),)).fetchone()
    if ch is None:
        conn.close()
        return {'ok': False, 'error': 'channel_not_found', 'status': 404}
    cur = conn.execute('DELETE FROM messages WHERE name = ? AND ts = ?', (ch['name'], str(ts)))
    if cur.rowcount == 0:
        conn.close()
        return {'ok': False, 'error': 'message_not_found', 'status': 404}
    conn.commit()
    conn.close()
    return {'ok': True, 'channel': ch['id'], 'ts': str(ts)}

_env_orig_chat_delete = chat_delete
def _env_chat_delete(db_path='state.db', **kwargs):
    _r = _env_orig_chat_delete(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'ok': True, 'messages': _r['items'], 'response_metadata': {'next_cursor': ''}}
    if 'error' in _r and _r.get('status') == 404:
        return {'ok': False, 'error': str(_r.get('error') or 'message not found').replace(' not found', '_not_found').replace(' ', '_')}
    if 'error' in _r and _r.get('status') == 400:
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    return _r
chat_delete = _env_chat_delete

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_chat_delete = chat_delete
def _bf_friction_chat_delete(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_chat_delete(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "chat_delete|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_chat_delete(*_bf_args, **_bf_kwargs)
_bf_friction_chat_delete.blobfish_original = _bf_orig_chat_delete
chat_delete = _bf_friction_chat_delete

def chat_schedule_message(db_path='state.db', **kwargs):
    '''Schedules a message to be sent to a channel at a future Unix timestamp; returns the scheduled_message_id (POST /chat.scheduleMessage)'''
    _missing = [p for p in ['channel', 'text', 'post_at'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "slack_scheduled_messages"').fetchone()[0] + 1
        _id = 'Q0' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "slack_scheduled_messages" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'Q0' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('channel') is not None:
            _cols.append('channel')
            _v = kwargs['channel']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('text') is not None:
            _cols.append('text')
            _v = kwargs['text']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('post_at') is not None:
            _cols.append('post_at')
            _v = kwargs['post_at']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('thread_ts') is not None:
            _cols.append('thread_ts')
            _v = kwargs['thread_ts']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "slack_scheduled_messages" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "slack_scheduled_messages" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r = {'ok': True, 'scheduled_message': _r}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_chat_schedule_message = chat_schedule_message
def _bf_friction_chat_schedule_message(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_chat_schedule_message(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "chat_schedule_message|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_chat_schedule_message(*_bf_args, **_bf_kwargs)
_bf_friction_chat_schedule_message.blobfish_original = _bf_orig_chat_schedule_message
chat_schedule_message = _bf_friction_chat_schedule_message

def users_list(db_path='state.db', **kwargs):
    '''Lists all users in a Slack team, including bots and deactivated profiles (GET /users.list)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('team_id') is not None:
            _where.append('"team_id" = ?')
            _args.append(str(kwargs['team_id']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "slack_users"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'ok': True, 'members': _r['items'], 'response_metadata': {'next_cursor': ''}}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_users_list = users_list
def _bf_friction_users_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_users_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "users_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_users_list(*_bf_args, **_bf_kwargs)
_bf_friction_users_list.blobfish_original = _bf_orig_users_list
users_list = _bf_friction_users_list

def users_info(db_path='state.db', **kwargs):
    '''Gets information about a user, including profile, presence, and admin flags (GET /users.info)'''
    _missing = [p for p in ['user'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "slack_users" WHERE "id" = ?', [str(kwargs['user'])]).fetchone()
        if _row is None:
            _r = {'error': 'user not found', 'status': 404}
            return {'ok': False, 'error': str(_r.get('error') or 'user not found').replace(' not found', '_not_found').replace(' ', '_')}
        _r = dict(_row)
        _r = {'ok': True, 'user': _r}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_users_info = users_info
def _bf_friction_users_info(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_users_info(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "users_info|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_users_info(*_bf_args, **_bf_kwargs)
_bf_friction_users_info.blobfish_original = _bf_orig_users_info
users_info = _bf_friction_users_info

def users_lookup_by_email(db_path='state.db', **kwargs):
    '''Find a user with an email address; returns users_not_found-style 404 when no profile matches (GET /users.lookupByEmail)'''
    _missing = [p for p in ['email'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "slack_users" WHERE "email" = ?', [str(kwargs['email'])]).fetchone()
        if _row is None:
            _r = {'error': 'user not found', 'status': 404}
            return {'ok': False, 'error': str(_r.get('error') or 'user not found').replace(' not found', '_not_found').replace(' ', '_')}
        _r = dict(_row)
        _r = {'ok': True, 'user': _r}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_users_lookup_by_email = users_lookup_by_email
def _bf_friction_users_lookup_by_email(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_users_lookup_by_email(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "users_lookup_by_email|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_users_lookup_by_email(*_bf_args, **_bf_kwargs)
_bf_friction_users_lookup_by_email.blobfish_original = _bf_orig_users_lookup_by_email
users_lookup_by_email = _bf_friction_users_lookup_by_email

def users_set_presence(db_path='state.db', **kwargs):
    '''Manually sets user presence to auto, active, or away; targets the given workspace user (the real API acts on the authed user) (POST /users.setPresence)'''
    _missing = [p for p in ['user', 'presence'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "slack_users" WHERE "id" = ?', [str(kwargs['user'])]).fetchone()
        if _row is None:
            _r = {'error': 'user not found', 'status': 404}
            return {'ok': False, 'error': str(_r.get('error') or 'user not found').replace(' not found', '_not_found').replace(' ', '_')}
        _sets, _args = [], []
        if kwargs.get('presence') is not None:
            _sets.append('"presence" = ?')
            _v = kwargs['presence']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        _sets.append('"updated" = ?')
        _args.append(datetime.datetime.now(datetime.timezone.utc).isoformat())
        if _sets:
            cur.execute('UPDATE "slack_users" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['user'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "slack_users" WHERE "id" = ?', [str(kwargs['user'])]).fetchone()
        _r = dict(_row)
        _r = {'ok': True, 'user': _r}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_users_set_presence = users_set_presence
def _bf_friction_users_set_presence(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_users_set_presence(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "users_set_presence|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_users_set_presence(*_bf_args, **_bf_kwargs)
_bf_friction_users_set_presence.blobfish_original = _bf_orig_users_set_presence
users_set_presence = _bf_friction_users_set_presence

def reactions_add(db_path='state.db', **kwargs):
    import sqlite3, hashlib, datetime
    channel = kwargs.get('channel')
    timestamp = kwargs.get('timestamp')
    name = kwargs.get('name')
    if not channel or timestamp is None or not name:
        return {'ok': False, 'error': 'channel, timestamp and name are required', 'status': 400}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    ch = conn.execute('SELECT * FROM channels WHERE id = ?', (str(channel),)).fetchone()
    if ch is None:
        ch = conn.execute('SELECT * FROM channels WHERE name = ? ORDER BY id LIMIT 1', (str(channel).lstrip('#'),)).fetchone()
    if ch is None:
        conn.close()
        return {'ok': False, 'error': 'channel_not_found', 'status': 404}
    msg = conn.execute('SELECT 1 FROM messages WHERE name = ? AND ts = ?', (ch['name'], str(timestamp))).fetchone()
    if msg is None:
        conn.close()
        return {'ok': False, 'error': 'message_not_found', 'status': 404}
    emoji = str(name).strip(':')
    bot = 'U0000099'
    dup = conn.execute('SELECT 1 FROM slack_reactions WHERE channel = ? AND timestamp = ? AND name = ? AND user = ?', (ch['id'], str(timestamp), emoji, bot)).fetchone()
    if dup is not None:
        conn.close()
        return {'ok': False, 'error': 'already_reacted', 'status': 400}
    rid = 'R' + hashlib.md5((ch['id'] + ':' + str(timestamp) + ':' + emoji + ':' + bot).encode('utf-8')).hexdigest()[:8].upper()
    created = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    conn.execute('INSERT INTO slack_reactions (id, channel, timestamp, name, user, created) VALUES (?, ?, ?, ?, ?, ?)', (rid, ch['id'], str(timestamp), emoji, bot, created))
    conn.commit()
    conn.close()
    return {'ok': True}

_env_orig_reactions_add = reactions_add
def _env_reactions_add(db_path='state.db', **kwargs):
    _r = _env_orig_reactions_add(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'ok': True, 'reactions': _r['items'], 'response_metadata': {'next_cursor': ''}}
    if 'error' in _r and _r.get('status') == 404:
        return {'ok': False, 'error': str(_r.get('error') or 'reaction not found').replace(' not found', '_not_found').replace(' ', '_')}
    if 'error' in _r and _r.get('status') == 400:
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    return _r
reactions_add = _env_reactions_add

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_reactions_add = reactions_add
def _bf_friction_reactions_add(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_reactions_add(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "reactions_add|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_reactions_add(*_bf_args, **_bf_kwargs)
_bf_friction_reactions_add.blobfish_original = _bf_orig_reactions_add
reactions_add = _bf_friction_reactions_add

def reactions_remove(db_path='state.db', **kwargs):
    import sqlite3
    channel = kwargs.get('channel')
    timestamp = kwargs.get('timestamp')
    name = kwargs.get('name')
    if not channel or timestamp is None or not name:
        return {'ok': False, 'error': 'channel, timestamp and name are required', 'status': 400}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    ch = conn.execute('SELECT * FROM channels WHERE id = ?', (str(channel),)).fetchone()
    if ch is None:
        ch = conn.execute('SELECT * FROM channels WHERE name = ? ORDER BY id LIMIT 1', (str(channel).lstrip('#'),)).fetchone()
    if ch is None:
        conn.close()
        return {'ok': False, 'error': 'channel_not_found', 'status': 404}
    emoji = str(name).strip(':')
    cur = conn.execute('DELETE FROM slack_reactions WHERE channel = ? AND timestamp = ? AND name = ?', (ch['id'], str(timestamp), emoji))
    if cur.rowcount == 0:
        conn.close()
        return {'ok': False, 'error': 'no_reaction', 'status': 404}
    conn.commit()
    conn.close()
    return {'ok': True}

_env_orig_reactions_remove = reactions_remove
def _env_reactions_remove(db_path='state.db', **kwargs):
    _r = _env_orig_reactions_remove(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'ok': True, 'reactions': _r['items'], 'response_metadata': {'next_cursor': ''}}
    if 'error' in _r and _r.get('status') == 404:
        return {'ok': False, 'error': str(_r.get('error') or 'reaction not found').replace(' not found', '_not_found').replace(' ', '_')}
    if 'error' in _r and _r.get('status') == 400:
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    return _r
reactions_remove = _env_reactions_remove

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_reactions_remove = reactions_remove
def _bf_friction_reactions_remove(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_reactions_remove(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "reactions_remove|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_reactions_remove(*_bf_args, **_bf_kwargs)
_bf_friction_reactions_remove.blobfish_original = _bf_orig_reactions_remove
reactions_remove = _bf_friction_reactions_remove

def reactions_get(db_path='state.db', **kwargs):
    '''Gets the reactions on a message identified by channel and timestamp (GET /reactions.get)'''
    _missing = [p for p in ['channel', 'timestamp'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('channel') is not None:
            _where.append('"channel" = ?')
            _args.append(str(kwargs['channel']))
        if kwargs.get('timestamp') is not None:
            _where.append('"timestamp" = ?')
            _args.append(str(kwargs['timestamp']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "slack_reactions"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'ok': True, 'reactions': _r['items'], 'response_metadata': {'next_cursor': ''}}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_reactions_get = reactions_get
def _bf_friction_reactions_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_reactions_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "reactions_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_reactions_get(*_bf_args, **_bf_kwargs)
_bf_friction_reactions_get.blobfish_original = _bf_orig_reactions_get
reactions_get = _bf_friction_reactions_get

def pins_add(db_path='state.db', **kwargs):
    '''Pins a message to a channel (POST /pins.add)'''
    _missing = [p for p in ['channel', 'timestamp'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "slack_pins"').fetchone()[0] + 1
        _id = 'Pn' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "slack_pins" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'Pn' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('channel') is not None:
            _cols.append('channel')
            _v = kwargs['channel']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('timestamp') is not None:
            _cols.append('timestamp')
            _v = kwargs['timestamp']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'created_by' not in _cols:
            _cols.append('created_by')
            _vals.append('U0000099')
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "slack_pins" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "slack_pins" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r = {'ok': True, 'pin': _r}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pins_add = pins_add
def _bf_friction_pins_add(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pins_add(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pins_add|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pins_add(*_bf_args, **_bf_kwargs)
_bf_friction_pins_add.blobfish_original = _bf_orig_pins_add
pins_add = _bf_friction_pins_add

def pins_list(db_path='state.db', **kwargs):
    '''Lists items pinned to a channel (GET /pins.list)'''
    _missing = [p for p in ['channel'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('channel') is not None:
            _where.append('"channel" = ?')
            _args.append(str(kwargs['channel']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "slack_pins"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'ok': True, 'items': _r['items'], 'response_metadata': {'next_cursor': ''}}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pins_list = pins_list
def _bf_friction_pins_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pins_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pins_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pins_list(*_bf_args, **_bf_kwargs)
_bf_friction_pins_list.blobfish_original = _bf_orig_pins_list
pins_list = _bf_friction_pins_list

def pins_remove(db_path='state.db', **kwargs):
    import sqlite3
    channel = kwargs.get('channel')
    timestamp = kwargs.get('timestamp')
    if not channel or timestamp is None:
        return {'ok': False, 'error': 'channel and timestamp are required', 'status': 400}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    ch = conn.execute('SELECT * FROM channels WHERE id = ?', (str(channel),)).fetchone()
    if ch is None:
        ch = conn.execute('SELECT * FROM channels WHERE name = ? ORDER BY id LIMIT 1', (str(channel).lstrip('#'),)).fetchone()
    if ch is None:
        conn.close()
        return {'ok': False, 'error': 'channel_not_found', 'status': 404}
    cur = conn.execute('DELETE FROM slack_pins WHERE channel = ? AND timestamp = ?', (ch['id'], str(timestamp)))
    if cur.rowcount == 0:
        conn.close()
        return {'ok': False, 'error': 'no_pin', 'status': 404}
    conn.commit()
    conn.close()
    return {'ok': True}

_env_orig_pins_remove = pins_remove
def _env_pins_remove(db_path='state.db', **kwargs):
    _r = _env_orig_pins_remove(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'ok': True, 'pins': _r['items'], 'response_metadata': {'next_cursor': ''}}
    if 'error' in _r and _r.get('status') == 404:
        return {'ok': False, 'error': str(_r.get('error') or 'pin not found').replace(' not found', '_not_found').replace(' ', '_')}
    if 'error' in _r and _r.get('status') == 400:
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    return _r
pins_remove = _env_pins_remove

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pins_remove = pins_remove
def _bf_friction_pins_remove(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pins_remove(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pins_remove|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pins_remove(*_bf_args, **_bf_kwargs)
_bf_friction_pins_remove.blobfish_original = _bf_orig_pins_remove
pins_remove = _bf_friction_pins_remove

def search_messages(db_path='state.db', **kwargs):
    '''Searches for messages matching a query across message text in the workspace (GET /search.messages)'''
    _missing = [p for p in ['query'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _qv = '%' + str(kwargs['query']) + '%'
        _where, _args = ["(\"text\" LIKE ?)"], [_qv] * 1
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "messages" WHERE ' + ' AND '.join(_where) + ' ORDER BY rowid LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'ok': True, 'messages': _r['items'], 'response_metadata': {'next_cursor': ''}}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_search_messages = search_messages
def _bf_friction_search_messages(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_search_messages(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "search_messages|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_search_messages(*_bf_args, **_bf_kwargs)
_bf_friction_search_messages.blobfish_original = _bf_orig_search_messages
search_messages = _bf_friction_search_messages

def usergroups_list(db_path='state.db', **kwargs):
    '''Lists all User Groups for a team, including handles, descriptions, and member counts (GET /usergroups.list)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('team_id') is not None:
            _where.append('"team_id" = ?')
            _args.append(str(kwargs['team_id']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "slack_usergroups"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'ok': True, 'usergroups': _r['items'], 'response_metadata': {'next_cursor': ''}}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_usergroups_list = usergroups_list
def _bf_friction_usergroups_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_usergroups_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "usergroups_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_usergroups_list(*_bf_args, **_bf_kwargs)
_bf_friction_usergroups_list.blobfish_original = _bf_orig_usergroups_list
usergroups_list = _bf_friction_usergroups_list

def usergroups_create(db_path='state.db', **kwargs):
    '''Create a User Group; the S0-prefixed usergroup id is generated server-side (POST /usergroups.create)'''
    _missing = [p for p in ['name'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "slack_usergroups"').fetchone()[0] + 1
        _id = 'S0' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "slack_usergroups" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'S0' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('name') is not None:
            _cols.append('name')
            _v = kwargs['name']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('handle') is not None:
            _cols.append('handle')
            _v = kwargs['handle']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('description') is not None:
            _cols.append('description')
            _v = kwargs['description']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'team_id' not in _cols:
            _cols.append('team_id')
            _vals.append('T0000001')
        if 'created_by' not in _cols:
            _cols.append('created_by')
            _vals.append('U0000099')
        if 'user_count' not in _cols:
            _cols.append('user_count')
            _vals.append(0)
        if 'users' not in _cols:
            _cols.append('users')
            _vals.append('')
        cur.execute('INSERT INTO "slack_usergroups" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "slack_usergroups" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r = {'ok': True, 'usergroup': _r}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_usergroups_create = usergroups_create
def _bf_friction_usergroups_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_usergroups_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "usergroups_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_usergroups_create(*_bf_args, **_bf_kwargs)
_bf_friction_usergroups_create.blobfish_original = _bf_orig_usergroups_create
usergroups_create = _bf_friction_usergroups_create

def usergroups_update(db_path='state.db', **kwargs):
    '''Update an existing User Group; only the fields provided are changed (POST /usergroups.update)'''
    _missing = [p for p in ['usergroup'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "slack_usergroups" WHERE "id" = ?', [str(kwargs['usergroup'])]).fetchone()
        if _row is None:
            _r = {'error': 'usergroup not found', 'status': 404}
            return {'ok': False, 'error': str(_r.get('error') or 'usergroup not found').replace(' not found', '_not_found').replace(' ', '_')}
        _sets, _args = [], []
        if kwargs.get('name') is not None:
            _sets.append('"name" = ?')
            _v = kwargs['name']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('handle') is not None:
            _sets.append('"handle" = ?')
            _v = kwargs['handle']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('description') is not None:
            _sets.append('"description" = ?')
            _v = kwargs['description']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "slack_usergroups" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['usergroup'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "slack_usergroups" WHERE "id" = ?', [str(kwargs['usergroup'])]).fetchone()
        _r = dict(_row)
        _r = {'ok': True, 'usergroup': _r}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_usergroups_update = usergroups_update
def _bf_friction_usergroups_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_usergroups_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "usergroups_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_usergroups_update(*_bf_args, **_bf_kwargs)
_bf_friction_usergroups_update.blobfish_original = _bf_orig_usergroups_update
usergroups_update = _bf_friction_usergroups_update

def team_info(db_path='state.db', **kwargs):
    import sqlite3
    team = kwargs.get('team')
    tid = str(team) if team else 'T0000001'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM slack_team WHERE id = ?', (tid,)).fetchone()
    conn.close()
    if row is None:
        return {'ok': False, 'error': 'team_not_found', 'status': 404}
    return {'ok': True, 'team': dict(row)}

_env_orig_team_info = team_info
def _env_team_info(db_path='state.db', **kwargs):
    _r = _env_orig_team_info(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'ok': True, 'team': _r['items'], 'response_metadata': {'next_cursor': ''}}
    if 'error' in _r and _r.get('status') == 404:
        return {'ok': False, 'error': str(_r.get('error') or 'team not found').replace(' not found', '_not_found').replace(' ', '_')}
    if 'error' in _r and _r.get('status') == 400:
        return {'ok': False, 'error': 'invalid_arguments', 'response_metadata': {'messages': [str(_r.get('error', ''))]}}
    return _r
team_info = _env_team_info

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_team_info = team_info
def _bf_friction_team_info(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_team_info(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "team_info|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_team_info(*_bf_args, **_bf_kwargs)
_bf_friction_team_info.blobfish_original = _bf_orig_team_info
team_info = _bf_friction_team_info

def emoji_list(db_path='state.db', **kwargs):
    '''Lists custom emoji for a team, including aliases and image URLs (GET /emoji.list)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "admin_emojis"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'ok': True, 'admin_emojis': _r['items'], 'response_metadata': {'next_cursor': ''}}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_emoji_list = emoji_list
def _bf_friction_emoji_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_emoji_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "emoji_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_emoji_list(*_bf_args, **_bf_kwargs)
_bf_friction_emoji_list.blobfish_original = _bf_orig_emoji_list
emoji_list = _bf_friction_emoji_list

