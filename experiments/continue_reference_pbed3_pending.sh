#!/usr/bin/env bash
# Resume reference-placement PBE+D3 batch (skips converged). MPI capped at ~2/3 CPUs.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOCK="$ROOT/experiments/.reference_pbed3_batch.lock"
# shellcheck source=cp2k_resource.sh
source "$ROOT/experiments/cp2k_resource.sh"

if pgrep -f 'cp2k\.psmp.*refpbed3' >/dev/null 2>&1; then
  echo "reference_pbed3 batch already running. Exit." >&2
  bash "$ROOT/experiments/exp5_reference_pbed3_status_line.sh"
  exit 0
fi

DIR="$ROOT/experiments/exp_5_synergy/reference_pbed3/inputs"
export NP="${NP:-$(cp2k_cap_np 2)}"
for inp in "$DIR"/C60_strain_*_refpbed3.inp; do
  [[ -f "$inp" ]] || continue
  base="$(basename "$inp" .inp)"
  out="$DIR/${base}.out"
  if [[ -f "$out" ]] && grep -q 'SCF run converged' "$out"; then
    continue
  fi
  if compgen -G "$DIR/${base}.out.failed_*" >/dev/null; then
    export NP=2
    echo "reference_pbed3: prior ABORT for $base -> NP=$NP" >&2
  fi
  break
done

export MPIRUN="${MPIRUN:-/opt/homebrew/bin/mpirun}"
export CP2K="${CP2K:-/opt/homebrew/bin/cp2k.psmp}"
export CP2K_DATA="${CP2K_DATA:-/opt/homebrew/share/cp2k/data}"
echo "reference_pbed3 resume NP=$NP SIMUKIT_MAX_CORES=$SIMUKIT_MAX_CORES" >&2

echo $$ >"$LOCK"
trap 'rm -f "$LOCK"' EXIT

export SKIP_GENERATE=1
bash "$ROOT/experiments/exp_5_synergy/reference_pbed3/run_reference_pbed3_validation.sh"
