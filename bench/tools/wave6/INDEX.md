# wave6 — 205 MCP tools

| vendor server | tool | type | target tables |
|---|---|---|---|
| github | `finance_records_agent` | read | account_links, account_sessions, apple_pay_domains |
| github | `finance_workflow_agent` | write | account_links, account_sessions, apple_pay_domains |
| github | `lookup_finance_expense_report_with_employees` | read | employees, finance_expense_reports |
| github | `query_finance_expense_reports` | read | finance_expense_reports |
| github | `sheet_agent` | write | agent_sheet_rows, agent_sheets |
| github | `update_finance_expense_reports_status` | write | finance_expense_reports |
| google-calendar | `calendar_acl_list` | read | acls |
| google-calendar | `calendar_agent` | write | agent_events |
| google-calendar | `calendar_calendar_list_get` | read | calendar_list_entries |
| google-calendar | `calendar_calendar_list_insert` | write | calendar_list_entries |
| google-calendar | `calendar_calendar_list_list` | read | calendar_lists |
| google-calendar | `calendar_calendars_get` | read | calendars |
| google-calendar | `calendar_calendars_insert` | write | calendars |
| google-calendar | `create_scheduled_run` | write | agent_scheduled_runs |
| google-calendar | `list_scheduled_runs` | read | agent_scheduled_runs |
| google-calendar | `query_calendar_events` | read | agent_events |
| jira | `customer_support_records_agent` | read | activity_log_lists, admin_lists, admin_with_apps |
| jira | `customer_support_workflow_agent` | write | activity_log_lists, admin_lists, admin_with_apps |
| jira | `lookup_support_ticket_with_employees` | read | employees, support_tickets |
| jira | `query_support_tickets` | read | support_tickets |
| jira | `update_support_tickets_status` | write | support_tickets |
| netsuite-erp | `admin_emoji_list` | read | admin_emojis |
| netsuite-erp | `lookup_sourcing_purchase_order_with_sourcing_vendors` | read | sourcing_purchase_orders, sourcing_vendors |
| netsuite-erp | `purchase_order_create` | write | purchase_orders |
| netsuite-erp | `purchase_order_get` | read | purchase_orders |
| netsuite-erp | `purchase_orders_list` | read | purchase_orders |
| netsuite-erp | `query_sourcing_purchase_orders` | read | sourcing_purchase_orders |
| netsuite-erp | `update_sourcing_purchase_orders_status` | write | sourcing_purchase_orders |
| notion-docs | `document_agent` | write | agent_documents |
| notion-docs | `draft_matter_document` | write | matter_documents |
| notion-docs | `query_documents` | read | agent_documents |
| notion-docs | `query_matter_documents` | read | matter_documents |
| notion-docs | `read_file` | read | agent_files |
| notion-docs | `read_matter_document` | read | matter_documents |
| pagerduty-support | `case_create` | write | cases |
| pagerduty-support | `cases_list` | read | cases |
| pagerduty-support | `get_billing_alerts` | read | alerts |
| pagerduty-support | `get_billing_alerts_id` | read | billing_alerts |
| pagerduty-support | `post_billing_alerts` | write | billing_alerts |
| revops-core | `add_to_knowledge` | write | agent_knowledge |
| revops-core | `admin_apps_approved_list` | read | admin_apps_approveds |
| revops-core | `admin_apps_requests_list` | read | admin_apps_requests |
| revops-core | `admin_apps_restricted_list` | read | admin_apps_restricteds |
| revops-core | `admin_emoji_add` | write | admin_emojis |
| revops-core | `admin_emoji_rename` | write | admin_emojis |
| revops-core | `admin_invite_requests_approved_list` | read | admin_invite_requests_approveds |
| revops-core | `admin_invite_requests_denied_list` | read | admin_invite_requests_denieds |
| revops-core | `admin_invite_requests_list` | read | admin_invite_requests |
| revops-core | `calls_add` | write | calls |
| revops-core | `calls_info` | read | calls |
| revops-core | `calls_update` | write | calls |
| revops-core | `case_get` | read | cases |
| revops-core | `create_api_keys` | write | api_keys |
| revops-core | `create_article` | write | articles |
| revops-core | `create_collection` | write | collections |
| revops-core | `create_content_import_source` | write | content_import_sources |
| revops-core | `create_data_export` | write | data_exports |
| revops-core | `create_news_item` | write | news_items |
| revops-core | `create_playbook` | write | agent_playbooks |
| revops-core | `customer_create` | write | customers |
| revops-core | `customer_get` | read | customers |
| revops-core | `customers_list` | read | customers |
| revops-core | `files_remote_add` | write | files |
| revops-core | `get_access_settings_activity` | read | activities |
| revops-core | `get_api_keys` | read | api_keys |
| revops-core | `get_application_fees` | read | application_fees |
| revops-core | `get_automation_link_stat` | read | automations_link_stats_responses |
| revops-core | `get_balance_transactions` | read | balance_transactions |
| revops-core | `get_billing_credit_balance_summary` | read | billing_credit_balance_summaries |
| revops-core | `get_billing_credit_balance_transactions_id` | read | billing_credit_balance_transactions |
| revops-core | `get_billing_meters_id` | read | billing_meters |
| revops-core | `get_campaigns` | read | campaigns |
| revops-core | `get_categories` | read | categories |
| revops-core | `get_content_import_source` | read | content_import_sources |
| revops-core | `get_credit_notes` | read | credit_notes |
| revops-core | `get_entitlements_active_entitlements` | read | active_entitlements |
| revops-core | `get_ips_assigned` | read | assigneds |
| revops-core | `get_issuing_authorizations` | read | authorizations |
| revops-core | `get_marketing_singlesends` | read | singlesends |
| revops-core | `get_suppression_blocks` | read | blocks |
| revops-core | `get_suppression_bounces` | read | bounces |
| revops-core | `get_tracking_settings_click` | read | click_trackings |
| revops-core | `getall_automation_stats` | read | automations_responses |
| revops-core | `human_resources_records_agent` | read | hr_leave_requests, hr_performance_reviews |
| revops-core | `human_resources_workflow_agent` | write | hr_leave_requests, hr_performance_reviews |
| revops-core | `identify_admin` | read | admin_with_apps |
| revops-core | `journal_entries_list` | read | journal_entries |
| revops-core | `journal_entry_create` | write | journal_entries |
| revops-core | `journal_entry_get` | read | journal_entries |
| revops-core | `list_admins` | read | admin_lists |
| revops-core | `list_articles` | read | article_lists |
| revops-core | `list_away_status_reasons` | read | away_status_reason_lists |
| revops-core | `list_playbooks` | read | agent_playbooks |
| revops-core | `lookup_company_finance_handoff_with_volume_bands` | read | company_finance_handoffs, volume_bands |
| revops-core | `lookup_company_marketing_handoff_with_volume_bands` | read | company_marketing_handoffs, volume_bands |
| revops-core | `lookup_company_sales_handoff_with_volume_bands` | read | company_sales_handoffs, volume_bands |
| revops-core | `lookup_company_sourcing_handoff_with_volume_bands` | read | company_sourcing_handoffs, volume_bands |
| revops-core | `lookup_employee_with_departments` | read | departments, employees |
| revops-core | `lookup_employee_work_assignment_with_employees` | read | employee_work_assignments, employees |
| revops-core | `lookup_finance_budget_with_departments` | read | departments, finance_budgets |
| revops-core | `lookup_hr_leave_request_with_employees` | read | employees, hr_leave_requests |
| revops-core | `lookup_marketing_campaign_with_employees` | read | employees, marketing_campaigns |
| revops-core | `lookup_marketing_content_asset_with_marketing_campaigns` | read | marketing_campaigns, marketing_content_assets |
| revops-core | `lookup_sourcing_vendor_with_employees` | read | employees, sourcing_vendors |
| revops-core | `opportunities_list` | read | opportunities |
| revops-core | `patch_api_keys_api_key_id` | write | api_keys |
| revops-core | `patch_campaigns_campaign_id` | write | campaigns |
| revops-core | `patch_marketing_singlesends_id` | write | singlesends |
| revops-core | `post_billing_meters` | write | billing_meters |
| revops-core | `post_campaigns` | write | campaigns |
| revops-core | `post_climate_orders` | write | climate_orders |
| revops-core | `post_identity_verification_sessions` | write | identity_verification_sessions |
| revops-core | `post_marketing_singlesends` | write | singlesends |
| revops-core | `post_test_helpers_issuing_authorizations` | write | issuing_authorizations |
| revops-core | `query_company_finance_handoffs` | read | company_finance_handoffs |
| revops-core | `query_company_marketing_handoffs` | read | company_marketing_handoffs |
| revops-core | `query_company_sales_handoffs` | read | company_sales_handoffs |
| revops-core | `query_company_sourcing_handoffs` | read | company_sourcing_handoffs |
| revops-core | `query_departments` | read | departments |
| revops-core | `query_employee_work_assignments` | read | employee_work_assignments |
| revops-core | `query_employees` | read | employees |
| revops-core | `query_files` | read | agent_files |
| revops-core | `query_finance_budgets` | read | finance_budgets |
| revops-core | `query_hr_leave_requests` | read | hr_leave_requests |
| revops-core | `query_hr_performance_reviews` | read | hr_performance_reviews |
| revops-core | `query_marketing_campaigns` | read | marketing_campaigns |
| revops-core | `query_marketing_content_assets` | read | marketing_content_assets |
| revops-core | `query_sales_opportunities` | read | sales_opportunities |
| revops-core | `query_sourcing_vendors` | read | sourcing_vendors |
| revops-core | `retrieve_admin` | read | admins |
| revops-core | `retrieve_article` | read | articles |
| revops-core | `retrieve_collection` | read | collections |
| revops-core | `retrieve_conversation` | read | conversations |
| revops-core | `retrieve_news_item` | read | news_items |
| revops-core | `save_memory` | write | agent_memories |
| revops-core | `search_knowledge` | read | agent_knowledge |
| revops-core | `search_memory` | read | agent_memories |
| revops-core | `task_create` | write | tasks |
| revops-core | `task_get` | read | tasks |
| revops-core | `tasks_list` | read | tasks |
| revops-core | `update_article` | write | articles |
| revops-core | `update_collection` | write | collections |
| revops-core | `update_company_finance_handoffs_status` | write | company_finance_handoffs |
| revops-core | `update_company_marketing_handoffs_status` | write | company_marketing_handoffs |
| revops-core | `update_company_sales_handoffs_status` | write | company_sales_handoffs |
| revops-core | `update_company_sourcing_handoffs_status` | write | company_sourcing_handoffs |
| revops-core | `update_content_import_source` | write | content_import_sources |
| revops-core | `update_departments_department_code` | write | departments |
| revops-core | `update_employee_work_assignments_status` | write | employee_work_assignments |
| revops-core | `update_employees_status` | write | employees |
| revops-core | `update_finance_budgets_status` | write | finance_budgets |
| revops-core | `update_hr_leave_requests_status` | write | hr_leave_requests |
| revops-core | `update_hr_performance_reviews_status` | write | hr_performance_reviews |
| revops-core | `update_marketing_campaigns_status` | write | marketing_campaigns |
| revops-core | `update_marketing_content_assets_status` | write | marketing_content_assets |
| revops-core | `update_news_item` | write | news_items |
| revops-core | `update_sales_opportunities_status` | write | sales_opportunities |
| revops-core | `update_sourcing_vendors_status` | write | sourcing_vendors |
| revops-core | `vendor_create` | write | vendors |
| revops-core | `vendor_get` | read | vendors |
| revops-core | `vendors_list` | read | vendors |
| salesforce-crm | `account_create` | write | accounts |
| salesforce-crm | `account_get` | read | accounts |
| salesforce-crm | `accounts_list` | read | accounts |
| salesforce-crm | `contact_create` | write | contacts |
| salesforce-crm | `contact_get` | read | contacts |
| salesforce-crm | `contacts_list` | read | contacts |
| salesforce-crm | `core_records_agent` | read | accept_all, account_tiering_standard, activity_logging_standards |
| salesforce-crm | `core_workflow_agent` | write | accept_all, account_tiering_standard, activity_logging_standards |
| salesforce-crm | `get_accounts_account_capabilities` | read | capabilities |
| salesforce-crm | `get_contactdb_segments_segment_id` | read | contactdb_segments |
| salesforce-crm | `get_customers_customer_bank_accounts` | read | bank_accounts |
| salesforce-crm | `get_mc_contacts_exports_id` | read | contact_exports |
| salesforce-crm | `lookup_sales_lead_with_employees` | read | employees, sales_leads |
| salesforce-crm | `lookup_sales_opportunity_with_sales_leads` | read | sales_leads, sales_opportunities |
| salesforce-crm | `marketing_records_agent` | read | all_segments_responses, api_keys, automations_link_stats_responses |
| salesforce-crm | `marketing_workflow_agent` | write | all_segments_responses, api_keys, automations_link_stats_responses |
| salesforce-crm | `opportunity_create` | write | opportunities |
| salesforce-crm | `opportunity_get` | read | opportunities |
| salesforce-crm | `post_account_links` | write | account_links |
| salesforce-crm | `post_account_sessions` | write | account_sessions |
| salesforce-crm | `post_marketing_contacts_batch` | write | batches |
| salesforce-crm | `query_sales_leads` | read | sales_leads |
| salesforce-crm | `sales_records_agent` | read | accounts, cases, company_sales_handoffs |
| salesforce-crm | `sales_workflow_agent` | write | accounts, cases, company_sales_handoffs |
| salesforce-crm | `sourcing_records_agent` | read | company_sourcing_handoffs, customers, journal_entries |
| salesforce-crm | `sourcing_workflow_agent` | write | company_sourcing_handoffs, customers, journal_entries |
| salesforce-crm | `update_sales_leads_status` | write | sales_leads |
| sendgrid-email | `get_categories_stats` | read | category_stats |
| sendgrid-email | `organization_records_agent` | read | departments, employee_work_assignments, employees |
| sendgrid-email | `organization_workflow_agent` | write | departments, employee_work_assignments, employees |
| slack | `admin_conversations_create` | write | admin_conversations |
| slack | `admin_conversations_ekm_list_original_connected_channel_info` | read | admin_conversations_ekms |
| slack | `admin_conversations_get_conversation_prefs` | read | admin_conversations |
| slack | `admin_conversations_rename` | write | admin_conversations |
| slack | `admin_conversations_restrict_access_list_groups` | read | admin_conversations_restrict_accesses |
| slack | `chat_scheduled_messages_list` | read | messages |
| slack | `conversations_create` | write | channels |
| stripe-billing | `get_charges` | read | charges |
| stripe-billing | `get_charges_charge_dispute` | read | disputes |
| stripe-billing | `get_invoice_rendering_templates` | read | invoice_rendering_templates |
| stripe-billing | `get_invoices` | read | invoices |
| stripe-billing | `get_payment_intents_intent_amount_details_line_items` | read | amount_details_line_items |
| stripe-billing | `post_charges` | write | charges |
| stripe-billing | `post_charges_charge_dispute_close` | write | disputes |
