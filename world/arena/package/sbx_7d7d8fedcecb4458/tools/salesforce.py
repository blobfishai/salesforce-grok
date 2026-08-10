"""Executable SALESFORCE tool module

Inspect each function: SQLite helpers are local fixtures; network-backed functions call their declared endpoint.
Tools: sales_records_agent, sourcing_records_agent, list_lead, get_account, list_account, list_opportunity, get_lead, get_opportunity, query_sales_leads, lookup_sales_lead_with_employees, core_workflow_agent, sales_workflow_agent, sourcing_workflow_agent, create_lead, update_status_lead, create_account, update_status_account, create_opportunity, update_status_opportunity, update_sales_leads_status
Tables: sales_leads, sales_opportunities, sourcing_purchase_orders, sourcing_vendors, lead, account, opportunity, employees, activity
"""
import json, sqlite3
"""Department records sub-agent: resolve one unique business handle from a free-text request without mutating state."""
import re, sqlite3

_SURFACES = {"sales_leads":{"table":"sales_leads","primary_key":"id","labels":["lead_number","company_name","contact_name"],"readable":["id","lead_number","company_name","contact_name","source","estimated_value","owner_employee_id","created_at","status"],"resolvable":["lead_number","company_name","contact_name","source","estimated_value","owner_employee_id","created_at"],"mutable":["lead_number","company_name","contact_name","source","estimated_value","status"],"lifecycles":{"status":["new","contacted","qualified","converted","lost"]}},"sales_opportunities":{"table":"sales_opportunities","primary_key":"id","labels":["opportunity_number","title"],"readable":["id","opportunity_number","title","lead_id","amount","owner_employee_id","expected_close_date","business_unit_id","status"],"resolvable":["opportunity_number","title","lead_id","amount","owner_employee_id","expected_close_date","business_unit_id"],"mutable":["opportunity_number","title","amount","expected_close_date","status"],"lifecycles":{"status":["discovery","proposal","negotiation","closed_won","closed_lost"]}}}

def _qi(name):
    return '"' + str(name).replace('"', '""') + '"'

_OUTCOME_GROUPS = [["approved","rejected","denied","declined"],["completed","cancelled","canceled","failed"],["paid","failed"],["closed_won","closed_lost"],["accepted","rejected"],["hired","rejected"]]
def _norm_status(value):
    return str(value).strip().strip("'\"").lower()
def _outcome_group(values, candidate):
    available = {_norm_status(item) for item in values}
    target = _norm_status(candidate)
    candidates = [group for group in _OUTCOME_GROUPS if target in group and sum(1 for item in group if item in available) >= 2]
    return max(candidates, key=lambda group: sum(1 for item in group if item in available)) if candidates else None
def _next_lifecycle_values(values, current):
    normalized = [_norm_status(item) for item in values]
    target = _norm_status(current)
    if target not in normalized:
        return []
    index = normalized.index(target)
    current_branch = _outcome_group(values, values[index])
    successor_index = index + 1
    if current_branch:
        branch_indices = [i for i, item in enumerate(values) if _norm_status(item) in current_branch]
        if index != min(branch_indices):
            return []
        while successor_index < len(values) and _norm_status(values[successor_index]) in current_branch:
            successor_index += 1
    if successor_index >= len(values):
        return []
    candidate = values[successor_index]
    candidate_branch = _outcome_group(values, candidate)
    if not candidate_branch:
        return [candidate]
    branch_indices = [i for i, item in enumerate(values) if _norm_status(item) in candidate_branch]
    if min(branch_indices) <= index:
        return []
    return [item for item in values if _norm_status(item) in candidate_branch]
def _invalid_lifecycle_transition(values, before, after):
    normalized = [_norm_status(item) for item in values]
    current, target = _norm_status(before), _norm_status(after)
    if current not in normalized or target not in normalized:
        return True
    if current == target:
        return False
    return target not in [_norm_status(item) for item in _next_lifecycle_values(values, before)]
def _lifecycle_action_terms(value):
    normalized = re.sub(r'[^a-z0-9]+', '_', _norm_status(value)).strip('_')
    aliases = {
        'approved': ['approve'], 'declined': ['decline', 'reject'],
        'completed': ['complete', 'finish'], 'cancelled': ['cancel'],
        'succeeded': ['succeed'], 'failed': ['fail'],
        'closed_won': ['won', 'win'], 'closed_lost': ['lost', 'lose'],
        'reviewed': ['review'], 'verified': ['verify'], 'retained': ['retain'],
        'archived': ['archive'], 'published': ['publish'], 'packed': ['pack'],
        'shipped': ['ship'],
    }
    terms = [normalized, *aliases.get(normalized, [])]
    if normalized.endswith('ied') and len(normalized) > 3:
        terms.append(normalized[:-3] + 'y')
    elif normalized.endswith('ed') and len(normalized) > 2:
        terms.extend([normalized[:-2], normalized[:-1]])
    return list(dict.fromkeys(term for term in terms if term))

def _parse_request_target(req):
    table_match = re.search(r'(?:in\s+)?table\s+"?([A-Za-z_][A-Za-z0-9_]*)"?', req, re.I | re.S)
    if not table_match:
        return None
    table = table_match.group(1)
    surface = _SURFACES.get(table)
    tail = req[table_match.end():]
    generic_handle = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?business\s+(?:handle|label|key|identifier|reference|ref)\s+"([^"]+)"', tail, re.I | re.S)
    canonical = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+([A-Za-z_][A-Za-z0-9_]*)\s+"([^"]+)"', tail, re.I | re.S)
    descriptive = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+(?:with|by)\s+(?:(business\s+(?:handle|label|key|identifier|reference|ref))|([A-Za-z_][A-Za-z0-9_]*))\s+"([^"]+)"', tail, re.I | re.S)
    whose_alias = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+whose\s+(?:(?:[A-Za-z_][A-Za-z0-9_]*\s+or\s+)?business\s+(?:handle|label|key|identifier|reference|ref)|business\s+(?:handle|label|key|identifier|reference|ref)\s+or\s+[A-Za-z_][A-Za-z0-9_]*)\s+(?:(?:is|equals?|match(?:es)?)\s+|corresponds?(?:\s+to)?(?:\s+(?:the\s+)?[A-Za-z][A-Za-z0-9 _-]{0,60})?\s+)?"([^"]+)"', tail, re.I | re.S)
    whose = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+whose\s+(?:(business\s+(?:handle|label|key|identifier|reference|ref))|([A-Za-z_][A-Za-z0-9_]*))\s+(?:(?:is|equals?|match(?:es)?)\s+|corresponds?(?:\s+to)?(?:\s+(?:the\s+)?[A-Za-z][A-Za-z0-9 _-]{0,60})?\s+)?"([^"]+)"', tail, re.I | re.S)
    associated = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+associated\s+with\s+(?:(business\s+(?:handle|label|key|identifier|reference|ref))|([A-Za-z_][A-Za-z0-9_]*))\s+"([^"]+)"', tail, re.I | re.S)
    named = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+named\s+"([^"]+)"', tail, re.I | re.S)
    natural_for = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9 _-]{0,60}?\s+for\s+([A-Za-z][A-Za-z0-9 .\'-]{1,80}?)\s+(?=and\s+(?:return|show|read|retrieve|report|give|inspect|check)\b)', tail, re.I | re.S)
    if generic_handle:
        label_field = 'business_handle'
        label_value = generic_handle.group(1)
        action_start = table_match.end() + generic_handle.end()
    elif canonical:
        label_field, label_value = canonical.group(1), canonical.group(2)
        action_start = table_match.end() + canonical.end()
    elif descriptive:
        label_field = 'business_handle' if descriptive.group(1) else descriptive.group(2)
        label_value = descriptive.group(3)
        action_start = table_match.end() + descriptive.end()
    elif whose_alias:
        label_field = 'business_handle'
        label_value = whose_alias.group(1)
        action_start = table_match.end() + whose_alias.end()
    elif whose:
        label_field = 'business_handle' if whose.group(1) else whose.group(2)
        label_value = whose.group(3)
        action_start = table_match.end() + whose.end()
    elif associated:
        label_field = 'business_handle' if associated.group(1) else associated.group(2)
        label_value = associated.group(3)
        action_start = table_match.end() + associated.end()
    elif named:
        label_field = 'business_handle'
        label_value = named.group(1)
        action_start = table_match.end() + named.end()
    elif natural_for and surface is not None and len(surface['labels']) == 1:
        label_field = surface['labels'][0]
        label_value = natural_for.group(1).strip()
        action_start = table_match.end() + natural_for.end()
    else:
        return None
    if surface is not None and label_field not in surface['labels']:
        entity = table[:-3] + 'y' if table.endswith('ies') else (table[:-1] if table.endswith('s') else table)
        aliases = {'handle', 'business_handle', 'business_ref', 'record', 'item', 'case', entity.lower()}
        if str(label_field).lower() == 'id' and surface['primary_key'] in surface['labels']:
            label_field = surface['primary_key']
        elif str(label_field).lower() in aliases and len(surface['labels']) == 1:
            label_field = surface['labels'][0]
        elif str(label_field).lower() in aliases:
            label_field = '__business_handle__'
    return table, label_field, label_value, action_start
def _resolve_label_field(conn, table, surface, label_field, label_value):
    if label_field in surface['labels']:
        return label_field, None
    if label_field in surface.get('resolvable', []):
        rows = conn.execute('SELECT 1 FROM ' + _qi(table) + ' WHERE ' + _qi(label_field) + ' = ? LIMIT 3', (label_value,)).fetchall()
        if len(rows) == 1:
            return label_field, None
        if len(rows) == 0:
            return None, {'error': 'not_found', 'message': 'no record matched the exact resolution attribute', 'table': table, 'field': label_field, 'value': label_value}
        return None, {'error': 'ambiguous_match', 'message': 'resolution attribute matched multiple records', 'field': label_field, 'match_count': len(rows)}
    if label_field != '__business_handle__':
        return None, {'error': 'invalid_business_handle', 'message': 'use a declared business handle or exact non-lifecycle resolution field', 'allowed': surface['labels'], 'resolution_fields': surface.get('resolvable', [])}
    matches = []
    for candidate in surface['labels']:
        rows = conn.execute('SELECT 1 FROM ' + _qi(table) + ' WHERE ' + _qi(candidate) + ' = ? LIMIT 2', (label_value,)).fetchall()
        if len(rows) == 1:
            matches.append(candidate)
    if len(matches) == 1:
        return matches[0], None
    if len(matches) == 0:
        return None, {'error': 'not_found', 'message': 'no record matched the generic business handle', 'table': table, 'value': label_value}
    return None, {'error': 'ambiguous_match', 'message': 'business handle matched more than one declared field', 'fields': matches}

def sales_records_agent(db_path, request=None, **kwargs):
    if not request or not str(request).strip():
        return {"error": "validation_error", "message": "request is required"}
    req = str(request).strip()
    # Safe bounded table inventory: production users and delegation
    # agents routinely ask to list a small queue before resolving one
    # item. This remains read-only and hard-caps the returned candidates.
    list_match = re.search(r'(?:in\s+)?table\s+"?([A-Za-z_][A-Za-z0-9_]*)"?\s*,?\s*list\s+all\b', req, re.I | re.S)
    if list_match and re.search(r'\b(?:return|show|read|retrieve|report|give|inspect|check)\b', req[list_match.end():], re.I | re.S):
        table = list_match.group(1)
        surface = _SURFACES.get(table)
        if surface is None:
            return {"error": "out_of_scope", "message": "table is not owned by this department", "available_tables": sorted(_SURFACES)}
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute('SELECT * FROM ' + _qi(table) + ' LIMIT 50').fetchall()
            return {"status": "found", "table": table, "count": len(rows), "records": [dict(row) for row in rows],
                    "resolution_receipt": {"request": req, "strategy": "bounded_table_list", "candidate_limit": 50, "match_count": len(rows), "available_business_handle_fields": surface.get("labels", []), "returned_fields": sorted(rows[0].keys()) if rows else [], "read_only": True, "mutation_applied": False}}
        finally:
            conn.close()
    # Safe production-style filtered read: one equality predicate plus
    # an optional NOT-IN clause. Field names must belong to the compiled
    # surface and every value remains parameterized.
    filter_match = re.search(r'(?:in\s+)?table\s+"?([A-Za-z_][A-Za-z0-9_]*)"?[\s\S]*?\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:any|all|the)?[\s\S]{0,120}?\b(?:with|whose|that\s+(?:references?|has)|referencing)\s+([A-Za-z_][A-Za-z0-9_]*)\s+(?:(?:is|equals?|matches?)\s+)?"([^"]+)"', req, re.I | re.S)
    if filter_match and re.search(r'\b(?:return|show|read|retrieve|report|give|inspect|check)\b', req[filter_match.end():], re.I | re.S):
        table, equal_field, equal_value = filter_match.groups()
        surface = _SURFACES.get(table)
        if surface is None:
            return {"error": "out_of_scope", "message": "table is not owned by this department", "available_tables": sorted(_SURFACES)}
        allowed_fields = set(surface.get('readable', []))
        if equal_field not in allowed_fields:
            return {"error": "invalid_filter_field", "message": "filter field is outside the compiled records surface", "allowed": sorted(allowed_fields)}
        negative = re.search(r'\band\s+([A-Za-z_][A-Za-z0-9_]*)\s+(?:is\s+)?not\s+"([^"]+)"(?:\s+or\s+"([^"]+)")?', req[filter_match.end():], re.I | re.S)
        clauses, values = [_qi(equal_field) + ' = ?'], [equal_value]
        filter_receipt = {equal_field: equal_value}
        if negative:
            negative_field = negative.group(1)
            negative_values = [value for value in negative.groups()[1:] if value is not None]
            if negative_field not in allowed_fields:
                return {"error": "invalid_filter_field", "message": "exclusion field is outside the compiled records surface", "allowed": sorted(allowed_fields)}
            clauses.append(_qi(negative_field) + ' NOT IN (' + ','.join('?' for _ in negative_values) + ')')
            values.extend(negative_values)
            filter_receipt[negative_field + '__not_in'] = negative_values
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute('SELECT * FROM ' + _qi(table) + ' WHERE ' + ' AND '.join(clauses) + ' LIMIT 50', values).fetchall()
            return {"status": "found", "table": table, "filters": filter_receipt, "count": len(rows), "records": [dict(row) for row in rows],
                    "resolution_receipt": {"request": req, "strategy": "parameterized_filter", "candidate_limit": 50, "match_count": len(rows), "allowed_filter_fields": sorted(allowed_fields), "returned_fields": sorted(rows[0].keys()) if rows else [], "read_only": True, "mutation_applied": False}}
        finally:
            conn.close()
    count_match = re.search(r'(?:in\s+)?table\s+"?([A-Za-z_][A-Za-z0-9_]*)"?\s*,?\s*(?:count|return\s+(?:the\s+)?(?:total\s+)?(?:number|count))\b', req, re.I | re.S)
    if count_match:
        table = count_match.group(1)
        if table not in _SURFACES:
            return {"error": "out_of_scope", "message": "table is not owned by this department", "available_tables": sorted(_SURFACES)}
        conn = sqlite3.connect(db_path)
        try:
            count = conn.execute('SELECT COUNT(*) FROM ' + _qi(table)).fetchone()[0]
            return {"status": "counted", "table": table, "count": count,
                    "resolution_receipt": {"request": req, "strategy": "exact_table_count", "table_scope": table, "read_only": True, "mutation_applied": False, "available_business_handle_fields": _SURFACES[table].get("labels", [])}}
        finally:
            conn.close()
    match = _parse_request_target(req)
    if match is None:
        return {"error": "request_not_understood", "message": "Use: in table <table>, find (or look up / locate / retrieve) <business_field> \"<value>\" and return the complete record", "available_tables": sorted(_SURFACES)}
    table, label_field, label_value, action_start = match
    if not re.search(r'\b(?:return|show|read|retrieve|report|give|inspect|check)\b', req[action_start:], re.I | re.S):
        return {"error": "request_not_understood", "message": "The records sub-agent requires an explicit read/report action after the business handle", "available_tables": sorted(_SURFACES)}
    surface = _SURFACES.get(table)
    if surface is None:
        return {"error": "out_of_scope", "message": "table is not owned by this department", "available_tables": sorted(_SURFACES)}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        label_field, handle_error = _resolve_label_field(conn, table, surface, label_field, label_value)
        if handle_error is not None:
            return handle_error
        rows = conn.execute('SELECT * FROM ' + _qi(table) + ' WHERE ' + _qi(label_field) + ' = ? LIMIT 3', (label_value,)).fetchall()
        if len(rows) == 0:
            return {"error": "not_found", "message": "no record matched the business handle", "table": table, "field": label_field, "value": label_value}
        if len(rows) > 1:
            return {"error": "ambiguous_match", "message": "business handle matched multiple records", "match_count": len(rows)}
        record = dict(rows[0])
        lifecycles = surface.get('lifecycles', {})
        next_values = {}
        for field, values in lifecycles.items():
            choices = _next_lifecycle_values(values, record.get(field))
            if choices:
                next_values[field] = choices[0] if len(choices) == 1 else choices
        return {"status": "found", "table": table, "business_handle": {label_field: label_value}, "record": record, "declared_lifecycles": lifecycles, "next_valid_values": next_values,
                "resolution_receipt": {"request": req, "strategy": "unique_business_handle" if label_field in surface.get("labels", []) else "unique_readable_attribute", "candidate_limit": 3, "match_count": 1, "matched_field": label_field, "available_business_handle_fields": surface.get("labels", []), "available_resolution_fields": surface.get("resolvable", []), "returned_fields": sorted(record), "read_only": True, "mutation_applied": False},
                "workflow_context": {"mutable_fields": surface.get("mutable", []), "declared_lifecycle_fields": sorted(lifecycles)}}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_sales_records_agent = sales_records_agent
def _bf_friction_sales_records_agent(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_sales_records_agent(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "sales_records_agent|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("b1e4baa134cb7067|" + _bf_sig).encode("utf-8")).hexdigest()
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
    return _bf_orig_sales_records_agent(*_bf_args, **_bf_kwargs)
_bf_friction_sales_records_agent.blobfish_original = _bf_orig_sales_records_agent
sales_records_agent = _bf_friction_sales_records_agent

"""Department records sub-agent: resolve one unique business handle from a free-text request without mutating state."""
import re, sqlite3

_SURFACES = {"sourcing_vendors":{"table":"sourcing_vendors","primary_key":"id","labels":["vendor_number","name","contact_name"],"readable":["id","vendor_number","name","category","contact_name","owner_employee_id","onboarded_at","status"],"resolvable":["vendor_number","name","category","contact_name","owner_employee_id","onboarded_at"],"mutable":["vendor_number","name","category","contact_name","onboarded_at","status"],"lifecycles":{"status":["prospective","under_review","approved","suspended"]}},"sourcing_purchase_orders":{"table":"sourcing_purchase_orders","primary_key":"id","labels":["po_number"],"readable":["id","po_number","vendor_id","requested_by_employee_id","amount","ordered_at","approver_employee_id","status"],"resolvable":["po_number","vendor_id","requested_by_employee_id","amount","ordered_at","approver_employee_id"],"mutable":["po_number","amount","ordered_at","status"],"lifecycles":{"status":["draft","submitted","approved","received","closed"]}}}

def _qi(name):
    return '"' + str(name).replace('"', '""') + '"'

_OUTCOME_GROUPS = [["approved","rejected","denied","declined"],["completed","cancelled","canceled","failed"],["paid","failed"],["closed_won","closed_lost"],["accepted","rejected"],["hired","rejected"]]
def _norm_status(value):
    return str(value).strip().strip("'\"").lower()
def _outcome_group(values, candidate):
    available = {_norm_status(item) for item in values}
    target = _norm_status(candidate)
    candidates = [group for group in _OUTCOME_GROUPS if target in group and sum(1 for item in group if item in available) >= 2]
    return max(candidates, key=lambda group: sum(1 for item in group if item in available)) if candidates else None
def _next_lifecycle_values(values, current):
    normalized = [_norm_status(item) for item in values]
    target = _norm_status(current)
    if target not in normalized:
        return []
    index = normalized.index(target)
    current_branch = _outcome_group(values, values[index])
    successor_index = index + 1
    if current_branch:
        branch_indices = [i for i, item in enumerate(values) if _norm_status(item) in current_branch]
        if index != min(branch_indices):
            return []
        while successor_index < len(values) and _norm_status(values[successor_index]) in current_branch:
            successor_index += 1
    if successor_index >= len(values):
        return []
    candidate = values[successor_index]
    candidate_branch = _outcome_group(values, candidate)
    if not candidate_branch:
        return [candidate]
    branch_indices = [i for i, item in enumerate(values) if _norm_status(item) in candidate_branch]
    if min(branch_indices) <= index:
        return []
    return [item for item in values if _norm_status(item) in candidate_branch]
def _invalid_lifecycle_transition(values, before, after):
    normalized = [_norm_status(item) for item in values]
    current, target = _norm_status(before), _norm_status(after)
    if current not in normalized or target not in normalized:
        return True
    if current == target:
        return False
    return target not in [_norm_status(item) for item in _next_lifecycle_values(values, before)]
def _lifecycle_action_terms(value):
    normalized = re.sub(r'[^a-z0-9]+', '_', _norm_status(value)).strip('_')
    aliases = {
        'approved': ['approve'], 'declined': ['decline', 'reject'],
        'completed': ['complete', 'finish'], 'cancelled': ['cancel'],
        'succeeded': ['succeed'], 'failed': ['fail'],
        'closed_won': ['won', 'win'], 'closed_lost': ['lost', 'lose'],
        'reviewed': ['review'], 'verified': ['verify'], 'retained': ['retain'],
        'archived': ['archive'], 'published': ['publish'], 'packed': ['pack'],
        'shipped': ['ship'],
    }
    terms = [normalized, *aliases.get(normalized, [])]
    if normalized.endswith('ied') and len(normalized) > 3:
        terms.append(normalized[:-3] + 'y')
    elif normalized.endswith('ed') and len(normalized) > 2:
        terms.extend([normalized[:-2], normalized[:-1]])
    return list(dict.fromkeys(term for term in terms if term))

def _parse_request_target(req):
    table_match = re.search(r'(?:in\s+)?table\s+"?([A-Za-z_][A-Za-z0-9_]*)"?', req, re.I | re.S)
    if not table_match:
        return None
    table = table_match.group(1)
    surface = _SURFACES.get(table)
    tail = req[table_match.end():]
    generic_handle = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?business\s+(?:handle|label|key|identifier|reference|ref)\s+"([^"]+)"', tail, re.I | re.S)
    canonical = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+([A-Za-z_][A-Za-z0-9_]*)\s+"([^"]+)"', tail, re.I | re.S)
    descriptive = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+(?:with|by)\s+(?:(business\s+(?:handle|label|key|identifier|reference|ref))|([A-Za-z_][A-Za-z0-9_]*))\s+"([^"]+)"', tail, re.I | re.S)
    whose_alias = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+whose\s+(?:(?:[A-Za-z_][A-Za-z0-9_]*\s+or\s+)?business\s+(?:handle|label|key|identifier|reference|ref)|business\s+(?:handle|label|key|identifier|reference|ref)\s+or\s+[A-Za-z_][A-Za-z0-9_]*)\s+(?:(?:is|equals?|match(?:es)?)\s+|corresponds?(?:\s+to)?(?:\s+(?:the\s+)?[A-Za-z][A-Za-z0-9 _-]{0,60})?\s+)?"([^"]+)"', tail, re.I | re.S)
    whose = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+whose\s+(?:(business\s+(?:handle|label|key|identifier|reference|ref))|([A-Za-z_][A-Za-z0-9_]*))\s+(?:(?:is|equals?|match(?:es)?)\s+|corresponds?(?:\s+to)?(?:\s+(?:the\s+)?[A-Za-z][A-Za-z0-9 _-]{0,60})?\s+)?"([^"]+)"', tail, re.I | re.S)
    associated = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+associated\s+with\s+(?:(business\s+(?:handle|label|key|identifier|reference|ref))|([A-Za-z_][A-Za-z0-9_]*))\s+"([^"]+)"', tail, re.I | re.S)
    named = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+named\s+"([^"]+)"', tail, re.I | re.S)
    natural_for = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9 _-]{0,60}?\s+for\s+([A-Za-z][A-Za-z0-9 .\'-]{1,80}?)\s+(?=and\s+(?:return|show|read|retrieve|report|give|inspect|check)\b)', tail, re.I | re.S)
    if generic_handle:
        label_field = 'business_handle'
        label_value = generic_handle.group(1)
        action_start = table_match.end() + generic_handle.end()
    elif canonical:
        label_field, label_value = canonical.group(1), canonical.group(2)
        action_start = table_match.end() + canonical.end()
    elif descriptive:
        label_field = 'business_handle' if descriptive.group(1) else descriptive.group(2)
        label_value = descriptive.group(3)
        action_start = table_match.end() + descriptive.end()
    elif whose_alias:
        label_field = 'business_handle'
        label_value = whose_alias.group(1)
        action_start = table_match.end() + whose_alias.end()
    elif whose:
        label_field = 'business_handle' if whose.group(1) else whose.group(2)
        label_value = whose.group(3)
        action_start = table_match.end() + whose.end()
    elif associated:
        label_field = 'business_handle' if associated.group(1) else associated.group(2)
        label_value = associated.group(3)
        action_start = table_match.end() + associated.end()
    elif named:
        label_field = 'business_handle'
        label_value = named.group(1)
        action_start = table_match.end() + named.end()
    elif natural_for and surface is not None and len(surface['labels']) == 1:
        label_field = surface['labels'][0]
        label_value = natural_for.group(1).strip()
        action_start = table_match.end() + natural_for.end()
    else:
        return None
    if surface is not None and label_field not in surface['labels']:
        entity = table[:-3] + 'y' if table.endswith('ies') else (table[:-1] if table.endswith('s') else table)
        aliases = {'handle', 'business_handle', 'business_ref', 'record', 'item', 'case', entity.lower()}
        if str(label_field).lower() == 'id' and surface['primary_key'] in surface['labels']:
            label_field = surface['primary_key']
        elif str(label_field).lower() in aliases and len(surface['labels']) == 1:
            label_field = surface['labels'][0]
        elif str(label_field).lower() in aliases:
            label_field = '__business_handle__'
    return table, label_field, label_value, action_start
def _resolve_label_field(conn, table, surface, label_field, label_value):
    if label_field in surface['labels']:
        return label_field, None
    if label_field in surface.get('resolvable', []):
        rows = conn.execute('SELECT 1 FROM ' + _qi(table) + ' WHERE ' + _qi(label_field) + ' = ? LIMIT 3', (label_value,)).fetchall()
        if len(rows) == 1:
            return label_field, None
        if len(rows) == 0:
            return None, {'error': 'not_found', 'message': 'no record matched the exact resolution attribute', 'table': table, 'field': label_field, 'value': label_value}
        return None, {'error': 'ambiguous_match', 'message': 'resolution attribute matched multiple records', 'field': label_field, 'match_count': len(rows)}
    if label_field != '__business_handle__':
        return None, {'error': 'invalid_business_handle', 'message': 'use a declared business handle or exact non-lifecycle resolution field', 'allowed': surface['labels'], 'resolution_fields': surface.get('resolvable', [])}
    matches = []
    for candidate in surface['labels']:
        rows = conn.execute('SELECT 1 FROM ' + _qi(table) + ' WHERE ' + _qi(candidate) + ' = ? LIMIT 2', (label_value,)).fetchall()
        if len(rows) == 1:
            matches.append(candidate)
    if len(matches) == 1:
        return matches[0], None
    if len(matches) == 0:
        return None, {'error': 'not_found', 'message': 'no record matched the generic business handle', 'table': table, 'value': label_value}
    return None, {'error': 'ambiguous_match', 'message': 'business handle matched more than one declared field', 'fields': matches}

def sourcing_records_agent(db_path, request=None, **kwargs):
    if not request or not str(request).strip():
        return {"error": "validation_error", "message": "request is required"}
    req = str(request).strip()
    # Safe bounded table inventory: production users and delegation
    # agents routinely ask to list a small queue before resolving one
    # item. This remains read-only and hard-caps the returned candidates.
    list_match = re.search(r'(?:in\s+)?table\s+"?([A-Za-z_][A-Za-z0-9_]*)"?\s*,?\s*list\s+all\b', req, re.I | re.S)
    if list_match and re.search(r'\b(?:return|show|read|retrieve|report|give|inspect|check)\b', req[list_match.end():], re.I | re.S):
        table = list_match.group(1)
        surface = _SURFACES.get(table)
        if surface is None:
            return {"error": "out_of_scope", "message": "table is not owned by this department", "available_tables": sorted(_SURFACES)}
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute('SELECT * FROM ' + _qi(table) + ' LIMIT 50').fetchall()
            return {"status": "found", "table": table, "count": len(rows), "records": [dict(row) for row in rows],
                    "resolution_receipt": {"request": req, "strategy": "bounded_table_list", "candidate_limit": 50, "match_count": len(rows), "available_business_handle_fields": surface.get("labels", []), "returned_fields": sorted(rows[0].keys()) if rows else [], "read_only": True, "mutation_applied": False}}
        finally:
            conn.close()
    # Safe production-style filtered read: one equality predicate plus
    # an optional NOT-IN clause. Field names must belong to the compiled
    # surface and every value remains parameterized.
    filter_match = re.search(r'(?:in\s+)?table\s+"?([A-Za-z_][A-Za-z0-9_]*)"?[\s\S]*?\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:any|all|the)?[\s\S]{0,120}?\b(?:with|whose|that\s+(?:references?|has)|referencing)\s+([A-Za-z_][A-Za-z0-9_]*)\s+(?:(?:is|equals?|matches?)\s+)?"([^"]+)"', req, re.I | re.S)
    if filter_match and re.search(r'\b(?:return|show|read|retrieve|report|give|inspect|check)\b', req[filter_match.end():], re.I | re.S):
        table, equal_field, equal_value = filter_match.groups()
        surface = _SURFACES.get(table)
        if surface is None:
            return {"error": "out_of_scope", "message": "table is not owned by this department", "available_tables": sorted(_SURFACES)}
        allowed_fields = set(surface.get('readable', []))
        if equal_field not in allowed_fields:
            return {"error": "invalid_filter_field", "message": "filter field is outside the compiled records surface", "allowed": sorted(allowed_fields)}
        negative = re.search(r'\band\s+([A-Za-z_][A-Za-z0-9_]*)\s+(?:is\s+)?not\s+"([^"]+)"(?:\s+or\s+"([^"]+)")?', req[filter_match.end():], re.I | re.S)
        clauses, values = [_qi(equal_field) + ' = ?'], [equal_value]
        filter_receipt = {equal_field: equal_value}
        if negative:
            negative_field = negative.group(1)
            negative_values = [value for value in negative.groups()[1:] if value is not None]
            if negative_field not in allowed_fields:
                return {"error": "invalid_filter_field", "message": "exclusion field is outside the compiled records surface", "allowed": sorted(allowed_fields)}
            clauses.append(_qi(negative_field) + ' NOT IN (' + ','.join('?' for _ in negative_values) + ')')
            values.extend(negative_values)
            filter_receipt[negative_field + '__not_in'] = negative_values
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute('SELECT * FROM ' + _qi(table) + ' WHERE ' + ' AND '.join(clauses) + ' LIMIT 50', values).fetchall()
            return {"status": "found", "table": table, "filters": filter_receipt, "count": len(rows), "records": [dict(row) for row in rows],
                    "resolution_receipt": {"request": req, "strategy": "parameterized_filter", "candidate_limit": 50, "match_count": len(rows), "allowed_filter_fields": sorted(allowed_fields), "returned_fields": sorted(rows[0].keys()) if rows else [], "read_only": True, "mutation_applied": False}}
        finally:
            conn.close()
    count_match = re.search(r'(?:in\s+)?table\s+"?([A-Za-z_][A-Za-z0-9_]*)"?\s*,?\s*(?:count|return\s+(?:the\s+)?(?:total\s+)?(?:number|count))\b', req, re.I | re.S)
    if count_match:
        table = count_match.group(1)
        if table not in _SURFACES:
            return {"error": "out_of_scope", "message": "table is not owned by this department", "available_tables": sorted(_SURFACES)}
        conn = sqlite3.connect(db_path)
        try:
            count = conn.execute('SELECT COUNT(*) FROM ' + _qi(table)).fetchone()[0]
            return {"status": "counted", "table": table, "count": count,
                    "resolution_receipt": {"request": req, "strategy": "exact_table_count", "table_scope": table, "read_only": True, "mutation_applied": False, "available_business_handle_fields": _SURFACES[table].get("labels", [])}}
        finally:
            conn.close()
    match = _parse_request_target(req)
    if match is None:
        return {"error": "request_not_understood", "message": "Use: in table <table>, find (or look up / locate / retrieve) <business_field> \"<value>\" and return the complete record", "available_tables": sorted(_SURFACES)}
    table, label_field, label_value, action_start = match
    if not re.search(r'\b(?:return|show|read|retrieve|report|give|inspect|check)\b', req[action_start:], re.I | re.S):
        return {"error": "request_not_understood", "message": "The records sub-agent requires an explicit read/report action after the business handle", "available_tables": sorted(_SURFACES)}
    surface = _SURFACES.get(table)
    if surface is None:
        return {"error": "out_of_scope", "message": "table is not owned by this department", "available_tables": sorted(_SURFACES)}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        label_field, handle_error = _resolve_label_field(conn, table, surface, label_field, label_value)
        if handle_error is not None:
            return handle_error
        rows = conn.execute('SELECT * FROM ' + _qi(table) + ' WHERE ' + _qi(label_field) + ' = ? LIMIT 3', (label_value,)).fetchall()
        if len(rows) == 0:
            return {"error": "not_found", "message": "no record matched the business handle", "table": table, "field": label_field, "value": label_value}
        if len(rows) > 1:
            return {"error": "ambiguous_match", "message": "business handle matched multiple records", "match_count": len(rows)}
        record = dict(rows[0])
        lifecycles = surface.get('lifecycles', {})
        next_values = {}
        for field, values in lifecycles.items():
            choices = _next_lifecycle_values(values, record.get(field))
            if choices:
                next_values[field] = choices[0] if len(choices) == 1 else choices
        return {"status": "found", "table": table, "business_handle": {label_field: label_value}, "record": record, "declared_lifecycles": lifecycles, "next_valid_values": next_values,
                "resolution_receipt": {"request": req, "strategy": "unique_business_handle" if label_field in surface.get("labels", []) else "unique_readable_attribute", "candidate_limit": 3, "match_count": 1, "matched_field": label_field, "available_business_handle_fields": surface.get("labels", []), "available_resolution_fields": surface.get("resolvable", []), "returned_fields": sorted(record), "read_only": True, "mutation_applied": False},
                "workflow_context": {"mutable_fields": surface.get("mutable", []), "declared_lifecycle_fields": sorted(lifecycles)}}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_sourcing_records_agent = sourcing_records_agent
def _bf_friction_sourcing_records_agent(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_sourcing_records_agent(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "sourcing_records_agent|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("b1e4baa134cb7067|" + _bf_sig).encode("utf-8")).hexdigest()
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
    return _bf_orig_sourcing_records_agent(*_bf_args, **_bf_kwargs)
_bf_friction_sourcing_records_agent.blobfish_original = _bf_orig_sourcing_records_agent
sourcing_records_agent = _bf_friction_sourcing_records_agent

import sqlite3

def list_lead(db_path):
    """List all lead records"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = [dict(row) for row in conn.execute("SELECT * FROM lead").fetchall()]
    conn.close()
    return {"rows": rows, "count": len(rows)}

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_list_lead = list_lead
def _bf_friction_list_lead(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_list_lead(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "list_lead|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("b1e4baa134cb7067|" + _bf_sig).encode("utf-8")).hexdigest()
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
    return _bf_orig_list_lead(*_bf_args, **_bf_kwargs)
_bf_friction_list_lead.blobfish_original = _bf_orig_list_lead
list_lead = _bf_friction_list_lead

import sqlite3

def get_account(db_path, id):
    """Get account by id"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM account WHERE id = ?", (id,)).fetchone()
    conn.close()
    if row is None:
        return {"error": "not found"}
    return {"rows": [dict(row)]}

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_account = get_account
def _bf_friction_get_account(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_account(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_account|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("b1e4baa134cb7067|" + _bf_sig).encode("utf-8")).hexdigest()
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
    return _bf_orig_get_account(*_bf_args, **_bf_kwargs)
_bf_friction_get_account.blobfish_original = _bf_orig_get_account
get_account = _bf_friction_get_account

import sqlite3

def list_account(db_path):
    """List all account records"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = [dict(row) for row in conn.execute("SELECT * FROM account").fetchall()]
    conn.close()
    return {"rows": rows, "count": len(rows)}

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_list_account = list_account
def _bf_friction_list_account(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_list_account(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "list_account|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("b1e4baa134cb7067|" + _bf_sig).encode("utf-8")).hexdigest()
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
    return _bf_orig_list_account(*_bf_args, **_bf_kwargs)
_bf_friction_list_account.blobfish_original = _bf_orig_list_account
list_account = _bf_friction_list_account

import sqlite3

def list_opportunity(db_path):
    """List all opportunity records"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = [dict(row) for row in conn.execute("SELECT * FROM opportunity").fetchall()]
    conn.close()
    return {"rows": rows, "count": len(rows)}

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_list_opportunity = list_opportunity
def _bf_friction_list_opportunity(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_list_opportunity(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "list_opportunity|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("b1e4baa134cb7067|" + _bf_sig).encode("utf-8")).hexdigest()
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
    return _bf_orig_list_opportunity(*_bf_args, **_bf_kwargs)
_bf_friction_list_opportunity.blobfish_original = _bf_orig_list_opportunity
list_opportunity = _bf_friction_list_opportunity

import sqlite3

def get_lead(db_path, id):
    """Get lead by id"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM lead WHERE id = ?", (id,)).fetchone()
    conn.close()
    if row is None:
        return {"error": "not found"}
    return {"rows": [dict(row)]}

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_lead = get_lead
def _bf_friction_get_lead(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_lead(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_lead|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("b1e4baa134cb7067|" + _bf_sig).encode("utf-8")).hexdigest()
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
    return _bf_orig_get_lead(*_bf_args, **_bf_kwargs)
_bf_friction_get_lead.blobfish_original = _bf_orig_get_lead
get_lead = _bf_friction_get_lead

import sqlite3

def get_opportunity(db_path, id):
    """Get opportunity by id"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM opportunity WHERE id = ?", (id,)).fetchone()
    conn.close()
    if row is None:
        return {"error": "not found"}
    return {"rows": [dict(row)]}

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_opportunity = get_opportunity
def _bf_friction_get_opportunity(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_opportunity(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_opportunity|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("b1e4baa134cb7067|" + _bf_sig).encode("utf-8")).hexdigest()
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
    return _bf_orig_get_opportunity(*_bf_args, **_bf_kwargs)
_bf_friction_get_opportunity.blobfish_original = _bf_orig_get_opportunity
get_opportunity = _bf_friction_get_opportunity

"""Query sales_leads"""
import sqlite3

def query_sales_leads(db_path: str, **filters) -> dict:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row_limit = min(int(filters.pop("limit", 100)), 500)
    sql = 'SELECT * FROM "sales_leads" WHERE 1=1'
    params = []
    valid_cols = {c[1] for c in conn.execute('PRAGMA table_info("sales_leads")').fetchall()}
    for k, v in filters.items():
        if k in valid_cols:
            quoted_k = '"' + k.replace('"', '""') + '"'
            sql += f" AND {quoted_k} = ?"
            params.append(v)
    sql += " LIMIT ?"
    params.append(row_limit)
    rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
    conn.close()
    return {"table": "sales_leads", "count": len(rows), "rows": rows}

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_query_sales_leads = query_sales_leads
def _bf_friction_query_sales_leads(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_query_sales_leads(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "query_sales_leads|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("b1e4baa134cb7067|" + _bf_sig).encode("utf-8")).hexdigest()
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
    return _bf_orig_query_sales_leads(*_bf_args, **_bf_kwargs)
_bf_friction_query_sales_leads.blobfish_original = _bf_orig_query_sales_leads
query_sales_leads = _bf_friction_query_sales_leads

"""Look up sales_lead with employees context"""
import sqlite3

def lookup_sales_lead_with_employees(db_path: str, id: int) -> dict:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM sales_leads WHERE id = ?", [id]).fetchone()
    if not row:
        conn.close()
        return {"error": f"sales_lead {id} not found"}
    result = dict(row)
    parent = conn.execute("SELECT * FROM employees WHERE id = ?", [row["owner_employee_id"]]).fetchone()
    result["employees"] = dict(parent) if parent else None
    conn.close()
    return result

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_lookup_sales_lead_with_employees = lookup_sales_lead_with_employees
def _bf_friction_lookup_sales_lead_with_employees(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_lookup_sales_lead_with_employees(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "lookup_sales_lead_with_employees|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("b1e4baa134cb7067|" + _bf_sig).encode("utf-8")).hexdigest()
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
    return _bf_orig_lookup_sales_lead_with_employees(*_bf_args, **_bf_kwargs)
_bf_friction_lookup_sales_lead_with_employees.blobfish_original = _bf_orig_lookup_sales_lead_with_employees
lookup_sales_lead_with_employees = _bf_friction_lookup_sales_lead_with_employees

"""Department workflow sub-agent: resolve one business handle and apply one narrow field update from a free-text request."""
import json, re, sqlite3

_SURFACES = {"account":{"table":"account","primary_key":"id","labels":["name"],"readable":["id","name","segment","region","tier","newclient","status","created_at"],"resolvable":["name","segment","region","tier","newclient","status","created_at"],"mutable":["name","segment","region","tier","newclient","status"],"lifecycles":{}},"activity":{"table":"activity","primary_key":"id","labels":["subject"],"readable":["id","subject","status","created_at"],"resolvable":["subject","status","created_at"],"mutable":["subject","status"],"lifecycles":{}}}

def _qi(name):
    return '"' + str(name).replace('"', '""') + '"'

_OUTCOME_GROUPS = [["approved","rejected","denied","declined"],["completed","cancelled","canceled","failed"],["paid","failed"],["closed_won","closed_lost"],["accepted","rejected"],["hired","rejected"]]
def _norm_status(value):
    return str(value).strip().strip("'\"").lower()
def _outcome_group(values, candidate):
    available = {_norm_status(item) for item in values}
    target = _norm_status(candidate)
    candidates = [group for group in _OUTCOME_GROUPS if target in group and sum(1 for item in group if item in available) >= 2]
    return max(candidates, key=lambda group: sum(1 for item in group if item in available)) if candidates else None
def _next_lifecycle_values(values, current):
    normalized = [_norm_status(item) for item in values]
    target = _norm_status(current)
    if target not in normalized:
        return []
    index = normalized.index(target)
    current_branch = _outcome_group(values, values[index])
    successor_index = index + 1
    if current_branch:
        branch_indices = [i for i, item in enumerate(values) if _norm_status(item) in current_branch]
        if index != min(branch_indices):
            return []
        while successor_index < len(values) and _norm_status(values[successor_index]) in current_branch:
            successor_index += 1
    if successor_index >= len(values):
        return []
    candidate = values[successor_index]
    candidate_branch = _outcome_group(values, candidate)
    if not candidate_branch:
        return [candidate]
    branch_indices = [i for i, item in enumerate(values) if _norm_status(item) in candidate_branch]
    if min(branch_indices) <= index:
        return []
    return [item for item in values if _norm_status(item) in candidate_branch]
def _invalid_lifecycle_transition(values, before, after):
    normalized = [_norm_status(item) for item in values]
    current, target = _norm_status(before), _norm_status(after)
    if current not in normalized or target not in normalized:
        return True
    if current == target:
        return False
    return target not in [_norm_status(item) for item in _next_lifecycle_values(values, before)]
def _lifecycle_action_terms(value):
    normalized = re.sub(r'[^a-z0-9]+', '_', _norm_status(value)).strip('_')
    aliases = {
        'approved': ['approve'], 'declined': ['decline', 'reject'],
        'completed': ['complete', 'finish'], 'cancelled': ['cancel'],
        'succeeded': ['succeed'], 'failed': ['fail'],
        'closed_won': ['won', 'win'], 'closed_lost': ['lost', 'lose'],
        'reviewed': ['review'], 'verified': ['verify'], 'retained': ['retain'],
        'archived': ['archive'], 'published': ['publish'], 'packed': ['pack'],
        'shipped': ['ship'],
    }
    terms = [normalized, *aliases.get(normalized, [])]
    if normalized.endswith('ied') and len(normalized) > 3:
        terms.append(normalized[:-3] + 'y')
    elif normalized.endswith('ed') and len(normalized) > 2:
        terms.extend([normalized[:-2], normalized[:-1]])
    return list(dict.fromkeys(term for term in terms if term))

def _parse_request_target(req):
    table_match = re.search(r'(?:in\s+)?table\s+"?([A-Za-z_][A-Za-z0-9_]*)"?', req, re.I | re.S)
    if not table_match:
        return None
    table = table_match.group(1)
    surface = _SURFACES.get(table)
    tail = req[table_match.end():]
    generic_handle = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?business\s+(?:handle|label|key|identifier|reference|ref)\s+"([^"]+)"', tail, re.I | re.S)
    canonical = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+([A-Za-z_][A-Za-z0-9_]*)\s+"([^"]+)"', tail, re.I | re.S)
    descriptive = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+(?:with|by)\s+(?:(business\s+(?:handle|label|key|identifier|reference|ref))|([A-Za-z_][A-Za-z0-9_]*))\s+"([^"]+)"', tail, re.I | re.S)
    whose_alias = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+whose\s+(?:(?:[A-Za-z_][A-Za-z0-9_]*\s+or\s+)?business\s+(?:handle|label|key|identifier|reference|ref)|business\s+(?:handle|label|key|identifier|reference|ref)\s+or\s+[A-Za-z_][A-Za-z0-9_]*)\s+(?:(?:is|equals?|match(?:es)?)\s+|corresponds?(?:\s+to)?(?:\s+(?:the\s+)?[A-Za-z][A-Za-z0-9 _-]{0,60})?\s+)?"([^"]+)"', tail, re.I | re.S)
    whose = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+whose\s+(?:(business\s+(?:handle|label|key|identifier|reference|ref))|([A-Za-z_][A-Za-z0-9_]*))\s+(?:(?:is|equals?|match(?:es)?)\s+|corresponds?(?:\s+to)?(?:\s+(?:the\s+)?[A-Za-z][A-Za-z0-9 _-]{0,60})?\s+)?"([^"]+)"', tail, re.I | re.S)
    associated = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+associated\s+with\s+(?:(business\s+(?:handle|label|key|identifier|reference|ref))|([A-Za-z_][A-Za-z0-9_]*))\s+"([^"]+)"', tail, re.I | re.S)
    named = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+named\s+"([^"]+)"', tail, re.I | re.S)
    natural_for = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9 _-]{0,60}?\s+for\s+([A-Za-z][A-Za-z0-9 .\'-]{1,80}?)\s+(?=and\s+(?:return|show|read|retrieve|report|give|inspect|check)\b)', tail, re.I | re.S)
    if generic_handle:
        label_field = 'business_handle'
        label_value = generic_handle.group(1)
        action_start = table_match.end() + generic_handle.end()
    elif canonical:
        label_field, label_value = canonical.group(1), canonical.group(2)
        action_start = table_match.end() + canonical.end()
    elif descriptive:
        label_field = 'business_handle' if descriptive.group(1) else descriptive.group(2)
        label_value = descriptive.group(3)
        action_start = table_match.end() + descriptive.end()
    elif whose_alias:
        label_field = 'business_handle'
        label_value = whose_alias.group(1)
        action_start = table_match.end() + whose_alias.end()
    elif whose:
        label_field = 'business_handle' if whose.group(1) else whose.group(2)
        label_value = whose.group(3)
        action_start = table_match.end() + whose.end()
    elif associated:
        label_field = 'business_handle' if associated.group(1) else associated.group(2)
        label_value = associated.group(3)
        action_start = table_match.end() + associated.end()
    elif named:
        label_field = 'business_handle'
        label_value = named.group(1)
        action_start = table_match.end() + named.end()
    elif natural_for and surface is not None and len(surface['labels']) == 1:
        label_field = surface['labels'][0]
        label_value = natural_for.group(1).strip()
        action_start = table_match.end() + natural_for.end()
    else:
        return None
    if surface is not None and label_field not in surface['labels']:
        entity = table[:-3] + 'y' if table.endswith('ies') else (table[:-1] if table.endswith('s') else table)
        aliases = {'handle', 'business_handle', 'business_ref', 'record', 'item', 'case', entity.lower()}
        if str(label_field).lower() == 'id' and surface['primary_key'] in surface['labels']:
            label_field = surface['primary_key']
        elif str(label_field).lower() in aliases and len(surface['labels']) == 1:
            label_field = surface['labels'][0]
        elif str(label_field).lower() in aliases:
            label_field = '__business_handle__'
    return table, label_field, label_value, action_start
def _resolve_label_field(conn, table, surface, label_field, label_value):
    if label_field in surface['labels']:
        return label_field, None
    if label_field in surface.get('resolvable', []):
        rows = conn.execute('SELECT 1 FROM ' + _qi(table) + ' WHERE ' + _qi(label_field) + ' = ? LIMIT 3', (label_value,)).fetchall()
        if len(rows) == 1:
            return label_field, None
        if len(rows) == 0:
            return None, {'error': 'not_found', 'message': 'no record matched the exact resolution attribute', 'table': table, 'field': label_field, 'value': label_value}
        return None, {'error': 'ambiguous_match', 'message': 'resolution attribute matched multiple records', 'field': label_field, 'match_count': len(rows)}
    if label_field != '__business_handle__':
        return None, {'error': 'invalid_business_handle', 'message': 'use a declared business handle or exact non-lifecycle resolution field', 'allowed': surface['labels'], 'resolution_fields': surface.get('resolvable', [])}
    matches = []
    for candidate in surface['labels']:
        rows = conn.execute('SELECT 1 FROM ' + _qi(table) + ' WHERE ' + _qi(candidate) + ' = ? LIMIT 2', (label_value,)).fetchall()
        if len(rows) == 1:
            matches.append(candidate)
    if len(matches) == 1:
        return matches[0], None
    if len(matches) == 0:
        return None, {'error': 'not_found', 'message': 'no record matched the generic business handle', 'table': table, 'value': label_value}
    return None, {'error': 'ambiguous_match', 'message': 'business handle matched more than one declared field', 'fields': matches}

def core_workflow_agent(db_path, request=None, **kwargs):
    if not request or not str(request).strip():
        return {"error": "validation_error", "message": "request is required"}
    req = str(request).strip()
    target = _parse_request_target(req)
    if target is None:
        return {"error": "request_not_understood", "message": "Use: in table <table>, find (or look up / locate / retrieve) <business_field> \"<value>\" and request one scoped update", "available_tables": sorted(_SURFACES)}
    table, label_field, label_value, action_start = target
    action = req[action_start:]
    exact = re.search(r'\band\s+(?:set|update|change|mark)\s+(?:(?:its|the)\s+)?([A-Za-z_][A-Za-z0-9_]*)(?:\s+(?:to|as)\s+|\s*=\s*)"([^"]*)"', action, re.I | re.S)
    set_next = re.search(r'\band\s+(?:set|update|change|mark)\s+(?:(?:its|the)\s+)?([A-Za-z_][A-Za-z0-9_]*)(?:\s+(?:to|as)\s+|\s*=\s*)(?:the\s+)?next\b', action, re.I | re.S)
    advance = re.search(r'\b(?:advance|move)\b(?=[\s\S]*\bnext\b)', action, re.I)
    advance_field = re.search(r'\b(?:advance|move)\s+(?:its\s+|the\s+)?([A-Za-z_][A-Za-z0-9_]*)\s+to\b', action, re.I)
    natural_transition = re.search(r'\band\s+([A-Za-z][A-Za-z0-9_-]{1,30})\s+(?:it|the\s+record|this\s+record)\b', action, re.I | re.S)
    read = re.search(r'\band\s+(?:return|show|read|retrieve|report|give|inspect|check)\b', action, re.I | re.S)
    natural_verb = None
    if exact:
        field, value = exact.groups()
    elif set_next:
        field, value = set_next.group(1), None
    elif advance:
        candidate = advance_field.group(1) if advance_field else 'status'
        field, value = ('status' if candidate.lower() in {'it', 'record', 'entry'} else candidate), None
    elif natural_transition:
        field, value = None, None
        natural_verb = natural_transition.group(1).lower()
    elif read:
        field, value = None, None
    else:
        return {"error": "request_not_understood", "message": "Request a record report, an exact field value, or the next declared lifecycle stage", "available_tables": sorted(_SURFACES)}
    surface = _SURFACES.get(table)
    if surface is None:
        return {"error": "out_of_scope", "message": "table is not owned by this department", "available_tables": sorted(_SURFACES)}
    if natural_verb is None and field is not None and field not in surface['mutable']:
        return {"error": "field_not_mutable", "message": "requested field is outside the delegated mutation surface", "allowed": surface["mutable"]}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        label_field, handle_error = _resolve_label_field(conn, table, surface, label_field, label_value)
        if handle_error is not None:
            return handle_error
        rows = conn.execute('SELECT * FROM ' + _qi(table) + ' WHERE ' + _qi(label_field) + ' = ? LIMIT 3', (label_value,)).fetchall()
        if len(rows) == 0:
            return {"error": "not_found", "message": "no record matched the business handle", "table": table, "field": label_field, "value": label_value}
        if len(rows) > 1:
            return {"error": "ambiguous_match", "message": "business handle matched multiple records", "match_count": len(rows)}
        row = rows[0]
        if natural_verb is not None:
            mentioned = []
            for lifecycle_field, lifecycle_values in surface.get('lifecycles', {}).items():
                for choice in _next_lifecycle_values(lifecycle_values, row[lifecycle_field]):
                    if natural_verb in _lifecycle_action_terms(choice):
                        mentioned.append((lifecycle_field, choice))
            if len(mentioned) == 0:
                fallback_values = {'review': 'reviewed', 'approve': 'approved', 'decline': 'declined', 'reject': 'rejected', 'close': 'closed', 'complete': 'completed', 'cancel': 'cancelled', 'archive': 'archived'}
                fallback_value = fallback_values.get(natural_verb)
                if fallback_value is not None and 'status' in surface['mutable'] and not surface.get('lifecycles', {}).get('status'):
                    field, value = 'status', fallback_value
                else:
                    return {"error": "unrecognized_lifecycle_action", "message": "the action verb does not name one next declared lifecycle value", "verb": natural_verb, "declared_lifecycles": surface.get("lifecycles", {})}
            if len(mentioned) > 1:
                return {"error": "ambiguous_lifecycle_action", "message": "the action verb maps to more than one next declared lifecycle value", "verb": natural_verb, "matches": mentioned}
            if len(mentioned) == 1:
                field, value = mentioned[0]
        if field is None:
            return {"status": "found", "table": table, "business_handle": {label_field: label_value}, "record": dict(row), "declared_lifecycles": surface.get("lifecycles", {}),
                    "resolution_receipt": {"request": req, "strategy": "unique_business_handle" if label_field in surface.get("labels", []) else "unique_readable_attribute", "candidate_limit": 3, "match_count": 1, "matched_field": label_field, "available_business_handle_fields": surface.get("labels", []), "available_resolution_fields": surface.get("resolvable", []), "returned_fields": sorted(row.keys()), "read_only": True, "mutation_applied": False},
                    "workflow_context": {"mutable_fields": surface.get("mutable", []), "declared_lifecycle_fields": sorted(surface.get("lifecycles", {}))}}
        before = row[field]
        lifecycle = surface.get('lifecycles', {}).get(field, [])
        if value is not None and lifecycle:
            canonical = next((item for item in lifecycle if str(item).lower() == str(value).lower()), None)
            if canonical is None:
                return {"error": "invalid_lifecycle_value", "message": "the requested value is outside the declared lifecycle", "field": field, "value": value, "allowed": lifecycle}
            value = canonical
            if _invalid_lifecycle_transition(lifecycle, before, value):
                return {"error": "lifecycle_violation", "message": "the requested transition is reverse or crosses terminal outcome branches", "field": field, "before": before, "value": value, "next_valid_values": _next_lifecycle_values(lifecycle, before)}
        if value is None:
            normalized = [_norm_status(item) for item in lifecycle]
            current = _norm_status(before)
            if current not in normalized:
                return {"error": "lifecycle_not_declared", "message": "the current value is not in a declared lifecycle", "field": field, "value": before, "allowed": lifecycle}
            choices = _next_lifecycle_values(lifecycle, before)
            if not choices:
                return {"status": "already_terminal", "table": table, "business_handle": {label_field: label_value}, "field": field, "value": before,
                        "resolution_receipt": {"request": req, "strategy": "unique_business_handle" if label_field in surface.get("labels", []) else "unique_readable_attribute", "match_count": 1, "matched_field": label_field},
                        "transition_receipt": {"declared_lifecycle": lifecycle, "before": before, "allowed_next_values": [], "mutation_applied": False, "reason": "terminal_state"}}
            if len(choices) > 1:
                # Production delegation requests often say both 'next'
                # and the concrete business outcome in a parenthetical
                # playbook (for example assigned -> in_progress ->
                # completed, or 'approve it'). Treat one uniquely named
                # branch as explicit intent; otherwise fail closed.
                action_norm = re.sub(r'[^a-z0-9]+', ' ', action.lower())
                aliases = {
                    'approved': ['approve'], 'declined': ['decline', 'reject'],
                    'completed': ['complete', 'finish'], 'cancelled': ['cancel'],
                    'succeeded': ['succeed'], 'failed': ['fail'],
                    'closed_won': ['won', 'win'], 'closed_lost': ['lost', 'lose'],
                }
                mentioned = []
                for choice in choices:
                    choice_norm = re.sub(r'[^a-z0-9]+', ' ', str(choice).lower()).strip()
                    terms = [choice_norm] + aliases.get(str(choice).lower(), [])
                    if any(re.search(r'(?<![a-z0-9])' + re.escape(term) + r'(?![a-z0-9])', action_norm) for term in terms if term):
                        mentioned.append(choice)
                if len(mentioned) != 1:
                    return {"error": "ambiguous_next_lifecycle", "message": "the next lifecycle stage branches; request an exact business outcome", "field": field, "before": before, "allowed": choices}
                value = mentioned[0]
            else:
                value = choices[0]
        if str(before) == str(value):
            return {"status": "already_current", "table": table, "business_handle": {label_field: label_value}, "field": field, "value": before,
                    "resolution_receipt": {"request": req, "strategy": "unique_business_handle" if label_field in surface.get("labels", []) else "unique_readable_attribute", "match_count": 1, "matched_field": label_field},
                    "transition_receipt": {"declared_lifecycle": lifecycle, "before": before, "after": value, "mutation_applied": False, "reason": "already_current"}}
        conn.execute('UPDATE ' + _qi(table) + ' SET ' + _qi(field) + ' = ? WHERE ' + _qi(surface['primary_key']) + ' = ?', (value, row[surface['primary_key']]))
        conn.commit()
        updated = conn.execute('SELECT * FROM ' + _qi(table) + ' WHERE ' + _qi(surface['primary_key']) + ' = ?', (row[surface['primary_key']],)).fetchone()
        return {"status": "updated", "table": table, "business_handle": {label_field: label_value}, "field": field, "before": before, "after": updated[field], "record": dict(updated),
                "resolution_receipt": {"request": req, "strategy": "unique_business_handle" if label_field in surface.get("labels", []) else "unique_readable_attribute", "candidate_limit": 3, "match_count": 1, "matched_field": label_field, "available_business_handle_fields": surface.get("labels", []), "available_resolution_fields": surface.get("resolvable", []), "returned_fields": sorted(updated.keys())},
                "transition_receipt": {"declared_lifecycle": lifecycle, "before": before, "after": updated[field], "mutation_applied": True, "changed_primary_key": row[surface["primary_key"]]},
                "policy_receipt": {"scope": "single_resolved_record", "mutable_fields": surface.get("mutable", []), "collateral_rows_changed": 0}}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_core_workflow_agent = core_workflow_agent
def _bf_friction_core_workflow_agent(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_core_workflow_agent(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "core_workflow_agent|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("b1e4baa134cb7067|" + _bf_sig).encode("utf-8")).hexdigest()
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
    return _bf_orig_core_workflow_agent(*_bf_args, **_bf_kwargs)
_bf_friction_core_workflow_agent.blobfish_original = _bf_orig_core_workflow_agent
core_workflow_agent = _bf_friction_core_workflow_agent

"""Department workflow sub-agent: resolve one business handle and apply one narrow field update from a free-text request."""
import json, re, sqlite3

_SURFACES = {"sales_leads":{"table":"sales_leads","primary_key":"id","labels":["lead_number","company_name","contact_name"],"readable":["id","lead_number","company_name","contact_name","source","estimated_value","owner_employee_id","created_at","status"],"resolvable":["lead_number","company_name","contact_name","source","estimated_value","owner_employee_id","created_at"],"mutable":["lead_number","company_name","contact_name","source","estimated_value","status"],"lifecycles":{"status":["new","contacted","qualified","converted","lost"]}},"sales_opportunities":{"table":"sales_opportunities","primary_key":"id","labels":["opportunity_number","title"],"readable":["id","opportunity_number","title","lead_id","amount","owner_employee_id","expected_close_date","business_unit_id","status"],"resolvable":["opportunity_number","title","lead_id","amount","owner_employee_id","expected_close_date","business_unit_id"],"mutable":["opportunity_number","title","amount","expected_close_date","status"],"lifecycles":{"status":["discovery","proposal","negotiation","closed_won","closed_lost"]}}}

def _qi(name):
    return '"' + str(name).replace('"', '""') + '"'

_OUTCOME_GROUPS = [["approved","rejected","denied","declined"],["completed","cancelled","canceled","failed"],["paid","failed"],["closed_won","closed_lost"],["accepted","rejected"],["hired","rejected"]]
def _norm_status(value):
    return str(value).strip().strip("'\"").lower()
def _outcome_group(values, candidate):
    available = {_norm_status(item) for item in values}
    target = _norm_status(candidate)
    candidates = [group for group in _OUTCOME_GROUPS if target in group and sum(1 for item in group if item in available) >= 2]
    return max(candidates, key=lambda group: sum(1 for item in group if item in available)) if candidates else None
def _next_lifecycle_values(values, current):
    normalized = [_norm_status(item) for item in values]
    target = _norm_status(current)
    if target not in normalized:
        return []
    index = normalized.index(target)
    current_branch = _outcome_group(values, values[index])
    successor_index = index + 1
    if current_branch:
        branch_indices = [i for i, item in enumerate(values) if _norm_status(item) in current_branch]
        if index != min(branch_indices):
            return []
        while successor_index < len(values) and _norm_status(values[successor_index]) in current_branch:
            successor_index += 1
    if successor_index >= len(values):
        return []
    candidate = values[successor_index]
    candidate_branch = _outcome_group(values, candidate)
    if not candidate_branch:
        return [candidate]
    branch_indices = [i for i, item in enumerate(values) if _norm_status(item) in candidate_branch]
    if min(branch_indices) <= index:
        return []
    return [item for item in values if _norm_status(item) in candidate_branch]
def _invalid_lifecycle_transition(values, before, after):
    normalized = [_norm_status(item) for item in values]
    current, target = _norm_status(before), _norm_status(after)
    if current not in normalized or target not in normalized:
        return True
    if current == target:
        return False
    return target not in [_norm_status(item) for item in _next_lifecycle_values(values, before)]
def _lifecycle_action_terms(value):
    normalized = re.sub(r'[^a-z0-9]+', '_', _norm_status(value)).strip('_')
    aliases = {
        'approved': ['approve'], 'declined': ['decline', 'reject'],
        'completed': ['complete', 'finish'], 'cancelled': ['cancel'],
        'succeeded': ['succeed'], 'failed': ['fail'],
        'closed_won': ['won', 'win'], 'closed_lost': ['lost', 'lose'],
        'reviewed': ['review'], 'verified': ['verify'], 'retained': ['retain'],
        'archived': ['archive'], 'published': ['publish'], 'packed': ['pack'],
        'shipped': ['ship'],
    }
    terms = [normalized, *aliases.get(normalized, [])]
    if normalized.endswith('ied') and len(normalized) > 3:
        terms.append(normalized[:-3] + 'y')
    elif normalized.endswith('ed') and len(normalized) > 2:
        terms.extend([normalized[:-2], normalized[:-1]])
    return list(dict.fromkeys(term for term in terms if term))

def _parse_request_target(req):
    table_match = re.search(r'(?:in\s+)?table\s+"?([A-Za-z_][A-Za-z0-9_]*)"?', req, re.I | re.S)
    if not table_match:
        return None
    table = table_match.group(1)
    surface = _SURFACES.get(table)
    tail = req[table_match.end():]
    generic_handle = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?business\s+(?:handle|label|key|identifier|reference|ref)\s+"([^"]+)"', tail, re.I | re.S)
    canonical = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+([A-Za-z_][A-Za-z0-9_]*)\s+"([^"]+)"', tail, re.I | re.S)
    descriptive = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+(?:with|by)\s+(?:(business\s+(?:handle|label|key|identifier|reference|ref))|([A-Za-z_][A-Za-z0-9_]*))\s+"([^"]+)"', tail, re.I | re.S)
    whose_alias = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+whose\s+(?:(?:[A-Za-z_][A-Za-z0-9_]*\s+or\s+)?business\s+(?:handle|label|key|identifier|reference|ref)|business\s+(?:handle|label|key|identifier|reference|ref)\s+or\s+[A-Za-z_][A-Za-z0-9_]*)\s+(?:(?:is|equals?|match(?:es)?)\s+|corresponds?(?:\s+to)?(?:\s+(?:the\s+)?[A-Za-z][A-Za-z0-9 _-]{0,60})?\s+)?"([^"]+)"', tail, re.I | re.S)
    whose = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+whose\s+(?:(business\s+(?:handle|label|key|identifier|reference|ref))|([A-Za-z_][A-Za-z0-9_]*))\s+(?:(?:is|equals?|match(?:es)?)\s+|corresponds?(?:\s+to)?(?:\s+(?:the\s+)?[A-Za-z][A-Za-z0-9 _-]{0,60})?\s+)?"([^"]+)"', tail, re.I | re.S)
    associated = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+associated\s+with\s+(?:(business\s+(?:handle|label|key|identifier|reference|ref))|([A-Za-z_][A-Za-z0-9_]*))\s+"([^"]+)"', tail, re.I | re.S)
    named = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+named\s+"([^"]+)"', tail, re.I | re.S)
    natural_for = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9 _-]{0,60}?\s+for\s+([A-Za-z][A-Za-z0-9 .\'-]{1,80}?)\s+(?=and\s+(?:return|show|read|retrieve|report|give|inspect|check)\b)', tail, re.I | re.S)
    if generic_handle:
        label_field = 'business_handle'
        label_value = generic_handle.group(1)
        action_start = table_match.end() + generic_handle.end()
    elif canonical:
        label_field, label_value = canonical.group(1), canonical.group(2)
        action_start = table_match.end() + canonical.end()
    elif descriptive:
        label_field = 'business_handle' if descriptive.group(1) else descriptive.group(2)
        label_value = descriptive.group(3)
        action_start = table_match.end() + descriptive.end()
    elif whose_alias:
        label_field = 'business_handle'
        label_value = whose_alias.group(1)
        action_start = table_match.end() + whose_alias.end()
    elif whose:
        label_field = 'business_handle' if whose.group(1) else whose.group(2)
        label_value = whose.group(3)
        action_start = table_match.end() + whose.end()
    elif associated:
        label_field = 'business_handle' if associated.group(1) else associated.group(2)
        label_value = associated.group(3)
        action_start = table_match.end() + associated.end()
    elif named:
        label_field = 'business_handle'
        label_value = named.group(1)
        action_start = table_match.end() + named.end()
    elif natural_for and surface is not None and len(surface['labels']) == 1:
        label_field = surface['labels'][0]
        label_value = natural_for.group(1).strip()
        action_start = table_match.end() + natural_for.end()
    else:
        return None
    if surface is not None and label_field not in surface['labels']:
        entity = table[:-3] + 'y' if table.endswith('ies') else (table[:-1] if table.endswith('s') else table)
        aliases = {'handle', 'business_handle', 'business_ref', 'record', 'item', 'case', entity.lower()}
        if str(label_field).lower() == 'id' and surface['primary_key'] in surface['labels']:
            label_field = surface['primary_key']
        elif str(label_field).lower() in aliases and len(surface['labels']) == 1:
            label_field = surface['labels'][0]
        elif str(label_field).lower() in aliases:
            label_field = '__business_handle__'
    return table, label_field, label_value, action_start
def _resolve_label_field(conn, table, surface, label_field, label_value):
    if label_field in surface['labels']:
        return label_field, None
    if label_field in surface.get('resolvable', []):
        rows = conn.execute('SELECT 1 FROM ' + _qi(table) + ' WHERE ' + _qi(label_field) + ' = ? LIMIT 3', (label_value,)).fetchall()
        if len(rows) == 1:
            return label_field, None
        if len(rows) == 0:
            return None, {'error': 'not_found', 'message': 'no record matched the exact resolution attribute', 'table': table, 'field': label_field, 'value': label_value}
        return None, {'error': 'ambiguous_match', 'message': 'resolution attribute matched multiple records', 'field': label_field, 'match_count': len(rows)}
    if label_field != '__business_handle__':
        return None, {'error': 'invalid_business_handle', 'message': 'use a declared business handle or exact non-lifecycle resolution field', 'allowed': surface['labels'], 'resolution_fields': surface.get('resolvable', [])}
    matches = []
    for candidate in surface['labels']:
        rows = conn.execute('SELECT 1 FROM ' + _qi(table) + ' WHERE ' + _qi(candidate) + ' = ? LIMIT 2', (label_value,)).fetchall()
        if len(rows) == 1:
            matches.append(candidate)
    if len(matches) == 1:
        return matches[0], None
    if len(matches) == 0:
        return None, {'error': 'not_found', 'message': 'no record matched the generic business handle', 'table': table, 'value': label_value}
    return None, {'error': 'ambiguous_match', 'message': 'business handle matched more than one declared field', 'fields': matches}

def sales_workflow_agent(db_path, request=None, **kwargs):
    if not request or not str(request).strip():
        return {"error": "validation_error", "message": "request is required"}
    req = str(request).strip()
    target = _parse_request_target(req)
    if target is None:
        return {"error": "request_not_understood", "message": "Use: in table <table>, find (or look up / locate / retrieve) <business_field> \"<value>\" and request one scoped update", "available_tables": sorted(_SURFACES)}
    table, label_field, label_value, action_start = target
    action = req[action_start:]
    exact = re.search(r'\band\s+(?:set|update|change|mark)\s+(?:(?:its|the)\s+)?([A-Za-z_][A-Za-z0-9_]*)(?:\s+(?:to|as)\s+|\s*=\s*)"([^"]*)"', action, re.I | re.S)
    set_next = re.search(r'\band\s+(?:set|update|change|mark)\s+(?:(?:its|the)\s+)?([A-Za-z_][A-Za-z0-9_]*)(?:\s+(?:to|as)\s+|\s*=\s*)(?:the\s+)?next\b', action, re.I | re.S)
    advance = re.search(r'\b(?:advance|move)\b(?=[\s\S]*\bnext\b)', action, re.I)
    advance_field = re.search(r'\b(?:advance|move)\s+(?:its\s+|the\s+)?([A-Za-z_][A-Za-z0-9_]*)\s+to\b', action, re.I)
    natural_transition = re.search(r'\band\s+([A-Za-z][A-Za-z0-9_-]{1,30})\s+(?:it|the\s+record|this\s+record)\b', action, re.I | re.S)
    read = re.search(r'\band\s+(?:return|show|read|retrieve|report|give|inspect|check)\b', action, re.I | re.S)
    natural_verb = None
    if exact:
        field, value = exact.groups()
    elif set_next:
        field, value = set_next.group(1), None
    elif advance:
        candidate = advance_field.group(1) if advance_field else 'status'
        field, value = ('status' if candidate.lower() in {'it', 'record', 'entry'} else candidate), None
    elif natural_transition:
        field, value = None, None
        natural_verb = natural_transition.group(1).lower()
    elif read:
        field, value = None, None
    else:
        return {"error": "request_not_understood", "message": "Request a record report, an exact field value, or the next declared lifecycle stage", "available_tables": sorted(_SURFACES)}
    surface = _SURFACES.get(table)
    if surface is None:
        return {"error": "out_of_scope", "message": "table is not owned by this department", "available_tables": sorted(_SURFACES)}
    if natural_verb is None and field is not None and field not in surface['mutable']:
        return {"error": "field_not_mutable", "message": "requested field is outside the delegated mutation surface", "allowed": surface["mutable"]}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        label_field, handle_error = _resolve_label_field(conn, table, surface, label_field, label_value)
        if handle_error is not None:
            return handle_error
        rows = conn.execute('SELECT * FROM ' + _qi(table) + ' WHERE ' + _qi(label_field) + ' = ? LIMIT 3', (label_value,)).fetchall()
        if len(rows) == 0:
            return {"error": "not_found", "message": "no record matched the business handle", "table": table, "field": label_field, "value": label_value}
        if len(rows) > 1:
            return {"error": "ambiguous_match", "message": "business handle matched multiple records", "match_count": len(rows)}
        row = rows[0]
        if natural_verb is not None:
            mentioned = []
            for lifecycle_field, lifecycle_values in surface.get('lifecycles', {}).items():
                for choice in _next_lifecycle_values(lifecycle_values, row[lifecycle_field]):
                    if natural_verb in _lifecycle_action_terms(choice):
                        mentioned.append((lifecycle_field, choice))
            if len(mentioned) == 0:
                fallback_values = {'review': 'reviewed', 'approve': 'approved', 'decline': 'declined', 'reject': 'rejected', 'close': 'closed', 'complete': 'completed', 'cancel': 'cancelled', 'archive': 'archived'}
                fallback_value = fallback_values.get(natural_verb)
                if fallback_value is not None and 'status' in surface['mutable'] and not surface.get('lifecycles', {}).get('status'):
                    field, value = 'status', fallback_value
                else:
                    return {"error": "unrecognized_lifecycle_action", "message": "the action verb does not name one next declared lifecycle value", "verb": natural_verb, "declared_lifecycles": surface.get("lifecycles", {})}
            if len(mentioned) > 1:
                return {"error": "ambiguous_lifecycle_action", "message": "the action verb maps to more than one next declared lifecycle value", "verb": natural_verb, "matches": mentioned}
            if len(mentioned) == 1:
                field, value = mentioned[0]
        if field is None:
            return {"status": "found", "table": table, "business_handle": {label_field: label_value}, "record": dict(row), "declared_lifecycles": surface.get("lifecycles", {}),
                    "resolution_receipt": {"request": req, "strategy": "unique_business_handle" if label_field in surface.get("labels", []) else "unique_readable_attribute", "candidate_limit": 3, "match_count": 1, "matched_field": label_field, "available_business_handle_fields": surface.get("labels", []), "available_resolution_fields": surface.get("resolvable", []), "returned_fields": sorted(row.keys()), "read_only": True, "mutation_applied": False},
                    "workflow_context": {"mutable_fields": surface.get("mutable", []), "declared_lifecycle_fields": sorted(surface.get("lifecycles", {}))}}
        before = row[field]
        lifecycle = surface.get('lifecycles', {}).get(field, [])
        if value is not None and lifecycle:
            canonical = next((item for item in lifecycle if str(item).lower() == str(value).lower()), None)
            if canonical is None:
                return {"error": "invalid_lifecycle_value", "message": "the requested value is outside the declared lifecycle", "field": field, "value": value, "allowed": lifecycle}
            value = canonical
            if _invalid_lifecycle_transition(lifecycle, before, value):
                return {"error": "lifecycle_violation", "message": "the requested transition is reverse or crosses terminal outcome branches", "field": field, "before": before, "value": value, "next_valid_values": _next_lifecycle_values(lifecycle, before)}
        if value is None:
            normalized = [_norm_status(item) for item in lifecycle]
            current = _norm_status(before)
            if current not in normalized:
                return {"error": "lifecycle_not_declared", "message": "the current value is not in a declared lifecycle", "field": field, "value": before, "allowed": lifecycle}
            choices = _next_lifecycle_values(lifecycle, before)
            if not choices:
                return {"status": "already_terminal", "table": table, "business_handle": {label_field: label_value}, "field": field, "value": before,
                        "resolution_receipt": {"request": req, "strategy": "unique_business_handle" if label_field in surface.get("labels", []) else "unique_readable_attribute", "match_count": 1, "matched_field": label_field},
                        "transition_receipt": {"declared_lifecycle": lifecycle, "before": before, "allowed_next_values": [], "mutation_applied": False, "reason": "terminal_state"}}
            if len(choices) > 1:
                # Production delegation requests often say both 'next'
                # and the concrete business outcome in a parenthetical
                # playbook (for example assigned -> in_progress ->
                # completed, or 'approve it'). Treat one uniquely named
                # branch as explicit intent; otherwise fail closed.
                action_norm = re.sub(r'[^a-z0-9]+', ' ', action.lower())
                aliases = {
                    'approved': ['approve'], 'declined': ['decline', 'reject'],
                    'completed': ['complete', 'finish'], 'cancelled': ['cancel'],
                    'succeeded': ['succeed'], 'failed': ['fail'],
                    'closed_won': ['won', 'win'], 'closed_lost': ['lost', 'lose'],
                }
                mentioned = []
                for choice in choices:
                    choice_norm = re.sub(r'[^a-z0-9]+', ' ', str(choice).lower()).strip()
                    terms = [choice_norm] + aliases.get(str(choice).lower(), [])
                    if any(re.search(r'(?<![a-z0-9])' + re.escape(term) + r'(?![a-z0-9])', action_norm) for term in terms if term):
                        mentioned.append(choice)
                if len(mentioned) != 1:
                    return {"error": "ambiguous_next_lifecycle", "message": "the next lifecycle stage branches; request an exact business outcome", "field": field, "before": before, "allowed": choices}
                value = mentioned[0]
            else:
                value = choices[0]
        if str(before) == str(value):
            return {"status": "already_current", "table": table, "business_handle": {label_field: label_value}, "field": field, "value": before,
                    "resolution_receipt": {"request": req, "strategy": "unique_business_handle" if label_field in surface.get("labels", []) else "unique_readable_attribute", "match_count": 1, "matched_field": label_field},
                    "transition_receipt": {"declared_lifecycle": lifecycle, "before": before, "after": value, "mutation_applied": False, "reason": "already_current"}}
        conn.execute('UPDATE ' + _qi(table) + ' SET ' + _qi(field) + ' = ? WHERE ' + _qi(surface['primary_key']) + ' = ?', (value, row[surface['primary_key']]))
        conn.commit()
        updated = conn.execute('SELECT * FROM ' + _qi(table) + ' WHERE ' + _qi(surface['primary_key']) + ' = ?', (row[surface['primary_key']],)).fetchone()
        return {"status": "updated", "table": table, "business_handle": {label_field: label_value}, "field": field, "before": before, "after": updated[field], "record": dict(updated),
                "resolution_receipt": {"request": req, "strategy": "unique_business_handle" if label_field in surface.get("labels", []) else "unique_readable_attribute", "candidate_limit": 3, "match_count": 1, "matched_field": label_field, "available_business_handle_fields": surface.get("labels", []), "available_resolution_fields": surface.get("resolvable", []), "returned_fields": sorted(updated.keys())},
                "transition_receipt": {"declared_lifecycle": lifecycle, "before": before, "after": updated[field], "mutation_applied": True, "changed_primary_key": row[surface["primary_key"]]},
                "policy_receipt": {"scope": "single_resolved_record", "mutable_fields": surface.get("mutable", []), "collateral_rows_changed": 0}}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_sales_workflow_agent = sales_workflow_agent
def _bf_friction_sales_workflow_agent(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_sales_workflow_agent(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "sales_workflow_agent|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("b1e4baa134cb7067|" + _bf_sig).encode("utf-8")).hexdigest()
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
    return _bf_orig_sales_workflow_agent(*_bf_args, **_bf_kwargs)
_bf_friction_sales_workflow_agent.blobfish_original = _bf_orig_sales_workflow_agent
sales_workflow_agent = _bf_friction_sales_workflow_agent

"""Department workflow sub-agent: resolve one business handle and apply one narrow field update from a free-text request."""
import json, re, sqlite3

_SURFACES = {"sourcing_vendors":{"table":"sourcing_vendors","primary_key":"id","labels":["vendor_number","name","contact_name"],"readable":["id","vendor_number","name","category","contact_name","owner_employee_id","onboarded_at","status"],"resolvable":["vendor_number","name","category","contact_name","owner_employee_id","onboarded_at"],"mutable":["vendor_number","name","category","contact_name","onboarded_at","status"],"lifecycles":{"status":["prospective","under_review","approved","suspended"]}},"sourcing_purchase_orders":{"table":"sourcing_purchase_orders","primary_key":"id","labels":["po_number"],"readable":["id","po_number","vendor_id","requested_by_employee_id","amount","ordered_at","approver_employee_id","status"],"resolvable":["po_number","vendor_id","requested_by_employee_id","amount","ordered_at","approver_employee_id"],"mutable":["po_number","amount","ordered_at","status"],"lifecycles":{"status":["draft","submitted","approved","received","closed"]}}}

def _qi(name):
    return '"' + str(name).replace('"', '""') + '"'

_OUTCOME_GROUPS = [["approved","rejected","denied","declined"],["completed","cancelled","canceled","failed"],["paid","failed"],["closed_won","closed_lost"],["accepted","rejected"],["hired","rejected"]]
def _norm_status(value):
    return str(value).strip().strip("'\"").lower()
def _outcome_group(values, candidate):
    available = {_norm_status(item) for item in values}
    target = _norm_status(candidate)
    candidates = [group for group in _OUTCOME_GROUPS if target in group and sum(1 for item in group if item in available) >= 2]
    return max(candidates, key=lambda group: sum(1 for item in group if item in available)) if candidates else None
def _next_lifecycle_values(values, current):
    normalized = [_norm_status(item) for item in values]
    target = _norm_status(current)
    if target not in normalized:
        return []
    index = normalized.index(target)
    current_branch = _outcome_group(values, values[index])
    successor_index = index + 1
    if current_branch:
        branch_indices = [i for i, item in enumerate(values) if _norm_status(item) in current_branch]
        if index != min(branch_indices):
            return []
        while successor_index < len(values) and _norm_status(values[successor_index]) in current_branch:
            successor_index += 1
    if successor_index >= len(values):
        return []
    candidate = values[successor_index]
    candidate_branch = _outcome_group(values, candidate)
    if not candidate_branch:
        return [candidate]
    branch_indices = [i for i, item in enumerate(values) if _norm_status(item) in candidate_branch]
    if min(branch_indices) <= index:
        return []
    return [item for item in values if _norm_status(item) in candidate_branch]
def _invalid_lifecycle_transition(values, before, after):
    normalized = [_norm_status(item) for item in values]
    current, target = _norm_status(before), _norm_status(after)
    if current not in normalized or target not in normalized:
        return True
    if current == target:
        return False
    return target not in [_norm_status(item) for item in _next_lifecycle_values(values, before)]
def _lifecycle_action_terms(value):
    normalized = re.sub(r'[^a-z0-9]+', '_', _norm_status(value)).strip('_')
    aliases = {
        'approved': ['approve'], 'declined': ['decline', 'reject'],
        'completed': ['complete', 'finish'], 'cancelled': ['cancel'],
        'succeeded': ['succeed'], 'failed': ['fail'],
        'closed_won': ['won', 'win'], 'closed_lost': ['lost', 'lose'],
        'reviewed': ['review'], 'verified': ['verify'], 'retained': ['retain'],
        'archived': ['archive'], 'published': ['publish'], 'packed': ['pack'],
        'shipped': ['ship'],
    }
    terms = [normalized, *aliases.get(normalized, [])]
    if normalized.endswith('ied') and len(normalized) > 3:
        terms.append(normalized[:-3] + 'y')
    elif normalized.endswith('ed') and len(normalized) > 2:
        terms.extend([normalized[:-2], normalized[:-1]])
    return list(dict.fromkeys(term for term in terms if term))

def _parse_request_target(req):
    table_match = re.search(r'(?:in\s+)?table\s+"?([A-Za-z_][A-Za-z0-9_]*)"?', req, re.I | re.S)
    if not table_match:
        return None
    table = table_match.group(1)
    surface = _SURFACES.get(table)
    tail = req[table_match.end():]
    generic_handle = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?business\s+(?:handle|label|key|identifier|reference|ref)\s+"([^"]+)"', tail, re.I | re.S)
    canonical = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+([A-Za-z_][A-Za-z0-9_]*)\s+"([^"]+)"', tail, re.I | re.S)
    descriptive = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+(?:with|by)\s+(?:(business\s+(?:handle|label|key|identifier|reference|ref))|([A-Za-z_][A-Za-z0-9_]*))\s+"([^"]+)"', tail, re.I | re.S)
    whose_alias = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+whose\s+(?:(?:[A-Za-z_][A-Za-z0-9_]*\s+or\s+)?business\s+(?:handle|label|key|identifier|reference|ref)|business\s+(?:handle|label|key|identifier|reference|ref)\s+or\s+[A-Za-z_][A-Za-z0-9_]*)\s+(?:(?:is|equals?|match(?:es)?)\s+|corresponds?(?:\s+to)?(?:\s+(?:the\s+)?[A-Za-z][A-Za-z0-9 _-]{0,60})?\s+)?"([^"]+)"', tail, re.I | re.S)
    whose = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+whose\s+(?:(business\s+(?:handle|label|key|identifier|reference|ref))|([A-Za-z_][A-Za-z0-9_]*))\s+(?:(?:is|equals?|match(?:es)?)\s+|corresponds?(?:\s+to)?(?:\s+(?:the\s+)?[A-Za-z][A-Za-z0-9 _-]{0,60})?\s+)?"([^"]+)"', tail, re.I | re.S)
    associated = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+associated\s+with\s+(?:(business\s+(?:handle|label|key|identifier|reference|ref))|([A-Za-z_][A-Za-z0-9_]*))\s+"([^"]+)"', tail, re.I | re.S)
    named = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,3}\s+named\s+"([^"]+)"', tail, re.I | re.S)
    natural_for = re.search(r'\b(?:find|locate|look\s+up|search\s+for|retrieve|fetch|get|pull\s+up|identify|select|open)\s+(?:the\s+)?[A-Za-z][A-Za-z0-9 _-]{0,60}?\s+for\s+([A-Za-z][A-Za-z0-9 .\'-]{1,80}?)\s+(?=and\s+(?:return|show|read|retrieve|report|give|inspect|check)\b)', tail, re.I | re.S)
    if generic_handle:
        label_field = 'business_handle'
        label_value = generic_handle.group(1)
        action_start = table_match.end() + generic_handle.end()
    elif canonical:
        label_field, label_value = canonical.group(1), canonical.group(2)
        action_start = table_match.end() + canonical.end()
    elif descriptive:
        label_field = 'business_handle' if descriptive.group(1) else descriptive.group(2)
        label_value = descriptive.group(3)
        action_start = table_match.end() + descriptive.end()
    elif whose_alias:
        label_field = 'business_handle'
        label_value = whose_alias.group(1)
        action_start = table_match.end() + whose_alias.end()
    elif whose:
        label_field = 'business_handle' if whose.group(1) else whose.group(2)
        label_value = whose.group(3)
        action_start = table_match.end() + whose.end()
    elif associated:
        label_field = 'business_handle' if associated.group(1) else associated.group(2)
        label_value = associated.group(3)
        action_start = table_match.end() + associated.end()
    elif named:
        label_field = 'business_handle'
        label_value = named.group(1)
        action_start = table_match.end() + named.end()
    elif natural_for and surface is not None and len(surface['labels']) == 1:
        label_field = surface['labels'][0]
        label_value = natural_for.group(1).strip()
        action_start = table_match.end() + natural_for.end()
    else:
        return None
    if surface is not None and label_field not in surface['labels']:
        entity = table[:-3] + 'y' if table.endswith('ies') else (table[:-1] if table.endswith('s') else table)
        aliases = {'handle', 'business_handle', 'business_ref', 'record', 'item', 'case', entity.lower()}
        if str(label_field).lower() == 'id' and surface['primary_key'] in surface['labels']:
            label_field = surface['primary_key']
        elif str(label_field).lower() in aliases and len(surface['labels']) == 1:
            label_field = surface['labels'][0]
        elif str(label_field).lower() in aliases:
            label_field = '__business_handle__'
    return table, label_field, label_value, action_start
def _resolve_label_field(conn, table, surface, label_field, label_value):
    if label_field in surface['labels']:
        return label_field, None
    if label_field in surface.get('resolvable', []):
        rows = conn.execute('SELECT 1 FROM ' + _qi(table) + ' WHERE ' + _qi(label_field) + ' = ? LIMIT 3', (label_value,)).fetchall()
        if len(rows) == 1:
            return label_field, None
        if len(rows) == 0:
            return None, {'error': 'not_found', 'message': 'no record matched the exact resolution attribute', 'table': table, 'field': label_field, 'value': label_value}
        return None, {'error': 'ambiguous_match', 'message': 'resolution attribute matched multiple records', 'field': label_field, 'match_count': len(rows)}
    if label_field != '__business_handle__':
        return None, {'error': 'invalid_business_handle', 'message': 'use a declared business handle or exact non-lifecycle resolution field', 'allowed': surface['labels'], 'resolution_fields': surface.get('resolvable', [])}
    matches = []
    for candidate in surface['labels']:
        rows = conn.execute('SELECT 1 FROM ' + _qi(table) + ' WHERE ' + _qi(candidate) + ' = ? LIMIT 2', (label_value,)).fetchall()
        if len(rows) == 1:
            matches.append(candidate)
    if len(matches) == 1:
        return matches[0], None
    if len(matches) == 0:
        return None, {'error': 'not_found', 'message': 'no record matched the generic business handle', 'table': table, 'value': label_value}
    return None, {'error': 'ambiguous_match', 'message': 'business handle matched more than one declared field', 'fields': matches}

def sourcing_workflow_agent(db_path, request=None, **kwargs):
    if not request or not str(request).strip():
        return {"error": "validation_error", "message": "request is required"}
    req = str(request).strip()
    target = _parse_request_target(req)
    if target is None:
        return {"error": "request_not_understood", "message": "Use: in table <table>, find (or look up / locate / retrieve) <business_field> \"<value>\" and request one scoped update", "available_tables": sorted(_SURFACES)}
    table, label_field, label_value, action_start = target
    action = req[action_start:]
    exact = re.search(r'\band\s+(?:set|update|change|mark)\s+(?:(?:its|the)\s+)?([A-Za-z_][A-Za-z0-9_]*)(?:\s+(?:to|as)\s+|\s*=\s*)"([^"]*)"', action, re.I | re.S)
    set_next = re.search(r'\band\s+(?:set|update|change|mark)\s+(?:(?:its|the)\s+)?([A-Za-z_][A-Za-z0-9_]*)(?:\s+(?:to|as)\s+|\s*=\s*)(?:the\s+)?next\b', action, re.I | re.S)
    advance = re.search(r'\b(?:advance|move)\b(?=[\s\S]*\bnext\b)', action, re.I)
    advance_field = re.search(r'\b(?:advance|move)\s+(?:its\s+|the\s+)?([A-Za-z_][A-Za-z0-9_]*)\s+to\b', action, re.I)
    natural_transition = re.search(r'\band\s+([A-Za-z][A-Za-z0-9_-]{1,30})\s+(?:it|the\s+record|this\s+record)\b', action, re.I | re.S)
    read = re.search(r'\band\s+(?:return|show|read|retrieve|report|give|inspect|check)\b', action, re.I | re.S)
    natural_verb = None
    if exact:
        field, value = exact.groups()
    elif set_next:
        field, value = set_next.group(1), None
    elif advance:
        candidate = advance_field.group(1) if advance_field else 'status'
        field, value = ('status' if candidate.lower() in {'it', 'record', 'entry'} else candidate), None
    elif natural_transition:
        field, value = None, None
        natural_verb = natural_transition.group(1).lower()
    elif read:
        field, value = None, None
    else:
        return {"error": "request_not_understood", "message": "Request a record report, an exact field value, or the next declared lifecycle stage", "available_tables": sorted(_SURFACES)}
    surface = _SURFACES.get(table)
    if surface is None:
        return {"error": "out_of_scope", "message": "table is not owned by this department", "available_tables": sorted(_SURFACES)}
    if natural_verb is None and field is not None and field not in surface['mutable']:
        return {"error": "field_not_mutable", "message": "requested field is outside the delegated mutation surface", "allowed": surface["mutable"]}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        label_field, handle_error = _resolve_label_field(conn, table, surface, label_field, label_value)
        if handle_error is not None:
            return handle_error
        rows = conn.execute('SELECT * FROM ' + _qi(table) + ' WHERE ' + _qi(label_field) + ' = ? LIMIT 3', (label_value,)).fetchall()
        if len(rows) == 0:
            return {"error": "not_found", "message": "no record matched the business handle", "table": table, "field": label_field, "value": label_value}
        if len(rows) > 1:
            return {"error": "ambiguous_match", "message": "business handle matched multiple records", "match_count": len(rows)}
        row = rows[0]
        if natural_verb is not None:
            mentioned = []
            for lifecycle_field, lifecycle_values in surface.get('lifecycles', {}).items():
                for choice in _next_lifecycle_values(lifecycle_values, row[lifecycle_field]):
                    if natural_verb in _lifecycle_action_terms(choice):
                        mentioned.append((lifecycle_field, choice))
            if len(mentioned) == 0:
                fallback_values = {'review': 'reviewed', 'approve': 'approved', 'decline': 'declined', 'reject': 'rejected', 'close': 'closed', 'complete': 'completed', 'cancel': 'cancelled', 'archive': 'archived'}
                fallback_value = fallback_values.get(natural_verb)
                if fallback_value is not None and 'status' in surface['mutable'] and not surface.get('lifecycles', {}).get('status'):
                    field, value = 'status', fallback_value
                else:
                    return {"error": "unrecognized_lifecycle_action", "message": "the action verb does not name one next declared lifecycle value", "verb": natural_verb, "declared_lifecycles": surface.get("lifecycles", {})}
            if len(mentioned) > 1:
                return {"error": "ambiguous_lifecycle_action", "message": "the action verb maps to more than one next declared lifecycle value", "verb": natural_verb, "matches": mentioned}
            if len(mentioned) == 1:
                field, value = mentioned[0]
        if field is None:
            return {"status": "found", "table": table, "business_handle": {label_field: label_value}, "record": dict(row), "declared_lifecycles": surface.get("lifecycles", {}),
                    "resolution_receipt": {"request": req, "strategy": "unique_business_handle" if label_field in surface.get("labels", []) else "unique_readable_attribute", "candidate_limit": 3, "match_count": 1, "matched_field": label_field, "available_business_handle_fields": surface.get("labels", []), "available_resolution_fields": surface.get("resolvable", []), "returned_fields": sorted(row.keys()), "read_only": True, "mutation_applied": False},
                    "workflow_context": {"mutable_fields": surface.get("mutable", []), "declared_lifecycle_fields": sorted(surface.get("lifecycles", {}))}}
        before = row[field]
        lifecycle = surface.get('lifecycles', {}).get(field, [])
        if value is not None and lifecycle:
            canonical = next((item for item in lifecycle if str(item).lower() == str(value).lower()), None)
            if canonical is None:
                return {"error": "invalid_lifecycle_value", "message": "the requested value is outside the declared lifecycle", "field": field, "value": value, "allowed": lifecycle}
            value = canonical
            if _invalid_lifecycle_transition(lifecycle, before, value):
                return {"error": "lifecycle_violation", "message": "the requested transition is reverse or crosses terminal outcome branches", "field": field, "before": before, "value": value, "next_valid_values": _next_lifecycle_values(lifecycle, before)}
        if value is None:
            normalized = [_norm_status(item) for item in lifecycle]
            current = _norm_status(before)
            if current not in normalized:
                return {"error": "lifecycle_not_declared", "message": "the current value is not in a declared lifecycle", "field": field, "value": before, "allowed": lifecycle}
            choices = _next_lifecycle_values(lifecycle, before)
            if not choices:
                return {"status": "already_terminal", "table": table, "business_handle": {label_field: label_value}, "field": field, "value": before,
                        "resolution_receipt": {"request": req, "strategy": "unique_business_handle" if label_field in surface.get("labels", []) else "unique_readable_attribute", "match_count": 1, "matched_field": label_field},
                        "transition_receipt": {"declared_lifecycle": lifecycle, "before": before, "allowed_next_values": [], "mutation_applied": False, "reason": "terminal_state"}}
            if len(choices) > 1:
                # Production delegation requests often say both 'next'
                # and the concrete business outcome in a parenthetical
                # playbook (for example assigned -> in_progress ->
                # completed, or 'approve it'). Treat one uniquely named
                # branch as explicit intent; otherwise fail closed.
                action_norm = re.sub(r'[^a-z0-9]+', ' ', action.lower())
                aliases = {
                    'approved': ['approve'], 'declined': ['decline', 'reject'],
                    'completed': ['complete', 'finish'], 'cancelled': ['cancel'],
                    'succeeded': ['succeed'], 'failed': ['fail'],
                    'closed_won': ['won', 'win'], 'closed_lost': ['lost', 'lose'],
                }
                mentioned = []
                for choice in choices:
                    choice_norm = re.sub(r'[^a-z0-9]+', ' ', str(choice).lower()).strip()
                    terms = [choice_norm] + aliases.get(str(choice).lower(), [])
                    if any(re.search(r'(?<![a-z0-9])' + re.escape(term) + r'(?![a-z0-9])', action_norm) for term in terms if term):
                        mentioned.append(choice)
                if len(mentioned) != 1:
                    return {"error": "ambiguous_next_lifecycle", "message": "the next lifecycle stage branches; request an exact business outcome", "field": field, "before": before, "allowed": choices}
                value = mentioned[0]
            else:
                value = choices[0]
        if str(before) == str(value):
            return {"status": "already_current", "table": table, "business_handle": {label_field: label_value}, "field": field, "value": before,
                    "resolution_receipt": {"request": req, "strategy": "unique_business_handle" if label_field in surface.get("labels", []) else "unique_readable_attribute", "match_count": 1, "matched_field": label_field},
                    "transition_receipt": {"declared_lifecycle": lifecycle, "before": before, "after": value, "mutation_applied": False, "reason": "already_current"}}
        conn.execute('UPDATE ' + _qi(table) + ' SET ' + _qi(field) + ' = ? WHERE ' + _qi(surface['primary_key']) + ' = ?', (value, row[surface['primary_key']]))
        conn.commit()
        updated = conn.execute('SELECT * FROM ' + _qi(table) + ' WHERE ' + _qi(surface['primary_key']) + ' = ?', (row[surface['primary_key']],)).fetchone()
        return {"status": "updated", "table": table, "business_handle": {label_field: label_value}, "field": field, "before": before, "after": updated[field], "record": dict(updated),
                "resolution_receipt": {"request": req, "strategy": "unique_business_handle" if label_field in surface.get("labels", []) else "unique_readable_attribute", "candidate_limit": 3, "match_count": 1, "matched_field": label_field, "available_business_handle_fields": surface.get("labels", []), "available_resolution_fields": surface.get("resolvable", []), "returned_fields": sorted(updated.keys())},
                "transition_receipt": {"declared_lifecycle": lifecycle, "before": before, "after": updated[field], "mutation_applied": True, "changed_primary_key": row[surface["primary_key"]]},
                "policy_receipt": {"scope": "single_resolved_record", "mutable_fields": surface.get("mutable", []), "collateral_rows_changed": 0}}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_sourcing_workflow_agent = sourcing_workflow_agent
def _bf_friction_sourcing_workflow_agent(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_sourcing_workflow_agent(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "sourcing_workflow_agent|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("b1e4baa134cb7067|" + _bf_sig).encode("utf-8")).hexdigest()
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
    return _bf_orig_sourcing_workflow_agent(*_bf_args, **_bf_kwargs)
_bf_friction_sourcing_workflow_agent.blobfish_original = _bf_orig_sourcing_workflow_agent
sourcing_workflow_agent = _bf_friction_sourcing_workflow_agent

import sqlite3

def create_lead(db_path, company, contactname, segment, status, interestproductid):
    """Create lead record"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO lead (company, contactname, segment, status, interestproductid) VALUES (?, ?, ?, ?, ?)", (company, contactname, segment, status, interestproductid,))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return {"id": row_id}

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_create_lead = create_lead
def _bf_friction_create_lead(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_create_lead(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "create_lead|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("b1e4baa134cb7067|" + _bf_sig).encode("utf-8")).hexdigest()
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
    return _bf_orig_create_lead(*_bf_args, **_bf_kwargs)
_bf_friction_create_lead.blobfish_original = _bf_orig_create_lead
create_lead = _bf_friction_create_lead

import sqlite3

def update_status_lead(db_path, id, status):
    """Update lead status"""
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("UPDATE lead SET status = ? WHERE id = ?", (status, id))
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    if updated == 0:
        return {"error": "not found"}
    return {"updated": updated}

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_update_status_lead = update_status_lead
def _bf_friction_update_status_lead(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_update_status_lead(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "update_status_lead|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("b1e4baa134cb7067|" + _bf_sig).encode("utf-8")).hexdigest()
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
    return _bf_orig_update_status_lead(*_bf_args, **_bf_kwargs)
_bf_friction_update_status_lead.blobfish_original = _bf_orig_update_status_lead
update_status_lead = _bf_friction_update_status_lead

import sqlite3

def create_account(db_path, name, segment, region, tier, newclient):
    """Create account record"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO account (name, segment, region, tier, newclient) VALUES (?, ?, ?, ?, ?)", (name, segment, region, tier, newclient,))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return {"id": row_id}

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_create_account = create_account
def _bf_friction_create_account(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_create_account(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "create_account|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("b1e4baa134cb7067|" + _bf_sig).encode("utf-8")).hexdigest()
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
    return _bf_orig_create_account(*_bf_args, **_bf_kwargs)
_bf_friction_create_account.blobfish_original = _bf_orig_create_account
create_account = _bf_friction_create_account

import sqlite3

def update_status_account(db_path, id, status):
    """Update account status"""
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("UPDATE account SET status = ? WHERE id = ?", (status, id))
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    if updated == 0:
        return {"error": "not found"}
    return {"updated": updated}

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_update_status_account = update_status_account
def _bf_friction_update_status_account(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_update_status_account(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "update_status_account|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("b1e4baa134cb7067|" + _bf_sig).encode("utf-8")).hexdigest()
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
    return _bf_orig_update_status_account(*_bf_args, **_bf_kwargs)
_bf_friction_update_status_account.blobfish_original = _bf_orig_update_status_account
update_status_account = _bf_friction_update_status_account

import sqlite3

def create_opportunity(db_path, accountid, stage, amount, products, status):
    """Create opportunity record"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO opportunity (accountid, stage, amount, products, status) VALUES (?, ?, ?, ?, ?)", (accountid, stage, amount, products, status,))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return {"id": row_id}

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_create_opportunity = create_opportunity
def _bf_friction_create_opportunity(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_create_opportunity(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "create_opportunity|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("b1e4baa134cb7067|" + _bf_sig).encode("utf-8")).hexdigest()
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
    return _bf_orig_create_opportunity(*_bf_args, **_bf_kwargs)
_bf_friction_create_opportunity.blobfish_original = _bf_orig_create_opportunity
create_opportunity = _bf_friction_create_opportunity

import sqlite3

def update_status_opportunity(db_path, id, status):
    """Update opportunity status"""
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("UPDATE opportunity SET status = ? WHERE id = ?", (status, id))
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    if updated == 0:
        return {"error": "not found"}
    return {"updated": updated}

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_update_status_opportunity = update_status_opportunity
def _bf_friction_update_status_opportunity(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_update_status_opportunity(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "update_status_opportunity|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("b1e4baa134cb7067|" + _bf_sig).encode("utf-8")).hexdigest()
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
    return _bf_orig_update_status_opportunity(*_bf_args, **_bf_kwargs)
_bf_friction_update_status_opportunity.blobfish_original = _bf_orig_update_status_opportunity
update_status_opportunity = _bf_friction_update_status_opportunity

"""Update sales_leads status with validation"""
import sqlite3

def update_sales_leads_status(db_path: str, id: int, new_status: str) -> dict:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM "sales_leads" WHERE "id" = ?', [id]).fetchone()
    if not row:
        conn.close()
        return {"error": f"sales leads {id} not found"}
    valid = ["new", "contacted", "qualified", "converted", "lost"]
    if valid and new_status not in valid:
        conn.close()
        return {"error": f"Invalid status '{new_status}'. Valid: {valid}"}
    old_status = row['status']
    conn.execute('UPDATE "sales_leads" SET "status" = ? WHERE "id" = ?', [new_status, id])
    conn.commit()
    conn.close()
    return {"updated": True, "id": id, "table": "sales_leads", "old_status": old_status, "new_status": new_status}

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_update_sales_leads_status = update_sales_leads_status
def _bf_friction_update_sales_leads_status(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_update_sales_leads_status(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "update_sales_leads_status|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    _bf_digest = _bf_hashlib.sha256(("b1e4baa134cb7067|" + _bf_sig).encode("utf-8")).hexdigest()
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
    return _bf_orig_update_sales_leads_status(*_bf_args, **_bf_kwargs)
_bf_friction_update_sales_leads_status.blobfish_original = _bf_orig_update_sales_leads_status
update_sales_leads_status = _bf_friction_update_sales_leads_status

