FROM node:22-bookworm-slim

# Agent-side workspace. The company lives in sibling containers reachable only
# over MCP; nothing about the world is on this filesystem, which is the point.
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-pip python3-venv curl jq ca-certificates procps \
    && rm -rf /var/lib/apt/lists/*
# pytest + the CTRF reporter are baked in: the verifier runs in this container,
# and a missing test runner silently scores every task 0.
RUN pip3 install --no-cache-dir --break-system-packages         mcp httpx pytest==8.4.1 pytest-json-ctrf==0.3.5

WORKDIR /app
