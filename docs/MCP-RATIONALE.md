# Why each vendor MCP exists — proof, thesis linkage, real-vs-mock diff

> Written 2026-08-10. Every claim below is traceable to an artifact in this repo:
> the world's authored thesis (`world.json.prompt` / `world.json.thesis`), the
> mock-service provenance records (`world.json.mock_service_specs`, with the real
> spec URLs and operation counts), the per-asset attestation digests
> (`mcp-assets.json`: `behavior_digest`, `tenant_seed_digest`), the demand census
> (`data/coverage/census-items.json`, 171 items), and the mounted tool inventory
> (`bench/tools/wave6/INDEX.md`, 205 tools).

## The proof chain

1. **The thesis names the stack.** The world prompt is not vendor-agnostic — it
   enumerates 19 lifecycle legs and names the archetype for each: *"outbound
   email sequencing … on SendGrid-style email infrastructure"* (leg 3), *"meeting
   scheduling with round-robin assignment on Google Calendar"* (leg 5), *"CRM core
   lead→contact→account→opportunity→quote→order in Salesforce"* (leg 6),
   *"Stripe-style billing: subscriptions, invoices, payments, a dunning ladder"*
   (leg 9), *"support cases with SLA tiers on Intercom-style ticketing"* (leg 12),
   plus *"Slack-style deal-room messaging carries approvals and escalations"*,
   *"a Notion-style knowledge base holds the SOP corpus"*, and *"NetSuite-style
   order records reconcile billing"*. Each vendor server is the executable form of
   a named leg.
2. **Mocks were mounted from the real vendors' machine-readable specs.**
   `world.json.mock_service_specs` records, per service, the exact source spec,
   its format, its SHA-256, and its operation count (table below). The tool
   schemas an agent sees are cut from the same OpenAPI/discovery documents the
   real products publish.
3. **Each mounted asset carries attestation digests.** `mcp-assets.json` pins a
   `behavior_digest` (the generated tool module) and `tenant_seed_digest` (the
   seeded data) per namespace — the mock's identity is auditable, not vibes.
4. **Demand was measured, not assumed.** The 171-item coverage census
   (CRMArena/-Pro task types, tau-bench-class benchmarks, the AI-SDR ecosystem,
   RevOps workflow canon) is the demand side; `docs/COVERAGE.md` matches it
   against this inventory (44 covered / 96 partial / 11 gaps). The vendors below
   are the supply side for that demand.

## The stack at a glance

| vendor server | thesis leg (prompt) | real spec mounted from | real ops | before densification | after (live) |
|---|---|---|---|---|---|
| salesforce-crm | (6) CRM core, (7) CPQ approvals | synthetic "Enterprise Twin" domain template (`blobfish://service-forge/domain-template/salesforce/v1`) | 30 | 27 | 23 |
| stripe-billing | (9) billing, dunning, refunds, proration | **Stripe's official OpenAPI** (`stripe/openapi/spec3.json`) | **587** | 7 | 38 |
| sendgrid-email | (3) outbound sequencing, (14) suppression/consent | **SendGrid OpenAPI** (apis.guru mirror) | 334 | 3 | 33 |
| slack | deal-room messaging, approvals, escalations | **Slack's official Web API spec** (`slackapi/slack-api-specs`) | 174 | 7 | 34 |
| google-calendar | (5) scheduling, round-robin | **Google's Calendar v3 discovery doc** | 38 | 10 | 26 |
| netsuite-erp | order reconciliation vs billing | synthetic "Enterprise Twin" template | 30 | 7 | 29 |
| revops-core | (11) CS health, (13) quota/comp, (17) analytics, (18) hygiene | **Intercom's official OpenAPI 2.15** absorbed as the internal platform + forged company tables | 161 | 122 | 104 |
| jira | (12) internal ticketing | none — identity-mapped (see "honest weak spots") | — | 5 | 32 |
| pagerduty-support | (12) escalation/paging | none — identity-mapped | — | 5 | 29 |
| notion-docs | SOP corpus / knowledge base | none — identity-mapped | — | 6 | 26 |
| github | (17)/(18) RevOps tooling, sheets/exports | none — identity-mapped | — | 6 | 33 |

*After = the landed densification pass (`world/blobfish-wave6/tool-specs/` +
`scripts/densify-vendor-tools.py`): 228 real-API tools added with 1:1 request
params AND 1:1 vendor response envelopes, 26 domain-irrelevant tools pruned
(ledger: `tool-specs/_pruned.json`), 407 tools / 293 tables total, every added
tool smoke-tested (228/228). "Before" counts that shrank (salesforce 27→23,
revops-core 122→104) reflect the prune. Reference point: grafana/mcp-grafana
ships ~40 tools on one server.

## Per-vendor rationale

### salesforce-crm — the system of record (the thesis IS a CRM world)
- **Proof of choice.** `company_type_key: "saas:crm"`; the census keyword "CRM"
  appears 317× across the 171 demand items; CRMArena/-Pro — the incumbent
  benchmark this world outgrows (`docs/COMPARISON.md`) — is Salesforce-native.
  Choosing any other CRM would have severed comparability.
- **Thesis role.** Legs 6-7: every cross-system invariant starts here
  (closed-won opportunity ⇒ executed order form ⇒ activated order ⇒ subscription
  ⇒ invoice). The verifiers' core state-diff assertions live on its tables.
- **Real vs mock.** Real Salesforce is not an OpenAPI surface — it's SOQL/SOSL +
  a metadata-driven REST describe layer; the twin template (30 ops) models the
  workflows, not the metadata engine. Mock lacks SOQL (typed query tools
  instead), triggers/flows, field-level security. The separate legacy
  `mcp/salesforce-crm-server.mjs` keeps a SOQL-subset mock for comparison runs.

### stripe-billing — money movement makes state verification real
- **Proof of choice.** Mounted from Stripe's own `spec3.json` (587 operations,
  sha-pinned). The world's billing tables (`charges`, `invoices`, `disputes`,
  `balance_transactions`, `billing_object_mapping_stripe_style`) are cut from it.
- **Thesis role.** Leg 9 is the *far end* of the flagship invariant chain — an
  agent that "closes a deal" but leaves billing unreconciled fails the verifier.
  Dunning-ladder and refund/credit policies give the SOP corpus teeth.
- **Real vs mock.** 7 of 587 ops mounted (1.2%) — reads on charges/invoices/
  disputes plus charge-create and dispute-close. No subscriptions, no payment
  intents, no refunds, no payment links (all named "missing" in COVERAGE.md's
  partials). The densification spec adds exactly those (~37 tools, ~6% of the
  real surface — comparable to Stripe's real agent-toolkit MCP, which exposes
  ~20 curated tools, not all 587 ops).

### sendgrid-email — the outbound channel the coverage audit calls its #1 gap
- **Proof of choice.** Mounted from the SendGrid OpenAPI (334 ops); "email"
  scores 195 census mentions — the AI-SDR ecosystem (sequencing, deliverability,
  suppression) is the single largest demand cluster outside the CRM itself.
- **Thesis role.** Legs 3 and 14: sequencing, reply classification, consent and
  suppression lists. COVERAGE.md's prioritized roadmap item #1 — *"Outbound send
  channel (~15 partials): a logged send_email write tool + outbound_messages
  table. Biggest single unlock"* — lands in this vendor's densification spec
  (`post_mail_send` + `sg_mail_sends` log).
- **Real vs mock.** Wave 6 mounts only 3 tools (stats + two sub-agents); several
  SendGrid-shaped surfaces (singlesends, suppression reads, tracking settings)
  were absorbed into revops-core namespaces instead. Fidelity gap: no actual
  SMTP semantics, no webhook events; suppression tables are read-only until the
  densified write tools land.

### slack — where approvals and escalations become observable
- **Proof of choice.** Mounted from Slack's official web-api spec (174 methods);
  the world seeds a `deal_room_channels_slack_style` table; the SOP corpus
  mandates approval sequences (Deal Desk → Compliance → Finance) that travel as
  deal-room messages.
- **Thesis role.** The prompt: *"Slack-style deal-room messaging carries
  approvals and escalations."* Verifiers assert approval ORDER from the trace —
  the channel that carries approvals must exist as a first-class system.
- **Real vs mock.** 7 of 174 methods (4%), skewed to admin-conversation reads;
  `messages` was read-only until densification (COVERAGE.md named the missing
  message-post tool in ~6 partials) — `chat_post_message` now exists and returns
  real Slack envelopes (`{"ok": true, "ts": ...}` / `channel_not_found`). The
  param-ignoring `admin_conversations_get_conversation_prefs` fidelity bug was
  resolved by pruning the tool (config noise). Live surface: 34 tools.

### google-calendar — scheduling is a measurable SLA, not a nicety
- **Proof of choice.** Mounted from Google's own discovery document (38 methods
  — the real API is genuinely small); the world carries a
  `meeting_scheduling_sla` policy table and a `meeting_types_and_durations`
  fixture; "calendar" hits 20 census items (meeting booking, prep/follow-up,
  round-robin routing).
- **Thesis role.** Leg 5; meeting-booking workflows are among the 44 *covered*
  census capabilities today (calendar_agent + agent_events + SLA doc).
- **Real vs mock.** 10 of 38 methods (26% — the deepest real-spec coverage in
  the stack). Missing: events CRUD granularity (list/insert exist only via the
  agent-style tools), freebusy, ACL writes — all in the densified spec (~25).

### netsuite-erp — the reconciliation counterparty
- **Proof of choice.** Enterprise-twin template (30 ops); the thesis demands
  *"NetSuite-style order records reconcile billing"* — an invariant needs two
  sides, and ERP is the second ledger.
- **Thesis role.** Order activation, PO three-way-match, journal reconciliation;
  the sourcing/finance handoff chains (`company_sourcing_handoffs` →
  `purchase_orders` → `journal_entries`) terminate here.
- **Real vs mock.** Real NetSuite is SuiteTalk/SuiteQL — schema-driven, not a
  public OpenAPI; the twin models the record types agents actually touch. The
  landed densification spec (23 tools, 9 `erp_` tables) adds SO lifecycle with
  status-transition validation, vendor-bill approval, payment application with
  overpayment/currency guards, and a planted three-way-match fixture
  (BILL-3006 ↔ purchase_order_004).

### revops-core — the Intercom spec wearing the company's own badge
- **Proof of choice.** Intercom's official OpenAPI 2.15 (161 ops) is in
  `mock_service_specs`, but no "intercom" vendor exists in
  `config/mcp-servers.json` — its operations (admins, conversations, articles,
  collections, news items, away-status) are recognizably the backbone of
  revops-core's 122 tools, fused with forged company tables (HR, finance,
  handoffs, knowledge, memories).
- **Thesis role.** Legs 11, 13, 17, 18 — plus leg 12's ticketing demand, which
  the prompt assigns to "Intercom-style ticketing." It is deliberately the
  distractor-mass server: tool *selection* under 122-tool pressure is itself
  part of the eval (the measured failure signature lives at ≥11 tool calls).
- **Real vs mock.** Intercom's conversation model (parts, assignment rules,
  SLAs) is flattened to typed table reads; the internal-platform half has no
  real-world counterpart by design (every company's internal tooling is bespoke).

### jira / pagerduty-support / notion-docs / github — identity-mapped, and said so
- **Proof of choice.** These four have **no external spec provenance** — they are
  world namespaces given real product identities in `config/mcp-servers.json`
  (commit 7b0f0bb, "one MCP server per vendor — realistic topology") because the
  simulated company would credibly run them: internal ticketing (Jira),
  escalation paging (PagerDuty), SOP knowledge base (Notion — the prompt names
  it), RevOps engineering surface (GitHub). The census supports the *functions*
  (escalation: 24 mentions; documents: 164) rather than the brands.
- **Thesis role.** Support-SLA and escalation workflows (leg 12), the SOP corpus
  that makes documents the difficulty lever, and the sheets/exports surface
  RevOps tasks write into.
- **Real vs mock.** This is the honest weak spot: today their tool surfaces are
  internal-domain tools wearing vendor names (jira = support_tickets ops,
  pagerduty = cases/billing_alerts, github = expense/sheets, notion = document
  store) — nothing like the real products' MCP servers (github-mcp-server ~40
  tools, mcp-atlassian ~30). The in-flight densification closes exactly this:
  real-API-shaped surfaces (JQL-ish search, issue transitions, incident
  ack/resolve, PR merge, block-level page editing) backed by new `jira_`/`pd_`/
  `gh_`/`notion_` tables — now landed: jira 32, pagerduty 29, github 33,
  notion 26 tools, each smoke-tested with its vendor's real response format.

## Cross-cutting real-vs-mock diffs (all vendors)

| dimension | real vendor | this world's mock |
|---|---|---|
| Auth | OAuth2 / API keys / scopes | none — session header on the world server (auth is not what's being measured) |
| Transport | HTTPS REST + webhooks/events | MCP (stdio per vendor; JSON-RPC to the world upstream) |
| Tenancy/state | live multi-tenant SaaS | copy-on-write SQLite per session (`session_isolation: copy_on_write_sqlite`), 214+ tables, deterministic resets |
| Failure modes | real rate limits, partial outages | deterministic friction: 3% of calls fail retryably, keyed by sha256(call signature) — reproducible across runs |
| Pagination | cursors (`starting_after`, `next_cursor`) | declared in schemas, mostly collapsed to `limit` |
| Eventing | webhooks, event buses | none (leg 18's "webhook event bus" is a named roadmap gap) |
| Data | live tenant data | seeded synthetic Morgan Stanley (SIMULATED) fixtures with planted task hooks and 500-row distractor mass |
| Verification | none (you trust the vendor) | every write is verifiable: state-diff + trace assertions, no LLM judge |

## Post-densification validation (measured 2026-08-10)

Flash re-sweep on the 407-tool world (25 tasks × 2 trials, deepseek-v4-flash,
$7.20, 0 infra errors — `data/flake/w6-densified-flash.json`) vs the
205-tool baseline (`w6-flash-validation.json`, $3.18):

- **Task outcomes identical**: same 15 solid-pass, same 10 solid-fail, 0 flaky
  on both sides — densification preserved benchmark comparability at the
  reference tier.
- **Depth frontier unchanged**: 1-5 calls 87% (was 88%), 21+ calls 0% (both).
- **Distractor drag is real**: already-failing deep tasks wander much further
  on the doubled surface (task_004 47→75.5 avg calls, task_006 54.5→83.5,
  task_007 45.5→81.5) and per-sweep cost doubled from the larger per-turn tool
  context. Whether the frontier model's flicker band moves at 407 tools is the
  open question for the next grok-4.5 sweep.

## The one-sentence answer

Each vendor server exists because the thesis prompt names its lifecycle leg, its
schemas are provably cut from the real vendor's published spec wherever one
exists (URLs + SHA digests in `world.json`/`mcp-assets.json`), the coverage
census quantifies the demand it serves, and where the mapping is identity-only
(jira/pagerduty/notion/github) this document says so — and the landed
densification pass (407 tools, 1:1 params and response envelopes, 26 noise tools
pruned) is what closed that fidelity gap.
