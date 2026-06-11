#!/bin/bash
# Copy converged Exp10 .out files to dft_results/ (gitignored *.out stay local-only).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/experiments/exp_10_size_scaling/inputs"
DST="$ROOT/dft_results/exp_10_size_scaling"
mkdir -p "$DST"
n=0
for f in "$SRC"/size_*.out; do
  [[ -f "$f" ]] || continue
  if grep -q 'SCF run converged' "$f" 2>/dev/null; then
    cp -f "$f" "$DST/"
    n=$((n + 1))
  fi
done
echo "synced $n converged Exp10 outputs -> $DST"
