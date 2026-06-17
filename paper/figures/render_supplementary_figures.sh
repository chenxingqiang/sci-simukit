#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
echo "== Fig S4: VBM/CBM + DOS =="
bash paper/figures/render_vbm_cbm_figure.sh
echo "== Fig S5: polaron lambda =="
bash paper/figures/render_polaron_lambda_figure.sh
echo "== Fig S6: dimer coupling + FCWD =="
bash paper/figures/render_dimer_fcwd_figure.sh
echo "Done: paper/figures/final_figures/"
