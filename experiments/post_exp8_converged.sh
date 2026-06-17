#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EXP8="$ROOT/experiments/exp_8_geometry_opt/inputs"
OUT="$EXP8/geoopt_pristine_sp.out"
if [[ ! -f "$OUT" ]] || ! grep -q 'SCF run converged' "$OUT"; then
  echo "geoopt_pristine_sp not converged" >&2
  exit 1
fi
mkdir -p "$ROOT/dft_results/exp_8_geometry_opt/outputs"
cp "$OUT" "$ROOT/dft_results/exp_8_geometry_opt/outputs/"
echo "Exp8: geoopt_pristine_sp archived (6/6 complete)"
