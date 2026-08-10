"""Department records sub-agent: resolve one unique business handle from a free-text request without mutating state."""
import re, sqlite3

_SURFACES = {"finance_expense_reports":{"table":"finance_expense_reports","primary_key":"id","labels":["report_number"],"readable":["id","report_number","employee_id","category","amount","submitted_at","approver_employee_id","status"],"resolvable":["report_number","employee_id","category","amount","submitted_at","approver_employee_id"],"mutable":["report_number","category","amount","submitted_at","status"],"lifecycles":{"status":["submitted","approved","reimbursed","rejected"]}},"finance_budgets":{"table":"finance_budgets","primary_key":"id","labels":["budget_number"],"readable":["id","budget_number","department_id","fiscal_quarter","allocated_amount","spent_amount","status"],"resolvable":["budget_number","department_id","fiscal_quarter","allocated_amount","spent_amount"],"mutable":["budget_number","fiscal_quarter","allocated_amount","spent_amount","status"],"lifecycles":{"status":["draft","active","closed"]}},"account_links":{"table":"account_links","primary_key":"id","labels":["id","url"],"readable":["id","created","expires_at","object","url"],"resolvable":["id","created","expires_at","object","url"],"mutable":["created","expires_at","object","url"],"lifecycles":{}},"account_sessions":{"table":"account_sessions","primary_key":"id","labels":["id"],"readable":["id","account","client_secret","components","expires_at","livemode","object"],"resolvable":["id","account","client_secret","components","expires_at","livemode","object"],"mutable":["account","client_secret","components","expires_at","livemode","object"],"lifecycles":{}},"apple_pay_domains":{"table":"apple_pay_domains","primary_key":"id","labels":["id","domain_name"],"readable":["id","created","domain_name","livemode","object"],"resolvable":["id","created","domain_name","livemode","object"],"mutable":["created","domain_name","livemode","object"],"lifecycles":{}},"application_fees":{"table":"application_fees","primary_key":"id","labels":["id"],"readable":["id","account","amount","amount_refunded","application","charge","created","currency","livemode","object","refunded","refunds","balance_transaction","fee_source","originating_transaction"],"resolvable":["id","account","amount","amount_refunded","application","charge","created","currency","livemode","object","refunded","refunds","balance_transaction","fee_source","originating_transaction"],"mutable":["account","amount","amount_refunded","application","charge","created","currency","livemode","object","refunded","refunds","balance_transaction","fee_source","originating_transaction"],"lifecycles":{}},"apps_secrets":{"table":"apps_secrets","primary_key":"id","labels":["id","name"],"readable":["id","created","livemode","name","object","scope","deleted","expires_at","payload"],"resolvable":["id","created","livemode","name","object","scope","deleted","expires_at","payload"],"mutable":["created","livemode","name","object","scope","deleted","expires_at","payload"],"lifecycles":{}},"balance_settings":{"table":"balance_settings","primary_key":"id","labels":["id"],"readable":["id","object","payments"],"resolvable":["id","object","payments"],"mutable":["object","payments"],"lifecycles":{}},"balance_transactions":{"table":"balance_transactions","primary_key":"id","labels":["id"],"readable":["id","amount","available_on","balance_type","created","currency","fee","fee_details","net","object","reporting_category","status","type","description","exchange_rate","source"],"resolvable":["id","amount","available_on","balance_type","created","currency","fee","fee_details","net","object","reporting_category","type","description","exchange_rate","source"],"mutable":["amount","available_on","balance_type","created","currency","fee","fee_details","net","object","reporting_category","status","type","description","exchange_rate","source"],"lifecycles":{"status":["The transaction's net funds status in the Stripe balance","which are either `available` or `pending`."]}},"balances":{"table":"balances","primary_key":"id","labels":["id"],"readable":["id","available","livemode","object","pending","connect_reserved","instant_available","issuing","refund_and_dispute_prefunding"],"resolvable":["id","available","livemode","object","pending","connect_reserved","instant_available","issuing","refund_and_dispute_prefunding"],"mutable":["available","livemode","object","pending","connect_reserved","instant_available","issuing","refund_and_dispute_prefunding"],"lifecycles":{}},"bank_accounts":{"table":"bank_accounts","primary_key":"id","labels":["id","account_holder_name","bank_name"],"readable":["id","country","currency","last4","object","status","account","account_holder_name","account_holder_type","account_type","available_payout_methods","bank_name","customer","default_for_currency","fingerprint","future_requirements","metadata","requirements","routing_number"],"resolvable":["id","country","currency","last4","object","account","account_holder_name","account_holder_type","account_type","available_payout_methods","bank_name","customer","default_for_currency","fingerprint","future_requirements","metadata","requirements","routing_number"],"mutable":["country","currency","last4","object","status","account","account_holder_name","account_holder_type","account_type","available_payout_methods","bank_name","customer","default_for_currency","fingerprint","future_requirements","metadata","requirements","routing_number"],"lifecycles":{"status":["For bank accounts","possible values are `new`","`validated`","`verified`","`verification_failed`","`tokenized_account_number_deactivated` or `er…"]}},"billing_alerts":{"table":"billing_alerts","primary_key":"id","labels":["id","title"],"readable":["id","alert_type","livemode","object","title","status","usage_threshold"],"resolvable":["id","alert_type","livemode","object","title","usage_threshold"],"mutable":["alert_type","livemode","object","title","status","usage_threshold"],"lifecycles":{"status":["active","archived","inactive"]}},"billing_credit_balance_summaries":{"table":"billing_credit_balance_summaries","primary_key":"id","labels":["id"],"readable":["id","balances","customer","livemode","object","customer_account"],"resolvable":["id","balances","customer","livemode","object","customer_account"],"mutable":["balances","customer","livemode","object","customer_account"],"lifecycles":{}},"billing_credit_balance_transactions":{"table":"billing_credit_balance_transactions","primary_key":"id","labels":["id"],"readable":["id","created","credit_grant","effective_at","livemode","object","credit","debit","test_clock","type"],"resolvable":["id","created","credit_grant","effective_at","livemode","object","credit","debit","test_clock","type"],"mutable":["created","credit_grant","effective_at","livemode","object","credit","debit","test_clock","type"],"lifecycles":{}},"billing_meters":{"table":"billing_meters","primary_key":"id","labels":["id","display_name","event_name"],"readable":["id","created","customer_mapping","default_aggregation","display_name","event_name","livemode","object","status","status_transitions","updated","value_settings","event_time_window"],"resolvable":["id","created","customer_mapping","default_aggregation","display_name","event_name","livemode","object","status_transitions","updated","value_settings","event_time_window"],"mutable":["created","customer_mapping","default_aggregation","display_name","event_name","livemode","object","status","status_transitions","updated","value_settings","event_time_window"],"lifecycles":{"status":["active","inactive"]}},"capabilities":{"table":"capabilities","primary_key":"id","labels":["id"],"readable":["id","account","object","requested","status","future_requirements","requested_at","requirements"],"resolvable":["id","account","object","requested","future_requirements","requested_at","requirements"],"mutable":["account","object","requested","status","future_requirements","requested_at","requirements"],"lifecycles":{"status":["active","inactive","pending","unrequested"]}},"charges":{"table":"charges","primary_key":"id","labels":["id","receipt_email","receipt_number","receipt_url"],"readable":["id","amount","amount_captured","amount_refunded","billing_details","captured","created","currency","disputed","livemode","metadata","object","paid","refunded","status","application","application_fee","application_fee_amount","balance_transaction","calculated_statement_descriptor","customer","description","failure_balance_transaction","failure_code","failure_message","fraud_details","on_behalf_of","outcome","payment_intent","payment_method","payment_method_details","presentment_details","radar_options","receipt_email","receipt_number","receipt_url","refunds","review","shipping","source_transfer","statement_descriptor","statement_descriptor_suffix","transfer","transfer_data","transfer_group"],"resolvable":["id","amount","amount_captured","amount_refunded","billing_details","captured","created","currency","disputed","livemode","metadata","object","paid","refunded","application","application_fee","application_fee_amount","balance_transaction","calculated_statement_descriptor","customer","description","failure_balance_transaction","failure_code","failure_message","fraud_details","on_behalf_of","outcome","payment_intent","payment_method","payment_method_details","presentment_details","radar_options","receipt_email","receipt_number","receipt_url","refunds","review","shipping","source_transfer","statement_descriptor","statement_descriptor_suffix","transfer","transfer_data","transfer_group"],"mutable":["amount","amount_captured","amount_refunded","billing_details","captured","created","currency","disputed","livemode","metadata","object","paid","refunded","status","application","application_fee","application_fee_amount","balance_transaction","calculated_statement_descriptor","customer","description","failure_balance_transaction","failure_code","failure_message","fraud_details","on_behalf_of","outcome","payment_intent","payment_method","payment_method_details","presentment_details","radar_options","receipt_email","receipt_number","receipt_url","refunds","review","shipping","source_transfer","statement_descriptor","statement_descriptor_suffix","transfer","transfer_data","transfer_group"],"lifecycles":{"status":["failed","pending","succeeded"]}},"checkout_sessions":{"table":"checkout_sessions","primary_key":"id","labels":["id","client_reference_id","cancel_url","customer_email"],"readable":["id","automatic_tax","created","custom_fields","custom_text","expires_at","livemode","mode","object","payment_method_types","payment_status","shipping_options","client_reference_id","status","adaptive_pricing","after_expiration","allow_promotion_codes","amount_subtotal","amount_total","billing_address_collection","branding_settings","cancel_url","client_secret","collected_information","consent","consent_collection","currency","currency_conversion","customer","customer_account","customer_creation","customer_details","customer_email","discounts","excluded_payment_method_types","integration_identifier","invoice","invoice_creation","line_items","locale","managed_payments","metadata","name_collection","optional_items","origin_context","payment_intent","payment_link","payment_method_collection"],"resolvable":["id","automatic_tax","created","custom_fields","custom_text","expires_at","livemode","mode","object","payment_method_types","shipping_options","client_reference_id","adaptive_pricing","after_expiration","allow_promotion_codes","amount_subtotal","amount_total","billing_address_collection","branding_settings","cancel_url","client_secret","collected_information","consent","consent_collection","currency","currency_conversion","customer","customer_account","customer_creation","customer_details","customer_email","discounts","excluded_payment_method_types","integration_identifier","invoice","invoice_creation","line_items","locale","managed_payments","metadata","name_collection","optional_items","origin_context","payment_intent","payment_link","payment_method_collection"],"mutable":["automatic_tax","created","custom_fields","custom_text","expires_at","livemode","mode","object","payment_method_types","payment_status","shipping_options","status","adaptive_pricing","after_expiration","allow_promotion_codes","amount_subtotal","amount_total","billing_address_collection","branding_settings","cancel_url","client_secret","collected_information","consent","consent_collection","currency","currency_conversion","customer","customer_account","customer_creation","customer_details","customer_email","discounts","excluded_payment_method_types","integration_identifier","invoice","invoice_creation","line_items","locale","managed_payments","metadata","name_collection","optional_items","origin_context","payment_intent","payment_link","payment_method_collection"],"lifecycles":{"payment_status":["no_payment_required","paid","unpaid"],"status":["complete","expired","open"]}},"climate_orders":{"table":"climate_orders","primary_key":"id","labels":["id"],"readable":["id","amount_fees","amount_subtotal","amount_total","created","currency","delivery_details","expected_delivery_year","livemode","metadata","metric_tons","object","product","status","beneficiary","canceled_at","cancellation_reason","certificate","confirmed_at","delayed_at","delivered_at","product_substituted_at"],"resolvable":["id","amount_fees","amount_subtotal","amount_total","created","currency","delivery_details","expected_delivery_year","livemode","metadata","metric_tons","object","product","beneficiary","canceled_at","cancellation_reason","certificate","confirmed_at","delayed_at","delivered_at","product_substituted_at"],"mutable":["amount_fees","amount_subtotal","amount_total","created","currency","delivery_details","expected_delivery_year","livemode","metadata","metric_tons","object","product","status","beneficiary","canceled_at","cancellation_reason","certificate","confirmed_at","delayed_at","delivered_at","product_substituted_at"],"lifecycles":{"status":["awaiting_funds","canceled","confirmed","delivered","open"]}},"credit_notes":{"table":"credit_notes","primary_key":"id","labels":["id","number"],"readable":["id","amount","amount_shipping","created","currency","customer","discount_amount","discount_amounts","invoice","lines","livemode","number","object","pdf","post_payment_amount","pre_payment_amount","pretax_credit_amounts","refunds","status","subtotal","total","type","customer_account","customer_balance_transaction","effective_at","memo","metadata","out_of_band_amount","reason","shipping_cost","subtotal_excluding_tax","total_excluding_tax","total_taxes","voided_at"],"resolvable":["id","amount","amount_shipping","created","currency","customer","discount_amount","discount_amounts","invoice","lines","livemode","number","object","pdf","post_payment_amount","pre_payment_amount","pretax_credit_amounts","refunds","subtotal","total","type","customer_account","customer_balance_transaction","effective_at","memo","metadata","out_of_band_amount","reason","shipping_cost","subtotal_excluding_tax","total_excluding_tax","total_taxes","voided_at"],"mutable":["amount","amount_shipping","created","currency","customer","discount_amount","discount_amounts","invoice","lines","livemode","number","object","pdf","post_payment_amount","pre_payment_amount","pretax_credit_amounts","refunds","status","subtotal","total","type","customer_account","customer_balance_transaction","effective_at","memo","metadata","out_of_band_amount","reason","shipping_cost","subtotal_excluding_tax","total_excluding_tax","total_taxes","voided_at"],"lifecycles":{"status":["issued","void"]}},"disputes":{"table":"disputes","primary_key":"id","labels":["id"],"readable":["id","amount","balance_transactions","charge","created","currency","enhanced_eligibility_types","evidence","evidence_details","is_charge_refundable","livemode","metadata","object","reason","status","payment_intent","payment_method_details"],"resolvable":["id","amount","balance_transactions","charge","created","currency","enhanced_eligibility_types","evidence","evidence_details","is_charge_refundable","livemode","metadata","object","reason","payment_intent","payment_method_details"],"mutable":["amount","balance_transactions","charge","created","currency","enhanced_eligibility_types","evidence","evidence_details","is_charge_refundable","livemode","metadata","object","reason","status","payment_intent","payment_method_details"],"lifecycles":{"status":["lost","needs_response","prevented","under_review","warning_closed","warning_needs_response","warning_under_review","won"]}},"identity_verification_sessions":{"table":"identity_verification_sessions","primary_key":"id","labels":["id","client_reference_id","url"],"readable":["id","created","livemode","metadata","object","status","type","client_reference_id","client_secret","last_error","last_verification_report","options","provided_details","redaction","related_customer","related_customer_account","related_person","url","verification_flow","verified_outputs"],"resolvable":["id","created","livemode","metadata","object","type","client_reference_id","client_secret","last_error","last_verification_report","options","provided_details","redaction","related_customer","related_customer_account","related_person","url","verification_flow","verified_outputs"],"mutable":["created","livemode","metadata","object","status","type","client_secret","last_error","last_verification_report","options","provided_details","redaction","related_customer","related_customer_account","related_person","url","verification_flow","verified_outputs"],"lifecycles":{"status":["canceled","processing","requires_input","verified"]}},"invoice_rendering_templates":{"table":"invoice_rendering_templates","primary_key":"id","labels":["id"],"readable":["id","created","livemode","object","status","version","metadata","nickname"],"resolvable":["id","created","livemode","object","version","metadata","nickname"],"mutable":["created","livemode","object","status","version","metadata","nickname"],"lifecycles":{"status":["active","archived"]}},"invoices":{"table":"invoices","primary_key":"id","labels":["id","account_name","customer_email","customer_name"],"readable":["id","amount_due","amount_overpaid","amount_paid","amount_paid_off_stripe","amount_remaining","amount_shipping","attempt_count","attempted","auto_advance","automatic_tax","collection_method","created","currency","customer","default_tax_rates","discounts","issuer","lines","livemode","object","payment_settings","period_end","period_start","post_payment_credit_notes_amount","pre_payment_credit_notes_amount","starting_balance","status_transitions","subtotal","total","status","account_country","account_name","account_tax_ids","application","automatically_finalizes_at","billing_reason","confirmation_secret","custom_fields","customer_account","customer_address","customer_email","customer_name","customer_phone","customer_shipping","customer_tax_exempt","customer_tax_ids","default_payment_method"],"resolvable":["id","amount_due","amount_overpaid","amount_paid","amount_paid_off_stripe","amount_remaining","amount_shipping","attempt_count","attempted","auto_advance","automatic_tax","collection_method","created","currency","customer","default_tax_rates","discounts","issuer","lines","livemode","object","payment_settings","period_end","period_start","post_payment_credit_notes_amount","pre_payment_credit_notes_amount","starting_balance","status_transitions","subtotal","total","account_country","account_name","account_tax_ids","application","automatically_finalizes_at","billing_reason","confirmation_secret","custom_fields","customer_account","customer_address","customer_email","customer_name","customer_phone","customer_shipping","customer_tax_exempt","customer_tax_ids","default_payment_method"],"mutable":["amount_due","amount_overpaid","amount_paid","amount_paid_off_stripe","amount_remaining","amount_shipping","attempt_count","attempted","auto_advance","automatic_tax","collection_method","created","currency","customer","default_tax_rates","discounts","issuer","lines","livemode","object","payment_settings","period_end","period_start","post_payment_credit_notes_amount","pre_payment_credit_notes_amount","starting_balance","status_transitions","subtotal","total","status","account_country","account_name","account_tax_ids","application","automatically_finalizes_at","billing_reason","confirmation_secret","custom_fields","customer_account","customer_address","customer_email","customer_name","customer_phone","customer_shipping","customer_tax_exempt","customer_tax_ids","default_payment_method"],"lifecycles":{"status":["draft","open","paid","uncollectible","void"]}},"issuing_authorizations":{"table":"issuing_authorizations","primary_key":"id","labels":["id"],"readable":["id","amount","approved","authorization_method","balance_transactions","card","created","currency","livemode","merchant_amount","merchant_currency","merchant_data","metadata","object","request_history","status","transactions","verification_data","amount_details","card_presence","cardholder","fleet","fraud_challenges","fuel","network_data","pending_request","token","treasury","verified_by_fraud_challenge","wallet"],"resolvable":["id","amount","approved","authorization_method","balance_transactions","card","created","currency","livemode","merchant_amount","merchant_currency","merchant_data","metadata","object","request_history","transactions","verification_data","amount_details","card_presence","cardholder","fleet","fraud_challenges","fuel","network_data","pending_request","token","treasury","verified_by_fraud_challenge","wallet"],"mutable":["amount","approved","authorization_method","balance_transactions","card","created","currency","livemode","merchant_amount","merchant_currency","merchant_data","metadata","object","request_history","status","transactions","verification_data","amount_details","card_presence","cardholder","fleet","fraud_challenges","fuel","network_data","pending_request","token","treasury","verified_by_fraud_challenge","wallet"],"lifecycles":{"status":["closed","expired","pending","reversed"]}},"company_finance_handoffs":{"table":"company_finance_handoffs","primary_key":"id","labels":["handoff_ref"],"readable":["id","handoff_ref","core_record_id","system_record_id","source_system","source_table","requested_action","status","contract_id"],"resolvable":["handoff_ref","core_record_id","system_record_id","source_system","source_table","requested_action","contract_id"],"mutable":["handoff_ref","source_system","source_table","requested_action","status"],"lifecycles":{"status":["queued","linked","verified","completed"]}}}

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

def finance_records_agent(db_path, request=None, **kwargs):
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
_bf_orig_finance_records_agent = finance_records_agent
def _bf_friction_finance_records_agent(*_bf_args, **_bf_kwargs):
    import hashlib as _bf_hashlib, json as _bf_json, sqlite3 as _bf_sqlite3
    _bf_db = _bf_args[0] if _bf_args else _bf_kwargs.get("db_path")
    if not isinstance(_bf_db, str) or not _bf_db:
        return _bf_orig_finance_records_agent(*_bf_args, **_bf_kwargs)
    _bf_call = {}
    for _bf_k, _bf_v in _bf_kwargs.items():
        if _bf_k == "db_path":
            continue
        if isinstance(_bf_v, float) and _bf_v.is_integer():
            _bf_v = int(_bf_v)
        _bf_call[_bf_k] = _bf_v
    _bf_sig = "finance_records_agent|" + _bf_json.dumps(_bf_call, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
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
    return _bf_orig_finance_records_agent(*_bf_args, **_bf_kwargs)
_bf_friction_finance_records_agent.blobfish_original = _bf_orig_finance_records_agent
finance_records_agent = _bf_friction_finance_records_agent
