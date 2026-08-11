"""VCode verifier for wf_001 — workflow task (lead_dedupe_merge)

Grading: several row-level outcomes must ALL hold, with collateral guards.
Targets computed from the world database at build time:
    duplicate pair on company_name='Crestline Trust': master=903, victim=904
"""
CHECKS = [{'name': 'duplicate_removed', 'kind': 'row_absent', 'table': 'sales_leads', 'row_id': 904}, {'name': 'survivorship_filled', 'kind': 'row_field', 'table': 'sales_leads', 'row_id': 903, 'field': 'estimated_value', 'expected': 98000.0}, {'name': 'child_reparented', 'kind': 'row_field', 'table': 'sales_opportunities', 'row_id': 9001, 'field': 'lead_id', 'expected': 903}]
ALLOWED_TABLES = ['sales_leads', 'sales_opportunities', 'lead_merge_log']

def _rows(state, table):
    return state.get(table, []) if isinstance(state, dict) else []

def _norm(text):
    if text is None:
        return ""
    s = str(text).strip().lower()
    for ch in ['"', "'", "`", "*", "\u2019"]:
        s = s.replace(ch, "")
    s = s.rstrip(".!")
    while "  " in s:
        s = s.replace("  ", " ")
    return s

def _final_answer(trace):
    for step in reversed(trace):
        if step.get("tool") == "_final_answer":
            args = step.get("arguments") or {}
            return args.get("answer")
    return None

def _successful(trace):
    return [s for s in trace if s.get("tool") != "_final_answer" and s.get("ok")]

def _tables_changed(initial_state, final_state):
    changed = []
    keys = set(initial_state or {}) | set(final_state or {})
    for t in sorted(keys):
        if _rows(initial_state, t) != _rows(final_state, t):
            changed.append(t)
    return changed


def _find(rows, row_id):
    for r in rows:
        if isinstance(r, dict) and str(r.get("id")) == str(row_id):
            return r
    return None

def verify(initial_state, final_state, trace):
    results, failed = [], []
    def chk(name, passed, detail):
        results.append({"name": name, "passed": bool(passed), "details": detail})
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
            chk(name, ok, "{}.{} == {!r}".format(table, c["field"], c["expected"]) if ok
                else "expected {}.{} == {!r} on {}, got {!r}".format(table, c["field"], c["expected"], c["row_id"], got))
        elif kind == "row_absent":
            ok = _find(rows, c["row_id"]) is None
            chk(name, ok, "row {} removed from {}".format(c["row_id"], table) if ok
                else "row {} still present in {}".format(c["row_id"], table))
        elif kind == "row_count_delta":
            before, after = len(_rows(initial_state, table)), len(rows)
            ok = (after - before) == c["delta"]
            chk(name, ok, "{} changed by {}".format(table, after - before) if ok
                else "expected {} to change by {}, saw {}".format(table, c["delta"], after - before))
        elif kind == "row_matching":
            hits = [r for r in rows if all(_norm(r.get(k)) == _norm(v) for k, v in c["match"].items())]
            ok = len(hits) >= c.get("at_least", 1)
            chk(name, ok, "{} row(s) in {} match {}".format(len(hits), table, c["match"]) if ok
                else "no row in {} matches {}".format(table, c["match"]))

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
    return {
        "task_id": "wf_001",
        "passed": len(structural_failed) == 0,
        "reward": round(reward, 4),
        "explanation": "All task checks passed" if not structural_failed else "Failed: " + ", ".join(structural_failed),
        "failed_conditions": structural_failed,
        "advisory_conditions": [],
        "assertions": results,
    }
