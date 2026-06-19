#!/usr/bin/env bash
# Seed-137 full tetramer grid (18 ENERGY). Run when Exp9 batch is idle.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
INP_DIR="$ROOT/experiments/exp_5_synergy/seed_validation/inputs"
LOG="$ROOT/experiments/local_run.log"
export CP2K_DATA="${CP2K_DATA:-/opt/homebrew/share/cp2k/data}"
CP2K="${CP2K:-/opt/homebrew/bin/cp2k.psmp}"
NP="${NP:-4}"

python3 "$ROOT/experiments/exp_5_synergy/seed_validation/generate_seed137_inputs.py"

for inp in "$INP_DIR"/seed137_*_rigid.inp; do
  base="$(basename "$inp" .inp)"
  out="$INP_DIR/${base}.out"
  if [[ -f "$out" ]] && grep -q 'SCF run converged' "$out"; then
    echo "[skip] $base"
    continue
  fi
  echo "[$(date -Iseconds)] START $base" | tee -a "$LOG"
  (cd "$INP_DIR" && mpirun -np "$NP" "$CP2K" -i "${base}.inp" -o "${base}.out")
  grep -q 'SCF run converged' "$out" || { echo "FAIL $base"; exit 1; }
done

python3 "$ROOT/experiments/exp_5_synergy/seed_validation/analyze_seed137.py"
