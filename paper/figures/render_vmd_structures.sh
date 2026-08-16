#!/bin/bash
# Export Exp5 tetramer XYZ + VMD scheme panels (Pristine | B | N | P).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT_DIR="$ROOT/paper/figures/final_figures"
XYZ_EXP5="$ROOT/dft_results/exp_5_synergy/xyz_structures"
TCL="$ROOT/dft_results/vmd_scripts/render_scheme_panels.tcl"
PY="${PYTHON:-/opt/homebrew/Caskroom/miniconda/base/bin/python3}"

# shellcheck source=/dev/null
source "$ROOT/scripts/setup_dft_viz_env.sh" 2>/dev/null || true

find_vmd() {
  if [[ -n "${VMD:-}" && -x "${VMD}" ]]; then
    echo "$VMD"
    return 0
  fi
  if command -v vmd >/dev/null 2>&1; then
    command -v vmd
    return 0
  fi
  for c in \
    /Applications/VMD.app/Contents/vmd2/lib/vmd_MACOSXARM64 \
    /Applications/VMD.app/Contents/vmd/vmd_MACARM64 \
    /Applications/VMD.app/Contents/vmd/vmd_MACOSXX86_64; do
    [[ -x "$c" ]] && { echo "$c"; return 0; }
  done
  return 1
}

mkdir -p "$OUT_DIR" "$XYZ_EXP5"

echo "Exporting XYZ from dft_results/exp_5_synergy ..."
"$PY" << PY
from pathlib import Path
import sys
sys.path.insert(0, "$ROOT/dft_results")
from export_xyz_files import process_experiment

base = Path("$ROOT/dft_results")
for exp in ("exp_5_synergy",):
    d = base / exp
    if d.exists():
        n = process_experiment(d)
        print(f"  {exp}: {n} xyz")
PY

for req in \
  C60_strain_+0.0_pristine_synergy.xyz \
  C60_strain_+0.0_B_doped_synergy.xyz \
  C60_strain_+0.0_N_doped_synergy.xyz \
  C60_strain_+0.0_P_doped_synergy.xyz; do
  if [[ ! -f "$XYZ_EXP5/$req" ]]; then
    echo "Missing $XYZ_EXP5/$req — check export_xyz_files.py / inp files"
    exit 1
  fi
done

VMD_BIN="$(find_vmd)" || {
  echo "VMD not found — install VMD or: source scripts/setup_dft_viz_env.sh"
  echo "Interactive fallback: cd $ROOT/dft_results/exp_5_synergy && vmd -e vmd_compare.tcl"
  exit 1
}

echo "Rendering scheme panels with VMD ..."
"$VMD_BIN" -dispdev text -e "$TCL" -args "$OUT_DIR" "$XYZ_EXP5"


echo "Converting TGA renders to PNG ..."
"$PY" << PYCONV
from pathlib import Path
from PIL import Image, ImageEnhance

out = Path("$OUT_DIR")

def enhance(img: Image.Image) -> Image.Image:
    rgb = img.convert("RGB")
    rgb = ImageEnhance.Contrast(rgb).enhance(1.14)
    rgb = ImageEnhance.Color(rgb).enhance(1.22)
    rgb = ImageEnhance.Sharpness(rgb).enhance(1.10)
    return rgb

for tga in sorted(out.glob("*.tga")):
    png = tga.with_suffix(".png")
    enhance(Image.open(tga)).save(png)
    print("converted", png.name)
PYCONV

if command -v magick >/dev/null 2>&1 && [[ -f "$OUT_DIR/scheme_tetramer_doping.png" ]]; then
  magick "$OUT_DIR/scheme_tetramer_doping.png" "$OUT_DIR/figure0_structure_scheme.pdf"
  echo "Wrote $OUT_DIR/figure0_structure_scheme.pdf"
elif command -v convert >/dev/null 2>&1 && [[ -f "$OUT_DIR/scheme_tetramer_doping.png" ]]; then
  convert "$OUT_DIR/scheme_tetramer_doping.png" "$OUT_DIR/figure0_structure_scheme.pdf"
  echo "Wrote $OUT_DIR/figure0_structure_scheme.pdf"
fi

echo "Done: $OUT_DIR/scheme_tetramer_doping.png (+ per-structure PNG)"

