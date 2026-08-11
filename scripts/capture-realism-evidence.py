#!/usr/bin/env python3
"""Phase D: capture REAL evidence that the tools and seeded documents work.

Nothing here is illustrative — every request is executed against the running
world server over MCP (POST /mcp, tools/call) inside a real copy-on-write
session, and every response is recorded verbatim. Writes evidence.json for the
report/artifact builder.

Run with the world served on :8971 —
  cd world/blobfish-wave6/package/sbx_291042075d7547f4 && PORT=8971 python3 server.py
  python3 scripts/capture-realism-evidence.py
"""
import json
import os
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.environ.get("WORLD_BASE", "http://127.0.0.1:8971")
OUT = os.path.join(ROOT, "data", "evidence", "realism-evidence.json")


def post(path, payload, session=None):
    req = urllib.request.Request(
        f"{BASE}{path}", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 **({"X-Blobfish-Session": session} if session else {})})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        # A real HTTP error IS evidence — record the server's own words.
        body = e.read().decode("utf-8", "replace")[:600]
        try:
            return {"_http_error": e.code, "body": json.loads(body)}
        except Exception:
            return {"_http_error": e.code, "body": body}


def new_session():
    return post("/sessions", {})["session_id"]


def call(session, tool, args):
    res = post("/mcp", {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                        "params": {"name": tool, "arguments": args}}, session)
    if "_http_error" in res:
        return {"tool": tool, "arguments": args, "response": res}
    text = ((res.get("result") or {}).get("content") or [{}])[0].get("text", "")
    try:
        parsed = json.loads(text)
    except Exception:
        parsed = text
    return {"tool": tool, "arguments": args, "response": parsed}


def main():
    session = new_session()
    ev = {"world_base": BASE, "session": session, "vendors": {}, "documents": [], "workflow": []}

    # ---- per-vendor: a real read, a real write, and a real error --------------
    probes = {
        "salesforce-crm (Service Cloud)": [
            ("salesforce.service_cases_list", {"issue_type": "Billing Discrepancy", "region": "West", "limit": 3}),
            ("salesforce.case_history_list", {"case_id": "case_svc_0002", "field_name": "OwnerId", "limit": 5}),
            ("salesforce.service_case_get", {"case_id": "does_not_exist"}),
        ],
        "salesforce-crm (Sales Cloud / CPQ)": [
            ("salesforce.quotes_list", {"status": "in_review", "limit": 3}),
            ("salesforce.quote_lines_list", {"quote_id": "quote_0006", "limit": 3}),
            ("salesforce.quote_update_status", {"quote_id": "quote_0006", "status": "rejected"}),
        ],
        "stripe-billing": [
            ("stripe.get_subscriptions", {"limit": 2}),
            ("stripe.post_invoices", {"customer": "cus_00000000000001", "currency": "usd"}),
            ("stripe.get_customers_customer", {"customer": "cus_nope"}),
        ],
        "slack": [
            ("slack.conversations_list", {"limit": 3}),
            ("slack.chat_post_message", {"channel": "C0000001",
                                          "text": "Deal Desk rejected Q-2026-2005 (34% > 15% tier authority)."}),
            ("slack.conversations_info", {"channel": "C0NOPE"}),
        ],
        "sendgrid-email": [
            ("email.post_mail_send", {"to": "cfo@summitgroup.example",
                                       "from": "renewals@morganstanleysimulated.com",
                                       "subject": "Summit renewal — order form attached",
                                       "body": "Attached is the countersigned order form."}),
            ("email.sg_mail_sends_list", {"limit": 2}),
        ],
        "pagerduty-support": [
            ("pagerduty.pd_incidents_list", {"status": "triggered", "limit": 2}),
            ("pagerduty.pd_incident_manage", {"id": "PT4KHLK", "status": "acknowledged",
                                               "from": "contact77709@morganstanleysimulated.com"}),
        ],
        "jira": [("jira.jira_search", {"jql": "billing", "max_results": 3})],
        "netsuite-erp": [("erp.erp_sales_orders_list", {"limit": 2}),
                         ("erp.erp_invoices_list", {"limit": 2})],
        "google-calendar": [("calendar.calendar_events_list", {"calendar_id": "primary", "max_results": 3})],
        "notion-docs": [("notion.notion_search", {"query": "renewal", "page_size": 3})],
        "github": [("github.gh_workflow_runs_list", {"repo": "revops/stripe-webhooks", "limit": 2})],
    }
    for vendor, calls in probes.items():
        ev["vendors"][vendor] = [call(session, t, a) for t, a in calls]

    # ---- seeded documents actually readable in-world -------------------------
    for title_hint in ["CPQ Discount Policy", "Renewal Playbook", "Lead Scoring",
                       "Deal Desk Charter", "Finance Approval Thresholds"]:
        r = call(session, "notion.query_documents", {"query": title_hint, "limit": 1})
        rows = r["response"]
        rows = rows.get("rows") if isinstance(rows, dict) else rows
        if isinstance(rows, list) and rows:
            d = rows[0]
            ev["documents"].append({
                "query": title_hint,
                "title": d.get("title"),
                "excerpt": (d.get("body") or "")[:600],
                "chars": len(d.get("body") or ""),
            })

    # ---- one cross-vendor workflow, executed for real ------------------------
    steps = [
        ("read the governing policy", "notion.query_documents", {"query": "CPQ Discount Policy", "limit": 1}),
        ("find the over-authority quote", "salesforce.quotes_list", {"status": "in_review", "limit": 5}),
        ("inspect its line items", "salesforce.quote_lines_list", {"quote_id": "quote_0011", "limit": 3}),
        ("reject it per policy", "salesforce.quote_update_status", {"quote_id": "quote_0011", "status": "rejected"}),
        ("announce in the deal room", "slack.chat_post_message",
         {"channel": "C0000001", "text": "Q-2026-2010 rejected: 31% exceeds the 15% Platinum authority."}),
        ("confirm the state change", "salesforce.quote_get", {"quote_id": "quote_0011"}),
    ]
    for label, tool, args in steps:
        rec = call(session, tool, args)
        rec["why"] = label
        # The world injects deterministic friction (~3% of call signatures fail
        # retryably once). Retrying is what a real agent does — capture both.
        resp = rec.get("response")
        if isinstance(resp, dict) and resp.get("retryable"):
            rec["friction"] = resp
            retry = call(session, tool, args)
            rec["response"] = retry["response"]
            rec["retried_after_friction"] = True
        ev["workflow"].append(rec)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(ev, f, indent=1, ensure_ascii=False)

    n_calls = sum(len(v) for v in ev["vendors"].values()) + len(ev["workflow"]) + len(ev["documents"])
    print(f"captured {n_calls} live calls across {len(ev['vendors'])} vendor surfaces")
    print(f"  documents read: {len(ev['documents'])}")
    print(f"  workflow steps: {len(ev['workflow'])}")
    print(f"  -> {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
