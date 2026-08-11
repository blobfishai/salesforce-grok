# Ingestion protocol — turning domain repos into world content

How an arbitrary sales-domain repository becomes runnable content in the
simulation world: its **tools**, **seed data**, **tasks**, **workflows** and
**verifiers**, with provenance, and with an explicit record of what could *not*
be ported.

The rule this protocol exists to enforce:

> **Never approximate silently.** An adapter that cannot port something
> faithfully must refuse it and say so in `refusals[]`. A coverage number is a
> measurement, not a judgement.

That rule is written in blood. `docs/TASK-COVERAGE.md` originally claimed "19 of
22 CRMArena categories are expressible" — a judgement made by reading, not
running; only 2 actually executed. And the first SOQL shim returned the literal
string `COUNT(Id)` where a count belonged, which would have corrupted every
measurement built on top of it.

---

## 1. The five things a repo can contribute

| contribution | what it is | where it usually lives |
|---|---|---|
| **tools** | callable verbs with input schemas | MCP servers, SDK clients, `functions.py` |
| **tables** | seed data + schema | SQLite mirrors, `db.json`, fixtures, doctype defs |
| **tasks** | prompts with ground truth | `tasks.json(l)`, HF datasets, `tasks_test.py` |
| **policies** | rules the agent must obey | `policy.md`, `wiki.md`, policy-atom YAML |
| **workflows** | ordered procedures practitioners run | `SKILL.md`, playbooks, LangGraph nodes |

## 2. The normalized intermediate: a World Contribution Package (WCP)

Every adapter emits one JSON document per source repo. Nothing downstream ever
reads a repo directly — only WCPs — so adding a source never touches the
importer.

```jsonc
{
  "source":   { "repo", "commit", "path", "url", "license" },
  "adapter":  { "name", "version" },
  "fidelity": "exact | adapted | inspired",
  "tables":   [ { "name", "columns": [...], "row_count", "rows_path" } ],
  "tools":    [ { "name", "namespace", "description", "input_schema", "binding" } ],
  "policies": [ { "id", "text", "severity", "hard_fail" } ],
  "tasks":    [ { "id", "prompt", "context", "tags", "verifier": { ... } } ],
  "refusals": [ { "kind", "what", "why", "count" } ]
}
```

### Fidelity levels — reported per task, never averaged away

| level | meaning | claim it supports |
|---|---|---|
| `exact` | the source's own data, prompt and verifier all run unmodified | "we reproduce benchmark X" — comparable to its published numbers |
| `adapted` | same task and ground truth, our tool surface or schema | "we cover the capability X tests" |
| `inspired` | authored from the source; no ground truth carried over | "grounded in X" — nothing more |

The 16 hand-authored tasks in `harbor/sales-world` are `inspired`. Saying so is
the point.

### Verifier archetypes

The corpus reduces to three, which the world already supports:

| archetype | ground truth | how it is checked here |
|---|---|---|
| `answer_match` | expected string + metric (`exact` / `fuzzy`) | agent writes its answer; verifier compares |
| `action_trace` | required tool calls with argument subsets | `/verifier/trace` — the same endpoint that catches false completion |
| `state_assert` | rows that must / must not change | `/verifier/query`, incl. `db:"seed"` collateral diffs |

## 3. The pipeline

```
  research/repos/<axis>/<repo>            383 cloned repos
            │
            ▼  scripts/ingest/ingest.py --adapter <name>
  research/parity/wcp/<repo>.json         World Contribution Packages
            │                              (+ refusals[], + provenance)
            ├─► scripts/ingest/report.py  → docs/INGESTION-REPORT.md
            │
            ▼  scripts/ingest/compile_tasks.py
  harbor/<dataset>/tasks.spec.jsonl       → gen-tasks.py → Harbor tasks
            │
            ▼  harbor run -a oracle       the gate: below 1.000 is our defect
```

Four gates, in order, none skippable:

1. **License gate** — an adapter records the source licence and refuses to vendor
   data or code whose licence does not permit it. Deriving *facts* is always fine.
2. **Fidelity gate** — every task is stamped `exact`/`adapted`/`inspired`.
3. **Oracle gate** — a compiled task whose reference solution does not score
   1.000 is our defect, not the model's.
4. **Grounding gate** — `scripts/grounding-judge.mjs` checks the cited excerpt
   actually supports the claim (`docs/GROUNDING-JUDGE.md`).

## 4. Adapters

An adapter is a function `(repo_dir) -> WCP`. It must:

- emit provenance for every artifact (repo + commit + path),
- stamp a fidelity level,
- append to `refusals[]` for anything it cannot port faithfully, with a count,
- never invent a value that the source did not contain.

| adapter | shape it handles | repos it covers |
|---|---|---|
| `crmarena` | HF task JSON + SQLite org mirror + SOQL tool surface | CRMArena, CRMArena-Pro |
| `taubench` | `Task(...)` literals with required `Action` sequences | tau-bench (retail, airline) |
| `tau2` | `tasks.json` + `policy.md` + `db.json` | tau2-bench (4 domains), tau2-verified |
| `mcp_server` | tool declarations in TS/JS/Python/Rust | 42 vendor MCP servers |
| `skillpack` | `SKILL.md` frontmatter + steps | 185 practitioner skills |
| `r2a` | policy-atom YAML + pressure schedules | R2A-Sales |
| `crm_schema` | doctype / entity definitions | Twenty, Frappe CRM, EspoCRM, … |

Adding a source is: pick the shape, point the adapter at the clone, run the four
gates. Only genuinely new shapes need new code.

## 5. What "reproduce it in the world" means concretely

For a benchmark to run at `exact` fidelity the world must serve three things:

1. **its data** — mount the source's own tables, unmodified;
2. **its tool surface** — the verbs its tasks assume, with matching semantics
   (for CRMArena that meant a SOQL shim, since its tools call a live org);
3. **its verifier** — its own metric, not a re-interpretation.

Where any of the three cannot be met, the task drops to `adapted` or is refused —
and the count appears in `docs/INGESTION-REPORT.md` rather than being rounded up
into a coverage claim.
