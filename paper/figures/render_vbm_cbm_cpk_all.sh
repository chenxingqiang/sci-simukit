#!/bin/bash
# One-shot CPK Figure S4 (pristine + B/N/P). Legacy ball-and-stick scripts unchanged.
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== CPK pristine (figureS4_cpk_*) ==="
bash "$DIR/render_vbm_cbm_figure_cpk.sh"

echo "=== CPK doped (figureS4_cpk_{B,N,P}_*) ==="
bash "$DIR/render_vbm_cbm_doped_figure_cpk.sh"

echo "Done. Legacy outputs: figureS4_* (render_vbm_cbm_figure.sh)"
