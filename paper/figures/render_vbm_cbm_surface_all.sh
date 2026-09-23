#!/opt/homebrew/bin/bash
# QuickSurf / MSMS Figure S4 (pristine + B/N/P). Does not touch CPK or ball-and-stick outputs.
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$DIR/../.." && pwd)"
MODE="${VMD_SURFACE_MODE:-msms_cages}"
export VMD_SURFACE_MODE="$MODE"
export VMD_MSMS_PROBE="${VMD_MSMS_PROBE:-1.3}"
export PYTHON="${PYTHON:-/opt/homebrew/Caskroom/miniconda/base/bin/python3}"
# shellcheck source=/dev/null
source "$ROOT/scripts/setup_dft_viz_env.sh" 2>/dev/null || true

echo "=== Surface pristine (VMD_SURFACE_MODE=$MODE probe=${VMD_MSMS_PROBE}A MSMS=${MSMSSERVER:-missing}) ==="
"$DIR/render_vbm_cbm_figure_surface.sh"

echo "=== Surface doped ==="
"$DIR/render_vbm_cbm_doped_figure_surface.sh"

OUT="$ROOT/paper/figures/out"
FF="$ROOT/paper/figures/final_figures"
cp -f "$FF/figureS4_surf_N_vbm_cbm_dos.pdf" "$OUT/figure_s4_vbm_cbm_N.pdf"
cp -f "$FF/figureS4_surf_P_n4_vbm_cbm.pdf" "$OUT/figure_s4_vbm_cbm_P_n4.pdf"
echo "Synced SI: $OUT/figure_s4_vbm_cbm_N.pdf $OUT/figure_s4_vbm_cbm_P_n4.pdf"
echo "Done. Outputs: figureS4_surf_*"
