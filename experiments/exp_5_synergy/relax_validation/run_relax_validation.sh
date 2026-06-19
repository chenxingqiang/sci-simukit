#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
INP_DIR="$ROOT/experiments/exp_5_synergy/relax_validation/inputs"
LOG="$ROOT/experiments/local_run.log"

export CP2K_DATA="${CP2K_DATA:-/opt/homebrew/share/cp2k/data}"
CP2K="${CP2K:-/opt/homebrew/bin/cp2k.psmp}"
NP="${NP:-4}"

TASKS=(
  relax_pristine_eps0_geo
  relax_pristine_eps3_geo
  relax_P_eps0_geo
  relax_P_eps3_geo
)

mkdir -p "$INP_DIR"
python3 "$ROOT/experiments/exp_5_synergy/relax_validation/generate_relax_inputs.py"

for task in "${TASKS[@]}"; do
  out="$INP_DIR/${task}.out"
  if [[ -f "$out" ]] && grep -q 'GEOMETRY OPTIMIZATION COMPLETED' "$out"; then
    echo "[skip] $task already converged"
    continue
  fi
  echo "[$(date -Iseconds)] START $task np=$NP" | tee -a "$LOG"
  (
    cd "$INP_DIR"
    mpirun -np "$NP" "$CP2K" -i "${task}.inp" -o "${task}.out"
  )
  if grep -q 'GEOMETRY OPTIMIZATION COMPLETED' "$out"; then
    echo "[$(date -Iseconds)] DONE $task" | tee -a "$LOG"
    python3 "$ROOT/experiments/exp_5_synergy/relax_validation/analyze_relax_s.py"
  else
    echo "[$(date -Iseconds)] FAIL $task (no GEO_OPT completion)" | tee -a "$LOG"
    exit 1
  fi
done

echo "All relax validation jobs finished."
python3 "$ROOT/experiments/exp_5_synergy/relax_validation/analyze_relax_s.py"
