#!/usr/bin/env python3
"""Generate deeper CRM tasks whose ground truth is computed, not authored.

    python3 scripts/ingest/wave_generator.py --wave 1 --per-template 40

CRMArena's own 1,170 tasks are mostly one or two hops. This builds waves on top
of the same org, at increasing hop depth, by pairing a natural-language prompt
with the SQL that computes its answer. Ground truth is therefore *derived from
the world* — the only way to scale past hand-authoring without inventing facts
(the failure mode `docs/INGESTION-PROTOCOL.md` exists to prevent).

Depth is the number of objects that must be joined to answer:

  depth 2   Case x Issue__c            "most reported issue for product P"
  depth 3   Case x OrderItem x Product2 "agent who closed most cases for product P"
  depth 4   Case x OrderItem x Product2 x Account  "region with most cases for family F"
  depth 5   + CaseHistory__c            "most transferred issue among agent A's cases"

Every template also emits **abstention** variants against parameters the data
cannot answer, whose ground truth is the literal "None" — mirroring the 195
unanswerable instances CRMArena ships, and directly probing the refusal
behaviour that separated models in the sales-world suite.

Output is a WCP, so it flows through the same compiler and gates as everything
else.
"""
from __future__ import annotations

import argparse
import json
import random
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "external" / "CRMArena" / "local_data" / "crmarena_data.db"
OUT = ROOT / "research" / "parity" / "wcp"

# The org spans 2020-01 .. 2024-05, so windows are drawn across that whole range;
# narrow quarters mostly produce unanswerable parameterisations that get dropped.
PERIODS = [("2021", "2021-01-01", "2021-12-31"), ("2022", "2022-01-01", "2022-12-31"),
           ("2023", "2023-01-01", "2023-12-31"),
           ("the first half of 2023", "2023-01-01", "2023-06-30"),
           ("the second half of 2023", "2023-07-01", "2023-12-31"),
           ("2022 and 2023 combined", "2022-01-01", "2023-12-31"),
           ("the life of the org to date", "2020-01-01", "2024-05-26")]


def q(conn, sql, params=()):
    conn.row_factory = sqlite3.Row
    return [dict(r) for r in conn.execute(sql, params)]


def one(conn, sql, params=()):
    rows = q(conn, sql, params)
    return rows[0] if rows else None


# ---------------------------------------------------------------- templates
def t_top_issue_for_product(conn, rng, n):
    """depth 2 — Case x Issue__c, scoped to a product and a period."""
    out = []
    prods = q(conn, """SELECT p.Id, p.Name, COUNT(*) n FROM "Case" c
                       JOIN OrderItem oi ON oi.Id = c.OrderItemId__c
                       JOIN Product2 p ON p.Id = oi.Product2Id
                       GROUP BY p.Id HAVING n >= 8 ORDER BY n DESC LIMIT 60""")
    for p in rng.sample(prods, min(n, len(prods))):
        label, start, end = rng.choice(PERIODS)
        row = one(conn, """SELECT i.Name AS issue, COUNT(*) n FROM "Case" c
                           JOIN OrderItem oi ON oi.Id = c.OrderItemId__c
                           JOIN Issue__c i ON i.Id = c.IssueId__c
                           WHERE oi.Product2Id = ? AND substr(c.CreatedDate,1,10) BETWEEN ? AND ?
                           GROUP BY i.Id ORDER BY n DESC, i.Name ASC LIMIT 1""", (p["Id"], start, end))
        out.append({
            "prompt": f"What was the most frequently reported issue for the product "
                      f"\"{p['Name']}\" during {label}? Return only the issue name, or None "
                      f"if there were no cases for that product in that period.",
            "answer": row["issue"] if row else None, "depth": 2,
            "tags": ["wave", "depth2", "top_issue_scoped"],
        })
    return out


def t_agent_most_cases_for_product(conn, rng, n):
    """depth 3 — Case x OrderItem x Product2, resolved to a named agent."""
    out = []
    prods = q(conn, """SELECT p.Id, p.Name, COUNT(*) n FROM "Case" c
                       JOIN OrderItem oi ON oi.Id = c.OrderItemId__c
                       JOIN Product2 p ON p.Id = oi.Product2Id
                       WHERE c.Status = 'Closed' GROUP BY p.Id HAVING n >= 6 ORDER BY n DESC LIMIT 60""")
    for p in rng.sample(prods, min(n, len(prods))):
        row = one(conn, """SELECT u.Id AS agent_id, COUNT(*) n FROM "Case" c
                           JOIN OrderItem oi ON oi.Id = c.OrderItemId__c
                           JOIN User u ON u.Id = c.OwnerId
                           WHERE oi.Product2Id = ? AND c.Status = 'Closed'
                           GROUP BY u.Id ORDER BY n DESC, u.Id ASC LIMIT 1""", (p["Id"],))
        out.append({
            "prompt": f"Which agent has closed the most cases relating to the product "
                      f"\"{p['Name']}\"? Return only the agent's Id.",
            "answer": row["agent_id"] if row else None, "depth": 3,
            "tags": ["wave", "depth3", "agent_for_product"],
        })
    return out


def t_region_for_issue(conn, rng, n):
    """depth 4 — Case x Issue__c x Account, aggregating by shipping state."""
    out = []
    issues = q(conn, "SELECT Id, Name FROM Issue__c")
    for i in rng.sample(issues, min(n, len(issues))):
        label, start, end = rng.choice(PERIODS)
        row = one(conn, """SELECT a.ShippingState AS region, COUNT(*) n FROM "Case" c
                           JOIN Account a ON a.Id = c.AccountId
                           WHERE c.IssueId__c = ? AND substr(c.CreatedDate,1,10) BETWEEN ? AND ?
                             AND a.ShippingState IS NOT NULL AND a.ShippingState <> ''
                           GROUP BY a.ShippingState ORDER BY n DESC, a.ShippingState ASC LIMIT 1""",
                  (i["Id"], start, end))
        out.append({
            "prompt": f"Which shipping state reported the most \"{i['Name']}\" cases during "
                      f"{label}? Return only the state code, or None if there were none.",
            "answer": row["region"] if row else None, "depth": 4,
            "tags": ["wave", "depth4", "region_for_issue"],
        })
    return out


def t_slowest_issue_for_region(conn, rng, n):
    """depth 4 — closure-time arithmetic across Case x Account x Issue__c."""
    out = []
    regions = q(conn, """SELECT ShippingState AS r, COUNT(*) n FROM Account
                         WHERE ShippingState IS NOT NULL AND ShippingState <> ''
                         GROUP BY ShippingState HAVING n >= 3 ORDER BY n DESC LIMIT 40""")
    for reg in rng.sample(regions, min(n, len(regions))):
        row = one(conn, """SELECT i.Name AS issue,
                                  AVG(julianday(substr(c.ClosedDate,1,10)) -
                                      julianday(substr(c.CreatedDate,1,10))) AS days
                           FROM "Case" c JOIN Account a ON a.Id = c.AccountId
                           JOIN Issue__c i ON i.Id = c.IssueId__c
                           WHERE a.ShippingState = ? AND c.ClosedDate IS NOT NULL AND c.ClosedDate <> ''
                           GROUP BY i.Id HAVING COUNT(*) >= 2
                           ORDER BY days DESC, i.Name ASC LIMIT 1""", (reg["r"],))
        out.append({
            "prompt": f"For customers shipping to {reg['r']}, which issue type took the longest on "
                      f"average to close? Consider only issue types with at least two closed cases "
                      f"there. Return only the issue name, or None if none qualify.",
            "answer": row["issue"] if row else None, "depth": 4,
            "tags": ["wave", "depth4", "slowest_issue_by_region"],
        })
    return out


def t_most_transferred_issue(conn, rng, n):
    """depth 5 — Case x CaseHistory__c x Issue__c: transfers are ownership changes."""
    out = []
    periods = PERIODS[:]
    rng.shuffle(periods)
    for label, start, end in (periods * ((n // max(1, len(periods))) + 1))[:n]:
        # A transfer is a *second or later* owner assignment: the first one is
        # just initial routing. The history field is 'Owner Assignment'.
        row = one(conn, """WITH transferred AS (
                             SELECT h.CaseId__c AS cid, COUNT(*) AS assigns
                             FROM CaseHistory__c h
                             WHERE h.Field__c = 'Owner Assignment'
                               AND substr(h.CreatedDate,1,10) BETWEEN ? AND ?
                             GROUP BY h.CaseId__c HAVING assigns > 1)
                           SELECT i.Name AS issue, COUNT(*) n
                           FROM transferred t JOIN "Case" c ON c.Id = t.cid
                           JOIN Issue__c i ON i.Id = c.IssueId__c
                           GROUP BY i.Id ORDER BY n DESC, i.Name ASC LIMIT 1""", (start, end))
        out.append({
            "prompt": f"During {label}, which issue type was transferred between agents most often? "
                      f"A transfer is a change of case owner. Return only the issue name, or None "
                      f"if there were no transfers in that period.",
            "answer": row["issue"] if row else None, "depth": 5,
            "tags": ["wave", "depth5", "most_transferred_issue"],
        })
    return out


def t_abstention(conn, rng, n):
    """Unanswerable by construction: the parameter has no data behind it."""
    out = []
    prods = q(conn, "SELECT Id, Name FROM Product2 ORDER BY Name LIMIT 400")
    empty = []
    for p in prods:
        row = one(conn, """SELECT COUNT(*) n FROM "Case" c
                           JOIN OrderItem oi ON oi.Id = c.OrderItemId__c
                           WHERE oi.Product2Id = ?""", (p["Id"],))
        if row and row["n"] == 0:
            empty.append(p)
        if len(empty) >= n * 2:
            break
    for p in rng.sample(empty, min(n, len(empty))):
        out.append({
            "prompt": f"What was the most frequently reported issue for the product "
                      f"\"{p['Name']}\"? Return only the issue name, or None if the question "
                      f"cannot be answered from the data.",
            "answer": None, "depth": 2,
            "tags": ["wave", "abstention", "unanswerable_product"],
        })
    return out


TEMPLATES = [t_top_issue_for_product, t_agent_most_cases_for_product, t_region_for_issue,
             t_slowest_issue_for_region, t_most_transferred_issue, t_abstention]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", type=int, default=1)
    ap.add_argument("--per-template", type=int, default=40)
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()

    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    rng = random.Random(args.seed + args.wave)
    pkg = {
        "source": {"repo": "SalesforceAIResearch/CRMArena", "path": "external/CRMArena",
                   "url": "https://github.com/SalesforceAIResearch/CRMArena",
                   "license": "Apache-2.0", "derivation": f"wave {args.wave} generator"},
        "adapter": {"name": "wave_generator", "version": "1.0"},
        "fidelity": "adapted",
        "tables": [], "tools": [], "policies": [], "tasks": [], "refusals": [],
    }

    counts, dropped = {}, 0
    for tpl in TEMPLATES:
        made = tpl(conn, rng, args.per_template)
        kept = 0
        for i, t in enumerate(made):
            # An answer the SQL could not resolve is only legitimate for the
            # abstention template; elsewhere it means the parameters were bad.
            if t["answer"] is None and "abstention" not in t["tags"]:
                dropped += 1
                continue
            kept += 1
            pkg["tasks"].append({
                "id": f"wave{args.wave}_{tpl.__name__[2:]}_{i:03d}",
                "prompt": t["prompt"],
                "context": {"required": f"- Answer from the CRM data only.\n"
                                        f"- This question requires joining {t['depth']} objects."},
                "tags": t["tags"] + [f"wave{args.wave}"],
                "fidelity": "adapted",
                "verifier": {"kind": "answer_match", "expected": t["answer"], "metric": "exact"},
            })
        counts[tpl.__name__[2:]] = kept
    if dropped:
        pkg["refusals"].append({
            "kind": "tasks", "what": "parameterisations with no resolvable answer",
            "why": "the SQL returned no row and the template was not an abstention template, so the "
                   "generated question would have had no defensible ground truth", "count": dropped})

    conn.close()
    path = OUT / f"wave{args.wave}.CRMArena.json"
    path.write_text(json.dumps(pkg, indent=1, default=str))
    n_abstain = sum(1 for t in pkg["tasks"] if t["verifier"]["expected"] is None)
    print(f"wave {args.wave}: {len(pkg['tasks'])} tasks -> {path.relative_to(ROOT)}")
    for k, v in counts.items():
        print(f"  {k:<32} {v}")
    print(f"  abstention tasks: {n_abstain} | dropped (no ground truth): {dropped}")
    by_depth: dict[int, int] = {}
    for t in pkg["tasks"]:
        d = int(next(x for x in t["tags"] if x.startswith("depth"))[5:]) if any(
            x.startswith("depth") for x in t["tags"]) else 2
        by_depth[d] = by_depth.get(d, 0) + 1
    print(f"  by join depth: {dict(sorted(by_depth.items()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
