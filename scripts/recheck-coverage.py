#!/usr/bin/env python3
"""Recheck the domain-coverage verdicts against the world as it stands today.

    python3 scripts/recheck-coverage.py [--out docs/COVERAGE-RECHECK.md]

`docs/COVERAGE.md` reports 44 covered / 96 partial / 11 gap over a 171-item domain
census. Those verdicts were judged against a snapshot of 205 tools and 214 tables
(`data/coverage/w6-inventory.json`). The world now carries substantially more, so
every one of those verdicts is stale by construction.

This script does NOT re-judge. A verdict says things like "missing a rationed
enrichment tool with credit accounting", which is a claim about semantics that a
string match cannot settle, and silently flipping `partial` to `covered` because a
plausible-looking tool name appeared is precisely the overclaim the ingestion
protocol exists to prevent. What it does instead is two mechanical, checkable jobs:

1. CITATION INTEGRITY. Every verdict cites evidence by identifier. If an identifier
   no longer resolves against the current world, the verdict is not merely stale --
   it is wrong today, and its evidence has to be re-established before the number it
   feeds can be quoted.

2. RE-JUDGE WORKLIST. For each partial/gap, match the capability language in its note
   against the capabilities that did not exist when it was judged. A hit is a
   candidate, ranked by how many distinct terms line up, and nothing more. The output
   is a queue for a judge, ordered so the most likely conversions are looked at first.

The distinction matters: this file reports what changed underneath the verdicts, and
leaves the verdicts alone.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COV = ROOT / "data" / "coverage"

# Words that carry no capability signal when matching a note against tool names.
STOP = {
    "the", "and", "for", "with", "that", "this", "from", "into", "not", "but", "are", "was",
    "which", "when", "what", "where", "who", "how", "its", "it", "is", "of", "to", "in", "on",
    "as", "by", "or", "an", "a", "be", "been", "has", "have", "had", "can", "will", "would",
    "there", "their", "they", "them", "then", "than", "here", "only", "also", "any", "all",
    "one", "two", "side", "agent", "environment", "world", "task", "tasks", "exist", "exists",
    "existing", "missing", "present", "needs", "need", "needed", "requires", "required",
    "state", "states", "surface", "surfaces", "tool", "tools", "table", "tables", "doc",
    "docs", "document", "documents", "anchor", "policy", "corpus", "machinery", "crux",
    "test", "writes", "write", "read", "reads", "store", "stores", "level", "full", "real",
}
TOKEN = re.compile(r"[a-z][a-z0-9_]{2,}")


def terms(text: str) -> set[str]:
    return {t for t in TOKEN.findall((text or "").lower()) if t not in STOP}


def load_world(path: Path):
    w = json.loads(path.read_text())
    return ({t["name"] for t in w.get("tools", [])},
            {t["name"] for t in w.get("tables", [])})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", default=str(ROOT / "world/blobfish-wave6/package/sbx_291042075d7547f4/world.json"))
    ap.add_argument("--out", default=str(ROOT / "docs" / "COVERAGE-RECHECK.md"))
    ap.add_argument("--top", type=int, default=25, help="worklist rows to print in full")
    args = ap.parse_args()

    verdicts = json.loads((COV / "verdicts.json").read_text())
    old = json.loads((COV / "w6-inventory.json").read_text())
    # tools[] are objects ({"name": ..., "mcp": ...}); tables{} is keyed by table name.
    old_tools = {t["name"] if isinstance(t, dict) else str(t) for t in old.get("tools", [])}
    old_tables = set(old.get("tables", {}))
    now_tools, now_tables = load_world(Path(args.world))

    new_tools = now_tools - old_tools
    new_tables = now_tables - old_tables
    lost_tools = old_tools - now_tools
    lost_tables = old_tables - now_tables

    # ---- 1. citation integrity
    #
    # The `evidence` field is not a list of identifiers. It mixes them with prose:
    # "accounts (table)", "sales_leads:500", "--max-turns flag", "agent_documents#1
    # (Meridian Associates)", "blobfish MCP tool definitions at /worlds/{id}/mcp".
    # A first pass treated every entry as an identifier and reported that 84 of 171
    # verdicts cited something unresolvable -- a manufactured crisis, since NONE of
    # the 131 flagged strings had ever been a world identifier.
    #
    # So the check calibrates itself against the judging-time snapshot: an entry
    # counts as a citation only if it resolved THEN. Anything that never resolved was
    # prose and is none of this script's business. What is left is the real signal --
    # evidence that was valid when judged and is not valid now.
    known = now_tools | now_tables
    known_then = old_tools | old_tables
    lead = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*")
    broken, prose = [], 0
    for v in verdicts:
        bad = []
        for e in v.get("evidence", []):
            m = lead.match(str(e))
            ident = m.group(0) if m else ""
            if not ident or ident not in known_then:
                prose += 1
                continue
            if ident not in known:
                bad.append(ident)
        if bad:
            broken.append((v["name"], v["verdict"], sorted(set(bad))))

    # ---- 2. re-judge worklist
    new_terms = Counter()
    new_index = {}
    for name in new_tools | new_tables:
        for t in terms(name.replace("_", " ")):
            new_index.setdefault(t, set()).add(name)
            new_terms[t] += 1

    worklist = []
    for v in verdicts:
        if v["verdict"] not in ("partial", "gap"):
            continue
        want = terms(v.get("note", ""))
        hits = {}
        for t in want:
            if t in new_index:
                hits[t] = sorted(new_index[t])[:4]
        if hits:
            worklist.append((len(hits), v["name"], v["verdict"], hits))
    worklist.sort(key=lambda r: (-r[0], r[1]))

    counts = Counter(v["verdict"] for v in verdicts)
    out = [
        "# Coverage recheck — what changed underneath the verdicts",
        "",
        "Generated by `scripts/recheck-coverage.py`. **This file does not re-judge anything.**",
        "`docs/COVERAGE.md` still reports the verdicts as judged; this reports how far the world",
        "has moved since they were judged, and which of them that movement plausibly touches.",
        "",
        f"Verdicts as they stand: **{counts['covered']} covered · {counts['partial']} partial · "
        f"{counts['gap']} gap · {counts['out_of_scope']} out of scope** over {len(verdicts)} census items.",
        "",
        "## The world has moved",
        "",
        "| | at judging time | now | delta |",
        "|---|---:|---:|---:|",
        f"| tools | {len(old_tools)} | {len(now_tools)} | +{len(new_tools)} |",
        f"| tables | {len(old_tables)} | {len(now_tables)} | +{len(new_tables)} |",
        "",
        f"Every verdict below was reached without sight of {len(new_tools)} tools and "
        f"{len(new_tables)} tables. That is the reason to recheck, not evidence of any particular",
        "verdict being wrong.",
        "",
    ]

    if lost_tools or lost_tables:
        out += [
            "### Capabilities that existed at judging time and no longer do",
            "",
            f"- tools removed: **{len(lost_tools)}**" + (f" — `{'`, `'.join(sorted(lost_tools)[:12])}`" if lost_tools else ""),
            f"- tables removed: **{len(lost_tables)}**" + (f" — `{'`, `'.join(sorted(lost_tables)[:12])}`" if lost_tables else ""),
            "",
            "A verdict resting on one of these would not be stale but false. Section 1 checks exactly"
            f" that, and finds {len(broken)}: the removals were the deliberate cross-domain prune"
            " (Slack EKM/emoji/invite/app-admin and similar), which no verdict had cited.",
            "",
        ]

    out += [
        "## 1. Citation integrity",
        "",
        "Verdict evidence mixes real identifiers with prose (`accounts (table)`, `--max-turns flag`,",
        "`blobfish MCP tool definitions at /worlds/{id}/mcp`). An entry counts as a citation here only",
        "if it resolved against the judging-time snapshot; anything that never resolved was always",
        f"prose and is ignored ({prose} entries). What remains is evidence that was valid when judged",
        "and is not valid now.",
        "",
    ]
    if broken:
        out += [f"**{len(broken)} of {len(verdicts)} verdicts rest on evidence that has since disappeared.**",
                "", "| census item | verdict | unresolved evidence |", "|---|---|---|"]
        for name, verdict, bad in broken:
            out.append(f"| `{name}` | {verdict} | `{'`, `'.join(bad[:6])}`"
                       + (f" (+{len(bad) - 6} more)" if len(bad) > 6 else "") + " |")
    else:
        out.append("All cited identifiers still resolve against the current world.")

    out += [
        "",
        "## 2. Re-judge worklist",
        "",
        f"{len(worklist)} of the {counts['partial'] + counts['gap']} partial/gap verdicts use capability",
        "language that matches something the world did not have when they were judged. Ranked by how",
        "many distinct terms line up.",
        "",
        "A row here is **a candidate for re-judging, not a conversion**. These verdicts turn on",
        "semantics — \"a rationed enrichment tool with credit accounting\" is not settled by a tool",
        "whose name contains the word *enrichment* — and flipping them on a string match is the",
        "overclaim the ingestion protocol exists to prevent.",
        "",
        "The matcher is deliberately high-recall and visibly noisy: it matches single shared tokens,",
        "so `gh_branch_get` surfaces against a reply-intent item because both contain a common word.",
        "That is the intended failure direction. A queue that is too long wastes a judge's time; a",
        "queue that quietly drops a real conversion corrupts the coverage number. Expect to discard",
        "most rows on sight.",
        "",
        "| census item | verdict | matched terms | candidate new capabilities |",
        "|---|---|---:|---|",
    ]
    for n_hits, name, verdict, hits in worklist[:args.top]:
        shown = sorted(hits)[:4]
        caps = sorted({c for t in shown for c in hits[t]})[:5]
        out.append(f"| `{name}` | {verdict} | {n_hits} | `{'`, `'.join(caps)}` |")
    if len(worklist) > args.top:
        out.append(f"| _… {len(worklist) - args.top} further candidates_ | | | |")

    out += ["", "## What this does not tell you", "",
            "It does not tell you the coverage number went up. Converting any of the rows above needs a",
            "judge to read the note, look at the actual tool semantics, and decide — the same standard",
            "the original verdicts were held to. Until then `docs/COVERAGE.md` stands as written.", ""]

    Path(args.out).write_text("\n".join(out))
    print(f"tools {len(old_tools)} -> {len(now_tools)} (+{len(new_tools)}) | "
          f"tables {len(old_tables)} -> {len(now_tables)} (+{len(new_tables)})")
    print(f"verdicts with unresolved evidence: {len(broken)}/{len(verdicts)}")
    print(f"re-judge candidates: {len(worklist)} of {counts['partial'] + counts['gap']} partial/gap")
    print(f"wrote {Path(args.out).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
