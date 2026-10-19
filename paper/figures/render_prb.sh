#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
PY="${PYTHON:-python3}"
"$PY" paper/figures/prb_main_figures.py
"$PY" paper/figures/fig_prl_main.py --prb >/dev/null || true
echo "OK: paper/figures/out/figure_prb_{1..4}_*.pdf"
