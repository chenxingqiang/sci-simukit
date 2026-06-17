#!/bin/bash
# One-line Exp8 status for agent loops.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IN="$ROOT/experiments/exp_8_geometry_opt/inputs"
CANON="$IN/geoopt_pristine_sp.out"

count_conv() {
  local f="$1"
  if [[ -f "$f" ]] && grep -q 'SCF run converged' "$f"; then
    echo 1
  else
    echo 0
  fi
}

active_sp_out() {
  local pid f
  for pid in $(pgrep -f 'geoopt_pristine_sp.inp' 2>/dev/null || true); do
    f=$(lsof -p "$pid" 2>/dev/null | awk '/geoopt_pristine_sp.*\.out/{print $NF; exit}' || true)
    if [[ -n "${f:-}" && -f "$f" ]]; then
      echo "$f"
      return
    fi
  done
  # Fallback: largest geoopt_pristine_sp.out* by line count / mtime
  local best="" best_n=0
  for f in "$IN"/geoopt_pristine_sp.out "$IN"/geoopt_pristine_sp.out*; do
    [[ -f "$f" ]] || continue
    local n
    n=$(grep -c 'OT DIIS' "$f" 2>/dev/null || echo 0)
    if (( n > best_n )); then
      best_n=$n
      best=$f
    fi
  done
  if [[ -n "$best" ]]; then
    echo "$best"
  else
    echo "$CANON"
  fi
}

n=0
for base in geoopt_pristine geoopt_N geoopt_B geoopt_P; do
  n=$((n + $(count_conv "$IN/${base}.out")))
done
n=$((n + $(count_conv "$IN/geoopt_N_sp.out")))

SP="$(active_sp_out)"
n=$((n + $(count_conv "$SP")))

running="none"
if pgrep -f 'geoopt_pristine_sp.inp' >/dev/null 2>&1; then
  running="geoopt_pristine_sp"
fi

ot="?"
grad="?"
ot_ref="~330"
if [[ -f "$SP" ]]; then
  ot=$(grep -c 'OT DIIS' "$SP" 2>/dev/null || echo 0)
  ot_line=$(grep 'OT DIIS' "$SP" 2>/dev/null | tail -1 || true)
  if [[ -n "$ot_line" ]]; then
    grad=$(echo "$ot_line" | awk '{print $4}')
  fi
fi

sp_conv=0
grep -q 'SCF run converged' "$SP" 2>/dev/null && sp_conv=1 || true

echo "Exp8 ${n}/6 | running=${running} | OT ${ot}/${ot_ref} | grad=${grad} | sp_out=$(basename "$SP") sp_conv=${sp_conv}"
