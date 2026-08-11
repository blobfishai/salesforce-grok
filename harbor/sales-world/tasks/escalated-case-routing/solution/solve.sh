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
    async with http_client('http://salesforce:8000/mcp') as (r, w, *_):
        async with ClientSession(r, w) as s:
            await s.initialize()
            print((await call(s, 'crm_followup_create', {'subject': 'Escalation chase - SVC-100004', 'status': 'open'}))[:100])
            print((await call(s, 'crm_followup_create', {'subject': 'Escalation chase - SVC-100029', 'status': 'open'}))[:100])
            print((await call(s, 'crm_followup_create', {'subject': 'Escalation chase - SVC-100094', 'status': 'open'}))[:100])
            print((await call(s, 'service_case_update_status', {'case_id': 'case_svc_0026', 'status': 'open'}))[:100])
            print((await call(s, 'service_case_update_status', {'case_id': 'case_svc_0097', 'status': 'open'}))[:100])
            print((await call(s, 'service_case_update_status', {'case_id': 'case_svc_0165', 'status': 'open'}))[:100])

asyncio.run(main())
PY
