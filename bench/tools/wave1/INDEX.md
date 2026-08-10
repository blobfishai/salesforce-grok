# wave1 — 104 MCP tools

| vendor server | tool | type | target tables |
|---|---|---|---|
| calendar | `calendar_agent` | write | agent_events |
| calendar | `create_scheduled_run` | write | agent_scheduled_runs |
| calendar | `list_scheduled_runs` | read | agent_scheduled_runs |
| calendar | `query_calendar_events` | read | agent_events |
| core | `add_to_knowledge` | write | agent_knowledge |
| core | `create_activity` | write | activity |
| core | `create_business_units` | write | business_units |
| core | `create_invariants_verifiable` | write | invariants_verifiable |
| core | `create_playbook` | write | agent_playbooks |
| core | `create_quote` | write | quote |
| core | `create_sales_manager_policy` | write | sales_manager_policy |
| core | `get_activity` | read | activity |
| core | `get_business_units` | read | business_units |
| core | `get_invariants_verifiable` | read | invariants_verifiable |
| core | `get_quote` | read | quote |
| core | `get_sales_manager_policy` | read | sales_manager_policy |
| core | `human_resources_records_agent` | read | hr_leave_requests, hr_performance_reviews |
| core | `human_resources_workflow_agent` | write | hr_leave_requests, hr_performance_reviews |
| core | `list_activity` | read | activity |
| core | `list_business_units` | read | business_units |
| core | `list_invariants_verifiable` | read | invariants_verifiable |
| core | `list_playbooks` | read | agent_playbooks |
| core | `list_quote` | read | quote |
| core | `list_sales_manager_policy` | read | sales_manager_policy |
| core | `lookup_employee_with_departments` | read | departments, employees |
| core | `lookup_employee_work_assignment_with_employees` | read | employee_work_assignments, employees |
| core | `lookup_finance_budget_with_departments` | read | departments, finance_budgets |
| core | `lookup_hr_leave_request_with_employees` | read | employees, hr_leave_requests |
| core | `lookup_marketing_campaign_with_employees` | read | employees, marketing_campaigns |
| core | `lookup_marketing_content_asset_with_marketing_campaigns` | read | marketing_campaigns, marketing_content_assets |
| core | `marketing_records_agent` | read | marketing_campaigns, marketing_content_assets |
| core | `marketing_workflow_agent` | write | marketing_campaigns, marketing_content_assets |
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
| core | `update_status_activity` | write | activity |
| core | `update_status_business_units` | write | business_units |
| core | `update_status_invariants_verifiable` | write | invariants_verifiable |
| core | `update_status_quote` | write | quote |
| core | `update_status_sales_manager_policy` | write | sales_manager_policy |
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
| notion | `draft_matter_document` | write | matter_documents |
| notion | `operations_records_agent` | read | matter_documents |
| notion | `operations_workflow_agent` | write | matter_documents |
| notion | `query_documents` | read | agent_documents |
| notion | `read_file` | read | agent_files |
| notion | `read_matter_document` | read | matter_documents |
| salesforce | `core_workflow_agent` | write | account, activity |
| salesforce | `create_account` | write | account |
| salesforce | `create_lead` | write | lead |
| salesforce | `create_opportunity` | write | opportunity |
| salesforce | `get_account` | read | account |
| salesforce | `get_lead` | read | lead |
| salesforce | `get_opportunity` | read | opportunity |
| salesforce | `list_account` | read | account |
| salesforce | `list_lead` | read | lead |
| salesforce | `list_opportunity` | read | opportunity |
| salesforce | `lookup_sales_lead_with_employees` | read | employees, sales_leads |
| salesforce | `query_sales_leads` | read | sales_leads |
| salesforce | `sales_records_agent` | read | sales_leads, sales_opportunities |
| salesforce | `sales_workflow_agent` | write | sales_leads, sales_opportunities |
| salesforce | `sourcing_records_agent` | read | sourcing_purchase_orders, sourcing_vendors |
| salesforce | `sourcing_workflow_agent` | write | sourcing_purchase_orders, sourcing_vendors |
| salesforce | `update_sales_leads_status` | write | sales_leads |
| salesforce | `update_status_account` | write | account |
| salesforce | `update_status_lead` | write | lead |
| salesforce | `update_status_opportunity` | write | opportunity |
