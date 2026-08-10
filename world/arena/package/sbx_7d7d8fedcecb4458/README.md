# morgan_stanley_simulated

Generated from: "Salesforce CRM (Sales Cloud + Service Cloud style) simulation world for a fictional bulge-bracket investment bank modeled on Morgan Stanley, at CRMArena-comparable depth (github.com/SalesforceAIResearch/CRMArena): 15+ interconnected Salesforce-style objects (Lead, Account, Contact, Opportunity, OpportunityLineItem, Product, Pricebook, Quote, QuoteApproval, Order, Case, CaseHistory, EmailMessage, KnowledgeArticle, Activity, User/Role), realistic record volumes and distributions, three personas (sales rep, sales analyst, service agent/manager), CPQ quotes with a sequential Deal Desk / Compliance / Finance approval matrix, lead conversion, order activation (Closed Won), service case lifecycle, pipeline and weighted forecast analytics. Persona-scoped tasks with deterministic, verifiable ground truths. All data synthetic."

## Quick start

```bash
docker build -t sbx_7d7d8fedcecb4458 .
docker run -p 8080:8080 sbx_7d7d8fedcecb4458
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
- **Tables**: 33
- **Tools**: 104
- **Tasks**: 27
- **Verifiers**: 27
- **Company family**: sbx_7d7d8fedcecb4458
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
