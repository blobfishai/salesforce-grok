#!/bin/bash
# Reference trajectory. Harbor runs this as the oracle: if it does not score 1.0,
# the task is broken, not the agent.
set -euo pipefail
python3 - <<'PY'
import asyncio
from mcp.client.session import ClientSession
try:
    from mcp.client.streamable_http import streamable_http_client as http_client
except ImportError:  # older SDKs used the unspaced name
    from mcp.client.streamable_http import streamablehttp_client as http_client

DECISIONS = {
    'quote_0002': 'approved',   # 12.5%, $1.584M list - inside deal desk authority
    'quote_0004': 'approved',   # 24%, $575K list - inside deal desk authority
    'quote_0006': 'rejected',   # invalid configuration
    'quote_0011': 'rejected',   # invalid configuration
    # quote_0003 stays in_review: $2.088M list crosses the Finance threshold
}

async def call(session, name, args, tries=8):
    """The world rate-limits writes the way a real CRM does; back off and retry."""
    for attempt in range(tries):
        res = await session.call_tool(name, args)
        text = res.content[0].text if res.content else ''
        if 'rate_limited' not in text:
            return text
        await asyncio.sleep(1.5 * (attempt + 1))
    return text

async def main():
    async with http_client('http://salesforce:8000/mcp') as (r, w, *_):
        async with ClientSession(r, w) as s:
            await s.initialize()
            listed = await call(s, 'quotes_list', {'status': 'in_review', 'limit': 50})
            print('queue:', listed[:400])
            for qid, status in DECISIONS.items():
                out = await call(s, 'quote_update_status', {'quote_id': qid, 'status': status})
                print(qid, '->', status, '|', out[:160])

asyncio.run(main())
PY
