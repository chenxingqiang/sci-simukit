#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
python3 paper/figures/fig_si_s5_marcus_pending.py
python3 paper/figures/fig_si_s6_exp4.py
echo "OK: paper/figures/out/figure_s5_marcus_pending.pdf"
echo "OK: paper/figures/out/figure_s6_j_exp4.pdf"
