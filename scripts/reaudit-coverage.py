#!/usr/bin/env python3
"""Re-audit the 171-item coverage census against the CURRENT world.

docs/COVERAGE.md's verdicts were judged against the 205-tool wave-6 world. Since
then the world gained the densified vendor surface, the CRMArena substrate and
the wave-7 RevOps primitives. This script does NOT re-judge the items — it
mechanically checks whether the SPECIFIC blocker each verdict named has since
been built, and reports the delta with evidence.

Each blocker below was lifted from the verdict note in data/coverage/verdicts.json
and is paired with the concrete tool/table that would close it. An item is
reported as "blocker closed" only when that artifact exists in world.json today.

Run: python3 scripts/reaudit-coverage.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, "world", "blobfish-wave6", "package", "sbx_291042075d7547f4")

world = json.load(open(os.path.join(PKG, "world.json")))
verdicts = json.load(open(os.path.join(ROOT, "data", "coverage", "verdicts.json")))
rows = verdicts if isinstance(verdicts, list) else verdicts.get("verdicts", verdicts.get("items", []))

TOOLS = {t["name"] for t in world["tools"]}
TABLES = {t["name"] for t in world["tables"]}
TASK_TYPES = set()
for t in world["tasks"]:
    p = t.get("provenance") or {}
    for key in ("crmarena_task_type", "workflow_type"):
        if p.get(key):
            TASK_TYPES.add(p[key])

# blocker phrase (as written in the verdict note) -> artifact that closes it
BLOCKERS = [
    (r"send_email|send/log|outbound send|post_message|message-post|logged outbound",
     "outbound send channel", lambda: "post_mail_send" in TOOLS and "chat_post_message" in TOOLS),
    (r"sequence-instance|sequence instance|ordered steps|delay_days|per-step A/B",
     "sequence object with ordered steps", lambda: "outreach_sequence_steps" in TABLES),
    (r"merge and delete|merge operation|re-parent|survivorship",
     "dedupe + merge with survivorship", lambda: "lead_merge" in TOOLS),
    (r"lead owner write|owner_id write|lead-create write tool|no create op targets sales_leads",
     "lead create + owner write", lambda: "lead_create" in TOOLS and "lead_update_fields" in TOOLS),
    (r"Quota table|quota table|per-rep-per-period quota",
     "quota object", lambda: "rep_quotas" in TABLES),
    (r"Forecast|forecast-snapshot|ForecastingItem",
     "forecast submission object", lambda: "forecast_submissions" in TABLES),
    (r"usage/engagement|usage telemetry|engagement-metrics|no per-account usage",
     "account usage telemetry", lambda: "account_usage" in TABLES),
    (r"health score|health-score|weighted health",
     "account health scores", lambda: "account_health" in TABLES),
    (r"CampaignMember|touch graph|touchpoint table",
     "campaign touch graph", lambda: "campaign_touches" in TABLES),
    (r"e-signature|envelope|esignature",
     "e-signature envelopes", lambda: "signature_envelopes" in TABLES),
    (r"Quote/QuoteLine|Quote object|quote-create|QuoteLineItem|no quote object",
     "quote + quote lines", lambda: "sales_quotes" in TABLES and "sales_quote_lines" in TABLES),
    (r"CaseHistory|ownership-change-event|transfer counts cannot",
     "case history / transfers", lambda: "case_history" in TABLES),
    (r"issue-taxonomy|issue taxonomy",
     "issue taxonomy", lambda: "issue_taxonomy" in TABLES),
    (r"geographic \(state/region\)|region\) field",
     "region dimension on cases", lambda: "service_cases" in TABLES),
    (r"inbound EmailMessage|email-inbox object|inbox object|no inbound email|thread object",
     "inbound email threads", lambda: "email_threads" in TABLES),
    (r"suppression write|blacklist_add|write tool to add a contact to the suppression",
     "suppression write ops", lambda: "sg_suppressions_add" in TOOLS),
    (r"raw SQL execution|aggregate|COUNT\(|GROUP BY",
     "aggregate query", lambda: "aggregate_query" in TOOLS),
    (r"PII field|PII field population|confirmed PII",
     "PII-carrying profiles", lambda: "customer_profiles" in TABLES),
    (r"per-case chat-transcript|case chat transcripts|attached case chats",
     "case transcripts", lambda: "case_messages" in TABLES),
    (r"Product2|product scoping dimension|product dimension",
     "product dimension", lambda: "product_catalog_items" in TABLES),
]


def blockers_for(note):
    hits = []
    for pattern, label, check in BLOCKERS:
        if re.search(pattern, note, re.I):
            hits.append((label, check()))
    return hits


def main():
    closed, partly, untouched, out_of_scope = [], [], [], []
    false_positive_gaps = []
    for r in rows:
        verdict, note, name = r.get("verdict"), r.get("note") or "", r.get("name")
        if verdict == "out_of_scope":
            out_of_scope.append(name)
            continue
        if verdict == "covered":
            continue
        hits = blockers_for(note)
        if not hits:
            untouched.append((name, verdict))
        elif verdict == "gap":
            # The 11 gaps are external-channel mocks (LinkedIn, SMS, SERP, SMTP,
            # job-change feeds). Keyword matches here are false positives — an
            # outbound EMAIL channel does not close an SMS or signal-feed gap —
            # so they are reported separately and never counted as closed.
            false_positive_gaps.append((name, [l for l, _ in hits]))
        elif all(ok for _, ok in hits):
            closed.append((name, verdict, [l for l, _ in hits]))
        else:
            partly.append((name, verdict, [(l, ok) for l, ok in hits]))

    n_scored = len([r for r in rows if r.get("verdict") not in ("out_of_scope",)])
    print(f"census items: {len(rows)}  (in-scope {n_scored}, out-of-scope {len(out_of_scope)})")
    print(f"already covered in the original audit: {len([r for r in rows if r.get('verdict') == 'covered'])}")
    print()
    print(f"BLOCKER NOW CLOSED — every named missing piece exists today: {len(closed)}")
    for name, verdict, labels in sorted(closed):
        mark = "*" if name in TASK_TYPES else " "
        print(f" {mark} {name:46} was {verdict:8} <- {', '.join(sorted(set(labels)))}")
    print()
    print(f"PARTIALLY CLOSED — some named pieces built, others still missing: {len(partly)}")
    for name, verdict, labels in sorted(partly)[:20]:
        remaining = [l for l, ok in labels if not ok]
        built = [l for l, ok in labels if ok]
        print(f"   {name:46} built: {', '.join(sorted(set(built))) or '—'} | still missing: {', '.join(sorted(set(remaining)))}")
    print()
    if false_positive_gaps:
        print(f"KEYWORD MATCHED BUT STILL A GAP — not counted as closed: {len(false_positive_gaps)}")
        for name, labels in sorted(false_positive_gaps):
            print(f"   {name:46} matched {', '.join(sorted(set(labels)))} — but this needs an external channel we do not mock")
        print()
    print(f"NO MATCHED BLOCKER PHRASE (needs human re-read): {len(untouched)}")
    print("   " + ", ".join(n for n, _ in sorted(untouched)[:18]) + (" …" if len(untouched) > 18 else ""))
    print()
    print(f"* = a task for this capability now exists in the world ({len(TASK_TYPES)} task types registered)")
    print(f"world today: {len(TOOLS)} tools, {len(TABLES)} tables, {len(world['tasks'])} tasks")


if __name__ == "__main__":
    main()
