#!/bin/bash
# HARNESS CHECK, NOT A SOLUTION. This submits the known ground truth to prove the
# world, the answer channel and the metric agree end to end. It does NOT show the
# task is solvable from the data with the tools provided — only a model run can.
#
# The answer is baked in at compile time rather than read from /tests, because
# Harbor mounts /tests into the verifier container only; the agent container
# cannot see it.
set -euo pipefail
python3 - <<'PY'
import asyncio, json
from mcp.client.session import ClientSession
try:
    from mcp.client.streamable_http import streamable_http_client as http_client
except ImportError:
    from mcp.client.streamable_http import streamablehttp_client as http_client

ANSWER = json.loads('"005Ws000001xYujIAE"')
ANSWER = 'None' if ANSWER is None else str(ANSWER)

async def main():
    async with http_client('http://crm:8080/mcp') as (r, w, *_):
        async with ClientSession(r, w) as s:
            await s.initialize()
            out = await s.call_tool('respond', {'answer': ANSWER})
            print(out.content[0].text[:160])

asyncio.run(main())
PY
