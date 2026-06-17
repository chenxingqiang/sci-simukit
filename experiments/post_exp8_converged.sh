#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EXP8="$ROOT/experiments/exp_8_geometry_opt/inputs"
CANON="$EXP8/geoopt_pristine_sp.out"

SRC=""
if [[ -f "$CANON" ]] && grep -q 'SCF run converged' "$CANON"; then
  SRC="$CANON"
else
  for f in "$EXP8"/geoopt_pristine_sp.out*; do
    [[ -f "$f" ]] || continue
    if grep -q 'SCF run converged' "$f"; then
      SRC="$f"
      break
    fi
  done
fi

if [[ -z "$SRC" ]]; then
  echo "geoopt_pristine_sp not converged (checked canonical + geoopt_pristine_sp.out*)" >&2
  exit 1
fi

if [[ "$SRC" != "$CANON" ]]; then
  cp "$SRC" "$CANON"
  echo "Consolidated $(basename "$SRC") -> geoopt_pristine_sp.out"
fi

mkdir -p "$ROOT/dft_results/exp_8_geometry_opt/outputs"
cp "$CANON" "$ROOT/dft_results/exp_8_geometry_opt/outputs/"
echo "Exp8: geoopt_pristine_sp archived (6/6 complete)"
