# World Organization — harbor format, tools, tasks, verifiers, mock data

> Detailed map of what exists, the autopsy of why the current tool universe is wrong
> for a sales world, and the brand-true redesign. Written 2026-08-10 after the
> namespace audit; companion to CREATION-PROTOCOL.md (the process) and
> STUDIO-QA.md (the generator audit).

## 1 · The harbor format — what lives where

A blobfish world ships as one `world.json` + a self-contained runnable package.
`harbor` is the **runtime contract inside world.json** (format_version 4), not the
creation method.

```
world.json
├─ thesis          roles, entities, workflows, policies, claims   (the framing)
├─ anchors         validated schema anchors (119 in wave-6, all "ok")
├─ tables[214]     name, columns, row_count, sample_rows          (THE MOCK DATA)
├─ tools[205]      name, mcp_name, asset_namespace, type,
│                  target_tables, input_schema, source (Python!)  (THE MCP TOOLS)
├─ tasks[25]       prompt, walk, required_tools, relevant_data,
│                  expected_state_changes, provenance, coverage
├─ verifiers[25]   assertions[], vcode (Python verify()), cases
└─ harbor          runtime: server.py, sqlite, endpoints, /mcp
                   manifest, seed→state startup, training kit

package/<world_id>/
├─ server.py       stdlib HTTP: /sessions /mcp /verify/{task} ... (+ our v2 patch)
├─ tools/*.py      the SAME tool sources, bucketed into the generator's
│                  fixed namespace files (calendar core email erp github
│                  jira notion pagerduty salesforce slack stripe)  ← the screenshot
├─ create_db.py → seed.db → state.db;  .sessions/*.db (copy-on-write per episode)
└─ train/          offline RL kit

repo projections (ours)
├─ bench/tools/<world>/<vendor>/*.{json,py}   browsable tool inventory
├─ bench/tasks|verifiers|traces|failed-traces|reports
├─ mcp/vendor-server.mjs + harness-server.mjs (per-product MCP proxies)
└─ bench/tasks/<world>/<task>.seed.json       task-level fixtures (task-seed.v1)
```

Direct answers to the two questions:
- **"Why is it these tools?"** `tools/*.py` filenames are the generator's *hardcoded
  namespace skeleton* — every world gets the same buckets regardless of domain, and
  the distiller scatters mounted services into them.
- **"Why here instead of the mcp folder?"** The harbor contract makes the world
  self-executing: implementations live in the package so `server.py` can run them.
  Our `mcp/` holds only proxies. In the redesign below, sales tools we author
  ourselves live in `mcp/` as first-class mock servers with their own databases.

## 2 · Namespace autopsy — the evidence

| namespace file | what it ACTUALLY contains (wave-6) | plausible intent | verdict |
|---|---|---|---|
| `salesforce` (27) | real CRM CRUD: accounts/contacts/opportunities/cases/tasks | Salesforce | ✅ keep |
| `core` (122) | internal records/workflow sub-agents, docs, sheets, memories | internal platform | ✅ keep (rename "revops-core") |
| `stripe` (7) | charges/invoices/disputes — plus deprecated `post_charges`, invoice-template + payment-intent line-item trivia; **no subscriptions/customers** | Stripe | ⚠️ wrong slice of the surface |
| `jira` (5) | support tickets + customer-support agents | Intercom/support | ❌ mislabeled |
| `pagerduty` (5) | cases + **billing alerts** | support?? billing?? | ❌ incoherent bucket |
| `erp` (7) | purchase orders + **`admin_emoji_list` (a Slack emoji tool)** | NetSuite | ❌ contaminated |
| `github` (6) | sheet agent + **finance expense-report tools** | Sheets/exports | ❌ mislabeled |
| `email` (3) | org-records agents + one SendGrid category-stats read | SendGrid | ❌ 1/3 relevant |
| `slack` (7) | admin conversation prefs, EKM, IDP groups — **no message send** | Slack | ❌ admin trivia, not messaging |
| `calendar` (10) | calendar ACL rules + agent_scheduled_runs — **no availability/booking** | Google Calendar | ❌ wrong slice |
| `notion` (6) | documents/matter documents/files | knowledge base | ✅ keep |

Three root causes, all generator-side (reported in STUDIO-QA.md):
1. **Fixed namespace skeleton** — the same 12 buckets are emitted for every world.
2. **Curated-pick selects admin surfaces** — the distiller favored seeded-entity
   tables and landed on `admin.emoji.list`, calendar ACLs, and Slack EKM instead of
   `send_message`, `book_meeting`, `create_subscription` — the verbs sellers use.
3. **Domain-blind bucketing** — Intercom ops under `pagerduty`/`jira`, sheets under
   `github`, one SendGrid read under `email`.

**Verdict: not shippable as a sales world.** Renaming proxies cannot repair a tool
universe whose operations are the wrong verbs.

## 3 · The redesign — a sales-driven tool universe

Per CREATION-PROTOCOL: research each real product's MCP/API surface, then mock it as
**our own MCP server in `mcp/servers/<product>/`** with **its own database file** —
data chaos by construction, since the same business entities live (inconsistently)
in several stores.

| MCP server | mocks | own store | core verbs (researched, not invented) |
|---|---|---|---|
| `salesforce-crm` | Salesforce Sales Cloud | `db/salesforce.db` | SOQL-ish query, lead/opp/case CRUD, convert_lead, log_activity |
| `hubspot-crm` | HubSpot | `db/hubspot.db` | contacts/companies/deals CRUD, pipelines, engagements, lists |
| `gong` | Gong | `db/gong.db` | list_calls, get_transcript, get_call_insights (MEDDIC/trackers), search |
| `granola` | Granola | `db/granola.db` | meeting notes: list_meetings, get_notes, action_items |
| `apollo` | Apollo.io | `db/apollo.db` | search_people/companies, enrich, sequences, email_verify |
| `outreach` | Outreach | `db/outreach.db` | sequences, enroll, reply classification, mailbox stats |
| `google-sheets` | Sheets | `files/*.csv` | read_range, append_row, find — the shadow-CRM spreadsheet |
| `google-drive` | Drive | `files/` | list/search/read docs — MSAs, order forms, decks |
| `gmail` | Gmail | `db/gmail.db` | threads, search, send (logged), labels |
| `google-calendar` | Calendar | `db/gcal.db` | availability, create_event, round-robin |
| `stripe-billing` | Stripe | `db/stripe.db` | customers, subscriptions, invoices, dunning |
| `docusign` | DocuSign | `db/docusign.db` | create_envelope, status, countersign |
| `slack` | Slack | `db/slack.db` | post_message, channels, history — messaging, not admin |
| `revops-core` | internal platform | world DB | keep the blobfish core (docs/sheets/sub-agents) |

**Data-chaos matrix** (the "what's total sales this week?" design): accounts exist in
salesforce AND hubspot (owner + spelling conflicts), some deals only in the
spreadsheet, invoices in stripe not yet synced to CRM, meeting outcomes only in
gong/granola. Reconciliation tasks are verifiable because each store is a separate
DB whose union has one seeded ground truth. Chaos scenarios come from research
(sync lag, duplicate leads, partial migration off HubSpot, rep-maintained sheet).

**Migration path** (each step shippable):
1. **Re-slice** the existing 205 tools into truthful servers by explicit tool→server
   mapping (not namespace), quarantining the admin-trivia tools out of the agent
   surface.
2. **Author** the missing sales servers from per-product research
   (`research/tools/<product>.md`: official MCP docs, OpenAPI, usage workflows) —
   start with hubspot-crm, gong, apollo, google-sheets, slack-messaging.
3. **Fragment** the data across stores + write reconciliation tasks; verifier reads
   all stores via the harness (initial-state override already supports multi-store
   baselines).
4. **Wave-7 generation** feeds the researched tool specs back to blobfish as
   `mock_services`/anchors — or bypasses generation for tools entirely and uses
   blobfish only for tables/tasks/verifiers over our tool surface.

## 4 · Tasks & verifiers organization (unchanged, works)

- `bench/tasks/<world>/task_XXX.json` + `.seed.json` (per-task fixtures: rows,
  documents, input docs, per-vendor seeding — verifier-safe via the v2 patch)
- `bench/verifiers/<world>/task_XXX.py` + `.meta.json`
- Task ladder + audit-before-blame per CREATION-PROTOCOL §5 (3 strikes → parked
  with env-fault check; flaky = the frontier; first-pass → escalate depth).

## 5 · Known generator bugs feeding upstream

See docs/STUDIO-QA.md — the running list (SSE-reconnect executor race, 25-min
assemble_calibrate ceiling, duplicate `required` schema entries, doc-text loss
during ingestion, unexpanded `{name}` templates, verifier row mispinning, stale
arena GT, namespace skeleton + admin-surface distillation above).
