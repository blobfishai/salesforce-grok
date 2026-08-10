# Vendor tool-spec format (wave-6 densification)

One JSON file per vendor server: `world/blobfish-wave6/tool-specs/<vendor>.json`.
Consumed by `scripts/densify-vendor-tools.mjs`, which generates the Python tool
source (param-respecting SQL against SQLite), the friction wrapper, the
`world.json` tool + table entries, `tools/<ns>.py`, `tools.py`, and
`mcp-assets.json`. Check `_constraints.json` for names already taken.

```json
{
  "vendor": "slack",                  // key in config/mcp-servers.json
  "namespace": "slack",               // asset_namespace / tools/<ns>.py module
  "tables": [                          // NEW tables only (existing ones just get referenced)
    {
      "name": "slack_users",
      "columns": [
        {"name": "id",   "type": "TEXT", "pk": true},
        {"name": "name", "type": "TEXT"}
      ],
      "sample_rows": [ {"id": "U01AAA01", "name": "mei.huang"} ]   // 6-15 realistic rows
    }
  ],
  "tools": [ <tool>, ... ]
}
```

## Tool entry

Common fields (all ops):

| field | req | meaning |
|---|---|---|
| `name` | ✔ | globally-unique bare tool name (see naming rules in `_constraints.json`) |
| `description` | ✔ | one line, ending with the real endpoint: `"... (GET /users.list)"` |
| `op` | ✔ | `list` \| `get` \| `create` \| `update` \| `delete` \| `search` \| `custom` |
| `table` | ✔ | primary backing table (new-in-this-spec or existing) |
| `params` | ✔ | `{name: {"type": "string"|"integer"|"number"|"boolean"|"object", "description": "..."}}` — real API param names + real doc text |
| `required` | | array of required param names |
| `extra_tables` | | additional tables read/written (for `target_tables`) |

Per-op fields:

- **list** — `filters`: params that become `WHERE col = ?` (param name == column
  name, or use `filter_map: {param: column}`). A `limit` param is honored
  automatically (default 30).
- **get** — `id_param` (✔), `id_column` (default `id`). Returns 404 error object
  when no row matches THE GIVEN id (never "first row" fallbacks).
- **create** — `fields`: params written as columns; `defaults`: `{col: literal}`
  server-side values; `id_prefix` (e.g. `"pi_"`, `"PD-"`); `created_at` column is
  auto-filled when the table has one. Returns the created row.
- **update** — `id_param` (✔), `id_column`, `set_fields`: params written if
  provided. 404 when no match. Returns the updated row.
- **delete** — `id_param` (✔), `id_column`. 404 when no match.
- **search** — `query_param` (default `query`, required), `search_columns`:
  `LIKE '%q%'` OR-match columns; optional `filters` as in list.
- **custom** — `custom_source`: the COMPLETE Python function
  (`def <name>(db_path='state.db', **kwargs):` ... using only sqlite3/json/
  datetime/hashlib), plus explicit `"type": "read"|"write"`. Use for semantics
  the patterns can't express (freebusy, ack/resolve transitions, message posting
  with thread ts, etc.). Keep it param-respecting and parameterized SQL only.

## Quality bar

- Mirror the REAL vendor API/MCP surface: real method names, real param names,
  real doc phrasing, plausible ID formats (`U0…`/`C0…` Slack, `cus_`/`pi_`
  Stripe, `PROJ-123` Jira, `P…` PagerDuty, uuid-ish Notion).
- Sample rows must be world-coherent: reuse Morgan Stanley (SIMULATED) entities —
  accounts like Summit Group / Riverside Group / Meridian / Ironwood /
  Harborview / Atlas / Crestline; employees like Mei Huang (SDR), Sarah Kim
  (Recruiter); emails `…@morganstanleysimulated.com`. All data synthetic.
- Every tool must be executable against the DB and respect every wired param.
- 20-30 tools per vendor; balanced read/write mix; cover the workflows an agent
  actually does with that product.
