# The real sales-agent tool landscape — categories, competitors, and what we mock

> Answers QUESTIONS.md #5/#6 (tool universe) at the landscape level. Synthesized
> 2026-08-10 from assistant domain knowledge (cutoff 2026-01); per the research
> protocol, category leaders should be re-verified against current pricing/G2
> data before any wave-7 mock is built. Mock-status column references
> `config/mcp-servers.json` and `docs/MCP-RATIONALE.md`.

## Category map

| category | leaders (competitors to each other) | what sellers do there | our mock status |
|---|---|---|---|
| CRM (system of record) | **Salesforce**, HubSpot, Microsoft Dynamics 365, Pipedrive, Zoho, Attio | pipeline, accounts, stage moves, forecasts roll up from here | **mocked** (salesforce-crm, 27 tools) + legacy SOQL-subset server |
| Sales engagement / sequencing | **Outreach**, Salesloft, Apollo.io (engagement half), Groove, Reply.io, Instantly, Smartlead | multi-step email/call/social cadences, reply triage, A/B steps | partial — sequencing policy tables + singlesends exist; send channel lands with sendgrid-email densification |
| Data / enrichment | **ZoomInfo**, Apollo.io (data half), Clearbit (HubSpot Breeze), Cognism, Lusha, **Clay** (orchestration) | list building, firmographic/contact enrichment, waterfalls with credit budgets | gap-by-design — enrichment-waterfall SOP + `tech_signals` exist; no provider tools (COVERAGE roadmap #5) |
| Intent / ABM signals | 6sense, Bombora, Demandbase, RB2B | account prioritization from intent topics | out of scope (needs external-web surrogate) |
| Conversation intelligence | **Gong**, Chorus (ZoomInfo), Clari Copilot, Granola (notes) | call recording→transcript→MEDDIC/BANT extraction, coaching | partial — 2 anchor transcripts, `meddic_scorecard`, `tracker_keywords`, `disposition_codes`; corpus depth is COVERAGE roadmap #2 |
| Scheduling | Calendly, **Chili Piper** (routing), Google Calendar underneath | round-robin routing, speed-to-lead booking | **mocked** (google-calendar; densification adds events CRUD + freebusy) |
| CPQ / quoting | Salesforce CPQ, DealHub, Conga, Subskribe | product/price config, discount approvals, quote docs | partial — full pricing/discount-policy substrate, no Quote object (top COVERAGE partial cluster) |
| Billing / subscriptions | **Stripe**, Zuora, Chargebee, Maxio, NetSuite (invoicing side) | subscriptions, invoices, dunning, proration | **mocked** (stripe-billing; densification adds subscriptions/PIs/refunds/payment links) |
| ERP / finance | **NetSuite**, SAP S/4, Sage Intacct, QuickBooks (SMB) | order records, AR/AP, revenue reconciliation | **mocked** (netsuite-erp; densified spec landed: SO lifecycle, bills, payments) |
| CLM / e-signature | **DocuSign**, Ironclad, PandaDoc, LinkSquares, Conga | envelopes, clause libraries, countersign order | partial — MSA/order-form artifacts + clause library tables; no envelope object |
| Support / ticketing | Zendesk, **Intercom**, Freshdesk, Jira Service Management | SLA-tiered cases, escalation | **mocked twice** — Intercom spec absorbed into revops-core; jira vendor (densification adds real issue/transition surface) |
| Incident / paging | **PagerDuty**, Opsgenie, incident.io | sev routing, on-call, ack/resolve | **mocked** (pagerduty-support; densified spec landed: 24 tools) |
| Knowledge / enablement | **Notion**, Confluence, Guru, Highspot, Seismic, Showpad | SOPs, battlecards, content engagement | **mocked** (notion-docs; densification adds pages/databases/blocks) |
| Team comms | **Slack**, Microsoft Teams | deal rooms, approval threads, escalations | **mocked** (slack; densification adds post/history/reactions) |
| Docs / sheets artifacts | Google Drive/Sheets, Microsoft 365, Airtable | order forms, rate cards, commission statements, trackers | partial — `agent_sheets`/`agent_documents` + gh sheets surface |
| Forecasting / RevOps analytics | **Clari**, BoostUp, Aviso, Gong Forecast | commit categories, pipeline inspection, snapshots | partial — forecast methodology tables + 500-row opportunity mass; no forecast-snapshot object |
| Compensation | CaptivateIQ, Spiff (Salesforce), Everstage, QuotaPath | plan → attainment → statements | partial — comp-plan anchor + sheet surface; no quota table (named partial) |
| Outbound phone / dialers | Orum, Nooks, Aircall, RingCentral | parallel dialing, voicemail drops | gap (named) — no telephony op |
| LinkedIn / social selling | LinkedIn Sales Navigator (no public API), Expandi, HeyReach | connect/message sequences, engager scraping | gap (named, wave-7 candidate) |
| SMS / WhatsApp | Twilio, Salesmsg | conversational follow-up | gap (named) |
| Email infra (deliverability) | **SendGrid**, Mailgun, Amazon SES, Postmark; warmup: Smartlead/Instantly | domain auth, suppression, warmup, bounce hygiene | **mocked** (sendgrid-email; densification adds send + suppression writes) |

Bold = the archetype our mock's namespace models (per `world.json.mock_service_specs` or identity mapping).

## What the landscape says about our choices

1. **We mock the systems of record + the channels, not the intelligence layers.**
   Gong/Clari/ZoomInfo-class products *derive* state; our verifiers need systems
   that *hold* state. Their capabilities enter the world as data fixtures
   (transcripts, scorecards, forecast rules) rather than as vendors — the right
   call for deterministic state-diff verification.
2. **One deliberate CRM, not two.** HubSpot-as-second-CRM is the strongest
   wave-7 candidate from the "data chaos" principle (same business fragmented
   across systems — CREATION-PROTOCOL §4); today the chaos axis is
   CRM-vs-sheets-vs-billing, not CRM-vs-CRM. `research/tools/hubspot-crm.md`
   stub already exists.
3. **The 11 named coverage gaps are all in this table's gap rows** (LinkedIn,
   SMS, SERP/web, SMTP verification, dialers) — they share one property: they
   front the live internet, which a deterministic world can only surrogate.
   That's a scope decision, not an omission (`docs/COVERAGE.md` says exactly this).
4. **Sequencing engines (Outreach/Salesloft) are half-mocked knowingly.** The
   policy substrate (sequence_design_rules, merge_field_conventions, snippets)
   exists; the send/execution loop arrives with `post_mail_send` + the
   `sg_mail_sends` log. A dedicated sequence-instance object (ordered steps,
   delay_days, per-step A/B) remains the named missing piece and belongs in a
   future outreach-style namespace if sequencing becomes a first-class eval axis.

## Follow-ups (kept open per protocol)

- Verify current MCP-server availability per leader (official Stripe/GitHub/
  Atlassian/Notion MCP servers existed pre-cutoff; Outreach/Gong/Clari MCP
  status unverified) — fill the `research/tools/*.md` stubs with links.
- Price/packaging shifts since 2026-01 (esp. ZoomInfo vs Apollo consolidation,
  Clay's enterprise motion) before committing wave-7 vendor identities.
