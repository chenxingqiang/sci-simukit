#!/usr/bin/env bash
# After ABORT / OT stall on a placement SP: relax EPS_SCF 1e-6 -> 1e-5 (idempotent).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
INP_DIR="$ROOT/experiments/exp_10_size_scaling/placement_validation/inputs"
base="${1:?usage: relax_placement_stall_eps.sh <task_base>}"
inp="$INP_DIR/${base}.inp"
[[ -f "$inp" ]] || { echo "missing $inp" >&2; exit 1; }
if grep -q "EPS_SCF 1.0E-6" "$inp"; then
  sed -i.bak "s/EPS_SCF 1.0E-6/EPS_SCF 1.0E-5/g" "$inp"
  echo "relaxed EPS_SCF -> 1e-5 for $base"
else
  echo "EPS already relaxed or non-default for $base"
fi
rm -f "$INP_DIR/${base}"-RESTART.wfn "$INP_DIR/${base}"-RESTART.wfn.bak-1 2>/dev/null || true
