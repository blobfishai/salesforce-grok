#!/bin/bash
# Launch a blobfish deep-generation wave and download the world when ready.
# Usage: WAVE=wave2 PAYLOAD=/path/payload.json IDEM=key OUTDIR=world/blobfish-wave2 bash scripts/run-deep-wave.sh
set -uo pipefail
REPO=/Users/samuelchien/dev/salesforce-grok
WAVE="${WAVE:?set WAVE}"
PAYLOAD="${PAYLOAD:?set PAYLOAD}"
IDEM="${IDEM:?set IDEM}"
OUTDIR="${OUTDIR:?set OUTDIR}"
SP="${SP:-/tmp}"
KEY=$(grep '^BLOBFISH_API_KEY=' "$REPO/.env" | head -1 | cut -d= -f2)
[ -z "$KEY" ] && { echo "no BLOBFISH_API_KEY"; exit 1; }

echo "== [$WAVE] submitting deep job =="
curl -sS -m 60 -X POST https://blobfish.ai/api/v1/sandbox/jobs \
  -H "X-API-Key: $KEY" -H 'Content-Type: application/json' -H "Idempotency-Key: $IDEM" \
  --data @"$PAYLOAD" -o "$SP/${WAVE}_submit.json" -w "submit http:%{http_code}\n"
head -c 500 "$SP/${WAVE}_submit.json"; echo
JOB_ID=$(node -e 'const j=require(process.argv[1]);console.log(j.job?.job_id??j.job_id??"")' "$SP/${WAVE}_submit.json")
[ -z "$JOB_ID" ] && { echo "FAILED: no job_id"; exit 1; }
echo "JOB_ID=$JOB_ID"

END=$((SECONDS+3600))
STATUS=creating_world
while [ $SECONDS -lt $END ]; do
  curl -sS -N -m 1800 -H "X-API-Key: $KEY" \
    "https://blobfish.ai/api/v1/sandbox/jobs/$JOB_ID/stream" >> "$SP/${WAVE}_stream.log" 2>&1 || true
  curl -sS -m 30 -H "X-API-Key: $KEY" \
    "https://blobfish.ai/api/v1/sandbox/jobs/$JOB_ID" -o "$SP/${WAVE}_status.json" || true
  STATUS=$(node -e 'try{const j=require(process.argv[1]);console.log(j.job?.status??j.status??"unknown")}catch{console.log("unknown")}' "$SP/${WAVE}_status.json")
  echo "[$WAVE] status=$STATUS elapsed=${SECONDS}s"
  if [ "$STATUS" = "ready" ] || [ "$STATUS" = "failed" ]; then break; fi
  sleep 10
done

if [ "$STATUS" != "ready" ]; then
  echo "[$WAVE] JOB DID NOT COMPLETE: status=$STATUS"
  tail -c 1200 "$SP/${WAVE}_stream.log" 2>/dev/null
  exit 1
fi

WORLD_ID=$(node -e 'const j=require(process.argv[1]);console.log(j.job?.world_id??j.world_id??"")' "$SP/${WAVE}_status.json")
echo "[$WAVE] WORLD_ID=$WORLD_ID"
mkdir -p "$REPO/$OUTDIR/package"
curl -sS -m 120 -H "X-API-Key: $KEY" "https://blobfish.ai/api/v1/sandbox/worlds/$WORLD_ID" \
  -o "$REPO/$OUTDIR/world-api.json" -w "world http:%{http_code} bytes:%{size_download}\n" || true
curl -sS -m 120 -H "X-API-Key: $KEY" "https://blobfish.ai/api/v1/sandbox/worlds/$WORLD_ID/quality" \
  -o "$REPO/$OUTDIR/quality.json" -w "quality http:%{http_code}\n" || true
curl -sS -L -m 300 -H "X-API-Key: $KEY" "https://blobfish.ai/api/v1/sandbox/worlds/$WORLD_ID/download" \
  -o "$SP/${WAVE}_package.tar" -w "package http:%{http_code} bytes:%{size_download}\n"
tar -xf "$SP/${WAVE}_package.tar" -C "$REPO/$OUTDIR/package" && echo "[$WAVE] extracted"
WJ=$(find "$REPO/$OUTDIR/package" -name world.json | head -1)
[ -n "$WJ" ] && cp "$WJ" "$REPO/$OUTDIR/world.json"
node -e '
const j=require(process.argv[1]);const w=j.world??j;const c=x=>Array.isArray(x)?x.length:0;
let rows=0;for(const t of w.tables??[])rows+=t.row_count??0;
console.log("company:",JSON.stringify(w.thesis?.company??null));
console.log("tables:",c(w.tables),"tools:",c(w.tools),"tasks:",c(w.tasks),"verifiers:",c(w.verifiers),"rows:",rows);
' "$REPO/$OUTDIR/world.json"
echo "WORLD_ID=$WORLD_ID" > "$SP/${WAVE}_result.txt"
echo "[$WAVE] DONE"
