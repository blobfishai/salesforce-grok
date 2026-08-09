#!/usr/bin/env node
/**
 * Smoke test for the local mock Salesforce CRM MCP server (offline, no LLM).
 * Exercises the full lead-to-order enterprise flow plus reports and policy guards.
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { McpClient } from "../sim/lib/mcp-client.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const config = JSON.parse(readFileSync(join(ROOT, "config", "world.config.json"), "utf8"));

let passed = 0, failed = 0;
const check = (name, cond, extra = "") => {
  if (cond) { passed++; console.log(`PASS  ${name}`); }
  else { failed++; console.log(`FAIL  ${name}  ${extra}`); }
};

const mcp = new McpClient(config.mcpLocalFallback.command, config.mcpLocalFallback.args, { cwd: ROOT });

try {
  const init = await mcp.start();
  check("initialize handshake", init.serverInfo?.name === "salesforce-crm-mock", JSON.stringify(init.serverInfo));

  const tools = await mcp.listTools();
  check("tools/list has >= 16 tools", tools.length >= 16, `got ${tools.length}`);

  const world = await mcp.callTool("describe_world");
  check("describe_world marks data synthetic", world.data?.meta?.synthetic === true);

  const won = await mcp.callTool("soql_query", { query: "SELECT id, name, stage FROM Opportunity WHERE stage = 'Closed Won'" });
  check("SOQL: one seeded Closed Won opportunity", won.data?.totalSize === 1, won.text.slice(0, 120));

  const like = await mcp.callTool("soql_query", { query: "SELECT name FROM Account WHERE name LIKE '%Pension%'" });
  check("SOQL LIKE filter", like.data?.totalSize === 1);

  const conv = await mcp.callTool("convert_lead", { leadId: "00Q-2026-001" });
  check("convert_lead creates account+contact+opportunity", conv.ok
    && conv.data?.account?.newClient === true
    && conv.data?.opportunity?.stage === "Qualification"
    && conv.data?.opportunity?.amount === 450000
    && conv.data?.lead?.status === "Converted", conv.text.slice(0, 200));

  const quote = await mcp.callTool("generate_quote", { opportunityId: "006-2026-003", discountPct: 12 });
  const quoteId = quote.data?.id;
  check("generate_quote computes TCV (7.2M - 12%)", quote.ok && quote.data?.tcv === 6336000, quote.text.slice(0, 200));

  const sub = await mcp.callTool("submit_quote_for_approval", { quoteId });
  const roles = (sub.data?.approvalSteps ?? []).map((s) => s.role);
  check("approval chain = Deal Desk -> Compliance Officer", sub.data?.status === "In Approval"
    && JSON.stringify(roles) === JSON.stringify(["Deal Desk", "Compliance Officer"]), JSON.stringify(roles));

  const early = await mcp.callTool("convert_quote_to_order", { quoteId });
  check("guard: cannot convert before approval", early.ok === false);

  const wrongRole = await mcp.callTool("process_approval", { quoteId, role: "Finance", decision: "Approve" });
  check("guard: wrong approver role rejected", wrongRole.ok === false);

  const dd = await mcp.callTool("process_approval", { quoteId, role: "Deal Desk", decision: "Approve", actorUserId: "005-DD-001", comment: "Margin acceptable" });
  check("Deal Desk approval advances chain", dd.ok && dd.data?.status === "In Approval");

  const co = await mcp.callTool("process_approval", { quoteId, role: "Compliance Officer", decision: "Approve", actorUserId: "005-CO-001", comment: "KYC cleared for new sovereign client" });
  check("Compliance approval completes chain", co.ok && co.data?.status === "Approved");

  const ord = await mcp.callTool("convert_quote_to_order", { quoteId });
  const orderId = ord.data?.order?.id;
  check("quote converts to activated order, opp Closed Won", ord.ok
    && ord.data?.order?.status === "Activated"
    && ord.data?.opportunity?.stage === "Closed Won", ord.text.slice(0, 200));

  const guardWon = await mcp.callTool("update_opportunity_stage", { opportunityId: "006-2026-001", stage: "Closed Won" });
  check("guard: Closed Won unreachable by stage edit", guardWon.ok === false);

  const kase = await mcp.callTool("create_case", { accountId: "001-HEL-004", subject: "Helios — Treasury Settlement onboarding", priority: "High", relatedOpportunityId: "006-2026-003" });
  const closed = await mcp.callTool("close_case", { caseId: kase.data?.id, resolution: "Settlement accounts configured; client live." });
  check("case lifecycle open -> closed", kase.ok && kase.data?.status === "Open" && closed.ok && closed.data?.status === "Closed");

  const act = await mcp.callTool("log_activity", { type: "Call", subject: "Win call with Director of Treasury", relatedTo: "006-2026-003", userId: "005-EW-001" });
  check("log_activity", act.ok && act.data?.id?.startsWith("00T-"));

  const pipe = await mcp.callTool("pipeline_report");
  check("pipeline_report Closed Won total = $7,650,000", pipe.data?.byStage?.["Closed Won"]?.amount === 7650000, JSON.stringify(pipe.data?.byStage?.["Closed Won"]));

  const fc = await mcp.callTool("forecast_report");
  check("forecast totals (open 4.06M, weighted 2.0935M, won 7.65M)",
    fc.data?.totals?.openAmount === 4060000
    && fc.data?.totals?.weightedAmount === 2093500
    && fc.data?.totals?.wonAmount === 7650000, JSON.stringify(fc.data?.totals));

  const flow = await mcp.callTool("get_flow_state", { opportunityId: "006-2026-003" });
  check("get_flow_state = Order activated with case + activities", flow.data?.flowStage === "Order activated"
    && flow.data?.cases?.length === 1
    && (flow.data?.activities?.length ?? 0) >= 2, `stage=${flow.data?.flowStage} cases=${flow.data?.cases?.length} acts=${flow.data?.activities?.length}`);

  check("order id well-formed", typeof orderId === "string" && orderId.startsWith("801-"));
} catch (e) {
  failed++;
  console.error("FATAL", e);
} finally {
  mcp.close();
}

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
