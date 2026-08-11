#!/usr/bin/env python3
"""Consume domain repos into World Contribution Packages (WCPs).

    python3 scripts/ingest/ingest.py                 # run every adapter
    python3 scripts/ingest/ingest.py --adapter mcp_server
    python3 scripts/ingest/ingest.py --list

Protocol: docs/INGESTION-PROTOCOL.md. One WCP per source repo lands in
research/parity/wcp/. Nothing downstream reads a repo directly, so adding a
source never touches the importer or the task compiler.

The governing rule, enforced by every adapter: anything that cannot be ported
faithfully goes into `refusals[]` with a count. Coverage is a measurement, not a
judgement — see the "19 of 22 expressible" overclaim this protocol exists to
prevent.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPOS = ROOT / "research" / "repos"
OUT = ROOT / "research" / "parity" / "wcp"
ADAPTERS: dict[str, callable] = {}


def adapter(name: str):
    def deco(fn):
        ADAPTERS[name] = fn
        fn.adapter_name = name
        return fn
    return deco


# --------------------------------------------------------------------- helpers
def git_commit(repo_dir: Path) -> str | None:
    try:
        return subprocess.run(["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
                              capture_output=True, text=True, timeout=30).stdout.strip() or None
    except Exception:
        return None


def detect_license(repo_dir: Path) -> str:
    """Best-effort licence identification; 'UNKNOWN' blocks vendoring, not facts."""
    for name in ("LICENSE", "LICENSE.txt", "LICENSE.md", "LICENCE", "COPYING", "LICENSE-PENDING.md"):
        p = repo_dir / name
        if p.exists():
            head = p.read_text(errors="ignore")[:2500].lower()
            for key, label in (("apache license", "Apache-2.0"), ("mit license", "MIT"),
                               ("bsd 3-clause", "BSD-3-Clause"), ("bsd 2-clause", "BSD-2-Clause"),
                               ("mozilla public license", "MPL-2.0"), ("gnu general public", "GPL"),
                               ("gnu affero", "AGPL"), ("creative commons", "CC")):
                if key in head:
                    return label
            return "OTHER"
    return "UNKNOWN"


def wcp(repo_dir: Path, adapter_name: str, fidelity: str) -> dict:
    rel = repo_dir.relative_to(ROOT) if repo_dir.is_relative_to(ROOT) else repo_dir
    owner_repo = repo_dir.name.replace("__", "/")
    return {
        "source": {
            "repo": owner_repo,
            "commit": git_commit(repo_dir),
            "path": str(rel),
            "url": f"https://github.com/{owner_repo}",
            "license": detect_license(repo_dir),
        },
        "adapter": {"name": adapter_name, "version": "1.0"},
        "fidelity": fidelity,
        "tables": [], "tools": [], "policies": [], "tasks": [], "refusals": [],
    }


def refuse(pkg: dict, kind: str, what: str, why: str, count: int = 1) -> None:
    pkg["refusals"].append({"kind": kind, "what": what, "why": why, "count": count})


# ------------------------------------------------------------- crmarena adapter
@adapter("crmarena")
def adapt_crmarena(_: Path | None = None) -> list[dict]:
    """CRMArena: 1,170 task instances + a SQLite org mirror + a SOQL tool surface.

    Fidelity is `exact` for tasks whose answer and metric we carry over verbatim.
    The tool surface is `adapted`: CRMArena's own functions call a live Salesforce
    org through simple_salesforce, so the world serves SOQL over the shipped
    mirror instead (harbor/crmarena-parity/images/world/soql.py).
    """
    repo_dir = ROOT / "external" / "CRMArena"
    tasks_file = ROOT / "research" / "parity" / "crmarena" / "crmarena_w_metadata.json"
    if not tasks_file.exists():
        return []
    pkg = wcp(repo_dir, "crmarena", "exact")
    pkg["source"]["dataset"] = "huggingface.co/datasets/Salesforce/CRMArena"

    instances = json.loads(tasks_file.read_text())
    by_metric: dict[str, int] = {}
    for t in instances:
        meta = t.get("metadata") or ""
        # metadata is a stringified dict of {'required': ..., 'optional': ...}
        required = optional = ""
        try:
            md = ast.literal_eval(meta) if isinstance(meta, str) and meta.strip().startswith("{") else {}
            required, optional = md.get("required", "") or "", md.get("optional", "") or ""
        except (ValueError, SyntaxError):
            required = meta
        metric = t.get("reward_metric", "exact_match")
        by_metric[metric] = by_metric.get(metric, 0) + 1
        answer = t.get("answer")
        pkg["tasks"].append({
            "id": f"crmarena_{t.get('task')}_{t.get('idx')}",
            "prompt": t.get("query", ""),
            "context": {"required": required, "optional": optional},
            "tags": [t.get("task"), "crmarena", "abstention" if str(answer) == "None" else "answerable"],
            "fidelity": "exact",
            "verifier": {
                "kind": "answer_match",
                "expected": answer,
                "metric": "fuzzy" if metric == "fuzzy_match" else "exact",
            },
        })

    # Seed data: the org mirror ships with the repo.
    for db_name, org in (("crmarena_data.db", "original"),
                         ("crmarenapro_b2b_data.db", "b2b"),
                         ("crmarenapro_b2c_data.db", "b2c")):
        db = repo_dir / "local_data" / db_name
        if not db.exists():
            continue
        conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        for (tname,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"):
            cols = [r[1] for r in conn.execute(f'PRAGMA table_info("{tname}")')]
            n = conn.execute(f'SELECT COUNT(*) FROM "{tname}"').fetchone()[0]
            pkg["tables"].append({"name": tname, "org": org, "columns": cols,
                                  "row_count": n, "rows_path": str(db.relative_to(ROOT))})
        conn.close()

    # Tool surface, as declared by CRMArena itself.
    init = repo_dir / "crm_sandbox" / "env" / "__init__.py"
    if init.exists():
        names = re.findall(r"^\s{4}([a-z_][a-z0-9_]*),?\s*$", init.read_text(), re.M)
        for n in dict.fromkeys(names):
            pkg["tools"].append({"name": n, "namespace": "crmarena", "description": "",
                                 "input_schema": None, "binding": "crm_sandbox/env/functions.py"})
        refuse(pkg, "tools", "CRMArena tool implementations",
               "functions.py calls a live Salesforce org via simple_salesforce; the world serves "
               "SOQL over the shipped SQLite mirror instead, so tool semantics are adapted, not exact",
               len(pkg["tools"]))

    refuse(pkg, "tasks", "CRMArena-Pro b2b/b2c splits",
           "only the base CRMArena split was downloaded; the Pro splits live in a separate HF config", 0)
    pkg["stats"] = {"instances": len(instances), "by_metric": by_metric}
    return [pkg]


# ------------------------------------------------------------ tau-bench adapter
@adapter("taubench")
def adapt_taubench(_: Path | None = None) -> list[dict]:
    """tau-bench: Task(...) literals whose ground truth is a required Action sequence."""
    base = REPOS / "eval" / "sierra-research__tau-bench" / "tau_bench" / "envs"
    if not base.exists():
        return []
    pkgs = []
    for domain_dir in sorted(d for d in base.iterdir() if d.is_dir() and (d / "tasks_test.py").exists()):
        pkg = wcp(REPOS / "eval" / "sierra-research__tau-bench", "taubench", "adapted")
        pkg["source"]["domain"] = domain_dir.name
        src = (domain_dir / "tasks_test.py").read_text()
        tree = ast.parse(src)
        n_tasks = skipped = 0
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and getattr(node.func, "id", "") == "Task"):
                continue
            kw = {}
            for k in node.keywords:
                try:
                    kw[k.arg] = ast.literal_eval(k.value)
                except ValueError:
                    kw[k.arg] = None  # nested Action(...) calls are not literals
            actions = []
            for k in node.keywords:
                if k.arg != "actions" or not isinstance(k.value, ast.List):
                    continue
                for el in k.value.elts:
                    if isinstance(el, ast.Call) and getattr(el.func, "id", "") == "Action":
                        a = {}
                        for ak in el.keywords:
                            try:
                                a[ak.arg] = ast.literal_eval(ak.value)
                            except ValueError:
                                a[ak.arg] = None
                        actions.append({"tool": a.get("name"), "args": a.get("kwargs") or {}})
            if not kw.get("instruction"):
                skipped += 1
                continue
            n_tasks += 1
            pkg["tasks"].append({
                "id": f"taubench_{domain_dir.name}_{n_tasks}",
                "prompt": kw["instruction"],
                "context": {"user_id": kw.get("user_id"), "domain": domain_dir.name},
                "tags": ["tau-bench", domain_dir.name],
                "fidelity": "adapted",
                "verifier": {"kind": "action_trace",
                             "required_calls": actions,
                             "order": "any",
                             "expected_outputs": kw.get("outputs") or []},
            })
        # Domain policy is the agent-facing rulebook.
        wiki = domain_dir / "wiki.md"
        if wiki.exists():
            pkg["policies"].append({"id": f"{domain_dir.name}_policy",
                                    "text": wiki.read_text()[:20000],
                                    "severity": "critical", "hard_fail": True})
        tools_dir = domain_dir / "tools"
        if tools_dir.exists():
            for f in sorted(tools_dir.glob("*.py")):
                if f.stem == "__init__":
                    continue
                pkg["tools"].append({"name": f.stem, "namespace": f"taubench_{domain_dir.name}",
                                     "description": "", "input_schema": None,
                                     "binding": str(f.relative_to(ROOT))})
        refuse(pkg, "data", f"{domain_dir.name} database",
               "tau-bench seeds its DB from JSON at runtime through its own env; the world would need "
               "an importer for that schema before these tasks can run at exact fidelity", 1)
        if skipped:
            refuse(pkg, "tasks", "tasks without a literal instruction",
                   "instruction was a non-literal expression the AST walker will not guess at", skipped)
        pkgs.append(pkg)
    return pkgs


# ----------------------------------------------------------- mcp_server adapter
_TOOL_PATTERNS = [
    re.compile(r'\b(?:registerTool|addTool|\.tool)\(\s*[\'"`]([a-zA-Z0-9_.\-]{3,64})[\'"`]'),
    re.compile(r'\bname:\s*[\'"`]([a-z][a-zA-Z0-9_.\-]{2,63})[\'"`]\s*,\s*\n?\s*(?:title|description|inputSchema)'),
    re.compile(r'@(?:mcp|server|app)\.tool\([^)]*\)\s*(?:async\s+)?def\s+([a-zA-Z0-9_]{3,64})'),
]
_DENY = re.compile(r'^(?:true|false|null|none|default|string|number|boolean|object|array|error|test|main|'
                   r'index|src|dist|build|lib|utils?|types?|config|schema|server|client|tool|tools|mcp|api|'
                   r'data|value|name|title|type|id|url|path|method|body|json|text|content|result|response)$')


@adapter("mcp_server")
def adapt_mcp_servers(_: Path | None = None) -> list[dict]:
    """Every cloned vendor MCP server contributes a tool surface to mock.

    No seed data and no tasks: these servers proxy a live SaaS, so what they
    yield is the verb vocabulary real agents are given.
    """
    base = REPOS / "mcp"
    if not base.exists():
        return []
    pkgs = []
    for repo_dir in sorted(d for d in base.iterdir() if d.is_dir()):
        pkg = wcp(repo_dir, "mcp_server", "adapted")
        vendor = repo_dir.name.split("__", 1)[-1]
        names: set[str] = set()
        for f in repo_dir.rglob("*"):
            if not f.is_file() or f.suffix not in {".ts", ".js", ".mjs", ".py", ".rs"}:
                continue
            if any(p in f.parts for p in (".git", "node_modules", "dist", "build")):
                continue
            try:
                if f.stat().st_size > 4_000_000:
                    continue
                text = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for pat in _TOOL_PATTERNS:
                for m in pat.finditer(text):
                    n = m.group(1)
                    if not _DENY.match(n.lower()) and "/" not in n:
                        names.add(n)
        for n in sorted(names):
            pkg["tools"].append({"name": n, "namespace": vendor, "description": "",
                                 "input_schema": None, "binding": None})
        refuse(pkg, "tools", "input schemas",
               "declared shapes are not extracted; only verb names are, so mocks need schemas authored",
               len(names))
        refuse(pkg, "data", "seed data", "MCP servers proxy a live SaaS and ship no fixtures", 1)
        if names:
            pkgs.append(pkg)
    return pkgs


# ------------------------------------------------------------ skillpack adapter
@adapter("skillpack")
def adapt_skillpacks(_: Path | None = None) -> list[dict]:
    """Practitioner SKILL.md files: workflow candidates, not graded tasks."""
    base = REPOS / "workflow"
    if not base.exists():
        return []
    pkgs = []
    for repo_dir in sorted(d for d in base.iterdir() if d.is_dir()):
        skills = list(repo_dir.rglob("SKILL.md"))
        if not skills:
            continue
        pkg = wcp(repo_dir, "skillpack", "inspired")
        for sf in skills:
            text = sf.read_text(errors="ignore")
            name = re.search(r"^name:\s*(.+)$", text, re.M)
            desc = re.search(r"^description:\s*(.+)$", text, re.M)
            pkg["tasks"].append({
                "id": f"skill_{repo_dir.name}_{sf.parent.name}",
                "prompt": (desc.group(1).strip().strip('"\'') if desc else "")[:600],
                "context": {"skill": (name.group(1).strip() if name else sf.parent.name),
                            "path": str(sf.relative_to(ROOT))},
                "tags": ["workflow", "skill", repo_dir.name],
                "fidelity": "inspired",
                "verifier": {"kind": "none",
                             "note": "a skill describes a procedure; it carries no ground truth"},
            })
        refuse(pkg, "verifier", "graded ground truth",
               "skills document procedures, not expected end states; tasks derived from them must be "
               "authored and gated separately", len(skills))
        pkgs.append(pkg)
    return pkgs


# ------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", action="append", help="run only these adapters")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    if args.list:
        for n in ADAPTERS:
            print(f"  {n}")
        return 0

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    chosen = args.adapter or list(ADAPTERS)
    total_pkgs = 0
    for name in chosen:
        fn = ADAPTERS.get(name)
        if not fn:
            print(f"unknown adapter: {name}")
            continue
        pkgs = fn() or []
        for pkg in pkgs:
            slug = pkg["source"]["repo"].replace("/", "__")
            if pkg["source"].get("domain"):
                slug += "__" + pkg["source"]["domain"]
            (out / f"{name}.{slug}.json").write_text(json.dumps(pkg, indent=1, default=str))
        total_pkgs += len(pkgs)
        t = sum(len(p["tasks"]) for p in pkgs)
        tl = sum(len(p["tools"]) for p in pkgs)
        tb = sum(len(p["tables"]) for p in pkgs)
        rf = sum(r["count"] for p in pkgs for r in p["refusals"])
        print(f"{name:<12} {len(pkgs):>3} pkg  {t:>5} tasks  {tl:>5} tools  {tb:>4} tables  {rf:>5} refused")

    print(f"\n{total_pkgs} WCPs -> {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
