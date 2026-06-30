#!/usr/bin/env bash
# Seed-137 full tetramer grid (24 ENERGY: 6 pristine + 18 B/N/P). Run when relax batch idle.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
INP_DIR="$ROOT/experiments/exp_5_synergy/seed_validation/inputs"
LOG="$ROOT/experiments/local_run.log"
# shellcheck source=cp2k_resource.sh
source "$ROOT/experiments/cp2k_resource.sh"
export CP2K_DATA="${CP2K_DATA:-/opt/homebrew/share/cp2k/data}"
CP2K="${CP2K:-/opt/homebrew/bin/cp2k.psmp}"
MPIRUN="${MPIRUN:-/opt/homebrew/bin/mpirun}"
# Tetramer ENERGY: suggest 4 MPI ranks, capped at ~2/3 logical CPUs (SIMUKIT_MAX_CORES).
NP="${NP:-$(cp2k_cap_np 4)}"

python3 "$ROOT/experiments/exp_5_synergy/seed_validation/generate_seed137_inputs.py"
if [[ "${RERUN_PROTOCOL_FIX:-0}" == 1 ]]; then
  ts="$(date +%Y%m%d_%H%M%S)"
  for out in "$INP_DIR"/seed137_*_rigid.out; do
    [[ -f "$out" ]] || continue
    mv "$out" "${out}.pre_protocol_fix_${ts}"
    echo "[archive] protocol fix -> ${out}.pre_protocol_fix_${ts}"
  done
fi

for inp in "$INP_DIR"/seed137_*_rigid.inp; do
  [[ -f "$inp" ]] || continue
  base="$(basename "$inp" .inp)"
  out="$INP_DIR/${base}.out"
  if [[ -f "$out" ]] && grep -q 'SCF run converged' "$out"; then
    echo "[skip] $base"
    continue
  fi
  if [[ -f "$out" ]] && grep -q 'ABORT' "$out"; then
    ts="$(date +%Y%m%d_%H%M%S)"
    mv "$out" "${out}.failed_${ts}"
    echo "[archive] $base ABORT -> ${out}.failed_${ts}"
  fi
  echo "[$(date -Iseconds)] START $base np=$NP cap=${SIMUKIT_MAX_CORES}" | tee -a "$LOG"
  (cd "$INP_DIR" && "$MPIRUN" -np "$NP" "$CP2K" -i "${base}.inp" -o "${base}.out")
  if grep -q 'SCF run converged' "$out"; then
    bash "$ROOT/experiments/post_seed137_validation.sh" || true
  else
    echo "FAIL $base"
    exit 1
  fi
done

bash "$ROOT/experiments/post_seed137_validation.sh"
