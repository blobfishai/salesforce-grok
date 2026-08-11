"""VCode verifier for w8_001 — conservation identity (funnel_conversion_waterfall)

The agent's written summary is checked three ways: every bucket must match the
value recomputed from the world, the buckets must SUM to the population, and the
population itself must be right. A summary that is internally consistent but
wrong fails, and so does one that is right in places but silently drops a bucket.

Expected, computed from the world at build time:
    {'converted': 168, 'contacted': 129, 'qualified': 111, 'new': 53, 'lost': 42, 'working': 1}
"""
EXPECTED = {'converted': 168, 'contacted': 129, 'qualified': 111, 'new': 53, 'lost': 42, 'working': 1}
TOTAL = 504
SHEET_TABLE = "agent_sheet_rows"

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
        results.append({"name": name, "passed": bool(passed), "details": detail})
        if not passed:
            failed.append(name)

    # the summary may be written to the sheet OR stated in the final answer;
    # both are legitimate deliverables for this request
    written = ""
    before = {str(r.get("id")) for r in _rows(initial_state, SHEET_TABLE)}
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
            missing.append("{}={}".format(bucket, count))
    chk("every_bucket_correct", not missing,
        "all {} buckets match the world".format(len(EXPECTED)) if not missing
        else "wrong or missing: " + ", ".join(missing))

    nums = _numbers_in(surface)
    chk("population_stated", TOTAL in nums,
        "population {} reported".format(TOTAL) if TOTAL in nums
        else "the total population ({}) never appears".format(TOTAL))

    # the identity itself: the parts must account for the whole
    identity_holds = sum(EXPECTED.values()) == TOTAL
    chk("conservation_identity", identity_holds and not missing and TOTAL in nums,
        "buckets sum to the population ({} = {})".format(" + ".join(str(v) for v in EXPECTED.values()), TOTAL)
        if (identity_holds and not missing and TOTAL in nums)
        else "the reported parts do not account for the whole")

    structural_failed = list(failed)
    reward = 0.0 if structural_failed else 1.0
    return {
        "task_id": "w8_001",
        "passed": len(structural_failed) == 0,
        "reward": round(reward, 4),
        "explanation": "All task checks passed" if not structural_failed else "Failed: " + ", ".join(structural_failed),
        "failed_conditions": structural_failed,
        "advisory_conditions": [],
        "assertions": results,
    }
