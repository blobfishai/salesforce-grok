#!/usr/bin/env python3
"""Check the world against the 27 workflow patterns open-source sales tooling
actually implements (research/answers/oss-sales-automation.md §9, derived from
56 live-verified GitHub repos) plus the scenario types contributed by the 2026
benchmark sweep (research/answers/new-benchmarks-2026.md).

For each pattern this reports one of:
  RUNNABLE   the primitives exist AND a graded task exercises the pattern
  BUILDABLE  the primitives exist, no task authored yet
  BLOCKED    a named primitive is missing — with what would close it

Evidence is checked mechanically against world.json, so the answer cannot drift
from what the world actually contains.

Run: python3 scripts/check-scenario-coverage.py [--markdown]
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, "world", "blobfish-wave6", "package", "sbx_291042075d7547f4")
world = json.load(open(os.path.join(PKG, "world.json")))

TOOLS = {t["name"] for t in world["tools"]}
# world.json declares the seeded tables; create_db.py additionally creates the
# private audit ledger, so check the built database too rather than under-report.
TABLES = {t["name"] for t in world["tables"]}
try:
    import sqlite3
    _db = sqlite3.connect(os.path.join(PKG, "seed.db"))
    TABLES |= {r[0] for r in _db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
    _db.close()
except Exception:
    pass
TASKS = {}
for t in world["tasks"]:
    p = t.get("provenance") or {}
    key = p.get("workflow_type") or p.get("crmarena_task_type")
    if key:
        TASKS.setdefault(key, []).append(t["task_id"])

# pattern -> (needs [artifacts], task types that exercise it, what closes it if blocked)
PATTERNS = [
    ("1. ICP definition -> filtered list build", ["query_sales_leads", "aggregate_query"], ["lead_qualification"], None),
    ("2. Waterfall enrichment with credit accounting", ["__missing_enrichment_providers__"], [],
     "provider tools with distinct coverage/failure rates + enrichment_cache + per-credit ledger"),
    ("3. Email discovery + MX/SMTP verification", ["__missing_smtp_verify__"], [],
     "mx_lookup / smtp_verify — external-channel gap by design"),
    ("4. Account research dossier", ["query_documents", "notion_search", "customer_profiles"], [], None),
    ("5. Buying-committee / org-chart mapping", ["query_employees", "lookup_employee_with_departments"], [], None),
    ("6. External signal detection (hiring/funding/tech)", ["tech_signals"], [],
     "a live web/news surface — external-channel gap by design"),
    ("7. Product-usage (PLG) signal -> account score", ["account_usage", "account_health_list"], ["churn_risk_save_workflow"], None),
    ("8. Lead scoring and grading with auditable reason", ["query_sales_leads", "lead_update_fields"], ["lead_qualification"], None),
    ("9. Lead routing / owner assignment under SLA", ["lead_create", "lead_update_fields"], ["inbound_lead_capture_routing"], None),
    ("10. Multi-step sequence enrollment with spacing", ["outreach_sequences", "outreach_sequence_steps", "sequence_enroll_lead"], ["sequence_enrollment"], None),
    ("11. Per-prospect message personalization", ["snippets", "merge_field_conventions", "post_mail_send"], [], None),
    ("12. Warmup + deliverability + suppression", ["sg_suppressions_add", "sg_domain_authenticate", "blocks", "bounces"], ["unsubscribe_optout_enforcement"], None),
    ("13. Reply detection and classification", ["email_threads", "email_thread_classify"], ["reply_intent_classification"], None),
    ("14. Autonomous multi-turn follow-up", ["email_messages", "post_mail_send"], [],
     "a simulated buyer replying in-episode (harness feature, not a tool)"),
    ("15. Meeting booking -> calendar event -> CRM activity", ["calendar_events_insert", "calendar_freebusy_query", "task_create"], [], None),
    ("16. Call capture -> transcript -> summary", ["calls_info", "transcript_evidence"], [],
     "a larger diarized transcript corpus (2 seeded today)"),
    ("17. Transcript -> MEDDIC extraction with citations", ["meddic_scorecard", "transcript_evidence"], [],
     "claim-level citation grading (verifier feature) + more transcripts"),
    ("18. Post-call CRM writeback", ["update_sales_opportunities_status", "task_create"], ["wrong_stage_rectification"], None),
    ("19. Stage-aware conversation control", ["opportunity_stage_gates"], [],
     "a conversation-stage framework doc + multi-turn scoring"),
    ("20. Stage progression with entry criteria / stale guard", ["update_sales_opportunities_status", "opportunity_stage_gates"], ["wrong_stage_rectification"], None),
    ("21. Quote-to-cash document chain", ["sales_quotes", "erp_sales_order_create", "erp_invoice_create", "post_invoices"], ["quote_approval", "discount_approval_policy_check"], None),
    ("22. Duplicate detection and merge", ["lead_find_duplicates", "lead_merge"], ["lead_dedupe_merge"], None),
    ("23. CRM hygiene audit -> remediation tasks", ["data_quality_rules", "task_create", "aggregate_query"],
     ["crm_data_hygiene_audit"], None),
    ("24. Cross-system sync / reverse ETL", ["agent_sheets", "sheet_agent", "aggregate_query"], [],
     "an explicit field-mapping + conflict-reconciliation surface"),
    ("25. Approval-gated write-back with audit trail", ["quote_update_status", "lead_merge_log_list"],
     ["discount_approval_policy_check", "audit_log_integrity_refusal"], None),
    ("26. Schema/metadata discovery before acting", ["aggregate_query", "describe_world"], [],
     "a list-objects/describe-fields tool on the vendor surfaces"),
    ("27. Segment -> campaign -> scored progression", ["campaign_touches", "get_campaigns", "post_campaigns"], ["campaign_attribution"], None),
]

# The workflow canon (research/answers/sales-workflow-canon.md, 21 scenarios from
# vendor + methodology sources). Listed here are the ones whose grading SHAPE is
# new to this world — restraint-graded (the correct action may be to write
# nothing) and conservation-identity checks — plus the canon staples.
CANON_SCENARIOS = [
    ("1.1 MEDDPICC gap remediation", ["meddic_scorecard", "task_create"], [], None),
    ("1.2 Champion vs Coach discrimination (restraint)", ["transcript_evidence", "contacts"], [],
     "needs a champion/coach fixture; the restraint VERIFIER family now exists (see rst_* pack)"),
    ("1.3 BANT lead conversion gate", ["sales_leads", "lead_update_fields"], ["lead_qualification"], None),
    ("2.1 Mutual action plan", ["agent_documents", "task_create"], [], None),
    ("2.2 Stage advance gate (restraint, two branches)", ["opportunity_stage_gates", "update_sales_opportunities_status"],
     ["wrong_stage_rectification", "stage_gate_refusal"], None),
    ("2.4 Weekly pipeline hygiene sweep", ["stale_opportunity_ladder", "aggregate_query", "task_create"], [], None),
    ("2.5 Submit the weekly forecast", ["forecast_submissions", "forecast_submit"], ["forecast_rollup_commit"], None),
    ("2.6 Sandbagging audit (restraint)", ["sandbagging_red_flags", "aggregate_query"],
     ["forecast_commit_discipline_refusal"], None),
    ("2.8 Win/loss capture on close", ["winloss_talking_points", "update_sales_opportunities_status"], [], None),
    ("3.1 Inbound MQL SLA breach recovery", ["sales_leads", "lead_update_fields", "task_create"], ["inbound_lead_capture_routing"], None),
    ("3.2 MQL rejected with reason code + recycled", ["company_marketing_handoffs", "update_company_marketing_handoffs_status"], [],
     "a rejection-reason field on the handoff record"),
    ("3.3 Fuzzy merge with source-priority survivorship", ["lead_find_duplicates", "lead_merge", "lead_merge_log"], ["lead_dedupe_merge"], None),
    ("3.4 Territory carve with ramped quota (restraint)", ["rep_quotas", "territory"], [],
     "a territory-assignment write tool + ramped-quota fixtures"),
    ("3.5 Split-credit commission statement", ["rep_quotas", "sheet_agent"], [],
     "an OpportunitySplit table and a clawback/dispute surface"),
    ("3.6 Contact hygiene + normalization pass", ["data_quality_rules", "contacts", "lead_update_fields"],
     ["crm_data_hygiene_audit"], None),
    ("3.7 Funnel conversion + pipeline waterfall (answer + identity)", ["aggregate_query", "funnel_conversion_rates"],
     ["funnel_conversion_waterfall"], None),
]

BENCH_SCENARIOS = [
    ("GTM-Bench: prospect list, per-row provenance, negative-scored", ["query_sales_leads", "aggregate_query"], [],
     "a scoring rule that PENALIZES unsupported rows (verifier feature)"),
    ("SDR-Bench: outreach graded on logged reply outcomes", ["email_threads", "post_mail_send"], [],
     "seeded ground-truth outcomes per outreach variant"),
    ("SalesLLM: multi-turn consultative sell vs buyer simulator", ["email_messages"], [],
     "a buyer persona that resists role inversion (harness)"),
    ("TERMS-Bench: negotiation surplus / mandate compliance", ["sales_quotes", "cpq_discount_policy"], [],
     "a counter-offer log with reservation values"),
    ("EnterpriseOps-Gym: infeasible-task safe refusal, scored", ["service_cases_list"],
     ["refusal_calibration_non_answerable", "discount_authority_refusal", "audit_log_integrity_refusal",
      "suppression_reenrollment_refusal"], None),
    ("Agent-Diff: pure state-diff grading with side-effect checks", ["lead_merge_log"], ["lead_dedupe_merge"], None),
    ("EntCollabBench: RBAC-isolated approval subset", ["quote_update_status"], [],
     "per-role permission isolation in the session layer"),
    ("World of Workflows: cascading side-effect prediction", ["_forge_actions"], [],
     "declared downstream business rules the agent must anticipate"),
    ("tau3-bench: voice channel", ["__missing_voice__"], [],
     "telephony/voice surface — external-channel gap by design"),
    ("DRBench: research over private stack + public web", ["query_documents", "news_items"], [],
     "a public-web surface — external-channel gap by design"),
]


def status(needs, tasks):
    missing = [n for n in needs if not n.startswith("__") and n not in TOOLS and n not in TABLES]
    synthetic = [n for n in needs if n.startswith("__")]
    if missing or synthetic:
        return "BLOCKED", missing + synthetic
    return ("RUNNABLE" if tasks else "BUILDABLE"), []


def main():
    md = "--markdown" in sys.argv
    lines = []
    counts = {"RUNNABLE": 0, "BUILDABLE": 0, "BLOCKED": 0}
    for title, group in (("Open-source workflow patterns (27)", PATTERNS),
                         ("Sales workflow canon (16 of 21 scenarios)", CANON_SCENARIOS),
                         ("2026 benchmark scenario types (10)", BENCH_SCENARIOS)):
        lines.append(f"\n## {title}\n" if md else f"\n=== {title}")
        if md:
            lines.append("| pattern | status | evidence / what's missing |")
            lines.append("|---|---|---|")
        for name, needs, task_keys, blocker in group:
            tasks = [tid for k in task_keys for tid in TASKS.get(k, [])]
            st, missing = status(needs, tasks)
            counts[st] += 1
            if st == "BLOCKED":
                detail = blocker or ("missing: " + ", ".join(missing))
            elif tasks:
                detail = "tasks: " + ", ".join(sorted(tasks)[:3])
            else:
                detail = "primitives: " + ", ".join(n for n in needs[:3])
            if md:
                lines.append(f"| {name} | **{st}** | {detail} |")
            else:
                lines.append(f"  {st:9} {name:58} {detail[:70]}")
    header = (f"scenario coverage — {len(PATTERNS)} OSS patterns + {len(CANON_SCENARIOS)} canon scenarios "
              f"+ {len(BENCH_SCENARIOS)} benchmark types "
              f"vs a world of {len(TOOLS)} tools / {len(TABLES)} tables / {len(world['tasks'])} tasks")
    print(("# " + header) if md else header)
    print("\n".join(lines))
    tot = sum(counts.values())
    print(f"\nRUNNABLE {counts['RUNNABLE']}/{tot} (primitives + graded task) · "
          f"BUILDABLE {counts['BUILDABLE']}/{tot} (primitives only) · "
          f"BLOCKED {counts['BLOCKED']}/{tot}")


if __name__ == "__main__":
    main()
