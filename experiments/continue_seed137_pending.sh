#!/bin/bash
# Resume Table IV seed-137 ENERGY batch (skips converged). MPI capped at ~2/3 CPUs.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOCK="$ROOT/experiments/.seed137_batch.lock"
# shellcheck source=cp2k_resource.sh
source "$ROOT/experiments/cp2k_resource.sh"

if pgrep -f 'cp2k\.psmp.*seed137_' >/dev/null 2>&1; then
  echo "seed137 batch already running. Exit." >&2
  bash "$ROOT/experiments/exp5_seed137_status_line.sh"
  exit 0
fi

INP="$ROOT/experiments/exp_5_synergy/seed_validation/inputs"
if [[ -z "${NP+x}" || "${NP}" == "$(cp2k_cap_np 4)" ]]; then
  for inp in "$INP"/seed137_*_rigid.inp; do
    [[ -f "$inp" ]] || continue
    base="$(basename "$inp" .inp)"
    out="$INP/${base}.out"
    if [[ -f "$out" ]] && grep -q 'SCF run converged' "$out"; then
      continue
    fi
    if compgen -G "$INP/${base}.out.failed_*" >/dev/null; then
      export NP=2
      echo "seed137: prior ABORT for $base -> NP=$NP" >&2
    fi
    break
  done
fi

export NP="${NP:-$(cp2k_cap_np 4)}"
export MPIRUN="${MPIRUN:-/opt/homebrew/bin/mpirun}"
export CP2K="${CP2K:-/opt/homebrew/bin/cp2k.psmp}"
export CP2K_DATA="${CP2K_DATA:-/opt/homebrew/share/cp2k/data}"
echo "seed137 resume NP=$NP SIMUKIT_MAX_CORES=$SIMUKIT_MAX_CORES" >&2

echo $$ >"$LOCK"
trap 'rm -f "$LOCK"' EXIT

bash "$ROOT/experiments/exp_5_synergy/seed_validation/run_seed137_validation.sh"
