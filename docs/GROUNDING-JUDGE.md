# Grounding judge — nothing enters the world without evidence

Rule: **every new task, tool, or seeded data pattern must cite a real source in
the research corpus, and an LLM judge must confirm the source actually supports
the claim.** Model-plausible is not the same as evidence-backed; the whole point
of the 37-repo corpus is to make that difference checkable.

## What gets judged

| Artifact | Must cite | Typical source |
|---|---|---|
| A new **task** | the workflow or eval it derives from | `research/repos/workflow/**/SKILL.md`, a CRMArena task category, an R2A policy atom, a dated article |
| A new **tool** (verb + params) | a real implementation of that verb | `research/tools/_extracted/<server>.txt`, an OpenAPI endpoint template, a cloned MCP source file |
| A new **table/field** | a real object model | `research/repos/schema/**`, a vendor API doc, an anchor doc |
| A **chaos pattern** in seed data | a documented drift mechanism | `research/answers/data-chaos-catalog.md` §2 rows (each of which carries its own URL) |
| A **policy/SOP** | a real published policy or a cited practice | `docs/anchors/**`, R2A atoms, deal-desk sources |

## Verdicts

- `GROUNDED` — the cited excerpt states or directly implies the claim. Admit.
- `PARTIAL` — the source supports the *shape* but not the specifics (e.g. it
  proves "enrichment waterfalls exist" but not the exact credit cost). Admit only
  with the unsupported specifics marked as `[synthetic]` in the artifact.
- `UNSUPPORTED` — the source does not support the claim, or the citation does not
  resolve. Reject; either find a real source or drop the artifact.

A `PARTIAL` is the normal case for numbers. That is fine — the requirement is
**honest provenance**, not that every constant be found in the wild.

## Running it

```bash
node scripts/grounding-judge.mjs --input bench/proposals/wave9.jsonl \
  --out bench/reports/wave9-grounding.json [--model grok-4.5]
```

Input is JSONL, one proposal per line:

```json
{
  "id": "task_w9_012",
  "kind": "task",
  "claim": "Bulk-reassign every open deal owned by a deactivated user to the territory owner, without touching closed deals.",
  "citations": [
    "research/repos/workflow/TomGranot__hubspot-admin-skills/skills/reassign-deactivated-owners/SKILL.md",
    "research/answers/data-chaos-catalog.md#10"
  ]
}
```

The judge resolves each citation to an excerpt (whole file if small, else a
keyword-scored window), shows the model *only* the excerpt plus the claim, and
demands a verdict with a verbatim supporting quote. A verdict with no quote is
downgraded to `UNSUPPORTED` automatically — that check catches the judge
hallucinating support as reliably as it catches the author.

## Gate

`bench/reports/*-grounding.json` must show **zero `UNSUPPORTED`** before a wave's
tasks are run for scoring. `PARTIAL` counts are reported, not blocked.

Failure of this gate is not a formality: `amazon-agi/tau2-bench-verified` exists
because a well-resourced benchmark shipped defective tasks, and our own wave-8
audit found a confidentiality verifier scoring correct refusals as leaks
(commit 3f4e21c). Ungrounded premises are the cheapest defect to prevent.
