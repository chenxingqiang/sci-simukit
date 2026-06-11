#!/bin/bash
# Relax SCF tolerance for slow-converging pristine 2×60 Exp10 tasks.
# Use after size_2x60_pristine_pos0pct ABORT or >400 OT steps without convergence.
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
for base in size_2x60_pristine_pos0pct size_2x60_pristine_pos3pct; do
  inp="$DIR/${base}.inp"
  [[ -f "$inp" ]] || continue
  sed -i '' 's/EPS_SCF 1.0E-6/EPS_SCF 1.0E-5/g' "$inp"
  echo "patched: $inp"
done
