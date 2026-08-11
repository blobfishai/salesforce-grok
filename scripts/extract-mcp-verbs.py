#!/usr/bin/env python3
"""Extract the tool/verb surface of every cloned MCP server.

Reads research/repos/mcp/* (and any MCP server found under workflow/), scans for
the handful of ways an MCP tool gets declared across TS/JS/Python SDKs, and emits:

  research/tools/_extracted/<owner__repo>.txt   one tool name per line
  research/tools/_extracted/INDEX.tsv           repo, vendor, tool count, path

The point is evidence: every verb we later mock should be traceable to a line in
a real server here, not invented.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOS = ROOT / "research" / "repos"
OUT = ROOT / "research" / "tools" / "_extracted"

SKIP_DIRS = {".git", "node_modules", "dist", "build", "__pycache__", ".venv", "venv", "coverage"}
EXTS = {".ts", ".js", ".mjs", ".py", ".json"}

# Declaration shapes, in rough order of specificity.
PATTERNS = [
    # server.tool("name" | registerTool("name" | addTool("name"
    re.compile(r'\b(?:registerTool|addTool|\.tool)\(\s*[\'"`]([a-zA-Z0-9_.\-]{3,64})[\'"`]'),
    # { name: "tool_name", description: ... }  — the classic ListTools entry
    re.compile(r'\bname:\s*[\'"`]([a-z][a-zA-Z0-9_.\-]{2,63})[\'"`]\s*,\s*\n?\s*(?:title|description|inputSchema)'),
    # export const X_TOOL = { name: "..." }  (handled by the above) and
    # case "tool_name":  in a CallTool switch
    re.compile(r'case\s+[\'"`]([a-z][a-z0-9_]{3,63})[\'"`]\s*:'),
    # Python: @mcp.tool() / @server.tool(...)  followed by def name(
    re.compile(r'@(?:mcp|server|app)\.tool\([^)]*\)\s*(?:async\s+)?def\s+([a-zA-Z0-9_]{3,64})'),
    # Python dict style: "name": "tool_name",
    re.compile(r'[\'"`]name[\'"`]\s*:\s*[\'"`]([a-z][a-zA-Z0-9_.\-]{2,63})[\'"`]'),
]

# Names that are obviously not tools.
DENY = re.compile(
    r'^(?:true|false|null|none|default|string|number|boolean|object|array|error|test|main|index|'
    r'src|dist|build|lib|utils?|types?|config|schema|server|client|tool|tools|mcp|api|data|value|'
    r'name|title|type|id|url|path|method|body|json|text|content|result|response|request|input|output|'
    r'node|npm|npx|python|typescript|javascript|eslint|prettier|vitest|jest|latest|module|commonjs)$'
)


def iter_files(root: Path):
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix not in EXTS:
            continue
        if p.stat().st_size > 4_000_000:
            continue
        yield p


def extract(repo_dir: Path) -> set[str]:
    names: set[str] = set()
    for f in iter_files(repo_dir):
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        # package.json / tsconfig noise: only mine JSON that smells like a tool spec
        if f.suffix == ".json" and '"inputSchema"' not in text and '"tools"' not in text:
            continue
        for pat in PATTERNS:
            for m in pat.finditer(text):
                n = m.group(1)
                if DENY.match(n.lower()):
                    continue
                if "/" in n or n.endswith((".ts", ".js", ".py", ".json")):
                    continue
                names.add(n)
    return names


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    roots = [REPOS / "mcp"]
    if not roots[0].exists():
        print("no cloned MCP repos found", file=sys.stderr)
        return 1
    for axis_dir in roots:
        for repo_dir in sorted(d for d in axis_dir.iterdir() if d.is_dir() or d.is_symlink()):
            names = sorted(extract(repo_dir))
            (OUT / f"{repo_dir.name}.txt").write_text("\n".join(names) + "\n", encoding="utf-8")
            vendor = repo_dir.name.split("__", 1)[1]
            rows.append((repo_dir.name, vendor, len(names), str(repo_dir.relative_to(ROOT))))
            print(f"{len(names):5d}  {repo_dir.name}")

    idx = OUT / "INDEX.tsv"
    with idx.open("w", encoding="utf-8") as fh:
        fh.write("repo\tvendor_hint\ttool_count\tpath\n")
        for r in sorted(rows, key=lambda x: -x[2]):
            fh.write("\t".join(map(str, r)) + "\n")
    print(f"\nwrote {idx.relative_to(ROOT)} ({len(rows)} repos, {sum(r[2] for r in rows)} verb candidates)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
