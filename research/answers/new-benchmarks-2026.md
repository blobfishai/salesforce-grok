# New Sales / CRM / RevOps Agent Benchmarks & Simulation Environments (not in the existing census)

Research date: 2026-08-10. Scope: benchmarks and simulation environments for sales, CRM, GTM and
revenue-operations agents that the repo's census (`data/coverage/census-items.json`) does **not**
already cover.

**Explicitly excluded as already-covered:** CRMArena, CRMArena-Pro, tau-bench, tau2-bench, WorkBench,
AgentBench, ToolBench, API-Bank, MCPEval, WebArena, WorkArena/WorkArena++, ST-WebAgentBench,
TheAgentCompany, AgenticPay, OfficeBench, OdysseyBench, PolyWorkBench, ai_sales_eval_arena.

> **Verification legend** — ✅ fully verified (paper + repo/site opened directly) · ⚠️ partially
> verified (abstract/landing page only; repo or full text not opened) · ❌ could not verify.

---

## Summary table

| # | Name | Appeared | What it is (1 line) | Environment | Grading | Doc corpus | Multi-turn user | Writes | Live web | Voice/SMS/LinkedIn | Verif. |
|---|------|----------|---------------------|-------------|---------|-----------|-----------------|--------|----------|--------------------|--------|
| 1 | **GTM-Bench** | Jun 2026 | First benchmark for evidence-grounded buyer/seller coherence: offer → ICP → ranked prospect list | Read-only prospect DB API + web search + sandboxed filesystem in Docker; agent Skill (SKILL.md) | 4 LLM judges (offer, ICP, per-row match, per-row audit) with **negative utility** for bad rows | ✅ (indexed site text) | ❌ (single-shot prompt) | ⚠️ writes artifacts only | ✅ | ❌ | ✅ |
| 2 | **SDR-Bench** (in "Benchmarking the Personalization Capabilities of LLMs") | May 2026 | Sales-outreach personalization graded against **real logged reply/meeting outcomes** | Temporally-constrained replay of ~115k real SDR emails + 5,435 calls | Real receiver actions (replied / booked) + human rep ratings | ✅ 6,279 customer success stories | ❌ single-message | ❌ | ❌ | ✅ email (SDR calls in corpus) | ✅ |
| 3 | **SalesLLM** ("Sell More, Play Less") | Apr 2026 | Multi-turn realistic *selling skill* benchmark w/ a trained buyer simulator (CustomerLM) | Pure dialogue; bilingual ZH/EN; financial services + consumer goods | LLM rater for sales-process progress + fine-tuned BERT buying-intent classifier | ❌ | ✅ CustomerLM (SFT+DPO on 8k+ human sales convos) | ❌ | ❌ | ❌ | ✅ |
| 4 | **TERMS-Bench** | May 2026 | Diagnostic negotiation benchmark: Bayesian game, goes beyond deal rate | Multi-turn simulated counterpart with hidden latent type/policy/payoff | Surplus extraction, cue use, belief calibration, compliance, optimality gap vs oracle | ❌ | ✅ (simulated counterparty) | ❌ | ❌ | ❌ | ⚠️ |
| 5 | **EnterpriseOps-Gym** (ServiceNow Research) | Mar 2026 | Stateful enterprise agent gym: 164 tables, 512 tools, 8 domains, 1,150 tasks | Containerized Docker sandbox, relational DB | Outcome-based **SQL verification scripts** (completion, integrity, policy, no side effects) | ❌ | ❌ | ✅ | ❌ | ❌ | ⚠️ |
| 6 | **Agent-Diff** | Feb 2026 | Enterprise-API agent benchmark evaluated purely by **state diff** via code execution | Containerized replicas of enterprise productivity APIs | State diff (expected env-state change), not trace/param matching | ✅ API docs (ablated) | ❌ | ✅ | ❌ | ❌ | ✅ |
| 7 | **EnterpriseBench: CoreCraft** (Surge AI) | Feb 2026 | High-fidelity RL env simulating a full customer-support org (2,500+ entities, 23 tools) | Stateful RL environment, gym-style | Expert-authored **rubric criteria, all must pass**; used as RL reward | ⚠️ | ⚠️ | ✅ | ❌ | ❌ | ⚠️ |
| 8 | **EntCollabBench** | May 2026 | Role-specialized **multi-agent** enterprise org: 11 agents, 6 depts, permission isolation | Enterprise system state w/ RBAC | Execution traces + DB state verification + deterministic policy adjudication (no NL judging) | ⚠️ | ❌ | ✅ | ❌ | ❌ | ⚠️ |
| 9 | **World of Workflows** | Jan 2026 | Tests whether agents have a *world model* of enterprise side effects (4,000+ business rules) | ServiceNow platform, 55 active workflows, 234 tasks | Constrained task completion + dynamics prediction (side-effect forecasting) | ❌ | ❌ | ✅ | ❌ | ❌ | ⚠️ |
| 10 | **DRBench** (ServiceNow) | Oct 2025, ICLR 2026 | Enterprise deep research across **private company stack + public web**; 100 tasks / 10 domains incl. **Sales** | Simulated enterprise stack: chat logs, cloud files, spreadsheets, PDFs, email, open web | Insight recall + citation grounding ("insight-centric" LLM-assisted scoring) | ✅ heavy | ❌ | ❌ | ✅ | ❌ | ✅ |
| 11 | **τ³-bench** (Sierra) | 2026 | Third-gen tau line: adds knowledge-retrieval (RAG) domain + **full-duplex voice** | Typed API tools + policy doc; dual-control env; realtime audio providers | Task success + separate policy-adherence score + pass^k consistency | ✅ ~700 banking docs | ✅ | ✅ | ❌ | ✅ **voice** | ✅ |
| 12 | **SCUBA** (Salesforce AI Research) | Sep 2025 | Computer-use (GUI) benchmark on real Salesforce orgs; 300 tasks, 3 personas | **Live Salesforce sandbox orgs** via browser/GUI, parallel execution | Per-task **rule-based evaluator** + fine-grained milestone/process reward | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| 13 | **Magentic Marketplace** (Microsoft Research) | Oct 2025 | Open-source **agent-to-agent market**: buyer assistants vs competing seller agents | HTTP/REST client-server sim; search, negotiation, proposals, payments | Consumer welfare, market efficiency, fairness, manipulation resistance, bias | ❌ | ✅ agent↔agent | ✅ (transactions/payments) | ❌ | ❌ | ✅ |
| 14 | **MCP-Bench** (Accenture) + **MCP-Atlas** (Scale Labs) | Aug 2025 / Apr 2026 update | MCP-native tool-use harnesses over many live third-party MCP servers | 28 live MCP servers w/ real API keys (MCP-Bench); Scale-hosted leaderboard (Atlas) | Rule-based schema validation + LLM judge (o4-mini) + tool-usage metrics; Atlas: judge + 100-tool-call budget | ❌ | ❌ | ⚠️ | ✅ **live APIs** | ❌ | ✅ / ⚠️ |
| 15 | **CirrusBench** | Mar 2026 | Cloud-service customer support from **authentic production tickets**, graded beyond correctness | Real ticket-grounded env w/ tool dependencies | Correctness + Normalized Efficiency Index, Logical Jump, single/multi-turn latency | ✅ real tickets | ✅ | ⚠️ | ❌ | ❌ | ⚠️ |
| 16 | **JourneyBench** ("Beyond IVR") | Jan 2026 | Policy-adherence benchmark built from **user-journey graphs** | Simulated support conversations, 3 domains, 703 convos | **User Journey Coverage Score** (graph-path coverage) vs business rules | ✅ policies | ✅ | ⚠️ | ❌ | ❌ (text, IVR-positioned) | ⚠️ |
| 17 | **MerchantBench** | Jul 2026 | 365-simulated-day e-commerce operator; long-term coherence | Order-level sim, 26 tools, ~99k real product records | Final net assets vs **human participant** baseline | ✅ product data | ❌ | ✅ | ❌ | ❌ | ⚠️ |
| 18 | **RetailBench** | Mar 2026 | 1,000-day partially-observable single-store retail operator | Data-grounded simulation | Net worth / sales vs privileged **oracle policy** over 180-day horizon | ❌ | ❌ | ✅ | ❌ | ❌ | ⚠️ |
| 19 | **CustomerSim** (ex-"SalesSim") | May 2026 | Benchmarks & aligns MLLMs as **retail buyer simulators** (360 personas) | Multimodal dialogue sim | Persona alignment, lexical diversity, fluency, decision consistency; UserGRPO alignment | ❌ | ✅ (it *is* the user) | ❌ | ❌ | ❌ | ⚠️ |
| 20 | **VISTA** | Jun 2026 | Versatile user-simulation toolkit; hybrid **UI + API** simulated users | E-commerce + educational customer service | 6 metrics for realism, capability coverage, interaction effectiveness | ❌ | ✅ | ⚠️ | ❌ | ❌ | ⚠️ |

---

## Per-source detail

### 1. GTM-Bench ⭐ (highest relevance)
- **URLs:** https://gtm-bench.ai/ · paper https://gtm-bench.ai/assets/gtm-bench-paper.pdf · code https://github.com/pearlengine/GTM.Bench
- **Appeared:** June 2026 (Blackpearl Group). Press: https://itbrief.com.au/story/blackpearl-unveils-gtm-bench-for-ai-sales-evaluation
- **What:** The first benchmark for evidence-grounded buyer/seller coherence in GTM workflows — explicitly
  positioned as complementary to CRMArena-Pro ("CRM benchmarks evaluate tool use and business-system
  operations… but do not [evaluate GTM coherence]").
- **Task/use-case types** — 72 tasks, 11 suites, 15 verticals, derived by embedding-clustering **59,881 real
  seller queries** submitted to Bebop.ai (2025-02-07 → 2026-05-19):
  - A — Offer-grounded lead lists (6)
  - B — Named-domain offer extraction (8) — e.g. *"Find the best-fit customers for bluevine.com. First infer what the company appears to sell, then generate ranked target-company leads."*
  - C — Offer-to-lead list (9) — e.g. *"I sell SEO/content marketing services. Briefly define the ICP, then generate ranked lead companies in marketing agencies."*
  - D — Vertical / geo / firmographic search (8)
  - E — Persona / contact activation (9)
  - F — Intent / trigger evidence (7)
  - G — Technographic search (5) — e.g. *"find businesses using shopify and klaviyo"*
  - H — Offer-grounded lookalikes (3)
  - I — Market-to-lead list (3)
  - J — Buyer search with contact details (10)
  - K — Limited-context prompts (4) — deliberately underspecified
  - (Source taxonomy also includes market research and non-GTM/ambiguous, discarded.)
- **Environment:** A GTM operator's terminal workspace. Read-only API to Blackpearl's **Pearl Engine**
  company/contact database (firmographics, seller-facing descriptions, contact attributes, quality signals,
  intent signals), reached through a provided `SKILL.md` (Anthropic Agent Skills format) named
  `public-data-access`. Plus **web search**, local search, Docker container, sandboxed filesystem. Agents
  get an `AGENTS.md` explaining scoring incentives.
- **Outputs:** exactly three artifacts — `OFFER.md`, `ICP.md`, `RESULTS.csv`.
- **Grading:** four separate LLM judges with distinct rubrics and calibration hardening —
  `Jo` (offer, 5 dims), `Jc` (ICP, 6 dims), `Jm` (per-row **match**), `Ja` (per-row **audit** for fabricated/
  embellished claims, cross-checked against the DB record + website + search results). Rows are graded
  A/B/sub-B; utility `u(r) ∈ {+1, 0, −1}`; task score `S_A(x) = Q_o(x)·Q_c(x)·Σ u(r)`; benchmark score is
  the sum. **Bad rows actively subtract**, so dumping the database scores negative. Judges: GPT-5.5 for
  offer/ICP, cheaper same-family model for the high-frequency row judges. Canonical DB identifiers
  (`UP_ID`) must be preserved so the evaluator can retrieve the full record.
- **Headline result:** 4 of 6 generalist agent systems scored **negative** overall. Leaderboard: Blackpearl
  RTSA 26,615.6 → GPT-5.5 (Codex) 4,040.9 → Claude Sonnet 4.6 400.1 → Claude Opus 4.7 −2,476.6 →
  DeepSeek V4 Pro −3,398.0 → Gemini 3.5 Flash −10,671.9 → Kimi K2.6 −15,402.3. One agent emitted 6,342
  prospect rows for a single task.
- **Needs:** live web research ✅ · document/indexed-site corpus ✅ · writes = artifacts only (no CRM
  mutations) · multi-turn users ❌ · telephony/LinkedIn ❌.
- **Caveat (stated by authors):** the production benchmark runs on Blackpearl's private Pearl Engine data
  environment; the public repo is a "reproduction package" that excludes proprietary systems, schemas,
  credentials and customer data. Repo showed **1 commit** and no visible license at time of check.

### 2. SDR-Bench — "Benchmarking the Personalization Capabilities of Large Language Models" ⭐
- **URL:** https://arxiv.org/abs/2607.20471 (HTML: https://arxiv.org/html/2607.20471)
- **Appeared:** submitted 2026-05-23 (Adobe-affiliated author list: Srivastava, Yedlapati, Aggarwal, Singla, Dixit, Ajmera, Krishnamurthy)
- **What:** Adapts Kamenica–Gentzkow **Bayesian Persuasion** to generative agents and instantiates it in sales.
- **Task types:** generate personalized outbound sales messages (SDR outreach) intended to induce a specific
  receiver action; retrieve/select the right customer success story as evidence; rank/discriminate successful
  vs unsuccessful outreach.
- **Environment:** replay over proprietary corpora from a Fortune-100 tech company and a mid-size healthcare
  firm — ~115,000 filtered outreach emails and 5,435 outreach calls by 124 SDRs — under a
  **temporal constraint to prevent leakage**. Public release: SDR-Bench corpus of **6,279 customer success
  stories, 22 industries, ~200 enterprises**, plus SDR-Arena.
- **Grading:** **real logged receiver outcomes** (replied / booked meeting) — not an LLM judge. Plus a human
  field study: 12 professional sales reps rated usefulness (48% immediately useful; inter-rater Pearson 0.82).
- **Finding:** a "personalization plateau" — on the Fortune-100 cohort **no frontier model or deep-research
  agent statistically separates successful from unsuccessful outreach**; alignment scores cluster 30–43%.
- **Needs:** document corpus ✅ (success stories) · email channel ✅ · multi-turn ❌ · writes ❌ · live web ❌.

### 3. SalesLLM — "Sell More, Play Less: Benchmarking LLM Realistic Selling Skill"
- **URL:** https://arxiv.org/abs/2604.07054 · HTML https://arxiv.org/html/2604.07054
- **Appeared:** 2026-04-08 (v1), 2026-04-09 (v2). Authors: Su, Hu, Su, Chen, Zhan, Yang, Huang.
- **What:** Bilingual (ZH/EN) benchmark of **multi-turn, goal-directed persuasion under asymmetric incentives**.
- **Task types:** consultative sales dialogues in **Financial Services** and **Consumer Goods**; 30,074 scripted
  configurations distilled to **1,805 curated multi-turn scenarios** with controllable difficulty and personas
  (objection handling, needs discovery, closing under buyer resistance).
- **Environment:** pure dialogue — no tools, no DB. The differentiator is **CustomerLM**, a buyer simulator
  trained by SFT + DPO on 8,000+ crowdworker sales conversations, reducing **role inversion** (simulator
  starts selling back) from 17.44% (GPT-4o) to 8.8%.
- **Grading:** dual metric — (i) LLM rater scoring sales-*process* progress, (ii) fine-tuned BERT classifiers
  for end-of-dialogue **buying intent**. Validated against human judgment at Pearson r = 0.98. 15 LLM variants evaluated.
- **Needs:** multi-turn simulated buyer ✅ · everything else ❌.

### 4. TERMS-Bench — "Diagnosing LLM Negotiation Agents Beyond Deal Rate"
- **URL:** https://arxiv.org/abs/2605.13909
- **Appeared:** 2026-05-13. Authors: E. Zhang, F. Zhang, Pappu, El, Blanchet, Athey, J. Liu, Zou (Stanford-heavy).
- **What:** Bayesian-game framework for **bilateral price negotiation** where the counterpart's latent type,
  policy and payoff are known to the evaluator but hidden from the agent.
- **Task types:** multi-round price/terms bargaining across counterpart archetypes; the diagnostic axes are the
  point — surplus extraction, **cue use** (reading signals about the counterpart), **belief calibration**,
  constraint/mandate **compliance**, optimality gap vs an oracle.
- **Grading:** decomposed diagnostics, not a single deal-rate. 13 LLM agents evaluated; finding is that frontier
  models **saturate deal rate but diverge sharply** on the underlying competencies.
- **Needs:** multi-turn simulated counterparty ✅ · everything else ❌.
- ⚠️ Project site referenced in the abstract; no GitHub URL surfaced.

### 5. EnterpriseOps-Gym (ServiceNow Research)
- **URLs:** arXiv:2603.13594 · overview https://www.alphaxiv.org/overview/2603.13594v1 · secondary write-up https://neurotechnus.com/en/ai-agent-evaluation-enterpriseops-gym/
- **Appeared:** 2026-03-13.
- **What:** Stateful agentic planning + tool-use gym across **8 interconnected enterprise domains** —
  Customer Service, HR, ITSM (operational backbones); Email, Calendar, Teams, Drive (collaboration); plus
  cross-domain orchestration.
- **Task types:** employee onboarding, ticket resolution, database updates, permission verification,
  policy-compliant operations, and **30 intentionally infeasible tasks** to test safe refusal.
- **Environment:** containerized Docker sandbox. **164 relational tables** (~1.7 FKs each), **512 functional
  tools**; the average task touches ~25 tables. ReAct loop.
- **Grading:** outcome-based **SQL verification scripts** checking four things — task completion, DB integrity
  constraints, permission/process compliance, and **absence of unintended side effects**. No sequence matching;
  multiple valid paths accepted.
- **Scale:** 1,150 expert-curated tasks authored by 160+ engineers/SMEs, with **human-written reference plans**.
- **Results:** 14 frontier models; best is Claude Opus 4.5 at **37.4%**; ITSM (policy-heavy) drops to 28.5%;
  safe-refusal accuracy on infeasible tasks only **53.9%**.
- ⚠️ No public GitHub repo surfaced; read via alphaXiv overview rather than the arXiv full text.

### 6. Agent-Diff
- **URLs:** https://arxiv.org/abs/2602.11224 · code https://github.com/agent-diff-bench/agent-diff
- **Appeared:** submitted 2026-02-11, latest version 2026-04-28. Authors: Pysklo, Zhuravel, Watson.
- **What:** 224 tasks over enterprise productivity-software workflows, executed as **code** against
  **containerized replicas of enterprise APIs** sandboxed from production.
- **Grading — the notable contribution:** success is decided *purely by whether the expected environment
  state change occurred*, explicitly rejecting "fuzzy trace or parameter matching." Separates outcome from
  method, so any valid path passes.
- **Needs:** API documentation is provided and its effect is ablation-tested · writes/mutations ✅ ·
  multi-turn users ❌ · live internet ❌.
- ⚠️ The abstract does not name the specific SaaS products replicated.

### 7. EnterpriseBench: CoreCraft (Surge AI)
- **URLs:** https://arxiv.org/abs/2602.16179 · leaderboard https://surgehq.ai/leaderboards/enterprisebench-corecraft · blog https://surgehq.ai/blog/enterprisebench-corecraft
- **Appeared:** submitted 2026-02-18, final 2026-03-02. Authors: Mehta, Ritchie, Garre, Niebres, Heiner, Chen (Surge AI).
- **What:** First environment in Surge's EnterpriseBench suite — a fully operational simulation of a
  **customer support organization**: 2,500+ entities across 14 entity types, 23 unique tools.
- **Grading:** expert-authored **rubric criteria where all criteria must be satisfied**; the rubric doubles as
  a dense RL reward.
- **Results:** GPT-5.2 and Claude Opus 4.6 solve **<30%** under full-rubric scoring. GLM 4.6 trained with GRPO
  went 25.37% → 36.76% in one epoch, and the gains **transferred out of distribution**: +4.5% BFCL Parallel,
  +7.4% τ²-Bench Retail, +6.8% Tool Decathlon. This is the strongest published evidence that a synthetic
  enterprise world *generalizes* as training signal, which matters for how this repo positions its own world.
- ⚠️ The abstract does not enumerate concrete task types; no public GitHub surfaced (leaderboard is hosted).

### 8. EntCollabBench — "Beyond the All-in-One Agent"
- **URL:** https://arxiv.org/abs/2605.08761
- **Appeared:** 2026-05-09. Large author list led by Tao Yu / Hao Wang.
- **What:** A **permission-isolated organization** with **11 role-specialized agents across 6 departments** —
  the first of these that makes RBAC and delegation first-class rather than assuming one omniscient agent.
- **Task types:** two subsets — a **workflow subset** (agents collaboratively mutate enterprise system state)
  and an **approval subset** (policy-grounded approve/deny decisions).
- **Grading:** execution traces + **database state verification** + **deterministic policy adjudication** —
  explicitly *not* natural-language response judging.
- **Failure modes named:** delegation, context transfer, parameter grounding, workflow closure, decision commitment.
- ⚠️ No GitHub surfaced.

### 9. World of Workflows
- **URL:** https://arxiv.org/abs/2601.22130
- **Appeared:** submitted 2026-01-29, revised 2026-02-10. Authors: Gupta, Li, Liu, Ganapathi Subramanian, Suleman, Zhang, Lu, Pasupalak.
- **What:** Tests whether agents hold a **world model** of an enterprise system: a ServiceNow-based environment
  with **4,000+ business rules and 55 active workflows**, 234 tasks.
- **The distinctive claim:** frontier models exhibit **"dynamics blindness"** — they fail to predict the
  **cascading side effects** of their own actions, producing *silent constraint violations*. Tasks evaluate both
  constrained task completion **and** enterprise-dynamics prediction (i.e. "what will happen if I do this?").
- ⚠️ GitHub said to be released but no URL surfaced; grading detail not fully specified in the abstract.

### 10. DRBench (ServiceNow)
- **URLs:** https://arxiv.org/abs/2510.00172 · https://github.com/ServiceNow/drbench · https://huggingface.co/papers/2510.00172
- **Appeared:** Oct 2025 preprint; forthcoming at **ICLR 2026**.
- **What:** Enterprise deep research — **100 tasks across 10 domains, one of which is Sales**, requiring facts
  from **both the public web and a private company knowledge base**.
- **Environment:** a simulated enterprise stack — internal chat logs, cloud file systems, spreadsheets, PDFs,
  emails, websites, open web. Each task is grounded in a realistic user persona and company context; generated
  via a synthesis pipeline with human-in-the-loop verification.
- **Grading:** insight-centric — **insight recall** (did the agent surface the critical insights), factual
  accuracy, citation grounding, and report coherence/structure.
- **Needs:** document corpus ✅ heavy · live web ✅ · writes ❌ · multi-turn ❌.

### 11. τ³-bench (Sierra) — successor to the covered tau/tau2
- **URLs:** repo https://github.com/sierra-research/tau2-bench (τ³ is maintained inside it) · overview https://benchmarkingagents.com/tau3-bench/ · leaderboard https://benchlm.ai/benchmarks/tau3-bench
- **Appeared:** 2026 (τ-bench Jun 2024, τ²-bench Jun 2025).
- **Why it is not "already covered":** the census covers tau-bench and tau2-bench. τ³ adds two genuinely new
  axes: (a) a **`banking_knowledge` retrieval domain** backed by **~700 interconnected knowledge documents**
  (RAG under policy), and (b) **full-duplex voice** evaluation against realtime audio providers (OpenAI, Gemini,
  xAI). Domains: mock, retail, airline, telecom, banking_knowledge. 75+ task-quality corrections vs τ².
- **Grading:** task success **plus a separately reported policy-adherence score**, and a **pass^k** consistency
  metric across repeated runs.
- **Difficulty:** frontier models with high reasoning budgets reach only ~**25.5%** on the banking domain.
- ⚠️ One aggregator lists Mistral Medium 3.5 128B at 91.4% overall; leaderboard numbers across aggregators are
  inconsistent and should be treated as unverified.

### 12. SCUBA — Salesforce Computer Use Benchmark
- **URLs:** https://arxiv.org/abs/2509.26506 · https://www.salesforce.com/blog/scuba-benchmark/
- **Appeared:** submitted 2025-09-30 (Salesforce AI Research: Dai, Ramakrishnan, Gu, Fernandez, Luo, Prabhu, Hu, Savarese, Xiong, Chen, Xu).
- **What:** The **GUI/computer-use** counterpart to CRMArena — 300 task instances derived from **real user
  interviews**, spanning three personas: **platform administrator, sales representative, service agent**.
- **Task types:** enterprise-software UI navigation, data manipulation, workflow automation, information
  retrieval, troubleshooting.
- **Environment:** **real Salesforce sandbox orgs** driven through the UI, with parallel execution support.
- **Grading:** each task has a **rule-based evaluator** giving both binary success and a **fine-grained
  milestone score (process reward)**.
- **Results:** open-source CUA models that do well on OSWorld score **<5%** on SCUBA; closed-source reach 39%
  zero-shot, up to **50%** with demonstration augmentation (also −13% time, −16% cost).
- ⚠️ No public GitHub repo surfaced; the OpenReview PDF was behind a bot-verification wall.

### 13. Magentic Marketplace (Microsoft Research)
- **URLs:** https://arxiv.org/abs/2510.25779 · https://github.com/microsoft/multi-agent-marketplace · https://www.microsoft.com/en-us/research/blog/magentic-marketplace-an-open-source-simulation-environment-for-studying-agentic-markets/ · https://labs.ai.azure.com/innovations/magentic-marketplace/
- **Appeared:** 2025-10-27, 24 authors.
- **What:** Open-source simulation of an **agentic market**: buyer-side **assistant agents** transacting against
  **competing seller/service agents** — i.e. the seller side is itself an agent under evaluation.
- **Task types:** product/service discovery under varying search mechanisms, open-ended negotiation, proposal
  exchange, and **payment/transaction execution**. HTTP/REST client-server with register / protocol-discovery /
  action-execution endpoints. Scales to hundreds of concurrent agents.
- **Grading:** economic — agent utility, consumer welfare, market efficiency, fairness, **manipulation
  resistance**, bias.
- **Key finding directly relevant to sales agents:** a **severe first-proposal bias** giving **10–30× advantage
  to response speed over proposal quality**, and welfare collapse as the number of options scales.

### 14. MCP-Bench (Accenture) & MCP-Atlas (Scale Labs)
- **URLs:** https://github.com/Accenture/mcp-bench · https://arxiv.org/abs/2508.20453 · ICLR 2026 proceedings PDF https://proceedings.iclr.cc/paper_files/paper/2026/file/9e4b14eb6f16fe7b5818a8d633a0606a-Paper-Conference.pdf · MCP-Atlas https://labs.scale.com/leaderboard/mcp_atlas · OpenMCP harness https://blog.chameleoncloud.org/posts/openmcp-reproducible-benchmarking-mcp-agents/
- **Appeared:** MCP-Bench NeurIPS 2025 Workshop on Scaling Environments for Agents (Sep 2025), ICLR 2026 conference version. MCP-Atlas re-scored Apr 2026.
- **What:** MCP-native tool-use harnesses. MCP-Bench spans **28 live MCP servers** requiring real API keys
  (NASA, National Park Service, Google Maps, Hugging Face, biomedical, crypto/DeFi, weather…), testing tool
  discovery/selection/chaining across single-, dual- and triple-server configurations.
- **Grading:** rule-based schema validation + LLM judge (o4-mini) + tool-usage effectiveness metrics.
  MCP-Atlas (Apr 2026) replaced its 20-turn limit with a **100-tool-call budget** and added retry handling for
  transient tool errors — a harness-design detail worth copying.
- **Gap worth noting:** MCP-Bench has **no sales/CRM/business-software servers** — the domain coverage is
  consumer/science APIs. That is a hole this repo's MCP topology could fill.
- ⚠️ MCP-Atlas details come from search snippets; the leaderboard page itself was not opened.

### 15. CirrusBench
- **URL:** https://arxiv.org/abs/2603.28569 · org https://github.com/CirrusAI
- **Appeared:** 2026-03-30, 18 authors.
- **What:** Technical customer service grounded in **authentic production cloud-service tickets** (not synthetic),
  with multi-turn logical chains and realistic tool dependencies.
- **Grading — the contribution:** "beyond correctness." **Customer-centric metrics**: Normalized Efficiency
  Index (NEI), Logical Jump (LJ), Single-Turn Latency (STL), Multi-Turn Latency (MTL). Measures *how expensively*
  a task was solved, not just whether.
- ⚠️ The GitHub org exists but the specific benchmark repo was not confirmed.

### 16. JourneyBench — "Beyond IVR: Benchmarking Customer Support LLM Agents for Business-Adherence"
- **URL:** https://arxiv.org/abs/2601.00596
- **Appeared:** 2026-01-02. Authors: Balaji, Mishra, Sachdeva, Agrawal.
- **What:** Policy-aware support agents evaluated via **graph representations of user journeys**; 703 evaluated
  conversations across 3 domains. Compares a Static-Prompt Agent vs a Dynamic-Prompt Agent design.
- **Grading — the contribution:** **User Journey Coverage Score** — did the agent traverse the required paths of
  the business-defined journey graph, rather than just produce an acceptable final answer. A cheap way to grade
  "did the rep follow the playbook."
- ⚠️ No GitHub surfaced; text-based despite the IVR framing.

### 17. MerchantBench
- **URL:** https://arxiv.org/abs/2607.28956 (HTML https://arxiv.org/html/2607.28956)
- **Appeared:** submitted 2026-07-31, revised 2026-08-04 (13 authors, Alibaba-affiliated names).
- **What:** **365-simulated-day** e-commerce operator testing "long-term coherence" — maintaining purposeful
  behavior while adapting to accumulated evidence.
- **Task types:** product sourcing, listing and pricing control, cash-flow management, feedback adaptation.
  26 interactive tools; grounded in ~99,000 real product records; couples immediate upstream supplier events
  with **delayed** downstream order outcomes.
- **Grading:** final net assets, benchmarked **against human participants** — best LLM reached only **27.3%**
  of human outcomes.

### 18. RetailBench
- **URL:** https://arxiv.org/abs/2603.16453 (submitted 2026-03-17, final 2026-07-08). Authors: L. Zhang, J. Wang, J. Wu, Z. Zhang.
- **What:** Single-store supermarket as a partially-observable decision process supporting **thousand-day**
  simulations; 180-day evaluation horizon.
- **Task types:** pricing, replenishment, supplier selection, shelf assortment, inventory aging, customer
  feedback handling, external-event response, cash-flow constraints.
- **Grading:** net worth / sales vs a **privileged oracle policy**. 7 LLMs; all fall substantially short.
- ❗ **Do not cite arXiv:2606.15862** — that is a duplicate submission of the same work, **withdrawn 2026-06-19**.
  Use 2603.16453.

### 19. CustomerSim (previously titled "SalesSim")
- **URL:** https://arxiv.org/abs/2605.08334 (submitted 2026-05-08, revised 2026-07-29). Authors: Pruksachatkun, Wan, Chen, Chang, Wu.
- **What:** Benchmarks and **aligns multimodal LLMs as retail buyer simulators** — 360 personas (earlier
  version cited 674) across 5–6 product categories.
- **Grading:** persona alignment, lexical diversity, conversational fluency, decision consistency. Introduces
  **UserGRPO**, lifting persona alignment 41.7% → 65.2%.
- **Why it matters here:** it is a benchmark *of the user simulator*, which is the weak link in any multi-turn
  sales eval. Pairs with SalesLLM's CustomerLM and with the "Lost in Simulation" critique below.
- ⚠️ Title changed between versions; no GitHub surfaced.

### 20. VISTA
- **URL:** https://arxiv.org/abs/2606.11079 (submitted 2026-06-09). Authors: Lu, Shea, Zhang, Yu (Columbia).
- **What:** A user-simulation toolkit with a **hybrid simulator combining UI-based and API-based interaction** —
  relevant if this repo ever needs simulated users that both click and call tools.
- **Grading:** six metrics for realism, capability coverage, and interaction effectiveness. Applied to
  e-commerce and educational customer service.
- ⚠️ No GitHub surfaced; implementation detail thin in the abstract.

---

## Supporting methodology papers (not benchmarks, but directly useful)

| Paper | URL | Why it matters |
|---|---|---|
| **Lost in Simulation: LLM-Simulated Users are Unreliable Proxies for Human Users in Agentic Evaluations** | https://arxiv.org/pdf/2601.17087 | Documents **benevolence bias** — simulated users are too cooperative, inflating multi-turn scores. Direct threat to any persona-simulator eval. |
| **Efficient Agent Evaluation via Diversity-Guided User Simulation** | https://arxiv.org/pdf/2604.21480 | How to get coverage from fewer simulated-user episodes. |
| **From Confident Closing to Silent Failure: Characterizing False Success in LLM Agents** | https://arxiv.org/pdf/2606.09863 | Agents claim completion while environment state says otherwise — argues for state-diff verification over self-report. |
| **Anchor: Mitigating Artifact Drift in Agent Benchmark Generation** | https://arxiv.org/pdf/2605.26321 | Keeping synthetic benchmark artifacts from drifting as they are generated — relevant to this repo's seeded-world generation. |
| **CompliBench: Benchmarking LLM Judges for Compliance Violation Detection in Dialogue** | https://arxiv.org/pdf/2604.12312 | Validates the judges used for policy-compliance grading. |
| **Towards a Science of AI Agent Reliability** | https://arxiv.org/pdf/2602.16666 | Framing for pass^k / variance reporting. |

---

## Commercial / closed environments (⚠️ marketing-sourced, none independently verified)

Surfaced via https://www.rl-list.com/rl-environments-for-enterprise and https://www.agentgym.tech/ .
Treat all claims as vendor-stated.

| Vendor | Claim relevant to sales/CRM | URL |
|---|---|---|
| **Fleet AI** | High-fidelity RL environments replicating **Salesforce** and Excel; open-source **Harbor** agent-eval/RL tooling; Python SDK | fleetai.com |
| **AgentGYM** | Clone real SaaS tools into gym-compatible sandboxes — Gmail, **Salesforce**, Slack, 50+ | agentgym.tech |
| **Scale AI** | **HubSpot**, Linear, Slack via MCP tools; desktop VMs; expert rubrics + automated verifiers | scale.com |
| **Collinear** | Jira, ServiceNow, Shopify, EMR, airline/hotel replicas; trajectories + reward signals + LLM judge | collinear.ai |
| **Plato** | Amazon, Airbnb, Gmail-style replicas + Linux desktop; structured state-tracking/scoring APIs | plato.so |
| **HUD** | Real software in isolated containers as agent-callable tools; OSWorld-Verified, SheetBench-50 | hud.ai |
| **AfterQuery** | Expert SFT/RL rubrics; publishes Terminal-Bench, VADER, FinanceQA, IDE-Bench | afterquery.com |
| **Prime Intellect** | 2,500+ community RL environments; Verifiers library; prime-rl | primeintellect.ai |
| **Automation Anywhere GBA-Bench** | Proprietary suite over 7 enterprise domains **including Sales**; 30+ frontier models. ❌ **No paper, no repo, no task list published — unverifiable.** | https://www.automationanywhere.com/company/blog/ai-agent-benchmarks |

---

## Things I could NOT verify

1. **arXiv:2606.15862 (RetailBench)** — **withdrawn 2026-06-19**; superseded by arXiv:2603.16453. Do not cite.
2. **GTM-Bench public repo** (`github.com/pearlengine/GTM.Bench`) — exists and README confirms a 72-question
   task set, Docker harness and eval code, but showed only **1 commit**, no visible license, and explicitly
   excludes the Pearl Engine data environment the published scores were produced on. **The headline leaderboard
   is therefore not independently reproducible.**
3. **SCUBA** — OpenReview PDF blocked by bot verification; details come from the arXiv abstract and the
   Salesforce blog. No public GitHub found.
4. **EnterpriseOps-Gym** — read via alphaXiv overview, not the arXiv full text. No public repo found.
5. **EnterpriseBench CoreCraft, EntCollabBench, World of Workflows, CirrusBench, JourneyBench, VISTA,
   CustomerSim, TERMS-Bench** — abstracts only; concrete task inventories and repos not confirmed.
6. **MCP-Atlas** leaderboard page not opened; details from search snippets only.
7. **τ³-bench leaderboard numbers** conflict across third-party aggregators (benchmarklist.com vs benchlm.ai);
   treat any specific score as unverified.
8. **GBA-Bench** (Automation Anywhere) — proprietary, no paper or repo. Unverifiable.
9. **All commercial RL-environment vendors** in the table above — sourced from a directory site
   (rl-list.com) and vendor marketing. No technical documentation was opened.
