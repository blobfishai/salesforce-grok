#!/usr/bin/env bash
# Build the two images every task in this dataset shares:
#
#   sales-world:<tag>          the simulated company (REST + MCP, 400+ tools)
#   sales-world-gateway:<tag>  per-vendor MCP facade over one tool namespace
#
# Usage: ./scripts/build-images.sh [world-package-dir] [tag]
# Default package is the densest world (wave 6).
set -euo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
PKG="${1:-$REPO/world/blobfish-wave6/package/sbx_291042075d7547f4}"
TAG="${2:-w6}"

[ -f "$PKG/world.json" ] || { echo "no world.json in $PKG" >&2; exit 1; }

echo "==> staging world payload from $PKG"
PAYLOAD="$HERE/images/world/payload"
rm -rf "$PAYLOAD"; mkdir -p "$PAYLOAD"
# Runtime only. state.db/traces/runs/.sessions are per-trial and must not ship.
for item in world.json seed.db server.py isolation.py tools tools.py tasks.jsonl company.json mcp-assets.json; do
  [ -e "$PKG/$item" ] && cp -R "$PKG/$item" "$PAYLOAD/"
done
rm -rf "$PAYLOAD/tools/__pycache__"
# Harbor entrypoint wraps (never edits) the packaged server.
cp "$HERE/images/world/harbor_server.py" "$PAYLOAD/"
du -sh "$PAYLOAD"

echo "==> building sales-world:$TAG"
docker build -q -t "sales-world:$TAG" "$HERE/images/world"

echo "==> building sales-world-gateway:$TAG"
docker build -q -t "sales-world-gateway:$TAG" "$HERE/images/gateway"

echo
echo "built:"
docker images --format '  {{.Repository}}:{{.Tag}}  {{.Size}}' | grep -E "^  sales-world(-gateway)?:$TAG"
echo
echo "next: harbor run --dataset-path $HERE/tasks --agent <agent> --model <model>"
