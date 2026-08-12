# Tasks

Every task an agent is asked to do in this world. Two committed suites, run with
[Harbor](https://github.com/harbor-framework/harbor) from the repo root:

```bash
harbor/sales-world/scripts/build-images.sh    # build the world image first

harbor run -p tasks/sales-world -a oracle     # 20 tasks — expect 1.000
harbor run -p tasks/crmarena   -a oracle      # 27 tasks — the CRMArena reproduction
```

| suite | tasks | what it is |
|---|---:|---|
| `sales-world/` | 20 | Hand-authored B2B revenue work across 11 vendor systems. The suite of record. |
| `crmarena/` | 27 | CRMArena's 9 task categories × 3, ported onto this world. grok-4.5 scored 36.7%, inside the published band. |

Generated in bulk and gitignored (regenerate with `scripts/ingest/compile_tasks.py`):
`crmarena-full/`, `crmarena-waves/` (870), `crmarena-slice/` (90).

## What a task is

```
tasks/sales-world/webhook-failure-triage/
  instruction.md                 the prompt, verbatim — this is what the model sees
  task.toml                      Harbor schema 1.1: timeouts, resources, MCP servers
  tests/checks.json              business assertions as SQL + expectation
  tests/test_outputs.py          one pytest per check, so CTRF names the assertion
  tests/test.sh                  verifier entrypoint -> reward.txt
  solution/solve.sh              reference rollout; the oracle gate
  environment/                   docker-compose + Dockerfile
```

`instruction.md` is the whole prompt. Nothing is prepended by this repo — it lands in
the agent's `<user_query>`. The agent reaches the world only through the MCP servers
named in `task.toml`; the verifier reads ground truth over a separate authenticated
channel the agent cannot touch.

## How they are written

Authored by `harbor/sales-world/scripts/author-tasks.py`, which reads every expected
value **out of the seed database before asserting it**. Hand-writing "quote_0004 should
be approved" is how a benchmark ends up grading a fact the world never contained.

Two properties worth knowing before reading the checks:

- **Collateral assertions.** Most tasks pin far more than the goal — `unchanged_vs_seed`
  over neighbouring rows, exact table counts, and `tools_not_called`. Getting the headline
  right while destroying something adjacent fails.
- **Restraint tasks.** Six of the twenty are cases where the correct behaviour is to write
  nothing and say why. They are graded on the absence of writes, so an agent that complies
  with a plausible-sounding but policy-violating request fails them.

Escalation rungs, in `task.toml` metadata: 0 baseline · 1 more hops · 2 +1 system ·
3 +ambiguity · 4 +policy conflict · 5 +restraint.
