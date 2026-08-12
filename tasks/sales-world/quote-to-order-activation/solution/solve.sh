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
    async with http_client('http://erp:8000/mcp') as (r, w, *_):
        async with ClientSession(r, w) as s:
            await s.initialize()
            print((await call(s, 'erp_sales_order_create', {'entity': 'customer_002', 'entity_name': 'Summit Group Account', 'memo': 'Activation for quote Q-2026-2000', 'total': 662400.0, 'currency': 'usd'}))[:120])
            print((await call(s, 'erp_sales_order_create', {'entity': 'customer_002', 'entity_name': 'Summit Group Account', 'memo': 'Activation for quote Q-2026-2007', 'total': 306000.0, 'currency': 'usd'}))[:120])
            print((await call(s, 'erp_sales_order_create', {'entity': 'customer_005', 'entity_name': 'Ironwood', 'memo': 'Activation for quote Q-2026-2009', 'total': 342090.0, 'currency': 'usd'}))[:120])
            print((await call(s, 'erp_sales_order_create', {'entity': 'customer_006', 'entity_name': 'Riverside Group Account', 'memo': 'Activation for quote Q-2026-2011', 'total': 1824000.0, 'currency': 'usd'}))[:120])

asyncio.run(main())
PY
