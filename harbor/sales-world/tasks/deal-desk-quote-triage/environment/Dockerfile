FROM python:3.12-slim

# Agent-side workspace. The company lives in sibling containers reachable over
# MCP; nothing about the world is available locally, which is the point.
RUN apt-get update && apt-get install -y --no-install-recommends curl jq \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir mcp httpx

WORKDIR /app
