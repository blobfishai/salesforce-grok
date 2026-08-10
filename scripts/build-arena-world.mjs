#!/usr/bin/env node
/**
 * Build the ARENA world — tasks modeled on real eval suites (CRMArena / CRMArena-Pro
 * task types), anchored in the world's own data + seeded input documents, with
 * ground truth COMPUTED from the data at build time and CRMArena-style answer
 * matching (exact / fuzzy / set).
 *
 * Task types: case_routing, top_issue_identification, handle_time (resolver
 * analytics), lead_qualification (BANT), policy_violation_identification (quote
 * vs KB articles), named_entity_disambiguation.
 *
 * Levels: 1 baseline · 2 hardened (conflicting policy revisions, near-tie data,
 * decoy KB articles, superseding notes, extra name collisions).
 *
 * Usage: node scripts/build-arena-world.mjs [--level 1|2]
 * Output: world/arena/package/<id>/ + world/arena/arena-tasks.json
 */
import { readFileSync, writeFileSync, mkdirSync, cpSync, rmSync } from "node:fs";
import { execSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SRC_ID = "sbx_7d7d8fedcecb4458";
const SRC = join(ROOT, "world", "blobfish", "package", SRC_ID);
const OUT = join(ROOT, "world", "arena", "package", SRC_ID);
const LEVEL = Number(process.argv.includes("--level") ? process.argv[process.argv.indexOf("--level") + 1] : 1);

rmSync(join(ROOT, "world", "arena"), { recursive: true, force: true });
mkdirSync(OUT, { recursive: true });
cpSync(SRC, OUT, { recursive: true });
for (const f of ["state.db", "seed.db"]) rmSync(join(OUT, f), { force: true });
rmSync(join(OUT, ".sessions"), { recursive: true, force: true });
rmSync(join(OUT, "traces"), { recursive: true, force: true });

const raw = JSON.parse(readFileSync(join(OUT, "world.json"), "utf8"));
const world = raw.world ?? raw;
const T = Object.fromEntries((world.tables ?? []).map((t) => [t.name, t]));
const rows = (n) => T[n].sample_rows;

// ------------------------------------------------------------------ analytics ground truth
const CATS = ["Billing discrepancy", "Problem updating", "Cannot access", "Question about"];
const catOf = (s) => CATS.find((c) => String(s).startsWith(c)) ?? "Other";
const DONE = new Set(["resolved", "closed"]);
const ACTIVE = new Set(["open", "in_progress", "waiting_customer"]);
const emp = Object.fromEntries(rows("employees").map((e) => [e.id, e]));

// exclude on_leave / terminated agents per routing policy
const eligible = (e) => e && e.status === "active";
// level 2 pulls the analytics window back to one quarter (level-1 turned out
// beyond the model's paging horizon — always-fail means too hard, per protocol)
const WIN = LEVEL >= 2 ? ["2025-10-01", "2025-12-31"] : ["2025-07-01", "2025-12-31"];
const stats = {};
for (const t of rows("support_tickets")) {
  const s = (stats[t.assignee_employee_id] ??= { done: 0, doneByCat: {}, active: 0, doneH2: 0 });
  if (DONE.has(t.status)) {
    s.done++;
    s.doneByCat[catOf(t.subject)] = (s.doneByCat[catOf(t.subject)] ?? 0) + 1;
    if (t.opened_at >= WIN[0] && t.opened_at <= WIN[1]) s.doneH2++;
  } else if (ACTIVE.has(t.status)) s.active++;
}
const rank = (metric) => Object.entries(stats)
  .filter(([id]) => eligible(emp[id]))
  .sort((a, b) => metric(b[1]) - metric(a[1]) || a[1].active - b[1].active || String(emp[a[0]].hire_date).localeCompare(String(emp[b[0]].hire_date)));

const routeCat = "Billing discrepancy";
const routedTo = rank((s) => s.doneByCat[routeCat] ?? 0)[0];
const activeByCat = {};
for (const t of rows("support_tickets")) if (ACTIVE.has(t.status)) activeByCat[catOf(t.subject)] = (activeByCat[catOf(t.subject)] ?? 0) + 1;
const topIssue = Object.entries(activeByCat).sort((a, b) => b[1] - a[1])[0];

// near-tie injection at level 2: bump the runner-up within 1 resolved billing ticket
if (LEVEL >= 2) {
  const [winner, runner] = rank((s) => s.doneByCat[routeCat] ?? 0);
  const need = (winner[1].doneByCat[routeCat] ?? 0) - (runner[1].doneByCat[routeCat] ?? 0) - 1;
  let maxTid = Math.max(...rows("support_tickets").map((r) => Number(r.id)));
  for (let i = 0; i < need; i++) {
    rows("support_tickets").push({ id: ++maxTid, ticket_number: `TKT-9${String(70000 + i)}`, subject: "Billing discrepancy in fee schedule", customer_name: "Halstead Fund", priority: "medium", assignee_employee_id: Number(runner[0]), opened_at: "2025-11-0" + ((i % 9) + 1), business_unit_id: 1, status: "resolved" });
    runner[1].doneByCat[routeCat] = (runner[1].doneByCat[routeCat] ?? 0) + 1;
  }
  T.support_tickets.row_count = rows("support_tickets").length;
}
const routedToFinal = rank((s) => s.doneByCat[routeCat] ?? 0)[0];

// handle_time GT must be computed AFTER near-tie injection: injected tickets are
// resolved and opened inside the analytics window, so they count toward doneH2.
// (2026-08-10 audit: the pre-injection GT was stale AND degenerate — every agent
// had zero in-window completions, so the "winner" was pure tie-break; three
// models found the true post-injection answer and were scored wrong.)
for (const s of Object.values(stats)) s.doneH2 = 0;
for (const t of rows("support_tickets")) {
  if (DONE.has(t.status) && t.opened_at >= WIN[0] && t.opened_at <= WIN[1]) {
    (stats[t.assignee_employee_id] ??= { done: 0, doneByCat: {}, active: 0, doneH2: 0 }).doneH2++;
  }
}
const busiest = rank((s) => s.doneH2)[0];
if (!busiest || (busiest[1].doneH2 ?? 0) === 0) {
  throw new Error(`handle_time window ${WIN} is degenerate: no eligible agent completed any in-window ticket — GT would be pure tie-break`);
}

// ------------------------------------------------------------------ seeded input documents
const docs = T.agent_documents;
let docId = Math.max(0, ...rows("agent_documents").map((r) => Number(r.id)));
const addDoc = (title, body, updated_at = "2026-06-01T09:00:00Z") => {
  rows("agent_documents").push({ id: ++docId, title, body, updated_at });
  docs.row_count = rows("agent_documents").length;
  return title;
};

const seeded = [];
seeded.push(addDoc(
  "Case Routing Policy (rev. 2 — CURRENT)",
  `Effective 2026-06-01, supersedes rev. 1. Issue categories are determined by the ticket subject prefix: "Billing discrepancy", "Problem updating", "Cannot access", "Question about". ` +
  `A new case routes to the ELIGIBLE agent who has completed (status resolved or closed) the most support tickets in the case's category. ` +
  `Eligibility: employees with status "active" only — agents on leave or terminated are never routed. ` +
  `Tie-break 1: fewer currently active tickets (open, in_progress, waiting_customer). Tie-break 2: earlier hire_date. Answer with the agent's employee_number.`
));
if (LEVEL >= 2) seeded.push(addDoc(
  "Case Routing Policy (rev. 1)",
  `[SUPERSEDED] Route new cases to the agent with the most total completed tickets regardless of category. All employees are eligible.`,
  "2025-03-10T09:00:00Z"
));

seeded.push(addDoc(
  "KB-101 — Discount Authority Policy",
  `Quotes may carry at most 15% discount without Deal Desk approval, and never more than 20% in an Approved state under any authority. Any Approved quote above 20% is out of policy.`
));
seeded.push(addDoc(
  "KB-102 — Regulated Product Approval Chain",
  `Quotes containing regulated products require the Compliance step recorded before approval.`
));
seeded.push(addDoc(
  "KB-103 — Payment Terms Standard",
  `Net-30 is standard; anything longer than Net-60 requires Finance sign-off.`
));
if (LEVEL >= 2) seeded.push(addDoc(
  "KB-104 — Promotional Discount Windows",
  `During declared promotional windows, list prices may be reduced at the catalog level. This policy does not change quote discount ceilings (see KB-101).`
));

const notesV1 =
  `Call 1 (2026-05-02): Riverside operations lead confirmed a approved budget envelope of $120k for this initiative; procurement has the PO template ready. ` +
  `Call 2 (2026-05-16): Clear need — their manual reconciliation runs 11 hours/week and misses SLAs; they want go-live inside Q4, and the project plan shows a committed timeline. ` +
  `Call 3 (2026-06-03): Our champion is an operations manager who cannot sign; the CFO (economic buyer) has not joined any call and deferred twice. No signature authority has been established.`;
const notesV2 =
  `Update (2026-07-21, supersedes earlier notes where they conflict): The CFO joined the last call and confirmed signing authority is resolved. ` +
  `However, group finance froze the initiative budget pending the H2 review — the $120k envelope is no longer approved. Need and timeline are unchanged.`;
seeded.push(addDoc("Lead Discussion Notes — Riverside Contact", notesV1, "2026-06-03T17:00:00Z"));
if (LEVEL >= 2) seeded.push(addDoc("Lead Discussion Notes — Riverside Contact (update)", notesV2, "2026-07-21T17:00:00Z"));

// NED collision employee(s)
let empMax = Math.max(...rows("employees").map((r) => Number(r.id)));
const target = rows("employees").find((e) => e.id === 1); // David Brown, dept 1, hired 2025
rows("employees").push({ id: ++empMax, employee_number: "EMP-556801", name: "David Brown", email: "contact55911@morganstanleysimulated.com", job_title: "Compliance Analyst", department_id: 4, hire_date: "2022-03-01", status: "active" });
if (LEVEL >= 2) rows("employees").push({ id: ++empMax, employee_number: "EMP-771204", name: "David Brown", email: "contact77425@morganstanleysimulated.com", job_title: "Sales Manager", department_id: 1, hire_date: "2021-09-20", status: "on_leave" });
T.employees.row_count = rows("employees").length;

// ------------------------------------------------------------------ the arena tasks (real eval formulations)
const tasks = [
  {
    id: "arena_case_routing", type: "case_routing", metric: "exact",
    gt: routedToFinal ? emp[routedToFinal[0]].employee_number : null,
    docs: ["Case Routing Policy (rev. 2 — CURRENT)"],
    prompt:
      `Use the case routing policy in the document store to determine the most suitable agent for the given case. Return only the employee number of the agent.\n` +
      `## Given Case\n- Case Subject: Billing discrepancy on Q3 custody statement\n- Case Description: The client reports fee lines on the Q3 custody statement that do not match the agreed schedule and requests correction.`,
  },
  {
    id: "arena_top_issue", type: "top_issue_identification", metric: "fuzzy",
    gt: topIssue[0],
    docs: [],
    prompt: `Identify the most common issue category among support tickets that are still active (status open, in_progress, or waiting_customer). The issue category is the ticket subject's leading phrase. Return only the category name.`,
  },
  {
    id: "arena_handle_time", type: "handle_time", metric: "exact",
    gt: busiest ? emp[busiest[0]].employee_number : null,
    docs: ["Case Routing Policy (rev. 2 — CURRENT)"],
    prompt: `Per the routing policy's definitions of completed tickets and eligibility, identify the agent who completed the most support tickets opened between ${WIN[0]} and ${WIN[1]}. Return only the employee number of the agent.`,
  },
  {
    id: "arena_lead_qualification", type: "lead_qualification", metric: "set",
    gt: LEVEL >= 2 ? ["Budget"] : ["Authority"],
    docs: LEVEL >= 2 ? ["Lead Discussion Notes — Riverside Contact", "Lead Discussion Notes — Riverside Contact (update)"] : ["Lead Discussion Notes — Riverside Contact"],
    prompt:
      `Based on the latest discussion notes for the lead "Riverside Contact" in the document store, can this lead be qualified? ` +
      `If the answer is no, which factors—'Budget', 'Authority', 'Need', or 'Timeline'—are responsible? Return only one or several of the four BANT factors, or 'None' if the lead qualifies.`,
  },
  {
    id: "arena_policy_violation", type: "policy_violation_identification", metric: "exact",
    gt: "KB-101",
    docs: ["KB-101 — Discount Authority Policy", "KB-102 — Regulated Product Approval Chain", "KB-103 — Payment Terms Standard"],
    prompt:
      `Does the price and configuration of quote id 1 comply with company policy as written in the knowledge base? ` +
      `If it does not, return only the Id of the knowledge article being violated (e.g. KB-102). If no violation is found, return None.`,
  },
  {
    id: "arena_ned", type: "named_entity_disambiguation", metric: "exact",
    gt: target.employee_number,
    docs: [],
    prompt:
      `More than one employee is named David Brown. Return only the employee number of the David Brown who works in department 1 and was hired in 2025.`,
  },
];

writeFileSync(join(OUT, "world.json"), JSON.stringify(raw, null, 1));
execSync("python3 create_db.py", { cwd: OUT, stdio: "inherit" });
execSync("cp seed.db state.db", { cwd: OUT });
writeFileSync(join(ROOT, "world", "arena", "arena-tasks.json"), JSON.stringify({ level: LEVEL, worldId: SRC_ID, builtAt: new Date().toISOString(), seededDocs: seeded, tasks }, null, 2));
cpSync(join(OUT, "world.json"), join(ROOT, "world", "arena", "world.json"));

console.log(`ARENA world level ${LEVEL} — ${tasks.length} real-eval-anchored tasks, ${seeded.length} seeded input documents`);
for (const t of tasks) console.log(`  ${t.id} [${t.type}] metric=${t.metric} gt=${JSON.stringify(t.gt)}`);
console.log("seeded docs:", seeded.join(" | "));
