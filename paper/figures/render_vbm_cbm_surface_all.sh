#!/bin/bash
# QuickSurf / MSMS Figure S4 (pristine + B/N/P). Does not touch CPK or ball-and-stick outputs.
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
MODE="${VMD_SURFACE_MODE:-msms_cages}"
export VMD_SURFACE_MODE="$MODE"
export VMD_MSMS_PROBE="${VMD_MSMS_PROBE:-1.3}"

echo "=== Surface pristine (VMD_SURFACE_MODE=$MODE probe=${VMD_MSMS_PROBE}A) ==="
bash "$DIR/render_vbm_cbm_figure_surface.sh"

echo "=== Surface doped ==="
bash "$DIR/render_vbm_cbm_doped_figure_surface.sh"

echo "Done. Outputs: figureS4_surf_*"
