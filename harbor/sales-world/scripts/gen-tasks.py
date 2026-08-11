#!/usr/bin/env python3
"""Generate Harbor task directories from the sales task spec.

    python3 scripts/gen-tasks.py [--spec tasks.spec.jsonl] [--out tasks] [--tag w6]

Each spec line becomes a self-contained Harbor task:

    tasks/<id>/
      task.toml                     schema 1.1 + one [[environment.mcp_servers]] per vendor
      instruction.md                the request, written the way a colleague would send it
      environment/
        Dockerfile                  agent-side image (python + mcp client)
        docker-compose.yaml         world + one gateway container per vendor
      tests/
        test.sh                     pytest -> /logs/verifier/{ctrf.json,reward.txt}
        test_outputs.py             one test function per check, so CTRF shows assertion detail
        checks.json                 the checks, data-only
      solution/solve.sh             reference trajectory (oracle run)

Design notes worth keeping:
- Tasks reference prebuilt images (`sales-world:<tag>`), so a task dir is ~8 KB
  rather than carrying a 15 MB copy of the company.
- Verification queries the database directly over the world's verifier-only SQL
  endpoint. Grading through the same MCP tools the agent used would let one tool
  bug fail a correct trajectory.
- The verifier token lives in `[verifier.env]` only, so the agent cannot reach
  the endpoint that holds the answer key.
"""
from __future__ import annotations

import argparse
import json
import shutil
import stat
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
VERIFIER_TOKEN = "harbor-verifier-token"  # scoped to [verifier.env]; not secret, just unreachable from the agent

AGENT_DOCKERFILE = """FROM python:3.12-slim

# Agent-side workspace. The company lives in sibling containers reachable over
# MCP; nothing about the world is available locally, which is the point.
RUN apt-get update && apt-get install -y --no-install-recommends curl jq \\
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir mcp httpx

WORKDIR /app
"""

TEST_SH = """#!/bin/bash
# Harbor verifier: run the checks, emit CTRF + a scalar reward.
set -uo pipefail

mkdir -p /logs/verifier

pip install --quiet --no-cache-dir pytest==8.4.1 pytest-json-ctrf==0.3.5 httpx >/dev/null 2>&1

pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
status=$?

# Partial credit: Harbor takes the scalar in reward.txt, and a long-horizon sales
# task that got 7 of 9 assertions right is genuinely different from one that did
# nothing. test_outputs.py writes the fraction; fall back to binary on crash.
if [ -s /logs/verifier/reward_fraction.txt ]; then
  cat /logs/verifier/reward_fraction.txt > /logs/verifier/reward.txt
elif [ $status -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

exit $status
"""

TEST_OUTPUTS = '''"""Verifier for {task_id}.

One test per check so the CTRF report names exactly which business assertion
failed — "quote left in draft" reads better in a results table than "task failed".
"""
import json
import os
import pathlib

import httpx
import pytest

WORLD = os.environ.get("WORLD_URL", "http://world:8080")
TOKEN = os.environ.get("HARBOR_VERIFIER_TOKEN", "{token}")
CHECKS = json.loads(pathlib.Path("/tests/checks.json").read_text())

_results = {{}}


def query(sql, params=None, db="state"):
    r = httpx.post(
        f"{{WORLD}}/verifier/query",
        json={{"sql": sql, "params": params or [], "db": db}},
        headers={{"X-Verifier-Token": TOKEN}},
        timeout=60.0,
    )
    r.raise_for_status()
    return r.json()["rows"]


def evaluate(check):
    rows = query(check["sql"], check.get("params"), check.get("db", "state"))
    exp = check["expect"]

    if "row_count" in exp:
        assert len(rows) == exp["row_count"], f"expected {{exp['row_count']}} rows, got {{len(rows)}}: {{rows[:5]}}"

    if "min_rows" in exp:
        assert len(rows) >= exp["min_rows"], f"expected >= {{exp['min_rows']}} rows, got {{len(rows)}}"

    if "scalar_equals" in exp:
        assert rows, "query returned no rows"
        got = list(rows[0].values())[0]
        want = exp["scalar_equals"]
        if isinstance(want, (int, float)) and not isinstance(want, bool):
            got = float(got)
            tol = exp.get("tolerance", 0)
            assert abs(got - float(want)) <= tol, f"expected {{want}} (+/-{{tol}}), got {{got}}"
        else:
            assert str(got).strip().lower() == str(want).strip().lower(), f"expected {{want!r}}, got {{got!r}}"

    if "scalar_between" in exp:
        assert rows, "query returned no rows"
        got = float(list(rows[0].values())[0])
        lo, hi = exp["scalar_between"]
        assert lo <= got <= hi, f"expected between {{lo}} and {{hi}}, got {{got}}"

    if "rows_equal" in exp:
        want = exp["rows_equal"]
        norm = lambda rs: sorted(
            [{{k: (str(v).strip().lower() if v is not None else None) for k, v in r.items()}} for r in rs],
            key=lambda d: json.dumps(d, sort_keys=True, default=str),
        )
        assert norm(rows) == norm(want), f"expected {{want}}, got {{rows}}"

    if exp.get("unchanged_vs_seed"):
        seed_rows = query(check["sql"], check.get("params"), db="seed")
        assert rows == seed_rows, (
            f"collateral damage: {{len(rows)}} rows now vs {{len(seed_rows)}} in the untouched world"
        )


@pytest.mark.parametrize("check", CHECKS, ids=[c["name"] for c in CHECKS])
def test_check(check):
    try:
        evaluate(check)
    except AssertionError:
        _results[check["name"]] = False
        raise
    _results[check["name"]] = True


@pytest.fixture(scope="session", autouse=True)
def _emit_fraction():
    """Write partial credit after the whole session, not per test."""
    yield
    passed = sum(1 for v in _results.values() if v)
    total = len(CHECKS)
    frac = round(passed / total, 4) if total else 0.0
    pathlib.Path("/logs/verifier").mkdir(parents=True, exist_ok=True)
    pathlib.Path("/logs/verifier/reward_fraction.txt").write_text(str(frac))
    pathlib.Path("/logs/verifier/checks_detail.json").write_text(
        json.dumps({{"passed": passed, "total": total, "reward": frac, "results": _results}}, indent=2)
    )
'''

SOLVE_SH = """#!/bin/bash
# Reference trajectory. Harbor runs this as the oracle: if it does not score 1.0,
# the task is broken, not the agent.
set -euo pipefail
{body}
"""


def compose(vendors: list[str], tag: str) -> str:
    lines = [
        "# Merged on top of Harbor's base compose. `main` is the agent container.",
        "services:",
        "  main:",
        "    depends_on:",
    ]
    for v in vendors:
        lines.append(f"      {v}:")
        lines.append("        condition: service_healthy")
    lines += [
        "",
        "  world:",
        f"    image: sales-world:{tag}",
        "    expose:",
        '      - "8080"',
        "    environment:",
        f"      HARBOR_VERIFIER_TOKEN: {VERIFIER_TOKEN}",
        "",
    ]
    for i, v in enumerate(vendors):
        lines += [
            f"  {v}:",
            f"    image: sales-world-gateway:{tag}",
            "    depends_on:",
            "      world:",
            "        condition: service_healthy",
            "    environment:",
            "      UPSTREAM: http://world:8080/mcp",
            f"      NAMESPACE: {v}",
            f"      VENDOR: {v}",
            "    expose:",
            '      - "8000"',
            "",
        ]
    return "\n".join(lines)


def task_toml(spec: dict, vendors: list[str]) -> str:
    kw = spec.get("keywords") or [spec.get("family", "sales")]
    out = [
        'schema_version = "1.1"',
        "",
        "[task]",
        f'name = "sales-world/{spec["id"]}"',
        f'description = "{spec["title"]}"',
        'authors = [{ name = "salesforce-grok sales-world" }]',
        "keywords = [" + ", ".join(f'"{k}"' for k in kw) + "]",
        "",
        "[metadata]",
        f'family = "{spec.get("family", "sales")}"',
        f'persona = "{spec.get("persona", "revenue operations")}"',
        f'difficulty = "{spec.get("difficulty", "medium")}"',
        "citations = [" + ", ".join(f'"{c}"' for c in spec.get("citations", [])) + "]",
        "",
        "[verifier]",
        f'timeout_sec = {float(spec.get("timeouts", {}).get("verifier", 600))}',
        "",
        "[verifier.env]",
        f'HARBOR_VERIFIER_TOKEN = "{VERIFIER_TOKEN}"',
        'WORLD_URL = "http://world:8080"',
        "",
        "[agent]",
        f'timeout_sec = {float(spec.get("timeouts", {}).get("agent", 1800))}',
        "",
        "[environment]",
        "build_timeout_sec = 900.0",
        "cpus = 2",
        "memory_mb = 4096",
        "storage_mb = 10240",
        "gpus = 0",
        "",
        "[environment.env]",
        "",
    ]
    for v in vendors:
        out += [
            "[[environment.mcp_servers]]",
            f'name = "{v}"',
            'transport = "streamable-http"',
            f'url = "http://{v}:8000/mcp"',
            "args = []",
            "",
        ]
    return "\n".join(out)


def write_exec(path: Path, content: str) -> None:
    path.write_text(content)
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default=str(HERE / "tasks.spec.jsonl"))
    ap.add_argument("--out", default=str(HERE / "tasks"))
    ap.add_argument("--tag", default="w6")
    ap.add_argument("--clean", action="store_true", help="remove generated tasks first")
    args = ap.parse_args()

    out = Path(args.out)
    if args.clean and out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    specs = [json.loads(l) for l in Path(args.spec).read_text().splitlines() if l.strip()]
    for spec in specs:
        vendors = spec.get("vendors") or ["salesforce"]
        d = out / spec["id"]
        (d / "environment").mkdir(parents=True, exist_ok=True)
        (d / "tests").mkdir(parents=True, exist_ok=True)
        (d / "solution").mkdir(parents=True, exist_ok=True)

        (d / "task.toml").write_text(task_toml(spec, vendors))
        (d / "instruction.md").write_text(spec["instruction"].rstrip() + "\n")
        (d / "environment" / "Dockerfile").write_text(AGENT_DOCKERFILE)
        (d / "environment" / "docker-compose.yaml").write_text(compose(vendors, args.tag))
        (d / "tests" / "checks.json").write_text(json.dumps(spec["verify"]["checks"], indent=2))
        (d / "tests" / "test_outputs.py").write_text(
            TEST_OUTPUTS.format(task_id=spec["id"], token=VERIFIER_TOKEN)
        )
        write_exec(d / "tests" / "test.sh", TEST_SH)
        write_exec(d / "solution" / "solve.sh", SOLVE_SH.format(body=spec.get("solution", "echo 'no reference solution'")))

        print(f"  {spec['id']:<44} {len(spec['verify']['checks'])} checks  vendors={','.join(vendors)}")

    print(f"\n{len(specs)} tasks -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
