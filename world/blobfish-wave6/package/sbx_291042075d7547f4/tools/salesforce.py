"""Executable SALESFORCE tool module

Inspect each function: SQLite helpers are local fixtures; network-backed functions call their declared endpoint.
Tools: core_records_agent, marketing_records_agent, sales_records_agent, sourcing_records_agent, accounts_list, contacts_list, account_get, contact_get, opportunity_get, get_accounts_account_capabilities, get_customers_customer_bank_accounts, get_contactdb_segments_segment_id, get_mc_contacts_exports_id, query_sales_leads, lookup_sales_lead_with_employees, lookup_sales_opportunity_with_sales_leads, core_workflow_agent, marketing_workflow_agent, sales_workflow_agent, sourcing_workflow_agent, account_create, contact_create, opportunity_create, post_account_links, post_account_sessions, post_marketing_contacts_batch, update_sales_leads_status
Tables: accept_all, account_tiering_standard, activity_logging_standards, attribution, case_management_sla, coaching_cadence, compliance_review_checklist, conversation_intelligence_standards, cpq_discount_policy, currency_handling, data_quality_rules, deal_desk_charter, disposition_codes, finance_approval_thresholds, forecast_methodology, fy2026_list_prices, handoff_to_ae, inbound_routing_matrix, lead_management_sop, lead_scoring_policy, meddic_scorecard, meeting_scheduling_sla, meeting_types_and_durations, mql_definition, opportunity_stage_gates, order_activation_runbook, renewal_playbook, risky, routing_decision_table, sal_gate, sequence_design_rules, snippets, snippets_and_retention, suppression_and_kpis, talk_ratio, territory, tracker_keywords, visitor_identification, volume_bands, web_form_definitions, all_segments_responses, api_keys, automations_link_stats_responses, automations_responses, batches, blocks, bounces, campaigns, category_stats, certificates, click_trackings, company_marketing_handoffs, contact_exports, contactdb_segments, marketing_campaigns, marketing_content_assets, singlesends, suppression_groups, accounts, cases, company_sales_handoffs, contacts, opportunities, sales_leads, sales_opportunities, tasks, company_sourcing_handoffs, customers, journal_entries, purchase_orders, sourcing_purchase_orders, sourcing_vendors, vendors, capabilities, bank_accounts, employees, account_links, account_sessions
"""
import json, sqlite3
"""Department records sub-agent: resolve one unique business handle from a free-text request without mutating state."""
import re, sqlite3

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

def core_records_agent(db_path, request=None, **kwargs):
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
_bf_orig_core_records_agent = core_records_agent
def _bf_friction_core_records_agent(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_core_records_agent(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "core_records_agent|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_core_records_agent(*_bf_args, **_bf_kwargs)
_bf_friction_core_records_agent.blobfish_original = _bf_orig_core_records_agent
core_records_agent = _bf_friction_core_records_agent

"""Department records sub-agent: resolve one unique business handle from a free-text request without mutating state."""
import re, sqlite3

_SURFACES = {"marketing_campaigns":{"table":"marketing_campaigns","primary_key":"id","labels":["campaign_code","name"],"readable":["id","campaign_code","name","channel","budget","owner_employee_id","start_date","end_date","status"],"resolvable":["campaign_code","name","channel","budget","owner_employee_id","start_date","end_date"],"mutable":["campaign_code","name","channel","budget","start_date","end_date","status"],"lifecycles":{"status":["draft","planned","active","paused","completed"]}},"marketing_content_assets":{"table":"marketing_content_assets","primary_key":"id","labels":["asset_number","title"],"readable":["id","asset_number","title","asset_type","campaign_id","author_employee_id","due_date","status"],"resolvable":["asset_number","title","asset_type","campaign_id","author_employee_id","due_date"],"mutable":["asset_number","title","asset_type","due_date","status"],"lifecycles":{"status":["draft","in_review","approved","published","archived"]}},"all_segments_responses":{"table":"all_segments_responses","primary_key":"id","labels":["id","name"],"readable":["id","contacts_count","created_at","name","next_sample_update","parent_list_ids","query_version","sample_updated_at","status","updated_at","metadata"],"resolvable":["id","contacts_count","created_at","name","next_sample_update","parent_list_ids","query_version","sample_updated_at","status","updated_at","metadata"],"mutable":["contacts_count","name","next_sample_update","parent_list_ids","query_version","status","metadata"],"lifecycles":{}},"api_keys":{"table":"api_keys","primary_key":"id","labels":["id","name"],"readable":["id","name","scopes","created_at"],"resolvable":["id","name","scopes","created_at"],"mutable":["name","scopes"],"lifecycles":{}},"automations_link_stats_responses":{"table":"automations_link_stats_responses","primary_key":"id","labels":["id"],"readable":["id","metadata","results","total_clicks"],"resolvable":["id","metadata","results","total_clicks"],"mutable":["metadata","results","total_clicks"],"lifecycles":{}},"automations_responses":{"table":"automations_responses","primary_key":"id","labels":["id"],"readable":["id","results","metadata"],"resolvable":["id","results","metadata"],"mutable":["results","metadata"],"lifecycles":{}},"batches":{"table":"batches","primary_key":"id","labels":["id"],"readable":["id","ids","created_at"],"resolvable":["id","ids","created_at"],"mutable":["ids"],"lifecycles":{}},"blocks":{"table":"blocks","primary_key":"id","labels":["id","email"],"readable":["id","delete_all","emails","email","created_at"],"resolvable":["id","delete_all","emails","email","created_at"],"mutable":["delete_all","emails","email"],"lifecycles":{}},"bounces":{"table":"bounces","primary_key":"id","labels":["id","email"],"readable":["id","delete_all","emails","created_at","created","status","email","reason"],"resolvable":["id","delete_all","emails","created_at","created","status","email","reason"],"mutable":["delete_all","emails","created","status","email","reason"],"lifecycles":{}},"campaigns":{"table":"campaigns","primary_key":"id","labels":["title","custom_unsubscribe_url","subject"],"readable":["id","created_at","title","status","sender_id","suppression_group_id","categories","custom_unsubscribe_url","editor","html_content","ip_pool","list_ids","plain_content","segment_ids","subject"],"resolvable":["created_at","title","status","sender_id","suppression_group_id","categories","custom_unsubscribe_url","editor","html_content","ip_pool","list_ids","plain_content","segment_ids","subject"],"mutable":["title","status","categories","custom_unsubscribe_url","editor","html_content","ip_pool","list_ids","plain_content","segment_ids","subject"],"lifecycles":{}},"category_stats":{"table":"category_stats","primary_key":"id","labels":["id"],"readable":["id","date","stats"],"resolvable":["id","date","stats"],"mutable":["date","stats"],"lifecycles":{}},"certificates":{"table":"certificates","primary_key":"id","labels":["id"],"readable":["id","enabled","integration_id","public_certificate","created_at"],"resolvable":["id","enabled","integration_id","public_certificate","created_at"],"mutable":["enabled","public_certificate"],"lifecycles":{}},"click_trackings":{"table":"click_trackings","primary_key":"id","labels":["id"],"readable":["id","enable_text","enabled"],"resolvable":["id","enable_text","enabled"],"mutable":["enable_text","enabled"],"lifecycles":{}},"contact_exports":{"table":"contact_exports","primary_key":"id","labels":["id"],"readable":["id","created_at","expires_at","status","updated_at","metadata","completed_at","contact_count","message","urls"],"resolvable":["id","created_at","expires_at","updated_at","metadata","completed_at","contact_count","message","urls"],"mutable":["expires_at","status","metadata","completed_at","contact_count","message","urls"],"lifecycles":{"status":["pending","ready","failure"]}},"contactdb_segments":{"table":"contactdb_segments","primary_key":"list_id","labels":["name"],"readable":["conditions","name","list_id","recipient_count"],"resolvable":["conditions","name","recipient_count"],"mutable":["conditions","name","recipient_count"],"lifecycles":{}},"singlesends":{"table":"singlesends","primary_key":"id","labels":["id","name"],"readable":["id","created_at","name","status","categories","email_config","send_at","send_to","updated_at","warnings"],"resolvable":["id","created_at","name","categories","email_config","send_at","send_to","updated_at","warnings"],"mutable":["name","status","categories","email_config","send_at","send_to","warnings"],"lifecycles":{"status":["draft","scheduled","triggered"]}},"suppression_groups":{"table":"suppression_groups","primary_key":"id","labels":["name","last_email_sent_at"],"readable":["id","description","name","is_default","last_email_sent_at","unsubscribes"],"resolvable":["description","name","is_default","last_email_sent_at","unsubscribes"],"mutable":["description","name","is_default","last_email_sent_at","unsubscribes"],"lifecycles":{}},"company_marketing_handoffs":{"table":"company_marketing_handoffs","primary_key":"id","labels":["handoff_ref"],"readable":["id","handoff_ref","core_record_id","system_record_id","source_system","source_table","requested_action","status","contract_id"],"resolvable":["handoff_ref","core_record_id","system_record_id","source_system","source_table","requested_action","contract_id"],"mutable":["handoff_ref","source_system","source_table","requested_action","status"],"lifecycles":{"status":["queued","linked","verified","completed"]}}}

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

def marketing_records_agent(db_path, request=None, **kwargs):
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
_bf_orig_marketing_records_agent = marketing_records_agent
def _bf_friction_marketing_records_agent(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_marketing_records_agent(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "marketing_records_agent|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_marketing_records_agent(*_bf_args, **_bf_kwargs)
_bf_friction_marketing_records_agent.blobfish_original = _bf_orig_marketing_records_agent
marketing_records_agent = _bf_friction_marketing_records_agent

"""Department records sub-agent: resolve one unique business handle from a free-text request without mutating state."""
import re, sqlite3

_SURFACES = {"sales_leads":{"table":"sales_leads","primary_key":"id","labels":["lead_number","company_name","contact_name"],"readable":["id","lead_number","company_name","contact_name","source","estimated_value","owner_employee_id","created_at","status"],"resolvable":["lead_number","company_name","contact_name","source","estimated_value","owner_employee_id","created_at"],"mutable":["lead_number","company_name","contact_name","source","estimated_value","status"],"lifecycles":{"status":["new","contacted","qualified","converted","lost"]}},"sales_opportunities":{"table":"sales_opportunities","primary_key":"id","labels":["opportunity_number","title"],"readable":["id","opportunity_number","title","lead_id","amount","owner_employee_id","expected_close_date","lead_management_sop_id","status"],"resolvable":["opportunity_number","title","lead_id","amount","owner_employee_id","expected_close_date","lead_management_sop_id"],"mutable":["opportunity_number","title","amount","expected_close_date","status"],"lifecycles":{"status":["discovery","proposal","negotiation","closed_won","closed_lost"]}},"accounts":{"table":"accounts","primary_key":"id","labels":["id","name"],"readable":["id","name","industry","status","owner_id","annual_revenue","created_at"],"resolvable":["id","name","industry","owner_id","annual_revenue","created_at"],"mutable":["name","industry","status","annual_revenue"],"lifecycles":{"status":["prospect","active","at_risk","inactive"]}},"cases":{"table":"cases","primary_key":"id","labels":["id","subject"],"readable":["id","account_id","contact_id","subject","status","priority","owner_id","description","created_at"],"resolvable":["id","account_id","contact_id","subject","priority","owner_id","description","created_at"],"mutable":["subject","status","priority","description"],"lifecycles":{"status":["new","working","waiting_customer","escalated","closed"]}},"contacts":{"table":"contacts","primary_key":"id","labels":["id","name","email"],"readable":["id","account_id","name","email","status","owner_id","created_at"],"resolvable":["id","account_id","name","email","owner_id","created_at"],"mutable":["name","email","status"],"lifecycles":{"status":["new","qualified","active","opted_out"]}},"opportunities":{"table":"opportunities","primary_key":"id","labels":["id","name"],"readable":["id","account_id","name","status","amount","close_date","owner_id","created_at"],"resolvable":["id","account_id","name","amount","close_date","owner_id","created_at"],"mutable":["name","status","amount","close_date"],"lifecycles":{"status":["discovery","proposal","negotiation","closed_won","closed_lost"]}},"tasks":{"table":"tasks","primary_key":"id","labels":["id"],"readable":["id","account_id","subject","status","priority","assigned_to","due_at","description"],"resolvable":["id","account_id","subject","priority","assigned_to","due_at","description"],"mutable":["subject","status","priority","assigned_to","due_at","description"],"lifecycles":{"status":["open","in_progress","blocked","completed","cancelled"]}},"company_sales_handoffs":{"table":"company_sales_handoffs","primary_key":"id","labels":["handoff_ref"],"readable":["id","handoff_ref","core_record_id","system_record_id","source_system","source_table","requested_action","status","contract_id"],"resolvable":["handoff_ref","core_record_id","system_record_id","source_system","source_table","requested_action","contract_id"],"mutable":["handoff_ref","source_system","source_table","requested_action","status"],"lifecycles":{"status":["queued","linked","verified","completed"]}}}

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
    return _bf_orig_sales_records_agent(*_bf_args, **_bf_kwargs)
_bf_friction_sales_records_agent.blobfish_original = _bf_orig_sales_records_agent
sales_records_agent = _bf_friction_sales_records_agent

"""Department records sub-agent: resolve one unique business handle from a free-text request without mutating state."""
import re, sqlite3

_SURFACES = {"sourcing_vendors":{"table":"sourcing_vendors","primary_key":"id","labels":["vendor_number","name","contact_name"],"readable":["id","vendor_number","name","category","contact_name","owner_employee_id","onboarded_at","status"],"resolvable":["vendor_number","name","category","contact_name","owner_employee_id","onboarded_at"],"mutable":["vendor_number","name","category","contact_name","onboarded_at","status"],"lifecycles":{"status":["prospective","under_review","approved","suspended"]}},"sourcing_purchase_orders":{"table":"sourcing_purchase_orders","primary_key":"id","labels":["po_number"],"readable":["id","po_number","vendor_id","requested_by_employee_id","amount","ordered_at","approver_employee_id","status"],"resolvable":["po_number","vendor_id","requested_by_employee_id","amount","ordered_at","approver_employee_id"],"mutable":["po_number","amount","ordered_at","status"],"lifecycles":{"status":["draft","submitted","approved","received","closed"]}},"customers":{"table":"customers","primary_key":"id","labels":["id","name","email"],"readable":["id","name","email","status","currency","balance","created_at"],"resolvable":["id","name","email","currency","balance","created_at"],"mutable":["name","email","status","currency","balance"],"lifecycles":{"status":["prospect","active","credit_hold","inactive"]}},"journal_entries":{"table":"journal_entries","primary_key":"id","labels":["id"],"readable":["id","status","amount","currency","memo","approved_by","created_at"],"resolvable":["id","amount","currency","memo","approved_by","created_at"],"mutable":["status","amount","currency","memo","approved_by"],"lifecycles":{"status":["draft","submitted","approved","posted","reversed"]}},"purchase_orders":{"table":"purchase_orders","primary_key":"id","labels":["id"],"readable":["id","vendor_id","status","amount","currency","owner_id","created_at"],"resolvable":["id","vendor_id","amount","currency","owner_id","created_at"],"mutable":["status","amount","currency"],"lifecycles":{"status":["draft","pending_approval","approved","received","closed","cancelled"]}},"vendors":{"table":"vendors","primary_key":"id","labels":["id","name","email"],"readable":["id","name","email","status","currency","balance","created_at"],"resolvable":["id","name","email","currency","balance","created_at"],"mutable":["name","email","status","currency","balance"],"lifecycles":{"status":["pending_review","active","on_hold","inactive"]}},"company_sourcing_handoffs":{"table":"company_sourcing_handoffs","primary_key":"id","labels":["handoff_ref"],"readable":["id","handoff_ref","core_record_id","system_record_id","source_system","source_table","requested_action","status","contract_id"],"resolvable":["handoff_ref","core_record_id","system_record_id","source_system","source_table","requested_action","contract_id"],"mutable":["handoff_ref","source_system","source_table","requested_action","status"],"lifecycles":{"status":["queued","linked","verified","completed"]}}}

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
    return _bf_orig_sourcing_records_agent(*_bf_args, **_bf_kwargs)
_bf_friction_sourcing_records_agent.blobfish_original = _bf_orig_sourcing_records_agent
sourcing_records_agent = _bf_friction_sourcing_records_agent

def accounts_list(db_path='state.db', **kwargs):
    '''List accounts with bounded lifecycle filtering. (GET /services/data/v1/accounts)'''
    if kwargs.get('status') is not None and kwargs.get('status') not in ['prospect', 'active', 'at_risk', 'inactive']:
        return {'error': 'invalid value for status: %r. Accepted: %s' % (kwargs.get('status'), ', '.join(['prospect', 'active', 'at_risk', 'inactive'])), 'status': 422, 'parameter': 'status', 'accepted': ['prospect', 'active', 'at_risk', 'inactive']}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('status') is not None:
            _where.append('"status" = ?')
            _args.append(str(kwargs['status']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "accounts"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        return {'items': _rows, 'count': len(_rows)}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_accounts_list = accounts_list
def _bf_friction_accounts_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_accounts_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "accounts_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_accounts_list(*_bf_args, **_bf_kwargs)
_bf_friction_accounts_list.blobfish_original = _bf_orig_accounts_list
accounts_list = _bf_friction_accounts_list

def contacts_list(db_path='state.db', **kwargs):
    '''List contacts with bounded lifecycle filtering. (GET /services/data/v1/contacts)'''
    if kwargs.get('status') is not None and kwargs.get('status') not in ['new', 'qualified', 'active', 'opted_out']:
        return {'error': 'invalid value for status: %r. Accepted: %s' % (kwargs.get('status'), ', '.join(['new', 'qualified', 'active', 'opted_out'])), 'status': 422, 'parameter': 'status', 'accepted': ['new', 'qualified', 'active', 'opted_out']}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('status') is not None:
            _where.append('"status" = ?')
            _args.append(str(kwargs['status']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "contacts"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        return {'items': _rows, 'count': len(_rows)}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_contacts_list = contacts_list
def _bf_friction_contacts_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_contacts_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "contacts_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_contacts_list(*_bf_args, **_bf_kwargs)
_bf_friction_contacts_list.blobfish_original = _bf_orig_contacts_list
contacts_list = _bf_friction_contacts_list

def account_get(db_path='state.db', **kwargs):
    '''Get one account by id. (GET /services/data/v1/accounts/{id})'''
    _missing = [p for p in ['id'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "accounts" WHERE "id" = ?', [str(kwargs.get('id'))]).fetchone()
        if _row is None:
            return {'error': 'account not found', 'status': 404}
        _out = dict(_row)
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_account_get = account_get
def _bf_friction_account_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_account_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "account_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_account_get(*_bf_args, **_bf_kwargs)
_bf_friction_account_get.blobfish_original = _bf_orig_account_get
account_get = _bf_friction_account_get

def contact_get(db_path='state.db', **kwargs):
    '''Get one contact by id. (GET /services/data/v1/contacts/{id})'''
    _missing = [p for p in ['id'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "contacts" WHERE "id" = ?', [str(kwargs.get('id'))]).fetchone()
        if _row is None:
            return {'error': 'contact not found', 'status': 404}
        _out = dict(_row)
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_contact_get = contact_get
def _bf_friction_contact_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_contact_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "contact_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_contact_get(*_bf_args, **_bf_kwargs)
_bf_friction_contact_get.blobfish_original = _bf_orig_contact_get
contact_get = _bf_friction_contact_get

def opportunity_get(db_path='state.db', **kwargs):
    '''Get one opportunity by id. (GET /services/data/v1/opportunities/{id})'''
    _missing = [p for p in ['id'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "opportunities" WHERE "id" = ?', [str(kwargs.get('id'))]).fetchone()
        if _row is None:
            return {'error': 'opportunity not found', 'status': 404}
        _out = dict(_row)
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_opportunity_get = opportunity_get
def _bf_friction_opportunity_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_opportunity_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "opportunity_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_opportunity_get(*_bf_args, **_bf_kwargs)
_bf_friction_opportunity_get.blobfish_original = _bf_orig_opportunity_get
opportunity_get = _bf_friction_opportunity_get

def get_accounts_account_capabilities(db_path='state.db', **kwargs):
    '''List all account capabilities (GET /v1/accounts/{account}/capabilities)'''
    _missing = [p for p in ['account'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('account') is not None:
            _where.append('"account" = ?')
            _args.append(str(kwargs['account']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "capabilities"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        return {'items': _rows, 'count': len(_rows)}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_accounts_account_capabilities = get_accounts_account_capabilities
def _bf_friction_get_accounts_account_capabilities(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_accounts_account_capabilities(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_accounts_account_capabilities|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_accounts_account_capabilities(*_bf_args, **_bf_kwargs)
_bf_friction_get_accounts_account_capabilities.blobfish_original = _bf_orig_get_accounts_account_capabilities
get_accounts_account_capabilities = _bf_friction_get_accounts_account_capabilities

def get_customers_customer_bank_accounts(db_path='state.db', **kwargs):
    '''List all bank accounts (GET /v1/customers/{customer}/bank_accounts)'''
    _missing = [p for p in ['customer'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('customer') is not None:
            _where.append('"customer" = ?')
            _args.append(str(kwargs['customer']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "bank_accounts"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        return {'items': _rows, 'count': len(_rows)}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_customers_customer_bank_accounts = get_customers_customer_bank_accounts
def _bf_friction_get_customers_customer_bank_accounts(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_customers_customer_bank_accounts(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_customers_customer_bank_accounts|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_customers_customer_bank_accounts(*_bf_args, **_bf_kwargs)
_bf_friction_get_customers_customer_bank_accounts.blobfish_original = _bf_orig_get_customers_customer_bank_accounts
get_customers_customer_bank_accounts = _bf_friction_get_customers_customer_bank_accounts

def get_contactdb_segments_segment_id(db_path='state.db', **kwargs):
    '''Retrieve a segment (GET /contactdb/segments/{segment_id})'''
    _missing = [p for p in ['segment_id', 'segment_id'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "contactdb_segments" WHERE "list_id" = ?', [str(kwargs.get('segment_id'))]).fetchone()
        if _row is None:
            return {'error': 'contactdb_segment not found', 'status': 404}
        _out = dict(_row)
        for _jc in ['conditions']:
            if isinstance(_out.get(_jc), str) and _out[_jc][:1] in ('[', '{'):
                try:
                    _out[_jc] = json.loads(_out[_jc])
                except Exception:
                    pass
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_contactdb_segments_segment_id = get_contactdb_segments_segment_id
def _bf_friction_get_contactdb_segments_segment_id(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_contactdb_segments_segment_id(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_contactdb_segments_segment_id|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_contactdb_segments_segment_id(*_bf_args, **_bf_kwargs)
_bf_friction_get_contactdb_segments_segment_id.blobfish_original = _bf_orig_get_contactdb_segments_segment_id
get_contactdb_segments_segment_id = _bf_friction_get_contactdb_segments_segment_id

def get_mc_contacts_exports_id(db_path='state.db', **kwargs):
    '''Export Contacts Status (GET /marketing/contacts/exports/{id})'''
    _missing = [p for p in ['id'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "contact_exports" WHERE "id" = ?', [str(kwargs.get('id'))]).fetchone()
        if _row is None:
            return {'error': 'contact_export not found', 'status': 404}
        _out = dict(_row)
        for _jc in ['metadata', 'urls']:
            if isinstance(_out.get(_jc), str) and _out[_jc][:1] in ('[', '{'):
                try:
                    _out[_jc] = json.loads(_out[_jc])
                except Exception:
                    pass
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_get_mc_contacts_exports_id = get_mc_contacts_exports_id
def _bf_friction_get_mc_contacts_exports_id(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_get_mc_contacts_exports_id(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "get_mc_contacts_exports_id|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_get_mc_contacts_exports_id(*_bf_args, **_bf_kwargs)
_bf_friction_get_mc_contacts_exports_id.blobfish_original = _bf_orig_get_mc_contacts_exports_id
get_mc_contacts_exports_id = _bf_friction_get_mc_contacts_exports_id

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
    return _bf_orig_lookup_sales_lead_with_employees(*_bf_args, **_bf_kwargs)
_bf_friction_lookup_sales_lead_with_employees.blobfish_original = _bf_orig_lookup_sales_lead_with_employees
lookup_sales_lead_with_employees = _bf_friction_lookup_sales_lead_with_employees

"""Look up sales_opportunity with sales_leads context"""
import sqlite3

def lookup_sales_opportunity_with_sales_leads(db_path: str, id: int) -> dict:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM sales_opportunities WHERE id = ?", [id]).fetchone()
    if not row:
        conn.close()
        return {"error": f"sales_opportunity {id} not found"}
    result = dict(row)
    parent = conn.execute("SELECT * FROM sales_leads WHERE id = ?", [row["lead_id"]]).fetchone()
    result["sales_leads"] = dict(parent) if parent else None
    conn.close()
    return result

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_lookup_sales_opportunity_with_sales_leads = lookup_sales_opportunity_with_sales_leads
def _bf_friction_lookup_sales_opportunity_with_sales_leads(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_lookup_sales_opportunity_with_sales_leads(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "lookup_sales_opportunity_with_sales_leads|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_lookup_sales_opportunity_with_sales_leads(*_bf_args, **_bf_kwargs)
_bf_friction_lookup_sales_opportunity_with_sales_leads.blobfish_original = _bf_orig_lookup_sales_opportunity_with_sales_leads
lookup_sales_opportunity_with_sales_leads = _bf_friction_lookup_sales_opportunity_with_sales_leads

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

"""Department workflow sub-agent: resolve one business handle and apply one narrow field update from a free-text request."""
import json, re, sqlite3

_SURFACES = {"marketing_campaigns":{"table":"marketing_campaigns","primary_key":"id","labels":["campaign_code","name"],"readable":["id","campaign_code","name","channel","budget","owner_employee_id","start_date","end_date","status"],"resolvable":["campaign_code","name","channel","budget","owner_employee_id","start_date","end_date"],"mutable":["campaign_code","name","channel","budget","start_date","end_date","status"],"lifecycles":{"status":["draft","planned","active","paused","completed"]}},"marketing_content_assets":{"table":"marketing_content_assets","primary_key":"id","labels":["asset_number","title"],"readable":["id","asset_number","title","asset_type","campaign_id","author_employee_id","due_date","status"],"resolvable":["asset_number","title","asset_type","campaign_id","author_employee_id","due_date"],"mutable":["asset_number","title","asset_type","due_date","status"],"lifecycles":{"status":["draft","in_review","approved","published","archived"]}},"all_segments_responses":{"table":"all_segments_responses","primary_key":"id","labels":["id","name"],"readable":["id","contacts_count","created_at","name","next_sample_update","parent_list_ids","query_version","sample_updated_at","status","updated_at","metadata"],"resolvable":["id","contacts_count","created_at","name","next_sample_update","parent_list_ids","query_version","sample_updated_at","status","updated_at","metadata"],"mutable":["contacts_count","name","next_sample_update","parent_list_ids","query_version","status","metadata"],"lifecycles":{}},"api_keys":{"table":"api_keys","primary_key":"id","labels":["id","name"],"readable":["id","name","scopes","created_at"],"resolvable":["id","name","scopes","created_at"],"mutable":["name","scopes"],"lifecycles":{}},"automations_link_stats_responses":{"table":"automations_link_stats_responses","primary_key":"id","labels":["id"],"readable":["id","metadata","results","total_clicks"],"resolvable":["id","metadata","results","total_clicks"],"mutable":["metadata","results","total_clicks"],"lifecycles":{}},"automations_responses":{"table":"automations_responses","primary_key":"id","labels":["id"],"readable":["id","results","metadata"],"resolvable":["id","results","metadata"],"mutable":["results","metadata"],"lifecycles":{}},"batches":{"table":"batches","primary_key":"id","labels":["id"],"readable":["id","ids","created_at"],"resolvable":["id","ids","created_at"],"mutable":["ids"],"lifecycles":{}},"blocks":{"table":"blocks","primary_key":"id","labels":["id","email"],"readable":["id","delete_all","emails","email","created_at"],"resolvable":["id","delete_all","emails","email","created_at"],"mutable":["delete_all","emails","email"],"lifecycles":{}},"bounces":{"table":"bounces","primary_key":"id","labels":["id","email"],"readable":["id","delete_all","emails","created_at","created","status","email","reason"],"resolvable":["id","delete_all","emails","created_at","created","status","email","reason"],"mutable":["delete_all","emails","created","status","email","reason"],"lifecycles":{}},"campaigns":{"table":"campaigns","primary_key":"id","labels":["title","custom_unsubscribe_url","subject"],"readable":["id","created_at","title","status","sender_id","suppression_group_id","categories","custom_unsubscribe_url","editor","html_content","ip_pool","list_ids","plain_content","segment_ids","subject"],"resolvable":["created_at","title","status","sender_id","suppression_group_id","categories","custom_unsubscribe_url","editor","html_content","ip_pool","list_ids","plain_content","segment_ids","subject"],"mutable":["title","status","categories","custom_unsubscribe_url","editor","html_content","ip_pool","list_ids","plain_content","segment_ids","subject"],"lifecycles":{}},"category_stats":{"table":"category_stats","primary_key":"id","labels":["id"],"readable":["id","date","stats"],"resolvable":["id","date","stats"],"mutable":["date","stats"],"lifecycles":{}},"certificates":{"table":"certificates","primary_key":"id","labels":["id"],"readable":["id","enabled","integration_id","public_certificate","created_at"],"resolvable":["id","enabled","integration_id","public_certificate","created_at"],"mutable":["enabled","public_certificate"],"lifecycles":{}},"click_trackings":{"table":"click_trackings","primary_key":"id","labels":["id"],"readable":["id","enable_text","enabled"],"resolvable":["id","enable_text","enabled"],"mutable":["enable_text","enabled"],"lifecycles":{}},"contact_exports":{"table":"contact_exports","primary_key":"id","labels":["id"],"readable":["id","created_at","expires_at","status","updated_at","metadata","completed_at","contact_count","message","urls"],"resolvable":["id","created_at","expires_at","updated_at","metadata","completed_at","contact_count","message","urls"],"mutable":["expires_at","status","metadata","completed_at","contact_count","message","urls"],"lifecycles":{"status":["pending","ready","failure"]}},"contactdb_segments":{"table":"contactdb_segments","primary_key":"list_id","labels":["name"],"readable":["conditions","name","list_id","recipient_count"],"resolvable":["conditions","name","recipient_count"],"mutable":["conditions","name","recipient_count"],"lifecycles":{}},"singlesends":{"table":"singlesends","primary_key":"id","labels":["id","name"],"readable":["id","created_at","name","status","categories","email_config","send_at","send_to","updated_at","warnings"],"resolvable":["id","created_at","name","categories","email_config","send_at","send_to","updated_at","warnings"],"mutable":["name","status","categories","email_config","send_at","send_to","warnings"],"lifecycles":{"status":["draft","scheduled","triggered"]}},"suppression_groups":{"table":"suppression_groups","primary_key":"id","labels":["name","last_email_sent_at"],"readable":["id","description","name","is_default","last_email_sent_at","unsubscribes"],"resolvable":["description","name","is_default","last_email_sent_at","unsubscribes"],"mutable":["description","name","is_default","last_email_sent_at","unsubscribes"],"lifecycles":{}},"company_marketing_handoffs":{"table":"company_marketing_handoffs","primary_key":"id","labels":["handoff_ref"],"readable":["id","handoff_ref","core_record_id","system_record_id","source_system","source_table","requested_action","status","contract_id"],"resolvable":["handoff_ref","core_record_id","system_record_id","source_system","source_table","requested_action","contract_id"],"mutable":["handoff_ref","source_system","source_table","requested_action","status"],"lifecycles":{"status":["queued","linked","verified","completed"]}}}

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

def marketing_workflow_agent(db_path, request=None, **kwargs):
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
_bf_orig_marketing_workflow_agent = marketing_workflow_agent
def _bf_friction_marketing_workflow_agent(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_marketing_workflow_agent(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "marketing_workflow_agent|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_marketing_workflow_agent(*_bf_args, **_bf_kwargs)
_bf_friction_marketing_workflow_agent.blobfish_original = _bf_orig_marketing_workflow_agent
marketing_workflow_agent = _bf_friction_marketing_workflow_agent

"""Department workflow sub-agent: resolve one business handle and apply one narrow field update from a free-text request."""
import json, re, sqlite3

_SURFACES = {"sales_leads":{"table":"sales_leads","primary_key":"id","labels":["lead_number","company_name","contact_name"],"readable":["id","lead_number","company_name","contact_name","source","estimated_value","owner_employee_id","created_at","status"],"resolvable":["lead_number","company_name","contact_name","source","estimated_value","owner_employee_id","created_at"],"mutable":["lead_number","company_name","contact_name","source","estimated_value","status"],"lifecycles":{"status":["new","contacted","qualified","converted","lost"]}},"sales_opportunities":{"table":"sales_opportunities","primary_key":"id","labels":["opportunity_number","title"],"readable":["id","opportunity_number","title","lead_id","amount","owner_employee_id","expected_close_date","lead_management_sop_id","status"],"resolvable":["opportunity_number","title","lead_id","amount","owner_employee_id","expected_close_date","lead_management_sop_id"],"mutable":["opportunity_number","title","amount","expected_close_date","status"],"lifecycles":{"status":["discovery","proposal","negotiation","closed_won","closed_lost"]}},"accounts":{"table":"accounts","primary_key":"id","labels":["id","name"],"readable":["id","name","industry","status","owner_id","annual_revenue","created_at"],"resolvable":["id","name","industry","owner_id","annual_revenue","created_at"],"mutable":["name","industry","status","annual_revenue"],"lifecycles":{"status":["prospect","active","at_risk","inactive"]}},"cases":{"table":"cases","primary_key":"id","labels":["id","subject"],"readable":["id","account_id","contact_id","subject","status","priority","owner_id","description","created_at"],"resolvable":["id","account_id","contact_id","subject","priority","owner_id","description","created_at"],"mutable":["subject","status","priority","description"],"lifecycles":{"status":["new","working","waiting_customer","escalated","closed"]}},"contacts":{"table":"contacts","primary_key":"id","labels":["id","name","email"],"readable":["id","account_id","name","email","status","owner_id","created_at"],"resolvable":["id","account_id","name","email","owner_id","created_at"],"mutable":["name","email","status"],"lifecycles":{"status":["new","qualified","active","opted_out"]}},"opportunities":{"table":"opportunities","primary_key":"id","labels":["id","name"],"readable":["id","account_id","name","status","amount","close_date","owner_id","created_at"],"resolvable":["id","account_id","name","amount","close_date","owner_id","created_at"],"mutable":["name","status","amount","close_date"],"lifecycles":{"status":["discovery","proposal","negotiation","closed_won","closed_lost"]}},"tasks":{"table":"tasks","primary_key":"id","labels":["id"],"readable":["id","account_id","subject","status","priority","assigned_to","due_at","description"],"resolvable":["id","account_id","subject","priority","assigned_to","due_at","description"],"mutable":["subject","status","priority","assigned_to","due_at","description"],"lifecycles":{"status":["open","in_progress","blocked","completed","cancelled"]}},"company_sales_handoffs":{"table":"company_sales_handoffs","primary_key":"id","labels":["handoff_ref"],"readable":["id","handoff_ref","core_record_id","system_record_id","source_system","source_table","requested_action","status","contract_id"],"resolvable":["handoff_ref","core_record_id","system_record_id","source_system","source_table","requested_action","contract_id"],"mutable":["handoff_ref","source_system","source_table","requested_action","status"],"lifecycles":{"status":["queued","linked","verified","completed"]}}}

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
    return _bf_orig_sales_workflow_agent(*_bf_args, **_bf_kwargs)
_bf_friction_sales_workflow_agent.blobfish_original = _bf_orig_sales_workflow_agent
sales_workflow_agent = _bf_friction_sales_workflow_agent

"""Department workflow sub-agent: resolve one business handle and apply one narrow field update from a free-text request."""
import json, re, sqlite3

_SURFACES = {"sourcing_vendors":{"table":"sourcing_vendors","primary_key":"id","labels":["vendor_number","name","contact_name"],"readable":["id","vendor_number","name","category","contact_name","owner_employee_id","onboarded_at","status"],"resolvable":["vendor_number","name","category","contact_name","owner_employee_id","onboarded_at"],"mutable":["vendor_number","name","category","contact_name","onboarded_at","status"],"lifecycles":{"status":["prospective","under_review","approved","suspended"]}},"sourcing_purchase_orders":{"table":"sourcing_purchase_orders","primary_key":"id","labels":["po_number"],"readable":["id","po_number","vendor_id","requested_by_employee_id","amount","ordered_at","approver_employee_id","status"],"resolvable":["po_number","vendor_id","requested_by_employee_id","amount","ordered_at","approver_employee_id"],"mutable":["po_number","amount","ordered_at","status"],"lifecycles":{"status":["draft","submitted","approved","received","closed"]}},"customers":{"table":"customers","primary_key":"id","labels":["id","name","email"],"readable":["id","name","email","status","currency","balance","created_at"],"resolvable":["id","name","email","currency","balance","created_at"],"mutable":["name","email","status","currency","balance"],"lifecycles":{"status":["prospect","active","credit_hold","inactive"]}},"journal_entries":{"table":"journal_entries","primary_key":"id","labels":["id"],"readable":["id","status","amount","currency","memo","approved_by","created_at"],"resolvable":["id","amount","currency","memo","approved_by","created_at"],"mutable":["status","amount","currency","memo","approved_by"],"lifecycles":{"status":["draft","submitted","approved","posted","reversed"]}},"purchase_orders":{"table":"purchase_orders","primary_key":"id","labels":["id"],"readable":["id","vendor_id","status","amount","currency","owner_id","created_at"],"resolvable":["id","vendor_id","amount","currency","owner_id","created_at"],"mutable":["status","amount","currency"],"lifecycles":{"status":["draft","pending_approval","approved","received","closed","cancelled"]}},"vendors":{"table":"vendors","primary_key":"id","labels":["id","name","email"],"readable":["id","name","email","status","currency","balance","created_at"],"resolvable":["id","name","email","currency","balance","created_at"],"mutable":["name","email","status","currency","balance"],"lifecycles":{"status":["pending_review","active","on_hold","inactive"]}},"company_sourcing_handoffs":{"table":"company_sourcing_handoffs","primary_key":"id","labels":["handoff_ref"],"readable":["id","handoff_ref","core_record_id","system_record_id","source_system","source_table","requested_action","status","contract_id"],"resolvable":["handoff_ref","core_record_id","system_record_id","source_system","source_table","requested_action","contract_id"],"mutable":["handoff_ref","source_system","source_table","requested_action","status"],"lifecycles":{"status":["queued","linked","verified","completed"]}}}

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
    return _bf_orig_sourcing_workflow_agent(*_bf_args, **_bf_kwargs)
_bf_friction_sourcing_workflow_agent.blobfish_original = _bf_orig_sourcing_workflow_agent
sourcing_workflow_agent = _bf_friction_sourcing_workflow_agent

def account_create(db_path='state.db', **kwargs):
    '''Create one tenant-scoped account. (POST /services/data/v1/accounts)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _n = cur.execute('SELECT COALESCE(MAX(rowid), 0) + 100 FROM "accounts"').fetchone()[0] + 1
        _base = datetime.datetime(2026, 1, 5, 9, 0, 0)
        _ts = (_base + datetime.timedelta(minutes=_n)).strftime('%Y-%m-%dT%H:%M:%SZ')
        _cols = ['"id"']
        _vals = ['account_%03d' % _n]
        if kwargs.get('name') is not None:
            _cols.append('"name"')
            _vals.append(str(kwargs['name']))
        if kwargs.get('industry') is not None:
            _cols.append('"industry"')
            _vals.append(str(kwargs['industry']))
        if kwargs.get('status') is not None:
            _cols.append('"status"')
            _vals.append(str(kwargs['status']))
        if kwargs.get('owner_id') is not None:
            _cols.append('"owner_id"')
            _vals.append(str(kwargs['owner_id']))
        if kwargs.get('annual_revenue') is not None:
            _cols.append('"annual_revenue"')
            _vals.append(float(kwargs['annual_revenue']))
        _cols.append('"created_at"')
        _vals.append(_ts)
        if '"status"' not in _cols:
            _cols.append('"status"')
            _vals.append('open')
        _sql = 'INSERT INTO "accounts" (' + ', '.join(_cols) + ') VALUES (' + ', '.join(['?'] * len(_vals)) + ')'
        try:
            cur.execute(_sql, _vals)
        except sqlite3.IntegrityError:
            conn.rollback()
            return {'error': 'conflict: duplicate key', 'status': 409}
        conn.commit()
        _row = cur.execute('SELECT * FROM "accounts" WHERE "id" = ?', [_vals[0]]).fetchone()
        _out = dict(_row)
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_account_create = account_create
def _bf_friction_account_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_account_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "account_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_account_create(*_bf_args, **_bf_kwargs)
_bf_friction_account_create.blobfish_original = _bf_orig_account_create
account_create = _bf_friction_account_create

def contact_create(db_path='state.db', **kwargs):
    '''Create one tenant-scoped contact. (POST /services/data/v1/contacts)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _n = cur.execute('SELECT COALESCE(MAX(rowid), 0) + 100 FROM "contacts"').fetchone()[0] + 1
        _base = datetime.datetime(2026, 1, 5, 9, 0, 0)
        _ts = (_base + datetime.timedelta(minutes=_n)).strftime('%Y-%m-%dT%H:%M:%SZ')
        _cols = ['"id"']
        _vals = ['contact_%03d' % _n]
        if kwargs.get('account_id') is not None:
            _cols.append('"account_id"')
            _vals.append(str(kwargs['account_id']))
        if kwargs.get('name') is not None:
            _cols.append('"name"')
            _vals.append(str(kwargs['name']))
        if kwargs.get('email') is not None:
            _cols.append('"email"')
            _vals.append(str(kwargs['email']))
        if kwargs.get('status') is not None:
            _cols.append('"status"')
            _vals.append(str(kwargs['status']))
        if kwargs.get('owner_id') is not None:
            _cols.append('"owner_id"')
            _vals.append(str(kwargs['owner_id']))
        _cols.append('"created_at"')
        _vals.append(_ts)
        if '"status"' not in _cols:
            _cols.append('"status"')
            _vals.append('open')
        _sql = 'INSERT INTO "contacts" (' + ', '.join(_cols) + ') VALUES (' + ', '.join(['?'] * len(_vals)) + ')'
        try:
            cur.execute(_sql, _vals)
        except sqlite3.IntegrityError:
            conn.rollback()
            return {'error': 'conflict: duplicate key', 'status': 409}
        conn.commit()
        _row = cur.execute('SELECT * FROM "contacts" WHERE "id" = ?', [_vals[0]]).fetchone()
        _out = dict(_row)
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_contact_create = contact_create
def _bf_friction_contact_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_contact_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "contact_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_contact_create(*_bf_args, **_bf_kwargs)
_bf_friction_contact_create.blobfish_original = _bf_orig_contact_create
contact_create = _bf_friction_contact_create

def opportunity_create(db_path='state.db', **kwargs):
    '''Create one tenant-scoped opportunity. (POST /services/data/v1/opportunities)'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _n = cur.execute('SELECT COALESCE(MAX(rowid), 0) + 100 FROM "opportunities"').fetchone()[0] + 1
        _base = datetime.datetime(2026, 1, 5, 9, 0, 0)
        _ts = (_base + datetime.timedelta(minutes=_n)).strftime('%Y-%m-%dT%H:%M:%SZ')
        _cols = ['"id"']
        _vals = ['opportunity_%03d' % _n]
        if kwargs.get('account_id') is not None:
            _cols.append('"account_id"')
            _vals.append(str(kwargs['account_id']))
        if kwargs.get('name') is not None:
            _cols.append('"name"')
            _vals.append(str(kwargs['name']))
        if kwargs.get('status') is not None:
            _cols.append('"status"')
            _vals.append(str(kwargs['status']))
        if kwargs.get('amount') is not None:
            _cols.append('"amount"')
            _vals.append(float(kwargs['amount']))
        if kwargs.get('owner_id') is not None:
            _cols.append('"owner_id"')
            _vals.append(str(kwargs['owner_id']))
        _cols.append('"created_at"')
        _vals.append(_ts)
        if '"status"' not in _cols:
            _cols.append('"status"')
            _vals.append('open')
        _sql = 'INSERT INTO "opportunities" (' + ', '.join(_cols) + ') VALUES (' + ', '.join(['?'] * len(_vals)) + ')'
        try:
            cur.execute(_sql, _vals)
        except sqlite3.IntegrityError:
            conn.rollback()
            return {'error': 'conflict: duplicate key', 'status': 409}
        conn.commit()
        _row = cur.execute('SELECT * FROM "opportunities" WHERE "id" = ?', [_vals[0]]).fetchone()
        _out = dict(_row)
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_opportunity_create = opportunity_create
def _bf_friction_opportunity_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_opportunity_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "opportunity_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_opportunity_create(*_bf_args, **_bf_kwargs)
_bf_friction_opportunity_create.blobfish_original = _bf_orig_opportunity_create
opportunity_create = _bf_friction_opportunity_create

def post_account_links(db_path='state.db', **kwargs):
    '''Create an account link (POST /v1/account_links)'''
    _missing = [p for p in ['account', 'type'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _n = cur.execute('SELECT COALESCE(MAX(rowid), 0) + 100 FROM "account_links"').fetchone()[0] + 1
        _base = datetime.datetime(2026, 1, 5, 9, 0, 0)
        _ts = (_base + datetime.timedelta(minutes=_n)).strftime('%Y-%m-%dT%H:%M:%SZ')
        _cols = ['"id"']
        _vals = ['account_link_' + str(_n).zfill(14) + '']
        _sql = 'INSERT INTO "account_links" (' + ', '.join(_cols) + ') VALUES (' + ', '.join(['?'] * len(_vals)) + ')'
        try:
            cur.execute(_sql, _vals)
        except sqlite3.IntegrityError:
            conn.rollback()
            return {'error': 'conflict: duplicate key', 'status': 409}
        conn.commit()
        _row = cur.execute('SELECT * FROM "account_links" WHERE "id" = ?', [_vals[0]]).fetchone()
        _out = dict(_row)
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_account_links = post_account_links
def _bf_friction_post_account_links(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_account_links(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_account_links|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_account_links(*_bf_args, **_bf_kwargs)
_bf_friction_post_account_links.blobfish_original = _bf_orig_post_account_links
post_account_links = _bf_friction_post_account_links

def post_account_sessions(db_path='state.db', **kwargs):
    '''Create an Account Session (POST /v1/account_sessions)'''
    _missing = [p for p in ['account', 'components'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _n = cur.execute('SELECT COALESCE(MAX(rowid), 0) + 100 FROM "account_sessions"').fetchone()[0] + 1
        _base = datetime.datetime(2026, 1, 5, 9, 0, 0)
        _ts = (_base + datetime.timedelta(minutes=_n)).strftime('%Y-%m-%dT%H:%M:%SZ')
        _cols = ['"id"']
        _vals = ['account_session_' + str(_n).zfill(14) + '']
        if kwargs.get('account') is not None:
            _cols.append('"account"')
            _vals.append(str(kwargs['account']))
        if kwargs.get('components') is not None:
            _cols.append('"components"')
            _vals.append(json.dumps(kwargs['components']) if not isinstance(kwargs['components'], str) else kwargs['components'])
        _sql = 'INSERT INTO "account_sessions" (' + ', '.join(_cols) + ') VALUES (' + ', '.join(['?'] * len(_vals)) + ')'
        try:
            cur.execute(_sql, _vals)
        except sqlite3.IntegrityError:
            conn.rollback()
            return {'error': 'conflict: duplicate key', 'status': 409}
        conn.commit()
        _row = cur.execute('SELECT * FROM "account_sessions" WHERE "id" = ?', [_vals[0]]).fetchone()
        _out = dict(_row)
        for _jc in ['components']:
            if isinstance(_out.get(_jc), str) and _out[_jc][:1] in ('[', '{'):
                try:
                    _out[_jc] = json.loads(_out[_jc])
                except Exception:
                    pass
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_account_sessions = post_account_sessions
def _bf_friction_post_account_sessions(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_account_sessions(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_account_sessions|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_account_sessions(*_bf_args, **_bf_kwargs)
_bf_friction_post_account_sessions.blobfish_original = _bf_orig_post_account_sessions
post_account_sessions = _bf_friction_post_account_sessions

def post_marketing_contacts_batch(db_path='state.db', **kwargs):
    '''Get Batched Contacts by IDs (POST /marketing/contacts/batch)'''
    _missing = [p for p in ['ids'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _n = cur.execute('SELECT COALESCE(MAX(rowid), 0) + 100 FROM "batches"').fetchone()[0] + 1
        _base = datetime.datetime(2026, 1, 5, 9, 0, 0)
        _ts = (_base + datetime.timedelta(minutes=_n)).strftime('%Y-%m-%dT%H:%M:%SZ')
        _cols = ['"id"']
        _vals = ['batch_%03d' % _n]
        if kwargs.get('ids') is not None:
            _cols.append('"ids"')
            _vals.append(json.dumps(kwargs['ids']) if not isinstance(kwargs['ids'], str) else kwargs['ids'])
        _cols.append('"created_at"')
        _vals.append(_ts)
        _sql = 'INSERT INTO "batches" (' + ', '.join(_cols) + ') VALUES (' + ', '.join(['?'] * len(_vals)) + ')'
        try:
            cur.execute(_sql, _vals)
        except sqlite3.IntegrityError:
            conn.rollback()
            return {'error': 'conflict: duplicate key', 'status': 409}
        conn.commit()
        _row = cur.execute('SELECT * FROM "batches" WHERE "id" = ?', [_vals[0]]).fetchone()
        _out = dict(_row)
        for _jc in ['ids']:
            if isinstance(_out.get(_jc), str) and _out[_jc][:1] in ('[', '{'):
                try:
                    _out[_jc] = json.loads(_out[_jc])
                except Exception:
                    pass
        return _out
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_post_marketing_contacts_batch = post_marketing_contacts_batch
def _bf_friction_post_marketing_contacts_batch(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_post_marketing_contacts_batch(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "post_marketing_contacts_batch|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_post_marketing_contacts_batch(*_bf_args, **_bf_kwargs)
_bf_friction_post_marketing_contacts_batch.blobfish_original = _bf_orig_post_marketing_contacts_batch
post_marketing_contacts_batch = _bf_friction_post_marketing_contacts_batch

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
    return _bf_orig_update_sales_leads_status(*_bf_args, **_bf_kwargs)
_bf_friction_update_sales_leads_status.blobfish_original = _bf_orig_update_sales_leads_status
update_sales_leads_status = _bf_friction_update_sales_leads_status

