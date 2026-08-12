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


# The schemas are NOT invented. `harbor/sales-world/scripts/author-tasks.py` already
# consumes all three tables and states their exact contract:
#
#   tiers = {r["account_name"]: r for r in rows(conn, "SELECT * FROM account_tiers")}
#   t["discount_authority_pct"] ... t["is_new_client"]
#   "SELECT product_code, is_regulated FROM product_regulatory_flags"
#   "SELECT rule_id, condition, threshold_usd, approver_role, sequence_order
#    FROM deal_desk_approval_matrix"
#
# An earlier version of this file guessed plausible-looking schemas instead (tier
# definitions keyed by ARR band, a discount/TCV matrix) and every one of them was
# the wrong shape, which surfaced immediately as `KeyError: 'account_name'`. The
# lesson is cheap and worth writing down: when a table already has a consumer, the
# consumer is the specification.
#
# Row coverage matters as much as shape. `tiers[q["account_name"]]` is an unguarded
# lookup over every account that appears on a quote, so a missing account is a crash,
# not a soft miss. All seven are present below.
REPAIRS = {
    "account_tiers": {
        "description": "Per-account tier assignment with the discount authority that tier carries "
                       "and whether the account is still inside its new-client window. The deal-desk "
                       "routing task reads its rule from here rather than from the prompt.",
        "columns": [
            col("account_id", pk=True), col("account_name"), col("tier"),
            col("discount_authority_pct", "REAL"), col("is_new_client", "INTEGER"),
            col("named_csm", "INTEGER"), col("qbr_frequency"),
        ],
        "sample_rows": [
            {"account_id": "account_001", "account_name": "Summit Group", "tier": "Tier 1",
             "discount_authority_pct": 25.0, "is_new_client": 0, "named_csm": 1,
             "qbr_frequency": "quarterly"},
            {"account_id": "account_002", "account_name": "Riverside Group", "tier": "Tier 1",
             "discount_authority_pct": 25.0, "is_new_client": 0, "named_csm": 1,
             "qbr_frequency": "quarterly"},
            {"account_id": "account_003", "account_name": "Meridian Capital", "tier": "Tier 2",
             "discount_authority_pct": 15.0, "is_new_client": 0, "named_csm": 1,
             "qbr_frequency": "semi-annual"},
            {"account_id": "account_004", "account_name": "Ironwood Holdings", "tier": "Tier 2",
             "discount_authority_pct": 15.0, "is_new_client": 1, "named_csm": 1,
             "qbr_frequency": "semi-annual"},
            {"account_id": "account_005", "account_name": "Harborview Partners", "tier": "Tier 3",
             "discount_authority_pct": 10.0, "is_new_client": 0, "named_csm": 0,
             "qbr_frequency": "annual"},
            {"account_id": "account_006", "account_name": "Atlas Advisory", "tier": "Tier 3",
             "discount_authority_pct": 10.0, "is_new_client": 0, "named_csm": 0,
             "qbr_frequency": "annual"},
            {"account_id": "account_007", "account_name": "Crestline Trust", "tier": "Tier 2",
             "discount_authority_pct": 15.0, "is_new_client": 1, "named_csm": 1,
             "qbr_frequency": "semi-annual"},
        ],
    },
    "deal_desk_approval_matrix": {
        "description": "The standing approval matrix: which condition pulls in which approver, and "
                       "in what order. Sequence 0 is terminal (an invalid configuration is rejected "
                       "outright); Deal Desk completes its own step, anything beyond it must wait.",
        "columns": [
            col("rule_id", pk=True), col("condition"), col("threshold_usd", "REAL"),
            col("approver_role"), col("sequence_order", "INTEGER"), col("notes"),
        ],
        "sample_rows": [
            {"rule_id": "R0", "condition": "invalid_configuration", "threshold_usd": None,
             "approver_role": "Reject", "sequence_order": 0,
             "notes": "A quote that does not configure cannot be approved at any discount."},
            {"rule_id": "R1", "condition": "discount_above_tier_authority", "threshold_usd": None,
             "approver_role": "Deal Desk", "sequence_order": 1,
             "notes": "Discount exceeds the authority carried by the account's tier."},
            {"rule_id": "R2", "condition": "list_total_above_threshold", "threshold_usd": 5000000.0,
             "approver_role": "Deal Desk", "sequence_order": 1,
             "notes": "Large-value quotes enter deal desk regardless of discount."},
            {"rule_id": "R3", "condition": "new_client", "threshold_usd": None,
             "approver_role": "Compliance", "sequence_order": 2,
             "notes": "First paper with a new client requires onboarding review."},
            {"rule_id": "R4", "condition": "regulated_product", "threshold_usd": None,
             "approver_role": "Compliance", "sequence_order": 2,
             "notes": "Regulated SKUs require a licensing and disclosure check."},
            {"rule_id": "R5", "condition": "list_total_above_threshold", "threshold_usd": 25000000.0,
             "approver_role": "Finance", "sequence_order": 3,
             "notes": "Above this value Finance signs before the quote leaves."},
        ],
    },
    "product_regulatory_flags": {
        "description": "Per-SKU regulatory classification. A regulated product pulls Compliance into "
                       "the approval chain regardless of discount or value.",
        "columns": [
            col("product_code", pk=True), col("product_name"), col("is_regulated", "INTEGER"),
            col("regime"), col("review_owner"), col("notes"),
        ],
        # Exactly one SKU on an in-review quote is regulated, and that is deliberate.
        # With PROD-FEED and PROD-RISK both regulated, every valid quote escalated to
        # Compliance and the routing task became degenerate: no quote could ever reach
        # `approved`, so an agent that escalated everything scored full marks. As set
        # below the five in-review quotes resolve to four outcomes by three different
        # rules — approved (deal-desk authority only), in_review via regulated product,
        # in_review via new client, and rejected on invalid configuration.
        "sample_rows": [
            {"product_code": "PROD-FEED", "product_name": "Market Data Feed L2", "is_regulated": 1,
             "regime": "exchange_licensing", "review_owner": "Compliance",
             "notes": "Venue agreement governs redistribution; onward supply needs review."},
            {"product_code": "PROD-RISK", "product_name": "Risk Analytics Suite", "is_regulated": 0,
             "regime": None, "review_owner": None,
             "notes": "Internal analytics tooling; carries no licensing regime of its own."},
            {"product_code": "PROD-PLAT", "product_name": "Atlas Platform", "is_regulated": 0,
             "regime": None, "review_owner": None, "notes": "No restriction."},
            {"product_code": "PROD-SUPP", "product_name": "Premium Support", "is_regulated": 0,
             "regime": None, "review_owner": None, "notes": "No restriction."},
            {"product_code": "PROD-ONBD", "product_name": "Onboarding Services", "is_regulated": 0,
             "regime": None, "review_owner": None, "notes": "No restriction."},
        ],
    },
}


def repair(path):
    raw = open(path).read()
    world = json.loads(raw)
    changed = []
    for table in world.get("tables", []):
        fix = REPAIRS.get(table["name"])
        if not fix:
            continue
        want = [c["name"] for c in fix["columns"]]
        have = [c["name"] for c in table.get("columns", [])]
        if have == want and table.get("sample_rows") == fix["sample_rows"]:
            continue  # already repaired, shape AND data
        # Re-apply on either a shape or a data mismatch. Comparing column names alone
        # silently skipped a corrected regulatory flag, which left the routing task
        # degenerate while the script reported success.
        # Re-apply on a shape mismatch, not just on an empty column list: an earlier
        # run of this script filled these tables with guessed schemas, and "has some
        # columns" is not the same as "has the right ones".
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
