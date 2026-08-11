# sales-world — a Harbor dataset for B2B revenue work

> **Simulation only.** Every account, contact, deal, and figure is synthetic test
> data. Not affiliated with, endorsed by, or representative of any real company.

A simulated B2B software company — 313 tables, 453 tools across 11 vendor
systems — packaged as a [Harbor](https://github.com/harbor-framework/harbor)
dataset. Agents meet it the way a new hire does: through Salesforce, NetSuite,
Jira, Slack, Gong-style call data and a dozen other servers that disagree with
each other.

## Why this exists

Public CRM benchmarks test single-system competence. CRMArena-Pro's 22 task
categories all run against one Salesforce org; τ-bench domains are one `db.json`
each; SCUBA is 300 tasks inside one Salesforce UI. Meanwhile the field reports
15–25% duplicate rates, 76% of records less than half complete, and CRM deal
amounts that *"rarely match recognized revenue"*.

So the tasks here put the chaos in the middle of the work, not around it — an
ERP that keys orders on an internal customer entity whose name only loosely
matches the CRM account, invoices raised with no source order, forecasts carried
in the wrong category after quota was already cleared.

Full derivation: [`research/THESIS.md`](../../research/THESIS.md), sourced from a
381-repo evidence corpus ([`research/SOURCES.md`](../../research/SOURCES.md)).

## Quickstart

```bash
pip install harbor                              # or: uv tool install harbor
./scripts/build-images.sh                       # builds sales-world:w6 + gateway

harbor run -p tasks -a oracle                   # reference solutions, expect 1.000
harbor run -p tasks -a claude-code -m anthropic/claude-sonnet-4-5 -k 2
```

Results land in Harbor's standard layout: `jobs/<name>/<trial>/verifier/`
carrying `reward.txt`, `ctrf.json`, and a `checks_detail.json` naming every
business assertion that passed or failed.

## The tasks

| task | family | rung | vendors | checks |
|---|---|---|---|---|
| `deal-desk-quote-triage` | deal desk | 0 | salesforce | 9 |
| `forecast-category-correction` | forecast | 1 | salesforce | 6 |
| `merge-duplicate-leads` | CRM hygiene | 1 | salesforce | 7 |
| `stop-bounced-sequences` | outbound hygiene | 1 | salesforce | 6 |
| `quote-to-order-activation` | quote-to-cash | 2 | salesforce + erp | 8 |
| `unlinked-invoice-reconciliation` | reconciliation | 2 | erp + jira | 8 |
| `restraint-unverifiable-discount-request` | restraint | 5 | salesforce | 5 |
| `restraint-bulk-lead-purge` | restraint | 5 | salesforce | 5 |

**Rung** is the escalation axis a task occupies relative to its seed task:
1 more hops · 2 +1 system · 3 +ambiguity · 4 +policy conflict · 5 +restraint.
Tasks a model solves first try get escalated a rung; tasks it fails three times
running are recorded as too hard and left alone. Flaky tasks are the frontier and
are kept.

Two of these have no equivalent in any public eval: `quote-to-order-activation`
and `unlinked-invoice-reconciliation` both require reconciling two systems of
record that were never designed to agree.

The restraint tasks grade *negative* assertions — the correct behaviour is to
write nothing and explain why. They are only meaningful because the world ships
the destructive tools to refuse: `lead_delete`, `account_delete`,
`opportunity_delete` and friends exist precisely so declining to use them counts.

## How it fits together

```
  agent container (main)                  one MCP server per vendor
  ┌────────────────────┐        ┌──────────────┐  ┌──────────────┐
  │ claude-code /      │◄──MCP──┤ salesforce   │  │ erp          │  ...
  │ codex / oracle     │        │ gateway:8000 │  │ gateway:8000 │
  └─────────┬──────────┘        └──────┬───────┘  └──────┬───────┘
            │                          │ JSON-RPC        │
            │                          ▼                 ▼
            │                   ┌─────────────────────────────┐
  verifier ─┴──/verifier/query─►│ sales-world:w6              │
   (SELECT only, token-gated)   │ 313 tables · 453 tools      │
                                │ state.db (mutable) + seed.db│
                                └─────────────────────────────┘
```

- **The gateway** exists because the world namespaces its tools
  (`salesforce.lead_merge`) while real agents meet Salesforce and NetSuite as
  separate servers with bare names. One container per vendor filters a single
  namespace and re-qualifies on call.
- **Grading reads the database**, not the MCP tools the agent used — otherwise a
  single tool bug fails a correct trajectory. The verifier token lives in
  `[verifier.env]` only, so the agent cannot reach the answer key, and the
  endpoint refuses anything that is not `SELECT`/`WITH`.
- **`db: "seed"`** re-runs any check against the untouched world, which is how
  collateral guards are written: *these rows must look exactly as they did*.
- **Partial credit**: `reward.txt` carries the fraction of checks passed. A
  long-horizon task that got 7 of 9 assertions right is genuinely different from
  one that did nothing, and the difference is the signal a frontier program wants.

## Authoring more tasks

```bash
python3 scripts/probe-world.py --db <seed.db>   # -> world-facts.md, real ids and values
python3 scripts/author-tasks.py                 # -> tasks.spec.jsonl, checks computed from the world
python3 scripts/gen-tasks.py --clean            # -> tasks/, Harbor task dirs
harbor run -p tasks -a oracle                   # the gate: anything below 1.000 is our bug
```

Every expected value is read out of the world before it is asserted. Writing
"quote_0004 should be approved" from memory is how a benchmark ends up grading a
fact the world never contained — the defect class `amazon-agi/tau2-bench-verified`
exists to correct. The oracle gate has already caught three such defects here,
before any model was billed for them.

New tasks must also cite a source in the research corpus and clear the grounding
judge ([`docs/GROUNDING-JUDGE.md`](../../docs/GROUNDING-JUDGE.md)), which shows
the judge only the claim and the cited excerpt and demands a verbatim quote.

## Coverage

[`docs/TOOL-COVERAGE.md`](../../docs/TOOL-COVERAGE.md) measures the world's tool
surface against every verb extracted from 42 cloned vendor MCP servers, matched
on a normalized `action:object` form so HubSpot's *deal* and Salesforce's
*opportunity* count as the same object. Currently **51%** of the corpus verb
surface, with the uncovered verbs ranked by how many independent servers ship
them — that ranking is the densification backlog.
