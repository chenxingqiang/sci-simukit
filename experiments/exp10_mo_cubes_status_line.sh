#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIR="$ROOT/experiments/exp_10_size_scaling/mo_cubes_sp/inputs"
total=0
done_n=0
running=""
for inp in "$DIR"/size_{4,6,8}x60_*_pos0pct_mo.inp; do
  [[ -f "$inp" ]] || continue
  total=$((total + 1))
  base="$(basename "$inp" .inp)"
  out="$DIR/${base}.out"
  if [[ -f "$out" ]] && grep -q 'SCF run converged' "$out"; then
    done_n=$((done_n + 1))
  elif pgrep -f "cp2k\.psmp.*${base}\.inp" >/dev/null 2>&1; then
    running="$base"
  fi
done
echo "Exp10 MO_CUBES ${done_n}/${total} | running=${running:-none}"
