#!/usr/bin/env python3
"""Wave-8 pack: two grading properties this world could not previously express.

The workflow canon (research/answers/sales-workflow-canon.md) argues that the
strongest verifiers are not field assertions but **conservation identities** —
algebraic invariants that "fail loudly under partial work" — and that the second
strongest bind an outcome's *cardinality* to what the data actually contains, so
an agent cannot pass by doing some of the work.

Both are implemented here:

  identity     the agent writes a funnel summary; the verifier recomputes every
               bucket from the database AND asserts the buckets sum to the
               population. A summary that is internally consistent but wrong
               fails; so does one that is right in places and drops a bucket.
  cardinality  the agent must open one remediation task per genuinely defective
               record — no more, no fewer. The expected count is derived from
               the data at build time, so padding or truncating both fail.

Golds are computed from seed.db, like every other pack.

Run: python3 scripts/build-wave8-tasks.py [--dry-run]
"""
import importlib.util
import json
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, "world", "blobfish-wave6", "package", "sbx_291042075d7547f4")
TOP_WORLD = os.path.join(ROOT, "world", "blobfish-wave6", "world.json")
PREFIX = "w8_"

_spec = importlib.util.spec_from_file_location("crma", os.path.join(ROOT, "scripts", "build-crmarena-tasks.py"))
crma = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(crma)

conn = sqlite3.connect(os.path.join(PKG, "seed.db"))
conn.row_factory = sqlite3.Row
q = lambda s, a=(): [dict(r) for r in conn.execute(s, a).fetchall()]
one = lambda s, a=(): (q(s, a) or [None])[0]

IDENTITY_VCODE = '''"""VCode verifier for {task_id} — conservation identity ({wf_type})

The agent's written summary is checked three ways: every bucket must match the
value recomputed from the world, the buckets must SUM to the population, and the
population itself must be right. A summary that is internally consistent but
wrong fails, and so does one that is right in places but silently drops a bucket.

Expected, computed from the world at build time:
    {expected!r}
"""
EXPECTED = {expected!r}
TOTAL = {total!r}
SHEET_TABLE = "agent_sheet_rows"
{helpers}

def _numbers_in(text):
    out, buf = [], ""
    for ch in str(text) + " ":
        if ch.isdigit():
            buf += ch
        elif ch == ",":
            continue
        else:
            if buf:
                out.append(int(buf))
                buf = ""
    return out

def verify(initial_state, final_state, trace):
    results, failed = [], []
    def chk(name, passed, detail):
        results.append({{"name": name, "passed": bool(passed), "details": detail}})
        if not passed:
            failed.append(name)

    # the summary may be written to the sheet OR stated in the final answer;
    # both are legitimate deliverables for this request
    written = ""
    before = {{str(r.get("id")) for r in _rows(initial_state, SHEET_TABLE)}}
    for r in _rows(final_state, SHEET_TABLE):
        if str(r.get("id")) not in before:
            written += " " + str(r.get("cells", ""))
    surface = (written + " " + str(_final_answer(trace) or "")).lower()

    chk("reported_something", bool(surface.strip()),
        "a summary was produced" if surface.strip() else "no summary was written or stated")

    missing = []
    for bucket, count in EXPECTED.items():
        # the bucket label must appear with its exact count somewhere near it
        idx = surface.find(bucket.lower())
        window = surface[max(0, idx - 90): idx + 90] if idx >= 0 else ""
        if idx < 0 or count not in _numbers_in(window):
            missing.append("{{}}={{}}".format(bucket, count))
    chk("every_bucket_correct", not missing,
        "all {{}} buckets match the world".format(len(EXPECTED)) if not missing
        else "wrong or missing: " + ", ".join(missing))

    nums = _numbers_in(surface)
    chk("population_stated", TOTAL in nums,
        "population {{}} reported".format(TOTAL) if TOTAL in nums
        else "the total population ({{}}) never appears".format(TOTAL))

    # the identity itself: the parts must account for the whole
    identity_holds = sum(EXPECTED.values()) == TOTAL
    chk("conservation_identity", identity_holds and not missing and TOTAL in nums,
        "buckets sum to the population ({{}} = {{}})".format(" + ".join(str(v) for v in EXPECTED.values()), TOTAL)
        if (identity_holds and not missing and TOTAL in nums)
        else "the reported parts do not account for the whole")

    structural_failed = list(failed)
    reward = 0.0 if structural_failed else 1.0
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

CARDINALITY_VCODE = '''"""VCode verifier for {task_id} — data-derived cardinality ({wf_type})

The agent must act on exactly the records that are genuinely defective — no
more, no fewer. The expected set was computed from the world at build time, so
padding the output and truncating it both fail.

Defective records: {targets!r}
"""
TARGETS = {targets!r}
TABLE = {table!r}
ALLOWED_TABLES = {allowed!r}
{helpers}

def verify(initial_state, final_state, trace):
    results, failed = [], []
    def chk(name, passed, detail):
        results.append({{"name": name, "passed": bool(passed), "details": detail}})
        if not passed:
            failed.append(name)

    before = {{str(r.get("id")) for r in _rows(initial_state, TABLE)}}
    created = [r for r in _rows(final_state, TABLE) if str(r.get("id")) not in before]

    chk("state_changed", initial_state != final_state,
        "world state changed" if initial_state != final_state else "NO state change — agent did nothing")

    chk("exact_cardinality", len(created) == len(TARGETS),
        "created exactly {{}} record(s), one per defective row".format(len(TARGETS))
        if len(created) == len(TARGETS)
        else "expected {{}} new row(s) in {{}}, saw {{}}".format(len(TARGETS), TABLE, len(created)))

    # stringify row values directly — the verifier sandbox provides no imports
    blob = " ".join(str(v).lower() for r in created for v in r.values()) if created else ""
    uncovered = [t for t in TARGETS if _norm(t).lower() not in blob]
    chk("every_target_covered", not uncovered,
        "every defective record is referenced" if not uncovered
        else "no created record references: " + ", ".join(str(u) for u in uncovered))

    changed = _tables_changed(initial_state, final_state)
    offtask = [t for t in changed if t not in ALLOWED_TABLES]
    chk("no_offtask_table_changes", not offtask,
        "only permitted tables changed" if not offtask else "collateral damage in: " + ", ".join(offtask))

    structural_failed = list(failed)
    reward = 0.0 if structural_failed else 1.0
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
    T, n = [], 0

    def nid():
        nonlocal n
        n += 1
        return f"{PREFIX}{n:03d}"

    # --- conservation identity: the funnel must account for every lead --------
    buckets = {r["status"]: r["n"] for r in
               q("SELECT status, COUNT(*) n FROM sales_leads GROUP BY status ORDER BY n DESC")}
    total = one("SELECT COUNT(*) n FROM sales_leads")["n"]
    assert sum(buckets.values()) == total
    T.append({
        "kind": "identity", "task_id": nid(), "wf_type": "funnel_conversion_waterfall",
        "prompt": ("Marketing and sales keep quoting different funnel numbers at each other. Give me the "
                   "definitive breakdown of the lead database by status — every stage with its count, plus "
                   "the total — so the two teams are working off one set of numbers."),
        "expected": buckets, "total": total,
        "tools": ["aggregate_query", "query_sales_leads", "sheet_agent"],
    })

    # --- data-derived cardinality: one remediation task per defective lead -----
    defective = q("SELECT id, company_name FROM sales_leads "
                  "WHERE estimated_value IS NULL OR source IS NULL OR source = '' ORDER BY id")
    T.append({
        "kind": "cardinality", "task_id": nid(), "wf_type": "crm_data_hygiene_audit",
        "prompt": ("Data hygiene sweep before the QBR: some leads are missing the deal size or the source "
                   "that tells us where they came from. Find every one of them and open a follow-up task "
                   "for each so the owning rep fixes their own record — one task per broken lead, and put "
                   "the lead's company name in the task so the rep knows what to look at."),
        "targets": [d["company_name"] for d in defective],
        "table": "tasks", "allowed": ["tasks"],
        "tools": ["query_sales_leads", "aggregate_query", "task_create"],
    })

    return T


def to_world(tasks):
    wt, wv = [], []
    for t in tasks:
        tid = t["task_id"]
        prov = {"source_benchmark": "sales workflow canon — conservation identities and "
                                    "data-derived cardinality (research/answers/sales-workflow-canon.md)",
                "workflow_type": t["wf_type"], "cloned_by": "scripts/build-wave8-tasks.py",
                "grading": t["kind"]}
        base = {"task_id": tid, "prompt": t["prompt"], "goal": f"Wave-8 — {t['wf_type']}",
                "complexity": "high", "method": "wave8_pack", "provenance": prov,
                "difficulty_tier": "reference", "required_tools": t["tools"]}
        if t["kind"] == "identity":
            base.update({"tables_affected": [], "expected_state_changes": [], "answer_graded": True,
                         "gold_answer": json.dumps(t["expected"])})
            vcode = IDENTITY_VCODE.format(task_id=tid, wf_type=t["wf_type"], expected=t["expected"],
                                          total=t["total"], helpers=crma.COMMON_HELPERS)
            assertions = ["reported_something", "every_bucket_correct", "population_stated",
                          "conservation_identity"]
            negs = [{"description": "One bucket omitted or wrong", "fails_assertion": "every_bucket_correct", "expected": "fail"},
                    {"description": "Parts do not sum to the whole", "fails_assertion": "conservation_identity", "expected": "fail"}]
        else:
            base.update({"tables_affected": [t["table"]],
                         "expected_state_changes": [{"table": t["table"], "rows": len(t["targets"])}]})
            vcode = CARDINALITY_VCODE.format(task_id=tid, wf_type=t["wf_type"], targets=t["targets"],
                                             table=t["table"], allowed=t["allowed"],
                                             helpers=crma.COMMON_HELPERS)
            assertions = ["state_changed", "exact_cardinality", "every_target_covered",
                          "no_offtask_table_changes"]
            negs = [{"description": "Fixes some but not all defective records", "fails_assertion": "exact_cardinality", "expected": "fail"},
                    {"description": "Pads the output with tasks for healthy records", "fails_assertion": "exact_cardinality", "expected": "fail"},
                    {"description": "Right count, wrong records", "fails_assertion": "every_target_covered", "expected": "fail"}]
        wt.append(base)
        wv.append({"task_id": tid, "assertions": assertions, "vcode": vcode,
                   "initial_state_check": json.dumps(t.get("expected") or t.get("targets")),
                   "field_policies": [],
                   "positive_case": {"description": f"Agent completes {t['wf_type']} correctly", "expected": "pass"},
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
    print(f"built {len(wt)} wave-8 tasks")
    for t, spec in zip(wt, tasks):
        detail = (f"identity over {len(spec.get('expected', {}))} buckets / {spec.get('total')} rows"
                  if spec["kind"] == "identity" else f"{len(spec.get('targets', []))} defective records")
        print(f"  {t['task_id']}  {spec['wf_type']:34} {spec['kind']:12} {detail}")
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
