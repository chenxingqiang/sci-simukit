#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
PY="${PYTHON:-python3}"
"$PY" paper/figures/fig_prb_four_main.py
# Keep legacy single-row composite for optional SI/PRL use
"$PY" paper/figures/fig_prl_main.py --prb >/dev/null || true
echo "OK: paper/figures/out/figure_prb_{1..4}_*.pdf"
