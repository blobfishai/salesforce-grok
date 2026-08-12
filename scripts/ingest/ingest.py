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


# ----------------------------------------------------------------- eval adapter
# Graded benchmarks that were cloned but never ingested. Unlike the schema adapter,
# the interesting question here is not "how much is there" but "how much of it is
# actually about selling" — a task with immaculate ground truth in the wrong vertical
# is not evidence that this world covers its domain, and porting it anyway is how a
# benchmark ends up measuring nothing.

def _tau2_pkgs() -> list[dict]:
    """tau2-bench and its Amazon verified fork: persona + instructions + action ground truth."""
    pkgs = []
    for repo_name in ("sierra-research__tau2-bench", "amazon-agi__tau2-bench-verified"):
        repo_dir = REPOS / "eval" / repo_name
        domains = repo_dir / "data" / "tau2" / "domains"
        if not domains.is_dir():
            continue
        for domain_dir in sorted(d for d in domains.iterdir() if d.is_dir()):
            tasks_file = domain_dir / "tasks.json"
            if not tasks_file.exists():
                continue
            try:
                raw = json.loads(tasks_file.read_text())
            except ValueError:
                continue
            tasks = raw.get("tasks", raw) if isinstance(raw, dict) else raw
            if not isinstance(tasks, list):
                continue
            pkg = wcp(repo_dir, "eval", "reference")
            pkg["source"]["domain"] = domain_dir.name
            graded = 0
            for t in tasks:
                if not isinstance(t, dict):
                    continue
                scen = t.get("user_scenario") or {}
                instr = scen.get("instructions")
                if isinstance(instr, dict):
                    instr = instr.get("reason_for_call") or instr.get("task_instructions") or ""
                actions = ((t.get("evaluation_criteria") or {}).get("actions")) or []
                if actions:
                    graded += 1
                pkg["tasks"].append({
                    "id": f"tau2_{domain_dir.name}_{t.get('id')}",
                    "prompt": str(instr or "")[:1200],
                    "context": {"domain": domain_dir.name, "persona": scen.get("persona"),
                                "path": str(tasks_file.relative_to(ROOT))},
                    "tags": ["eval", "tau2", domain_dir.name],
                    "fidelity": "reference",
                    "verifier": {"kind": "action_sequence" if actions else "none",
                                 "expected_actions": [a.get("name") for a in actions if isinstance(a, dict)]},
                })
            # The ground truth is real; the vertical is not ours. Say so rather than
            # importing airline refunds into a CRM and calling it sales coverage.
            refuse(pkg, "tasks", "direct execution in this world",
                   f"tau2 '{domain_dir.name}' grades a different vertical against its own tool set; "
                   "the task SHAPE (persona + instructions + required action sequence) is the "
                   "transferable part, not the content", len(pkg["tasks"]))
            if graded:
                refuse(pkg, "verifier", "action-sequence ground truth",
                       "expected_actions name tau2 tools, which do not exist here; an equivalent "
                       "assertion must be written against this world's own surface", graded)
            pkgs.append(pkg)
    return pkgs


_ATTIO_SECTION = re.compile(r"^##\s+(.+?)\s*$", re.M)


def _attio_pkgs() -> list[dict]:
    """ArcadeAI's Attio benchmark: CRM read/filter queries with acceptance criteria."""
    repo_dir = REPOS / "eval" / "ArcadeAI__attio-mcp-benchmark"
    evals = repo_dir / "evals"
    if not evals.is_dir():
        return []
    pkg = wcp(repo_dir, "eval", "adapted")
    pkg["source"]["domain"] = "attio-crm-queries"
    not_expressible = 0
    for md in sorted(evals.glob("*.md")):
        text = md.read_text(errors="ignore")
        sections, order = {}, _ATTIO_SECTION.split(text)
        for i in range(1, len(order) - 1, 2):
            sections[order[i].strip().lower()] = order[i + 1].strip()
        query = sections.get("query", "").strip().strip('"')
        criteria = [ln.strip("- [ ]").strip()
                    for ln in sections.get("acceptance criteria", "").splitlines()
                    if ln.strip().startswith("- [")]
        if not query:
            not_expressible += 1
            continue
        pkg["tasks"].append({
            "id": f"attio_{md.stem}",
            "prompt": query,
            "context": {"expected_behavior": sections.get("expected behavior", "")[:600],
                        "path": str(md.relative_to(ROOT))},
            "tags": ["eval", "attio", "crm-query"],
            "fidelity": "adapted",
            "verifier": {"kind": "acceptance_criteria", "criteria": criteria},
        })
    # Attio IS a CRM, so these port on subject matter. What does not port is the
    # grading: acceptance criteria are prose, not a state assertion.
    refuse(pkg, "verifier", "machine-checkable ground truth",
           "acceptance criteria are natural-language checklists; running them here needs a SQL "
           "or state-diff assertion authored against this world's tables", len(pkg["tasks"]))
    if not_expressible:
        refuse(pkg, "tasks", "eval file without a Query section",
               "file does not follow the eval template", not_expressible)
    return [pkg] if pkg["tasks"] else []


def _r2a_pkgs() -> list[dict]:
    """R2A sales benchmark: structured policy atoms — required and forbidden behaviour."""
    repo_dir = REPOS / "eval" / "qinyh10300__R2A-Sales-Benchmark"
    atoms = repo_dir / "benchmark" / "policy_atoms"
    if not atoms.is_dir():
        return []
    try:
        import yaml
    except ImportError:
        return []
    pkg = wcp(repo_dir, "eval", "adapted")
    pkg["source"]["domain"] = "sales-policy-atoms"
    unparsed = 0
    for yf in sorted(atoms.glob("*.yaml")):
        try:
            d = yaml.safe_load(yf.read_text(errors="ignore")) or {}
        except Exception:
            unparsed += 1
            continue
        if not isinstance(d, dict) or not d.get("id"):
            unparsed += 1
            continue
        pkg["policies"].append({
            "id": d.get("id"),
            "severity": d.get("severity"),
            "hard_fail": bool(d.get("hard_fail")),
            "applies_when": d.get("applicability"),
            "required_behaviors": d.get("required_behaviors") or [],
            "forbidden_claims": d.get("forbidden_claims") or [],
            "escalate_when": d.get("escalate_when") or [],
            "context": {"path": str(yf.relative_to(ROOT))},
        })
    hard = [p for p in pkg["policies"] if p["hard_fail"]]
    # These are the best restraint source in the corpus: a hard_fail atom states an
    # action that must NOT be taken, which is exactly what a restraint task asserts.
    refuse(pkg, "tasks", "runnable task",
           "a policy atom states a rule, not a scenario; each becomes a restraint task only "
           "once paired with world state that tempts the agent to break it", len(pkg["policies"]))
    if unparsed:
        refuse(pkg, "policies", "unparsable atom", "YAML did not load or had no id", unparsed)
    print(f"    r2a: {len(pkg['policies'])} policy atoms ({len(hard)} hard-fail)")
    return [pkg] if pkg["policies"] else []


@adapter("eval")
def adapt_evals(_: Path | None = None) -> list[dict]:
    """Graded sales/agent benchmarks that were cloned but never ingested."""
    return _tau2_pkgs() + _attio_pkgs() + _r2a_pkgs()


# --------------------------------------------------------------- schema adapter
# Real production CRM/ERP data models. This is the denominator for the claim that
# the world covers its domain: not what one benchmark models, but what shipping
# CRMs actually store. Each stack states its schema differently, so there is one
# extractor per format and an explicit refusal when none of them bites.

_SQL_TABLE = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`\"\[]?([A-Za-z_][\w]*)[`\"\]]?\s*\((.*?)\)\s*(?:ENGINE|;)",
    re.I | re.S)
_SQL_COL = re.compile(r"^\s*[`\"\[]?([A-Za-z_][\w]*)[`\"\]]?\s+(?:INT|BIGINT|SMALLINT|TINYINT|VARCHAR|CHAR|TEXT|"
                      r"DATE|DATETIME|TIMESTAMP|DECIMAL|NUMERIC|FLOAT|DOUBLE|BOOL|BLOB|JSON|ENUM|UUID|SERIAL)",
                      re.I | re.M)
_LARAVEL_CREATE = re.compile(r"Schema::create\(\s*['\"]([\w]+)['\"](.*?)(?=Schema::create\(|\Z)", re.S)
_LARAVEL_COL = re.compile(r"\$table->\w+\(\s*['\"]([\w]+)['\"]")
_TS_ENTITY = re.compile(r"@Entity\([^)]*\)\s*(?:@\w+\([^)]*\)\s*)*export\s+class\s+(\w+)", re.S)
_TS_COL = re.compile(r"@(?:Column|ManyToOne|OneToMany|ManyToMany|OneToOne|PrimaryColumn|"
                     r"PrimaryGeneratedColumn|CreateDateColumn|UpdateDateColumn)\([^;]*?\)\s*(\w+)\s*[?!]?\s*:")
_MONGOOSE = re.compile(r"new\s+(?:mongoose\.)?Schema\(\s*\{(.*?)\n\}\s*[,)]", re.S)
_MONGOOSE_KEY = re.compile(r"^\s{2,4}(\w+)\s*:", re.M)

_SUITE_TABLE = re.compile(r"['\"]table['\"]\s*=>\s*['\"](\w+)['\"]")
_SUITE_FIELD = re.compile(r"['\"](\w+)['\"]\s*=>\s*array\s*\(\s*['\"]name['\"]\s*=>\s*['\"]\1['\"]")

_MAX_BYTES = 4_000_000
_MAX_FILES = 1500

# File discovery is grep/find-driven, not rglob-with-a-cap. An earlier version
# capped the ITERATION rather than the matches, so on a large repo the cap was
# spent on thousands of irrelevant files before the target directory was reached:
# EspoCRM yielded 2 entities of 110, Frappe 0 of 59, Twenty 0 of 41. Selecting the
# candidate files up front is both correct and much faster.


def _read(p: Path) -> str:
    try:
        if p.stat().st_size > _MAX_BYTES:
            return ""
        return p.read_text(errors="ignore")
    except OSError:
        return ""


def _prune(paths):
    out = []
    for p in paths:
        if not p:
            continue
        q = Path(p)
        if any(part in (".git", "node_modules", "vendor", "dist", "build") for part in q.parts):
            continue
        out.append(q)
    return out[:_MAX_FILES]


def _find(repo: Path, args: list[str]) -> list[Path]:
    try:
        r = subprocess.run(["find", str(repo), "-type", "f", *args],
                           capture_output=True, text=True, timeout=90)
        return _prune(r.stdout.split("\n"))
    except Exception:
        return []


def _grep_files(repo: Path, needle: str, include: str | None = None) -> list[Path]:
    """Files containing `needle` — far cheaper than reading every candidate."""
    cmd = ["grep", "-rl", "--binary-files=without-match", needle, str(repo)]
    if include:
        cmd.insert(2, f"--include={include}")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return _prune(r.stdout.split("\n"))
    except Exception:
        return []


def _espo(repo):
    """EspoCRM: metadata/entityDefs/<Entity>.json, fields keyed by name."""
    tables = {}
    for p in _find(repo, ["-path", "*entityDefs*", "-name", "*.json"]):
        try:
            d = json.loads(_read(p) or "{}")
        except ValueError:
            continue
        if isinstance(d.get("fields"), dict) and d["fields"]:
            tables[p.stem] = sorted(d["fields"])
    return tables


def _frappe(repo):
    """Frappe: doctype/<name>/<name>.json with a fields[] array."""
    tables = {}
    for p in _find(repo, ["-path", "*doctype*", "-name", "*.json"]):
        try:
            d = json.loads(_read(p) or "{}")
        except ValueError:
            continue
        if not isinstance(d, dict):
            continue
        if d.get("doctype") == "DocType" or (d.get("name") and isinstance(d.get("fields"), list)):
            cols = [f.get("fieldname") for f in d.get("fields", [])
                    if isinstance(f, dict) and f.get("fieldname")]
            if cols:
                tables[str(d.get("name") or p.stem)] = sorted(set(cols))
    return tables


def _django(repo):
    """Django: class X(models.Model) with Field() assignments."""
    tables = {}
    for p in _find(repo, ["-name", "models.py"]):
        try:
            tree = ast.parse(_read(p))
        except (SyntaxError, ValueError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            if not any("Model" in ast.unparse(b) for b in node.bases):
                continue
            cols = [t.id for stmt in node.body if isinstance(stmt, ast.Assign)
                    for t in stmt.targets if isinstance(t, ast.Name)
                    and isinstance(stmt.value, ast.Call) and "Field" in ast.unparse(stmt.value.func)]
            if cols:
                tables[node.name] = sorted(set(cols))
    return tables


def _laravel(repo):
    """Laravel migrations: Schema::create('t', fn) with $table->type('col')."""
    tables = {}
    for p in _grep_files(repo, "Schema::create", "*.php"):
        for name, body in _LARAVEL_CREATE.findall(_read(p)):
            cols = set(_LARAVEL_COL.findall(body))
            if cols:
                tables.setdefault(name, set()).update(cols)
    return {k: sorted(v) for k, v in tables.items()}


def _typeorm(repo):
    """TypeORM: @Entity() export class X with decorated properties."""
    tables = {}
    for p in _grep_files(repo, "@Entity(", "*.ts"):
        text = _read(p)
        cols = sorted(set(_TS_COL.findall(text)))
        for name in _TS_ENTITY.findall(text):
            if cols:
                tables[name] = cols
    return tables


def _mongoose(repo):
    """Mongoose: new Schema({ key: ... }) — entity named for its file."""
    tables = {}
    for p in _grep_files(repo, "Schema(", "*.js"):
        for body in _MONGOOSE.findall(_read(p)):
            cols = sorted(set(_MONGOOSE_KEY.findall(body)))
            if cols:
                tables[p.stem] = cols
    return tables


def _suitecrm(repo):
    """SugarCRM/SuiteCRM vardefs.php: 'table' => 'x' with a fields array."""
    tables = {}
    for p in _find(repo, ["-name", "vardefs.php"]):
        text = _read(p)
        m = _SUITE_TABLE.search(text)
        if not m:
            continue
        cols = sorted(set(_SUITE_FIELD.findall(text)))
        if cols:
            tables[m.group(1)] = cols
    return tables


def _sql(repo):
    """Any CREATE TABLE, wherever it lives — the most portable signal there is."""
    tables = {}
    for p in _grep_files(repo, "CREATE TABLE"):
        for name, body in _SQL_TABLE.findall(_read(p)):
            cols = sorted(set(_SQL_COL.findall(body)))
            if cols:
                tables.setdefault(name, cols)
    return tables


_EXTRACTORS = (("espo", _espo), ("frappe", _frappe), ("django", _django),
               ("laravel", _laravel), ("typeorm", _typeorm), ("mongoose", _mongoose),
               ("suitecrm", _suitecrm), ("sql", _sql))


@adapter("schema")
def adapt_schemas(_: Path | None = None) -> list[dict]:
    """Production CRM/ERP data models — the domain's real entity vocabulary."""
    base = REPOS / "schema"
    if not base.exists():
        return []
    pkgs = []
    for repo_dir in sorted(d for d in base.iterdir() if d.is_dir()):
        pkg = wcp(repo_dir, "schema", "reference")
        found, formats = {}, []
        for fmt_name, fn in _EXTRACTORS:
            try:
                got = fn(repo_dir)
            except Exception:
                got = {}
            if got:
                formats.append(fmt_name)
                for t, cols in got.items():
                    found.setdefault(t, cols)
        for name, cols in sorted(found.items()):
            pkg["tables"].append({
                "name": name,
                "columns": [{"name": c} for c in cols],
                "provenance": {"repo": pkg["source"]["repo"], "formats": formats},
            })
        if not found:
            refuse(pkg, "tables", "schema definition",
                   "no CREATE TABLE, ORM model, migration or entity-definition file matched any "
                   "known extractor; the repo may define its schema at runtime or ship none", 1)
        else:
            # A data model is evidence about the domain, never a runnable capability.
            refuse(pkg, "tools", "executable behaviour",
                   "a schema states what is stored, not what can be done with it; tools must be "
                   "authored against the world's own surface", len(found))
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
