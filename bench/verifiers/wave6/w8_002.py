"""VCode verifier for w8_002 — data-derived cardinality (crm_data_hygiene_audit)

The agent must act on exactly the records that are genuinely defective — no
more, no fewer. The expected set was computed from the world at build time, so
padding the output and truncating it both fail.

Defective records: ['Harborview Partners', 'Crestline Trust', 'Crestline Trust']
"""
TARGETS = ['Harborview Partners', 'Crestline Trust', 'Crestline Trust']
TABLE = 'tasks'
ALLOWED_TABLES = ['tasks']

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


def verify(initial_state, final_state, trace):
    results, failed = [], []
    def chk(name, passed, detail):
        results.append({"name": name, "passed": bool(passed), "details": detail})
        if not passed:
            failed.append(name)

    before = {str(r.get("id")) for r in _rows(initial_state, TABLE)}
    created = [r for r in _rows(final_state, TABLE) if str(r.get("id")) not in before]

    chk("state_changed", initial_state != final_state,
        "world state changed" if initial_state != final_state else "NO state change — agent did nothing")

    chk("exact_cardinality", len(created) == len(TARGETS),
        "created exactly {} record(s), one per defective row".format(len(TARGETS))
        if len(created) == len(TARGETS)
        else "expected {} new row(s) in {}, saw {}".format(len(TARGETS), TABLE, len(created)))

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
    return {
        "task_id": "w8_002",
        "passed": len(structural_failed) == 0,
        "reward": round(reward, 4),
        "explanation": "All task checks passed" if not structural_failed else "Failed: " + ", ".join(structural_failed),
        "failed_conditions": structural_failed,
        "advisory_conditions": [],
        "assertions": results,
    }
