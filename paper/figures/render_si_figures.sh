#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
PY="${PYTHON:-python3}"
"$PY" paper/figures/fig_si_s1_pdos_exp7.py
"$PY" paper/figures/fig_si_s2_marcus.py
"$PY" paper/figures/fig_si_s3_j_exp4.py
echo "OK: paper/figures/out/figure_s1_pdos_exp7.pdf"
echo "OK: paper/figures/out/figure_s2_marcus.pdf"
echo "OK: paper/figures/out/figure_s3_j_exp4.pdf"
