#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
DIR="$ROOT/experiments/exp_10_size_scaling/mo_cubes_sp/inputs"
ARCH="$ROOT/dft_results/exp_10_size_scaling/mo_cubes"
PY="${PYTHON:-python3}"

stem="${1:-}"
if [[ -z "$stem" ]]; then
  for out in "$DIR"/size_*_mo.out; do
    [[ -f "$out" ]] || continue
    base="$(basename "$out" .out)"
    grep -q 'SCF run converged' "$out" || continue
    dest="$ARCH/$base"
    mkdir -p "$dest"
    cp -f "$DIR/$base.out" "$dest/" 2>/dev/null || true
    shopt -s nullglob
    for f in "$DIR/$base"-WFN_*.cube; do
      cp -f "$f" "$dest/"
    done
  done
else
  dest="$ARCH/$stem"
  mkdir -p "$dest"
  cp -f "$DIR/${stem}.out" "$dest/" 2>/dev/null || true
  shopt -s nullglob
  for f in "$DIR/${stem}"-WFN_*.cube; do
    cp -f "$f" "$dest/"
  done
fi

"$PY" "$ROOT/experiments/exp_10_size_scaling/mo_cubes_sp/analyze_mo_cubes.py" --write
