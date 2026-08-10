# morgan_stanley_simulated

Generated from: "Maximum-complexity revenue-operations simulation world for the fictional bulge-bracket investment bank "Morgan Stanley (SIMULATED)". Evolve the existing Salesforce CRM (Sales Cloud + Service Cloud) lead-to-order world into the FULL B2B revenue lifecycle across an integrated GTM stack: (1) lead capture and enrichment waterfall with ICP scoring and intent signals; (2) inbound routing with an MQL->SAL acceptance gate; (3) outbound email sequencing with reply classification on SendGrid-style email infrastructure; (4) dialer plus conversation intelligence with diarized call transcripts and MEDDIC scorecards; (5) meeting scheduling with round-robin assignment on Google Calendar; (6) CRM core lead->contact->account->opportunity->quote->order in Salesforce; (7) CPQ with tiered discount authority and the sequential Deal Desk -> Compliance -> Finance approval matrix; (8) contract lifecycle and e-signature with a clause library and customer-first countersign order; (9) Stripe-style billing: subscriptions, invoices, payments, a dunning ladder, refunds/credits and proration reconciled against activated orders; (10) forecasting and pipeline inspection with commit categories and stale-deal rules; (11) customer success: weighted health scores, churn playbooks, EBR cadence, renewals on a 120-day timeline with uplift policy; (12) support cases with SLA tiers on Intercom-style ticketing; (13) territory, quota and compensation including deal splits and commission statements; (14) marketing automation: campaigns, nurture tracks, an MQL->SQL handoff SLA, consent and suppression lists; (15) sales enablement: battlecards against three named fictional competitors and content engagement tracking; (16) proposals/RFP responses with a security-questionnaire answer library; (17) analytics and reporting with exact KPI formulas; (18) RevOps data hygiene: duplicate detection, merges, and a webhook event bus between systems; (19) partner deal registration with conflict windows and margin tiers. Slack-style deal-room messaging carries approvals and escalations, Gmail-style correspondence threads, a Notion-style knowledge base holds the SOP corpus, Google Drive/Sheets document stores hold the artifacts (MSAs, order forms, rate cards, call transcripts, commission statements, win/loss reports), NetSuite-style order records reconcile billing, and Workday-style rep rosters carry quotas. Deep multi-hop cross-system workflows with strict policy gates from the anchor SOPs; cross-system invariants (closed-won opportunity => executed order form => activated order => subscription => invoice => payment) and document-grounded decisions where the agent must read the governing SOP or artifact before acting. All data synthetic."

## Quick start

```bash
docker build -t sbx_291042075d7547f4 .
docker run -p 8080:8080 sbx_291042075d7547f4
```

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| GET | /world | World identity, thesis, and resource-count summary |
| GET | /tools | List tool definitions and input schemas |
| GET | /tasks | List packaged tasks |
| GET | /traces | List traces recorded in the current runtime state |
| GET | /tables | List tables with row counts |
| GET | /tables/{name} | Sample rows from one table |
| POST | /sessions | Create an isolated copy-on-write world session |
| DELETE | /sessions/{session_id} | Close an isolated session and remove its mutable state |
| POST | /mcp | MCP JSON-RPC initialize, tools/list, and tools/call |
| POST | /tool-call | Execute one tool with {tool, args} |
| POST | /task/{task_id}/run | Replay a packaged task trajectory and run VCode |
| POST | /chat | Run the bundled stateful heuristic agent with {message} |
| POST | /reset | Reset runtime state from the immutable seed |
| POST | /verify/{task_id} | Run the verifier for one task |

## World summary

- **Domain**: saas
- **Vertical**: Crm
- **Tables**: 214
- **Tools**: 205
- **Tasks**: 25
- **Verifiers**: 25
- **Company family**: company_0ce72a7af0db73ee382c
- **Scenario packs**: 0
- **Persisted trajectories**: 0 (the train kit self-heals locally when this is zero)

## MCP quick start

The server is prebuilt. Starting it never generates or compiles a world. Tool names are
namespaced by reusable asset in `mcp-assets.json`; company identity and scenario packs are
preserved in `company.json`.

```bash
curl -sS http://localhost:8080/mcp -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

## Train and measure on this world

The bundle is a self-contained RL gym: freshly replayed verifier-passed trajectories +
executable VCode verifiers + a keyless training kit. See `train/README.md`.

```bash
python3 train/run_training_eval.py --dry-run   # validate training data (stdlib only)
python3 train/run_training_eval.py --smoke     # measured small-Qwen SFT + GRPO scorecard
```
