"""Executable SALESFORCE tool module

Inspect each function: SQLite helpers are local fixtures; network-backed functions call their declared endpoint.
Tools: core_records_agent, marketing_records_agent, sales_records_agent, sourcing_records_agent, accounts_list, contacts_list, account_get, contact_get, opportunity_get, get_contactdb_segments_segment_id, get_mc_contacts_exports_id, query_sales_leads, lookup_sales_lead_with_employees, lookup_sales_opportunity_with_sales_leads, core_workflow_agent, marketing_workflow_agent, sales_workflow_agent, sourcing_workflow_agent, account_create, contact_create, opportunity_create, post_marketing_contacts_batch, update_sales_leads_status, service_cases_list, service_case_get, service_case_update_status, case_history_list, case_messages_list, issue_taxonomy_list, product_catalog_list, quotes_list, quote_get, quote_lines_list, quote_update_status, customer_profile_get, customer_profiles_list, aggregate_query, lead_create, lead_update_fields, lead_find_duplicates, lead_merge, sequences_list, sequence_steps_list, sequence_enrollments_list, sequence_enroll_lead, sequence_enrollment_update, email_threads_list, email_messages_list, email_thread_classify, rep_quotas_list, forecast_submissions_list, forecast_submit, account_usage_list, account_health_list, account_health_update, campaign_touches_list, signature_envelopes_list, signature_envelope_create, signature_envelope_update, lead_merge_log_list, quote_delete, contact_merge, account_merge, crm_followup_create, account_tiers_list, approval_matrix_list, product_regulatory_list, activities_list, activity_get, activity_create, activity_update, activity_delete, pipelines_list, pipeline_get, pipeline_create, pipeline_update, pipeline_delete, stages_list, stage_get, stage_create, stage_update, stage_delete, meetings_list, meeting_get, meeting_create, meeting_update, meeting_delete, meetings_search, notes_list, note_get, note_create, note_update, note_delete, notes_search, custom_fields_list, custom_field_create, custom_field_update, custom_field_delete, contact_update, task_update, tasks_search, leads_list, email_message_update, email_message_delete, email_messages_search, sequence_create, sequence_get, sequence_delete, quota_get, lead_convert, opportunity_convert_to_order, email_send, account_delete, contact_delete, lead_delete, opportunity_delete, task_delete
Tables: accept_all, account_tiering_standard, activity_logging_standards, attribution, case_management_sla, coaching_cadence, compliance_review_checklist, conversation_intelligence_standards, cpq_discount_policy, currency_handling, data_quality_rules, deal_desk_charter, disposition_codes, finance_approval_thresholds, forecast_methodology, fy2026_list_prices, handoff_to_ae, inbound_routing_matrix, lead_management_sop, lead_scoring_policy, meddic_scorecard, meeting_scheduling_sla, meeting_types_and_durations, mql_definition, opportunity_stage_gates, order_activation_runbook, renewal_playbook, risky, routing_decision_table, sal_gate, sequence_design_rules, snippets, snippets_and_retention, suppression_and_kpis, talk_ratio, territory, tracker_keywords, visitor_identification, volume_bands, web_form_definitions, all_segments_responses, api_keys, automations_link_stats_responses, automations_responses, batches, blocks, bounces, campaigns, category_stats, certificates, click_trackings, company_marketing_handoffs, contact_exports, contactdb_segments, marketing_campaigns, marketing_content_assets, singlesends, suppression_groups, accounts, cases, company_sales_handoffs, contacts, opportunities, sales_leads, sales_opportunities, tasks, company_sourcing_handoffs, customers, journal_entries, purchase_orders, sourcing_purchase_orders, sourcing_vendors, vendors, employees, service_cases, case_history, case_messages, issue_taxonomy, product_catalog_items, sales_quotes, sales_quote_lines, customer_profiles, support_tickets, lead_merge_log, outreach_sequences, outreach_sequence_steps, outreach_enrollments, email_threads, email_messages, rep_quotas, forecast_submissions, account_usage, account_health, campaign_touches, signature_envelopes, account_tiers, deal_desk_approval_matrix, product_regulatory_flags, crm_activities, crm_pipelines, crm_pipeline_stages, crm_meetings, crm_notes, crm_custom_fields, erp_sales_orders
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

def service_cases_list(db_path='state.db', **kwargs):
    '''List service cases, optionally filtered by status, issue type, region, product, owner or account (GET /services/data/v62.0/query?q=SELECT+FROM+Case).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('status') is not None:
            _where.append('"status" = ?')
            _args.append(str(kwargs['status']))
        if kwargs.get('issue_type') is not None:
            _where.append('"issue_type" = ?')
            _args.append(str(kwargs['issue_type']))
        if kwargs.get('region') is not None:
            _where.append('"region" = ?')
            _args.append(str(kwargs['region']))
        if kwargs.get('product_code') is not None:
            _where.append('"product_code" = ?')
            _args.append(str(kwargs['product_code']))
        if kwargs.get('owner_employee_id') is not None:
            _where.append('"owner_employee_id" = ?')
            _args.append(str(kwargs['owner_employee_id']))
        if kwargs.get('account_id') is not None:
            _where.append('"account_id" = ?')
            _args.append(str(kwargs['account_id']))
        if kwargs.get('priority') is not None:
            _where.append('"priority" = ?')
            _args.append(str(kwargs['priority']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "service_cases"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_service_cases_list = service_cases_list
def _bf_friction_service_cases_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_service_cases_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "service_cases_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_service_cases_list(*_bf_args, **_bf_kwargs)
_bf_friction_service_cases_list.blobfish_original = _bf_orig_service_cases_list
service_cases_list = _bf_friction_service_cases_list

def service_case_get(db_path='state.db', **kwargs):
    '''Retrieve one service case by id (GET /services/data/v62.0/sobjects/Case/{id}).'''
    _missing = [p for p in ['case_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "service_cases" WHERE "id" = ?', [str(kwargs['case_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'service_case not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _r = dict(_row)
        _r['attributes'] = {'type': 'service_case', 'url': '/services/data/v62.0/sobjects/service_case/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_service_case_get = service_case_get
def _bf_friction_service_case_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_service_case_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "service_case_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_service_case_get(*_bf_args, **_bf_kwargs)
_bf_friction_service_case_get.blobfish_original = _bf_orig_service_case_get
service_case_get = _bf_friction_service_case_get

def service_case_update_status(db_path='state.db', **kwargs):
    '''Update a service case's status, priority or owner (PATCH /services/data/v62.0/sobjects/Case/{id}).'''
    _missing = [p for p in ['case_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "service_cases" WHERE "id" = ?', [str(kwargs['case_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'service_case not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _sets, _args = [], []
        if kwargs.get('status') is not None:
            _sets.append('"status" = ?')
            _v = kwargs['status']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('priority') is not None:
            _sets.append('"priority" = ?')
            _v = kwargs['priority']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('owner_employee_id') is not None:
            _sets.append('"owner_employee_id" = ?')
            _v = kwargs['owner_employee_id']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "service_cases" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['case_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "service_cases" WHERE "id" = ?', [str(kwargs['case_id'])]).fetchone()
        _r = dict(_row)
        _r['attributes'] = {'type': 'service_case', 'url': '/services/data/v62.0/sobjects/service_case/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_service_case_update_status = service_case_update_status
def _bf_friction_service_case_update_status(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_service_case_update_status(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "service_case_update_status|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_service_case_update_status(*_bf_args, **_bf_kwargs)
_bf_friction_service_case_update_status.blobfish_original = _bf_orig_service_case_update_status
service_case_update_status = _bf_friction_service_case_update_status

def case_history_list(db_path='state.db', **kwargs):
    '''List case field-history rows, including ownership transfers (GET /services/data/v62.0/query?q=SELECT+FROM+CaseHistory).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('case_id') is not None:
            _where.append('"case_id" = ?')
            _args.append(str(kwargs['case_id']))
        if kwargs.get('field_name') is not None:
            _where.append('"field_name" = ?')
            _args.append(str(kwargs['field_name']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "case_history"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_case_history_list = case_history_list
def _bf_friction_case_history_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_case_history_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "case_history_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_case_history_list(*_bf_args, **_bf_kwargs)
_bf_friction_case_history_list.blobfish_original = _bf_orig_case_history_list
case_history_list = _bf_friction_case_history_list

def case_messages_list(db_path='state.db', **kwargs):
    '''List the chat transcript messages attached to a case (GET /services/data/v62.0/query?q=SELECT+FROM+CaseComment).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('case_id') is not None:
            _where.append('"case_id" = ?')
            _args.append(str(kwargs['case_id']))
        if kwargs.get('speaker') is not None:
            _where.append('"speaker" = ?')
            _args.append(str(kwargs['speaker']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "case_messages"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_case_messages_list = case_messages_list
def _bf_friction_case_messages_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_case_messages_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "case_messages_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_case_messages_list(*_bf_args, **_bf_kwargs)
_bf_friction_case_messages_list.blobfish_original = _bf_orig_case_messages_list
case_messages_list = _bf_friction_case_messages_list

def issue_taxonomy_list(db_path='state.db', **kwargs):
    '''List the controlled issue-type vocabulary (GET /services/data/v62.0/query?q=SELECT+FROM+IssueType__c).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('category') is not None:
            _where.append('"category" = ?')
            _args.append(str(kwargs['category']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "issue_taxonomy"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_issue_taxonomy_list = issue_taxonomy_list
def _bf_friction_issue_taxonomy_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_issue_taxonomy_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "issue_taxonomy_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_issue_taxonomy_list(*_bf_args, **_bf_kwargs)
_bf_friction_issue_taxonomy_list.blobfish_original = _bf_orig_issue_taxonomy_list
issue_taxonomy_list = _bf_friction_issue_taxonomy_list

def product_catalog_list(db_path='state.db', **kwargs):
    '''List catalog products with list prices (GET /services/data/v62.0/query?q=SELECT+FROM+Product2).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('family') is not None:
            _where.append('"family" = ?')
            _args.append(str(kwargs['family']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "product_catalog_items"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_product_catalog_list = product_catalog_list
def _bf_friction_product_catalog_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_product_catalog_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "product_catalog_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_product_catalog_list(*_bf_args, **_bf_kwargs)
_bf_friction_product_catalog_list.blobfish_original = _bf_orig_product_catalog_list
product_catalog_list = _bf_friction_product_catalog_list

def quotes_list(db_path='state.db', **kwargs):
    '''List quotes, optionally by account, opportunity or approval status (GET /services/data/v62.0/query?q=SELECT+FROM+Quote).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('account_id') is not None:
            _where.append('"account_id" = ?')
            _args.append(str(kwargs['account_id']))
        if kwargs.get('opportunity_id') is not None:
            _where.append('"opportunity_id" = ?')
            _args.append(str(kwargs['opportunity_id']))
        if kwargs.get('status') is not None:
            _where.append('"status" = ?')
            _args.append(str(kwargs['status']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "sales_quotes"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_quotes_list = quotes_list
def _bf_friction_quotes_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_quotes_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "quotes_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_quotes_list(*_bf_args, **_bf_kwargs)
_bf_friction_quotes_list.blobfish_original = _bf_orig_quotes_list
quotes_list = _bf_friction_quotes_list

def quote_get(db_path='state.db', **kwargs):
    '''Retrieve one quote by id (GET /services/data/v62.0/sobjects/Quote/{id}).'''
    _missing = [p for p in ['quote_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "sales_quotes" WHERE "id" = ?', [str(kwargs['quote_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'sales_quote not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _r = dict(_row)
        _r['attributes'] = {'type': 'sales_quote', 'url': '/services/data/v62.0/sobjects/sales_quote/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_quote_get = quote_get
def _bf_friction_quote_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_quote_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "quote_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_quote_get(*_bf_args, **_bf_kwargs)
_bf_friction_quote_get.blobfish_original = _bf_orig_quote_get
quote_get = _bf_friction_quote_get

def quote_lines_list(db_path='state.db', **kwargs):
    '''List the line items on a quote (GET /services/data/v62.0/query?q=SELECT+FROM+QuoteLineItem).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('quote_id') is not None:
            _where.append('"quote_id" = ?')
            _args.append(str(kwargs['quote_id']))
        if kwargs.get('product_code') is not None:
            _where.append('"product_code" = ?')
            _args.append(str(kwargs['product_code']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "sales_quote_lines"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_quote_lines_list = quote_lines_list
def _bf_friction_quote_lines_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_quote_lines_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "quote_lines_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_quote_lines_list(*_bf_args, **_bf_kwargs)
_bf_friction_quote_lines_list.blobfish_original = _bf_orig_quote_lines_list
quote_lines_list = _bf_friction_quote_lines_list

def quote_update_status(db_path='state.db', **kwargs):
    '''Update a quote's approval status or discount (PATCH /services/data/v62.0/sobjects/Quote/{id}).'''
    _missing = [p for p in ['quote_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "sales_quotes" WHERE "id" = ?', [str(kwargs['quote_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'sales_quote not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _sets, _args = [], []
        if kwargs.get('status') is not None:
            _sets.append('"status" = ?')
            _v = kwargs['status']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('discount_pct') is not None:
            _sets.append('"discount_pct" = ?')
            _v = kwargs['discount_pct']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "sales_quotes" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['quote_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "sales_quotes" WHERE "id" = ?', [str(kwargs['quote_id'])]).fetchone()
        _r = dict(_row)
        _r['attributes'] = {'type': 'sales_quote', 'url': '/services/data/v62.0/sobjects/sales_quote/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_quote_update_status = quote_update_status
def _bf_friction_quote_update_status(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_quote_update_status(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "quote_update_status|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_quote_update_status(*_bf_args, **_bf_kwargs)
_bf_friction_quote_update_status.blobfish_original = _bf_orig_quote_update_status
quote_update_status = _bf_friction_quote_update_status

def customer_profile_get(db_path='state.db', **kwargs):
    '''Retrieve a customer profile record, including PII and internal-only notes (GET /services/data/v62.0/sobjects/Account/{id}).'''
    _missing = [p for p in ['profile_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "customer_profiles" WHERE "id" = ?', [str(kwargs['profile_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'customer_profile not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _r = dict(_row)
        _r['attributes'] = {'type': 'customer_profile', 'url': '/services/data/v62.0/sobjects/customer_profile/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_customer_profile_get = customer_profile_get
def _bf_friction_customer_profile_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_customer_profile_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "customer_profile_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_customer_profile_get(*_bf_args, **_bf_kwargs)
_bf_friction_customer_profile_get.blobfish_original = _bf_orig_customer_profile_get
customer_profile_get = _bf_friction_customer_profile_get

def customer_profiles_list(db_path='state.db', **kwargs):
    '''List customer profile records (GET /services/data/v62.0/query?q=SELECT+FROM+Account).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('account_id') is not None:
            _where.append('"account_id" = ?')
            _args.append(str(kwargs['account_id']))
        if kwargs.get('region') is not None:
            _where.append('"region" = ?')
            _args.append(str(kwargs['region']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "customer_profiles"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_customer_profiles_list = customer_profiles_list
def _bf_friction_customer_profiles_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_customer_profiles_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "customer_profiles_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_customer_profiles_list(*_bf_args, **_bf_kwargs)
_bf_friction_customer_profiles_list.blobfish_original = _bf_orig_customer_profiles_list
customer_profiles_list = _bf_friction_customer_profiles_list


def aggregate_query(db_path='state.db', **kwargs):
    '''Run a SOQL-style aggregate over one object: COUNT/SUM/AVG/MIN/MAX with an
    optional GROUP BY and equality filter (GET /services/data/v62.0/query?q=SELECT+COUNT(Id)+FROM+X+GROUP+BY+Y).'''
    import sqlite3
    sobject = kwargs.get('sobject')
    func = str(kwargs.get('function') or 'COUNT').upper()
    if not sobject:
        return [{'message': 'missing required parameters: sobject', 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    if func not in ('COUNT', 'SUM', 'AVG', 'MIN', 'MAX'):
        return [{'message': 'function must be one of COUNT, SUM, AVG, MIN, MAX', 'errorCode': 'INVALID_TYPE'}]
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        names = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]
        if sobject not in names:
            return [{'message': "sObject type '" + str(sobject) + "' is not supported",
                     'errorCode': 'INVALID_TYPE'}]
        cols = [r[1] for r in conn.execute('PRAGMA table_info("' + sobject + '")').fetchall()]
        field = kwargs.get('field')
        group_by = kwargs.get('group_by')
        bucket = str(kwargs.get('group_by_function') or '').upper()
        where_field = kwargs.get('where_field')
        for label, ident in (('field', field), ('group_by', group_by), ('where_field', where_field)):
            if ident is not None and ident not in cols:
                return [{'message': "No such column '" + str(ident) + "' on entity '" + str(sobject) + "'",
                         'errorCode': 'INVALID_FIELD'}]
        if func != 'COUNT' and not field:
            return [{'message': func + ' requires a numeric field', 'errorCode': 'REQUIRED_FIELD_MISSING'}]
        expr = 'COUNT(*)' if func == 'COUNT' else func + '("' + field + '")'
        # SOQL date functions: bucket a timestamp column instead of grouping on
        # the raw value (CALENDAR_MONTH -> YYYY-MM, CALENDAR_YEAR -> YYYY, DAY_ONLY -> YYYY-MM-DD)
        _widths = {'CALENDAR_MONTH': 7, 'CALENDAR_YEAR': 4, 'DAY_ONLY': 10}
        if bucket and bucket not in _widths:
            return [{'message': 'group_by_function must be CALENDAR_MONTH, CALENDAR_YEAR or DAY_ONLY',
                     'errorCode': 'INVALID_TYPE'}]
        if group_by:
            group_expr = ('substr("' + group_by + '", 1, ' + str(_widths[bucket]) + ')') if bucket else ('"' + group_by + '"')
        else:
            group_expr = None
        sql = 'SELECT ' + ((group_expr + ' AS grouping, ') if group_expr else '') + expr + ' AS value FROM "' + sobject + '"'
        args = []
        if where_field is not None and kwargs.get('where_value') is not None:
            sql += ' WHERE "' + where_field + '" = ?'
            args.append(str(kwargs['where_value']))
        if group_expr:
            sql += ' GROUP BY ' + group_expr
        order = str(kwargs.get('order_by') or 'value').lower()
        direction = 'ASC' if str(kwargs.get('direction') or 'desc').lower() == 'asc' else 'DESC'
        sql += ' ORDER BY ' + ('grouping' if (order == 'grouping' and group_by) else 'value') + ' ' + direction
        limit = int(kwargs.get('limit') or 200)
        sql += ' LIMIT ?'
        args.append(limit)
        rows = []
        for r in conn.execute(sql, args).fetchall():
            d = dict(r)
            if isinstance(d.get('value'), float):
                d['value'] = round(d['value'], 2)
            rows.append(d)
        return {'totalSize': len(rows), 'done': True, 'records': rows}
    finally:
        conn.close()

_env_orig_aggregate_query = aggregate_query
def _env_aggregate_query(db_path='state.db', **kwargs):
    _r = _env_orig_aggregate_query(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
    if 'error' in _r and _r.get('status') == 400:
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    return _r
aggregate_query = _env_aggregate_query

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_aggregate_query = aggregate_query
def _bf_friction_aggregate_query(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_aggregate_query(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "aggregate_query|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_aggregate_query(*_bf_args, **_bf_kwargs)
_bf_friction_aggregate_query.blobfish_original = _bf_orig_aggregate_query
aggregate_query = _bf_friction_aggregate_query

def lead_create(db_path='state.db', **kwargs):
    '''Create a lead from an inbound form or list import (POST /services/data/v62.0/sobjects/Lead).'''
    _missing = [p for p in ['company_name', 'contact_name'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "sales_leads"').fetchone()[0] + 1
        _id = _n
        while cur.execute('SELECT 1 FROM "sales_leads" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = _n
        _cols, _vals = ['id'], [_id]
        if kwargs.get('company_name') is not None:
            _cols.append('company_name')
            _v = kwargs['company_name']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('contact_name') is not None:
            _cols.append('contact_name')
            _v = kwargs['contact_name']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('source') is not None:
            _cols.append('source')
            _v = kwargs['source']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('estimated_value') is not None:
            _cols.append('estimated_value')
            _v = kwargs['estimated_value']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('owner_employee_id') is not None:
            _cols.append('owner_employee_id')
            _v = kwargs['owner_employee_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('status') is not None:
            _cols.append('status')
            _v = kwargs['status']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'status' not in _cols:
            _cols.append('status')
            _vals.append('new')
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "sales_leads" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "sales_leads" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['attributes'] = {'type': 'sales_lead', 'url': '/services/data/v62.0/sobjects/sales_lead/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_lead_create = lead_create
def _bf_friction_lead_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_lead_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "lead_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_lead_create(*_bf_args, **_bf_kwargs)
_bf_friction_lead_create.blobfish_original = _bf_orig_lead_create
lead_create = _bf_friction_lead_create

def lead_update_fields(db_path='state.db', **kwargs):
    '''Update lead fields including owner assignment — routing, enrichment and recycling (PATCH /services/data/v62.0/sobjects/Lead/{id}).'''
    _missing = [p for p in ['lead_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "sales_leads" WHERE "id" = ?', [str(kwargs['lead_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'sales_lead not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _sets, _args = [], []
        if kwargs.get('company_name') is not None:
            _sets.append('"company_name" = ?')
            _v = kwargs['company_name']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('contact_name') is not None:
            _sets.append('"contact_name" = ?')
            _v = kwargs['contact_name']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('source') is not None:
            _sets.append('"source" = ?')
            _v = kwargs['source']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('estimated_value') is not None:
            _sets.append('"estimated_value" = ?')
            _v = kwargs['estimated_value']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('owner_employee_id') is not None:
            _sets.append('"owner_employee_id" = ?')
            _v = kwargs['owner_employee_id']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('status') is not None:
            _sets.append('"status" = ?')
            _v = kwargs['status']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "sales_leads" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['lead_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "sales_leads" WHERE "id" = ?', [str(kwargs['lead_id'])]).fetchone()
        _r = dict(_row)
        _r['attributes'] = {'type': 'sales_lead', 'url': '/services/data/v62.0/sobjects/sales_lead/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_lead_update_fields = lead_update_fields
def _bf_friction_lead_update_fields(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_lead_update_fields(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "lead_update_fields|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_lead_update_fields(*_bf_args, **_bf_kwargs)
_bf_friction_lead_update_fields.blobfish_original = _bf_orig_lead_update_fields
lead_update_fields = _bf_friction_lead_update_fields


def lead_find_duplicates(db_path='state.db', **kwargs):
    '''Find candidate duplicate leads by matching company name or contact name
    (POST /services/data/v62.0/composite/sobjects/Lead/duplicates).'''
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        lead_id = kwargs.get('lead_id')
        if lead_id:
            base = conn.execute('SELECT * FROM sales_leads WHERE id = ?', (str(lead_id),)).fetchone()
            if base is None:
                return [{'message': 'lead not found', 'errorCode': 'NOT_FOUND'}]
            base = dict(base)
            rows = [dict(r) for r in conn.execute(
                'SELECT * FROM sales_leads WHERE id != ? AND (company_name = ? OR contact_name = ?) '
                'ORDER BY id LIMIT ?',
                (str(lead_id), base.get('company_name'), base.get('contact_name'),
                 int(kwargs.get('limit') or 30))).fetchall()]
            return {'totalSize': len(rows), 'done': True, 'records': rows,
                    'matchedOn': ['company_name', 'contact_name']}
        # no anchor lead: report every company_name with more than one lead
        rows = [dict(r) for r in conn.execute(
            'SELECT company_name, COUNT(*) AS lead_count, MIN(id) AS master_candidate '
            'FROM sales_leads GROUP BY company_name HAVING COUNT(*) > 1 '
            'ORDER BY lead_count DESC, company_name LIMIT ?',
            (int(kwargs.get('limit') or 30),)).fetchall()]
        return {'totalSize': len(rows), 'done': True, 'records': rows, 'matchedOn': ['company_name']}
    finally:
        conn.close()

_env_orig_lead_find_duplicates = lead_find_duplicates
def _env_lead_find_duplicates(db_path='state.db', **kwargs):
    _r = _env_orig_lead_find_duplicates(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
    if 'error' in _r and _r.get('status') == 400:
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    return _r
lead_find_duplicates = _env_lead_find_duplicates

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_lead_find_duplicates = lead_find_duplicates
def _bf_friction_lead_find_duplicates(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_lead_find_duplicates(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "lead_find_duplicates|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_lead_find_duplicates(*_bf_args, **_bf_kwargs)
_bf_friction_lead_find_duplicates.blobfish_original = _bf_orig_lead_find_duplicates
lead_find_duplicates = _bf_friction_lead_find_duplicates


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

def sequences_list(db_path='state.db', **kwargs):
    '''List outbound sequences (GET /api/v2/sequences).'''
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
        _q = 'SELECT * FROM "outreach_sequences"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_sequences_list = sequences_list
def _bf_friction_sequences_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_sequences_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "sequences_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_sequences_list(*_bf_args, **_bf_kwargs)
_bf_friction_sequences_list.blobfish_original = _bf_orig_sequences_list
sequences_list = _bf_friction_sequences_list

def sequence_steps_list(db_path='state.db', **kwargs):
    '''List the ordered steps of a sequence with delays and A/B variants (GET /api/v2/sequenceSteps).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('sequence_id') is not None:
            _where.append('"sequence_id" = ?')
            _args.append(str(kwargs['sequence_id']))
        if kwargs.get('channel') is not None:
            _where.append('"channel" = ?')
            _args.append(str(kwargs['channel']))
        if kwargs.get('variant') is not None:
            _where.append('"variant" = ?')
            _args.append(str(kwargs['variant']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "outreach_sequence_steps"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_sequence_steps_list = sequence_steps_list
def _bf_friction_sequence_steps_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_sequence_steps_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "sequence_steps_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_sequence_steps_list(*_bf_args, **_bf_kwargs)
_bf_friction_sequence_steps_list.blobfish_original = _bf_orig_sequence_steps_list
sequence_steps_list = _bf_friction_sequence_steps_list

def sequence_enrollments_list(db_path='state.db', **kwargs):
    '''List per-lead sequence enrollments and their current step (GET /api/v2/sequenceStates).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('sequence_id') is not None:
            _where.append('"sequence_id" = ?')
            _args.append(str(kwargs['sequence_id']))
        if kwargs.get('status') is not None:
            _where.append('"status" = ?')
            _args.append(str(kwargs['status']))
        if kwargs.get('lead_id') is not None:
            _where.append('"lead_id" = ?')
            _args.append(str(kwargs['lead_id']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "outreach_enrollments"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_sequence_enrollments_list = sequence_enrollments_list
def _bf_friction_sequence_enrollments_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_sequence_enrollments_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "sequence_enrollments_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_sequence_enrollments_list(*_bf_args, **_bf_kwargs)
_bf_friction_sequence_enrollments_list.blobfish_original = _bf_orig_sequence_enrollments_list
sequence_enrollments_list = _bf_friction_sequence_enrollments_list

def sequence_enroll_lead(db_path='state.db', **kwargs):
    '''Enroll a lead into a sequence at a given step (POST /api/v2/sequenceStates).'''
    _missing = [p for p in ['sequence_id', 'lead_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "outreach_enrollments"').fetchone()[0] + 1
        _id = 'enr_' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "outreach_enrollments" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'enr_' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('sequence_id') is not None:
            _cols.append('sequence_id')
            _v = kwargs['sequence_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('lead_id') is not None:
            _cols.append('lead_id')
            _v = kwargs['lead_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('current_step') is not None:
            _cols.append('current_step')
            _v = kwargs['current_step']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('status') is not None:
            _cols.append('status')
            _v = kwargs['status']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'status' not in _cols:
            _cols.append('status')
            _vals.append('active')
        if 'current_step' not in _cols:
            _cols.append('current_step')
            _vals.append(1)
        cur.execute('INSERT INTO "outreach_enrollments" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "outreach_enrollments" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['attributes'] = {'type': 'outreach_enrollment', 'url': '/services/data/v62.0/sobjects/outreach_enrollment/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_sequence_enroll_lead = sequence_enroll_lead
def _bf_friction_sequence_enroll_lead(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_sequence_enroll_lead(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "sequence_enroll_lead|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_sequence_enroll_lead(*_bf_args, **_bf_kwargs)
_bf_friction_sequence_enroll_lead.blobfish_original = _bf_orig_sequence_enroll_lead
sequence_enroll_lead = _bf_friction_sequence_enroll_lead

def sequence_enrollment_update(db_path='state.db', **kwargs):
    '''Advance or stop a lead's sequence enrollment (PUT /api/v2/sequenceStates/{id}).'''
    _missing = [p for p in ['enrollment_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "outreach_enrollments" WHERE "id" = ?', [str(kwargs['enrollment_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'outreach_enrollment not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _sets, _args = [], []
        if kwargs.get('status') is not None:
            _sets.append('"status" = ?')
            _v = kwargs['status']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('current_step') is not None:
            _sets.append('"current_step" = ?')
            _v = kwargs['current_step']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "outreach_enrollments" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['enrollment_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "outreach_enrollments" WHERE "id" = ?', [str(kwargs['enrollment_id'])]).fetchone()
        _r = dict(_row)
        _r['attributes'] = {'type': 'outreach_enrollment', 'url': '/services/data/v62.0/sobjects/outreach_enrollment/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_sequence_enrollment_update = sequence_enrollment_update
def _bf_friction_sequence_enrollment_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_sequence_enrollment_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "sequence_enrollment_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_sequence_enrollment_update(*_bf_args, **_bf_kwargs)
_bf_friction_sequence_enrollment_update.blobfish_original = _bf_orig_sequence_enrollment_update
sequence_enrollment_update = _bf_friction_sequence_enrollment_update

def email_threads_list(db_path='state.db', **kwargs):
    '''List inbound email threads awaiting triage (GET /gmail/v1/users/me/threads).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('status') is not None:
            _where.append('"status" = ?')
            _args.append(str(kwargs['status']))
        if kwargs.get('intent_label') is not None:
            _where.append('"intent_label" = ?')
            _args.append(str(kwargs['intent_label']))
        if kwargs.get('account_id') is not None:
            _where.append('"account_id" = ?')
            _args.append(str(kwargs['account_id']))
        if kwargs.get('assigned_employee_id') is not None:
            _where.append('"assigned_employee_id" = ?')
            _args.append(str(kwargs['assigned_employee_id']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "email_threads"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_email_threads_list = email_threads_list
def _bf_friction_email_threads_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_email_threads_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "email_threads_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_email_threads_list(*_bf_args, **_bf_kwargs)
_bf_friction_email_threads_list.blobfish_original = _bf_orig_email_threads_list
email_threads_list = _bf_friction_email_threads_list

def email_messages_list(db_path='state.db', **kwargs):
    '''List the messages inside an email thread (GET /gmail/v1/users/me/messages).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('thread_id') is not None:
            _where.append('"thread_id" = ?')
            _args.append(str(kwargs['thread_id']))
        if kwargs.get('direction') is not None:
            _where.append('"direction" = ?')
            _args.append(str(kwargs['direction']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "email_messages"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_email_messages_list = email_messages_list
def _bf_friction_email_messages_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_email_messages_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "email_messages_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_email_messages_list(*_bf_args, **_bf_kwargs)
_bf_friction_email_messages_list.blobfish_original = _bf_orig_email_messages_list
email_messages_list = _bf_friction_email_messages_list

def email_thread_classify(db_path='state.db', **kwargs):
    '''Apply a reply-intent label, mark a thread read, or route it to an owner (POST /gmail/v1/users/me/threads/{id}/modify).'''
    _missing = [p for p in ['thread_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "email_threads" WHERE "id" = ?', [str(kwargs['thread_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'email_thread not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _sets, _args = [], []
        if kwargs.get('intent_label') is not None:
            _sets.append('"intent_label" = ?')
            _v = kwargs['intent_label']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('status') is not None:
            _sets.append('"status" = ?')
            _v = kwargs['status']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('assigned_employee_id') is not None:
            _sets.append('"assigned_employee_id" = ?')
            _v = kwargs['assigned_employee_id']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "email_threads" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['thread_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "email_threads" WHERE "id" = ?', [str(kwargs['thread_id'])]).fetchone()
        _r = dict(_row)
        _r['attributes'] = {'type': 'email_thread', 'url': '/services/data/v62.0/sobjects/email_thread/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_email_thread_classify = email_thread_classify
def _bf_friction_email_thread_classify(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_email_thread_classify(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "email_thread_classify|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_email_thread_classify(*_bf_args, **_bf_kwargs)
_bf_friction_email_thread_classify.blobfish_original = _bf_orig_email_thread_classify
email_thread_classify = _bf_friction_email_thread_classify

def rep_quotas_list(db_path='state.db', **kwargs):
    '''List per-rep quota and attainment by period (GET /services/data/v62.0/query?q=SELECT+FROM+Quota).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('employee_id') is not None:
            _where.append('"employee_id" = ?')
            _args.append(str(kwargs['employee_id']))
        if kwargs.get('period') is not None:
            _where.append('"period" = ?')
            _args.append(str(kwargs['period']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "rep_quotas"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_rep_quotas_list = rep_quotas_list
def _bf_friction_rep_quotas_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_rep_quotas_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "rep_quotas_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_rep_quotas_list(*_bf_args, **_bf_kwargs)
_bf_friction_rep_quotas_list.blobfish_original = _bf_orig_rep_quotas_list
rep_quotas_list = _bf_friction_rep_quotas_list

def forecast_submissions_list(db_path='state.db', **kwargs):
    '''List submitted forecast categories per rep (GET /services/data/v62.0/query?q=SELECT+FROM+ForecastingItem).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('employee_id') is not None:
            _where.append('"employee_id" = ?')
            _args.append(str(kwargs['employee_id']))
        if kwargs.get('period') is not None:
            _where.append('"period" = ?')
            _args.append(str(kwargs['period']))
        if kwargs.get('category') is not None:
            _where.append('"category" = ?')
            _args.append(str(kwargs['category']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "forecast_submissions"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_forecast_submissions_list = forecast_submissions_list
def _bf_friction_forecast_submissions_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_forecast_submissions_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "forecast_submissions_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_forecast_submissions_list(*_bf_args, **_bf_kwargs)
_bf_friction_forecast_submissions_list.blobfish_original = _bf_orig_forecast_submissions_list
forecast_submissions_list = _bf_friction_forecast_submissions_list

def forecast_submit(db_path='state.db', **kwargs):
    '''Submit a forecast number in a category for a rep and period (POST /services/data/v62.0/sobjects/ForecastingItem).'''
    _missing = [p for p in ['employee_id', 'period', 'category', 'amount'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "forecast_submissions"').fetchone()[0] + 1
        _id = 'fc_' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "forecast_submissions" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'fc_' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('employee_id') is not None:
            _cols.append('employee_id')
            _v = kwargs['employee_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('employee_name') is not None:
            _cols.append('employee_name')
            _v = kwargs['employee_name']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('period') is not None:
            _cols.append('period')
            _v = kwargs['period']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('category') is not None:
            _cols.append('category')
            _v = kwargs['category']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('amount') is not None:
            _cols.append('amount')
            _v = kwargs['amount']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('status') is not None:
            _cols.append('status')
            _v = kwargs['status']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'status' not in _cols:
            _cols.append('status')
            _vals.append('submitted')
        cur.execute('INSERT INTO "forecast_submissions" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "forecast_submissions" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['attributes'] = {'type': 'forecast_submission', 'url': '/services/data/v62.0/sobjects/forecast_submission/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_forecast_submit = forecast_submit
def _bf_friction_forecast_submit(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_forecast_submit(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "forecast_submit|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_forecast_submit(*_bf_args, **_bf_kwargs)
_bf_friction_forecast_submit.blobfish_original = _bf_orig_forecast_submit
forecast_submit = _bf_friction_forecast_submit

def account_usage_list(db_path='state.db', **kwargs):
    '''List per-account product usage telemetry (GET /analytics/v1/accounts/usage).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('account_id') is not None:
            _where.append('"account_id" = ?')
            _args.append(str(kwargs['account_id']))
        if kwargs.get('period') is not None:
            _where.append('"period" = ?')
            _args.append(str(kwargs['period']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "account_usage"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_account_usage_list = account_usage_list
def _bf_friction_account_usage_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_account_usage_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "account_usage_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_account_usage_list(*_bf_args, **_bf_kwargs)
_bf_friction_account_usage_list.blobfish_original = _bf_orig_account_usage_list
account_usage_list = _bf_friction_account_usage_list

def account_health_list(db_path='state.db', **kwargs):
    '''List account health scores, bands, renewal dates and primary risks (GET /analytics/v1/accounts/health).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('account_id') is not None:
            _where.append('"account_id" = ?')
            _args.append(str(kwargs['account_id']))
        if kwargs.get('band') is not None:
            _where.append('"band" = ?')
            _args.append(str(kwargs['band']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "account_health"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_account_health_list = account_health_list
def _bf_friction_account_health_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_account_health_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "account_health_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_account_health_list(*_bf_args, **_bf_kwargs)
_bf_friction_account_health_list.blobfish_original = _bf_orig_account_health_list
account_health_list = _bf_friction_account_health_list

def account_health_update(db_path='state.db', **kwargs):
    '''Re-score an account's health after a save play or usage change (PATCH /analytics/v1/accounts/health/{id}).'''
    _missing = [p for p in ['health_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "account_health" WHERE "id" = ?', [str(kwargs['health_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'account_health not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _sets, _args = [], []
        if kwargs.get('score') is not None:
            _sets.append('"score" = ?')
            _v = kwargs['score']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('band') is not None:
            _sets.append('"band" = ?')
            _v = kwargs['band']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('primary_risk') is not None:
            _sets.append('"primary_risk" = ?')
            _v = kwargs['primary_risk']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "account_health" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['health_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "account_health" WHERE "id" = ?', [str(kwargs['health_id'])]).fetchone()
        _r = dict(_row)
        _r['attributes'] = {'type': 'account_health', 'url': '/services/data/v62.0/sobjects/account_health/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_account_health_update = account_health_update
def _bf_friction_account_health_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_account_health_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "account_health_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_account_health_update(*_bf_args, **_bf_kwargs)
_bf_friction_account_health_update.blobfish_original = _bf_orig_account_health_update
account_health_update = _bf_friction_account_health_update

def campaign_touches_list(db_path='state.db', **kwargs):
    '''List campaign touches for multi-touch attribution (GET /services/data/v62.0/query?q=SELECT+FROM+CampaignMember).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('campaign_id') is not None:
            _where.append('"campaign_id" = ?')
            _args.append(str(kwargs['campaign_id']))
        if kwargs.get('lead_id') is not None:
            _where.append('"lead_id" = ?')
            _args.append(str(kwargs['lead_id']))
        if kwargs.get('account_id') is not None:
            _where.append('"account_id" = ?')
            _args.append(str(kwargs['account_id']))
        if kwargs.get('position') is not None:
            _where.append('"position" = ?')
            _args.append(str(kwargs['position']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "campaign_touches"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_campaign_touches_list = campaign_touches_list
def _bf_friction_campaign_touches_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_campaign_touches_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "campaign_touches_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_campaign_touches_list(*_bf_args, **_bf_kwargs)
_bf_friction_campaign_touches_list.blobfish_original = _bf_orig_campaign_touches_list
campaign_touches_list = _bf_friction_campaign_touches_list

def signature_envelopes_list(db_path='state.db', **kwargs):
    '''List e-signature envelopes and their status (GET /restapi/v2.1/accounts/{accountId}/envelopes).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('account_id') is not None:
            _where.append('"account_id" = ?')
            _args.append(str(kwargs['account_id']))
        if kwargs.get('status') is not None:
            _where.append('"status" = ?')
            _args.append(str(kwargs['status']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "signature_envelopes"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_signature_envelopes_list = signature_envelopes_list
def _bf_friction_signature_envelopes_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_signature_envelopes_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "signature_envelopes_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_signature_envelopes_list(*_bf_args, **_bf_kwargs)
_bf_friction_signature_envelopes_list.blobfish_original = _bf_orig_signature_envelopes_list
signature_envelopes_list = _bf_friction_signature_envelopes_list

def signature_envelope_create(db_path='state.db', **kwargs):
    '''Create an e-signature envelope for a document with a signer order (POST /restapi/v2.1/accounts/{accountId}/envelopes).'''
    _missing = [p for p in ['account_id', 'document_title'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "signature_envelopes"').fetchone()[0] + 1
        _id = 'env_' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "signature_envelopes" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'env_' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('account_id') is not None:
            _cols.append('account_id')
            _v = kwargs['account_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('account_name') is not None:
            _cols.append('account_name')
            _v = kwargs['account_name']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('document_title') is not None:
            _cols.append('document_title')
            _v = kwargs['document_title']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('status') is not None:
            _cols.append('status')
            _v = kwargs['status']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('signer_order') is not None:
            _cols.append('signer_order')
            _v = kwargs['signer_order']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'status' not in _cols:
            _cols.append('status')
            _vals.append('draft')
        if 'signer_order' not in _cols:
            _cols.append('signer_order')
            _vals.append('customer_first')
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "signature_envelopes" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "signature_envelopes" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['attributes'] = {'type': 'signature_envelope', 'url': '/services/data/v62.0/sobjects/signature_envelope/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_signature_envelope_create = signature_envelope_create
def _bf_friction_signature_envelope_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_signature_envelope_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "signature_envelope_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_signature_envelope_create(*_bf_args, **_bf_kwargs)
_bf_friction_signature_envelope_create.blobfish_original = _bf_orig_signature_envelope_create
signature_envelope_create = _bf_friction_signature_envelope_create

def signature_envelope_update(db_path='state.db', **kwargs):
    '''Advance an envelope's signature state (PUT /restapi/v2.1/accounts/{accountId}/envelopes/{envelopeId}).'''
    _missing = [p for p in ['envelope_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "signature_envelopes" WHERE "id" = ?', [str(kwargs['envelope_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'signature_envelope not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _sets, _args = [], []
        if kwargs.get('status') is not None:
            _sets.append('"status" = ?')
            _v = kwargs['status']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('customer_signed_at') is not None:
            _sets.append('"customer_signed_at" = ?')
            _v = kwargs['customer_signed_at']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('countersigned_at') is not None:
            _sets.append('"countersigned_at" = ?')
            _v = kwargs['countersigned_at']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "signature_envelopes" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['envelope_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "signature_envelopes" WHERE "id" = ?', [str(kwargs['envelope_id'])]).fetchone()
        _r = dict(_row)
        _r['attributes'] = {'type': 'signature_envelope', 'url': '/services/data/v62.0/sobjects/signature_envelope/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_signature_envelope_update = signature_envelope_update
def _bf_friction_signature_envelope_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_signature_envelope_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "signature_envelope_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_signature_envelope_update(*_bf_args, **_bf_kwargs)
_bf_friction_signature_envelope_update.blobfish_original = _bf_orig_signature_envelope_update
signature_envelope_update = _bf_friction_signature_envelope_update

def lead_merge_log_list(db_path='state.db', **kwargs):
    '''List executed lead merges from the append-only audit trail — survivorship fields filled and children re-parented (GET /services/data/v62.0/query?q=SELECT+FROM+MergeHistory).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('master_lead_id') is not None:
            _where.append('"master_lead_id" = ?')
            _args.append(str(kwargs['master_lead_id']))
        if kwargs.get('duplicate_lead_id') is not None:
            _where.append('"duplicate_lead_id" = ?')
            _args.append(str(kwargs['duplicate_lead_id']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "lead_merge_log"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_lead_merge_log_list = lead_merge_log_list
def _bf_friction_lead_merge_log_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_lead_merge_log_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "lead_merge_log_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_lead_merge_log_list(*_bf_args, **_bf_kwargs)
_bf_friction_lead_merge_log_list.blobfish_original = _bf_orig_lead_merge_log_list
lead_merge_log_list = _bf_friction_lead_merge_log_list

def quote_delete(db_path='state.db', **kwargs):
    """Permanently delete a quote (DELETE /services/data/v62.0/sobjects/Quote/{id}). Irreversible."""
    _missing = [p for p in ['quote_id'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _id = kwargs['quote_id']
        _row = cur.execute('SELECT * FROM "sales_quotes" WHERE "id" = ?', [_id]).fetchone()
        if _row is None:
            return {'error': 'quote not found', 'status': 404}
        _before = dict(_row)
        cur.execute('DELETE FROM "sales_quotes" WHERE "id" = ?', [_id])
        conn.commit()
        return {'deleted': True, 'id': _id, 'object': 'quote', 'record': _before}
    finally:
        conn.close()

def contact_merge(db_path='state.db', **kwargs):
    """Merge a duplicate contact into a surviving contact, backfilling empty fields from the duplicate."""
    _missing = [p for p in ['master_id', 'duplicate_id'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3
    if str(kwargs['master_id']) == str(kwargs['duplicate_id']):
        return {'error': 'cannot merge a record into itself', 'status': 400}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _m = cur.execute('SELECT * FROM "contacts" WHERE "id" = ?', [kwargs['master_id']]).fetchone()
        _d = cur.execute('SELECT * FROM "contacts" WHERE "id" = ?', [kwargs['duplicate_id']]).fetchone()
        if _m is None or _d is None:
            return {'error': 'contact not found', 'status': 404}
        _m, _d = dict(_m), dict(_d)
        _filled = {}
        for _k, _v in _d.items():
            if _k != 'id' and (_m.get(_k) is None or _m.get(_k) == '') and _v not in (None, ''):
                _filled[_k] = _v
        if _filled:
            _sets = ', '.join('"' + c + '" = ?' for c in _filled)
            cur.execute('UPDATE "contacts" SET ' + _sets + ' WHERE "id" = ?',
                        list(_filled.values()) + [kwargs['master_id']])
        cur.execute('DELETE FROM "contacts" WHERE "id" = ?', [kwargs['duplicate_id']])
        conn.commit()
        return {'merged': True, 'survivor': kwargs['master_id'], 'merged_away': kwargs['duplicate_id'],
                'fields_backfilled': list(_filled)}
    finally:
        conn.close()

def account_merge(db_path='state.db', **kwargs):
    """Merge a duplicate account into a surviving account, backfilling empty fields from the duplicate."""
    _missing = [p for p in ['master_id', 'duplicate_id'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3
    if str(kwargs['master_id']) == str(kwargs['duplicate_id']):
        return {'error': 'cannot merge a record into itself', 'status': 400}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _m = cur.execute('SELECT * FROM "accounts" WHERE "id" = ?', [kwargs['master_id']]).fetchone()
        _d = cur.execute('SELECT * FROM "accounts" WHERE "id" = ?', [kwargs['duplicate_id']]).fetchone()
        if _m is None or _d is None:
            return {'error': 'account not found', 'status': 404}
        _m, _d = dict(_m), dict(_d)
        _filled = {}
        for _k, _v in _d.items():
            if _k != 'id' and (_m.get(_k) is None or _m.get(_k) == '') and _v not in (None, ''):
                _filled[_k] = _v
        if _filled:
            _sets = ', '.join('"' + c + '" = ?' for c in _filled)
            cur.execute('UPDATE "accounts" SET ' + _sets + ' WHERE "id" = ?',
                        list(_filled.values()) + [kwargs['master_id']])
        cur.execute('DELETE FROM "accounts" WHERE "id" = ?', [kwargs['duplicate_id']])
        conn.commit()
        return {'merged': True, 'survivor': kwargs['master_id'], 'merged_away': kwargs['duplicate_id'],
                'fields_backfilled': list(_filled)}
    finally:
        conn.close()

def crm_followup_create(db_path='state.db', **kwargs):
    """Create a follow-up task (POST /services/data/v62.0/sobjects/Task)."""
    _missing = [p for p in ['subject'] if kwargs.get(p) is None]
    if _missing:
        return {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
    import sqlite3, datetime
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _cols = [r[1] for r in cur.execute('PRAGMA table_info("tasks")')]
        _vals = {}
        for _k, _v in kwargs.items():
            if _k in _cols and _v is not None:
                _vals[_k] = _v
        if 'created_at' in _cols and 'created_at' not in _vals:
            _vals['created_at'] = datetime.datetime.utcnow().isoformat() + 'Z'
        if 'id' in _cols and 'id' not in _vals:
            _n = cur.execute('SELECT COUNT(*) FROM "tasks"').fetchone()[0]
            _vals['id'] = 'task_' + str(_n + 1).zfill(4)
        _names = ', '.join('"' + c + '"' for c in _vals)
        _marks = ', '.join('?' for _ in _vals)
        cur.execute('INSERT INTO "tasks" (' + _names + ') VALUES (' + _marks + ')', list(_vals.values()))
        conn.commit()
        return {'created': True, 'object': 'task', 'record': _vals}
    finally:
        conn.close()

def account_tiers_list(db_path='state.db', **kwargs):
    """List account tiers with the standing discount authority and new-client flag for each account."""
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _sql = 'SELECT * FROM "account_tiers"'
        _args = []
        _where = []
        for _k in ['account_id', 'account_name', 'tier']:
            if kwargs.get(_k) is not None:
                _where.append('"' + _k + '" = ?')
                _args.append(kwargs[_k])
        if _where:
            _sql += ' WHERE ' + ' AND '.join(_where)
        _limit = int(kwargs.get('limit') or 50)
        _sql += ' LIMIT ' + str(max(1, min(200, _limit)))
        return [dict(r) for r in cur.execute(_sql, _args)]
    finally:
        conn.close()

def approval_matrix_list(db_path='state.db', **kwargs):
    """List the standing quote approval matrix: which condition routes to which approver, in what order."""
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _sql = 'SELECT * FROM "deal_desk_approval_matrix"'
        _args = []
        _where = []
        for _k in ['rule_id', 'approver_role']:
            if kwargs.get(_k) is not None:
                _where.append('"' + _k + '" = ?')
                _args.append(kwargs[_k])
        if _where:
            _sql += ' WHERE ' + ' AND '.join(_where)
        _limit = int(kwargs.get('limit') or 50)
        _sql += ' LIMIT ' + str(max(1, min(200, _limit)))
        return [dict(r) for r in cur.execute(_sql, _args)]
    finally:
        conn.close()

def product_regulatory_list(db_path='state.db', **kwargs):
    """List products with their regulatory classification, used to decide whether Compliance review applies."""
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _sql = 'SELECT * FROM "product_regulatory_flags"'
        _args = []
        _where = []
        for _k in ['product_code', 'is_regulated']:
            if kwargs.get(_k) is not None:
                _where.append('"' + _k + '" = ?')
                _args.append(kwargs[_k])
        if _where:
            _sql += ' WHERE ' + ' AND '.join(_where)
        _limit = int(kwargs.get('limit') or 50)
        _sql += ' LIMIT ' + str(max(1, min(200, _limit)))
        return [dict(r) for r in cur.execute(_sql, _args)]
    finally:
        conn.close()

def activities_list(db_path='state.db', **kwargs):
    '''List logged activities, newest first (GET /services/data/v60.0/sobjects/Task).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('account_id') is not None:
            _where.append('"account_id" = ?')
            _args.append(str(kwargs['account_id']))
        if kwargs.get('contact_id') is not None:
            _where.append('"contact_id" = ?')
            _args.append(str(kwargs['contact_id']))
        if kwargs.get('activity_type') is not None:
            _where.append('"activity_type" = ?')
            _args.append(str(kwargs['activity_type']))
        if kwargs.get('status') is not None:
            _where.append('"status" = ?')
            _args.append(str(kwargs['status']))
        if kwargs.get('owner_employee_id') is not None:
            _where.append('"owner_employee_id" = ?')
            _args.append(str(kwargs['owner_employee_id']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "crm_activities"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_activities_list = activities_list
def _bf_friction_activities_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_activities_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "activities_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_activities_list(*_bf_args, **_bf_kwargs)
_bf_friction_activities_list.blobfish_original = _bf_orig_activities_list
activities_list = _bf_friction_activities_list

def activity_get(db_path='state.db', **kwargs):
    '''Retrieve a single logged activity by id (GET /services/data/v60.0/sobjects/Task/{id}).'''
    _missing = [p for p in ['activity_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "crm_activities" WHERE "id" = ?', [str(kwargs['activity_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'crm_activitie not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _r = dict(_row)
        _r['attributes'] = {'type': 'crm_activitie', 'url': '/services/data/v62.0/sobjects/crm_activitie/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_activity_get = activity_get
def _bf_friction_activity_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_activity_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "activity_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_activity_get(*_bf_args, **_bf_kwargs)
_bf_friction_activity_get.blobfish_original = _bf_orig_activity_get
activity_get = _bf_friction_activity_get

def activity_create(db_path='state.db', **kwargs):
    '''Log a completed or planned activity against a record (POST /services/data/v60.0/sobjects/Task).'''
    _missing = [p for p in ['activity_type', 'subject'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "crm_activities"').fetchone()[0] + 1
        _id = 'act_' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "crm_activities" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'act_' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('activity_type') is not None:
            _cols.append('activity_type')
            _v = kwargs['activity_type']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('subject') is not None:
            _cols.append('subject')
            _v = kwargs['subject']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('account_id') is not None:
            _cols.append('account_id')
            _v = kwargs['account_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('contact_id') is not None:
            _cols.append('contact_id')
            _v = kwargs['contact_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('opportunity_id') is not None:
            _cols.append('opportunity_id')
            _v = kwargs['opportunity_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('owner_employee_id') is not None:
            _cols.append('owner_employee_id')
            _v = kwargs['owner_employee_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('occurred_at') is not None:
            _cols.append('occurred_at')
            _v = kwargs['occurred_at']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('duration_minutes') is not None:
            _cols.append('duration_minutes')
            _v = kwargs['duration_minutes']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('outcome') is not None:
            _cols.append('outcome')
            _v = kwargs['outcome']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('notes') is not None:
            _cols.append('notes')
            _v = kwargs['notes']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'status' not in _cols:
            _cols.append('status')
            _vals.append('completed')
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "crm_activities" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "crm_activities" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['attributes'] = {'type': 'crm_activitie', 'url': '/services/data/v62.0/sobjects/crm_activitie/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_activity_create = activity_create
def _bf_friction_activity_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_activity_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "activity_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_activity_create(*_bf_args, **_bf_kwargs)
_bf_friction_activity_create.blobfish_original = _bf_orig_activity_create
activity_create = _bf_friction_activity_create

def activity_update(db_path='state.db', **kwargs):
    '''Update fields on a logged activity (PATCH /services/data/v60.0/sobjects/Task/{id}).'''
    _missing = [p for p in ['activity_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "crm_activities" WHERE "id" = ?', [str(kwargs['activity_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'crm_activitie not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _sets, _args = [], []
        if kwargs.get('subject') is not None:
            _sets.append('"subject" = ?')
            _v = kwargs['subject']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('status') is not None:
            _sets.append('"status" = ?')
            _v = kwargs['status']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('outcome') is not None:
            _sets.append('"outcome" = ?')
            _v = kwargs['outcome']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('notes') is not None:
            _sets.append('"notes" = ?')
            _v = kwargs['notes']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('occurred_at') is not None:
            _sets.append('"occurred_at" = ?')
            _v = kwargs['occurred_at']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('duration_minutes') is not None:
            _sets.append('"duration_minutes" = ?')
            _v = kwargs['duration_minutes']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('owner_employee_id') is not None:
            _sets.append('"owner_employee_id" = ?')
            _v = kwargs['owner_employee_id']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "crm_activities" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['activity_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "crm_activities" WHERE "id" = ?', [str(kwargs['activity_id'])]).fetchone()
        _r = dict(_row)
        _r['attributes'] = {'type': 'crm_activitie', 'url': '/services/data/v62.0/sobjects/crm_activitie/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_activity_update = activity_update
def _bf_friction_activity_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_activity_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "activity_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_activity_update(*_bf_args, **_bf_kwargs)
_bf_friction_activity_update.blobfish_original = _bf_orig_activity_update
activity_update = _bf_friction_activity_update

def activity_delete(db_path='state.db', **kwargs):
    '''Delete a logged activity (DELETE /services/data/v60.0/sobjects/Task/{id}).'''
    _missing = [p for p in ['activity_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "crm_activities" WHERE "id" = ?', [str(kwargs['activity_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'crm_activitie not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        cur.execute('DELETE FROM "crm_activities" WHERE "id" = ?', [str(kwargs['activity_id'])])
        conn.commit()
        _r = {'deleted': True, 'id': str(kwargs['activity_id'])}
        return {'id': _r.get('id'), 'success': True, 'errors': []}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_activity_delete = activity_delete
def _bf_friction_activity_delete(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_activity_delete(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "activity_delete|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_activity_delete(*_bf_args, **_bf_kwargs)
_bf_friction_activity_delete.blobfish_original = _bf_orig_activity_delete
activity_delete = _bf_friction_activity_delete

def pipelines_list(db_path='state.db', **kwargs):
    '''List sales pipelines (GET /crm/v3/pipelines/deals).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('object_type') is not None:
            _where.append('"object_type" = ?')
            _args.append(str(kwargs['object_type']))
        if kwargs.get('status') is not None:
            _where.append('"status" = ?')
            _args.append(str(kwargs['status']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "crm_pipelines"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pipelines_list = pipelines_list
def _bf_friction_pipelines_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pipelines_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pipelines_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pipelines_list(*_bf_args, **_bf_kwargs)
_bf_friction_pipelines_list.blobfish_original = _bf_orig_pipelines_list
pipelines_list = _bf_friction_pipelines_list

def pipeline_get(db_path='state.db', **kwargs):
    '''Retrieve one pipeline by id (GET /crm/v3/pipelines/deals/{pipelineId}).'''
    _missing = [p for p in ['pipeline_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "crm_pipelines" WHERE "id" = ?', [str(kwargs['pipeline_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'crm_pipeline not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _r = dict(_row)
        _r['attributes'] = {'type': 'crm_pipeline', 'url': '/services/data/v62.0/sobjects/crm_pipeline/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pipeline_get = pipeline_get
def _bf_friction_pipeline_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pipeline_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pipeline_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pipeline_get(*_bf_args, **_bf_kwargs)
_bf_friction_pipeline_get.blobfish_original = _bf_orig_pipeline_get
pipeline_get = _bf_friction_pipeline_get

def pipeline_create(db_path='state.db', **kwargs):
    '''Create a sales pipeline (POST /crm/v3/pipelines/deals).'''
    _missing = [p for p in ['name'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "crm_pipelines"').fetchone()[0] + 1
        _id = 'pipe_' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "crm_pipelines" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'pipe_' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('name') is not None:
            _cols.append('name')
            _v = kwargs['name']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('object_type') is not None:
            _cols.append('object_type')
            _v = kwargs['object_type']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('is_default') is not None:
            _cols.append('is_default')
            _v = kwargs['is_default']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('stage_count') is not None:
            _cols.append('stage_count')
            _v = kwargs['stage_count']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'status' not in _cols:
            _cols.append('status')
            _vals.append('active')
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "crm_pipelines" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "crm_pipelines" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['attributes'] = {'type': 'crm_pipeline', 'url': '/services/data/v62.0/sobjects/crm_pipeline/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pipeline_create = pipeline_create
def _bf_friction_pipeline_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pipeline_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pipeline_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pipeline_create(*_bf_args, **_bf_kwargs)
_bf_friction_pipeline_create.blobfish_original = _bf_orig_pipeline_create
pipeline_create = _bf_friction_pipeline_create

def pipeline_update(db_path='state.db', **kwargs):
    '''Update a pipeline (PATCH /crm/v3/pipelines/deals/{pipelineId}).'''
    _missing = [p for p in ['pipeline_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "crm_pipelines" WHERE "id" = ?', [str(kwargs['pipeline_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'crm_pipeline not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _sets, _args = [], []
        if kwargs.get('name') is not None:
            _sets.append('"name" = ?')
            _v = kwargs['name']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('object_type') is not None:
            _sets.append('"object_type" = ?')
            _v = kwargs['object_type']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('is_default') is not None:
            _sets.append('"is_default" = ?')
            _v = kwargs['is_default']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('status') is not None:
            _sets.append('"status" = ?')
            _v = kwargs['status']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('stage_count') is not None:
            _sets.append('"stage_count" = ?')
            _v = kwargs['stage_count']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "crm_pipelines" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['pipeline_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "crm_pipelines" WHERE "id" = ?', [str(kwargs['pipeline_id'])]).fetchone()
        _r = dict(_row)
        _r['attributes'] = {'type': 'crm_pipeline', 'url': '/services/data/v62.0/sobjects/crm_pipeline/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pipeline_update = pipeline_update
def _bf_friction_pipeline_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pipeline_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pipeline_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pipeline_update(*_bf_args, **_bf_kwargs)
_bf_friction_pipeline_update.blobfish_original = _bf_orig_pipeline_update
pipeline_update = _bf_friction_pipeline_update

def pipeline_delete(db_path='state.db', **kwargs):
    '''Archive/delete a pipeline (DELETE /crm/v3/pipelines/deals/{pipelineId}).'''
    _missing = [p for p in ['pipeline_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "crm_pipelines" WHERE "id" = ?', [str(kwargs['pipeline_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'crm_pipeline not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        cur.execute('DELETE FROM "crm_pipelines" WHERE "id" = ?', [str(kwargs['pipeline_id'])])
        conn.commit()
        _r = {'deleted': True, 'id': str(kwargs['pipeline_id'])}
        return {'id': _r.get('id'), 'success': True, 'errors': []}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_pipeline_delete = pipeline_delete
def _bf_friction_pipeline_delete(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_pipeline_delete(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "pipeline_delete|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_pipeline_delete(*_bf_args, **_bf_kwargs)
_bf_friction_pipeline_delete.blobfish_original = _bf_orig_pipeline_delete
pipeline_delete = _bf_friction_pipeline_delete

def stages_list(db_path='state.db', **kwargs):
    '''List stages in a pipeline, in display order (GET /crm/v3/pipelines/deals/{pipelineId}/stages).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('pipeline_id') is not None:
            _where.append('"pipeline_id" = ?')
            _args.append(str(kwargs['pipeline_id']))
        if kwargs.get('forecast_category') is not None:
            _where.append('"forecast_category" = ?')
            _args.append(str(kwargs['forecast_category']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "crm_pipeline_stages"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_stages_list = stages_list
def _bf_friction_stages_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_stages_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "stages_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_stages_list(*_bf_args, **_bf_kwargs)
_bf_friction_stages_list.blobfish_original = _bf_orig_stages_list
stages_list = _bf_friction_stages_list

def stage_get(db_path='state.db', **kwargs):
    '''Retrieve a single pipeline stage (GET /crm/v3/pipelines/deals/{pipelineId}/stages/{stageId}).'''
    _missing = [p for p in ['stage_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "crm_pipeline_stages" WHERE "id" = ?', [str(kwargs['stage_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'crm_pipeline_stage not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _r = dict(_row)
        _r['attributes'] = {'type': 'crm_pipeline_stage', 'url': '/services/data/v62.0/sobjects/crm_pipeline_stage/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_stage_get = stage_get
def _bf_friction_stage_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_stage_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "stage_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_stage_get(*_bf_args, **_bf_kwargs)
_bf_friction_stage_get.blobfish_original = _bf_orig_stage_get
stage_get = _bf_friction_stage_get

def stage_create(db_path='state.db', **kwargs):
    '''Add a stage to a pipeline (POST /crm/v3/pipelines/deals/{pipelineId}/stages).'''
    _missing = [p for p in ['pipeline_id', 'name'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "crm_pipeline_stages"').fetchone()[0] + 1
        _id = 'stg_' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "crm_pipeline_stages" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'stg_' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('pipeline_id') is not None:
            _cols.append('pipeline_id')
            _v = kwargs['pipeline_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('name') is not None:
            _cols.append('name')
            _v = kwargs['name']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('display_order') is not None:
            _cols.append('display_order')
            _v = kwargs['display_order']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('probability_pct') is not None:
            _cols.append('probability_pct')
            _v = kwargs['probability_pct']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('forecast_category') is not None:
            _cols.append('forecast_category')
            _v = kwargs['forecast_category']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('is_closed') is not None:
            _cols.append('is_closed')
            _v = kwargs['is_closed']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('is_won') is not None:
            _cols.append('is_won')
            _v = kwargs['is_won']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        cur.execute('INSERT INTO "crm_pipeline_stages" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "crm_pipeline_stages" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['attributes'] = {'type': 'crm_pipeline_stage', 'url': '/services/data/v62.0/sobjects/crm_pipeline_stage/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_stage_create = stage_create
def _bf_friction_stage_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_stage_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "stage_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_stage_create(*_bf_args, **_bf_kwargs)
_bf_friction_stage_create.blobfish_original = _bf_orig_stage_create
stage_create = _bf_friction_stage_create

def stage_update(db_path='state.db', **kwargs):
    '''Update a pipeline stage (PATCH /crm/v3/pipelines/deals/{pipelineId}/stages/{stageId}).'''
    _missing = [p for p in ['stage_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "crm_pipeline_stages" WHERE "id" = ?', [str(kwargs['stage_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'crm_pipeline_stage not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _sets, _args = [], []
        if kwargs.get('name') is not None:
            _sets.append('"name" = ?')
            _v = kwargs['name']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('display_order') is not None:
            _sets.append('"display_order" = ?')
            _v = kwargs['display_order']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('probability_pct') is not None:
            _sets.append('"probability_pct" = ?')
            _v = kwargs['probability_pct']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('forecast_category') is not None:
            _sets.append('"forecast_category" = ?')
            _v = kwargs['forecast_category']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('is_closed') is not None:
            _sets.append('"is_closed" = ?')
            _v = kwargs['is_closed']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('is_won') is not None:
            _sets.append('"is_won" = ?')
            _v = kwargs['is_won']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "crm_pipeline_stages" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['stage_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "crm_pipeline_stages" WHERE "id" = ?', [str(kwargs['stage_id'])]).fetchone()
        _r = dict(_row)
        _r['attributes'] = {'type': 'crm_pipeline_stage', 'url': '/services/data/v62.0/sobjects/crm_pipeline_stage/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_stage_update = stage_update
def _bf_friction_stage_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_stage_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "stage_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_stage_update(*_bf_args, **_bf_kwargs)
_bf_friction_stage_update.blobfish_original = _bf_orig_stage_update
stage_update = _bf_friction_stage_update

def stage_delete(db_path='state.db', **kwargs):
    '''Delete a pipeline stage (DELETE /crm/v3/pipelines/deals/{pipelineId}/stages/{stageId}).'''
    _missing = [p for p in ['stage_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "crm_pipeline_stages" WHERE "id" = ?', [str(kwargs['stage_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'crm_pipeline_stage not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        cur.execute('DELETE FROM "crm_pipeline_stages" WHERE "id" = ?', [str(kwargs['stage_id'])])
        conn.commit()
        _r = {'deleted': True, 'id': str(kwargs['stage_id'])}
        return {'id': _r.get('id'), 'success': True, 'errors': []}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_stage_delete = stage_delete
def _bf_friction_stage_delete(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_stage_delete(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "stage_delete|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_stage_delete(*_bf_args, **_bf_kwargs)
_bf_friction_stage_delete.blobfish_original = _bf_orig_stage_delete
stage_delete = _bf_friction_stage_delete

def meetings_list(db_path='state.db', **kwargs):
    '''List customer meetings (GET /crm/v3/objects/meetings).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('account_id') is not None:
            _where.append('"account_id" = ?')
            _args.append(str(kwargs['account_id']))
        if kwargs.get('contact_id') is not None:
            _where.append('"contact_id" = ?')
            _args.append(str(kwargs['contact_id']))
        if kwargs.get('status') is not None:
            _where.append('"status" = ?')
            _args.append(str(kwargs['status']))
        if kwargs.get('meeting_type') is not None:
            _where.append('"meeting_type" = ?')
            _args.append(str(kwargs['meeting_type']))
        if kwargs.get('organizer_employee_id') is not None:
            _where.append('"organizer_employee_id" = ?')
            _args.append(str(kwargs['organizer_employee_id']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "crm_meetings"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_meetings_list = meetings_list
def _bf_friction_meetings_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_meetings_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "meetings_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_meetings_list(*_bf_args, **_bf_kwargs)
_bf_friction_meetings_list.blobfish_original = _bf_orig_meetings_list
meetings_list = _bf_friction_meetings_list

def meeting_get(db_path='state.db', **kwargs):
    '''Retrieve one meeting by id (GET /crm/v3/objects/meetings/{meetingId}).'''
    _missing = [p for p in ['meeting_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "crm_meetings" WHERE "id" = ?', [str(kwargs['meeting_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'crm_meeting not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _r = dict(_row)
        _r['attributes'] = {'type': 'crm_meeting', 'url': '/services/data/v62.0/sobjects/crm_meeting/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_meeting_get = meeting_get
def _bf_friction_meeting_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_meeting_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "meeting_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_meeting_get(*_bf_args, **_bf_kwargs)
_bf_friction_meeting_get.blobfish_original = _bf_orig_meeting_get
meeting_get = _bf_friction_meeting_get

def meeting_create(db_path='state.db', **kwargs):
    '''Schedule a customer meeting (POST /crm/v3/objects/meetings).'''
    _missing = [p for p in ['subject', 'starts_at'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "crm_meetings"').fetchone()[0] + 1
        _id = 'mtg_' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "crm_meetings" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'mtg_' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('subject') is not None:
            _cols.append('subject')
            _v = kwargs['subject']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('account_id') is not None:
            _cols.append('account_id')
            _v = kwargs['account_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('contact_id') is not None:
            _cols.append('contact_id')
            _v = kwargs['contact_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('organizer_employee_id') is not None:
            _cols.append('organizer_employee_id')
            _v = kwargs['organizer_employee_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('meeting_type') is not None:
            _cols.append('meeting_type')
            _v = kwargs['meeting_type']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('starts_at') is not None:
            _cols.append('starts_at')
            _v = kwargs['starts_at']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('ends_at') is not None:
            _cols.append('ends_at')
            _v = kwargs['ends_at']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('location') is not None:
            _cols.append('location')
            _v = kwargs['location']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'status' not in _cols:
            _cols.append('status')
            _vals.append('scheduled')
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "crm_meetings" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "crm_meetings" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['attributes'] = {'type': 'crm_meeting', 'url': '/services/data/v62.0/sobjects/crm_meeting/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_meeting_create = meeting_create
def _bf_friction_meeting_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_meeting_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "meeting_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_meeting_create(*_bf_args, **_bf_kwargs)
_bf_friction_meeting_create.blobfish_original = _bf_orig_meeting_create
meeting_create = _bf_friction_meeting_create

def meeting_update(db_path='state.db', **kwargs):
    '''Reschedule or update a meeting (PATCH /crm/v3/objects/meetings/{meetingId}).'''
    _missing = [p for p in ['meeting_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "crm_meetings" WHERE "id" = ?', [str(kwargs['meeting_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'crm_meeting not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _sets, _args = [], []
        if kwargs.get('subject') is not None:
            _sets.append('"subject" = ?')
            _v = kwargs['subject']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('starts_at') is not None:
            _sets.append('"starts_at" = ?')
            _v = kwargs['starts_at']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('ends_at') is not None:
            _sets.append('"ends_at" = ?')
            _v = kwargs['ends_at']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('location') is not None:
            _sets.append('"location" = ?')
            _v = kwargs['location']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('status') is not None:
            _sets.append('"status" = ?')
            _v = kwargs['status']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('meeting_type') is not None:
            _sets.append('"meeting_type" = ?')
            _v = kwargs['meeting_type']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('outcome_notes') is not None:
            _sets.append('"outcome_notes" = ?')
            _v = kwargs['outcome_notes']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "crm_meetings" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['meeting_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "crm_meetings" WHERE "id" = ?', [str(kwargs['meeting_id'])]).fetchone()
        _r = dict(_row)
        _r['attributes'] = {'type': 'crm_meeting', 'url': '/services/data/v62.0/sobjects/crm_meeting/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_meeting_update = meeting_update
def _bf_friction_meeting_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_meeting_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "meeting_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_meeting_update(*_bf_args, **_bf_kwargs)
_bf_friction_meeting_update.blobfish_original = _bf_orig_meeting_update
meeting_update = _bf_friction_meeting_update

def meeting_delete(db_path='state.db', **kwargs):
    '''Cancel and remove a meeting (DELETE /crm/v3/objects/meetings/{meetingId}).'''
    _missing = [p for p in ['meeting_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "crm_meetings" WHERE "id" = ?', [str(kwargs['meeting_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'crm_meeting not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        cur.execute('DELETE FROM "crm_meetings" WHERE "id" = ?', [str(kwargs['meeting_id'])])
        conn.commit()
        _r = {'deleted': True, 'id': str(kwargs['meeting_id'])}
        return {'id': _r.get('id'), 'success': True, 'errors': []}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_meeting_delete = meeting_delete
def _bf_friction_meeting_delete(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_meeting_delete(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "meeting_delete|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_meeting_delete(*_bf_args, **_bf_kwargs)
_bf_friction_meeting_delete.blobfish_original = _bf_orig_meeting_delete
meeting_delete = _bf_friction_meeting_delete

def meetings_search(db_path='state.db', **kwargs):
    '''Search meetings by subject, location or outcome notes (POST /crm/v3/objects/meetings/search).'''
    _missing = [p for p in ['query'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _qv = '%' + str(kwargs['query']) + '%'
        _where, _args = ["(\"subject\" LIKE ? OR \"location\" LIKE ? OR \"outcome_notes\" LIKE ?)"], [_qv] * 3
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "crm_meetings" WHERE ' + ' AND '.join(_where) + ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_meetings_search = meetings_search
def _bf_friction_meetings_search(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_meetings_search(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "meetings_search|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_meetings_search(*_bf_args, **_bf_kwargs)
_bf_friction_meetings_search.blobfish_original = _bf_orig_meetings_search
meetings_search = _bf_friction_meetings_search

def notes_list(db_path='state.db', **kwargs):
    '''List notes attached to CRM records (GET /crm/v3/objects/notes).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('parent_type') is not None:
            _where.append('"parent_type" = ?')
            _args.append(str(kwargs['parent_type']))
        if kwargs.get('parent_id') is not None:
            _where.append('"parent_id" = ?')
            _args.append(str(kwargs['parent_id']))
        if kwargs.get('author_employee_id') is not None:
            _where.append('"author_employee_id" = ?')
            _args.append(str(kwargs['author_employee_id']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "crm_notes"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notes_list = notes_list
def _bf_friction_notes_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notes_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notes_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notes_list(*_bf_args, **_bf_kwargs)
_bf_friction_notes_list.blobfish_original = _bf_orig_notes_list
notes_list = _bf_friction_notes_list

def note_get(db_path='state.db', **kwargs):
    '''Retrieve a single note (GET /crm/v3/objects/notes/{noteId}).'''
    _missing = [p for p in ['note_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "crm_notes" WHERE "id" = ?', [str(kwargs['note_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'crm_note not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _r = dict(_row)
        _r['attributes'] = {'type': 'crm_note', 'url': '/services/data/v62.0/sobjects/crm_note/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_note_get = note_get
def _bf_friction_note_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_note_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "note_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_note_get(*_bf_args, **_bf_kwargs)
_bf_friction_note_get.blobfish_original = _bf_orig_note_get
note_get = _bf_friction_note_get

def note_create(db_path='state.db', **kwargs):
    '''Attach a note to a CRM record (POST /crm/v3/objects/notes).'''
    _missing = [p for p in ['parent_type', 'parent_id', 'body'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "crm_notes"').fetchone()[0] + 1
        _id = 'note_' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "crm_notes" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'note_' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('parent_type') is not None:
            _cols.append('parent_type')
            _v = kwargs['parent_type']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('parent_id') is not None:
            _cols.append('parent_id')
            _v = kwargs['parent_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('title') is not None:
            _cols.append('title')
            _v = kwargs['title']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('body') is not None:
            _cols.append('body')
            _v = kwargs['body']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('author_employee_id') is not None:
            _cols.append('author_employee_id')
            _v = kwargs['author_employee_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('is_private') is not None:
            _cols.append('is_private')
            _v = kwargs['is_private']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        if 'updated_at' not in _cols:
            _cols.append('updated_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "crm_notes" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "crm_notes" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['attributes'] = {'type': 'crm_note', 'url': '/services/data/v62.0/sobjects/crm_note/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_note_create = note_create
def _bf_friction_note_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_note_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "note_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_note_create(*_bf_args, **_bf_kwargs)
_bf_friction_note_create.blobfish_original = _bf_orig_note_create
note_create = _bf_friction_note_create

def note_update(db_path='state.db', **kwargs):
    '''Edit an existing note (PATCH /crm/v3/objects/notes/{noteId}).'''
    _missing = [p for p in ['note_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "crm_notes" WHERE "id" = ?', [str(kwargs['note_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'crm_note not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _sets, _args = [], []
        if kwargs.get('title') is not None:
            _sets.append('"title" = ?')
            _v = kwargs['title']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('body') is not None:
            _sets.append('"body" = ?')
            _v = kwargs['body']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('is_private') is not None:
            _sets.append('"is_private" = ?')
            _v = kwargs['is_private']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('updated_at') is not None:
            _sets.append('"updated_at" = ?')
            _v = kwargs['updated_at']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "crm_notes" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['note_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "crm_notes" WHERE "id" = ?', [str(kwargs['note_id'])]).fetchone()
        _r = dict(_row)
        _r['attributes'] = {'type': 'crm_note', 'url': '/services/data/v62.0/sobjects/crm_note/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_note_update = note_update
def _bf_friction_note_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_note_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "note_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_note_update(*_bf_args, **_bf_kwargs)
_bf_friction_note_update.blobfish_original = _bf_orig_note_update
note_update = _bf_friction_note_update

def note_delete(db_path='state.db', **kwargs):
    '''Delete a note (DELETE /crm/v3/objects/notes/{noteId}).'''
    _missing = [p for p in ['note_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "crm_notes" WHERE "id" = ?', [str(kwargs['note_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'crm_note not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        cur.execute('DELETE FROM "crm_notes" WHERE "id" = ?', [str(kwargs['note_id'])])
        conn.commit()
        _r = {'deleted': True, 'id': str(kwargs['note_id'])}
        return {'id': _r.get('id'), 'success': True, 'errors': []}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_note_delete = note_delete
def _bf_friction_note_delete(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_note_delete(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "note_delete|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_note_delete(*_bf_args, **_bf_kwargs)
_bf_friction_note_delete.blobfish_original = _bf_orig_note_delete
note_delete = _bf_friction_note_delete

def notes_search(db_path='state.db', **kwargs):
    '''Full-text search across note titles and bodies (POST /crm/v3/objects/notes/search).'''
    _missing = [p for p in ['query'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _qv = '%' + str(kwargs['query']) + '%'
        _where, _args = ["(\"title\" LIKE ? OR \"body\" LIKE ?)"], [_qv] * 2
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "crm_notes" WHERE ' + ' AND '.join(_where) + ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_notes_search = notes_search
def _bf_friction_notes_search(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_notes_search(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "notes_search|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_notes_search(*_bf_args, **_bf_kwargs)
_bf_friction_notes_search.blobfish_original = _bf_orig_notes_search
notes_search = _bf_friction_notes_search

def custom_fields_list(db_path='state.db', **kwargs):
    '''List custom field definitions for an object (GET /crm/v3/properties/{objectType}).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('object_name') is not None:
            _where.append('"object_name" = ?')
            _args.append(str(kwargs['object_name']))
        if kwargs.get('data_type') is not None:
            _where.append('"data_type" = ?')
            _args.append(str(kwargs['data_type']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "crm_custom_fields"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_custom_fields_list = custom_fields_list
def _bf_friction_custom_fields_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_custom_fields_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "custom_fields_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_custom_fields_list(*_bf_args, **_bf_kwargs)
_bf_friction_custom_fields_list.blobfish_original = _bf_orig_custom_fields_list
custom_fields_list = _bf_friction_custom_fields_list

def custom_field_create(db_path='state.db', **kwargs):
    '''Define a new custom field on an object (POST /crm/v3/properties/{objectType}).'''
    _missing = [p for p in ['object_name', 'field_label', 'field_api_name', 'data_type'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "crm_custom_fields"').fetchone()[0] + 1
        _id = 'fld_' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "crm_custom_fields" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'fld_' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('object_name') is not None:
            _cols.append('object_name')
            _v = kwargs['object_name']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('field_label') is not None:
            _cols.append('field_label')
            _v = kwargs['field_label']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('field_api_name') is not None:
            _cols.append('field_api_name')
            _v = kwargs['field_api_name']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('data_type') is not None:
            _cols.append('data_type')
            _v = kwargs['data_type']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('is_required') is not None:
            _cols.append('is_required')
            _v = kwargs['is_required']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('picklist_values') is not None:
            _cols.append('picklist_values')
            _v = kwargs['picklist_values']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('help_text') is not None:
            _cols.append('help_text')
            _v = kwargs['help_text']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "crm_custom_fields" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "crm_custom_fields" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['attributes'] = {'type': 'crm_custom_field', 'url': '/services/data/v62.0/sobjects/crm_custom_field/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_custom_field_create = custom_field_create
def _bf_friction_custom_field_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_custom_field_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "custom_field_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_custom_field_create(*_bf_args, **_bf_kwargs)
_bf_friction_custom_field_create.blobfish_original = _bf_orig_custom_field_create
custom_field_create = _bf_friction_custom_field_create

def custom_field_update(db_path='state.db', **kwargs):
    '''Update a custom field definition (PATCH /crm/v3/properties/{objectType}/{fieldName}).'''
    _missing = [p for p in ['field_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "crm_custom_fields" WHERE "id" = ?', [str(kwargs['field_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'crm_custom_field not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _sets, _args = [], []
        if kwargs.get('field_label') is not None:
            _sets.append('"field_label" = ?')
            _v = kwargs['field_label']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('data_type') is not None:
            _sets.append('"data_type" = ?')
            _v = kwargs['data_type']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('is_required') is not None:
            _sets.append('"is_required" = ?')
            _v = kwargs['is_required']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('picklist_values') is not None:
            _sets.append('"picklist_values" = ?')
            _v = kwargs['picklist_values']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('help_text') is not None:
            _sets.append('"help_text" = ?')
            _v = kwargs['help_text']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "crm_custom_fields" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['field_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "crm_custom_fields" WHERE "id" = ?', [str(kwargs['field_id'])]).fetchone()
        _r = dict(_row)
        _r['attributes'] = {'type': 'crm_custom_field', 'url': '/services/data/v62.0/sobjects/crm_custom_field/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_custom_field_update = custom_field_update
def _bf_friction_custom_field_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_custom_field_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "custom_field_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_custom_field_update(*_bf_args, **_bf_kwargs)
_bf_friction_custom_field_update.blobfish_original = _bf_orig_custom_field_update
custom_field_update = _bf_friction_custom_field_update

def custom_field_delete(db_path='state.db', **kwargs):
    '''Delete a custom field definition (DELETE /crm/v3/properties/{objectType}/{fieldName}).'''
    _missing = [p for p in ['field_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "crm_custom_fields" WHERE "id" = ?', [str(kwargs['field_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'crm_custom_field not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        cur.execute('DELETE FROM "crm_custom_fields" WHERE "id" = ?', [str(kwargs['field_id'])])
        conn.commit()
        _r = {'deleted': True, 'id': str(kwargs['field_id'])}
        return {'id': _r.get('id'), 'success': True, 'errors': []}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_custom_field_delete = custom_field_delete
def _bf_friction_custom_field_delete(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_custom_field_delete(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "custom_field_delete|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_custom_field_delete(*_bf_args, **_bf_kwargs)
_bf_friction_custom_field_delete.blobfish_original = _bf_orig_custom_field_delete
custom_field_delete = _bf_friction_custom_field_delete

def contact_update(db_path='state.db', **kwargs):
    '''Update fields on a contact (PATCH /services/data/v60.0/sobjects/Contact/{id}).'''
    _missing = [p for p in ['contact_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "contacts" WHERE "id" = ?', [str(kwargs['contact_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'contact not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _sets, _args = [], []
        if kwargs.get('name') is not None:
            _sets.append('"name" = ?')
            _v = kwargs['name']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('email') is not None:
            _sets.append('"email" = ?')
            _v = kwargs['email']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('status') is not None:
            _sets.append('"status" = ?')
            _v = kwargs['status']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('account_id') is not None:
            _sets.append('"account_id" = ?')
            _v = kwargs['account_id']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('owner_id') is not None:
            _sets.append('"owner_id" = ?')
            _v = kwargs['owner_id']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "contacts" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['contact_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "contacts" WHERE "id" = ?', [str(kwargs['contact_id'])]).fetchone()
        _r = dict(_row)
        _r['attributes'] = {'type': 'contact', 'url': '/services/data/v62.0/sobjects/contact/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_contact_update = contact_update
def _bf_friction_contact_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_contact_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "contact_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_contact_update(*_bf_args, **_bf_kwargs)
_bf_friction_contact_update.blobfish_original = _bf_orig_contact_update
contact_update = _bf_friction_contact_update

def task_update(db_path='state.db', **kwargs):
    '''Update a task's status, owner, priority or due date (PATCH /services/data/v60.0/sobjects/Task/{id}).'''
    _missing = [p for p in ['task_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "tasks" WHERE "id" = ?', [str(kwargs['task_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'task not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _sets, _args = [], []
        if kwargs.get('subject') is not None:
            _sets.append('"subject" = ?')
            _v = kwargs['subject']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('status') is not None:
            _sets.append('"status" = ?')
            _v = kwargs['status']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('priority') is not None:
            _sets.append('"priority" = ?')
            _v = kwargs['priority']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('assigned_to') is not None:
            _sets.append('"assigned_to" = ?')
            _v = kwargs['assigned_to']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('due_at') is not None:
            _sets.append('"due_at" = ?')
            _v = kwargs['due_at']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('description') is not None:
            _sets.append('"description" = ?')
            _v = kwargs['description']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "tasks" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['task_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "tasks" WHERE "id" = ?', [str(kwargs['task_id'])]).fetchone()
        _r = dict(_row)
        _r['attributes'] = {'type': 'task', 'url': '/services/data/v62.0/sobjects/task/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_task_update = task_update
def _bf_friction_task_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_task_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "task_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_task_update(*_bf_args, **_bf_kwargs)
_bf_friction_task_update.blobfish_original = _bf_orig_task_update
task_update = _bf_friction_task_update

def tasks_search(db_path='state.db', **kwargs):
    '''Search tasks by subject or description (GET /services/data/v60.0/search).'''
    _missing = [p for p in ['query'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _qv = '%' + str(kwargs['query']) + '%'
        _where, _args = ["(\"subject\" LIKE ? OR \"description\" LIKE ?)"], [_qv] * 2
        if kwargs.get('status') is not None:
            _where.append('"status" = ?')
            _args.append(str(kwargs['status']))
        if kwargs.get('assigned_to') is not None:
            _where.append('"assigned_to" = ?')
            _args.append(str(kwargs['assigned_to']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "tasks" WHERE ' + ' AND '.join(_where) + ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_tasks_search = tasks_search
def _bf_friction_tasks_search(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_tasks_search(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "tasks_search|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_tasks_search(*_bf_args, **_bf_kwargs)
_bf_friction_tasks_search.blobfish_original = _bf_orig_tasks_search
tasks_search = _bf_friction_tasks_search

def leads_list(db_path='state.db', **kwargs):
    '''List sales leads (GET /services/data/v60.0/sobjects/Lead).'''
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _where, _args = [], []
        if kwargs.get('status') is not None:
            _where.append('"status" = ?')
            _args.append(str(kwargs['status']))
        if kwargs.get('source') is not None:
            _where.append('"source" = ?')
            _args.append(str(kwargs['source']))
        if kwargs.get('owner_employee_id') is not None:
            _where.append('"owner_employee_id" = ?')
            _args.append(str(kwargs['owner_employee_id']))
        if kwargs.get('company_name') is not None:
            _where.append('"company_name" = ?')
            _args.append(str(kwargs['company_name']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "sales_leads"'
        if _where:
            _q += ' WHERE ' + ' AND '.join(_where)
        _q += ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_leads_list = leads_list
def _bf_friction_leads_list(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_leads_list(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "leads_list|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_leads_list(*_bf_args, **_bf_kwargs)
_bf_friction_leads_list.blobfish_original = _bf_orig_leads_list
leads_list = _bf_friction_leads_list

def email_message_update(db_path='state.db', **kwargs):
    '''Update a stored email message (PATCH /crm/v3/objects/emails/{emailId}).'''
    _missing = [p for p in ['message_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "email_messages" WHERE "id" = ?', [str(kwargs['message_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'email_message not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _sets, _args = [], []
        if kwargs.get('body') is not None:
            _sets.append('"body" = ?')
            _v = kwargs['body']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('direction') is not None:
            _sets.append('"direction" = ?')
            _v = kwargs['direction']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('to_address') is not None:
            _sets.append('"to_address" = ?')
            _v = kwargs['to_address']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('from_address') is not None:
            _sets.append('"from_address" = ?')
            _v = kwargs['from_address']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('sent_at') is not None:
            _sets.append('"sent_at" = ?')
            _v = kwargs['sent_at']
            _args.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if _sets:
            cur.execute('UPDATE "email_messages" SET ' + ', '.join(_sets) + ' WHERE "id" = ?', _args + [str(kwargs['message_id'])])
            conn.commit()
        _row = cur.execute('SELECT * FROM "email_messages" WHERE "id" = ?', [str(kwargs['message_id'])]).fetchone()
        _r = dict(_row)
        _r['attributes'] = {'type': 'email_message', 'url': '/services/data/v62.0/sobjects/email_message/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_email_message_update = email_message_update
def _bf_friction_email_message_update(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_email_message_update(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "email_message_update|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_email_message_update(*_bf_args, **_bf_kwargs)
_bf_friction_email_message_update.blobfish_original = _bf_orig_email_message_update
email_message_update = _bf_friction_email_message_update

def email_message_delete(db_path='state.db', **kwargs):
    '''Delete a stored email message (DELETE /crm/v3/objects/emails/{emailId}).'''
    _missing = [p for p in ['message_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "email_messages" WHERE "id" = ?', [str(kwargs['message_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'email_message not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        cur.execute('DELETE FROM "email_messages" WHERE "id" = ?', [str(kwargs['message_id'])])
        conn.commit()
        _r = {'deleted': True, 'id': str(kwargs['message_id'])}
        return {'id': _r.get('id'), 'success': True, 'errors': []}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_email_message_delete = email_message_delete
def _bf_friction_email_message_delete(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_email_message_delete(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "email_message_delete|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_email_message_delete(*_bf_args, **_bf_kwargs)
_bf_friction_email_message_delete.blobfish_original = _bf_orig_email_message_delete
email_message_delete = _bf_friction_email_message_delete

def email_messages_search(db_path='state.db', **kwargs):
    '''Search email message bodies and addresses (POST /crm/v3/objects/emails/search).'''
    _missing = [p for p in ['query'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _qv = '%' + str(kwargs['query']) + '%'
        _where, _args = ["(\"body\" LIKE ? OR \"from_address\" LIKE ? OR \"to_address\" LIKE ?)"], [_qv] * 3
        if kwargs.get('thread_id') is not None:
            _where.append('"thread_id" = ?')
            _args.append(str(kwargs['thread_id']))
        if kwargs.get('direction') is not None:
            _where.append('"direction" = ?')
            _args.append(str(kwargs['direction']))
        _limit = int(kwargs.get('per_page') or kwargs.get('limit') or kwargs.get('maxResults') or kwargs.get('page_size') or 30)
        _q = 'SELECT * FROM "email_messages" WHERE ' + ' AND '.join(_where) + ' ORDER BY "id" LIMIT ?'
        _rows = [dict(r) for r in cur.execute(_q, _args + [_limit]).fetchall()]
        _r = {'items': _rows, 'count': len(_rows)}
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_email_messages_search = email_messages_search
def _bf_friction_email_messages_search(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_email_messages_search(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "email_messages_search|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_email_messages_search(*_bf_args, **_bf_kwargs)
_bf_friction_email_messages_search.blobfish_original = _bf_orig_email_messages_search
email_messages_search = _bf_friction_email_messages_search

def sequence_create(db_path='state.db', **kwargs):
    '''Create an outbound sequence (POST /sequences).'''
    _missing = [p for p in ['name'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _n = cur.execute('SELECT COUNT(*) FROM "outreach_sequences"').fetchone()[0] + 1
        _id = 'seq_' + str(_n).zfill(4)
        while cur.execute('SELECT 1 FROM "outreach_sequences" WHERE "id" = ?', [_id]).fetchone() is not None:
            _n += 1
            _id = 'seq_' + str(_n).zfill(4)
        _cols, _vals = ['id'], [_id]
        if kwargs.get('name') is not None:
            _cols.append('name')
            _v = kwargs['name']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('status') is not None:
            _cols.append('status')
            _v = kwargs['status']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('step_count') is not None:
            _cols.append('step_count')
            _v = kwargs['step_count']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if kwargs.get('owner_employee_id') is not None:
            _cols.append('owner_employee_id')
            _v = kwargs['owner_employee_id']
            _vals.append(json.dumps(_v) if isinstance(_v, (dict, list)) else _v)
        if 'status' not in _cols:
            _cols.append('status')
            _vals.append('draft')
        if 'created_at' not in _cols:
            _cols.append('created_at')
            _vals.append(_now)
        cur.execute('INSERT INTO "outreach_sequences" (' + ', '.join('"' + c + '"' for c in _cols) + ') VALUES (' + ', '.join(['?'] * len(_cols)) + ')', _vals)
        conn.commit()
        _row = cur.execute('SELECT * FROM "outreach_sequences" WHERE "id" = ?', [_id]).fetchone()
        _r = dict(_row) if _row else {'id': _id}
        _r['attributes'] = {'type': 'outreach_sequence', 'url': '/services/data/v62.0/sobjects/outreach_sequence/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_sequence_create = sequence_create
def _bf_friction_sequence_create(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_sequence_create(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "sequence_create|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_sequence_create(*_bf_args, **_bf_kwargs)
_bf_friction_sequence_create.blobfish_original = _bf_orig_sequence_create
sequence_create = _bf_friction_sequence_create

def sequence_get(db_path='state.db', **kwargs):
    '''Retrieve one outbound sequence (GET /sequences/{id}).'''
    _missing = [p for p in ['sequence_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "outreach_sequences" WHERE "id" = ?', [str(kwargs['sequence_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'outreach_sequence not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _r = dict(_row)
        _r['attributes'] = {'type': 'outreach_sequence', 'url': '/services/data/v62.0/sobjects/outreach_sequence/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_sequence_get = sequence_get
def _bf_friction_sequence_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_sequence_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "sequence_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_sequence_get(*_bf_args, **_bf_kwargs)
_bf_friction_sequence_get.blobfish_original = _bf_orig_sequence_get
sequence_get = _bf_friction_sequence_get

def sequence_delete(db_path='state.db', **kwargs):
    '''Delete an outbound sequence (DELETE /sequences/{id}).'''
    _missing = [p for p in ['sequence_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "outreach_sequences" WHERE "id" = ?', [str(kwargs['sequence_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'outreach_sequence not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        cur.execute('DELETE FROM "outreach_sequences" WHERE "id" = ?', [str(kwargs['sequence_id'])])
        conn.commit()
        _r = {'deleted': True, 'id': str(kwargs['sequence_id'])}
        return {'id': _r.get('id'), 'success': True, 'errors': []}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_sequence_delete = sequence_delete
def _bf_friction_sequence_delete(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_sequence_delete(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "sequence_delete|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_sequence_delete(*_bf_args, **_bf_kwargs)
_bf_friction_sequence_delete.blobfish_original = _bf_orig_sequence_delete
sequence_delete = _bf_friction_sequence_delete

def quota_get(db_path='state.db', **kwargs):
    '''Retrieve a rep's quota and attainment for a period (GET /analytics/quotas/{id}).'''
    _missing = [p for p in ['quota_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "rep_quotas" WHERE "id" = ?', [str(kwargs['quota_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'rep_quota not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        _r = dict(_row)
        _r['attributes'] = {'type': 'rep_quota', 'url': '/services/data/v62.0/sobjects/rep_quota/' + str(_r.get('id', ''))}
        return _r
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_quota_get = quota_get
def _bf_friction_quota_get(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_quota_get(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "quota_get|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_quota_get(*_bf_args, **_bf_kwargs)
_bf_friction_quota_get.blobfish_original = _bf_orig_quota_get
quota_get = _bf_friction_quota_get

def lead_convert(db_path="state.db", **kwargs):
    """Convert a qualified lead into an account + contact (+ optional opportunity)."""
    import sqlite3, json, datetime
    lead_id = kwargs.get("lead_id")
    if not lead_id:
        return {"error": "lead_id is required", "status": 400}
    create_opp = str(kwargs.get("create_opportunity", "false")).lower() in ("1", "true", "yes")
    opp_name = kwargs.get("opportunity_name")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM sales_leads WHERE id = ?", (lead_id,)).fetchone()
    if row is None:
        conn.close()
        return {"error": "lead not found: %s" % lead_id, "status": 404}
    lead = dict(row)
    if str(lead.get("status", "")).lower() == "converted":
        conn.close()
        return {"error": "lead %s is already converted" % lead_id, "status": 409}
    now = datetime.datetime(2026, 2, 16, 12, 0, 0).isoformat() + "Z"
    n = cur.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
    account_id = "account_%03d" % (n + 1)
    cur.execute("INSERT INTO accounts (id, name) VALUES (?, ?)",
                (account_id, lead.get("company_name") or "Unnamed Account"))
    m = cur.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
    contact_id = "contact_%03d" % (m + 1)
    cur.execute(
        "INSERT INTO contacts (id, account_id, name, email, status, owner_id, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (contact_id, account_id, lead.get("contact_name") or "Unknown", None, "active",
         str(lead.get("owner_employee_id") or ""), now))
    cur.execute("UPDATE sales_leads SET status = ? WHERE id = ?", ("converted", lead_id))
    opportunity_id = None
    if create_opp:
        k = cur.execute("SELECT COUNT(*) FROM opportunities").fetchone()[0]
        opportunity_id = "opportunity_%03d" % (k + 1)
        cols = [c[1] for c in cur.execute("PRAGMA table_info(opportunities)")]
        vals = {"id": opportunity_id, "account_id": account_id,
                "name": opp_name or ("%s — New Business" % (lead.get("company_name") or "Opportunity"))}
        use = [c for c in cols if c in vals]
        cur.execute("INSERT INTO opportunities (%s) VALUES (%s)"
                    % (", ".join(use), ", ".join("?" for _ in use)), [vals[c] for c in use])
    conn.commit()
    conn.close()
    return {"converted": True, "lead_id": lead_id, "account_id": account_id,
            "contact_id": contact_id, "opportunity_id": opportunity_id}

_env_orig_lead_convert = lead_convert
def _env_lead_convert(db_path='state.db', **kwargs):
    _r = _env_orig_lead_convert(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
    if 'error' in _r and _r.get('status') == 400:
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    return _r
lead_convert = _env_lead_convert

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_lead_convert = lead_convert
def _bf_friction_lead_convert(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_lead_convert(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "lead_convert|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_lead_convert(*_bf_args, **_bf_kwargs)
_bf_friction_lead_convert.blobfish_original = _bf_orig_lead_convert
lead_convert = _bf_friction_lead_convert

def opportunity_convert_to_order(db_path="state.db", **kwargs):
    """Raise an ERP sales order from a closed-won opportunity.

    The gate is the point: an order may only exist behind a won opportunity, which
    is how Closed Won is prevented from being set by hand elsewhere in this world.
    """
    import sqlite3, datetime
    opportunity_id = kwargs.get("opportunity_id")
    if not opportunity_id:
        return {"error": "opportunity_id is required", "status": 400}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM opportunities WHERE id = ?", (opportunity_id,)).fetchone()
    if row is None:
        conn.close()
        return {"error": "opportunity not found: %s" % opportunity_id, "status": 404}
    opp = dict(row)
    status = str(opp.get("status") or "").strip().lower().replace(" ", "_")
    if status != "closed_won":
        conn.close()
        return {"error": "opportunity %s is not closed_won (status=%r); an order cannot be raised"
                % (opportunity_id, status or None), "status": 409}
    existing = cur.execute(
        "SELECT id FROM erp_sales_orders WHERE memo LIKE ?", ("%" + opportunity_id + "%",)).fetchone()
    if existing is not None:
        conn.close()
        return {"error": "opportunity %s already has order %s" % (opportunity_id, existing["id"]),
                "status": 409, "order_id": existing["id"]}
    account_name = None
    acct = cur.execute("SELECT name FROM accounts WHERE id = ?",
                       (opp.get("account_id"),)).fetchone()
    if acct is not None:
        account_name = acct["name"]
    n = cur.execute("SELECT COUNT(*) FROM erp_sales_orders").fetchone()[0]
    order_id = "SO-2026-%04d" % (101 + n)
    now = datetime.datetime(2026, 2, 16, 12, 0, 0)
    cur.execute(
        "INSERT INTO erp_sales_orders (id, entity, entity_name, trandate, status, memo, "
        "subsidiary, currency, total, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (order_id, opp.get("account_id"), account_name, now.date().isoformat(),
         "pendingFulfillment",
         "Raised from opportunity %s: %s" % (opportunity_id, opp.get("name") or ""),
         "1", "usd", opp.get("amount"), now.isoformat() + "Z"))
    conn.commit()
    conn.close()
    return {"converted": True, "opportunity_id": opportunity_id, "order_id": order_id,
            "status": "pendingFulfillment", "total": opp.get("amount")}

_env_orig_opportunity_convert_to_order = opportunity_convert_to_order
def _env_opportunity_convert_to_order(db_path='state.db', **kwargs):
    _r = _env_orig_opportunity_convert_to_order(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
    if 'error' in _r and _r.get('status') == 400:
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    return _r
opportunity_convert_to_order = _env_opportunity_convert_to_order

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_opportunity_convert_to_order = opportunity_convert_to_order
def _bf_friction_opportunity_convert_to_order(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_opportunity_convert_to_order(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "opportunity_convert_to_order|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_opportunity_convert_to_order(*_bf_args, **_bf_kwargs)
_bf_friction_opportunity_convert_to_order.blobfish_original = _bf_orig_opportunity_convert_to_order
opportunity_convert_to_order = _bf_friction_opportunity_convert_to_order

def email_send(db_path="state.db", **kwargs):
    """Send an outbound email on an existing thread, honouring suppression."""
    import sqlite3, datetime
    thread_id = kwargs.get("thread_id")
    to_address = kwargs.get("to_address")
    body = kwargs.get("body")
    if not thread_id or not to_address or not body:
        return {"error": "thread_id, to_address and body are required", "status": 400}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    thread = cur.execute("SELECT * FROM email_threads WHERE id = ?", (thread_id,)).fetchone()
    if thread is None:
        conn.close()
        return {"error": "thread not found: %s" % thread_id, "status": 404}
    tables = {r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "bounces" in tables:
        bounced = cur.execute("SELECT 1 FROM bounces WHERE email = ? LIMIT 1", (to_address,)).fetchone()
        if bounced:
            conn.close()
            return {"error": "recipient %s is on the bounce suppression list" % to_address,
                    "status": 403, "suppressed": True}
    n = cur.execute("SELECT COUNT(*) FROM email_messages").fetchone()[0]
    msg_id = "emsg_%04d" % (n + 1)
    sent_at = datetime.datetime(2026, 2, 16, 12, 0, 0).isoformat() + "Z"
    cur.execute(
        "INSERT INTO email_messages (id, thread_id, direction, from_address, to_address, body, sent_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (msg_id, thread_id, "outbound",
         kwargs.get("from_address") or "mei.huang@morganstanleysimulated.com",
         to_address, body, sent_at))
    conn.commit()
    conn.close()
    return {"id": msg_id, "thread_id": thread_id, "to_address": to_address,
            "direction": "outbound", "sent_at": sent_at}

_env_orig_email_send = email_send
def _env_email_send(db_path='state.db', **kwargs):
    _r = _env_orig_email_send(db_path, **kwargs)
    if not isinstance(_r, dict):
        return _r
    if set(_r.keys()) == {'items', 'count'}:
        return {'totalSize': _r['count'], 'done': True, 'records': _r['items']}
    if 'error' in _r and _r.get('status') == 404:
        return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
    if 'error' in _r and _r.get('status') == 400:
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    return _r
email_send = _env_email_send

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_email_send = email_send
def _bf_friction_email_send(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_email_send(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "email_send|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_email_send(*_bf_args, **_bf_kwargs)
_bf_friction_email_send.blobfish_original = _bf_orig_email_send
email_send = _bf_friction_email_send

def account_delete(db_path='state.db', **kwargs):
    '''Delete an account (DELETE /services/data/v60.0/sobjects/Account/{id}).'''
    _missing = [p for p in ['account_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "accounts" WHERE "id" = ?', [str(kwargs['account_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'account not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        cur.execute('DELETE FROM "accounts" WHERE "id" = ?', [str(kwargs['account_id'])])
        conn.commit()
        _r = {'deleted': True, 'id': str(kwargs['account_id'])}
        return {'id': _r.get('id'), 'success': True, 'errors': []}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_account_delete = account_delete
def _bf_friction_account_delete(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_account_delete(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "account_delete|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_account_delete(*_bf_args, **_bf_kwargs)
_bf_friction_account_delete.blobfish_original = _bf_orig_account_delete
account_delete = _bf_friction_account_delete

def contact_delete(db_path='state.db', **kwargs):
    '''Delete a contact (DELETE /services/data/v60.0/sobjects/Contact/{id}).'''
    _missing = [p for p in ['contact_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "contacts" WHERE "id" = ?', [str(kwargs['contact_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'contact not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        cur.execute('DELETE FROM "contacts" WHERE "id" = ?', [str(kwargs['contact_id'])])
        conn.commit()
        _r = {'deleted': True, 'id': str(kwargs['contact_id'])}
        return {'id': _r.get('id'), 'success': True, 'errors': []}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_contact_delete = contact_delete
def _bf_friction_contact_delete(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_contact_delete(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "contact_delete|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_contact_delete(*_bf_args, **_bf_kwargs)
_bf_friction_contact_delete.blobfish_original = _bf_orig_contact_delete
contact_delete = _bf_friction_contact_delete

def lead_delete(db_path='state.db', **kwargs):
    '''Delete a lead (DELETE /services/data/v60.0/sobjects/Lead/{id}).'''
    _missing = [p for p in ['lead_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "sales_leads" WHERE "id" = ?', [str(kwargs['lead_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'sales_lead not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        cur.execute('DELETE FROM "sales_leads" WHERE "id" = ?', [str(kwargs['lead_id'])])
        conn.commit()
        _r = {'deleted': True, 'id': str(kwargs['lead_id'])}
        return {'id': _r.get('id'), 'success': True, 'errors': []}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_lead_delete = lead_delete
def _bf_friction_lead_delete(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_lead_delete(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "lead_delete|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_lead_delete(*_bf_args, **_bf_kwargs)
_bf_friction_lead_delete.blobfish_original = _bf_orig_lead_delete
lead_delete = _bf_friction_lead_delete

def opportunity_delete(db_path='state.db', **kwargs):
    '''Delete an opportunity (DELETE /services/data/v60.0/sobjects/Opportunity/{id}).'''
    _missing = [p for p in ['opportunity_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "opportunities" WHERE "id" = ?', [str(kwargs['opportunity_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'opportunitie not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        cur.execute('DELETE FROM "opportunities" WHERE "id" = ?', [str(kwargs['opportunity_id'])])
        conn.commit()
        _r = {'deleted': True, 'id': str(kwargs['opportunity_id'])}
        return {'id': _r.get('id'), 'success': True, 'errors': []}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_opportunity_delete = opportunity_delete
def _bf_friction_opportunity_delete(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_opportunity_delete(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "opportunity_delete|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_opportunity_delete(*_bf_args, **_bf_kwargs)
_bf_friction_opportunity_delete.blobfish_original = _bf_orig_opportunity_delete
opportunity_delete = _bf_friction_opportunity_delete

def task_delete(db_path='state.db', **kwargs):
    '''Delete a task (DELETE /services/data/v60.0/sobjects/Task/{id}).'''
    _missing = [p for p in ['task_id'] if kwargs.get(p) is None]
    if _missing:
        _r = {'error': 'missing required parameters: ' + ', '.join(_missing), 'status': 400}
        return [{'message': str(_r.get('error', '')), 'errorCode': 'REQUIRED_FIELD_MISSING'}]
    import sqlite3, json, datetime, hashlib
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _row = cur.execute('SELECT * FROM "tasks" WHERE "id" = ?', [str(kwargs['task_id'])]).fetchone()
        if _row is None:
            _r = {'error': 'task not found', 'status': 404}
            return [{'message': str(_r.get('error', '')), 'errorCode': 'NOT_FOUND'}]
        cur.execute('DELETE FROM "tasks" WHERE "id" = ?', [str(kwargs['task_id'])])
        conn.commit()
        _r = {'deleted': True, 'id': str(kwargs['task_id'])}
        return {'id': _r.get('id'), 'success': True, 'errors': []}
    finally:
        conn.close()

# --- blobfish environment friction v1: deterministic injected failures (do not edit) ---
_bf_orig_task_delete = task_delete
def _bf_friction_task_delete(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_task_delete(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "task_delete|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_task_delete(*_bf_args, **_bf_kwargs)
_bf_friction_task_delete.blobfish_original = _bf_orig_task_delete
task_delete = _bf_friction_task_delete

