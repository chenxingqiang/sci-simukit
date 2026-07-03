#!/usr/bin/env bash
# P0: periodic n=1 P four-corner fixed-cell GEO_OPT (sequential batch).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
# shellcheck source=cp2k_resource.sh
source "$ROOT/experiments/cp2k_resource.sh"

DIR="$ROOT/experiments/exp_10_size_scaling/periodic_relax_validation/inputs"
python3 "$ROOT/experiments/exp_10_size_scaling/periodic_relax_validation/generate_periodic_relax_inputs.py"

if pgrep -f 'cp2k\.psmp' >/dev/null 2>&1; then
  echo "CP2K already running; abort." >&2
  exit 1
fi

export CP2K_DATA="${CP2K_DATA:-/opt/homebrew/share/cp2k/data}"
CP2K="${CP2K:-/opt/homebrew/bin/cp2k.psmp}"
MPIRUN="${MPIRUN:-/opt/homebrew/bin/mpirun}"

for stem in per_relax_n1_pristine_eps0_geo per_relax_n1_pristine_eps3_geo \
            per_relax_n1_P_eps0_geo per_relax_n1_P_eps3_geo; do
  inp="$DIR/${stem}.inp"
  out="$DIR/${stem}.out"
  if grep -q 'GEOMETRY OPTIMIZATION COMPLETED' "$out" 2>/dev/null; then
    echo "skip converged: $stem"
    continue
  fi
  NP="$(cp2k_cap_np 2)"
  echo "=== $stem np=$NP ==="
  (cd "$DIR" && "$MPIRUN" -np "$NP" "$CP2K" -i "$(basename "$inp")" -o "$(basename "$out")")
done

bash "$ROOT/experiments/post_periodic_relax_validation.sh"
