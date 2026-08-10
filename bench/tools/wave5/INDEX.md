# wave5 — 171 MCP tools

| vendor server | tool | type | target tables |
|---|---|---|---|
| calendar | `calendar_agent` | write | agent_events |
| calendar | `create_scheduled_run` | write | agent_scheduled_runs |
| calendar | `list_scheduled_runs` | read | agent_scheduled_runs |
| calendar | `query_calendar_events` | read | agent_events |
| core | `add_to_knowledge` | write | agent_knowledge |
| core | `case_get` | read | cases |
| core | `create_activity_logging_standards` | write | activity_logging_standards |
| core | `create_case_management_sla` | write | case_management_sla |
| core | `create_company_sales_handoffs` | write | company_sales_handoffs |
| core | `create_compliance_officer` | write | compliance_officer |
| core | `create_compliance_review_checklist` | write | compliance_review_checklist |
| core | `create_cpq_discount_policy` | write | cpq_discount_policy |
| core | `create_data_quality_rules` | write | data_quality_rules |
| core | `create_deal_desk_charter` | write | deal_desk_charter |
| core | `create_finance_approval_thresholds` | write | finance_approval_thresholds |
| core | `create_forecast_methodology` | write | forecast_methodology |
| core | `create_order_activation_runbook` | write | order_activation_runbook |
| core | `create_playbook` | write | agent_playbooks |
| core | `create_record_retention` | write | record_retention |
| core | `create_renewal_playbook` | write | renewal_playbook |
| core | `create_sales_analyst` | write | sales_analyst |
| core | `create_sales_manager` | write | sales_manager |
| core | `create_territory` | write | territory |
| core | `get_activity_logging_standards` | read | activity_logging_standards |
| core | `get_case_management_sla` | read | case_management_sla |
| core | `get_company_sales_handoffs` | read | company_sales_handoffs |
| core | `get_compliance_officer` | read | compliance_officer |
| core | `get_compliance_review_checklist` | read | compliance_review_checklist |
| core | `get_cpq_discount_policy` | read | cpq_discount_policy |
| core | `get_data_quality_rules` | read | data_quality_rules |
| core | `get_deal_desk_charter` | read | deal_desk_charter |
| core | `get_finance_approval_thresholds` | read | finance_approval_thresholds |
| core | `get_forecast_methodology` | read | forecast_methodology |
| core | `get_order_activation_runbook` | read | order_activation_runbook |
| core | `get_record_retention` | read | record_retention |
| core | `get_renewal_playbook` | read | renewal_playbook |
| core | `get_sales_analyst` | read | sales_analyst |
| core | `get_sales_manager` | read | sales_manager |
| core | `get_territory` | read | territory |
| core | `human_resources_records_agent` | read | hr_leave_requests, hr_performance_reviews |
| core | `human_resources_workflow_agent` | write | hr_leave_requests, hr_performance_reviews |
| core | `list_activity_logging_standards` | read | activity_logging_standards |
| core | `list_case_management_sla` | read | case_management_sla |
| core | `list_company_sales_handoffs` | read | company_sales_handoffs |
| core | `list_compliance_officer` | read | compliance_officer |
| core | `list_compliance_review_checklist` | read | compliance_review_checklist |
| core | `list_cpq_discount_policy` | read | cpq_discount_policy |
| core | `list_data_quality_rules` | read | data_quality_rules |
| core | `list_deal_desk_charter` | read | deal_desk_charter |
| core | `list_finance_approval_thresholds` | read | finance_approval_thresholds |
| core | `list_forecast_methodology` | read | forecast_methodology |
| core | `list_order_activation_runbook` | read | order_activation_runbook |
| core | `list_playbooks` | read | agent_playbooks |
| core | `list_record_retention` | read | record_retention |
| core | `list_renewal_playbook` | read | renewal_playbook |
| core | `list_sales_analyst` | read | sales_analyst |
| core | `list_sales_manager` | read | sales_manager |
| core | `list_territory` | read | territory |
| core | `lookup_employee_with_departments` | read | departments, employees |
| core | `lookup_employee_work_assignment_with_employees` | read | employee_work_assignments, employees |
| core | `lookup_finance_budget_with_departments` | read | departments, finance_budgets |
| core | `lookup_hr_leave_request_with_employees` | read | employees, hr_leave_requests |
| core | `lookup_hr_performance_review_with_employees` | read | employees, hr_performance_reviews |
| core | `lookup_marketing_campaign_with_employees` | read | employees, marketing_campaigns |
| core | `lookup_marketing_content_asset_with_marketing_campaigns` | read | marketing_campaigns, marketing_content_assets |
| core | `lookup_sourcing_vendor_with_employees` | read | employees, sourcing_vendors |
| core | `marketing_records_agent` | read | marketing_campaigns, marketing_content_assets |
| core | `marketing_workflow_agent` | write | marketing_campaigns, marketing_content_assets |
| core | `opportunities_list` | read | opportunities |
| core | `query_departments` | read | departments |
| core | `query_employee_work_assignments` | read | employee_work_assignments |
| core | `query_employees` | read | employees |
| core | `query_files` | read | agent_files |
| core | `query_finance_budgets` | read | finance_budgets |
| core | `query_hr_leave_requests` | read | hr_leave_requests |
| core | `query_hr_performance_reviews` | read | hr_performance_reviews |
| core | `query_marketing_campaigns` | read | marketing_campaigns |
| core | `query_marketing_content_assets` | read | marketing_content_assets |
| core | `query_sales_opportunities` | read | sales_opportunities |
| core | `query_sourcing_vendors` | read | sourcing_vendors |
| core | `save_memory` | write | agent_memories |
| core | `search_knowledge` | read | agent_knowledge |
| core | `search_memory` | read | agent_memories |
| core | `task_create` | write | tasks |
| core | `task_get` | read | tasks |
| core | `tasks_list` | read | tasks |
| core | `update_departments_department_code` | write | departments |
| core | `update_employee_work_assignments_status` | write | employee_work_assignments |
| core | `update_employees_status` | write | employees |
| core | `update_finance_budgets_status` | write | finance_budgets |
| core | `update_hr_leave_requests_status` | write | hr_leave_requests |
| core | `update_hr_performance_reviews_status` | write | hr_performance_reviews |
| core | `update_marketing_campaigns_status` | write | marketing_campaigns |
| core | `update_marketing_content_assets_status` | write | marketing_content_assets |
| core | `update_sales_opportunities_status` | write | sales_opportunities |
| core | `update_sourcing_vendors_status` | write | sourcing_vendors |
| core | `update_status_activity_logging_standards` | write | activity_logging_standards |
| core | `update_status_case_management_sla` | write | case_management_sla |
| core | `update_status_company_sales_handoffs` | write | company_sales_handoffs |
| core | `update_status_compliance_officer` | write | compliance_officer |
| core | `update_status_compliance_review_checklist` | write | compliance_review_checklist |
| core | `update_status_cpq_discount_policy` | write | cpq_discount_policy |
| core | `update_status_data_quality_rules` | write | data_quality_rules |
| core | `update_status_deal_desk_charter` | write | deal_desk_charter |
| core | `update_status_finance_approval_thresholds` | write | finance_approval_thresholds |
| core | `update_status_forecast_methodology` | write | forecast_methodology |
| core | `update_status_order_activation_runbook` | write | order_activation_runbook |
| core | `update_status_record_retention` | write | record_retention |
| core | `update_status_renewal_playbook` | write | renewal_playbook |
| core | `update_status_sales_analyst` | write | sales_analyst |
| core | `update_status_sales_manager` | write | sales_manager |
| core | `update_status_territory` | write | territory |
| email | `organization_records_agent` | read | departments, employee_work_assignments, employees |
| email | `organization_workflow_agent` | write | departments, employee_work_assignments, employees |
| erp | `lookup_sourcing_purchase_order_with_sourcing_vendors` | read | sourcing_purchase_orders, sourcing_vendors |
| erp | `query_sourcing_purchase_orders` | read | sourcing_purchase_orders |
| erp | `update_sourcing_purchase_orders_status` | write | sourcing_purchase_orders |
| github | `finance_records_agent` | read | finance_budgets, finance_expense_reports |
| github | `finance_workflow_agent` | write | finance_budgets, finance_expense_reports |
| github | `lookup_finance_expense_report_with_employees` | read | employees, finance_expense_reports |
| github | `query_finance_expense_reports` | read | finance_expense_reports |
| github | `sheet_agent` | write | agent_sheet_rows, agent_sheets |
| github | `update_finance_expense_reports_status` | write | finance_expense_reports |
| jira | `customer_support_records_agent` | read | support_tickets |
| jira | `customer_support_workflow_agent` | write | support_tickets |
| jira | `lookup_support_ticket_with_employees` | read | employees, support_tickets |
| jira | `query_support_tickets` | read | support_tickets |
| jira | `update_support_tickets_status` | write | support_tickets |
| notion | `document_agent` | write | agent_documents |
| notion | `query_documents` | read | agent_documents |
| notion | `read_file` | read | agent_files |
| pagerduty | `case_create` | write | cases |
| pagerduty | `cases_list` | read | cases |
| salesforce | `account_create` | write | accounts |
| salesforce | `account_get` | read | accounts |
| salesforce | `accounts_list` | read | accounts |
| salesforce | `contact_create` | write | contacts |
| salesforce | `contact_get` | read | contacts |
| salesforce | `contacts_list` | read | contacts |
| salesforce | `core_records_agent` | read | account_tiering_standard, activity_logging_standards, case_management_sla |
| salesforce | `core_workflow_agent` | write | account_tiering_standard, activity_logging_standards, case_management_sla |
| salesforce | `create_account_executive_sales_rep` | write | account_executive_sales_rep |
| salesforce | `create_account_tiering_standard` | write | account_tiering_standard |
| salesforce | `create_lead_management_sop` | write | lead_management_sop |
| salesforce | `create_lead_scoring_policy` | write | lead_scoring_policy |
| salesforce | `create_opportunity_stage_gates` | write | opportunity_stage_gates |
| salesforce | `get_account_executive_sales_rep` | read | account_executive_sales_rep |
| salesforce | `get_account_tiering_standard` | read | account_tiering_standard |
| salesforce | `get_lead_management_sop` | read | lead_management_sop |
| salesforce | `get_lead_scoring_policy` | read | lead_scoring_policy |
| salesforce | `get_opportunity_stage_gates` | read | opportunity_stage_gates |
| salesforce | `list_account_executive_sales_rep` | read | account_executive_sales_rep |
| salesforce | `list_account_tiering_standard` | read | account_tiering_standard |
| salesforce | `list_lead_management_sop` | read | lead_management_sop |
| salesforce | `list_lead_scoring_policy` | read | lead_scoring_policy |
| salesforce | `list_opportunity_stage_gates` | read | opportunity_stage_gates |
| salesforce | `lookup_sales_lead_with_employees` | read | employees, sales_leads |
| salesforce | `lookup_sales_opportunity_with_sales_leads` | read | sales_leads, sales_opportunities |
| salesforce | `opportunity_create` | write | opportunities |
| salesforce | `opportunity_get` | read | opportunities |
| salesforce | `query_sales_leads` | read | sales_leads |
| salesforce | `sales_records_agent` | read | accounts, cases, company_sales_handoffs |
| salesforce | `sales_workflow_agent` | write | accounts, cases, company_sales_handoffs |
| salesforce | `sourcing_records_agent` | read | sourcing_purchase_orders, sourcing_vendors |
| salesforce | `sourcing_workflow_agent` | write | sourcing_purchase_orders, sourcing_vendors |
| salesforce | `update_sales_leads_status` | write | sales_leads |
| salesforce | `update_status_account_executive_sales_rep` | write | account_executive_sales_rep |
| salesforce | `update_status_account_tiering_standard` | write | account_tiering_standard |
| salesforce | `update_status_lead_management_sop` | write | lead_management_sop |
| salesforce | `update_status_lead_scoring_policy` | write | lead_scoring_policy |
| salesforce | `update_status_opportunity_stage_gates` | write | opportunity_stage_gates |
