"""Regression tests for the SOQL shim.

The shim's whole value is that it never answers wrongly. These tests exist
because an earlier revision returned the literal string `COUNT(Id)` where a
count belonged — plausible-looking output that would have corrupted every
CRMArena parity measurement downstream.

    python3 harbor/crmarena-parity/tests/test_soql.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "harbor/crmarena-parity/images/world"))

from soql import run_soql, soql_to_sql, SoqlUnsupported, SoqlError  # noqa: E402

DB = str(ROOT / "external/CRMArena/local_data/crmarena_data.db")
failures: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"{'PASS' if cond else 'FAIL'}  {name}" + (f"  — {detail}" if not cond and detail else ""))
    if not cond:
        failures.append(name)


def refused(sql: str) -> bool:
    return "error" in run_soql(DB, sql)


# --- aggregates: the defect this file exists to catch -----------------------
r = run_soql(DB, "SELECT COUNT() FROM Case WHERE Status = 'Closed'")
check("COUNT() returns an integer", isinstance(r.get("records", [{}])[0].get("expr0"), int), str(r)[:120])

r = run_soql(DB, "SELECT OwnerId, COUNT(Id) FROM Case GROUP BY OwnerId ORDER BY OwnerId LIMIT 3")
rec = r.get("records", [{}])[0]
check("mixed field + COUNT(f) aliases to expr0", "expr0" in rec, str(rec)[:140])
check("mixed COUNT(f) value is an integer", isinstance(rec.get("expr0"), int), str(rec)[:140])
check("grouped counts are plausible", sum(x["expr0"] for x in r.get("records", [])) > 0, str(r)[:120])

r = run_soql(DB, "SELECT MAX(CreatedDate) FROM Case")
check("MAX(f) works", isinstance(r.get("records", [{}])[0].get("expr0"), str), str(r)[:120])

# --- refusals: never guess --------------------------------------------------
check("relationship fields refused", refused("SELECT Account.Name FROM Case LIMIT 1"))
check("subqueries refused", refused("SELECT Id FROM Case WHERE Id IN (SELECT Id FROM Case)"))
check("HAVING refused", refused("SELECT OwnerId, COUNT(Id) FROM Case GROUP BY OwnerId HAVING COUNT(Id) > 2"))
check("arbitrary expressions refused", refused("SELECT Id + 1 FROM Case LIMIT 1"))
check("unknown function refused", refused("SELECT WEIRD(Id) FROM Case LIMIT 1"))

# --- date handling ----------------------------------------------------------
# The mirror stores '2024-05-26T06:58:00.000+0000'; comparing that against a
# bare date must not drop same-day rows.
sql = soql_to_sql("SELECT Id FROM Case WHERE CreatedDate <= TODAY")
check("date comparison truncates the stored timestamp", "substr(" in sql, sql[:140])

total = run_soql(DB, "SELECT COUNT() FROM Case")["records"][0]["expr0"]
le_today = run_soql(DB, "SELECT COUNT() FROM Case WHERE CreatedDate <= TODAY")["records"][0]["expr0"]
check("all cases predate the pinned today", le_today == total, f"{le_today} vs {total}")

recent = run_soql(DB, "SELECT COUNT() FROM Case WHERE CreatedDate >= LAST_N_DAYS:30")["records"][0]["expr0"]
check("LAST_N_DAYS:30 is empty (data ends 2024-05-26)", recent == 0, str(recent))

# A boundary that would silently fail without truncation: the max CreatedDate
# day itself must be included by <=.
maxday = run_soql(DB, "SELECT MAX(CreatedDate) FROM Case")["records"][0]["expr0"][:10]
# Bare ISO literals are valid SOQL. Unquoted they would be arithmetic to SQLite
# (2024-05-26 -> 1993) and match nothing, so this asserts real translation.
n_on_day = run_soql(DB, f"SELECT COUNT() FROM Case WHERE CreatedDate <= {maxday}")
check("bare ISO date literal is translated, not evaluated as arithmetic",
      n_on_day.get("records", [{}])[0].get("expr0") == total, str(n_on_day)[:140])
n_after = run_soql(DB, f"SELECT COUNT() FROM Case WHERE CreatedDate > {maxday}")
check("bare ISO date literal excludes correctly on the other side",
      n_after.get("records", [{}])[0].get("expr0") == 0, str(n_after)[:140])
check("undecodable date-shaped token still refused",
      refused("SELECT Id FROM Case WHERE CreatedDate BETWEEN 2024-01-01 AND 2024-02-01"))

# --- ordinary reads ---------------------------------------------------------
r = run_soql(DB, "SELECT Id, Subject FROM Case LIMIT 3")
check("plain select returns rows", r.get("totalSize") == 3, str(r)[:120])
r = run_soql(DB, "SELECT Id, Name FROM Product2 WHERE Name LIKE '%Jersey%' LIMIT 5")
check("LIKE filter works", r.get("totalSize", 0) > 0 and "Jersey" in r["records"][0]["Name"], str(r)[:120])

print()
if failures:
    print(f"{len(failures)} FAILED: {', '.join(failures)}")
    raise SystemExit(1)
print("all SOQL shim checks passed")
