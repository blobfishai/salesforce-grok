# wave6 — 443 MCP tools

| vendor server | tool | type | target tables |
|---|---|---|---|
| github | `finance_records_agent` | read | account_links, account_sessions, apple_pay_domains |
| github | `finance_workflow_agent` | write | account_links, account_sessions, apple_pay_domains |
| github | `gh_branch_get` | read | gh_branches |
| github | `gh_branches_list` | read | gh_branches |
| github | `gh_commit_get` | read | gh_commits |
| github | `gh_commits_list` | read | gh_commits |
| github | `gh_issue_comment_create` | write | gh_issue_comments |
| github | `gh_issue_comments_list` | read | gh_issue_comments |
| github | `gh_issue_create` | write | gh_issues, gh_repos, gh_pull_requests |
| github | `gh_issue_get` | read | gh_issues |
| github | `gh_issue_update` | write | gh_issues |
| github | `gh_issues_list` | read | gh_issues |
| github | `gh_pull_create` | write | gh_pull_requests, gh_repos, gh_issues |
| github | `gh_pull_files_list` | read | gh_pull_files |
| github | `gh_pull_get` | read | gh_pull_requests |
| github | `gh_pull_merge` | write | gh_pull_requests, gh_commits, gh_branches |
| github | `gh_pull_review_create` | write | gh_pull_reviews, gh_pull_requests |
| github | `gh_pull_reviews_list` | read | gh_pull_reviews |
| github | `gh_pull_update` | write | gh_pull_requests |
| github | `gh_pulls_list` | read | gh_pull_requests |
| github | `gh_release_create` | write | gh_releases |
| github | `gh_releases_list` | read | gh_releases |
| github | `gh_repo_get` | read | gh_repos |
| github | `gh_repos_list` | read | gh_repos |
| github | `gh_search_code` | read | gh_code_index |
| github | `gh_search_issues` | read | gh_issues |
| github | `gh_workflow_run_get` | read | gh_workflow_runs |
| github | `gh_workflow_run_rerun` | write | gh_workflow_runs |
| github | `gh_workflow_runs_list` | read | gh_workflow_runs |
| github | `lookup_finance_expense_report_with_employees` | read | employees, finance_expense_reports |
| github | `query_finance_expense_reports` | read | finance_expense_reports |
| github | `sheet_agent` | write | agent_sheet_rows, agent_sheets |
| github | `update_finance_expense_reports_status` | write | finance_expense_reports |
| google-calendar | `calendar_acl_delete` | write | acls |
| google-calendar | `calendar_acl_insert` | write | acls |
| google-calendar | `calendar_acl_list` | read | acls |
| google-calendar | `calendar_agent` | write | agent_events |
| google-calendar | `calendar_calendar_list_get` | read | calendar_list_entries |
| google-calendar | `calendar_calendar_list_insert` | write | calendar_list_entries |
| google-calendar | `calendar_calendar_list_list` | read | calendar_lists |
| google-calendar | `calendar_calendars_delete` | write | calendars |
| google-calendar | `calendar_calendars_get` | read | calendars |
| google-calendar | `calendar_calendars_insert` | write | calendars |
| google-calendar | `calendar_calendars_update` | write | calendars |
| google-calendar | `calendar_colors_get` | read | colors |
| google-calendar | `calendar_events_delete` | write | agent_events |
| google-calendar | `calendar_events_get` | read | agent_events, cal_event_details, cal_event_attendees |
| google-calendar | `calendar_events_insert` | write | agent_events, cal_event_details, cal_event_attendees |
| google-calendar | `calendar_events_instances` | read | agent_events, cal_event_details |
| google-calendar | `calendar_events_list` | read | agent_events, cal_event_details, cal_event_attendees |
| google-calendar | `calendar_events_move` | write | cal_event_details, agent_events, calendars |
| google-calendar | `calendar_events_patch` | write | agent_events, cal_event_details, cal_event_attendees |
| google-calendar | `calendar_events_quick_add` | write | agent_events, cal_event_details, cal_settings |
| google-calendar | `calendar_events_update` | write | agent_events, cal_event_details, cal_event_attendees |
| google-calendar | `calendar_freebusy_query` | read | cal_event_details, agent_events, calendars |
| google-calendar | `calendar_settings_list` | read | cal_settings |
| google-calendar | `create_scheduled_run` | write | agent_scheduled_runs |
| google-calendar | `list_scheduled_runs` | read | agent_scheduled_runs |
| google-calendar | `query_calendar_events` | read | agent_events |
| jira | `customer_support_records_agent` | read | activity_log_lists, admin_lists, admin_with_apps |
| jira | `customer_support_workflow_agent` | write | activity_log_lists, admin_lists, admin_with_apps |
| jira | `jira_board_get` | read | jira_boards |
| jira | `jira_boards_list` | read | jira_boards |
| jira | `jira_comment_add` | write | jira_comments |
| jira | `jira_comments_list` | read | jira_comments |
| jira | `jira_issue_assign` | write | jira_issues |
| jira | `jira_issue_create` | write | jira_issues, jira_projects |
| jira | `jira_issue_delete` | write | jira_issues |
| jira | `jira_issue_get` | read | jira_issues |
| jira | `jira_issue_transition` | write | jira_issues, jira_transitions, jira_comments |
| jira | `jira_issue_update` | write | jira_issues |
| jira | `jira_labels_list` | read | jira_issues |
| jira | `jira_priorities_list` | read | jira_priorities |
| jira | `jira_project_components_list` | read | jira_components |
| jira | `jira_project_get` | read | jira_projects |
| jira | `jira_project_versions_list` | read | jira_versions |
| jira | `jira_projects_list` | read | jira_projects |
| jira | `jira_search` | read | jira_issues |
| jira | `jira_sprint_get` | read | jira_sprints |
| jira | `jira_sprint_issues_list` | read | jira_issues |
| jira | `jira_sprints_list` | read | jira_sprints |
| jira | `jira_statuses_list` | read | jira_statuses |
| jira | `jira_transitions_list` | read | jira_transitions, jira_issues |
| jira | `jira_users_search` | read | employees |
| jira | `jira_watchers_add` | write | jira_watchers |
| jira | `jira_watchers_list` | read | jira_watchers |
| jira | `jira_worklog_add` | write | jira_worklogs |
| jira | `jira_worklogs_list` | read | jira_worklogs |
| jira | `lookup_support_ticket_with_employees` | read | employees, support_tickets |
| jira | `query_support_tickets` | read | support_tickets |
| jira | `update_support_tickets_status` | write | support_tickets |
| netsuite-erp | `erp_credit_memo_create` | write | erp_credit_memos |
| netsuite-erp | `erp_credit_memos_list` | read | erp_credit_memos |
| netsuite-erp | `erp_currencies_list` | read | erp_currencies |
| netsuite-erp | `erp_customer_payment_create` | write | erp_customer_payments, erp_invoices |
| netsuite-erp | `erp_customer_payments_list` | read | erp_customer_payments |
| netsuite-erp | `erp_inventory_adjustment_create` | write | erp_inventory_levels |
| netsuite-erp | `erp_inventory_levels_list` | read | erp_inventory_levels |
| netsuite-erp | `erp_invoice_create` | write | erp_invoices |
| netsuite-erp | `erp_invoice_get` | read | erp_invoices |
| netsuite-erp | `erp_invoices_list` | read | erp_invoices |
| netsuite-erp | `erp_item_create` | write | erp_items |
| netsuite-erp | `erp_item_get` | read | erp_items |
| netsuite-erp | `erp_items_list` | read | erp_items |
| netsuite-erp | `erp_sales_order_create` | write | erp_sales_orders |
| netsuite-erp | `erp_sales_order_get` | read | erp_sales_orders |
| netsuite-erp | `erp_sales_order_update_status` | write | erp_sales_orders |
| netsuite-erp | `erp_sales_orders_list` | read | erp_sales_orders |
| netsuite-erp | `erp_saved_search_run` | read | erp_sales_orders |
| netsuite-erp | `erp_subsidiaries_list` | read | erp_subsidiaries |
| netsuite-erp | `erp_vendor_bill_approve` | write | erp_vendor_bills |
| netsuite-erp | `erp_vendor_bill_create` | write | erp_vendor_bills |
| netsuite-erp | `erp_vendor_bill_get` | read | erp_vendor_bills |
| netsuite-erp | `erp_vendor_bills_list` | read | erp_vendor_bills |
| netsuite-erp | `lookup_sourcing_purchase_order_with_sourcing_vendors` | read | sourcing_purchase_orders, sourcing_vendors |
| netsuite-erp | `purchase_order_create` | write | purchase_orders |
| netsuite-erp | `purchase_order_get` | read | purchase_orders |
| netsuite-erp | `purchase_orders_list` | read | purchase_orders |
| netsuite-erp | `query_sourcing_purchase_orders` | read | sourcing_purchase_orders |
| netsuite-erp | `update_sourcing_purchase_orders_status` | write | sourcing_purchase_orders |
| notion-docs | `document_agent` | write | agent_documents |
| notion-docs | `draft_matter_document` | write | matter_documents |
| notion-docs | `notion_block_delete` | write | notion_blocks |
| notion-docs | `notion_block_get` | read | notion_blocks |
| notion-docs | `notion_blocks_append` | write | notion_blocks, notion_pages |
| notion-docs | `notion_blocks_children_list` | read | notion_blocks |
| notion-docs | `notion_comment_create` | write | notion_comments |
| notion-docs | `notion_comments_list` | read | notion_comments |
| notion-docs | `notion_database_create` | write | notion_databases |
| notion-docs | `notion_database_get` | read | notion_databases |
| notion-docs | `notion_database_query` | read | notion_database_rows, notion_databases |
| notion-docs | `notion_database_row_create` | write | notion_database_rows |
| notion-docs | `notion_database_row_update` | write | notion_database_rows |
| notion-docs | `notion_databases_list` | read | notion_databases |
| notion-docs | `notion_page_archive` | write | notion_pages |
| notion-docs | `notion_page_create` | write | notion_pages |
| notion-docs | `notion_page_get` | read | notion_pages |
| notion-docs | `notion_page_properties_get` | read | notion_database_rows |
| notion-docs | `notion_page_update` | write | notion_pages |
| notion-docs | `notion_search` | read | notion_pages, notion_databases |
| notion-docs | `notion_user_get` | read | notion_users |
| notion-docs | `notion_users_list` | read | notion_users |
| notion-docs | `query_documents` | read | agent_documents |
| notion-docs | `query_matter_documents` | read | matter_documents |
| notion-docs | `read_file` | read | agent_files |
| notion-docs | `read_matter_document` | read | matter_documents |
| pagerduty-support | `case_create` | write | cases |
| pagerduty-support | `cases_list` | read | cases |
| pagerduty-support | `get_billing_alerts` | read | alerts |
| pagerduty-support | `get_billing_alerts_id` | read | billing_alerts |
| pagerduty-support | `pd_escalation_policies_list` | read | pd_escalation_policies |
| pagerduty-support | `pd_escalation_policy_get` | read | pd_escalation_policies |
| pagerduty-support | `pd_incident_create` | write | pd_incidents, pd_services, pd_priorities |
| pagerduty-support | `pd_incident_get` | read | pd_incidents |
| pagerduty-support | `pd_incident_log_entries_list` | read | pd_log_entries |
| pagerduty-support | `pd_incident_manage` | write | pd_incidents, pd_log_entries, pd_oncalls |
| pagerduty-support | `pd_incident_note_create` | write | pd_incident_notes, pd_incidents, pd_users |
| pagerduty-support | `pd_incident_notes_list` | read | pd_incident_notes |
| pagerduty-support | `pd_incidents_list` | read | pd_incidents |
| pagerduty-support | `pd_maintenance_window_create` | write | pd_maintenance_windows |
| pagerduty-support | `pd_maintenance_windows_list` | read | pd_maintenance_windows |
| pagerduty-support | `pd_oncalls_list` | read | pd_oncalls, pd_users, pd_schedules |
| pagerduty-support | `pd_priorities_list` | read | pd_priorities |
| pagerduty-support | `pd_schedule_get` | read | pd_schedules |
| pagerduty-support | `pd_schedule_overrides_create` | write | pd_schedule_overrides |
| pagerduty-support | `pd_schedules_list` | read | pd_schedules |
| pagerduty-support | `pd_service_create` | write | pd_services |
| pagerduty-support | `pd_service_get` | read | pd_services |
| pagerduty-support | `pd_service_update` | write | pd_services |
| pagerduty-support | `pd_services_list` | read | pd_services |
| pagerduty-support | `pd_team_get` | read | pd_teams |
| pagerduty-support | `pd_teams_list` | read | pd_teams |
| pagerduty-support | `pd_user_get` | read | pd_users |
| pagerduty-support | `pd_users_list` | read | pd_users |
| pagerduty-support | `post_billing_alerts` | write | billing_alerts |
| revops-core | `add_to_knowledge` | write | agent_knowledge |
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
| revops-core | `get_api_keys` | read | api_keys |
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
| revops-core | `get_marketing_singlesends` | read | singlesends |
| revops-core | `get_suppression_blocks` | read | blocks |
| revops-core | `get_suppression_bounces` | read | bounces |
| revops-core | `getall_automation_stats` | read | automations_responses |
| revops-core | `human_resources_records_agent` | read | hr_leave_requests, hr_performance_reviews |
| revops-core | `human_resources_workflow_agent` | write | hr_leave_requests, hr_performance_reviews |
| revops-core | `identify_admin` | read | admin_with_apps |
| revops-core | `journal_entries_list` | read | journal_entries |
| revops-core | `journal_entry_create` | write | journal_entries |
| revops-core | `journal_entry_get` | read | journal_entries |
| revops-core | `list_admins` | read | admin_lists |
| revops-core | `list_articles` | read | article_lists |
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
| revops-core | `post_marketing_singlesends` | write | singlesends |
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
| salesforce-crm | `account_health_list` | read | account_health |
| salesforce-crm | `account_health_update` | write | account_health |
| salesforce-crm | `account_usage_list` | read | account_usage |
| salesforce-crm | `accounts_list` | read | accounts |
| salesforce-crm | `aggregate_query` | read | sales_opportunities, service_cases, sales_leads |
| salesforce-crm | `campaign_touches_list` | read | campaign_touches |
| salesforce-crm | `case_history_list` | read | case_history |
| salesforce-crm | `case_messages_list` | read | case_messages |
| salesforce-crm | `contact_create` | write | contacts |
| salesforce-crm | `contact_get` | read | contacts |
| salesforce-crm | `contacts_list` | read | contacts |
| salesforce-crm | `core_records_agent` | read | accept_all, account_tiering_standard, activity_logging_standards |
| salesforce-crm | `core_workflow_agent` | write | accept_all, account_tiering_standard, activity_logging_standards |
| salesforce-crm | `customer_profile_get` | read | customer_profiles |
| salesforce-crm | `customer_profiles_list` | read | customer_profiles |
| salesforce-crm | `email_messages_list` | read | email_messages |
| salesforce-crm | `email_thread_classify` | write | email_threads |
| salesforce-crm | `email_threads_list` | read | email_threads |
| salesforce-crm | `forecast_submissions_list` | read | forecast_submissions |
| salesforce-crm | `forecast_submit` | write | forecast_submissions |
| salesforce-crm | `get_contactdb_segments_segment_id` | read | contactdb_segments |
| salesforce-crm | `get_mc_contacts_exports_id` | read | contact_exports |
| salesforce-crm | `issue_taxonomy_list` | read | issue_taxonomy |
| salesforce-crm | `lead_create` | write | sales_leads |
| salesforce-crm | `lead_find_duplicates` | read | sales_leads |
| salesforce-crm | `lead_merge` | write | sales_leads, sales_opportunities, lead_merge_log |
| salesforce-crm | `lead_update_fields` | write | sales_leads |
| salesforce-crm | `lookup_sales_lead_with_employees` | read | employees, sales_leads |
| salesforce-crm | `lookup_sales_opportunity_with_sales_leads` | read | sales_leads, sales_opportunities |
| salesforce-crm | `marketing_records_agent` | read | all_segments_responses, api_keys, automations_link_stats_responses |
| salesforce-crm | `marketing_workflow_agent` | write | all_segments_responses, api_keys, automations_link_stats_responses |
| salesforce-crm | `opportunity_create` | write | opportunities |
| salesforce-crm | `opportunity_get` | read | opportunities |
| salesforce-crm | `post_marketing_contacts_batch` | write | batches |
| salesforce-crm | `product_catalog_list` | read | product_catalog_items |
| salesforce-crm | `query_sales_leads` | read | sales_leads |
| salesforce-crm | `quote_get` | read | sales_quotes |
| salesforce-crm | `quote_lines_list` | read | sales_quote_lines |
| salesforce-crm | `quote_update_status` | write | sales_quotes |
| salesforce-crm | `quotes_list` | read | sales_quotes |
| salesforce-crm | `rep_quotas_list` | read | rep_quotas |
| salesforce-crm | `sales_records_agent` | read | accounts, cases, company_sales_handoffs |
| salesforce-crm | `sales_workflow_agent` | write | accounts, cases, company_sales_handoffs |
| salesforce-crm | `sequence_enroll_lead` | write | outreach_enrollments |
| salesforce-crm | `sequence_enrollment_update` | write | outreach_enrollments |
| salesforce-crm | `sequence_enrollments_list` | read | outreach_enrollments |
| salesforce-crm | `sequence_steps_list` | read | outreach_sequence_steps |
| salesforce-crm | `sequences_list` | read | outreach_sequences |
| salesforce-crm | `service_case_get` | read | service_cases |
| salesforce-crm | `service_case_update_status` | write | service_cases |
| salesforce-crm | `service_cases_list` | read | service_cases |
| salesforce-crm | `signature_envelope_create` | write | signature_envelopes |
| salesforce-crm | `signature_envelope_update` | write | signature_envelopes |
| salesforce-crm | `signature_envelopes_list` | read | signature_envelopes |
| salesforce-crm | `sourcing_records_agent` | read | company_sourcing_handoffs, customers, journal_entries |
| salesforce-crm | `sourcing_workflow_agent` | write | company_sourcing_handoffs, customers, journal_entries |
| salesforce-crm | `update_sales_leads_status` | write | sales_leads |
| sendgrid-email | `get_categories_stats` | read | category_stats |
| sendgrid-email | `organization_records_agent` | read | departments, employee_work_assignments, employees |
| sendgrid-email | `organization_workflow_agent` | write | departments, employee_work_assignments, employees |
| sendgrid-email | `post_mail_send` | write | sg_mail_sends, sg_templates, sg_template_versions |
| sendgrid-email | `sg_api_keys_list` | read | sg_api_keys |
| sendgrid-email | `sg_blocks_delete` | write | blocks |
| sendgrid-email | `sg_bounces_delete` | write | bounces |
| sendgrid-email | `sg_contacts_list` | read | sg_contacts |
| sendgrid-email | `sg_contacts_search` | read | sg_contacts |
| sendgrid-email | `sg_contacts_upsert` | write | sg_contacts |
| sendgrid-email | `sg_domain_authenticate` | write | authentication_domains |
| sendgrid-email | `sg_domains_list` | read | authentication_domains |
| sendgrid-email | `sg_global_suppressions_add` | write | sg_global_suppressions |
| sendgrid-email | `sg_global_suppressions_list` | read | sg_global_suppressions |
| sendgrid-email | `sg_list_add_contact` | write | sg_list_members, sg_lists, sg_contacts |
| sendgrid-email | `sg_lists_create` | write | sg_lists |
| sendgrid-email | `sg_lists_list` | read | sg_lists |
| sendgrid-email | `sg_mail_sends_list` | read | sg_mail_sends |
| sendgrid-email | `sg_segments_list` | read | contactdb_segments |
| sendgrid-email | `sg_senders_create` | write | sg_senders |
| sendgrid-email | `sg_senders_get` | read | sg_senders |
| sendgrid-email | `sg_senders_list` | read | sg_senders |
| sendgrid-email | `sg_stats_by_category` | read | sg_mail_sends, category_stats |
| sendgrid-email | `sg_stats_get` | read | sg_mail_sends, blocks, bounces |
| sendgrid-email | `sg_suppressions_add` | write | sg_suppressions, suppression_groups |
| sendgrid-email | `sg_suppressions_list` | read | sg_suppressions |
| sendgrid-email | `sg_template_version_create` | write | sg_template_versions |
| sendgrid-email | `sg_templates_create` | write | sg_templates |
| sendgrid-email | `sg_templates_get` | read | sg_templates |
| sendgrid-email | `sg_templates_list` | read | sg_templates |
| sendgrid-email | `sg_templates_update` | write | sg_templates |
| sendgrid-email | `sg_unsubscribe_groups_create` | write | suppression_groups |
| sendgrid-email | `sg_unsubscribe_groups_list` | read | suppression_groups |
| slack | `admin_conversations_create` | write | admin_conversations |
| slack | `admin_conversations_rename` | write | admin_conversations |
| slack | `chat_delete` | write | messages, channels |
| slack | `chat_post_message` | write | messages, channels |
| slack | `chat_schedule_message` | write | slack_scheduled_messages |
| slack | `chat_scheduled_messages_list` | read | messages |
| slack | `chat_update` | write | messages, channels |
| slack | `conversations_archive` | write | channels |
| slack | `conversations_create` | write | channels |
| slack | `conversations_history` | read | messages, channels |
| slack | `conversations_info` | read | channels |
| slack | `conversations_invite` | write | slack_channel_members, channels, slack_users |
| slack | `conversations_join` | write | slack_channel_members, channels |
| slack | `conversations_list` | read | channels |
| slack | `conversations_members` | read | slack_channel_members |
| slack | `conversations_replies` | read | messages, channels |
| slack | `conversations_set_purpose` | write | channels |
| slack | `conversations_set_topic` | write | channels |
| slack | `emoji_list` | read | admin_emojis |
| slack | `pins_add` | write | slack_pins |
| slack | `pins_list` | read | slack_pins |
| slack | `pins_remove` | write | slack_pins, channels |
| slack | `reactions_add` | write | slack_reactions, channels, messages |
| slack | `reactions_get` | read | slack_reactions |
| slack | `reactions_remove` | write | slack_reactions, channels |
| slack | `search_messages` | read | messages |
| slack | `team_info` | read | slack_team |
| slack | `usergroups_create` | write | slack_usergroups |
| slack | `usergroups_list` | read | slack_usergroups |
| slack | `usergroups_update` | write | slack_usergroups |
| slack | `users_info` | read | slack_users |
| slack | `users_list` | read | slack_users |
| slack | `users_lookup_by_email` | read | slack_users |
| slack | `users_set_presence` | write | slack_users |
| stripe-billing | `delete_subscriptions_subscription` | write | subscriptions |
| stripe-billing | `get_balance` | read | balance_transactions |
| stripe-billing | `get_charges` | read | charges |
| stripe-billing | `get_charges_charge_dispute` | read | disputes |
| stripe-billing | `get_coupons` | read | coupons |
| stripe-billing | `get_customers` | read | customers |
| stripe-billing | `get_customers_customer` | read | customers |
| stripe-billing | `get_disputes` | read | disputes |
| stripe-billing | `get_events` | read | stripe_events |
| stripe-billing | `get_invoice_rendering_templates` | read | invoice_rendering_templates |
| stripe-billing | `get_invoices` | read | invoices |
| stripe-billing | `get_payment_intents` | read | payment_intents |
| stripe-billing | `get_payment_intents_intent_amount_details_line_items` | read | amount_details_line_items |
| stripe-billing | `get_payment_links` | read | payment_links |
| stripe-billing | `get_prices` | read | prices |
| stripe-billing | `get_products` | read | products |
| stripe-billing | `get_refunds` | read | refunds |
| stripe-billing | `get_subscriptions` | read | subscriptions |
| stripe-billing | `get_subscriptions_subscription` | read | subscriptions |
| stripe-billing | `post_charges` | write | charges |
| stripe-billing | `post_charges_charge_dispute_close` | write | disputes |
| stripe-billing | `post_coupons` | write | coupons |
| stripe-billing | `post_customers` | write | customers |
| stripe-billing | `post_customers_customer` | write | customers |
| stripe-billing | `post_invoiceitems` | write | invoiceitems |
| stripe-billing | `post_invoices` | write | invoices |
| stripe-billing | `post_invoices_invoice_finalize` | write | invoices, invoiceitems |
| stripe-billing | `post_invoices_invoice_pay` | write | invoices |
| stripe-billing | `post_invoices_invoice_void` | write | invoices |
| stripe-billing | `post_payment_intents` | write | payment_intents |
| stripe-billing | `post_payment_intents_intent_capture` | write | payment_intents |
| stripe-billing | `post_payment_intents_intent_confirm` | write | payment_intents |
| stripe-billing | `post_payment_links` | write | payment_links, prices |
| stripe-billing | `post_prices` | write | prices |
| stripe-billing | `post_products` | write | products |
| stripe-billing | `post_refunds` | write | refunds, charges |
| stripe-billing | `post_subscriptions` | write | subscriptions |
| stripe-billing | `post_subscriptions_subscription` | write | subscriptions |
