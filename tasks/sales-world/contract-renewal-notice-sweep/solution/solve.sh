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
            print((await call(s, 'reminder_create', {'subject': 'Renewal notice window open - MS-2025-0041', 'remind_at': '2026-02-16T09:00:00Z', 'related_type': 'contract', 'related_id': 'ctr_0001', 'owner_employee_id': '1'}))[:120])
            print((await call(s, 'reminder_create', {'subject': 'Renewal notice window open - MS-2025-0088', 'remind_at': '2026-02-16T09:00:00Z', 'related_type': 'contract', 'related_id': 'ctr_0003', 'owner_employee_id': '2'}))[:120])

asyncio.run(main())
PY
