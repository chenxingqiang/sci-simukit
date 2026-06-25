#!/bin/bash
# Resume Table IV seed-137 ENERGY batch (skips converged). Mac default: NP=2.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOCK="$ROOT/experiments/.seed137_batch.lock"

if pgrep -f 'cp2k\.psmp.*seed137_' >/dev/null 2>&1; then
  echo "seed137 batch already running. Exit." >&2
  bash "$ROOT/experiments/exp5_seed137_status_line.sh"
  exit 0
fi

export NP="${NP:-2}"
export MPIRUN="${MPIRUN:-/opt/homebrew/bin/mpirun}"
export CP2K="${CP2K:-/opt/homebrew/bin/cp2k.psmp}"
export CP2K_DATA="${CP2K_DATA:-/opt/homebrew/share/cp2k/data}"

echo $$ >"$LOCK"
trap 'rm -f "$LOCK"' EXIT

bash "$ROOT/experiments/exp_5_synergy/seed_validation/run_seed137_validation.sh"
