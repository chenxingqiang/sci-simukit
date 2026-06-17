#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT_DIR="$ROOT/paper/figures/final_figures"
CACHE="$OUT_DIR/_vbm_cbm_cache"
TCL="$ROOT/dft_results/vmd_scripts/render_vbm_cbm.tcl"
CUBE_DIR="$ROOT/dft_results/exp_7_electronic_structure/outputs"
HOMO_CUBE="$CUBE_DIR/elec_pos0p0_pristine-WFN_00240_1-1_0.cube"
LUMO_CUBE="$CUBE_DIR/elec_pos0p0_pristine-WFN_00241_1-1_0.cube"
PDOS="$ROOT/experiments/exp_7_electronic_structure/results/elec_pos0p0_pristine-k1-1.pdos"
find_vmd() {
  local vmddir="/Applications/VMD.app/Contents/vmd2/lib"
  local bin="$vmddir/vmd_MACOSXARM64"
  if [[ -x "$bin" ]]; then echo "export VMDDIR=$vmddir; $bin"; return 0; fi
  command -v vmd >/dev/null 2>&1 && { echo vmd; return 0; }
  return 1
}
mkdir -p "$CACHE" "$OUT_DIR"
VBM_TGA="$CACHE/vbm_isosurface.tga"
CBM_TGA="$CACHE/cbm_isosurface.tga"
VBM_PNG="$CACHE/vbm_isosurface.png"
CBM_PNG="$CACHE/cbm_isosurface.png"
OUT_PDF="$OUT_DIR/figureS4_vbm_cbm_dos.pdf"
VMD_CMD="$(find_vmd)" || { echo "VMD not found"; exit 1; }
echo "Rendering VBM/CBM with VMD..."
eval "$VMD_CMD -dispdev text -e \"$TCL\" -args \"$HOMO_CUBE\" \"$LUMO_CUBE\" \"$VBM_TGA\" \"$CBM_TGA\" 0.015"
python3 << CONV
from pathlib import Path
from PIL import Image
for tga, png in [("$VBM_TGA","$VBM_PNG"),("$CBM_TGA","$CBM_PNG")]:
    Image.open(tga).save(png)
    print("converted", png)
CONV
echo "Compositing DOS panel..."
python3 << PY
import sys
sys.path.insert(0, "$ROOT/paper/figures")
from pathlib import Path
from vbm_cbm_dos_panel import compose_vbm_cbm_figure
compose_vbm_cbm_figure(Path("$VBM_PNG"), Path("$CBM_PNG"), Path("$PDOS"), Path("$OUT_PDF"))
PY
echo "Done: $OUT_PDF"
