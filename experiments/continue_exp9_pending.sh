#!/bin/bash
# Sequential Exp9 pending: GEO_OPT (5) then vertical SP (8). Mac-safe single batch.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=cp2k_resource.sh
source "$ROOT/experiments/cp2k_resource.sh"

CP2K="${CP2K:-/opt/homebrew/bin/cp2k.psmp}"
export CP2K_DATA="${CP2K_DATA:-/opt/homebrew/share/cp2k/data}"
INP_DIR="$ROOT/experiments/exp_9_charged_polaron/inputs"
VERT_DIR="$INP_DIR/vertical"
OUT_DIR="$ROOT/dft_results/exp_9_charged_polaron/outputs"
LOG="$ROOT/experiments/local_run.log"
LOCK="$ROOT/experiments/.exp9_batch.lock"

if [[ ! -x "$CP2K" ]]; then
  echo "CP2K not found: $CP2K" >&2
  exit 1
fi

if [[ -f "$LOCK" ]] && kill -0 "$(cat "$LOCK")" 2>/dev/null; then
  echo "Exp9 batch already running (pid $(cat "$LOCK")). Exit." >&2
  exit 1
fi
if pgrep -f 'cp2k\.psmp.*polaron_' >/dev/null 2>&1; then
  echo "CP2K polaron_* job already running. Exit." >&2
  exit 1
fi

echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT

mkdir -p "$OUT_DIR"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') [exp9] $*" >> "$LOG"; }

geo_done() {
  local out="$1"
  [[ -f "$out" ]] && grep -q 'PROGRAM ENDED' "$out" 2>/dev/null
}

sp_done() {
  local out="$1"
  [[ -f "$out" ]] && grep -q 'SCF run converged' "$out" 2>/dev/null
}

archive_partial() {
  local out="$1"
  if [[ -f "$out" ]] && ! geo_done "$out" && ! sp_done "$out"; then
    local ts
    ts="$(date +%Y%m%d_%H%M%S)"
    log "ARCHIVE partial: $(basename "$out") -> .failed_${ts}"
    mv "$out" "${out}.failed_${ts}"
  fi
}

run_geo_opt() {
  local base="$1"
  local inp="$INP_DIR/${base}.inp"
  local out="$OUT_DIR/${base}.out"

  if geo_done "$out"; then
    log "SKIP GEO_OPT (done): $base"
    return 0
  fi
  if [[ ! -f "$inp" ]]; then
    log "MISSING inp: $inp"
    return 1
  fi

  archive_partial "$out"
  local np
  np="$(cp2k_cap_np 4)"
  log "START GEO_OPT: $base (np=$np, out=$OUT_DIR)"
  cd "$OUT_DIR"
  mpirun -np "$np" "$CP2K" -i "$inp" -o "$(basename "$out")" >> "$LOG" 2>&1

  if geo_done "$out"; then
    log "DONE GEO_OPT: $base"
    bash "$ROOT/experiments/post_exp9_converged.sh" >> "$LOG" 2>&1 || true
    return 0
  fi
  log "INCOMPLETE GEO_OPT: $base (no PROGRAM ENDED)"
  return 1
}

run_vertical_sp() {
  local base="$1"
  local inp="$VERT_DIR/${base}.inp"
  local out="$OUT_DIR/${base}.out"

  if sp_done "$out"; then
    log "SKIP vertical SP (done): $base"
    return 0
  fi
  if [[ ! -f "$inp" ]]; then
    log "MISSING vertical inp: $inp"
    return 1
  fi

  archive_partial "$out"
  local np
  np="$(cp2k_cap_np 4)"
  log "START vertical SP: $base (np=$np)"
  cd "$VERT_DIR"
  mpirun -np "$np" "$CP2K" -i "$(basename "$inp")" -o "$out" >> "$LOG" 2>&1

  if sp_done "$out"; then
    log "DONE vertical SP: $base"
    bash "$ROOT/experiments/post_exp9_converged.sh" >> "$LOG" 2>&1 || true
    return 0
  fi
  log "INCOMPLETE vertical SP: $base"
  return 1
}

mapfile -t PENDING_GEO < <(python3 -c "
import json
d = json.load(open('$ROOT/experiments/analysis/exp9_polaron_verification.json'))
for p in d.get('pending_geo_opt') or []:
    print(p)
" 2>/dev/null || true)

mapfile -t PENDING_VERT < <(python3 -c "
import json
d = json.load(open('$ROOT/experiments/analysis/exp9_polaron_verification.json'))
vs = d.get('vertical_sp') or {}
done = set(vs.get('outputs_converged') or [])
for p in vs.get('inputs_pending') or []:
    if p not in done:
        print(p)
" 2>/dev/null || true)

log "========== Exp9 batch start (max_np=${SIMUKIT_MAX_CORES}/${_ncpu}) =========="
python3 "$ROOT/experiments/analysis/analyze_exp9_polaron.py" >> "$LOG" 2>&1 || true
log "Pending GEO_OPT: ${PENDING_GEO[*]:-none} | vertical SP: ${PENDING_VERT[*]:-none}"

for base in "${PENDING_GEO[@]}"; do
  run_geo_opt "$base" || true
done

python3 "$ROOT/experiments/exp_9_charged_polaron/generate_vertical_sp.py" >> "$LOG" 2>&1 || true

for base in "${PENDING_VERT[@]}"; do
  run_vertical_sp "$base" || true
done

bash "$ROOT/experiments/post_exp9_converged.sh" >> "$LOG" 2>&1 || true
log "========== Exp9 batch finished =========="
bash "$ROOT/experiments/exp9_status_line.sh" >> "$LOG"
