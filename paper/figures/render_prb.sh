#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
PY="${PYTHON:-/opt/homebrew/Caskroom/miniconda/base/bin/python3}"
"$PY" paper/figures/fig_prl_main.py --prb
echo "OK: paper/figures/out/figure_prb_main.pdf"
