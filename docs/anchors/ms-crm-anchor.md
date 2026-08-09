# Anchor PRD — Simulated Morgan Stanley Salesforce CRM (Lead-to-Order)

> SIMULATION ONLY. All entities are synthetic. This document describes a fictional
> sandbox modeled on a bulge-bracket investment bank ("Morgan Stanley (SIMULATED)").
> It is not affiliated with, endorsed by, or representative of Morgan Stanley.

## Domain
Sales-cloud CRM operations for institutional financial products sold by a simulated
investment bank: lead management, opportunity pipeline, CPQ quoting with an approval
chain, order activation, service cases, activity logging, and forecasting.

## Business Units
- Institutional Securities
- Wealth Management
- Investment Management

## Object Schemas

### Lead
- id: string (00Q-*)
- company: string
- contactName: string, email: string (fictional domain)
- segment: string, region: enum [AMER, EMEA, APAC]
- status: enum [New, Working, Converted, Disqualified]
- interestProductId: ref Product

### Account
- id: string (001-*)
- name: string
- segment: enum [Hedge Fund, Pension, Private Equity, Sovereign Wealth, Insurance, Family Office]
- region: enum [AMER, EMEA, APAC]
- tier: enum [Platinum, Gold, Silver]
- newClient: boolean

### Contact
- id: string (003-*), accountId: ref Account, name, title, email

### Product
- id: string (01t-*), name, family (business unit), listPrice (USD annual), regulated: boolean

### Opportunity
- id: string (006-*)
- accountId: ref Account, name
- stage: enum [Qualification, Discovery, Proposal, Negotiation, Closed Won, Closed Lost]
- amount: number (sum of list price x qty), ownerId: ref User
- products: array of { productId, qty }, closeDate: date

### Quote
- id: string (0Q0-*), opportunityId: ref Opportunity
- discountPct: number, tcv: number (post-discount total contract value)
- status: enum [Draft, In Approval, Approved, Rejected, Converted]
- approvalSteps: array of { step, role, status, actor, comment }

### Order
- id: string (801-*), quoteId: ref Quote, status: enum [Activated, Cancelled], tcv, activatedDate

### Case
- id: string (500-*), accountId: ref Account, subject, priority: enum [Low, Medium, High]
- status: enum [Open, Closed], relatedOpportunityId?: ref Opportunity, resolution?

### Activity
- id: string (00T-*), type: enum [Call, Email, Meeting, Task]
- subject, relatedTo: any record id, userId, date, notes

## Enterprise Flow (SOP): Lead-to-Order
1. Convert a qualified Lead into Account + Contact + Opportunity (new clients flagged).
2. Advance the Opportunity through Qualification → Discovery → Proposal → Negotiation.
3. Generate a CPQ Quote with a discount; TCV computed from product lines.
4. Submit the Quote for approval. The chain is computed from the matrix below and is
   processed sequentially; any rejection halts the deal.
5. Convert the fully Approved Quote to an activated Order; the Opportunity becomes
   Closed Won (the ONLY way to reach Closed Won).
6. Open an onboarding Case for the client and log Activities (calls, emails, tasks).
7. Forecast reports weight open pipeline by stage probability:
   Qualification 10%, Discovery 25%, Proposal 50%, Negotiation 75%.

## Approval Matrix (CPQ)
| Step order | Approver role      | Triggered when                                    |
|------------|--------------------|---------------------------------------------------|
| 1          | Deal Desk          | discountPct > 15 OR quote TCV > $5,000,000        |
| 2          | Compliance Officer | account.newClient = true OR any product.regulated |
| 3          | Finance            | quote TCV > $25,000,000                           |

If no rule triggers, the quote auto-approves.

## Invariants (verifiable)
- An Order must reference a Quote with status Approved (at conversion time).
- A rejected Quote can never be converted; Closed Won only via quote-to-order conversion.
- A converted Lead must yield exactly one Account, one Contact, and one Opportunity.
- Weighted forecast = sum(open opportunity amount x stage probability).

## Task Suite (CRMArena-inspired)
Task design follows CRMArena (Salesforce AI Research, github.com/SalesforceAIResearch/CRMArena):
persona-scoped, environment-grounded tasks with objectively verifiable answers.

Personas and example tasks:
- **Sales rep (agentic flows)**: convert an inbound family-office lead into
  account/contact/opportunity; push a high-value regulated quote through the
  Deal Desk → Compliance chain; reject an over-discounted quote with a reason.
- **Sales analyst (text-to-answer)**: which stage holds the most open pipeline value;
  best region by open pipeline; top product family by weighted forecast;
  monthly trend of opportunity close dates.
- **Service agent**: route and close an onboarding case with a resolution;
  identify the account with the most historical cases.
- **Sales manager (policy)**: decide whether a proposed discount/TCV combination
  requires Deal Desk, Compliance, or Finance approval, citing the matrix.

Every task must have a deterministic ground-truth answer computable from the tables.
