#!/usr/bin/env bash
# Clone the sales-domain evidence corpus (evals · workflows · MCP tools · CRM schemas)
# listed in research/repos.manifest.tsv into research/repos/<axis>/<owner>__<name>.
# Shallow, single-branch, parallel, resumable. Writes research/repos/CLONE-LOG.tsv.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MANIFEST="$ROOT/research/repos.manifest.tsv"
DEST="$ROOT/research/repos"
JOBS="${JOBS:-8}"

mkdir -p "$DEST/.status"
rm -f "$DEST/.status"/*

clone_one() {
  ROOT="$1"; DEST="$2"; axis="$3"; repo="$4"; mode="$5"
  owner="${repo%%/*}"; name="${repo##*/}"
  dir="$DEST/$axis/${owner}__${name}"
  key="${axis}__${owner}__${name}"

  # Disk guard: the corpus is large and the sweep is unattended. Stop taking on
  # new repos once free space drops under ~6 GB rather than filling the volume.
  free_mb=$(df -m "$DEST" | awk 'NR==2{print $4}')
  if [ "${free_mb:-0}" -lt 6000 ] && [ ! -d "$dir/.git" ]; then
    printf 'SKIP\t%s\t%s\t-\t0\t0K\tdisk guard: %sMB free\n' "$axis" "$repo" "$free_mb" \
      > "$DEST/.status/$key"
    echo "[SKIP] $repo (disk guard)"
    return 0
  fi

  if [ -d "$dir/.git" ]; then
    status=SKIP; note="already present"
  else
    mkdir -p "$(dirname "$dir")"
    if [ "$mode" = "sparse" ]; then
      if git clone --depth 1 --single-branch --filter=blob:none --sparse \
          "https://github.com/$repo.git" "$dir" >/dev/null 2>&1; then
        git -C "$dir" sparse-checkout set \
          packages/twenty-server/src/modules \
          packages/twenty-server/src/engine/metadata-modules \
          packages/twenty-shared/src >/dev/null 2>&1
        status=OK; note="sparse"
      else
        status=FAIL; note="clone failed"
      fi
    else
      # 5-minute ceiling per repo so one fat repo cannot stall the sweep
      if timeout 300 git clone --depth 1 --single-branch \
          "https://github.com/$repo.git" "$dir" >/dev/null 2>&1; then
        status=OK; note=""
      else
        status=FAIL; note="clone failed or timed out (private/renamed/deleted/large?)"
        rm -rf "$dir"
      fi
    fi
  fi

  if [ -d "$dir" ]; then
    files=$(find "$dir/" -type f -not -path '*/.git/*' 2>/dev/null | wc -l | tr -d ' ')
    bytes=$(du -sk "$dir/" 2>/dev/null | cut -f1)
  else
    files=0; bytes=0
  fi
  printf '%s\t%s\t%s\t%s\t%s\t%sK\t%s\n' \
    "$status" "$axis" "$repo" "${dir#$ROOT/}" "$files" "$bytes" "$note" \
    > "$DEST/.status/$key"
  echo "[$status] $repo ($files files)"
}
export -f clone_one

# Only axis/repo/mode reach xargs — the "why" column is prose and blows the arg limit.
grep -v '^#' "$MANIFEST" | awk -F'\t' 'NF>=4 && $1!="" {print $1" "$2" "$4}' \
  | xargs -P "$JOBS" -n 3 bash -c 'clone_one "'"$ROOT"'" "'"$DEST"'" "$0" "$1" "$2"'

LOG="$DEST/CLONE-LOG.tsv"
printf 'status\taxis\trepo\tpath\tfiles\tbytes\tnote\n' > "$LOG"
cat "$DEST/.status"/* >> "$LOG"
rm -rf "$DEST/.status"

echo "--- summary ---"
awk -F'\t' 'NR>1{c[$1]++} END{for(k in c) printf "%s: %d\n", k, c[k]}' "$LOG"
