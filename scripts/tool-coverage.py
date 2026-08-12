#!/usr/bin/env python3
"""Measure how much of the real sales tool surface the world actually implements.

    python3 scripts/tool-coverage.py [--world <world.json>] [--out docs/TOOL-COVERAGE.md]

The claim "this world encompasses the sales tool surface" has to be checkable.
This compares the verbs extracted from every cloned vendor MCP server
(research/tools/_extracted/) against the world's own tool list, matching on a
normalized action+object form so `create_deal` / `deals_create` / `post_deals`
count as the same verb. It reports coverage per vendor and, more usefully, the
uncovered verbs ranked by how many independent implementations ship them — a
verb five different servers implement is one real sellers actually use.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTRACTED = ROOT / "research" / "tools" / "_extracted"

# HTTP-verb and framework prefixes carry no domain meaning.
NOISE = re.compile(r"^(get|post|put|patch|delete|list|fetch|read|retrieve|search|find|query|create|update|"
                   r"add|remove|del|new|do|run|exec|call|handle|api|v\d+|crm|sf|hs|pd|mcp|tool)_?", re.I)
SPLIT = re.compile(r"[_\-.]+|(?<=[a-z0-9])(?=[A-Z])")

# Map many spellings of the same action onto one.
ACTIONS = {
    "create": "create", "new": "create", "post": "create", "add": "create", "insert": "create", "upsert": "create",
    "update": "update", "patch": "update", "edit": "update", "modify": "update", "set": "update",
    "delete": "delete", "remove": "delete", "archive": "delete", "del": "delete", "destroy": "delete",
    "get": "read", "read": "read", "fetch": "read", "retrieve": "read", "show": "read", "info": "read",
    "list": "list", "all": "list", "index": "list",
    "search": "search", "query": "search", "find": "search", "filter": "search",
    "merge": "merge", "convert": "convert", "send": "send", "enroll": "enroll", "approve": "approve",
}
# Object synonyms across CRMs: HubSpot "deal" == Salesforce "opportunity" == Pipedrive "deal".
OBJECTS = {
    "deal": "opportunity", "deals": "opportunity", "opportunity": "opportunity", "opportunities": "opportunity",
    "company": "account", "companies": "account", "organization": "account", "organizations": "account",
    "org": "account", "account": "account", "accounts": "account",
    "person": "contact", "persons": "contact", "people": "contact", "contact": "contact", "contacts": "contact",
    "lead": "lead", "leads": "lead", "prospect": "lead", "prospects": "lead",
    "quote": "quote", "quotes": "quote", "estimate": "quote",
    "invoice": "invoice", "invoices": "invoice", "bill": "invoice",
    "ticket": "case", "tickets": "case", "case": "case", "cases": "case", "issue": "case", "issues": "case",
    "task": "task", "tasks": "task", "activity": "activity", "activities": "activity",
    "note": "note", "notes": "note", "email": "email", "emails": "email", "mail": "email",
    "sequence": "sequence", "sequences": "sequence", "cadence": "sequence", "campaign": "campaign",
    "meeting": "meeting", "meetings": "meeting", "event": "event", "events": "event", "call": "call", "calls": "call",
    "pipeline": "pipeline", "stage": "stage", "stages": "stage", "product": "product", "products": "product",
    "user": "user", "users": "user", "owner": "user", "field": "field", "fields": "field",
    "property": "field", "properties": "field", "attribute": "field", "attributes": "field",
    "list": "list_object", "lists": "list_object", "segment": "list_object", "segments": "list_object",
    "subscription": "subscription", "subscriptions": "subscription", "payment": "payment", "payments": "payment",
    "order": "order", "orders": "order", "customer": "customer", "customers": "customer",
    "message": "message", "messages": "message", "channel": "channel", "channels": "channel",
    "document": "document", "documents": "document", "file": "file", "files": "file",
    "envelope": "envelope", "signature": "envelope", "forecast": "forecast", "quota": "quota",
}


def canon(name: str) -> str | None:
    """Reduce a tool name to `action:object`, or None if it carries no domain signal."""
    parts = [p.lower() for p in SPLIT.split(name) if p]
    if not parts:
        return None
    action = next((ACTIONS[p] for p in parts if p in ACTIONS), None)
    obj = next((OBJECTS[p] for p in parts if p in OBJECTS), None)
    if not obj:
        return None
    return f"{action or 'read'}:{obj}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", default=str(ROOT / "world/blobfish-wave6/package/sbx_291042075d7547f4/world.json"))
    ap.add_argument("--out", default=str(ROOT / "docs" / "TOOL-COVERAGE.md"))
    args = ap.parse_args()

    world = json.loads(Path(args.world).read_text())
    world_names = [(t.get("mcp_name") or t["name"]) for t in world["tools"]]
    world_canon = {c for n in world_names if (c := canon(n.split(".", 1)[-1]))}

    # Which real servers implement each canonical verb.
    verb_sources: dict[str, set[str]] = defaultdict(set)
    per_repo: dict[str, tuple[int, int]] = {}
    for f in sorted(EXTRACTED.glob("*.txt")):
        names = [n.strip() for n in f.read_text().splitlines() if n.strip()]
        canons = {c for n in names if (c := canon(n))}
        if not canons:
            continue
        for c in canons:
            verb_sources[c].add(f.stem)
        covered = len(canons & world_canon)
        per_repo[f.stem] = (covered, len(canons))

    all_canon = set(verb_sources)
    covered = all_canon & world_canon
    missing = all_canon - world_canon

    out = [
        "# Tool coverage — the world vs the real sales tool surface",
        "",
        "Generated by `scripts/tool-coverage.py`. Compares every verb extracted from the",
        "cloned vendor MCP servers (`research/tools/_extracted/`) against the world's own",
        "tool list, matched on a normalized `action:object` form so `create_deal`,",
        "`deals_create` and `post_deals` count once — and so HubSpot's *deal* and",
        "Salesforce's *opportunity* are recognized as the same object.",
        "",
        f"- world tools: **{len(world_names)}** across {len({n.split('.')[0] for n in world_names})} namespaces",
        f"- distinct domain verbs in the corpus: **{len(all_canon)}**",
        f"- covered by the world: **{len(covered)}** ({100 * len(covered) / max(1, len(all_canon)):.0f}%)",
        f"- not yet covered: **{len(missing)}**",
        "",
        "## Coverage per vendor server",
        "",
        "| server | verbs | covered | % |",
        "|---|---:|---:|---:|",
    ]
    for repo, (cov, tot) in sorted(per_repo.items(), key=lambda kv: -kv[1][1]):
        out.append(f"| `{repo}` | {tot} | {cov} | {100 * cov / max(1, tot):.0f}% |")

    out += [
        "",
        "## Uncovered verbs, ranked by independent implementations",
        "",
        "A verb several unrelated servers all ship is one sellers actually use; a verb one",
        "server ships is that vendor's idiosyncrasy. This ranking is the densification backlog.",
        "",
        "| verb | servers implementing it |",
        "|---|---:|",
    ]
    # Show the WHOLE backlog. This table is the densification worklist, so a
    # silent top-N would make the gap look smaller than it is.
    missing_ranked = Counter({v: len(s) for v, s in verb_sources.items() if v in missing})
    for verb, srcs in sorted(missing_ranked.most_common(), key=lambda kv: (-kv[1], kv[0])):
        out.append(f"| `{verb}` | {srcs} |")

    out += ["", "## Covered verbs", "", "```", *sorted(covered), "```", ""]

    Path(args.out).write_text("\n".join(out))
    print(f"world tools {len(world_names)} | corpus verbs {len(all_canon)} | "
          f"covered {len(covered)} ({100 * len(covered) / max(1, len(all_canon)):.0f}%) | missing {len(missing)}")
    print(f"wrote {Path(args.out).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
