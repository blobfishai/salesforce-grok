#!/usr/bin/env python3
"""Give the three column-less tables in the wave-6 world a real schema and rows.

    python3 scripts/repair-phantom-tables.py

Commit 5c14dc5 ("Put the approval policy in the world") registered `account_tiers`,
`deal_desk_approval_matrix` and `product_regulatory_flags` in world.json with an
empty `columns` list, no `sample_rows`, and shipped one reader tool for each
(`account_tiers_list`, `approval_matrix_list`, `product_regulatory_list`). The
consequences were live:

  * `create_db.py` died with `sqlite3.OperationalError: near ")"` — SQLite cannot
    create a table with no columns — so the world could not be rebuilt from
    world.json at all;
  * the three tables were absent from seed.db, so their three tools failed at
    runtime against any freshly built database;
  * the world's advertised table count included three tables that did not exist.

densify-vendor-tools.py cannot repair this: it skips tables whose name is already
registered and explicitly does not migrate schema. Hence this one-shot repair.

The content is not invented freely — it matches the approval policy the world
already enforces elsewhere (`cpq_discount_policy`, `finance_approval_thresholds`,
`deal_desk_charter`) and the discount/TCV matrix asserted by the shipped
deal-desk-quote-triage task: <=25% and <=$2M is deal-desk authority, above either
threshold is Finance, and an invalid configuration is a reject at any discount.

Idempotent: re-running on an already-repaired world.json changes nothing.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, "world", "blobfish-wave6", "package", "sbx_291042075d7547f4")
TOP_WORLD = os.path.join(ROOT, "world", "blobfish-wave6", "world.json")


def col(name, typ="TEXT", pk=False):
    d = {"name": name, "type": typ}
    if pk:
        d["pk"] = True
    return d


REPAIRS = {
    "account_tiers": {
        "description": "Account tier definitions: the ARR bands that drive support SLA, "
                       "CSM coverage and QBR cadence. Referenced by the account tiering standard.",
        "columns": [
            col("id", pk=True), col("tier_name"), col("min_arr", "REAL"), col("max_arr", "REAL"),
            col("support_sla_hours", "INTEGER"), col("named_csm", "INTEGER"),
            col("qbr_frequency"), col("renewal_notice_days", "INTEGER"),
        ],
        "sample_rows": [
            {"id": "tier_1", "tier_name": "Tier 1", "min_arr": 500000.0, "max_arr": None,
             "support_sla_hours": 1, "named_csm": 1, "qbr_frequency": "quarterly",
             "renewal_notice_days": 120},
            {"id": "tier_2", "tier_name": "Tier 2", "min_arr": 100000.0, "max_arr": 499999.99,
             "support_sla_hours": 4, "named_csm": 1, "qbr_frequency": "semi-annual",
             "renewal_notice_days": 90},
            {"id": "tier_3", "tier_name": "Tier 3", "min_arr": 25000.0, "max_arr": 99999.99,
             "support_sla_hours": 8, "named_csm": 0, "qbr_frequency": "annual",
             "renewal_notice_days": 60},
            {"id": "tier_4", "tier_name": "Tier 4", "min_arr": 0.0, "max_arr": 24999.99,
             "support_sla_hours": 24, "named_csm": 0, "qbr_frequency": "none",
             "renewal_notice_days": 30},
        ],
    },
    "deal_desk_approval_matrix": {
        "description": "Discount and TCV bands mapped to the approving authority. This is the "
                       "matrix the deal desk runs: deal-desk authority inside both thresholds, "
                       "Finance above either, and invalid configurations rejected outright.",
        "columns": [
            col("id", pk=True), col("min_discount_pct", "REAL"), col("max_discount_pct", "REAL"),
            col("max_tcv", "REAL"), col("approver_role"), col("sla_hours", "INTEGER"),
            col("requires_written_record", "INTEGER"), col("notes"),
        ],
        "sample_rows": [
            {"id": "apr_0001", "min_discount_pct": 0.0, "max_discount_pct": 25.0,
             "max_tcv": 2000000.0, "approver_role": "Deal Desk", "sla_hours": 24,
             "requires_written_record": 0,
             "notes": "Inside deal desk authority. Approve without escalation."},
            {"id": "apr_0002", "min_discount_pct": 25.01, "max_discount_pct": 40.0,
             "max_tcv": None, "approver_role": "Finance", "sla_hours": 48,
             "requires_written_record": 1,
             "notes": "Above the discount band. Finance approval must be recorded before approval."},
            {"id": "apr_0003", "min_discount_pct": 40.01, "max_discount_pct": 100.0,
             "max_tcv": None, "approver_role": "CFO", "sla_hours": 72,
             "requires_written_record": 1,
             "notes": "Exceptional discount. CFO sign-off required in writing."},
            {"id": "apr_0004", "min_discount_pct": 0.0, "max_discount_pct": 25.0,
             "max_tcv": None, "approver_role": "Finance", "sla_hours": 48,
             "requires_written_record": 1,
             "notes": "Discount inside band but list total above $2,000,000: Finance still approves."},
        ],
    },
    "product_regulatory_flags": {
        "description": "Per-product regulatory restrictions by jurisdiction. Products carrying a "
                       "restriction cannot be quoted into that jurisdiction without review.",
        "columns": [
            col("id", pk=True), col("product_code"), col("product_name"), col("jurisdiction"),
            col("restriction"), col("requires_review", "INTEGER"), col("review_owner"), col("notes"),
        ],
        "sample_rows": [
            {"id": "reg_0001", "product_code": "MDF-L2", "product_name": "Market Data Feed L2",
             "jurisdiction": "EU", "restriction": "redistribution_prohibited", "requires_review": 1,
             "review_owner": "Compliance",
             "notes": "Exchange licence forbids onward redistribution without a venue agreement."},
            {"id": "reg_0002", "product_code": "MDF-L2", "product_name": "Market Data Feed L2",
             "jurisdiction": "US", "restriction": "none", "requires_review": 0,
             "review_owner": None, "notes": "No restriction."},
            {"id": "reg_0003", "product_code": "ATL-PLAT", "product_name": "Atlas Platform",
             "jurisdiction": "APAC", "restriction": "data_residency", "requires_review": 1,
             "review_owner": "Legal",
             "notes": "Customer data must remain in-region; requires the APAC hosting addendum."},
            {"id": "reg_0004", "product_code": "RSK-ANALYTICS", "product_name": "Risk Analytics Suite",
             "jurisdiction": "EU", "restriction": "model_disclosure", "requires_review": 1,
             "review_owner": "Compliance",
             "notes": "EU AI Act transparency obligations apply to the scoring models."},
            {"id": "reg_0005", "product_code": "ATL-PLAT", "product_name": "Atlas Platform",
             "jurisdiction": "US", "restriction": "none", "requires_review": 0,
             "review_owner": None, "notes": "No restriction."},
            {"id": "reg_0006", "product_code": "PRM-SUPPORT", "product_name": "Premium Support",
             "jurisdiction": "EU", "restriction": "none", "requires_review": 0,
             "review_owner": None, "notes": "No restriction."},
        ],
    },
}


def repair(path):
    raw = open(path).read()
    world = json.loads(raw)
    changed = []
    for table in world.get("tables", []):
        fix = REPAIRS.get(table["name"])
        if not fix or table.get("columns"):
            continue  # not ours, or already repaired
        table["columns"] = fix["columns"]
        table["sample_rows"] = fix["sample_rows"]
        table["row_count"] = len(fix["sample_rows"])
        table["description"] = fix["description"]
        changed.append(table["name"])
    if not changed:
        return []
    # Preserve the file's existing serialization style (this world.json ships minified).
    minified = "\n" not in raw.strip()
    text = json.dumps(world, ensure_ascii=False) if minified else json.dumps(world, indent=1, ensure_ascii=False)
    if raw.endswith("\n"):
        text += "\n"
    open(path, "w").write(text)
    return changed


def main():
    total = 0
    for path in (os.path.join(PKG, "world.json"), TOP_WORLD):
        if not os.path.exists(path):
            continue
        changed = repair(path)
        rel = os.path.relpath(path, ROOT)
        print(f"{rel}: repaired {len(changed)} tables" + (f" ({', '.join(changed)})" if changed else " (already clean)"))
        total += len(changed)
    if total == 0:
        print("nothing to repair")
    return 0


if __name__ == "__main__":
    sys.exit(main())
