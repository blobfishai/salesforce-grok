"""Free-text records/sheet sub-agent. Verbs: create sheet "T" with columns: a, b · write rows to "T": <TSV> · read "T" | read <table> · update "T" row N set col = value. Per-call write cap: 50 rows."""
import hashlib, json, re, sqlite3

_WORLD_TABLES = ["lead_management_sop","lead_scoring_policy","account_tiering_standard","opportunity_stage_gates","cpq_discount_policy","deal_desk_charter","compliance_review_checklist","finance_approval_thresholds","order_activation_runbook","case_management_sla","activity_logging_standards","forecast_methodology","renewal_playbook","territory","data_quality_rules","account_executive_sales_rep","sales_analyst","compliance_officer","sales_manager","record_retention","sequence_design_rules","merge_field_conventions","snippets","conversation_intelligence_standards","disposition_codes","meddic_scorecard","talk_ratio","tracker_keywords","snippets_and_retention","coaching_cadence","meeting_scheduling_sla","meeting_types_and_durations","handoff_to_ae","aum_bands","tech_signals","accept_all","risky","unknown","inbound_routing_matrix","visitor_identification","web_form_definitions","routing_decision_table","suppression_and_kpis","order_form","nda","sow","invoicing_rules","deal_health_score","stale_opportunity_ladder","coverage_ratio","slipped_pulled_in_lost","commit","best_case","sandbagging_red_flags","support_25","engagement_20","playbooks","week_1_t_120_to_t_114","week_2_t_113_to_t_107","weeks_10_12_t_57_to_t_37","weeks_13_16_t_36_to_t_8","monthly_timeline_business_days","account_transfer_protocol_on_rep_departure","mql_definition","sal_gate","attribution","fy2026_campaigns","utm_conventions","their_strengths_do_not_dismiss","their_weaknesses_attack_here","pricing_pressure_guidance","winloss_talking_points","strengths","weaknesses","answer_reuse_and_approval_rules","partner_tiers","conflict_check_and_the_90_day_window","co_sell_and_named_account_overlap","billing_object_mapping_stripe_style","deal_room_channels_slack_style","dedupe_race_handling","failure_and_retry_semantics","funnel_conversion_rates","win_rate_calculation_rules","revenue_metric_definitions","board_pack_metrics","meddic_extraction_scorecard","risk_notes_csm_post_call","term_and_renewal","line_items_list_prices_per_13_product_catalogmd","billing","renewal_mechanics_per_msa_and_14_renewal_playbookmd","fy2026_list_prices","volume_bands","currency_handling","aggregates","transcript_evidence","departments","employees","employee_work_assignments","sales_leads","sales_opportunities","hr_leave_requests","hr_performance_reviews","finance_expense_reports","finance_budgets","support_tickets","marketing_campaigns","marketing_content_assets","sourcing_vendors","sourcing_purchase_orders","accounts","cases","contacts","opportunities","tasks","account_links","account_sessions","active_entitlements","alerts","amount_details_line_items","apple_pay_domains","application_fees","apps_secrets","authorizations","balance_settings","balance_transactions","balances","bank_accounts","billing_alerts","billing_credit_balance_summaries","billing_credit_balance_transactions","billing_meters","capabilities","charges","checkout_sessions","climate_orders","credit_notes","disputes","identity_verification_sessions","invoice_rendering_templates","invoices","issuing_authorizations","activities","all_segments_responses","api_keys","assigneds","authentication_domains","automations_link_stats_responses","automations_responses","batches","blocks","bounces","campaigns","categories","category_stats","certificates","click_trackings","contact_exports","contactdb_segments","singlesends","suppression_groups","activity_log_lists","admin_lists","admin_with_apps","admins","ai_call_responses","article_lists","articles","away_status_reason_lists","collections","content_import_sources","conversations","data_exports","help_centers","news_items","admin_apps_approveds","admin_apps_requests","admin_apps_restricteds","admin_conversations","admin_conversations_ekms","admin_conversations_restrict_accesses","admin_emojis","admin_invite_requests","admin_invite_requests_approveds","admin_invite_requests_denieds","calls","channels","files","messages","acl_rules","acls","calendar_list_entries","calendar_lists","calendars","colors","customers","journal_entries","purchase_orders","vendors","company_marketing_handoffs","company_sales_handoffs","company_finance_handoffs","company_sourcing_handoffs","matter_documents"]
_WRITE_CAP = 50
_AMBIGUOUS_PCT = 15
_PARTIAL_PCT = 3
_FRICTION_SEED = "3ba25889bd4c5d1d"

def _qi(name):
    return '"' + str(name).replace('"', '""') + '"'

def _ambiguous(req, pct):
    if pct <= 0:
        return False
    digest = int(hashlib.sha256(req.encode('utf-8', 'ignore')).hexdigest()[:8], 16)
    return (digest % 100) < pct

def _partial_flagged(req, pct, seed):
    if pct <= 0:
        return False
    digest = int(hashlib.sha256((seed + '|partial|' + req).encode('utf-8', 'ignore')).hexdigest()[:8], 16)
    return (digest % 100) < pct

def _bf_attempt(db_path, sig):
    conn = sqlite3.connect(str(db_path) + '.bf-friction')
    try:
        conn.execute('CREATE TABLE IF NOT EXISTS attempts (sig TEXT PRIMARY KEY, n INTEGER NOT NULL)')
        conn.execute('INSERT INTO attempts (sig, n) VALUES (?, 1) ON CONFLICT(sig) DO UPDATE SET n = n + 1', (sig,))
        conn.commit()
        return conn.execute('SELECT n FROM attempts WHERE sig = ?', (sig,)).fetchone()[0]
    finally:
        conn.close()

def _sheet_by_title(conn, title):
    return conn.execute("SELECT * FROM agent_sheets WHERE title = ?", (title,)).fetchone()

def _create_sheet(conn, title, columns):
    next_id = (conn.execute("SELECT MAX(id) FROM agent_sheets").fetchone()[0] or 0) + 1
    conn.execute("INSERT INTO agent_sheets (id, title, columns_spec, created_at) VALUES (?, ?, ?, datetime('now'))",
                 (next_id, title, ", ".join(columns)))
    conn.commit()
    return next_id

def sheet_agent(db_path, request=None, **kwargs):
    if not request or not str(request).strip():
        return {"error": "validation_error", "message": "request is required — describe what the sheet agent should do"}
    req = str(request).strip()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        m = re.search(r'^\s*create\s+(?:a\s+)?(?:new\s+)?sheet\s+"([^"]+)"(?:\s+with\s+columns?\s*:?\s*([^\n]+))?', req, re.I)
        if m:
            title = m.group(1).strip()
            columns = [c.strip() for c in re.split(r'[,\t]', m.group(2) or '') if c.strip()]
            existing = _sheet_by_title(conn, title)
            if existing:
                return {"status": "already_exists", "sheet": title, "sheet_id": existing["id"]}
            sheet_id = _create_sheet(conn, title, columns)
            return {"status": "created", "sheet": title, "sheet_id": sheet_id, "columns": columns}
        m = re.search(r'(?:write|append|import)\s+(?:the\s+)?rows?\s+(?:to|into)\s+"([^"]+)"[^\n]*\n(.+)$', req, re.I | re.S)
        if m:
            title = m.group(1).strip()
            lines = [l for l in m.group(2).splitlines() if l.strip()]
            sheet = _sheet_by_title(conn, title)
            if sheet is None:
                sheet_id = _create_sheet(conn, title, [])
            else:
                sheet_id = sheet["id"]
            to_write = lines[:_WRITE_CAP]
            remaining = len(lines) - len(to_write)
            # Deterministic injected partial write (environment friction):
            # the FIRST attempt of a flagged multi-row import applies only
            # half the chunk and reports an explicit error; a retry of the
            # SAME request applies exactly the rest (content-deduplicated),
            # composing with the per-call write cap above.
            _partial_skipped = None
            if len(to_write) >= 2 and _partial_flagged(req, _PARTIAL_PCT, _FRICTION_SEED):
                _attempt = _bf_attempt(db_path, 'sheet_agent|partial|' + req)
                if _attempt == 1:
                    _cut = max(1, len(to_write) // 2)
                    _partial_skipped = len(to_write) - _cut
                    to_write = to_write[:_cut]
                else:
                    _existing = {r["cells"] for r in conn.execute("SELECT cells FROM agent_sheet_rows WHERE sheet_id = ?", (sheet_id,)).fetchall()}
                    to_write = [l for l in to_write if l not in _existing]
            base_index = conn.execute("SELECT COALESCE(MAX(row_index), 0) FROM agent_sheet_rows WHERE sheet_id = ?", (sheet_id,)).fetchone()[0]
            next_id = (conn.execute("SELECT MAX(id) FROM agent_sheet_rows").fetchone()[0] or 0) + 1
            for offset, line in enumerate(to_write):
                conn.execute("INSERT INTO agent_sheet_rows (id, sheet_id, row_index, cells) VALUES (?, ?, ?, ?)",
                             (next_id + offset, sheet_id, base_index + offset + 1, line))
            conn.commit()
            if _partial_skipped is not None:
                return {"error": "partial_write",
                        "message": "wrote %d of %d row(s) before the backend timed out — %d row(s) were NOT written; retry the request to apply the remainder" % (len(to_write), len(to_write) + _partial_skipped, _partial_skipped + remaining),
                        "rows_written": len(to_write), "rows_remaining": _partial_skipped + remaining, "retryable": True}
            if to_write and _ambiguous(req, _AMBIGUOUS_PCT):
                # Ambiguous success: the write IS applied, but the ack is
                # null-ish — verify state instead of trusting the response.
                return {"output": None}
            resp = {"status": "rows_written", "sheet": title, "rows_written": len(to_write),
                    "rows_remaining": remaining, "total_rows_in_sheet": base_index + len(to_write)}
            if remaining > 0:
                resp["note"] = ("per-call write cap is %d rows; %d row(s) were NOT written — "
                                "send the remaining rows in the next call" % (_WRITE_CAP, remaining))
                resp["next_range"] = "rows %d-%d" % (len(to_write) + 1, len(lines))
            return resp
        m = re.search(r'^\s*update\s+"([^"]+)"\s+row\s+(\d+)\s+set\s+([A-Za-z0-9_ ]+?)\s*=\s*(.+)$', req, re.I)
        if m:
            title, row_index, column, value = m.group(1).strip(), int(m.group(2)), m.group(3).strip(), m.group(4).strip().strip('"')
            sheet = _sheet_by_title(conn, title)
            if sheet is None:
                titles = [r["title"] for r in conn.execute("SELECT title FROM agent_sheets ORDER BY id").fetchall()]
                return {"error": "not_found", "message": "no sheet titled %r; existing sheets: %r" % (title, titles)}
            row = conn.execute("SELECT * FROM agent_sheet_rows WHERE sheet_id = ? AND row_index = ?", (sheet["id"], row_index)).fetchone()
            if row is None:
                return {"error": "not_found", "message": "sheet %r has no row %d" % (title, row_index)}
            cells = row["cells"] or ""
            new_cells = cells + "\t" + column + "=" + value if cells else column + "=" + value
            conn.execute("UPDATE agent_sheet_rows SET cells = ? WHERE id = ?", (new_cells, row["id"]))
            conn.commit()
            if _ambiguous(req, _AMBIGUOUS_PCT):
                return {"output": None}
            return {"status": "row_updated", "sheet": title, "row_index": row_index, "cells": new_cells}
        m = re.search(r'^\s*read\s+"([^"]+)"', req, re.I)
        if m:
            title = m.group(1).strip()
            sheet = _sheet_by_title(conn, title)
            if sheet is None:
                return {"error": "not_found", "message": "no sheet titled %r" % title}
            rows = [dict(r) for r in conn.execute("SELECT row_index, cells FROM agent_sheet_rows WHERE sheet_id = ? ORDER BY row_index LIMIT 200", (sheet["id"],)).fetchall()]
            return {"sheet": title, "columns": sheet["columns_spec"], "count": len(rows), "rows": rows}
        m = re.search(r'^\s*read\s+([A-Za-z_][A-Za-z0-9_]*)\b', req, re.I)
        if m:
            table = m.group(1)
            if table not in _WORLD_TABLES:
                return {"error": "not_found", "message": "unknown world table %r; no state was changed" % table}
            rows = [dict(r) for r in conn.execute('SELECT * FROM ' + _qi(table) + ' LIMIT 50').fetchall()]
            return {"table": table, "count": len(rows), "rows": rows}
        # Unrecognized request: sub-agents interpret loosely — treat the
        # request as the title of a new working sheet (a real write).
        title = re.sub(r'\s+', ' ', req)[:80]
        existing = _sheet_by_title(conn, title)
        if existing:
            return {"status": "already_exists", "sheet": title, "sheet_id": existing["id"],
                    "hint": "verbs: create sheet \"T\" with columns: … · write rows to \"T\": <TSV> · read \"T\" · update \"T\" row N set col = value"}
        sheet_id = _create_sheet(conn, title, [])
        return {"status": "created", "sheet": title, "sheet_id": sheet_id,
                "hint": "verbs: create sheet \"T\" with columns: … · write rows to \"T\": <TSV> · read \"T\" | read <table> · update \"T\" row N set col = value"}
    finally:
        conn.close()