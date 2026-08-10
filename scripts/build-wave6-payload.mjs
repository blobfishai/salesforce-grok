#!/usr/bin/env node
/**
 * Assemble the wave-6 deep-job payload: max-complexity revenue-operations world.
 * Anchors = full wave2 corpus (18 files) + wave6 corpus (26 files: 12 new workflow
 * categories + artifact documents). Mock services = the full vendored GTM stack,
 * explicit list (the 2-service auto-resolution cap only applies to prompt matching).
 *
 * Usage: node scripts/build-wave6-payload.mjs > /tmp/wave6-payload.json
 */
import { readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");

const PROMPT = `Maximum-complexity revenue-operations simulation world for the fictional bulge-bracket investment bank "Morgan Stanley (SIMULATED)". Evolve the existing Salesforce CRM (Sales Cloud + Service Cloud) lead-to-order world into the FULL B2B revenue lifecycle across an integrated GTM stack: (1) lead capture and enrichment waterfall with ICP scoring and intent signals; (2) inbound routing with an MQL->SAL acceptance gate; (3) outbound email sequencing with reply classification on SendGrid-style email infrastructure; (4) dialer plus conversation intelligence with diarized call transcripts and MEDDIC scorecards; (5) meeting scheduling with round-robin assignment on Google Calendar; (6) CRM core lead->contact->account->opportunity->quote->order in Salesforce; (7) CPQ with tiered discount authority and the sequential Deal Desk -> Compliance -> Finance approval matrix; (8) contract lifecycle and e-signature with a clause library and customer-first countersign order; (9) Stripe-style billing: subscriptions, invoices, payments, a dunning ladder, refunds/credits and proration reconciled against activated orders; (10) forecasting and pipeline inspection with commit categories and stale-deal rules; (11) customer success: weighted health scores, churn playbooks, EBR cadence, renewals on a 120-day timeline with uplift policy; (12) support cases with SLA tiers on Intercom-style ticketing; (13) territory, quota and compensation including deal splits and commission statements; (14) marketing automation: campaigns, nurture tracks, an MQL->SQL handoff SLA, consent and suppression lists; (15) sales enablement: battlecards against three named fictional competitors and content engagement tracking; (16) proposals/RFP responses with a security-questionnaire answer library; (17) analytics and reporting with exact KPI formulas; (18) RevOps data hygiene: duplicate detection, merges, and a webhook event bus between systems; (19) partner deal registration with conflict windows and margin tiers. Slack-style deal-room messaging carries approvals and escalations, Gmail-style correspondence threads, a Notion-style knowledge base holds the SOP corpus, Google Drive/Sheets document stores hold the artifacts (MSAs, order forms, rate cards, call transcripts, commission statements, win/loss reports), NetSuite-style order records reconcile billing, and Workday-style rep rosters carry quotas. Deep multi-hop cross-system workflows with strict policy gates from the anchor SOPs; cross-system invariants (closed-won opportunity => executed order form => activated order => subscription => invoice => payment) and document-grounded decisions where the agent must read the governing SOP or artifact before acting. All data synthetic.`;

// tool_limit: <=0 means ALL of the service's operations; positive caps the mount.
const MOCK_SERVICES = [
  { service: "salesforce", tool_limit: 0 },
  { service: "stripe", tool_limit: 80 },
  { service: "sendgrid", tool_limit: 45 },
  { service: "intercom", tool_limit: 40 },
  { service: "slack", tool_limit: 35 },
  { service: "gmail", tool_limit: 30 },
  { service: "googlecalendar", tool_limit: 20 },
  { service: "googledrive", tool_limit: 20 },
  { service: "googlesheets", tool_limit: 0 },
  { service: "notion", tool_limit: 0 },
  { service: "netsuite", tool_limit: 0 },
  { service: "workday", tool_limit: 15 },
];

function corpus(dir) {
  return readdirSync(dir)
    .filter((f) => f.endsWith(".md"))
    .sort()
    .map((f) => ({ filename: f, content: readFileSync(join(dir, f), "utf8") }));
}

const anchors = [
  ...corpus(join(ROOT, "docs", "anchors", "wave2")),
  ...corpus(join(ROOT, "docs", "anchors", "wave6")),
];

const payload = {
  prompt: PROMPT,
  company_instance_key: "morgan_stanley_simulated",
  fresh: true,
  target_failure_rate: 0.6,
  anchor_files: anchors,
  mock_services: MOCK_SERVICES,
};

process.stderr.write(`anchors: ${anchors.length} files, ${anchors.reduce((a, f) => a + f.content.length, 0)} chars; mock_services: ${MOCK_SERVICES.length}\n`);
process.stdout.write(JSON.stringify(payload));
