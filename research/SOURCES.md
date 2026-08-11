# Source index — sales-world research

Every claim in `research/answers/**` and `research/tools/**` must resolve to a row
here. Two kinds of source: **cloned repo** (durable, re-readable, diffable) and
**web** (dated, may drift — quote the sentence you rely on).

Cloned corpus: 37 repos, 1.9 GB, `research/repos/` — manifest
`research/repos.manifest.tsv`, results `research/repos/CLONE-LOG.tsv`
(36 OK, 1 reused from `external/CRMArena`). Cloned 2026-08-11, shallow/single-branch.

---

## 1. Evals & benchmarks (`research/repos/eval/`)

| Source | What it gives us | Path |
|---|---|---|
| **CRMArena / CRMArena-Pro** (Salesforce AI Research) | 9 (v1) → **19 task categories + 3 confidentiality probes** (v2), B2B & B2C orgs, aided/interactive modes, real Salesforce sandbox | `eval/SalesforceAIResearch__CRMArena` → `run_tasks_crmarena_pro.sh` |
| **MCPEval** (Salesforce AI Research, arXiv 2507.12806) | Auto **task generation from an MCP tool surface** + trajectory-level deep evaluation; per-domain benchmark folders (yfinance, airbnb, healthcare, sqlite, filesystem …) | `eval/SalesforceAIResearch__MCPEval` |
| **τ-bench / τ²-bench** (Sierra) | Domain **policy.md + db.json + tasks.json** pattern; user simulator; DB-state verification; retail/airline/telecom/banking | `eval/sierra-research__tau-bench`, `…__tau2-bench` |
| **τ²-bench-verified** (Amazon AGI) | Catalogue of benchmark-authoring defects that were corrected — a checklist for our own verifiers | `eval/amazon-agi__tau2-bench-verified` |
| **R2A-Sales** | **Rule-to-Action Gap**: 39 versioned policy atoms, 58 interactive scenarios, 2,016 matched static↔interactive pairs, 6 mock tools, pressure schedules, terminal conditions | `eval/qinyh10300__R2A-Sales-Benchmark` |
| **ai_sales_eval_arena** | LLM-judge **rubric grading of sales call transcripts**, tournament (round-robin/elimination) ranking; 8 seeded transcripts | `eval/Rperry2174__ai_sales_eval_arena` |
| **attio-mcp-benchmark** (Arcade) | 8 CRM read queries scored on **expressibility + token cost**; documents a real schema-discovery failure loop | `eval/ArcadeAI__attio-mcp-benchmark` |
| **ShampooSalesAgent** | Minimal conversational sales agent + benchmark; order capture to CSV | `eval/jackfsuia__ShampooSalesAgent` |
| **agentune** (SparkBeyond) | analyze → improve → **simulate** loop tuned to a KPI (conversion, CSAT) | `eval/SparkBeyond__agentune` |

Web:
- SCUBA: Salesforce Computer Use Benchmark — 300 task instances from real user
  interviews, personas = platform admin / sales rep / service agent; sandbox
  execution with **milestone (checkpoint) metrics**; zero-shot ≤5% (open) vs up to
  39% (closed), 50% with demonstrations. https://arxiv.org/pdf/2509.26506 (fetched 2026-08-11)
- Salesforce "Generative AI Benchmark for CRM" — accuracy / cost / speed / trust
  & safety framing. https://www.salesforceairesearch.com/crm-benchmark (2026-08-11; TLS error on fetch, cited via search result)
- "Beyond Accuracy: A Multi-Dimensional Framework for Evaluating Enterprise
  Agentic AI Systems" https://arxiv.org/pdf/2511.14136

## 2. Practitioner workflows & skills (`research/repos/workflow/`)

185 skill definitions inventoried → `research/answers/_data/workflow-skills.tsv`.

| Source | Task family it evidences | Path |
|---|---|---|
| **hubspot-admin-skills** (36 skills) | CRM **data hygiene / RevOps admin**: dedupe, lifecycle backfill, owner reassignment, bounce suppression, property/list/workflow cleanup, quarterly audit, workflows-as-code | `workflow/TomGranot__hubspot-admin-skills` |
| **YALC GTM-OS** (~55 skills) | Outbound engine: ICP definition, lookalikes, PredictLeads signals, enrichment, sequence copywriting by persona seniority, campaign launch/tracking, reply handling, **lost-deal revival** | `workflow/Othmane-Khadri__YALC-the-GTM-operating-system` |
| **gtm-pipeline-skills** (10) | Company search → contact filter → enrichment → signal scoring → outreach, as an explicit staged pipeline | `workflow/keinsaasforever__gtm-pipeline-skills` |
| **gtm-eng-skills** (15) | TAM building, qualified-title discovery, niche signal discovery (Won vs Lost), GTM analytics | `workflow/getaero-io__gtm-eng-skills` |
| **markster-os** (~40) | Full motion cold-email → funnel → event → **debrief creating CRM records from meeting notes**, stage-aware follow-up | `workflow/markster-public__markster-os` |
| **b2b-sdr-agent-template** | 10-stage pipeline, memory layers, quotation/proforma PDF generation, delivery queue | `workflow/iPythoning__b2b-sdr-agent-template` |
| **sales-outreach-automation-langgraph** | Explicit LangGraph node sequence for research → qualify → personalize → send | `workflow/kaymen99__sales-outreach-automation-langgraph` |
| **Autonomous-Sales-Inbox-and-CRM-Assistant** | Inbox triage ↔ CRM sync, auto-draft replies | `workflow/jacob-dietle__…` |
| **bricks** | Local Clay alternative: sheet + enrichment/agent columns (the spreadsheet-as-CRM surface) | `workflow/BraaMohammed__bricks` |
| **SDRbot**, **ai-crm-agents**, **marketplace-mcp** | Terminal RevOps agent; 6 autonomous CRM agents; 9 GTM/RevOps agents over real SFDC/HubSpot | `workflow/NForce-ai__SDRbot`, `…KlementMultiverse__ai-crm-agents`, `…LeanScaleTeam__marketplace-mcp` |

## 3. Tool surfaces (`research/repos/mcp/`)

Verb inventories extracted by `scripts/extract-mcp-verbs.py` →
`research/tools/_extracted/` (INDEX.tsv + one file per server).

| Vendor | Server(s) | Verbs extracted |
|---|---|---|
| Attio | `kesslerio__attio-mcp-server` | 285 |
| Pipedrive | `nubiia-dev__mcp-pipedrive` | 142 |
| HubSpot | `shinzo-labs__hubspot-mcp` · `calypsoCodex__hubspot-mcp-extended` | 112 · 95 tools / **68 distinct REST endpoint templates** |
| Close | `BusyBee3333__close-crm-mcp-2026-complete` | 94 |
| Twenty | `mhenry3164__twenty-crm-mcp-server` | 31 |
| Salesforce | `tsmztech__mcp-server-salesforce` · `jaworjar95__salesforce-mcp-server` | 26 · 18 |
| Multi-CRM (SFDC/HubSpot/Zoho/Pipedrive) | `zavora-ai__mcp-crm` (Rust) | 27 |
| Gong | `JustinBeckwith__gongio-mcp` | 22 |
| LinkedIn | `Linked-API__linkedapi-mcp` | 14 |
| Apollo.io | `lkm1developer__apollo-io-mcp-server` | 7 |
| — index | `RupertBarrow__awesome-salesforce-mcp` | link farm for further sourcing |

## 4. CRM data models (`research/repos/schema/`)

- `schema/twentyhq__twenty` — open Salesforce alternative, standard object/field
  model in code (sparse checkout: server modules + metadata modules).
- `schema/frappe__crm` — doctype schemas for lead / deal / organization.

## 5. Web sources — domain, roles, chaos (all fetched 2026-08-11)

**Roles & process**
- https://www.salesscreen.com/blog/b2b-saas-sales-operations-team-structure-a-complete-guide
- https://getgangly.com/blog/sales-careers-explained-sdr-bdr-ae-csm-sales-engineer
- https://syncgtm.com/blog/b2b-sales-roles · https://syncgtm.com/blog/sales-development-representative-roles
- https://handbook.gitlab.com/handbook/sales/commercial/comm-sales-opp-stages/ — a *public, real* stage definition with exit criteria
- https://www.weflow.ai/blog/sales-process — 7 stages, exit criteria, KPIs
- https://meddic.academy/meddic-as-a-sales-process/ · https://altiorco.com/revops-dictionary/opportunity-stages

**Deal desk / CPQ approvals**
- https://b2bprocess.com/deal-desk — definition, workflow, roles, metrics, SOP
- https://dealhub.io/glossary/approval-workflow/ · /quote-approval/ · /discount-approval/
- https://cpq-integrations.com/cpqpedia/sales-approval-workflow/
- https://skopx.com/resources/automate-deal-desk-approvals — three-tier matrix, 60–70% queue reduction
- https://fintastiq.com/blog/the-technology-that-cuts-deal-desk-delays-and-what-it-doesnt-fix — 9-day approval chain case

**Data chaos**
- https://www.default.com/post/crm-data-hygiene — 15–25% duplicate rates; 76% of entries <half complete
- https://www.landbase.com/blog/crm-data-audit-2026-step-by-step-revops
- https://syncmatters.com/blog/why-crm-data-migration-is-still-the-biggest-bottleneck — 54% delayed, 67% find data issues mid-migration
- https://www.pedowitzgroup.com/blog/12-enterprise-crm-gaps-blocking-revenue-in-2026 — shadow spreadsheets as distrust signal; 14-day enrichment lag
- https://pipeline.zoominfo.com/sales/crm-data-quality-gtm-intelligence
- https://durity.com/en-us/blog/why-hubspot-deal-amount-fields-rarely-match-recognized-revenue-in-saas — CRM amount ≠ recognized revenue
- https://durity.com/en-us/blog/why-hubspot-reports-differ-from-finance-statements
- https://blog.coupler.io/revenue-reconciliation/ — reconciliation cadence: weekly variance, monthly review, quarterly diagnostic
- https://www.scalexp.com/hubspot-or-salesforce-quickbooks-for-saas-why-revenue-reporting-breaks/ — cloned renewal deals double-counting
