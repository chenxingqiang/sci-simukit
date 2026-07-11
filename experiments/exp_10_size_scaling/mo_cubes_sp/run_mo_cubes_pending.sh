#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
DIR="$ROOT/experiments/exp_10_size_scaling/mo_cubes_sp/inputs"
LOG="$ROOT/experiments/local_run.log"
LOCK="$ROOT/experiments/.mo_cubes_batch.lock"
# shellcheck source=cp2k_resource.sh
source "$ROOT/experiments/cp2k_resource.sh"

if [[ -f "$LOCK" ]] && kill -0 "$(cat "$LOCK")" 2>/dev/null; then
  echo "mo_cubes batch already running (pid $(cat "$LOCK")). Exit." >&2
  bash "$ROOT/experiments/exp10_mo_cubes_status_line.sh"
  exit 0
fi
if pgrep -f 'cp2k\.psmp.*size_[468]x60_.*_mo' >/dev/null 2>&1; then
  echo "CP2K mo_cubes job already running. Exit." >&2
  exit 0
fi

export MPIRUN="${MPIRUN:-/opt/homebrew/bin/mpirun}"
export CP2K="${CP2K:-/opt/homebrew/bin/cp2k.psmp}"
export CP2K_DATA="${CP2K_DATA:-/opt/homebrew/share/cp2k/data}"

suggest_np() {
  local base="$1"
  local np=4
  if [[ "$base" == size_8x60_* ]]; then np=10
  elif [[ "$base" == size_6x60_* ]]; then np=8
  elif [[ "$base" == size_4x60_* ]]; then np=6
  fi
  cp2k_cap_np "$np"
}

echo $$ >"$LOCK"
trap 'rm -f "$LOCK"' EXIT

python3 "$ROOT/experiments/exp_10_size_scaling/mo_cubes_sp/generate_mo_cubes_inputs.py" >/dev/null

for inp in "$DIR"/size_{4,6,8}x60_*_pos0pct_mo.inp; do
  [[ -f "$inp" ]] || continue
  base="$(basename "$inp" .inp)"
  out="$DIR/${base}.out"
  if [[ -f "$out" ]] && grep -q 'SCF run converged' "$out"; then
    continue
  fi
  NP="$(suggest_np "$base")"
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) START mo_cubes: $base np=$NP" >>"$LOG"
  echo "Running $base (np=$NP) ..." >&2
  (
    cd "$DIR"
    "$MPIRUN" -np "$NP" "$CP2K" -i "${base}.inp" -o "${base}.out"
  )
  if grep -q 'SCF run converged' "$out"; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) DONE mo_cubes: $base" >>"$LOG"
    bash "$ROOT/experiments/exp_10_size_scaling/mo_cubes_sp/post_mo_cubes_converged.sh" "$base"
  else
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FAIL mo_cubes: $base" >>"$LOG"
    echo "WARNING: $base did not converge" >&2
  fi
done

bash "$ROOT/experiments/exp10_mo_cubes_status_line.sh"
