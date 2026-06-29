#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
INP_DIR="$ROOT/experiments/exp_10_size_scaling/placement_validation/inputs"
LOG="$ROOT/experiments/local_run.log"
# shellcheck source=cp2k_resource.sh
source "$ROOT/experiments/cp2k_resource.sh"
export CP2K_DATA="${CP2K_DATA:-/opt/homebrew/share/cp2k/data}"
CP2K="${CP2K:-/opt/homebrew/bin/cp2k.psmp}"
MPIRUN="${MPIRUN:-/opt/homebrew/bin/mpirun}"
NP="${NP:-$(cp2k_cap_np 4)}"

python3 "$ROOT/experiments/exp_10_size_scaling/placement_validation/generate_periodic_placement_inputs.py"

shopt -s nullglob
for inp in "$INP_DIR"/place_seed*.inp; do
  base="$(basename "$inp" .inp)"
  out="$INP_DIR/${base}.out"
  if [[ -f "$out" ]] && grep -q 'SCF run converged' "$out"; then
    echo "[skip] $base"
    continue
  fi
  if [[ -f "$out" ]] && grep -q 'ABORT' "$out"; then
    ts="$(date +%Y%m%d_%H%M%S)"
    mv "$out" "${out}.failed_${ts}"
    bash "$ROOT/experiments/exp_10_size_scaling/placement_validation/relax_placement_stall_eps.sh" "$base"
  fi
  echo "[$(date -Iseconds)] START $base np=$NP" | tee -a "$LOG"
  (cd "$INP_DIR" && "$MPIRUN" -np "$NP" "$CP2K" -i "${base}.inp" -o "${base}.out")
  grep -q 'SCF run converged' "$out" || { echo "FAIL $base"; exit 1; }
done

python3 "$ROOT/experiments/exp_10_size_scaling/placement_validation/analyze_periodic_placement.py"
bash "$ROOT/experiments/exp10_placement_status_line.sh"
