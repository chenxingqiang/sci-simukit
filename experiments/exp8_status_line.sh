#!/bin/bash
# One-line Exp8 status for agent loops.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IN="$ROOT/experiments/exp_8_geometry_opt/inputs"
SP="$IN/geoopt_pristine_sp.out"

count_conv() {
  local f="$1"
  if [[ -f "$f" ]] && grep -q 'SCF run converged' "$f"; then
    echo 1
  else
    echo 0
  fi
}

n=0
for base in geoopt_pristine geoopt_N geoopt_B geoopt_P; do
  n=$((n + $(count_conv "$IN/${base}.out")))
done
n=$((n + $(count_conv "$IN/geoopt_N_sp.out")))
n=$((n + $(count_conv "$SP")))

running="none"
if pgrep -f 'prterun.*geoopt_pristine_sp' >/dev/null 2>&1; then
  running="geoopt_pristine_sp"
fi

ot="?"
grad="?"
if [[ -f "$SP" ]]; then
  ot_line=$(grep 'OT DIIS' "$SP" 2>/dev/null | tail -1 || true)
  if [[ -n "$ot_line" ]]; then
    ot=$(echo "$ot_line" | awk '{print $1}')
    grad=$(echo "$ot_line" | awk '{print $4}')
  fi
fi

sp_conv=0
grep -q 'SCF run converged' "$SP" 2>/dev/null && sp_conv=1 || true

echo "Exp8 ${n}/6 | running=${running} | OT ${ot}/? | grad=${grad} | sp_conv=${sp_conv} | next=geoopt_pristine_sp"
