FROM node:22-bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-pip python3-venv curl jq ca-certificates procps \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install --no-cache-dir --break-system-packages \
        mcp httpx pytest==8.4.1 pytest-json-ctrf==0.3.5
WORKDIR /app
