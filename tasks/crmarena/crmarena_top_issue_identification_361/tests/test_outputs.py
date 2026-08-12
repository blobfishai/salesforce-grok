"""CRMArena parity verifier — reproduces CRMArena's own scoring.

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
TOKEN = os.environ.get("HARBOR_VERIFIER_TOKEN", "harbor-verifier-token")
EXPECTED = json.loads(pathlib.Path("/tests/expected.json").read_text())


def _fetch(tries=4):
    last = None
    for attempt in range(tries):
        try:
            r = httpx.post(f"{WORLD}/verifier/answer", json={},
                           headers={"X-Verifier-Token": TOKEN}, timeout=120.0)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001 - retried; a transport blip is not a wrong answer
            last = e
            time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"verifier endpoint unreachable: {last}")


def normalize_answer(s):
    """Verbatim from CRMArena crm_sandbox/agents/utils.py."""
    def remove_articles(text):
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def white_space_fix(text):
        return " ".join(text.split())

    def handle_punc(text):
        exclude = set(string.punctuation + "".join(["\u2018", "\u2019", "\u00b4", "`"]))
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
        + ", ".join(sorted({c['tool'] for c in RESULT.get('calls', [])}))
    )


@pytest.mark.skipif(METRIC != "exact", reason="exact_match tasks only")
def test_exact_match():
    assert PROPOSED == GT, f"expected {GT!r}, got {PROPOSED!r}"


@pytest.mark.skipif(METRIC != "fuzzy", reason="fuzzy_match tasks only")
def test_fuzzy_match():
    f1 = f1_score(PROPOSED or "", GT)
    assert f1 >= 0.5, f"token F1 {f1:.2f} below 0.5 — expected {GT!r}, got {PROPOSED!r}"


@pytest.fixture(scope="session", autouse=True)
def _emit_reward():
    yield
    if METRIC == "exact":
        reward = 1.0 if (RESULT.get("responded") and PROPOSED == GT) else 0.0
        detail = {"metric": "exact_match", "expected": GT, "proposed": PROPOSED}
    else:
        f1 = f1_score(PROPOSED or "", GT) if RESULT.get("responded") else 0.0
        em = 1.0 if normalize_answer(PROPOSED or "") == normalize_answer(GT) else 0.0
        reward = round(f1, 4)
        detail = {"metric": "fuzzy_match", "f1": round(f1, 4), "em": em,
                   "expected": GT, "proposed": PROPOSED}
    detail["tool_calls"] = len(RESULT.get("calls", []))
    detail["reward"] = reward
    pathlib.Path("/logs/verifier").mkdir(parents=True, exist_ok=True)
    pathlib.Path("/logs/verifier/reward_fraction.txt").write_text(str(reward))
    pathlib.Path("/logs/verifier/checks_detail.json").write_text(json.dumps(detail, indent=2))
