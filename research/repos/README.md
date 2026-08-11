# Evidence corpus — cloned sales-domain repositories

37 repositories across four axes, cloned shallow/single-branch on 2026-08-11.
**Not tracked in git** (see `.gitignore`); regenerate with:

```bash
JOBS=10 ./scripts/clone-research-repos.sh     # reads research/repos.manifest.tsv
python3 scripts/extract-mcp-verbs.py          # -> research/tools/_extracted/
```

| Axis | Count | What it is for |
|---|---|---|
| `eval/` | 10 | Task taxonomies and verification schemes → `research/answers/eval-task-census.md` |
| `workflow/` | 12 | What practitioners actually automate → `research/answers/workflow-task-census.md` (185 skills inventoried) |
| `mcp/` | 13 | Real verb surfaces per vendor → `research/tools/_extracted/INDEX.tsv` |
| `schema/` | 2 | Real CRM object models (Twenty, Frappe CRM) |

`eval/SalesforceAIResearch__CRMArena` is a symlink to `external/CRMArena`
(already present, 336 MB of SQLite fixtures — not re-cloned).

Results table: `CLONE-LOG.tsv` (status · axis · repo · path · files · size).

Licensing: these are third-party repositories retained locally as research
evidence. Anything reused in the world must be cited (`docs/GROUNDING-JUDGE.md`)
and must respect the upstream license — check `LICENSE` in each repo before
copying code or data rather than deriving facts from it.
