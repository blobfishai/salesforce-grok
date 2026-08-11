#!/usr/bin/env bash
# Build the CRMArena parity world image. The org mirror ships with the upstream
# repo (external/CRMArena), so it is copied in at build time rather than vendored.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
TAG="${1:-v1}"
SRC="$REPO/external/CRMArena/local_data/crmarena_data.db"
[ -f "$SRC" ] || { echo "missing $SRC (clone SalesforceAIResearch/CRMArena)" >&2; exit 1; }
cp "$SRC" "$HERE/images/world/crmarena_data.db"
docker build -q -t "crmarena-parity:$TAG" "$HERE/images/world"
rm -f "$HERE/images/world/crmarena_data.db"
echo "built crmarena-parity:$TAG"
