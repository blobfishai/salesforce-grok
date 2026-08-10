#!/usr/bin/env python3
"""Smoke-test every spec-generated vendor tool against a scratch copy of seed.db.

Envelope-aware: probes understand each namespace's 1:1 vendor response format
(Stripe data/error.code, Slack ok/error, Google kind/error.code, PagerDuty
plural-key/error.code, Notion object/status, GitHub bare arrays/status, NetSuite
items/o:errorDetails, Jira values/errorMessages, SendGrid result/errors).

State-changing probes (create/update/delete) verify the DATABASE directly, so
they hold regardless of envelope shape. Friction is bypassed via
`.blobfish_original` (which still includes the envelope layer). Custom tools are
called with generically-bound required params; any dict/list return passes,
raising fails.

Run AFTER scripts/densify-vendor-tools.py + create_db.py. Non-zero exit on any
failure; prints per-tool PASS/FAIL.
"""
import json
import os
import shutil
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, "world", "blobfish-wave6", "package", "sbx_291042075d7547f4")
SPECS_DIR = os.path.join(ROOT, "world", "blobfish-wave6", "tool-specs")
SCRATCH = os.environ.get("SMOKE_DB") or os.path.join(
    os.environ.get("TMPDIR", "/tmp"), "densify-smoke-state.db")

GENERIC = {"string": "smoke_test_value", "integer": 2, "number": 1.5,
           "boolean": True, "object": {}, "array": []}


def response_key(t, ns):
    rk = t.get("response_key")
    if rk:
        return rk
    table = t["table"]
    for prefix in (ns + "_", "slack_", "pd_", "gh_", "jira_", "notion_", "erp_", "sg_", "cal_"):
        if table.startswith(prefix):
            return table[len(prefix):]
    return table


def items_of(ns, r, rk):
    if ns == "github":
        return r if isinstance(r, list) else None
    if not isinstance(r, dict):
        return None
    if ns == "stripe":
        return r.get("data")
    if ns == "slack":
        return r.get(rk)
    if ns == "email":
        return r.get("result")
    if ns in ("calendar", "erp"):
        return r.get("items")
    if ns == "jira":
        return r.get("issues") if "issues" in r else r.get("values")
    if ns == "pagerduty":
        return r.get(rk)
    if ns == "notion":
        return r.get("results")
    return None


def is_not_found(ns, r):
    if not isinstance(r, dict):
        return False
    if ns == "stripe":
        return isinstance(r.get("error"), dict) and r["error"].get("code") == "resource_missing"
    if ns == "slack":
        return r.get("ok") is False and str(r.get("error", "")).endswith("_not_found")
    if ns == "email":
        return "errors" in r
    if ns == "calendar":
        return isinstance(r.get("error"), dict) and r["error"].get("code") == 404
    if ns == "erp":
        return r.get("status") == 404
    if ns == "jira":
        return "errorMessages" in r
    if ns == "pagerduty":
        return isinstance(r.get("error"), dict) and r["error"].get("code") == 2100
    if ns == "github":
        return r.get("status") == "404"
    if ns == "notion":
        return r.get("object") == "error" and r.get("status") == 404
    return False


def is_missing_params(ns, r):
    if not isinstance(r, dict):
        return False
    if ns == "stripe":
        return isinstance(r.get("error"), dict) and r["error"].get("code") == "parameter_missing"
    if ns == "slack":
        return r.get("ok") is False and r.get("error") == "invalid_arguments"
    if ns == "email":
        return "errors" in r
    if ns == "calendar":
        return isinstance(r.get("error"), dict) and r["error"].get("code") == 400
    if ns == "erp":
        return r.get("status") == 400
    if ns == "jira":
        return "errorMessages" in r
    if ns == "pagerduty":
        return isinstance(r.get("error"), dict) and r["error"].get("code") == 2001
    if ns == "github":
        return r.get("status") == "422"
    if ns == "notion":
        return r.get("object") == "error" and r.get("status") == 400
    return False


def fresh_db():
    shutil.copy2(os.path.join(PKG, "seed.db"), SCRATCH)
    leftover = SCRATCH + ".bf-friction"
    if os.path.exists(leftover):
        os.remove(leftover)
    return SCRATCH


def load_fn(source, name):
    ns = {}
    exec(source, ns)
    fn = ns[name]
    return getattr(fn, "blobfish_original", fn)


def query(db, sql, args=()):
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]
    finally:
        conn.close()


def row1(db, table, col=None):
    rows = query(db, f'SELECT * FROM "{table}" LIMIT 1')
    if not rows:
        return None
    return rows[0] if col is None else rows[0].get(col)


def count(db, table):
    return query(db, f'SELECT COUNT(*) AS n FROM "{table}"')[0]["n"]


def required_kwargs(t):
    return {p: GENERIC.get(t["params"][p].get("type", "string"), "smoke_test_value")
            for p in t.get("required", [])}


def probe(t, ns, fn, db):
    op, table = t["op"], t.get("table")
    idc = t.get("id_column", "id")
    rk = response_key(t, ns)
    if op in ("list", "search"):
        kwargs = required_kwargs(t)
        # required params that are also filters must hold REAL values from the
        # table, else they contradict the filter under test and match nothing
        base0 = row1(db, table)
        fmap0 = t.get("filter_map", {})
        for p in t.get("required", []):
            if p in t.get("filters", []) and base0 is not None:
                v = base0.get(fmap0.get(p, p))
                if v is not None:
                    kwargs[p] = v
        if op == "search":
            qp = t.get("query_param", "query")
            needle = "e"
            base = row1(db, table)
            for c in t.get("search_columns", []):
                v = (base or {}).get(c)
                if isinstance(v, str) and len(v) >= 3:
                    needle = v[1:4]
                    break
            kwargs[qp] = needle
        r = fn(db, **kwargs)
        items = items_of(ns, r, rk)
        assert isinstance(items, list), f"{op} envelope wrong: {json.dumps(r)[:160]}"
        if op == "list":
            base = row1(db, table)
            fmap = t.get("filter_map", {})
            for p in t.get("filters", []):
                val = (base or {}).get(fmap.get(p, p))
                if val is None:
                    continue
                fr = fn(db, **{**kwargs, p: val})
                fitems = items_of(ns, fr, rk)
                assert fitems, f"filter {p}={val!r} matched nothing"
        return "ok"
    if op == "get":
        rid = row1(db, table, idc)
        bogus = fn(db, **{**required_kwargs(t), t["id_param"]: "___smoke_bogus___"})
        assert is_not_found(ns, bogus), f"bogus id gave {json.dumps(bogus)[:160]}"
        noargs = fn(db)
        assert is_missing_params(ns, noargs), f"missing id gave {json.dumps(noargs)[:160]}"
        if rid is not None:
            r = fn(db, **{**required_kwargs(t), t["id_param"]: rid})
            assert not is_not_found(ns, r) and str(rid) in json.dumps(r), \
                f"real id {rid!r} gave {json.dumps(r)[:160]}"
        return "ok" if rid is not None else "ok (empty table; error paths only)"
    if op == "create":
        before = count(db, table)
        r = fn(db, **required_kwargs(t))
        assert count(db, table) == before + 1, f"row count did not grow: {json.dumps(r)[:160]}"
        return "ok"
    if op == "update":
        rid = row1(db, table, idc)
        bogus = fn(db, **{**required_kwargs(t), t["id_param"]: "___smoke_bogus___"})
        assert is_not_found(ns, bogus), f"bogus id gave {json.dumps(bogus)[:160]}"
        if rid is None:
            return "ok (empty table; 404 path only)"
        kwargs = {**required_kwargs(t), t["id_param"]: rid}
        fmap = t.get("field_map", {})
        checked = None
        for p in t.get("set_fields", []):
            val = GENERIC.get(t["params"][p].get("type", "string"), "smoke_updated")
            val = "smoke_updated" if isinstance(val, str) else val
            kwargs[p] = val
            checked = (fmap.get(p, p), val)
            break
        fn(db, **kwargs)
        if checked and not isinstance(checked[1], (dict, list)):
            newval = query(db, f'SELECT "{checked[0]}" AS v FROM "{table}" WHERE "{idc}" = ?', (rid,))
            assert newval and newval[0]["v"] == checked[1], f"{checked[0]} not updated in DB"
        return "ok"
    if op == "delete":
        rid = row1(db, table, idc)
        if rid is None:
            return "ok (empty table)"
        fn(db, **{**required_kwargs(t), t["id_param"]: rid})
        left = query(db, f'SELECT 1 FROM "{table}" WHERE "{idc}" = ?', (rid,))
        assert not left, "row still present after delete"
        again = fn(db, **{**required_kwargs(t), t["id_param"]: rid})
        assert is_not_found(ns, again), f"second delete gave {json.dumps(again)[:160]}"
        return "ok"
    # custom: generic bind; dict or list return passes, raising fails
    r = fn(db, **required_kwargs(t))
    assert isinstance(r, (dict, list)), f"custom returned {type(r).__name__}"
    return "ok (custom)"


def main():
    world = json.load(open(os.path.join(PKG, "world.json")))
    sources = {t["name"]: t["source"] for t in world["tools"]}
    spec_files = sorted(f for f in os.listdir(SPECS_DIR)
                        if f.endswith(".json") and not f.startswith("_"))
    failures, total = [], 0
    for fname in spec_files:
        spec = json.load(open(os.path.join(SPECS_DIR, fname)))
        ns = spec["namespace"]
        print(f"\n== {spec['vendor']} ({len(spec['tools'])} tools)")
        for t in spec["tools"]:
            total += 1
            db = fresh_db()
            try:
                if t["name"] not in sources:
                    raise AssertionError("tool missing from world.json (generator not run?)")
                fn = load_fn(sources[t["name"]], t["name"])
                note = probe(t, ns, fn, db)
                print(f"  PASS  {t['name']:55} {note}")
            except Exception as e:
                failures.append((t["name"], str(e)))
                print(f"  FAIL  {t['name']:55} {str(e)[:140]}")
    print(f"\n{total - len(failures)}/{total} passed")
    if failures:
        print("failures:")
        for name, err in failures:
            print(f"  {name}: {err[:200]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
