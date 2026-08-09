#!/usr/bin/env node
/**
 * Mock Salesforce CRM MCP server — "Morgan Stanley (SIMULATED)" lead-to-order world.
 *
 * Zero-dependency MCP server over stdio (newline-delimited JSON-RPC 2.0).
 * Implements: initialize, ping, tools/list, tools/call, resources/list, resources/read.
 * All data is synthetic; state lives in memory for the life of the process.
 */
import { readFileSync } from "node:fs";
import { createInterface } from "node:readline";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SEED_PATH = join(ROOT, "data", "seed", "world-seed.json");
const seed = JSON.parse(readFileSync(SEED_PATH, "utf8"));
const state = structuredClone(seed);

const OBJECTS = {
  account: "accounts", contact: "contacts", lead: "leads", opportunity: "opportunities",
  quote: "quotes", order: "orders", case: "cases", activity: "activities",
  product: "products", user: "users",
};
const ID_FORMATS = {
  opportunities: { prefix: "006-2026-", pad: 3 },
  quotes: { prefix: "0Q0-2026-", pad: 3 },
  orders: { prefix: "801-2026-", pad: 3 },
  leads: { prefix: "00Q-2026-", pad: 3 },
  accounts: { prefix: "001-NEW-", pad: 3 },
  contacts: { prefix: "003-NEW-", pad: 3 },
  cases: { prefix: "500-2026-", pad: 4 },
  activities: { prefix: "00T-2026-", pad: 4 },
};

const today = () => new Date().toISOString().slice(0, 10);
const plusDays = (d) => new Date(Date.now() + d * 86400e3).toISOString().slice(0, 10);
const byId = (coll, id) => state[coll].find((r) => r.id === id);
const round2 = (n) => Math.round(n * 100) / 100;

function nextId(coll) {
  const { prefix, pad } = ID_FORMATS[coll];
  let n = state[coll].length + 1;
  let id;
  do { id = prefix + String(n++).padStart(pad, "0"); } while (byId(coll, id));
  return id;
}

function findAnywhere(id) {
  for (const coll of Object.values(OBJECTS)) {
    const rec = byId(coll, id);
    if (rec) return { coll, rec };
  }
  return null;
}

class ToolError extends Error {}
const need = (cond, msg) => { if (!cond) throw new ToolError(msg); };

// ---------------------------------------------------------------- SOQL subset
function runSoql(query) {
  const m = /^\s*SELECT\s+(.+?)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+?))?(?:\s+LIMIT\s+(\d+))?\s*$/i.exec(query);
  need(m, "Unsupported SOQL. Use: SELECT <fields|*> FROM <Object> [WHERE f op v [AND ...]] [LIMIT n]");
  const [, fieldPart, objName, wherePart, limitPart] = m;
  const coll = OBJECTS[objName.toLowerCase()];
  need(coll, `Unknown object '${objName}'. Objects: Account, Contact, Lead, Opportunity, Quote, Order, Case, Activity, Product, User`);

  let rows = state[coll].slice();
  if (wherePart) {
    const conds = wherePart.split(/\s+AND\s+/i).map((c) => {
      const cm = /^\s*(\w+)\s*(=|!=|>=|<=|>|<|LIKE)\s*(.+?)\s*$/i.exec(c);
      need(cm, `Bad WHERE clause: '${c}' (OR is not supported)`);
      let [, field, op, raw] = cm;
      let value;
      if (/^'.*'$/.test(raw)) value = raw.slice(1, -1);
      else if (/^(true|false)$/i.test(raw)) value = raw.toLowerCase() === "true";
      else if (!Number.isNaN(Number(raw))) value = Number(raw);
      else value = raw;
      return { field, op: op.toUpperCase(), value };
    });
    rows = rows.filter((r) =>
      conds.every(({ field, op, value }) => {
        const key = Object.keys(r).find((k) => k.toLowerCase() === field.toLowerCase());
        const v = key ? r[key] : undefined;
        switch (op) {
          case "=": return v === value;
          case "!=": return v !== value;
          case ">": return v > value;
          case "<": return v < value;
          case ">=": return v >= value;
          case "<=": return v <= value;
          case "LIKE": {
            const re = new RegExp("^" + String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace(/%/g, ".*") + "$", "i");
            return re.test(String(v));
          }
          default: return false;
        }
      })
    );
  }
  if (limitPart) rows = rows.slice(0, Number(limitPart));
  const fields = fieldPart.trim() === "*" ? null : fieldPart.split(",").map((f) => f.trim());
  const records = fields
    ? rows.map((r) => Object.fromEntries(fields.map((f) => {
        const key = Object.keys(r).find((k) => k.toLowerCase() === f.toLowerCase());
        return [key ?? f, key ? r[key] : null];
      })))
    : rows;
  return { totalSize: records.length, records };
}

// ------------------------------------------------------------- flow mechanics
function computeApprovalChain(quote) {
  const opp = byId("opportunities", quote.opportunityId);
  const account = byId("accounts", opp.accountId);
  const prods = opp.products.map((p) => byId("products", p.productId));
  const rules = state.approvalPolicy.rules;
  const triggered = [];
  if (quote.discountPct > rules["Deal Desk"].discountPctGt || quote.tcv > rules["Deal Desk"].tcvGt) {
    triggered.push({ role: "Deal Desk", reason: `discount ${quote.discountPct}% / TCV $${quote.tcv.toLocaleString()} vs policy (> ${rules["Deal Desk"].discountPctGt}% or > $${rules["Deal Desk"].tcvGt.toLocaleString()})` });
  }
  if (account.newClient || prods.some((p) => p.regulated)) {
    const why = [account.newClient ? "new client" : null, prods.some((p) => p.regulated) ? "regulated product(s)" : null].filter(Boolean).join(" + ");
    triggered.push({ role: "Compliance Officer", reason: why });
  }
  if (quote.tcv > rules["Finance"].tcvGt) {
    triggered.push({ role: "Finance", reason: `TCV $${quote.tcv.toLocaleString()} > $${rules["Finance"].tcvGt.toLocaleString()}` });
  }
  const order = state.approvalPolicy.sequence;
  triggered.sort((a, b) => order.indexOf(a.role) - order.indexOf(b.role));
  return triggered.map((t, i) => ({ step: i + 1, role: t.role, reason: t.reason, status: "Pending", actor: null, comment: null }));
}

const quarterOf = (dateStr) => {
  const [y, m] = dateStr.split("-").map(Number);
  return `${y}-Q${Math.ceil(m / 3)}`;
};

// ----------------------------------------------------------------- tool table
const TOOLS = [
  {
    name: "describe_world",
    description: "Describe the simulation world: org, business units, record counts, approval policy, stage probabilities, and the lead-to-order flow.",
    inputSchema: { type: "object", properties: {} },
    handler: () => ({
      meta: state.meta,
      businessUnits: state.businessUnits,
      recordCounts: Object.fromEntries(Object.values(OBJECTS).map((c) => [c, state[c].length])),
      approvalPolicy: state.approvalPolicy,
      flow: "convert_lead -> opportunity stages -> generate_quote -> submit_quote_for_approval -> process_approval (per step) -> convert_quote_to_order (Closed Won) -> create_case / log_activity -> pipeline_report / forecast_report",
    }),
  },
  {
    name: "soql_query",
    description: "Run a SOQL-like query. Syntax: SELECT <fields|*> FROM <Account|Contact|Lead|Opportunity|Quote|Order|Case|Activity|Product|User> [WHERE field op value [AND ...]] [LIMIT n]. Ops: = != > < >= <= LIKE ('%' wildcards). Strings in single quotes. No OR/joins.",
    inputSchema: { type: "object", properties: { query: { type: "string" } }, required: ["query"] },
    handler: ({ query }) => runSoql(query),
  },
  {
    name: "get_record",
    description: "Fetch one record by object name and id.",
    inputSchema: {
      type: "object",
      properties: {
        object: { type: "string", enum: ["Account", "Contact", "Lead", "Opportunity", "Quote", "Order", "Case", "Activity", "Product", "User"] },
        id: { type: "string" },
      },
      required: ["object", "id"],
    },
    handler: ({ object, id }) => {
      const coll = OBJECTS[object.toLowerCase()];
      need(coll, `Unknown object '${object}'`);
      const rec = byId(coll, id);
      need(rec, `${object} '${id}' not found`);
      return rec;
    },
  },
  {
    name: "list_accounts",
    description: "List client accounts, optionally filtered by segment, region, or new-client status.",
    inputSchema: {
      type: "object",
      properties: { segment: { type: "string" }, region: { type: "string" }, newClientOnly: { type: "boolean" } },
    },
    handler: ({ segment, region, newClientOnly } = {}) =>
      state.accounts.filter((a) =>
        (!segment || a.segment === segment) && (!region || a.region === region) && (!newClientOnly || a.newClient)),
  },
  {
    name: "convert_lead",
    description: "Convert a New/Working lead into Account + Contact + Opportunity (Salesforce lead conversion). The new account is flagged newClient; the opportunity starts at Qualification with the lead's product of interest.",
    inputSchema: { type: "object", properties: { leadId: { type: "string" }, ownerId: { type: "string" } }, required: ["leadId"] },
    handler: ({ leadId, ownerId }) => {
      const lead = byId("leads", leadId);
      need(lead, `Lead '${leadId}' not found`);
      need(["New", "Working"].includes(lead.status), `Lead is ${lead.status}; only New/Working leads can be converted`);
      const product = byId("products", lead.interestProductId);
      const account = {
        id: nextId("accounts"), name: lead.company, segment: lead.segment, region: lead.region,
        tier: "Silver", newClient: true, synthetic: true,
      };
      state.accounts.push(account);
      const contact = {
        id: nextId("contacts"), accountId: account.id, name: lead.contactName,
        title: "Primary Contact", email: lead.email, synthetic: true,
      };
      state.contacts.push(contact);
      const opp = {
        id: nextId("opportunities"), accountId: account.id,
        name: `${lead.company} — ${product ? product.name : "New Business"}`,
        stage: "Qualification", amount: product ? product.listPrice : 0,
        ownerId: ownerId ?? "005-EW-001",
        products: product ? [{ productId: product.id, qty: 1 }] : [],
        closeDate: plusDays(90), synthetic: true,
      };
      state.opportunities.push(opp);
      lead.status = "Converted";
      lead.convertedRefs = { accountId: account.id, contactId: contact.id, opportunityId: opp.id };
      return { lead, account, contact, opportunity: opp };
    },
  },
  {
    name: "create_opportunity",
    description: "Create a new opportunity for an existing account with product line items. Amount is computed from list prices. Stage starts at Qualification.",
    inputSchema: {
      type: "object",
      properties: {
        accountId: { type: "string" },
        name: { type: "string" },
        ownerId: { type: "string" },
        closeDate: { type: "string", description: "YYYY-MM-DD" },
        products: {
          type: "array",
          items: { type: "object", properties: { productId: { type: "string" }, qty: { type: "number" } }, required: ["productId", "qty"] },
          minItems: 1,
        },
      },
      required: ["accountId", "name", "products", "closeDate"],
    },
    handler: ({ accountId, name, ownerId, products, closeDate }) => {
      need(byId("accounts", accountId), `Account '${accountId}' not found`);
      let amount = 0;
      for (const line of products) {
        const p = byId("products", line.productId);
        need(p, `Product '${line.productId}' not found`);
        need(line.qty > 0, "qty must be > 0");
        amount += p.listPrice * line.qty;
      }
      const opp = {
        id: nextId("opportunities"), accountId, name, stage: "Qualification",
        amount, ownerId: ownerId ?? "005-EW-001", products, closeDate, synthetic: true,
      };
      state.opportunities.push(opp);
      return opp;
    },
  },
  {
    name: "update_opportunity_stage",
    description: "Move an opportunity to a new stage. 'Closed Won' is not allowed here — it is reached only by converting an approved quote to an order.",
    inputSchema: {
      type: "object",
      properties: { opportunityId: { type: "string" }, stage: { type: "string" } },
      required: ["opportunityId", "stage"],
    },
    handler: ({ opportunityId, stage }) => {
      const opp = byId("opportunities", opportunityId);
      need(opp, `Opportunity '${opportunityId}' not found`);
      need(state.meta.stages.includes(stage), `Invalid stage '${stage}'. Valid: ${state.meta.stages.join(", ")}`);
      need(stage !== "Closed Won", "Policy: Closed Won is only reachable via convert_quote_to_order");
      need(!opp.stage.startsWith("Closed"), `Opportunity is already ${opp.stage}`);
      opp.stage = stage;
      return opp;
    },
  },
  {
    name: "generate_quote",
    description: "Generate a CPQ quote from an opportunity's product lines with a discount percentage. Computes TCV. Quote starts as Draft.",
    inputSchema: {
      type: "object",
      properties: {
        opportunityId: { type: "string" },
        discountPct: { type: "number", description: "0-100" },
      },
      required: ["opportunityId", "discountPct"],
    },
    handler: ({ opportunityId, discountPct }) => {
      const opp = byId("opportunities", opportunityId);
      need(opp, `Opportunity '${opportunityId}' not found`);
      need(!opp.stage.startsWith("Closed"), `Cannot quote a ${opp.stage} opportunity`);
      need(discountPct >= 0 && discountPct < 100, "discountPct must be in [0, 100)");
      const list = opp.products.reduce((s, l) => s + byId("products", l.productId).listPrice * l.qty, 0);
      const quote = {
        id: nextId("quotes"), opportunityId, discountPct,
        listTotal: list, tcv: round2(list * (1 - discountPct / 100)),
        status: "Draft", approvalSteps: [], createdDate: today(), synthetic: true,
      };
      state.quotes.push(quote);
      return quote;
    },
  },
  {
    name: "submit_quote_for_approval",
    description: "Submit a Draft quote for approval. The chain (Deal Desk / Compliance Officer / Finance) is computed from policy. Auto-approves when no rule triggers.",
    inputSchema: { type: "object", properties: { quoteId: { type: "string" } }, required: ["quoteId"] },
    handler: ({ quoteId }) => {
      const quote = byId("quotes", quoteId);
      need(quote, `Quote '${quoteId}' not found`);
      need(quote.status === "Draft", `Quote is ${quote.status}; only Draft quotes can be submitted`);
      quote.approvalSteps = computeApprovalChain(quote);
      quote.status = quote.approvalSteps.length === 0 ? "Approved" : "In Approval";
      return quote;
    },
  },
  {
    name: "process_approval",
    description: "Approve or reject the CURRENT pending approval step of a quote. The acting role must match that step's approver role.",
    inputSchema: {
      type: "object",
      properties: {
        quoteId: { type: "string" },
        role: { type: "string", enum: ["Deal Desk", "Compliance Officer", "Finance"] },
        decision: { type: "string", enum: ["Approve", "Reject"] },
        actorUserId: { type: "string" },
        comment: { type: "string" },
      },
      required: ["quoteId", "role", "decision"],
    },
    handler: ({ quoteId, role, decision, actorUserId, comment }) => {
      const quote = byId("quotes", quoteId);
      need(quote, `Quote '${quoteId}' not found`);
      need(quote.status === "In Approval", `Quote is ${quote.status}; nothing to approve`);
      const current = quote.approvalSteps.find((s) => s.status === "Pending");
      need(current, "No pending approval step");
      need(current.role === role, `Current pending step ${current.step} requires role '${current.role}', not '${role}'`);
      current.status = decision === "Approve" ? "Approved" : "Rejected";
      current.actor = actorUserId ?? null;
      current.comment = comment ?? null;
      current.decidedDate = today();
      if (decision === "Reject") quote.status = "Rejected";
      else if (quote.approvalSteps.every((s) => s.status === "Approved")) quote.status = "Approved";
      return quote;
    },
  },
  {
    name: "convert_quote_to_order",
    description: "Convert a fully Approved quote into an activated Order. Marks the opportunity Closed Won (the only path to Closed Won).",
    inputSchema: { type: "object", properties: { quoteId: { type: "string" } }, required: ["quoteId"] },
    handler: ({ quoteId }) => {
      const quote = byId("quotes", quoteId);
      need(quote, `Quote '${quoteId}' not found`);
      need(quote.status === "Approved", `Quote must be fully Approved to convert (currently ${quote.status})`);
      const order = { id: nextId("orders"), quoteId, status: "Activated", tcv: quote.tcv, activatedDate: today(), synthetic: true };
      state.orders.push(order);
      quote.status = "Converted";
      const opp = byId("opportunities", quote.opportunityId);
      opp.stage = "Closed Won";
      return { order, quote: { id: quote.id, status: quote.status }, opportunity: { id: opp.id, stage: opp.stage } };
    },
  },
  {
    name: "create_case",
    description: "Open a service case for an account (e.g., client onboarding after a won deal), optionally linked to an opportunity.",
    inputSchema: {
      type: "object",
      properties: {
        accountId: { type: "string" },
        subject: { type: "string" },
        priority: { type: "string", enum: ["Low", "Medium", "High"] },
        relatedOpportunityId: { type: "string" },
      },
      required: ["accountId", "subject", "priority"],
    },
    handler: ({ accountId, subject, priority, relatedOpportunityId }) => {
      need(byId("accounts", accountId), `Account '${accountId}' not found`);
      if (relatedOpportunityId) need(byId("opportunities", relatedOpportunityId), `Opportunity '${relatedOpportunityId}' not found`);
      const c = {
        id: nextId("cases"), accountId, subject, priority, status: "Open",
        relatedOpportunityId: relatedOpportunityId ?? null, openedDate: today(), closedDate: null, resolution: null, synthetic: true,
      };
      state.cases.push(c);
      return c;
    },
  },
  {
    name: "close_case",
    description: "Close an open case with a resolution note.",
    inputSchema: {
      type: "object",
      properties: { caseId: { type: "string" }, resolution: { type: "string" } },
      required: ["caseId", "resolution"],
    },
    handler: ({ caseId, resolution }) => {
      const c = byId("cases", caseId);
      need(c, `Case '${caseId}' not found`);
      need(c.status === "Open", `Case is ${c.status}`);
      c.status = "Closed";
      c.closedDate = today();
      c.resolution = resolution;
      return c;
    },
  },
  {
    name: "log_activity",
    description: "Log a Call, Email, Meeting, or Task activity against any record (account, opportunity, case, lead, ...).",
    inputSchema: {
      type: "object",
      properties: {
        type: { type: "string", enum: ["Call", "Email", "Meeting", "Task"] },
        subject: { type: "string" },
        relatedTo: { type: "string", description: "id of any existing record" },
        userId: { type: "string" },
        notes: { type: "string" },
      },
      required: ["type", "subject", "relatedTo"],
    },
    handler: ({ type, subject, relatedTo, userId, notes }) => {
      need(findAnywhere(relatedTo), `No record found with id '${relatedTo}'`);
      const a = {
        id: nextId("activities"), type, subject, relatedTo,
        userId: userId ?? "005-EW-001", date: today(), notes: notes ?? null, synthetic: true,
      };
      state.activities.push(a);
      return a;
    },
  },
  {
    name: "pipeline_report",
    description: "Opportunity pipeline grouped by stage: count and total amount, plus open-pipeline total.",
    inputSchema: { type: "object", properties: {} },
    handler: () => {
      const byStage = {};
      for (const stage of state.meta.stages) byStage[stage] = { count: 0, amount: 0 };
      for (const o of state.opportunities) {
        byStage[o.stage].count += 1;
        byStage[o.stage].amount += o.amount;
      }
      const open = state.opportunities.filter((o) => !o.stage.startsWith("Closed"));
      return { byStage, openPipeline: { count: open.length, amount: open.reduce((s, o) => s + o.amount, 0) } };
    },
  },
  {
    name: "forecast_report",
    description: "Weighted forecast by close-date quarter: open pipeline weighted by stage probability (Qualification 10%, Discovery 25%, Proposal 50%, Negotiation 75%) plus Closed Won amounts.",
    inputSchema: { type: "object", properties: {} },
    handler: () => {
      const prob = state.meta.stageProbability;
      const quarters = {};
      for (const o of state.opportunities) {
        const q = quarterOf(o.closeDate);
        quarters[q] ??= { quarter: q, openAmount: 0, weightedAmount: 0, wonAmount: 0 };
        if (o.stage === "Closed Won") quarters[q].wonAmount += o.amount;
        else if (o.stage !== "Closed Lost") {
          quarters[q].openAmount += o.amount;
          quarters[q].weightedAmount += o.amount * (prob[o.stage] ?? 0);
        }
      }
      const rows = Object.values(quarters).sort((a, b) => a.quarter.localeCompare(b.quarter))
        .map((r) => ({ ...r, weightedAmount: round2(r.weightedAmount) }));
      return {
        stageProbability: prob,
        quarters: rows,
        totals: {
          openAmount: round2(rows.reduce((s, r) => s + r.openAmount, 0)),
          weightedAmount: round2(rows.reduce((s, r) => s + r.weightedAmount, 0)),
          wonAmount: round2(rows.reduce((s, r) => s + r.wonAmount, 0)),
        },
      };
    },
  },
  {
    name: "get_flow_state",
    description: "Show where an opportunity sits in the lead-to-order flow: its quotes, approval steps, orders, related cases, and activities.",
    inputSchema: { type: "object", properties: { opportunityId: { type: "string" } }, required: ["opportunityId"] },
    handler: ({ opportunityId }) => {
      const opp = byId("opportunities", opportunityId);
      need(opp, `Opportunity '${opportunityId}' not found`);
      const quotes = state.quotes.filter((q) => q.opportunityId === opportunityId);
      const orders = state.orders.filter((o) => quotes.some((q) => q.id === o.quoteId));
      const cases = state.cases.filter((c) => c.relatedOpportunityId === opportunityId);
      const activities = state.activities.filter((a) => a.relatedTo === opportunityId);
      const flowStage = orders.length ? "Order activated"
        : quotes.some((q) => q.status === "Approved") ? "Quote approved"
        : quotes.some((q) => q.status === "In Approval") ? "In approval"
        : quotes.some((q) => q.status === "Rejected") ? "Quote rejected"
        : quotes.length ? "Quoted"
        : "Pre-quote";
      return { flowStage, opportunity: opp, quotes, orders, cases, activities };
    },
  },
];

// --------------------------------------------------------------- MCP plumbing
const SERVER_INFO = { name: "salesforce-crm-mock", version: "1.0.0" };
const RESOURCES = [
  { uri: "crm://world/seed", name: "World seed data", mimeType: "application/json", get: () => seed },
  { uri: "crm://world/state", name: "Live world state", mimeType: "application/json", get: () => state },
  { uri: "crm://world/policy", name: "CPQ approval policy", mimeType: "application/json", get: () => state.approvalPolicy },
];

const send = (msg) => process.stdout.write(JSON.stringify(msg) + "\n");
const reply = (id, result) => send({ jsonrpc: "2.0", id, result });
const replyErr = (id, code, message) => send({ jsonrpc: "2.0", id, error: { code, message } });

function handle(msg) {
  const { id, method, params = {} } = msg;
  const isNotification = id === undefined || id === null;
  try {
    switch (method) {
      case "initialize":
        return reply(id, {
          protocolVersion: params.protocolVersion ?? "2025-06-18",
          capabilities: { tools: { listChanged: false }, resources: {} },
          serverInfo: SERVER_INFO,
          instructions:
            "Simulated Salesforce CRM for 'Morgan Stanley (SIMULATED)'. All data is synthetic. " +
            "Lead-to-order flow: convert_lead, advance opportunity stages, generate_quote, submit_quote_for_approval, " +
            "process_approval per pending step, convert_quote_to_order (Closed Won), then create_case/log_activity and reports.",
        });
      case "notifications/initialized":
      case "notifications/cancelled":
        return;
      case "ping":
        return reply(id, {});
      case "tools/list":
        return reply(id, { tools: TOOLS.map(({ name, description, inputSchema }) => ({ name, description, inputSchema })) });
      case "tools/call": {
        const tool = TOOLS.find((t) => t.name === params.name);
        if (!tool) return replyErr(id, -32602, `Unknown tool '${params.name}'`);
        try {
          const result = tool.handler(params.arguments ?? {});
          return reply(id, { content: [{ type: "text", text: JSON.stringify(result, null, 2) }], isError: false });
        } catch (e) {
          if (e instanceof ToolError) {
            return reply(id, { content: [{ type: "text", text: `ERROR: ${e.message}` }], isError: true });
          }
          throw e;
        }
      }
      case "resources/list":
        return reply(id, { resources: RESOURCES.map(({ uri, name, mimeType }) => ({ uri, name, mimeType })) });
      case "resources/read": {
        const res = RESOURCES.find((r) => r.uri === params.uri);
        if (!res) return replyErr(id, -32602, `Unknown resource '${params.uri}'`);
        return reply(id, { contents: [{ uri: res.uri, mimeType: res.mimeType, text: JSON.stringify(res.get(), null, 2) }] });
      }
      default:
        if (!isNotification) return replyErr(id, -32601, `Method not found: ${method}`);
    }
  } catch (e) {
    if (!isNotification) return replyErr(id, -32603, `Internal error: ${e.message}`);
    process.stderr.write(`[salesforce-crm-mock] error in ${method}: ${e.stack}\n`);
  }
}

const rl = createInterface({ input: process.stdin, terminal: false });
rl.on("line", (line) => {
  if (!line.trim()) return;
  let msg;
  try { msg = JSON.parse(line); } catch { return replyErr(null, -32700, "Parse error"); }
  handle(msg);
});
rl.on("close", () => process.exit(0));
process.stderr.write(`[salesforce-crm-mock] ready — ${TOOLS.length} tools, seed: ${SEED_PATH}\n`);
