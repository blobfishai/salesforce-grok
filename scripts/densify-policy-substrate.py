#!/usr/bin/env python3
"""Put the approval policy *in the world* instead of in the task prompt.

    python3 scripts/densify-policy-substrate.py [--dry-run]

Every task in the first suite was solved 2/2 by claude-sonnet-4.5 (16/16 trials,
mean reward 1.000). The single largest reason: the prompt handed the model the
decision rule as a table. That measures rule execution, which frontier models are
good at, not rule *retrieval and application*, which is the actual job — and
which wave 4/5 of this program already showed is where the difficulty lives.

This seeds the real policy from `docs/anchors/wave2/05-cpq-discount-policy.md`
as queryable data:

  account_tiers              per-account tier, discount authority, new-client flag
  deal_desk_approval_matrix  the rules: condition -> approver -> sequence
  product_regulatory_flags   which products drag Compliance into the deal

and adds read tools so an agent can find them. New tables rather than edits to
the existing degenerate policy tables (`cpq_discount_policy` currently holds
name/status/created_at rows and nothing else), because the generated tools
hardcode their readable columns.

Idempotent. Writes seed.db and world.json; back up before first run.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "world/blobfish-wave6/package/sbx_291042075d7547f4"

# Grounded in docs/anchors/wave2/05-cpq-discount-policy.md:
#   "Platinum up to 15%, Gold 10%, Silver 5% without escalation. Any discount above
#    authority, or quote TCV > $5,000,000, requires Deal Desk approval. New-client or
#    regulated-product quotes add Compliance review. TCV > $25,000,000 adds Finance
#    sign-off. Approvals execute strictly in the order Deal Desk -> Compliance ->
#    Finance; any rejection halts the quote."
TIERS = [
    # account_id, account_name, tier, discount_authority_pct, is_new_client
    ("account_001", "Summit Group", "Platinum", 15.0, 0),
    ("account_002", "Riverside Group", "Gold", 10.0, 0),
    ("account_003", "Meridian Capital", "Platinum", 15.0, 1),   # new logo this year
    ("account_004", "Ironwood Holdings", "Silver", 5.0, 0),
    ("account_005", "Harborview Partners", "Gold", 10.0, 0),
    ("account_006", "Atlas Advisory", "Silver", 5.0, 1),
    ("account_007", "Crestline Trust", "Gold", 10.0, 0),
]

MATRIX = [
    # rule_id, condition, threshold, approver_role, sequence_order, halts_on_reject, note
    ("DD-01", "discount_above_account_tier_authority", None, "Deal Desk", 1, 1,
     "Any discount above the account tier's standing authority requires Deal Desk approval."),
    ("DD-02", "quote_tcv_above_usd", 5000000.0, "Deal Desk", 1, 1,
     "Quote TCV above $5,000,000 requires Deal Desk approval regardless of discount."),
    ("CO-01", "account_is_new_client", None, "Compliance", 2, 1,
     "New-client quotes add Compliance review. Deal Desk approval alone is not sufficient."),
    ("CO-02", "quote_contains_regulated_product", None, "Compliance", 2, 1,
     "Quotes containing a regulated product add Compliance review."),
    ("FI-01", "quote_tcv_above_usd", 25000000.0, "Finance", 3, 1,
     "Quote TCV above $25,000,000 adds Finance sign-off."),
    ("CFG-01", "quote_configuration_invalid", None, "None", 0, 1,
     "A quote whose configuration is invalid is rejected outright and is not routed to any approver."),
]

REGULATED = [
    ("PROD-PLAT", "Wealth Platform License", 0, ""),
    ("PROD-FEED", "Market Data Feed", 1, "Redistribution of licensed market data is exchange-regulated."),
    ("PROD-RISK", "Risk Analytics Module", 1, "Model outputs are used in regulatory capital reporting."),
    ("PROD-ONBD", "Onboarding Services", 0, ""),
    ("PROD-SUPP", "Premier Support", 0, ""),
]

DDL = {
    "account_tiers": """CREATE TABLE IF NOT EXISTS account_tiers (
        id TEXT PRIMARY KEY, account_id TEXT, account_name TEXT, tier TEXT,
        discount_authority_pct REAL, is_new_client INTEGER, effective_from TEXT)""",
    "deal_desk_approval_matrix": """CREATE TABLE IF NOT EXISTS deal_desk_approval_matrix (
        id TEXT PRIMARY KEY, rule_id TEXT, condition TEXT, threshold_usd REAL,
        approver_role TEXT, sequence_order INTEGER, halts_on_reject INTEGER, note TEXT)""",
    "product_regulatory_flags": """CREATE TABLE IF NOT EXISTS product_regulatory_flags (
        id TEXT PRIMARY KEY, product_code TEXT, product_name TEXT,
        is_regulated INTEGER, rationale TEXT)""",
}

LIST_SRC = '''def {fn}(db_path='state.db', **kwargs):
    """{doc}"""
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        _sql = 'SELECT * FROM "{table}"'
        _args = []
        _where = []
        for _k in {filters!r}:
            if kwargs.get(_k) is not None:
                _where.append('"' + _k + '" = ?')
                _args.append(kwargs[_k])
        if _where:
            _sql += ' WHERE ' + ' AND '.join(_where)
        _limit = int(kwargs.get('limit') or 50)
        _sql += ' LIMIT ' + str(max(1, min(200, _limit)))
        return [dict(r) for r in cur.execute(_sql, _args)]
    finally:
        conn.close()
'''


def list_tool(name, table, doc, filters, props):
    return {
        "name": name, "mcp_name": f"salesforce.{name}", "asset_namespace": "salesforce",
        "description": doc, "type": "read", "target_tables": [table],
        "parameters": {k: v["type"] for k, v in props.items()},
        "input_schema": {"type": "object", "properties": props, "additionalProperties": False},
        "source": LIST_SRC.format(fn=name, doc=doc, table=table, filters=filters),
    }


def new_tools():
    lim = {"type": "integer", "description": "Maximum number of records to return (default 50)."}
    return [
        list_tool("account_tiers_list", "account_tiers",
                  "List account tiers with the standing discount authority and new-client flag for each account.",
                  ["account_id", "account_name", "tier"],
                  {"account_id": {"type": "string", "description": "Filter to one account id."},
                   "account_name": {"type": "string", "description": "Filter to one account name."},
                   "tier": {"type": "string", "description": "Filter to a tier: Platinum, Gold or Silver."},
                   "limit": lim}),
        list_tool("approval_matrix_list", "deal_desk_approval_matrix",
                  "List the standing quote approval matrix: which condition routes to which approver, in what order.",
                  ["rule_id", "approver_role"],
                  {"rule_id": {"type": "string", "description": "Filter to one rule id."},
                   "approver_role": {"type": "string", "description": "Filter to one approver role."},
                   "limit": lim}),
        list_tool("product_regulatory_list", "product_regulatory_flags",
                  "List products with their regulatory classification, used to decide whether Compliance review applies.",
                  ["product_code", "is_regulated"],
                  {"product_code": {"type": "string", "description": "Filter to one product code."},
                   "is_regulated": {"type": "integer", "description": "Filter to regulated (1) or unregulated (0)."},
                   "limit": lim}),
    ]


def seed(conn, dry: bool) -> int:
    cur = conn.cursor()
    for ddl in DDL.values():
        cur.execute(ddl)
    written = 0
    if cur.execute("SELECT COUNT(*) FROM account_tiers").fetchone()[0] == 0:
        cur.executemany("INSERT INTO account_tiers VALUES (?,?,?,?,?,?,?)",
                        [(f"tier_{i:04d}", a, n, t, d, nc, "2026-01-01")
                         for i, (a, n, t, d, nc) in enumerate(TIERS, 1)])
        written += len(TIERS)
    if cur.execute("SELECT COUNT(*) FROM deal_desk_approval_matrix").fetchone()[0] == 0:
        cur.executemany("INSERT INTO deal_desk_approval_matrix VALUES (?,?,?,?,?,?,?,?)",
                        [(f"rule_{i:04d}", r, c, th, ap, so, hr, nt)
                         for i, (r, c, th, ap, so, hr, nt) in enumerate(MATRIX, 1)])
        written += len(MATRIX)
    if cur.execute("SELECT COUNT(*) FROM product_regulatory_flags").fetchone()[0] == 0:
        cur.executemany("INSERT INTO product_regulatory_flags VALUES (?,?,?,?,?)",
                        [(f"reg_{i:04d}", pc, pn, rg, ra)
                         for i, (pc, pn, rg, ra) in enumerate(REGULATED, 1)])
        written += len(REGULATED)
    if dry:
        conn.rollback()
    else:
        conn.commit()
    return written


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    seed_db = PKG / "seed.db"
    world_path = PKG / "world.json"

    if not args.dry_run:
        for p in (seed_db, world_path):
            bak = p.with_suffix(p.suffix + ".prepolicy.bak")
            if not bak.exists():
                shutil.copy2(p, bak)

    conn = sqlite3.connect(seed_db)
    rows_written = seed(conn, args.dry_run)
    counts = {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in DDL}
    conn.close()

    world = json.loads(world_path.read_text())
    have = {t.get("mcp_name") or t["name"] for t in world["tools"]}
    added = [t for t in new_tools() if t["mcp_name"] not in have]

    # Register the new tables so /tables and the world summary see them.
    known = {t.get("name") for t in world.get("tables", [])}
    new_tables = [{"name": t, "columns": [], "row_count": counts[t]} for t in DDL if t not in known]

    print(f"tables: {', '.join(f'{t}={c}' for t, c in counts.items())}  ({rows_written} rows written)")
    for t in added:
        print(f"  + {t['mcp_name']:<38} read -> {t['target_tables'][0]}")

    if args.dry_run:
        print(f"\ndry run: {len(added)} tools, {len(new_tables)} table registrations")
        return 0

    world["tools"].extend(added)
    world.setdefault("tables", []).extend(new_tables)
    world_path.write_text(json.dumps(world))
    print(f"\nworld now has {len(world['tools'])} tools and {len(world['tables'])} tables")
    # state.db is rebuilt from seed.db by the image, but refresh the local copy too.
    shutil.copy2(seed_db, PKG / "state.db")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
