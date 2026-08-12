#!/usr/bin/env python3
"""Compile `answer_match` WCP tasks into a runnable Harbor dataset.

    python3 scripts/ingest/compile_tasks.py --wcp crmarena.SalesforceAIResearch__CRMArena.json \
        --out tasks/crmarena --sample 27 --stratify-by tag

Closes the gap between *ingested* and *running*. Grading reproduces CRMArena's
own metric rather than reinterpreting it, because that is what licenses the
`exact` fidelity claim and comparison with its published numbers:

  exact_match  strict string equality (crm_sandbox/env/env.py:calculate_reward),
               with a null ground truth compared as the literal "None"
  fuzzy_match  SQuAD-style normalisation + token F1
               (crm_sandbox/agents/utils.py:normalize_answer, f1_score)

Harbor needs one scalar per trial, so fuzzy tasks report F1 as the reward and
carry em/f1 through in checks_detail.json.
"""
from __future__ import annotations

import argparse
import collections
import json
import random
import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WCP_DIR = ROOT / "research" / "parity" / "wcp"
VERIFIER_TOKEN = "harbor-verifier-token"

AGENT_DOCKERFILE = """FROM node:22-bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \\
        python3 python3-pip python3-venv curl jq ca-certificates procps \\
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install --no-cache-dir --break-system-packages \\
        mcp httpx pytest==8.4.1 pytest-json-ctrf==0.3.5
WORKDIR /app
"""

COMPOSE = """# Merged on top of Harbor's base compose.
services:
  main:
    depends_on:
      crm:
        condition: service_healthy

  crm:
    image: crmarena-parity:{tag}
    pull_policy: never
    expose:
      - "8080"
    environment:
      HARBOR_VERIFIER_TOKEN: {token}
"""

TEST_SH = """#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier
if ! python3 -m pytest --version >/dev/null 2>&1; then
  echo "pytest missing from image, installing" >&2
  pip3 install --no-cache-dir --break-system-packages pytest==8.4.1 pytest-json-ctrf==0.3.5 httpx
fi
python3 -m pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
status=$?
if [ -s /logs/verifier/reward_fraction.txt ]; then
  cat /logs/verifier/reward_fraction.txt > /logs/verifier/reward.txt
elif [ $status -eq 0 ]; then echo 1 > /logs/verifier/reward.txt
else echo 0 > /logs/verifier/reward.txt
fi
exit $status
"""

TEST_OUTPUTS = '''"""CRMArena parity verifier — reproduces CRMArena's own scoring.

exact_match: strict equality, per crm_sandbox/env/env.py:calculate_reward.
fuzzy_match: normalize_answer + token F1, per crm_sandbox/agents/utils.py.
Neither is reinterpreted; that is what the `exact` fidelity claim rests on.
"""
import json
import os
import pathlib
import re
import string
import time
from collections import Counter

import httpx
import pytest

WORLD = os.environ.get("CRM_URL", "http://crm:8080")
TOKEN = os.environ.get("HARBOR_VERIFIER_TOKEN", "{token}")
EXPECTED = json.loads(pathlib.Path("/tests/expected.json").read_text())


def _fetch(tries=4):
    last = None
    for attempt in range(tries):
        try:
            r = httpx.post(f"{{WORLD}}/verifier/answer", json={{}},
                           headers={{"X-Verifier-Token": TOKEN}}, timeout=120.0)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001 - retried; a transport blip is not a wrong answer
            last = e
            time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"verifier endpoint unreachable: {{last}}")


def normalize_answer(s):
    """Verbatim from CRMArena crm_sandbox/agents/utils.py."""
    def remove_articles(text):
        return re.sub(r"\\b(a|an|the)\\b", " ", text)

    def white_space_fix(text):
        return " ".join(text.split())

    def handle_punc(text):
        exclude = set(string.punctuation + "".join(["\\u2018", "\\u2019", "\\u00b4", "`"]))
        return "".join(ch if ch not in exclude else " " for ch in text)

    return white_space_fix(remove_articles(handle_punc(str(s).lower().replace("_", " ")))).strip()


def f1_score(prediction, ground_truth):
    p_tokens = normalize_answer(prediction).split()
    g_tokens = normalize_answer(ground_truth).split()
    common = Counter(p_tokens) & Counter(g_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0
    precision = num_same / len(p_tokens)
    recall = num_same / len(g_tokens)
    return (2 * precision * recall) / (precision + recall)


RESULT = _fetch()
PROPOSED = RESULT.get("answer")
GT = EXPECTED["expected"]
GT = "None" if GT is None else str(GT)
METRIC = EXPECTED["metric"]


def test_answer_was_submitted():
    """CRMArena scores the respond() payload; nothing submitted is nothing scored."""
    assert RESULT.get("responded"), (
        "agent never called respond(); tools used: "
        + ", ".join(sorted({{c['tool'] for c in RESULT.get('calls', [])}}))
    )


@pytest.mark.skipif(METRIC != "exact", reason="exact_match tasks only")
def test_exact_match():
    assert PROPOSED == GT, f"expected {{GT!r}}, got {{PROPOSED!r}}"


@pytest.mark.skipif(METRIC != "fuzzy", reason="fuzzy_match tasks only")
def test_fuzzy_match():
    f1 = f1_score(PROPOSED or "", GT)
    assert f1 >= 0.5, f"token F1 {{f1:.2f}} below 0.5 — expected {{GT!r}}, got {{PROPOSED!r}}"


@pytest.fixture(scope="session", autouse=True)
def _emit_reward():
    yield
    if METRIC == "exact":
        reward = 1.0 if (RESULT.get("responded") and PROPOSED == GT) else 0.0
        detail = {{"metric": "exact_match", "expected": GT, "proposed": PROPOSED}}
    else:
        f1 = f1_score(PROPOSED or "", GT) if RESULT.get("responded") else 0.0
        em = 1.0 if normalize_answer(PROPOSED or "") == normalize_answer(GT) else 0.0
        reward = round(f1, 4)
        detail = {{"metric": "fuzzy_match", "f1": round(f1, 4), "em": em,
                   "expected": GT, "proposed": PROPOSED}}
    detail["tool_calls"] = len(RESULT.get("calls", []))
    detail["reward"] = reward
    pathlib.Path("/logs/verifier").mkdir(parents=True, exist_ok=True)
    pathlib.Path("/logs/verifier/reward_fraction.txt").write_text(str(reward))
    pathlib.Path("/logs/verifier/checks_detail.json").write_text(json.dumps(detail, indent=2))
'''

SOLVE_SH = """#!/bin/bash
# HARNESS CHECK, NOT A SOLUTION. This submits the known ground truth to prove the
# world, the answer channel and the metric agree end to end. It does NOT show the
# task is solvable from the data with the tools provided — only a model run can.
#
# The answer is baked in at compile time rather than read from /tests, because
# Harbor mounts /tests into the verifier container only; the agent container
# cannot see it.
set -euo pipefail
python3 - <<'PY'
import asyncio, json
from mcp.client.session import ClientSession
try:
    from mcp.client.streamable_http import streamable_http_client as http_client
except ImportError:
    from mcp.client.streamable_http import streamablehttp_client as http_client

ANSWER = json.loads({answer_json!r})
ANSWER = 'None' if ANSWER is None else str(ANSWER)

async def main():
    async with http_client('http://crm:8080/mcp') as (r, w, *_):
        async with ClientSession(r, w) as s:
            await s.initialize()
            out = await s.call_tool('respond', {'answer': ANSWER})
            print(out.content[0].text[:160])

asyncio.run(main())
PY
"""

# The question leads. Context must never start the file: an instruction beginning
# with "- " is parsed as a flag by CLI agents (grok-build died with
# "unexpected argument '- ' found" on all 20 trials).
INSTRUCTION = """# CRM question

{prompt}

## Context
{required}

## How to work
The CRM is on the `crm` MCP server. Query it with `issue_soql_query` (SOQL;
relationship traversal like `Account.Name` and subqueries are not supported), and
use `get_schema` to see what fields an object has. `search_knowledge_articles`
searches the knowledge base.

When you have the answer, call `respond` **exactly once** with the answer only —
an Id, a value, or the string `None` if the question cannot be answered from the
data. Do not include explanation in the answer.
{optional}"""


def task_toml(t: dict, tag: str) -> str:
    cat = (t.get("tags") or ["crmarena"])[0]
    kw = [k for k in (t.get("tags") or []) if k]
    return "\n".join([
        'schema_version = "1.1"', "",
        "[task]",
        f'name = "crmarena-parity/{t["id"]}"',
        f'description = "CRMArena {cat} — reproduced at exact fidelity"',
        'authors = [{ name = "CRMArena (Salesforce AI Research), ingested by salesforce-grok" }]',
        "keywords = [" + ", ".join(f'"{k}"' for k in kw) + "]", "",
        "[metadata]",
        f'source = "SalesforceAIResearch/CRMArena"',
        f'category = "{cat}"',
        f'fidelity = "{t.get("fidelity", "exact")}"',
        f'reward_metric = "{t["verifier"]["metric"]}_match"', "",
        "[verifier]", "timeout_sec = 600.0", "",
        "[verifier.env]",
        f'HARBOR_VERIFIER_TOKEN = "{VERIFIER_TOKEN}"',
        'CRM_URL = "http://crm:8080"', "",
        "[agent]", "timeout_sec = 1800.0", "",
        "[environment]", "build_timeout_sec = 900.0", "cpus = 2", "memory_mb = 4096",
        "storage_mb = 10240", "gpus = 0", "", "[environment.env]", "",
        "[[environment.mcp_servers]]", 'name = "crm"', 'transport = "streamable-http"',
        'url = "http://crm:8080/mcp"', "args = []", "",
    ])


def write_exec(path: Path, content: str) -> None:
    path.write_text(content)
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wcp", default="crmarena.SalesforceAIResearch__CRMArena.json")
    ap.add_argument("--out", default=str(ROOT / "tasks/crmarena"))
    ap.add_argument("--tag", default="v1", help="world image tag")
    ap.add_argument("--sample", type=int, default=0, help="0 = compile everything")
    ap.add_argument("--stratify-by", default="tag", choices=["tag", "none"])
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    pkg = json.loads((WCP_DIR / args.wcp).read_text())
    tasks = [t for t in pkg["tasks"] if t.get("verifier", {}).get("kind") == "answer_match"]
    if not tasks:
        print("no answer_match tasks in that WCP")
        return 1

    if args.sample:
        rng = random.Random(args.seed)
        if args.stratify_by == "tag":
            buckets: dict[str, list] = collections.defaultdict(list)
            for t in tasks:
                buckets[(t.get("tags") or ["?"])[0]].append(t)
            per = max(1, args.sample // max(1, len(buckets)))
            picked = []
            for _, items in sorted(buckets.items()):
                picked.extend(rng.sample(items, min(per, len(items))))
            tasks = picked[: args.sample] if args.sample < len(picked) else picked
        else:
            tasks = rng.sample(tasks, min(args.sample, len(tasks)))

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    by_cat = collections.Counter()
    for t in tasks:
        d = out / t["id"]
        (d / "environment").mkdir(parents=True, exist_ok=True)
        (d / "tests").mkdir(parents=True, exist_ok=True)
        (d / "solution").mkdir(parents=True, exist_ok=True)

        ctx = t.get("context") or {}
        optional = (ctx.get("optional") or "").strip()
        (d / "instruction.md").write_text(INSTRUCTION.format(
            required=(ctx.get("required") or "").strip(),
            prompt=t["prompt"].strip(),
            optional=("\n\n## Domain reference\n" + optional) if optional else "",
        ).strip() + "\n")
        (d / "task.toml").write_text(task_toml(t, args.tag))
        (d / "environment" / "Dockerfile").write_text(AGENT_DOCKERFILE)
        (d / "environment" / "docker-compose.yaml").write_text(
            COMPOSE.format(tag=args.tag, token=VERIFIER_TOKEN))
        (d / "tests" / "expected.json").write_text(json.dumps({
            "expected": t["verifier"]["expected"], "metric": t["verifier"]["metric"],
            "task_id": t["id"],
        }, indent=1))
        (d / "tests" / "test_outputs.py").write_text(TEST_OUTPUTS.format(token=VERIFIER_TOKEN))
        write_exec(d / "tests" / "test.sh", TEST_SH)
        write_exec(d / "solution" / "solve.sh",
                   SOLVE_SH.replace('{answer_json!r}', repr(json.dumps(t['verifier']['expected']))))
        by_cat[(t.get("tags") or ["?"])[0]] += 1

    rel = out.relative_to(ROOT) if out.is_absolute() and out.is_relative_to(ROOT) else out
    print(f"compiled {len(tasks)} tasks -> {rel}")
    for c, n in sorted(by_cat.items()):
        print(f"  {c:<34} {n}")
    n_abstain = sum(1 for t in tasks if str(t["verifier"]["expected"]) == "None")
    print(f"  (of which {n_abstain} are abstention tasks whose correct answer is 'None')")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
