#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT_DIR="$ROOT/paper/figures/final_figures"
XYZ_EXP5="$ROOT/dft_results/exp_5_synergy/xyz_structures"
TCL="$ROOT/dft_results/vmd_scripts/render_scheme_panels.tcl"

find_vmd() {
  if command -v vmd >/dev/null 2>&1; then command -v vmd; return 0; fi
  for c in \
    /Applications/VMD.app/Contents/vmd/vmd_MACARM64 \
    /Applications/VMD.app/Contents/vmd/vmd_MACOSXX86_64; do
    [[ -x "$c" ]] && { echo "$c"; return 0; }
  done
  return 1
}

mkdir -p "$OUT_DIR"
python3 << PY
from pathlib import Path
import sys
sys.path.insert(0, "$ROOT/dft_results")
from export_xyz_files import process_experiment
base = Path("$ROOT/dft_results")
for exp in ("exp_1_structure", "exp_5_synergy"):
    d = base / exp
    if d.exists():
        process_experiment(d)
PY

VMD_BIN="$(find_vmd)" || {
  echo "VMD not found — open interactively:"
  echo "  cd $ROOT/dft_results/exp_5_synergy && vmd -e vmd_compare.tcl"
  exit 0
}

"$VMD_BIN" -dispdev text -e "$TCL" -args "$OUT_DIR" "$XYZ_EXP5"
if command -v convert >/dev/null 2>&1 && [[ -f "$OUT_DIR/scheme_tetramer_doping.png" ]]; then
  convert "$OUT_DIR/scheme_tetramer_doping.png" "$OUT_DIR/figure0_structure_scheme.pdf"
fi
echo "Done: $OUT_DIR/"
