"""Department workflow sub-agent: resolve one business handle and apply one narrow field update from a free-text request."""
import json, re, sqlite3

_SURFACES = {"lead_management_sop":{"table":"lead_management_sop","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"lead_scoring_policy":{"table":"lead_scoring_policy","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"account_tiering_standard":{"table":"account_tiering_standard","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"opportunity_stage_gates":{"table":"opportunity_stage_gates","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"cpq_discount_policy":{"table":"cpq_discount_policy","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"deal_desk_charter":{"table":"deal_desk_charter","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"compliance_review_checklist":{"table":"compliance_review_checklist","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"finance_approval_thresholds":{"table":"finance_approval_thresholds","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"order_activation_runbook":{"table":"order_activation_runbook","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"case_management_sla":{"table":"case_management_sla","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"activity_logging_standards":{"table":"activity_logging_standards","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"forecast_methodology":{"table":"forecast_methodology","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"renewal_playbook":{"table":"renewal_playbook","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"territory":{"table":"territory","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"data_quality_rules":{"table":"data_quality_rules","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"sequence_design_rules":{"table":"sequence_design_rules","primary_key":"id","labels":["email"],"readable":["id","maximum","account_tiering_standard_id","standard","emails","email","calls","one","status","created_at"],"resolvable":["maximum","account_tiering_standard_id","standard","emails","email","calls","one","status","created_at"],"mutable":["maximum","standard","emails","email","calls","one","status"],"lifecycles":{}},"snippets":{"table":"snippets","primary_key":"id","labels":["ref"],"readable":["id","ftr","obj","ref","noshow","status","created_at"],"resolvable":["ftr","obj","ref","noshow","status","created_at"],"mutable":["ftr","obj","ref","noshow","status"],"lifecycles":{}},"conversation_intelligence_standards":{"table":"conversation_intelligence_standards","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"disposition_codes":{"table":"disposition_codes","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"meddic_scorecard":{"table":"meddic_scorecard","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"talk_ratio":{"table":"talk_ratio","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"tracker_keywords":{"table":"tracker_keywords","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"snippets_and_retention":{"table":"snippets_and_retention","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"coaching_cadence":{"table":"coaching_cadence","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"meeting_scheduling_sla":{"table":"meeting_scheduling_sla","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"meeting_types_and_durations":{"table":"meeting_types_and_durations","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"handoff_to_ae":{"table":"handoff_to_ae","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"accept_all":{"table":"accept_all","primary_key":"id","labels":["capped_at_1_email_week_contact"],"readable":["id","sequence_design_rules_id","sequence_eligible","capped_at_1_email_week_contact","status","created_at"],"resolvable":["sequence_design_rules_id","sequence_eligible","capped_at_1_email_week_contact","status","created_at"],"mutable":["sequence_eligible","capped_at_1_email_week_contact","status"],"lifecycles":{}},"risky":{"table":"risky","primary_key":"id","labels":["excluded_from_email_steps"],"readable":["id","excluded_from_email_steps","risk_notes_csm_post_call_id","call_and_linked_in_steps_only","monthly_timeline_business_days_id","re_verify_after_30_days","status","created_at"],"resolvable":["excluded_from_email_steps","risk_notes_csm_post_call_id","call_and_linked_in_steps_only","monthly_timeline_business_days_id","re_verify_after_30_days","status","created_at"],"mutable":["excluded_from_email_steps","call_and_linked_in_steps_only","re_verify_after_30_days","status"],"lifecycles":{}},"inbound_routing_matrix":{"table":"inbound_routing_matrix","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"visitor_identification":{"table":"visitor_identification","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"web_form_definitions":{"table":"web_form_definitions","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"routing_decision_table":{"table":"routing_decision_table","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"suppression_and_kpis":{"table":"suppression_and_kpis","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"mql_definition":{"table":"mql_definition","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"sal_gate":{"table":"sal_gate","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"attribution":{"table":"attribution","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"fy2026_list_prices":{"table":"fy2026_list_prices","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"volume_bands":{"table":"volume_bands","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}},"currency_handling":{"table":"currency_handling","primary_key":"id","labels":["name"],"readable":["id","name","status","created_at"],"resolvable":["name","created_at"],"mutable":["name","status"],"lifecycles":{"status":["active","inactive","pending"]}}}

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
    return _bf_orig_core_workflow_agent(*_bf_args, **_bf_kwargs)
_bf_friction_core_workflow_agent.blobfish_original = _bf_orig_core_workflow_agent
core_workflow_agent = _bf_friction_core_workflow_agent
