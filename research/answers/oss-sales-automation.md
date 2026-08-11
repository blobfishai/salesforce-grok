# Open-source sales automation & AI-SDR/RevOps tooling — GitHub inventory

> Purpose: enumerate what real open-source sales/GTM software actually *automates*, so we can
> check the simulated Morgan Stanley world can run the same scenarios.
>
> Method: GitHub REST API (`gh api`) for star counts, `pushed_at`, archived flag and license —
> every row below was fetched live, not recalled. READMEs were pulled via
> `repos/{owner}/{repo}/readme` and read for workflow steps. **Snapshot date: 2026-08-11.**
> Star counts drift; treat them as order-of-magnitude.
>
> Repos I could not verify are in [§7 Unverified](#7-unverified--flagged).

---

## 1 · Summary table

Sorted by category, then stars. "Last push" is `pushed_at`.

| Repo | Cat | Stars | Last push | License | Key workflow it automates |
|---|---|---:|---|---|---|
| [twentyhq/twenty](https://github.com/twentyhq/twenty) | CRM | 54,695 | 2026-08-11 | NOASSERTION | People/Companies/Opportunities/Notes/Tasks as code; publish custom objects + workflows to a workspace |
| [odoo/odoo](https://github.com/odoo/odoo) | CRM | 53,637 | 2026-08-11 | NOASSERTION | Lead → Opportunity pipeline, activity scheduling, assignment rules, quotation handoff to Sales |
| [frappe/erpnext](https://github.com/frappe/erpnext) | CRM | 37,933 | 2026-08-10 | GPL-3.0 | Full quote-to-cash: Lead → Opportunity → Quotation → Sales Order → Delivery → Sales Invoice |
| [krayin/laravel-crm](https://github.com/krayin/laravel-crm) | CRM | 23,659 | 2026-08-07 | MIT | Leads, quotes, persons/orgs, activities (call/meeting/lunch), automation workflows, web-to-lead forms |
| [Dolibarr/dolibarr](https://github.com/Dolibarr/dolibarr) | CRM | 7,504 | 2026-08-11 | GPL-3.0 | Third parties → proposals → orders → invoices → contracts (ERP-side commercial chain) |
| [SuiteCRM/SuiteCRM](https://github.com/SuiteCRM/SuiteCRM) | CRM | 5,642 | 2026-07-31 | AGPL-3.0 | Classic SFA object set + declarative Workflow module (conditions → actions) + Campaigns/Target Lists |
| [frappe/crm](https://github.com/frappe/crm) | CRM | 3,303 | 2026-08-10 | AGPL-3.0 | Leads/Deals kanban, email templates, **built-in telephony (Twilio/Exotel) with call recording + call logs**, WhatsApp |
| [espocrm/espocrm](https://github.com/espocrm/espocrm) | CRM | 3,214 | 2026-08-10 | AGPL-3.0 | Leads/Contacts/Accounts/Opportunities/Cases/Campaigns/Target Lists + BPM workflows + custom entities |
| [relaticle/relaticle](https://github.com/relaticle/relaticle) | CRM | 1,498 | 2026-08-10 | AGPL-3.0 | Self-hosted CRM shipping **30 MCP tools** natively — CRM designed agent-first |
| [marmelab/atomic-crm](https://github.com/marmelab/atomic-crm) | CRM | 1,196 | 2026-08-10 | MIT | Contacts/companies/deals kanban, tasks+reminders, **CC-the-CRM email capture**, import/export, activity log |
| [vtiger-crm/vtigercrm](https://github.com/vtiger-crm/vtigercrm) | CRM | 256 | 2026-05-03 | NOASSERTION | Leads/orgs/contacts/opportunities/quotes/invoices + workflow engine (low activity; main dev is off-GitHub) |
| [mautic/mautic](https://github.com/mautic/mautic) | AI-SDR/MAP | 10,312 | 2026-08-10 | NOASSERTION | Segment → drag-drop campaign builder (decision/action flow) → **point-based lead scoring** → stage promotion |
| [knadh/listmonk](https://github.com/knadh/listmonk) | AI-SDR/MAP | 22,697 | 2026-08-10 | AGPL-3.0 | Lists/subscribers with SQL-queryable attributes, campaign send, templates, bounce processing, transactional API |
| [filip-michalsky/SalesGPT](https://github.com/filip-michalsky/SalesGPT) | AI-SDR | 2,719 | **2024-09-17** | MIT | Stage-aware sales conversation agent (7 stages) + product-catalog RAG tool + Stripe payment link; voice/email/SMS |
| [eracle/OpenOutreach](https://github.com/eracle/OpenOutreach) | AI-SDR | 2,659 | 2026-08-11 | NOASSERTION | Product+ICP prose → LLM ICP filter → firmographic paging → GP-regressor scoring → LLM classify → gated paid email lookup → agentic multi-turn email |
| [zubair-trabzada/ai-sales-team-claude](https://github.com/zubair-trabzada/ai-sales-team-claude) | AI-SDR | 1,025 | 2026-03-27 | MIT | `/sales prospect <url>` → 5 parallel agents → firmographics fit, decision makers, **BANT+MEDDIC score**, competitive intel, 5-email sequence, PDF report |
| [melgarafael/DeskcommCRM](https://github.com/melgarafael/DeskcommCRM) | AI-SDR | 467 | 2026-08-10 | MIT | WhatsApp-native AI sales OS: agents answer, qualify and sell inside a self-hosted CRM (WAHA gateway) |
| [kaymen99/sales-outreach-automation-langgraph](https://github.com/kaymen99/sales-outreach-automation-langgraph) | AI-SDR | 364 | **2025-01-15** | n/a | LangGraph: LinkedIn scrape → site/blog + social + news analysis → pain points → qualify → personalized email + interview script + report; writes to HubSpot/Airtable/Sheets |
| [Othmane-Khadri/YALC-the-GTM-operating-system](https://github.com/Othmane-Khadri/YALC-the-GTM-operating-system) | AI-SDR | 277 | 2026-07-01 | MIT | CLI GTM OS: scrape own site → synthesize ICP/positioning framework → **confidence-gated human review** → campaign plan → lead qualification |
| [iPythoning/b2b-sdr-agent-template](https://github.com/iPythoning/b2b-sdr-agent-template) | AI-SDR | 152 | 2026-07-13 | MIT | 10-stage SDR pipeline driven by 10 cron jobs, 4-engine memory, WhatsApp/Email/Telegram channels |
| [impecablemee/gtm-mcp](https://github.com/impecablemee/gtm-mcp) | AI-SDR | 66 | 2026-04-20 | n/a | One `/launch`: Apollo company search → AI fit classification → ICP filter → contact extraction → sequence copy → SmartLead campaign (test-send gate first) |
| [warmbly/warmbly](https://github.com/warmbly/warmbly) | AI-SDR | 55 | 2026-08-06 | Apache-2.0 | Multi-step sequences with per-mailbox caps/spacing, unified reply inbox, **mailbox warmup pool**, bounce/complaint/suppression, visual AI reply playbooks |
| [laramies/theHarvester](https://github.com/laramies/theHarvester) | Enrich | 17,000 | 2026-08-10 | n/a | OSINT harvest of emails/subdomains/names/hosts per domain across many sources (security-origin, used as a free email finder) |
| [joeyism/linkedin_scraper](https://github.com/joeyism/linkedin_scraper) | Enrich | 4,399 | 2026-04-10 | GPL-3.0 | Selenium scrape of LinkedIn Person / Company / Job objects into structured records |
| [speedyapply/JobSpy](https://github.com/speedyapply/JobSpy) | Enrich | 4,057 | 2026-02-18 | MIT | Job-posting scrape across LinkedIn/Indeed/Glassdoor/Google/ZipRecruiter — the canonical **hiring-signal** source |
| [omkarcloud/google-maps-scraper](https://github.com/omkarcloud/google-maps-scraper) | Enrich | 3,080 | 2026-07-27 | MIT | Local-business lead extraction, 50+ fields incl. emails/phones/reviews |
| [AfterShip/email-verifier](https://github.com/AfterShip/email-verifier) | Enrich | 1,594 | 2026-02-26 | MIT | Syntax → MX → disposable/free/role-account detection → SMTP deliverability probe, without sending |
| [kiryano/Scout](https://github.com/kiryano/Scout) | Enrich | 454 | 2026-02-22 | MIT | Scrape Instagram/Twitch/TikTok/LinkedIn profiles, extract emails from bios |
| [buyukakyuz/email-sleuth](https://github.com/buyukakyuz/email-sleuth) | Enrich | 418 | 2025-12-20 | MIT | Name + domain → **permute candidate email patterns → verify** → return best guess with confidence |
| [cullenwatson/StaffSpy](https://github.com/cullenwatson/StaffSpy) | Enrich | 324 | 2025-06-17 | WTFPL | Fetch an entire company's staff from LinkedIn with experiences/schools/skills/contact info (org-chart build) |
| [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | Enrich | 165,161 | 2026-08-10 | AGPL-3.0 | Scrape/crawl/search/extract structured JSON from any site — the substrate under most AI enrichment columns |
| [browser-use/browser-use](https://github.com/browser-use/browser-use) | Enrich | 108,676 | 2026-08-06 | MIT | LLM drives a real browser — used to operate portals/CRMs that have no API |
| [Zackriya-Solutions/meetily](https://github.com/Zackriya-Solutions/meetily) | ConvIntel | 28,865 | 2026-06-05 | MIT | Local live transcription (Parakeet/Whisper) + speaker diarization + AI summary, fully offline |
| [Vexa-ai/vexa](https://github.com/Vexa-ai/vexa) | ConvIntel | 2,669 | 2026-08-10 | Apache-2.0 | **Bot joins Meet/Teams/Zoom/Jitsi** → real-time speaker-attributed transcript API → meetings compile to Markdown knowledge repo → sandboxed agents work it |
| [zime-ai/zime-gtm-skills](https://github.com/zime-ai/zime-gtm-skills) | ConvIntel | 13 | 2026-08-10 | MIT | 29 skills auditing call transcripts + CRM exports against **MEDDICC/BANT/pain rubrics**; every dimension Covered/Partial/Missed with a quote or timestamp citation |
| [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | MCP | 89,415 | 2026-08-10 | NOASSERTION | Reference + community MCP server index (no first-party CRM server; sales vendors live in the community list) |
| [salesforcecli/mcp](https://github.com/salesforcecli/mcp) | MCP | 454 | 2026-07-31 | Apache-2.0 | **OFFICIAL Salesforce DX MCP.** Toolsets `orgs,metadata,data,users` + `run_apex_test`; per-org scoping, GA gating |
| [forcedotcom/mcp-hosted](https://github.com/forcedotcom/mcp-hosted) | MCP | 132 | 2026-07-23 | Apache-2.0 | **OFFICIAL** docs/wiki for Salesforce-hosted remote MCP servers + client auth |
| [HubSpot/mcp-server](https://github.com/HubSpot/mcp-server) | MCP | 5 | **2025-04-25** | n/a | Under the official HubSpot org but a near-empty shell — the shipped artifact is the `@hubspot/mcp-server` npm package. See §7 |
| [baryhuang/mcp-hubspot](https://github.com/baryhuang/mcp-hubspot) | MCP | 127 | 2025-11-11 | MIT | Community HubSpot: create contact/company **with duplicate prevention**, company activity, recent conversations, FAISS semantic search over retrieved data |
| [mhenry3164/twenty-crm-mcp-server](https://github.com/mhenry3164/twenty-crm-mcp-server) | MCP | 88 | 2026-07-30 | MIT | Twenty CRUD for people/companies/opportunities/notes/tasks, batch create ≤60, cursor pagination, **schema/metadata discovery incl. custom objects** |
| [kesslerio/attio-mcp-server](https://github.com/kesslerio/attio-mcp-server) | MCP | 69 | 2026-08-01 | NOASSERTION | Attio: 19 universal ops over companies/people/deals/tasks/lists/notes, batch, relationship traversal, **read auto-approve / write approval-gated** |
| [WillDent/pipedrive-mcp-server](https://github.com/WillDent/pipedrive-mcp-server) | MCP | 60 | 2026-07-21 | MIT | Pipedrive **read-only by default**; opt-in `move-deal`/`add-deal-note` are preview-first, need `execute:true`, do an optimistic stale-stage check, and emit an audit line |
| [JustinBeckwith/gongio-mcp](https://github.com/JustinBeckwith/gongio-mcp) | MCP | 21 | 2026-08-09 | MIT | Gong: `list/get/search_calls`, `get_call_summary`, `get_call_transcript`, `search_calls_by_opportunity`, `search_transcripts`, `get_trackers` |
| [lkm1developer/apollo-io-mcp-server](https://github.com/lkm1developer/apollo-io-mcp-server) | MCP | 40 | 2025-04-18 | MIT | Apollo.io MCP (TypeScript) |
| [thevgergroup/apollo-io-mcp](https://github.com/thevgergroup/apollo-io-mcp) | MCP | 19 | 2026-08-10 | MIT | Apollo: `search_people/companies`, `enrich_person/company`, `bulk_enrich_*`, `get_organization_job_postings`, `search_news_articles` |
| [dedupeio/dedupe](https://github.com/dedupeio/dedupe) | RevOps | 4,498 | 2025-07-29 | MIT | Active-learning fuzzy matching: human labels candidate pairs → blocking + scoring → dedup/entity resolution |
| [Multiwoven/multiwoven](https://github.com/Multiwoven/multiwoven) | RevOps | 1,666 | 2026-08-11 | AGPL-3.0 | Open Reverse ETL (Hightouch/Census alt): warehouse model → field mapping → incremental sync into CRM/tools |
| [zinggAI/zingg](https://github.com/zinggAI/zingg) | RevOps | 1,236 | 2026-08-10 | AGPL-3.0 | Spark-scale identity resolution / MDM: find training data → label → train → match → link → single customer view |
| [zapier/gtm-cheat-codes](https://github.com/zapier/gtm-cheat-codes) | RevOps | 321 | 2026-07-13 | MIT | Zapier's own GTM agent skills: campaign planning/postmortem, **lead follow-up QA**, account prioritization, cross-CRM coordination — all with approval gates + safe writeback |
| [clay-run/agent-plugins](https://github.com/clay-run/agent-plugins) | RevOps | 98 | 2026-08-10 | n/a | **OFFICIAL Clay**: skills + MCP tools + `clay` CLI for building enrichment tables, AI columns, exports |
| [supaglue-labs/supaglue](https://github.com/supaglue-labs/supaglue) | RevOps | 426 | **2024-03-07 · ARCHIVED** | MIT | Unified CRM API across Salesforce/HubSpot/Pipedrive — the OSS "one schema for all CRMs". Dead but architecturally instructive |
| [getbeton/inspector](https://github.com/getbeton/inspector) | RevOps | 36 | 2026-06-08 | AGPL-3.0 | PostHog usage → detect buying signals (trial-conversion intent, power-user emergence, adoption velocity) → account score → route to Attio/HubSpot/Pipedrive/Zoho |
| [Astoriel/LeadGenius](https://github.com/Astoriel/LeadGenius) | RevOps | 31 | 2026-08-11 | n/a | 4 layers: webhook ingest → **waterfall enrichment** → rules-as-code scoring (dbt/Postgres) → reverse ETL to CRM. Reference impl, mock mode — see §7 |
| [dhisana-ai/gtm-ai-tools](https://github.com/dhisana-ai/gtm-ai-tools) | RevOps | 15 | 2025-07-06 | NOASSERTION | NL description → generated GTM tool; lead discovery, enrichment, qualification, **CRM data hygiene**, outreach copy; run over CSV → push to CRM/webhook/Clay |
| [marketinguys/awesome-gtm-engineering](https://github.com/marketinguys/awesome-gtm-engineering) | RevOps | 139 | 2025-06-08 | MIT | Curated index of GTM-engineering tooling (useful as a discovery seed, not a tool) |

---

## 2 · Open-source CRMs — what objects and workflows they model

The object model is remarkably convergent. Every serious OSS CRM lands on some variant of:
**Lead → (convert) → Contact + Account + Opportunity**, with `Activity` (call/meeting/task/note)
hanging off all of them, and a stage-based pipeline on the Opportunity.

- **[twentyhq/twenty](https://github.com/twentyhq/twenty)** (54.7k★, active daily) — People,
  Companies, Opportunities, Notes, Tasks; the differentiator is **CRM-as-code**: `defineObject({
  nameSingular:'deal', fields:[{name:'amount', type:FieldType.CURRENCY}, ...] })` then
  `npx twenty app:publish`. Objects, views, **agents and logic functions** ship as versioned app
  artifacts. Workflow: define custom object → publish to workspace → drive via REST/GraphQL + webhooks.
- **[espocrm/espocrm](https://github.com/espocrm/espocrm)** (3.2k★) — the widest *stock* object set:
  Leads, Contacts, Accounts, Opportunities, Cases, Campaigns, Target Lists, Documents. Entity Manager
  creates custom entities/fields/relations at runtime; the (paid) Advanced Pack adds BPM workflows.
  Workflow: target list → mass-email campaign → lead capture → convert → opportunity stages → case handoff.
- **[SuiteCRM/SuiteCRM](https://github.com/SuiteCRM/SuiteCRM)** (5.6k★) — the SugarCRM lineage:
  Accounts/Contacts/Leads/Opportunities/Quotes/Contracts/Cases/Campaigns, plus a **declarative Workflow
  module** (record conditions → actions: modify field, create record, send email) and Security Groups
  for row-level access. Closest analogue to Salesforce's declarative automation.
- **[frappe/crm](https://github.com/frappe/crm)** (3.3k★) — Leads/Deals with kanban and custom views,
  all activity on one page. Notable for our purposes: **telephony is first-class** — Twilio and Exotel
  built in with call recording and call logs, plus WhatsApp, and an ERPNext bridge for invoicing.
  That gives a native call-log object most OSS CRMs lack.
- **[frappe/erpnext](https://github.com/frappe/erpnext)** (37.9k★) — the only one that models the
  **full quote-to-cash chain** as distinct documents: Lead → Opportunity → Quotation → Sales Order →
  Delivery Note → Sales Invoice, each with its own state machine.
- **[odoo/odoo](https://github.com/odoo/odoo)** (53.6k★) — CRM app is Lead → Opportunity with
  pipeline stages, scheduled *Activities* as a first-class nudge object, lead assignment/scoring rules,
  and handoff to the Sales app for quotations.
- **[krayin/laravel-crm](https://github.com/krayin/laravel-crm)** (23.7k★) — Leads, Quotes, Persons,
  Organizations, Products, typed Activities (call/meeting/lunch), **automation workflows** and web forms.
- **[marmelab/atomic-crm](https://github.com/marmelab/atomic-crm)** (1.2k★) — contacts, companies,
  deals on a kanban, tasks with reminders, aggregated activity log, CSV import/export. Its standout
  workflow is **email capture by CC**: CC the CRM address and the message is saved as a note on the contact.
- **[relaticle/relaticle](https://github.com/relaticle/relaticle)** (1.5k★) — worth watching: an OSS
  CRM that ships **30 MCP tools** in the box rather than bolting an integration on afterwards.
- **[Dolibarr/dolibarr](https://github.com/Dolibarr/dolibarr)** (7.5k★) and
  **[vtiger-crm/vtigercrm](https://github.com/vtiger-crm/vtigercrm)** (256★) round out the ERP-flavoured
  end; vtiger's GitHub mirror is low-activity (last push 2026-05-03), primary development happens off-GitHub.

**Implication for our world:** the object graph we simulate (Account/Contact/Lead/Opportunity/Activity/
Task + stage transitions) matches the OSS consensus. The two things OSS CRMs model that are easy to
miss are (a) a **first-class call-log/recording object** (frappe/crm) and (b) the **quote → order →
invoice documents** downstream of Closed Won (ERPNext, Dolibarr).

---

## 3 · AI SDR / outbound automation

The strongest reference implementation here is **[eracle/OpenOutreach](https://github.com/eracle/OpenOutreach)**
(2,659★, pushed 2026-08-11), because its README states the pipeline explicitly:

1. Operator supplies a **product description + campaign objective** in prose
   (e.g. "SaaS analytics platform" targeting "VP of Engineering at Series B startups").
2. An LLM converts that into an **ICP filter** and pages matching firmographic profiles from a licensed
   discovery source (BetterContact Lead Finder) — *no emails yet, nothing billed*.
3. A **Gaussian Process Regressor over profile embeddings scores the pool**, so expensive steps go to the
   most promising candidates first (explore/exploit).
4. An **LLM classifies** each selected candidate; every decision is fed back into the scorer.
5. A **confidence gate rations a paid work-email lookup** (one credit per verified hit).
6. A hit routes into **agentic email**: personalized opener sent from the operator's own mailbox, then
   the agent reads replies and runs **multi-turn follow-up**.

Note the economic structure — *search is free, contact data costs money, so scoring exists to ration
spend*. Any realistic simulation of outbound should have a cost-gated enrichment step.

Other implementations, and what is distinct about each:

- **[filip-michalsky/SalesGPT](https://github.com/filip-michalsky/SalesGPT)** (2,719★, but **last push
  2024-09-17 — effectively dormant**). Historically the canonical OSS "AI sales agent". Its contribution
  is the **sales conversation stage analyzer**: the agent classifies which of ~7 stages the conversation
  is in (introduction → qualification → value prop → needs analysis → solution presentation → objection
  handling → close) and acts accordingly. Has a product-knowledge-base RAG tool to suppress hallucination,
  works across voice/email/SMS/WhatsApp, and can generate a Stripe payment link to actually transact.
- **[zubair-trabzada/ai-sales-team-claude](https://github.com/zubair-trabzada/ai-sales-team-claude)**
  (1,025★). `/sales prospect https://acme.com` fans out **5 parallel agents** → company research &
  firmographics (fit score /100), decision-maker identification, **BANT opportunity assessment (score
  /100)**, competitive intelligence, outreach strategy (5-email sequence) → composite prospect grade →
  `PROSPECT-ANALYSIS.md` + PDF pipeline report.
- **[kaymen99/sales-outreach-automation-langgraph](https://github.com/kaymen99/sales-outreach-automation-langgraph)**
  (364★, last push 2025-01-15). LangGraph state machine: LinkedIn profile scrape → company website/blog
  analysis → social activity across FB/X/YouTube → recent company news → **pain-point identification** →
  qualification against predefined criteria → generate personalized email + interview-prep script +
  tailored outreach report → write to HubSpot / Airtable / Google Sheets through one standardized schema.
- **[impecablemee/gtm-mcp](https://github.com/impecablemee/gtm-mcp)** (66★). Built by a lead-gen agency
  from thousands of real campaigns. One `/launch` command: **find companies (Apollo) → AI-classify fit →
  apply ICP filtering rules → extract contacts → write the sequence → launch the SmartLead campaign**,
  with test emails routed to the operator's own inbox before activation. Apify for supplementary scraping.
- **[warmbly/warmbly](https://github.com/warmbly/warmbly)** (55★, Apache-2.0) — the most complete OSS
  *sending-side* model: multi-step sequences with **per-mailbox caps and spacing**, a unified reply inbox,
  a **warmup pool of monitored mailboxes**, deliverability accounting (bounces, complaints, suppression
  lists, inbox placement), and **visual reply playbooks with AI steps**. Also carries its own light CRM
  (contacts, pipelines, deals, tasks, meetings).
- **[Othmane-Khadri/YALC](https://github.com/Othmane-Khadri/YALC-the-GTM-operating-system)** (277★).
  Scrapes your own website → synthesizes an ICP/positioning framework → **high-confidence sections
  auto-commit, low-confidence sections queue for human sign-off** at a review dashboard. That
  confidence-gated human-in-the-loop pattern is worth mirroring in evals.
- **[iPythoning/b2b-sdr-agent-template](https://github.com/iPythoning/b2b-sdr-agent-template)** (152★) —
  10-stage pipeline driven by **10 cron jobs** (i.e. the SDR loop as scheduled background work, not a
  single request) across WhatsApp/Email/Telegram.
- **[melgarafael/DeskcommCRM](https://github.com/melgarafael/DeskcommCRM)** (467★) — WhatsApp-first AI
  sales OS; agents answer, qualify and close inside a self-hosted CRM. Relevant because it shows the
  non-email channel as the primary surface.
- **Classic marketing automation** still matters: **[mautic/mautic](https://github.com/mautic/mautic)**
  (10.3k★) is segment → drag-drop campaign builder (decision/action branches) → **point-based lead
  scoring** → stage promotion → form/landing-page capture; **[knadh/listmonk](https://github.com/knadh/listmonk)**
  (22.7k★) is the send/bounce/subscriber-attribute layer with SQL-queryable segmentation.

**Gap:** there is no mature OSS equivalent of Outreach/Salesloft *cadences* (multi-channel task queues
with rep-owned call/LinkedIn steps). Warmbly is the closest and it is email-centric at 55★.

---

## 4 · Lead scraping / enrichment OSS

- **[firecrawl/firecrawl](https://github.com/firecrawl/firecrawl)** (165k★) — scrape/crawl/search/extract
  structured JSON from arbitrary sites. This is the substrate under most "AI enrichment column" products.
- **[browser-use/browser-use](https://github.com/browser-use/browser-use)** (108.7k★) — LLM-driven real
  browser; the fallback when a CRM or data portal has no API.
- **[laramies/theHarvester](https://github.com/laramies/theHarvester)** (17k★) — domain → emails,
  subdomains, names, hosts across many sources. Security-tooling origin, routinely repurposed as a free
  email finder for a target company.
- **[joeyism/linkedin_scraper](https://github.com/joeyism/linkedin_scraper)** (4,399★) — Selenium scrape of
  LinkedIn **Person / Company / Job** into structured records.
- **[cullenwatson/StaffSpy](https://github.com/cullenwatson/StaffSpy)** (324★) — pull an entire company's
  staff roster with experiences, schools, skills and contact info. This is the **org-chart / buying-committee
  build** step done cheaply.
- **[speedyapply/JobSpy](https://github.com/speedyapply/JobSpy)** (4,057★) — job postings across
  LinkedIn/Indeed/Glassdoor/Google/ZipRecruiter. In GTM use this is a **hiring-signal** feed ("they're
  hiring 5 data engineers → they're building a data team → trigger").
- **[omkarcloud/google-maps-scraper](https://github.com/omkarcloud/google-maps-scraper)** (3,080★) —
  local-business lead extraction, 50+ fields including emails, phones and reviews.
- **[AfterShip/email-verifier](https://github.com/AfterShip/email-verifier)** (1,594★, Go) — the
  verification half: syntax → MX lookup → **disposable / free / role-account detection** → SMTP
  deliverability probe, all without sending mail.
- **[buyukakyuz/email-sleuth](https://github.com/buyukakyuz/email-sleuth)** (418★) — the discovery half:
  name + domain → **permute candidate patterns** (`f.last@`, `first@`, `flast@`…) → verify each → return
  the best candidate with a confidence score. Together with the verifier this is the whole
  "find + verify email" waterfall, open source.
- **[kiryano/Scout](https://github.com/kiryano/Scout)** (454★) — Instagram/Twitch/TikTok/LinkedIn profile
  scraping with email extraction from bios (creator/SMB segments).

**Note:** these are the *components*; there is no single OSS Apollo/ZoomInfo, because the moat is the
licensed contact database, not the code. OpenOutreach's design concedes this explicitly — it buys the
data from a licensed provider and open-sources only the orchestration around it.

---

## 5 · Sales conversation intelligence

- **[Zackriya-Solutions/meetily](https://github.com/Zackriya-Solutions/meetily)** (28,865★) — privacy-first
  local meeting assistant: live transcription (Parakeet/Whisper, claimed 4× faster), **speaker diarization**,
  AI summary. Runs entirely offline. Workflow: record → transcribe live → diarize → summarize → export.
- **[Vexa-ai/vexa](https://github.com/Vexa-ai/vexa)** (2,669★, Apache-2.0) — the more GTM-shaped one:
  **a bot joins Google Meet / Teams / Zoom / Jitsi**, streams speaker-attributed transcripts in real time
  over a self-hosted API, then **meetings compile into Markdown in a git repo** and sandboxed agents read
  and write that repo. That is the whole "call → durable structured knowledge → agent acts on it" chain,
  self-hosted. The bot-joins-the-call part is the genuinely hard piece nobody else open-sources.
- **[zime-ai/zime-gtm-skills](https://github.com/zime-ai/zime-gtm-skills)** (13★ but directly on-topic) —
  29 agent skills that **audit call transcripts and CRM exports against GTM rubrics**, on two axes:
  deal stage (discovery → renewal) and initiative (**MEDDICC, BANT, pain identification**). Each rubric
  dimension is returned Covered / Partial / Missed **with a direct quote or timestamp** — their stated
  rule is "an uncited finding doesn't ship". This is the best open articulation of what
  transcript→qualification extraction should output, and it maps directly onto verifier design.
- Smaller/adjacent, verified but low-star: `alphaparkinc/genpark-sales-post-call-agent-skill` (9★,
  transcript → auto-update CRM + email templates), `Ismail-2001/Meeting-Intelligence-Agent` (4★,
  multi-agent BANT/MEDDIC from conversations), `Nik1125/twenty-zadarma` (5★, Twenty CRM + telephony
  with transcripts).
- **Gong itself** publishes [gong-io/gecko](https://github.com/gong-io/gecko) (306★, conversation
  annotation tool) and [gong-io/call-playbook](https://github.com/gong-io/call-playbook) (3★) — but
  **no official Gong MCP server or OSS conversation-intelligence product**.

**Gap:** OSS covers capture (meetily, vexa) and rubric-scoring (zime) well, but the middle — *automatic
CRM field writeback from a call* — exists only in sub-15★ repos.

---

## 6 · MCP servers for sales tools — official vs community

| Vendor | Official server? | Evidence |
|---|---|---|
| **Salesforce** | ✅ **Yes, two** | [salesforcecli/mcp](https://github.com/salesforcecli/mcp) (454★, Apache-2.0, active) — the DX MCP server, toolsets `orgs,metadata,data,users`, plus `run_apex_test`, with per-org scoping and an `--allow-non-ga-tools` gate. And [forcedotcom/mcp-hosted](https://github.com/forcedotcom/mcp-hosted) (132★) for **Salesforce-hosted remote MCP servers** |
| **HubSpot** | ⚠️ **Nominally** | [HubSpot/mcp-server](https://github.com/HubSpot/mcp-server) exists under the official org but has **5★ and no push since 2025-04-25** — the real distribution is the `@hubspot/mcp-server` npm package. Treat the GitHub repo as not the source of truth |
| **Clay** | ✅ Yes | [clay-run/agent-plugins](https://github.com/clay-run/agent-plugins) (98★, active) — official skills + MCP tools + `clay` CLI |
| **Attio** | ❌ Community only on GitHub | Best: [kesslerio/attio-mcp-server](https://github.com/kesslerio/attio-mcp-server) (69★). Attio's own MCP is a hosted/remote endpoint, not an open repo |
| **Pipedrive** | ❌ Community only | Best: [WillDent/pipedrive-mcp-server](https://github.com/WillDent/pipedrive-mcp-server) (60★) |
| **Gong** | ❌ Community only | Best: [JustinBeckwith/gongio-mcp](https://github.com/JustinBeckwith/gongio-mcp) (21★). `gong-io` org publishes no MCP server |
| **Apollo.io** | ❌ Community only, very fragmented | ~10 competing repos, all <45★: [lkm1developer/apollo-io-mcp-server](https://github.com/lkm1developer/apollo-io-mcp-server) (40★), [thevgergroup/apollo-io-mcp](https://github.com/thevgergroup/apollo-io-mcp) (19★) |
| **Outreach** | ❌ **Nothing** | The `outreach-io` GitHub org does not exist; no credible community server found |
| **Salesloft** | ❌ **Nothing** | [SalesLoft](https://github.com/SalesLoft) org publishes only `api-example` (6★) and infra libraries — no MCP |
| **Twenty** | ❌ Community | [mhenry3164/twenty-crm-mcp-server](https://github.com/mhenry3164/twenty-crm-mcp-server) (88★) |

**Design patterns worth stealing, observed across these servers:**

- **Read/write asymmetry with approval gates.** Pipedrive's server is *read-only by default*; writes must
  be named in `PIPEDRIVE_WRITE_TOOLS`, they **preview by default and only mutate with `execute:true`**,
  `move-deal` requires `expectedCurrentStageId` and does an optimistic **stale-state check**, and the audit
  line records only operation/entity-ID/outcome/timestamp — never note contents or credentials. Attio's
  server uses MCP safety annotations to auto-approve reads and request approval for writes.
- **Universal vs scoped tools.** Attio consolidated 40+ resource-specific tools into **19 universal
  operations** (`search_records`, `batch_records`, `get_record_info`), then re-added scoped writes
  (`create_company`, `update_company`) only where a generic write could mutate the wrong object class.
- **Schema/metadata discovery as a tool.** Twenty's server exposes `get_metadata_objects` /
  `get_object_metadata` so the agent can discover custom objects, fields and enum options before acting.
- **Output-size guardrails.** Gong's `search_calls` auto-paginates up to ~5000 calls, then **falls back to
  a compact table if formatted output would exceed `MAX_MCP_OUTPUT_LENGTH` (default 50,000 chars)** — you
  still get every call ID, and drill in with `get_call_summary`.
- **Duplicate prevention on create.** The HubSpot community server's `hubspot_create_contact` /
  `hubspot_create_company` do dedupe checks as part of the create call.

---

## 7 · RevOps / analytics OSS

- **[dedupeio/dedupe](https://github.com/dedupeio/dedupe)** (4,498★, last push 2025-07-29) — **active-learning**
  record linkage: the tool proposes candidate pairs, a human labels match/distinct, it learns blocking
  predicates + a scoring model, then clusters duplicates. This is exactly the CRM dedupe/merge workflow.
- **[zinggAI/zingg](https://github.com/zinggAI/zingg)** (1,236★, active) — the same problem at Spark scale
  for MDM: `findTrainingData` → label → `train` → `match` → `link` → single customer view across systems.
- **[Multiwoven/multiwoven](https://github.com/Multiwoven/multiwoven)** (1,666★, active) — OSS Reverse ETL
  (Hightouch/Census alternative): pick a warehouse model → map fields to a destination object → incremental
  sync into CRM/marketing tools. The standard "warehouse is source of truth, CRM is a destination" pattern.
- **[getbeton/inspector](https://github.com/getbeton/inspector)** (36★) — OSS Pocus/Common Room: read
  PostHog product usage → detect named behavioral signals (**trial-conversion intent, power-user emergence,
  feature-adoption velocity**) → score each account → push signal + score + *why now* into Attio / HubSpot /
  Pipedrive / Zoho so reps get a prioritized list. This is PLG lead routing, end to end.
- **[Astoriel/LeadGenius](https://github.com/Astoriel/LeadGenius)** (31★) — a clean 4-layer reference
  architecture: FastAPI **webhook ingest** → **waterfall enrichment** → **rules-as-code scoring** (dbt +
  Postgres, deliberately transparent vs "black box" MadKudu/Clearbit) → **reverse ETL to CRM**, with an
  Evidence BI dashboard built in CI. Author labels it a portfolio reference implementation running in mock
  mode — see §8.
- **[zapier/gtm-cheat-codes](https://github.com/zapier/gtm-cheat-codes)** (321★) — Zapier's own GTM team's
  agent skills. The named business workflows are a good checklist: campaign planning, campaign postmortem,
  media inbox triage, **lead follow-up QA (find missed, slow, or low-quality follow-up and create
  owner-ready actions)**, account prioritization by why-now signals, sales personalization from CRM +
  product usage, customer decks, **cross-CRM coordination**, customer-proof retrieval. Explicitly framed
  around *identity, permissions, approval gates, audit trails and safe writeback*.
- **[dhisana-ai/gtm-ai-tools](https://github.com/dhisana-ai/gtm-ai-tools)** (15★) — describe a GTM workflow
  in natural language, the agent picks few-shot examples and generates a runnable tool; ships tools for
  lead discovery, enrichment, qualification, **CRM data hygiene** and outreach content, runnable over CSVs
  with results pushed to CRMs, webhooks or Clay tables.
- **[supaglue-labs/supaglue](https://github.com/supaglue-labs/supaglue)** (426★, **ARCHIVED 2024-03-07**) —
  a unified CRM API normalizing Salesforce/HubSpot/Pipedrive to one schema. Dead, but the normalization
  schema is the best OSS statement of "the common sales object model".

**Gap:** **quota, commission and territory management have essentially no credible OSS.** Searches for
`quota attainment`, `commission`, `territory management` return only sub-5★ dashboards and Power BI
portfolio projects. Same for **forecasting** — `sales forecasting` hits are all Kaggle competition
solutions from 2018, not operational tools. If our world models quota/commission/forecast-submission, it
is modeling something with no open-source analogue to check against.

---

## 8 · Unverified / flagged

- **`tomquirk/linkedin-api`** — **could not verify.** Returns 404; the repo appears deleted or renamed.
  Widely cited in older writeups. Verified alternatives listed in §4.
- **[HubSpot/mcp-server](https://github.com/HubSpot/mcp-server)** — exists under the official org but is
  a 5★ shell with no activity since 2025-04-25. The functioning official server ships via npm
  (`@hubspot/mcp-server`), which I did not verify on npm. Do not treat the GitHub repo as the artifact.
- **[supaglue-labs/supaglue](https://github.com/supaglue-labs/supaglue)** — verified but **archived**
  (`archived: true`, last push 2024-03-07). Reference only.
- **[filip-michalsky/SalesGPT](https://github.com/filip-michalsky/SalesGPT)** (2,719★) and
  **[kaymen99/sales-outreach-automation-langgraph](https://github.com/kaymen99/sales-outreach-automation-langgraph)**
  (364★) — verified and not archived, but **dormant** (last push 2024-09-17 and 2025-01-15). Historically
  influential; do not assume they run against current APIs.
- **[Astoriel/LeadGenius](https://github.com/Astoriel/LeadGenius)** — the README states it is a portfolio
  reference implementation with a snapshot date and that "mock mode is a deliberate reproducibility path,
  not a claim that every third-party enrichment connector works live". Architecture is sound; treat the
  connectors as unproven.
- **`ai-sdr` GitHub topic** — searched, **returns zero repos**. The category exists in practice but is not
  organized under that topic; `sales-automation`, `cold-email`, `lead-generation`, `revops` and
  `go-to-market` are the topics that actually carry traffic.
- A large fraction of 2026 "GTM" repos are **agent skill packs, not software** (`zapier/gtm-cheat-codes`,
  `LeadMagic/gtm-skills`, `AIDevGTM/gtm-cofounder`, `LaGrowthMachine/gtm-system`, `Zevenue/headless-gtm`).
  They are legitimate signal about *which workflows people want automated*, but they are prompts over
  vendor APIs, not runnable systems. I have used them only as workflow evidence, never as tool evidence.

---

## 9 · Distinct workflow patterns (the deliverable)

Deduplicated across all 56 verified repos. Each line is one pattern; the parenthetical names the
strongest open-source exemplar. **This is the list to check the simulated world against.**

1. **ICP definition → filtered list build** — turn prose targeting criteria into a structured firmographic/technographic filter and page matching accounts (OpenOutreach, gtm-mcp).
2. **Waterfall enrichment** — try provider A, then B, then C until a field resolves, with per-credit cost accounting and a confidence gate before spending (OpenOutreach, LeadGenius).
3. **Email discovery by pattern permutation + verification** — name + domain → candidate patterns → MX/SMTP/role-account verification → best candidate with confidence, before any send (email-sleuth + AfterShip/email-verifier).
4. **Account research dossier** — website + blog + recent news + social activity + job postings → summarized pain points and a fit score (kaymen99, ai-sales-team-claude).
5. **Buying-committee / org-chart mapping** — enumerate the decision makers, titles and roles at a target account (StaffSpy, ai-sales-team-claude).
6. **Signal detection from external events** — hiring, funding, tech-stack change, review activity → a "why now" trigger attached to an account (JobSpy, gtm-ai-tools).
7. **Product-usage (PLG) signal → account score** — behavioral events → named signals (trial intent, power-user emergence, adoption velocity) → account score (getbeton/inspector).
8. **Lead scoring and grading** — rules-as-code or ML producing a numeric fit/intent score with an auditable reason (Mautic points, LeadGenius dbt rules, OpenOutreach GP regressor).
9. **Lead routing / owner assignment under an SLA** — score + segment + territory rules select an owner and start a response-time clock (LeadGenius, Odoo assignment rules).
10. **Multi-step, multi-channel sequence enrollment** — enroll a contact in a cadence of email/LinkedIn/call/WhatsApp steps with spacing rules and per-mailbox send caps (Warmbly, gtm-mcp, b2b-sdr-agent-template).
11. **Per-prospect message personalization** — merge research artifacts + snippets/templates into a specific opener rather than a mail-merge (nearly all AI-SDR repos).
12. **Mailbox warmup and deliverability management** — warmup pool, rotation/throttling, bounce and complaint handling, suppression lists, inbox-placement tracking (Warmbly, listmonk).
13. **Reply detection and classification** — interested / not now / referral / objection / unsubscribe / OOO → drives the next action (Warmbly reply playbooks, OpenOutreach).
14. **Autonomous multi-turn follow-up** — the agent keeps the thread going across replies until a meeting is booked or the lead is disqualified (OpenOutreach, SalesGPT).
15. **Meeting booking → calendar event → CRM activity** — check availability, send the invite, log it against the record (Warmbly, frappe/crm).
16. **Call capture → transcription → diarization → summary + action items** — a bot joins or a local recorder captures, output is speaker-attributed (Vexa, meetily, Gong MCP `get_call_summary`).
17. **Transcript → structured qualification extraction** — score a call against MEDDIC/MEDDICC/BANT dimensions, marking each Covered/Partial/Missed **with a verbatim quote or timestamp as citation** (zime-gtm-skills).
18. **Post-call CRM writeback** — update opportunity fields, stage, next steps and log the activity directly from the transcript (genpark post-call skill, zapier gtm-cheat-codes).
19. **Stage-aware conversation control** — classify which sales stage the interaction is in and select the next move accordingly (SalesGPT stage analyzer).
20. **Opportunity stage progression with entry criteria** — advance a deal through a defined pipeline, validating the target stage and guarding against stale state (every CRM; Pipedrive MCP `move-deal` with `expectedCurrentStageId`).
21. **Quote-to-cash document chain** — Opportunity → Quotation → Sales Order → Delivery → Invoice, each a stateful document (ERPNext, Dolibarr, Krayin).
22. **Duplicate detection and merge / entity resolution** — candidate pair generation, blocking, scoring, human-labeled active learning, cluster and merge (dedupe, zingg; also HubSpot MCP create-with-dedupe).
23. **CRM data hygiene audit → remediation tasks** — find missing fields, stale stages, past-due close dates, unassigned or un-followed-up records, and emit owner-ready actions (zapier lead-follow-up QA, gtm-ai-tools).
24. **Cross-system sync / reverse ETL** — map fields between warehouse ↔ CRM or CRM-A ↔ CRM-B, sync incrementally, reconcile conflicts (Multiwoven, supaglue, zapier cross-CRM coordination).
25. **Approval-gated write-back with audit trail** — preview the mutation, require explicit human approval or `execute:true`, then write, and record operation/entity/outcome/timestamp without leaking payloads (Pipedrive MCP, Attio MCP, zapier gtm-cheat-codes, YALC confidence gating).
26. **Schema/metadata discovery before acting** — list objects, fields, enum options and custom objects so the agent can act on a workspace it has not seen before (Twenty MCP, Salesforce DX MCP `metadata` toolset).
27. **Segment → campaign → scored progression** — build a segment, run a branching drip campaign, accumulate points, promote across lifecycle stages (Mautic, EspoCRM target lists + campaigns).

Patterns **1–18** are the outbound/AE core and are densely covered by OSS. Patterns **20, 22–26** are the
RevOps/agent-safety layer. **Quota attainment, commission calculation, territory design and forecast
submission appear in no credible open-source tool** — they are a real workflow class with no OSS analogue
to validate against.
