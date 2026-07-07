#!/usr/bin/env bash
# Reference-placement (seed 42) tetramer grid — PBE+D3 modernization (Table I matched-functional).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
DIR="$ROOT/experiments/exp_5_synergy/reference_pbed3/inputs"
LOG="$ROOT/experiments/local_run.log"
# shellcheck source=cp2k_resource.sh
source "$ROOT/experiments/cp2k_resource.sh"
export CP2K_DATA="${CP2K_DATA:-/opt/homebrew/share/cp2k/data}"
CP2K="${CP2K:-/opt/homebrew/bin/cp2k.psmp}"
MPIRUN="${MPIRUN:-/opt/homebrew/bin/mpirun}"

if pgrep -f 'cp2k\.psmp.*refpbed3' >/dev/null 2>&1; then
  echo "reference_pbed3 CP2K already running; abort." >&2
  exit 1
fi

if [[ "${SKIP_GENERATE:-0}" != 1 ]]; then
  python3 "$ROOT/experiments/exp_5_synergy/reference_pbed3/generate_reference_pbed3_inputs.py"
fi

for inp in "$DIR"/*.inp; do
  base="$(basename "$inp" .inp)"
  out="$DIR/${base}.out"
  if [[ -f "$out" ]] && grep -q 'SCF run converged' "$out"; then
    echo "[skip] $base"
    continue
  fi
  if [[ -f "$out" ]] && grep -q 'ABORT' "$out"; then
    ts="$(date +%Y%m%d_%H%M%S)"
    mv "$out" "${out}.failed_${ts}"
    echo "[archive] $base ABORT -> ${out}.failed_${ts}"
  fi
  if compgen -G "$DIR/${base}.out.failed_*" >/dev/null 2>&1; then
    if grep -qE 'EPS_SCF[[:space:]]+1\.0E-6' "$inp"; then
      bash "$ROOT/experiments/relax_reference_pbed3_eps.sh" "$base"
      echo "[relax] prior failure(s) for $base -> EPS_SCF 1e-5 before retry"
    fi
  fi
  NP="$(cp2k_cap_np 2)"
  echo "[$(date -Iseconds)] START $base np=$NP" | tee -a "$LOG"
  (cd "$DIR" && "$MPIRUN" -np "$NP" "$CP2K" -i "${base}.inp" -o "${base}.out")
  if grep -q 'SCF run converged' "$out" 2>/dev/null; then
    bash "$ROOT/experiments/post_reference_pbed3_validation.sh" || true
  fi
done

python3 "$ROOT/experiments/exp_5_synergy/reference_pbed3/analyze_reference_pbed3.py"
