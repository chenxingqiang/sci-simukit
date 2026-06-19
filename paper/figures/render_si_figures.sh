#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
PY="${PYTHON:-/opt/homebrew/Caskroom/miniconda/base/bin/python3}"
"$PY" paper/figures/fig_si_s4_pdos_exp7.py
"$PY" paper/figures/fig_si_s5_marcus_pending.py
"$PY" paper/figures/fig_si_s6_exp4.py
echo "OK: paper/figures/out/figure_s4_pdos_exp7.pdf"
echo "OK: paper/figures/out/figure_s5_marcus_pending.pdf"
echo "OK: paper/figures/out/figure_s6_j_exp4.pdf"
