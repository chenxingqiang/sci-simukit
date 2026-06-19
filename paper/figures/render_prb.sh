#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
python3 paper/figures/fig_prl_main.py --prb
echo "OK: paper/figures/out/figure_prb_main.pdf"
