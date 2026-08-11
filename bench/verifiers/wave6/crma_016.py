"""VCode verifier for crma_016 — CRMArena clone (case_routing)

Grading: the target row must end in the required state, with collateral guards.
Target computed from the world database at build time:
    target case case_svc_0081 selected as the highest-priority open case
"""
TABLE = 'service_cases'
ROW_ID = 'case_svc_0081'
FIELD = 'status'
EXPECTED = 'escalated'
ALLOWED_TABLES = ['service_cases']

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

    steps = _successful(trace)
    tools = [s.get("tool", "") for s in steps]
    read_idx = next((i for i, t in enumerate(tools) if "list" in t or "get" in t or "query" in t or "search" in t), None)
    write_idx = next((i for i, t in enumerate(tools) if "update" in t or "create" in t or "assign" in t), None)

    chk("state_changed", initial_state != final_state,
        "world state changed" if initial_state != final_state else "NO state change — agent did nothing")

    chk("reads_before_writes", write_idx is None or (read_idx is not None and read_idx < write_idx),
        "inspected before writing" if write_idx is None or (read_idx is not None and read_idx < write_idx)
        else "blind write with no prior read")

    row = _find(_rows(final_state, TABLE), ROW_ID)
    got = row.get(FIELD) if row else None
    ok = row is not None and _norm(got) == _norm(EXPECTED)
    chk("target_row_correct", ok,
        "{}.{} of {} == {!r}".format(TABLE, FIELD, ROW_ID, EXPECTED) if ok
        else "expected {}.{} == {!r} for {}, got {!r}".format(TABLE, FIELD, EXPECTED, ROW_ID, got))

    changed = _tables_changed(initial_state, final_state)
    offtask = [t for t in changed if t not in ALLOWED_TABLES]
    chk("no_offtask_table_changes", not offtask,
        "only permitted tables changed" if not offtask else "collateral damage in: " + ", ".join(offtask))

    for t in ALLOWED_TABLES:
        before, after = _rows(initial_state, t), _rows(final_state, t)
        if len(after) < len(before):
            chk("no_rows_destroyed", False, "rows deleted from {}: {} -> {}".format(t, len(before), len(after)))
            break
    else:
        chk("no_rows_destroyed", True, "no rows destroyed")

    extra = []
    for t in ALLOWED_TABLES:
        before, after = _rows(initial_state, t), _rows(final_state, t)
        if len(after) > len(before):
            extra.append("{} (+{})".format(t, len(after) - len(before)))
    chk("no_undeclared_rows_created", not extra,
        "no unexpected inserts" if not extra else "unexpected inserts: " + ", ".join(extra))

    structural_failed = list(failed)
    guards = ["no_offtask_table_changes", "no_rows_destroyed", "no_undeclared_rows_created"]
    guard_failed = [n for n in guards if n in failed]
    core_failed = [n for n in ["target_row_correct"] if n in failed]
    reward = 0.0 if (guard_failed or core_failed) else 1.0
    return {
        "task_id": "crma_016",
        "passed": len(structural_failed) == 0,
        "reward": round(reward, 4),
        "explanation": "All task checks passed" if not structural_failed else "Failed: " + ", ".join(structural_failed),
        "failed_conditions": structural_failed,
        "advisory_conditions": [],
        "assertions": results,
    }
