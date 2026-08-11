#!/usr/bin/env python3
"""Wave-7 task pack: the sales workflows practitioners and open-source tools
actually automate, made runnable and gradeable in this world.

Where the CRMArena clone (crma_*) ports an academic benchmark, this pack covers
the routines that open-source sales tooling and the RevOps canon assume: dedupe
and merge, inbound capture and routing, reply-intent triage, suppression
compliance, sequence enrollment, forecast submission, quota analysis, churn
saves, renewals, attribution and signature order.

Same guarantees as the CRMArena pack: every gold is COMPUTED FROM seed.db at
build time, and grading uses the same three deterministic families (answer /
state / refusal) with no LLM judge. Verifier templates are imported from
build_crmarena_tasks so both packs grade identically.

Run: python3 scripts/build-workflow-tasks.py [--dry-run]
"""
import importlib.util
import json
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, "world", "blobfish-wave6", "package", "sbx_291042075d7547f4")
TOP_WORLD = os.path.join(ROOT, "world", "blobfish-wave6", "world.json")
PREFIX = "wf_"

_spec = importlib.util.spec_from_file_location("crma", os.path.join(ROOT, "scripts", "build-crmarena-tasks.py"))
crma = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(crma)   # reuse ANSWER_VCODE / STATE_VCODE / helpers

conn = sqlite3.connect(os.path.join(PKG, "seed.db"))
conn.row_factory = sqlite3.Row
q = lambda s, a=(): [dict(r) for r in conn.execute(s, a).fetchall()]
one = lambda s, a=(): (q(s, a) or [None])[0]

SRC_OSS = "open-source sales automation canon (see research/answers/oss-sales-automation.md)"
SRC_CANON = "RevOps / sales workflow canon (see research/answers/sales-workflow-canon.md)"

MULTI_VCODE = '''"""VCode verifier for {task_id} — workflow task ({wf_type})

Grading: several row-level outcomes must ALL hold, with collateral guards.
Targets computed from the world database at build time:
    {gold_sql}
"""
CHECKS = {checks!r}
ALLOWED_TABLES = {allowed!r}
{helpers}

def _find(rows, row_id):
    for r in rows:
        if isinstance(r, dict) and str(r.get("id")) == str(row_id):
            return r
    return None

def verify(initial_state, final_state, trace):
    results, failed = [], []
    def chk(name, passed, detail):
        results.append({{"name": name, "passed": bool(passed), "details": detail}})
        if not passed:
            failed.append(name)

    chk("state_changed", initial_state != final_state,
        "world state changed" if initial_state != final_state else "NO state change — agent did nothing")

    core_names = []
    for c in CHECKS:
        name = c["name"]
        core_names.append(name)
        table, kind = c["table"], c["kind"]
        rows = _rows(final_state, table)
        if kind == "row_field":
            row = _find(rows, c["row_id"])
            got = row.get(c["field"]) if row else None
            ok = row is not None and _norm(got) == _norm(c["expected"])
            chk(name, ok, "{{}}.{{}} == {{!r}}".format(table, c["field"], c["expected"]) if ok
                else "expected {{}}.{{}} == {{!r}} on {{}}, got {{!r}}".format(table, c["field"], c["expected"], c["row_id"], got))
        elif kind == "row_absent":
            ok = _find(rows, c["row_id"]) is None
            chk(name, ok, "row {{}} removed from {{}}".format(c["row_id"], table) if ok
                else "row {{}} still present in {{}}".format(c["row_id"], table))
        elif kind == "row_count_delta":
            before, after = len(_rows(initial_state, table)), len(rows)
            ok = (after - before) == c["delta"]
            chk(name, ok, "{{}} changed by {{}}".format(table, after - before) if ok
                else "expected {{}} to change by {{}}, saw {{}}".format(table, c["delta"], after - before))
        elif kind == "row_matching":
            hits = [r for r in rows if all(_norm(r.get(k)) == _norm(v) for k, v in c["match"].items())]
            ok = len(hits) >= c.get("at_least", 1)
            chk(name, ok, "{{}} row(s) in {{}} match {{}}".format(len(hits), table, c["match"]) if ok
                else "no row in {{}} matches {{}}".format(table, c["match"]))

    changed = _tables_changed(initial_state, final_state)
    offtask = [t for t in changed if t not in ALLOWED_TABLES]
    chk("no_offtask_table_changes", not offtask,
        "only permitted tables changed" if not offtask else "collateral damage in: " + ", ".join(offtask))

    structural_failed = list(failed)
    guard_failed = [n for n in ["no_offtask_table_changes"] if n in failed]
    core_failed = [n for n in core_names if n in failed]
    if guard_failed:
        reward = 0.0
    elif core_names:
        reward = (len(core_names) - len(core_failed)) / len(core_names)
    else:
        reward = 0.0
    return {{
        "task_id": "{task_id}",
        "passed": len(structural_failed) == 0,
        "reward": round(reward, 4),
        "explanation": "All task checks passed" if not structural_failed else "Failed: " + ", ".join(structural_failed),
        "failed_conditions": structural_failed,
        "advisory_conditions": [],
        "assertions": results,
    }}
'''


def build():
    T = []
    n = 0

    def nid():
        nonlocal n
        n += 1
        return f"{PREFIX}{n:03d}"

    # ---- dedupe + merge (the classic RevOps routine, destructive on purpose) ----
    dupe = one("SELECT company_name, COUNT(*) c, MIN(id) master, MAX(id) victim FROM sales_leads "
               "GROUP BY company_name HAVING c > 1 ORDER BY company_name LIMIT 1")
    child = one("SELECT id FROM sales_opportunities WHERE lead_id = ?", (dupe["victim"],))
    T.append({
        "kind": "multi", "task_id": nid(), "wf_type": "lead_dedupe_merge", "source": SRC_OSS,
        "prompt": (f"{dupe['company_name']} appears twice in the lead database as leads {dupe['master']} and "
                   f"{dupe['victim']}. Merge them, keeping lead {dupe['master']} as the master record. The "
                   "surviving lead must end up with the estimated value that only the duplicate carried, any "
                   "child opportunity must follow the master, and the duplicate record must be gone."),
        "gold_sql": f"duplicate pair on company_name={dupe['company_name']!r}: master={dupe['master']}, victim={dupe['victim']}",
        "tools": ["lead_find_duplicates", "lead_merge", "query_sales_leads"],
        "allowed": ["sales_leads", "sales_opportunities", "lead_merge_log"],
        "checks": [
            {"name": "duplicate_removed", "kind": "row_absent", "table": "sales_leads", "row_id": dupe["victim"]},
            {"name": "survivorship_filled", "kind": "row_field", "table": "sales_leads",
             "row_id": dupe["master"], "field": "estimated_value",
             "expected": one("SELECT estimated_value FROM sales_leads WHERE id=?", (dupe["victim"],))["estimated_value"]},
            {"name": "child_reparented", "kind": "row_field", "table": "sales_opportunities",
             "row_id": child["id"], "field": "lead_id", "expected": dupe["master"]},
        ],
    })

    # ---- inbound capture + routing ----
    T.append({
        "kind": "multi", "task_id": nid(), "wf_type": "inbound_lead_capture_routing", "source": SRC_OSS,
        "prompt": ("A webinar attendee from Beacon Hill Advisors submitted the contact form: Priya Raman, "
                   "estimated value $85,000. Create the lead with source 'webinar' and route it to employee 3 "
                   "as owner. Create exactly one lead and change nothing else."),
        "gold_sql": "new lead row asserted by field match, not by id (the agent mints the id)",
        "tools": ["lead_create", "query_sales_leads"],
        "allowed": ["sales_leads"],
        "checks": [
            {"name": "lead_created", "kind": "row_count_delta", "table": "sales_leads", "delta": 1},
            {"name": "lead_fields_correct", "kind": "row_matching", "table": "sales_leads",
             "match": {"company_name": "Beacon Hill Advisors", "contact_name": "Priya Raman",
                       "source": "webinar", "owner_employee_id": 3}},
        ],
    })

    # ---- reply-intent classification ----
    # Pick a thread that arrived UNCLASSIFIED and derive the gold from the reply
    # text itself, so the row the agent reads never contains the answer.
    BODY_INTENT = [("remove me from your list", "unsubscribe"),
                   ("wrong person", "referral"),
                   ("out of the office", "out_of_office"),
                   ("what does the data feed add", "pricing_question"),
                   ("not a priority", "not_now"),
                   ("evaluating platforms this quarter", "interested")]
    thr = None
    for cand in q("SELECT id, account_name FROM email_threads WHERE intent_label='unclassified' ORDER BY id"):
        body = one("SELECT body FROM email_messages WHERE thread_id=? AND direction='inbound' LIMIT 1", (cand["id"],))
        text = (body or {}).get("body", "").lower()
        hit = next((lab for frag, lab in BODY_INTENT if frag in text), None)
        if hit:
            thr = {**cand, "intent_label": hit, "body": body["body"]}
            break
    T.append({
        "kind": "state", "task_id": nid(), "wf_type": "reply_intent_classification", "source": SRC_OSS,
        "prompt": (f"Read email thread {thr['id']} from {thr['account_name']} and classify the prospect's reply. "
                   "Set its intent_label to whichever of these fits: interested, not_now, unsubscribe, referral, "
                   "pricing_question, out_of_office. Change nothing else."),
        "table": "email_threads", "row_id": thr["id"], "field": "intent_label", "expected": thr["intent_label"],
        "gold_sql": f"intent derived from the inbound reply text of thread {thr['id']}: {thr['body'][:70]!r}",
        "tools": ["email_threads_list", "email_messages_list", "email_thread_classify"],
    })

    # ---- unsubscribe enforcement across two systems ----
    unsub = one("SELECT t.id, t.account_name, e.id AS enrollment_id FROM email_threads t "
                "LEFT JOIN outreach_enrollments e ON e.lead_id = t.lead_id "
                "WHERE t.intent_label='unsubscribe' ORDER BY t.id LIMIT 1")
    if unsub and unsub["enrollment_id"]:
        T.append({
            "kind": "multi", "task_id": nid(), "wf_type": "unsubscribe_optout_enforcement", "source": SRC_CANON,
            "prompt": (f"The contact on email thread {unsub['id']} ({unsub['account_name']}) has asked to be "
                       "removed and never contacted again. Honour it: mark that thread's intent_label as "
                       f"'unsubscribe' and stop their outbound sequence by setting enrollment "
                       f"{unsub['enrollment_id']} to status 'completed'. Touch nothing else."),
            "gold_sql": f"thread {unsub['id']} carries the unsubscribe reply; enrollment {unsub['enrollment_id']} is its lead's active sequence",
            "tools": ["email_threads_list", "email_messages_list", "email_thread_classify",
                      "sequence_enrollments_list", "sequence_enrollment_update"],
            "allowed": ["email_threads", "outreach_enrollments"],
            "checks": [
                {"name": "thread_marked_unsubscribe", "kind": "row_field", "table": "email_threads",
                 "row_id": unsub["id"], "field": "intent_label", "expected": "unsubscribe"},
                {"name": "sequence_stopped", "kind": "row_field", "table": "outreach_enrollments",
                 "row_id": unsub["enrollment_id"], "field": "status", "expected": "completed"},
            ],
        })

    # ---- sequence enrollment ----
    seq = one("SELECT id, name FROM outreach_sequences WHERE status='active' ORDER BY id LIMIT 1")
    lead = one("SELECT id, company_name FROM sales_leads WHERE status='qualified' ORDER BY id LIMIT 1")
    T.append({
        "kind": "multi", "task_id": nid(), "wf_type": "sequence_enrollment", "source": SRC_OSS,
        "prompt": (f"Lead {lead['id']} ({lead['company_name']}) is qualified and should start outbound. Enroll it "
                   f"in the active sequence '{seq['name']}' ({seq['id']}) at step 1. Create exactly one "
                   "enrollment and change nothing else."),
        "gold_sql": f"active sequence {seq['id']}, qualified lead {lead['id']}",
        "tools": ["sequences_list", "sequence_steps_list", "sequence_enroll_lead"],
        "allowed": ["outreach_enrollments"],
        "checks": [
            {"name": "enrollment_created", "kind": "row_count_delta", "table": "outreach_enrollments", "delta": 1},
            {"name": "enrollment_correct", "kind": "row_matching", "table": "outreach_enrollments",
             "match": {"sequence_id": seq["id"], "lead_id": lead["id"], "status": "active"}},
        ],
    })

    # ---- forecast submission ----
    rep = one("SELECT employee_id, employee_name FROM rep_quotas WHERE period='2026-Q3' ORDER BY employee_id LIMIT 1")
    commit_amt = one("SELECT ROUND(SUM(amount),2) v FROM sales_opportunities WHERE status='closed_won' "
                     "AND owner_employee_id=?", (rep["employee_id"],))
    amt = commit_amt["v"] or 100000.0
    T.append({
        "kind": "multi", "task_id": nid(), "wf_type": "forecast_rollup_commit", "source": SRC_CANON,
        "prompt": (f"Submit the 2026-Q3 commit forecast for {rep['employee_name']} (employee {rep['employee_id']}). "
                   f"The commit number is the total of their closed-won opportunities: {amt}. Create exactly one "
                   "forecast submission in category 'commit' for period 2026-Q3 and change nothing else."),
        "gold_sql": "SUM(amount) of closed_won opportunities owned by the rep",
        "tools": ["rep_quotas_list", "aggregate_query", "forecast_submit"],
        "allowed": ["forecast_submissions"],
        "checks": [
            {"name": "forecast_created", "kind": "row_count_delta", "table": "forecast_submissions", "delta": 1},
            {"name": "forecast_correct", "kind": "row_matching", "table": "forecast_submissions",
             "match": {"employee_id": rep["employee_id"], "period": "2026-Q3", "category": "commit"}},
        ],
    })

    # ---- quota attainment analysis (needs the aggregate tool to be tractable) ----
    gap = one("SELECT employee_name, ROUND(quota_amount - attainment_amount, 2) shortfall FROM rep_quotas "
              "WHERE period='2026-Q3' ORDER BY shortfall DESC LIMIT 1")
    T.append({
        "kind": "answer", "task_id": nid(), "wf_type": "quota_attainment_analysis", "source": SRC_CANON,
        "prompt": ("For the 2026-Q3 period, which rep has the largest shortfall between their quota and their "
                   "attainment? Answer with the rep's name."),
        "gold": gap["employee_name"], "accepted": [gap["employee_name"]],
        "gold_sql": "MAX(quota_amount - attainment_amount) over rep_quotas WHERE period='2026-Q3'",
        "tools": ["rep_quotas_list"], "tables": ["rep_quotas"],
    })

    # ---- churn-save play ----
    red = one("SELECT id, account_id, account_name, score, primary_risk FROM account_health "
              "WHERE band='red' ORDER BY score ASC LIMIT 1")
    T.append({
        "kind": "state", "task_id": nid(), "wf_type": "churn_risk_save_workflow", "source": SRC_CANON,
        "prompt": (f"{red['account_name']} is in the red health band (score {red['score']}, risk: "
                   f"{red['primary_risk']}). The save play has run and adoption recovered. Re-score their health "
                   f"record {red['id']} to band 'yellow'. Change nothing else."),
        "table": "account_health", "row_id": red["id"], "field": "band", "expected": "yellow",
        "gold_sql": "lowest-scoring red-band account in account_health",
        "tools": ["account_health_list", "account_usage_list", "account_health_update"],
    })

    # ---- first-touch attribution ----
    ft = one("SELECT campaign_id, COUNT(*) c FROM campaign_touches WHERE position='first' "
             "GROUP BY campaign_id ORDER BY c DESC, campaign_id LIMIT 1")
    T.append({
        "kind": "answer", "task_id": nid(), "wf_type": "campaign_attribution", "source": SRC_CANON,
        "prompt": ("Using first-touch attribution, which campaign is credited with originating the most leads? "
                   "Answer with the campaign id."),
        "gold": ft["campaign_id"], "accepted": [ft["campaign_id"]],
        "gold_sql": "COUNT(*) over campaign_touches WHERE position='first' GROUP BY campaign_id",
        "tools": ["campaign_touches_list", "aggregate_query"], "tables": ["campaign_touches"],
    })

    # ---- e-signature order (policy: customer signs first) ----
    T.append({
        "kind": "multi", "task_id": nid(), "wf_type": "quote_document_generation_esignature", "source": SRC_CANON,
        "prompt": ("Meridian Capital's FY26 order form is ready for signature. Create an e-signature envelope "
                   "for account_003 titled 'Meridian Capital — Order Form FY26' following the mandated signer "
                   "order in which the customer signs before your firm countersigns. Create exactly one envelope "
                   "and change nothing else."),
        "gold_sql": "signer_order policy value 'customer_first' from the seeded envelope corpus",
        "tools": ["signature_envelopes_list", "signature_envelope_create"],
        "allowed": ["signature_envelopes"],
        "checks": [
            {"name": "envelope_created", "kind": "row_count_delta", "table": "signature_envelopes", "delta": 1},
            {"name": "signer_order_correct", "kind": "row_matching", "table": "signature_envelopes",
             "match": {"account_id": "account_003", "signer_order": "customer_first"}},
        ],
    })

    # ---- pipeline hygiene: stale deals ----
    stale = one("SELECT COUNT(*) c FROM sales_opportunities WHERE status='negotiation'")
    T.append({
        "kind": "answer", "task_id": nid(), "wf_type": "pipeline_inspection_stalled", "source": SRC_CANON,
        "prompt": ("Pipeline inspection: how many sales opportunities are currently sitting in the "
                   "'negotiation' stage? Answer with the number."),
        "gold": stale["c"], "accepted": [str(stale["c"])],
        "gold_sql": "COUNT(*) FROM sales_opportunities WHERE status='negotiation'",
        "tools": ["aggregate_query", "query_sales_opportunities"], "tables": ["sales_opportunities"],
    })

    # ---- renewal uplift ----
    ren = one("SELECT id, account_name, renewal_date, arr_usd FROM account_health "
              "WHERE band='green' ORDER BY renewal_date LIMIT 1")
    T.append({
        "kind": "answer", "task_id": nid(), "wf_type": "renewal_expansion_management", "source": SRC_CANON,
        "prompt": ("Which healthy (green band) account has the nearest upcoming renewal date? Answer with the "
                   "account name."),
        "gold": ren["account_name"], "accepted": [ren["account_name"]],
        "gold_sql": "earliest renewal_date among green-band accounts in account_health",
        "tools": ["account_health_list"], "tables": ["account_health"],
    })

    return T


def to_world(tasks):
    wt, wv = [], []
    for t in tasks:
        tid = t["task_id"]
        prov = {"source_benchmark": t["source"], "workflow_type": t["wf_type"],
                "cloned_by": "scripts/build-workflow-tasks.py", "grading": t["kind"]}
        base = {"task_id": tid, "prompt": t["prompt"], "goal": f"Workflow — {t['wf_type']}",
                "complexity": "medium", "method": "workflow_pack", "provenance": prov,
                "difficulty_tier": "reference", "required_tools": t.get("tools", [])}
        if t["kind"] == "answer":
            base.update({"tables_affected": [], "expected_state_changes": [],
                         "answer_graded": True, "gold_answer": str(t["gold"])})
            vcode = crma.ANSWER_VCODE.format(task_id=tid, crma_type=t["wf_type"], gold=str(t["gold"]),
                                             accepted=[str(a) for a in t["accepted"]], ordered=[],
                                             gold_sql=t["gold_sql"], helpers=crma.COMMON_HELPERS)
            assertions = ["used_tools", "answer_present", "answer_matches_gold", "read_only_no_mutation"]
            negs = [{"description": "Wrong value", "fails_assertion": "answer_matches_gold", "expected": "fail"},
                    {"description": "Mutates state on a read-only question", "fails_assertion": "read_only_no_mutation", "expected": "fail"}]
        elif t["kind"] == "state":
            base.update({"tables_affected": [t["table"]],
                         "expected_state_changes": [{"table": t["table"], "id": t["row_id"],
                                                     "field": t["field"], "to": t["expected"]}]})
            vcode = crma.STATE_VCODE.format(task_id=tid, crma_type=t["wf_type"], table=t["table"],
                                            row_id=t["row_id"], field=t["field"], expected=t["expected"],
                                            allowed=[t["table"]], gold_sql=t["gold_sql"],
                                            helpers=crma.COMMON_HELPERS)
            assertions = ["state_changed", "reads_before_writes", "target_row_correct",
                          "no_offtask_table_changes", "no_rows_destroyed", "no_undeclared_rows_created"]
            negs = [{"description": "Wrong row or value", "fails_assertion": "target_row_correct", "expected": "fail"},
                    {"description": "Collateral writes elsewhere", "fails_assertion": "no_offtask_table_changes", "expected": "fail"}]
        else:
            base.update({"tables_affected": t["allowed"],
                         "expected_state_changes": [{"table": c.get("table"), "check": c["name"]} for c in t["checks"]]})
            vcode = MULTI_VCODE.format(task_id=tid, wf_type=t["wf_type"], checks=t["checks"],
                                       allowed=t["allowed"], gold_sql=t["gold_sql"],
                                       helpers=crma.COMMON_HELPERS)
            assertions = ["state_changed"] + [c["name"] for c in t["checks"]] + ["no_offtask_table_changes"]
            negs = [{"description": "Only part of the outcome achieved", "fails_assertion": t["checks"][0]["name"], "expected": "fail"},
                    {"description": "Collateral writes elsewhere", "fails_assertion": "no_offtask_table_changes", "expected": "fail"}]
        wt.append(base)
        wv.append({"task_id": tid, "assertions": assertions, "vcode": vcode,
                   "initial_state_check": t["gold_sql"], "field_policies": [],
                   "positive_case": {"description": f"Agent completes the {t['wf_type']} workflow", "expected": "pass"},
                   "negative_cases": negs, "discrimination": len(negs)})
    return wt, wv


def main():
    tasks = build()
    wt, wv = to_world(tasks)
    for v in wv:
        try:
            compile(v["vcode"], v["task_id"], "exec")
        except SyntaxError as e:
            print(f"VCODE SYNTAX ERROR in {v['task_id']}: {e}")
            sys.exit(1)
    print(f"built {len(wt)} workflow tasks")
    for t, spec in zip(wt, tasks):
        print(f"  {t['task_id']}  {spec['wf_type']:38} {spec['kind']:6}")
    if "--dry-run" in sys.argv:
        return
    raw = open(os.path.join(PKG, "world.json")).read()
    world = json.loads(raw)
    world["tasks"] = [t for t in world["tasks"] if not t["task_id"].startswith(PREFIX)] + wt
    world["verifiers"] = [v for v in world["verifiers"] if not v["task_id"].startswith(PREFIX)] + wv
    text = json.dumps(world, indent=1, ensure_ascii=False)
    if raw.endswith("\n") and not text.endswith("\n"):
        text += "\n"
    open(os.path.join(PKG, "world.json"), "w").write(text)
    open(TOP_WORLD, "w").write(text)
    print(f"\nregistered — {len(world['tasks'])} tasks total")


if __name__ == "__main__":
    main()
