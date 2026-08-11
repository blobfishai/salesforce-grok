"""VCode verifier for crma_006 — CRMArena clone (named_entity_disambiguation)

Grading: exact-match on the agent's final answer (normalized), plus a read-only
guard. Gold was computed from the world database at build time:
    SELECT product_code, COUNT(*) n FROM service_cases GROUP BY 1 ORDER BY n DESC LIMIT 1
"""
GOLD = 'Wealth Platform License'
ACCEPTED = ['Wealth Platform License', 'PROD-PLAT']
# For multi-part answers (e.g. an approval sequence) the agent legitimately
# replies in prose. Grade the ORDER of the required tokens rather than demanding
# one literal string — still deterministic, no judge.
ORDERED_TOKENS = []

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

    steps = _successful(trace)
    chk("used_tools", len(steps) > 0,
        "agent called {} tool(s)".format(len(steps)) if steps else "no successful tool calls — answered without consulting the world")

    answer = _final_answer(trace)
    chk("answer_present", answer is not None,
        "final answer recorded" if answer is not None else "agent never produced a final answer")

    norm = _norm(answer)
    hit = any(_norm(a) == norm for a in ACCEPTED) or any(_norm(a) in norm for a in ACCEPTED)
    if not hit and ORDERED_TOKENS:
        pos, ordered_ok = -1, True
        for tok in ORDERED_TOKENS:
            nxt = norm.find(_norm(tok), pos + 1)
            if nxt <= pos:
                ordered_ok = False
                break
            pos = nxt
        hit = ordered_ok
    chk("answer_matches_gold", bool(answer) and hit,
        "answer matches gold {!r}".format(GOLD) if hit else "expected {!r}, got {!r}".format(GOLD, answer))

    changed = _tables_changed(initial_state, final_state)
    chk("read_only_no_mutation", not changed,
        "world state untouched" if not changed else "analytics task mutated: " + ", ".join(changed))

    structural_failed = list(failed)
    core = ["answer_matches_gold"]
    core_failed = [n for n in core if n in failed]
    guard_failed = [n for n in ["read_only_no_mutation"] if n in failed]
    reward = 0.0 if (guard_failed or core_failed) else 1.0
    return {
        "task_id": "crma_006",
        "passed": len(structural_failed) == 0,
        "reward": round(reward, 4),
        "explanation": "All task checks passed" if not structural_failed else "Failed: " + ", ".join(structural_failed),
        "failed_conditions": structural_failed,
        "advisory_conditions": [],
        "assertions": results,
    }
