#!/usr/bin/env bash
# Run four matched-functional PBE+D3 rigid SP tasks (Table III quantitative benchmark).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
INP_DIR="$ROOT/experiments/exp_5_synergy/relax_validation/rigid_pbed3/inputs"
LOG="$ROOT/experiments/local_run.log"
# shellcheck source=cp2k_resource.sh
source "$ROOT/experiments/cp2k_resource.sh"
export CP2K_DATA="${CP2K_DATA:-/opt/homebrew/share/cp2k/data}"
CP2K="${CP2K:-/opt/homebrew/bin/cp2k.psmp}"
MPIRUN="${MPIRUN:-/opt/homebrew/bin/mpirun}"
NP="${NP:-$(cp2k_cap_np 4)}"

python3 "$ROOT/experiments/exp_5_synergy/relax_validation/rigid_pbed3/generate_rigid_pbed3_inputs.py"

TASKS=(
  rigid_pbed3_pristine_eps0_sp
  rigid_pbed3_pristine_eps3_sp
  rigid_pbed3_P_eps0_sp
  rigid_pbed3_P_eps3_sp
)

for task in "${TASKS[@]}"; do
  out="$INP_DIR/${task}.out"
  if [[ -f "$out" ]] && grep -q 'SCF run converged' "$out"; then
    echo "[skip] $task"
    continue
  fi
  if [[ -f "$out" ]] && grep -q 'ABORT' "$out"; then
    ts="$(date +%Y%m%d_%H%M%S)"
    mv "$out" "${out}.failed_${ts}"
    echo "[archive] $task ABORT -> ${out}.failed_${ts}"
  fi
  echo "[$(date -Iseconds)] START $task np=$NP" | tee -a "$LOG"
  (cd "$INP_DIR" && "$MPIRUN" -np "$NP" "$CP2K" -i "${task}.inp" -o "${task}.out")
  grep -q 'SCF run converged' "$out" || { echo "FAIL $task"; exit 1; }
  bash "$ROOT/experiments/post_rigid_pbed3.sh" || true
done

bash "$ROOT/experiments/post_rigid_pbed3.sh"
echo "rigid_pbed3 batch finished."
