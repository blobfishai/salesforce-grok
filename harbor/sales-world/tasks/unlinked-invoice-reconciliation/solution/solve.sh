#!/bin/bash
# Reference trajectory. Harbor runs this as the oracle: if it does not score 1.0,
# the task is broken, not the agent.
set -euo pipefail
python3 - <<'PY'
import asyncio, json
from mcp.client.session import ClientSession
try:
    from mcp.client.streamable_http import streamable_http_client as http_client
except ImportError:
    from mcp.client.streamable_http import streamablehttp_client as http_client

async def call(s, name, args, tries=8):
    """The world rate-limits writes like a real CRM; back off and retry."""
    for attempt in range(tries):
        res = await s.call_tool(name, args)
        text = res.content[0].text if res.content else ''
        if 'rate_limited' not in text:
            return text
        await asyncio.sleep(1.5 * (attempt + 1))
    return text

async def main():
    async with http_client('http://jira:8000/mcp') as (r, w, *_):
        async with ClientSession(r, w) as s:
            await s.initialize()
            print((await call(s, 'jira_issue_create', {'project_key': 'RECON', 'issue_type': 'Task', 'summary': 'Unlinked invoice INV-1004 has no source sales order', 'description': 'Invoice INV-1004 for Atlas (USD 30000.0) is not created_from any sales order.'}))[:120])
            print((await call(s, 'jira_issue_create', {'project_key': 'RECON', 'issue_type': 'Task', 'summary': 'Unlinked invoice INV-1005 has no source sales order', 'description': 'Invoice INV-1005 for Riverside Group Account (EUR 8330.0) is not created_from any sales order.'}))[:120])
            print((await call(s, 'jira_issue_create', {'project_key': 'RECON', 'issue_type': 'Task', 'summary': 'Unlinked invoice INV-1006 has no source sales order', 'description': 'Invoice INV-1006 for Crestline (GBP 6300.0) is not created_from any sales order.'}))[:120])
            print((await call(s, 'jira_issue_create', {'project_key': 'RECON', 'issue_type': 'Task', 'summary': 'Unlinked invoice INV-1007 has no source sales order', 'description': 'Invoice INV-1007 for Riverside Group Account (EUR 14994.0) is not created_from any sales order.'}))[:120])
            print((await call(s, 'jira_issue_create', {'project_key': 'RECON', 'issue_type': 'Task', 'summary': 'Unlinked invoice INV-1008 has no source sales order', 'description': 'Invoice INV-1008 for Summit Group Account (GBP 30000.0) is not created_from any sales order.'}))[:120])

asyncio.run(main())
PY
