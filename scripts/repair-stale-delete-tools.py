#!/usr/bin/env python3
"""Drop the five hand-written CRM delete tools so densify regenerates them correctly.

    python3 scripts/repair-stale-delete-tools.py && python3 scripts/densify-vendor-tools.py

`account_delete`, `contact_delete`, `lead_delete`, `opportunity_delete` and
`task_delete` predate the tool-spec pipeline. Bringing them under
`scripts/smoke-test-new-tools.py` for the first time exposed two defects:

1. WRONG ERROR ENVELOPE. Every other salesforce-namespace tool returns the real
   Salesforce REST error shape — a list, `[{"errorCode": "NOT_FOUND", ...}]` —
   which is what the world's own envelope contract and the smoke test's
   `is_not_found("salesforce", ...)` both expect. These five return the generic
   built-in `{"error": ..., "status": 404}` instead. An agent that branches on
   the documented Salesforce error shape cannot see their failures.

2. `opportunity_delete` OPERATED ON THE WRONG TABLE. Its siblings
   (`opportunities_list`, `opportunity_get`, `opportunity_create`) all read and
   write `opportunities` (10 rows). `opportunity_delete` alone deleted from
   `sales_opportunities` (501 rows) while declaring `opportunities` as its
   subject. `opportunity_get(id)` followed by `opportunity_delete(id)` therefore
   returned "not found" and left the row in place — a trap that manufactures
   benchmark failures that look like model errors but are world bugs.

Deleting the stale entries lets densify-vendor-tools.py generate them from
`tool-specs/crm-core-crud.json`, where they are ordinary `op: delete` entries and
so inherit the standard envelope and the correct table. Verified by the smoke
test: the eight spec-generated deletes in the same namespace already pass.

Idempotent: re-running after the repair finds nothing to remove.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, "world", "blobfish-wave6", "package", "sbx_291042075d7547f4")
TOP_WORLD = os.path.join(ROOT, "world", "blobfish-wave6", "world.json")

STALE = {"account_delete", "contact_delete", "lead_delete", "opportunity_delete", "task_delete"}


def is_stale(tool):
    """Only remove the hand-written originals, never a regenerated replacement.

    The spec-generated versions carry `spec_generated`; the hand-written ones do
    not. Falling back to the opportunity table mismatch keeps this correct even
    if that marker is absent.
    """
    if tool["name"] not in STALE:
        return False
    if tool.get("spec_generated"):
        return False
    src = tool.get("source") or ""
    return "'error':" in src or '"error":' in src or "sales_opportunities" in src


def repair(path):
    raw = open(path).read()
    world = json.loads(raw)
    before = len(world["tools"])
    removed = [t["name"] for t in world["tools"] if is_stale(t)]
    if not removed:
        return []
    world["tools"] = [t for t in world["tools"] if not is_stale(t)]
    assert len(world["tools"]) == before - len(removed)
    minified = "\n" not in raw.strip()
    text = json.dumps(world, ensure_ascii=False) if minified else json.dumps(world, indent=1, ensure_ascii=False)
    if raw.endswith("\n"):
        text += "\n"
    open(path, "w").write(text)
    return removed


def main():
    total = 0
    for path in (os.path.join(PKG, "world.json"), TOP_WORLD):
        if not os.path.exists(path):
            continue
        removed = repair(path)
        print(f"{os.path.relpath(path, ROOT)}: removed {len(removed)}"
              + (f" ({', '.join(sorted(removed))})" if removed else " (already clean)"))
        total += len(removed)
    if total:
        print("\nnow re-run: python3 scripts/densify-vendor-tools.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
