# Anchor PRD — Simulated Morgan Stanley Salesforce ERP (Quote-to-Cash)

> SIMULATION ONLY. All entities are synthetic. This document describes a fictional
> sandbox modeled on a bulge-bracket investment bank ("Morgan Stanley (SIMULATED)").
> It is not affiliated with, endorsed by, or representative of Morgan Stanley.

## Domain
Revenue operations (quote-to-cash) for institutional financial products sold by a
simulated investment bank through a Salesforce-style ERP/CRM.

## Business Units
- Institutional Securities
- Wealth Management
- Investment Management

## Object Schemas

### Account
- id: string (001-*)
- name: string
- segment: enum [Hedge Fund, Pension, Private Equity, Sovereign Wealth, Insurance]
- region: enum [AMER, EMEA, APAC]
- tier: enum [Platinum, Gold, Silver]
- newClient: boolean

### Contact
- id: string (003-*)
- accountId: ref Account
- name: string
- title: string
- email: string (fictional domain)

### Product
- id: string (01t-*)
- name: string
- family: string (business unit)
- listPrice: number (USD, annual)
- regulated: boolean (triggers Compliance review)
- revRecMonths: number (straight-line revenue recognition period)

### Opportunity
- id: string (006-*)
- accountId: ref Account
- name: string
- stage: enum [Qualification, Discovery, Proposal, Negotiation, Closed Won, Closed Lost]
- amount: number (sum of list prices x qty)
- ownerId: ref User
- products: array of { productId, qty }
- closeDate: date

### Quote
- id: string (0Q0-*)
- opportunityId: ref Opportunity
- discountPct: number
- tcv: number (total contract value after discount)
- status: enum [Draft, In Approval, Approved, Rejected, Converted]
- approvalSteps: array of { step, role, status, actor, comment }

### Order
- id: string (801-*)
- quoteId: ref Quote
- status: enum [Activated, Cancelled]
- tcv: number
- activatedDate: date

### Invoice
- id: string (INV-*)
- orderId: ref Order
- amountDue: number
- terms: Net-30
- status: enum [Issued, Paid, Overdue]

### Payment
- id: string (PAY-*)
- invoiceId: ref Invoice
- amount: number
- receivedDate: date

## Enterprise Flow (SOP): Quote-to-Cash
1. Account Executive opens an Opportunity with products (stage Qualification → Negotiation).
2. Generate a Quote from the Opportunity with a discount percentage; TCV computed.
3. Submit the Quote for approval. The approval chain is computed from the matrix below
   and must be processed sequentially. Any rejection halts the flow.
4. Once fully Approved, convert the Quote to an Order (activates it, Opportunity → Closed Won).
5. Generate a Net-30 Invoice from the activated Order.
6. Record Payment against the Invoice; ledger updated.
7. Revenue is recognized straight-line over each product's revRecMonths.

## Approval Matrix
| Step order | Approver role      | Triggered when                                        |
|------------|--------------------|-------------------------------------------------------|
| 1          | Deal Desk          | discountPct > 15 OR quote TCV > $5,000,000            |
| 2          | Compliance Officer | account.newClient = true OR any product.regulated     |
| 3          | Finance (CFO del.) | quote TCV > $25,000,000                               |

If no rule triggers, the quote auto-approves. Closed Won may only be reached via
quote-to-order conversion, never by direct stage edit.

## Invariants (verifiable)
- An Order must reference a Quote with status Approved.
- Invoice.amountDue equals Order.tcv.
- Invoice becomes Paid only when payments received >= amountDue.
- A rejected Quote can never be converted.
- Sum(recognized revenue) <= Sum(activated Order tcv).

## Example Tasks for the Sandbox
- Approve a blocked high-value quote through the full Deal Desk → Compliance chain.
- Detect and reject a quote whose discount exceeds policy without Deal Desk sign-off.
- Reconcile an invoice that was paid short and report the AR gap.
- Produce a pipeline report by stage and a revenue-recognition schedule.
