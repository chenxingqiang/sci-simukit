#!/bin/bash
# CPK / space-filling Figure S4 (parallel to render_vbm_cbm_figure.sh; does not replace it).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT_DIR="$ROOT/paper/figures/final_figures"
CACHE="$OUT_DIR/_vbm_cbm_cache_cpk"
TCL_ISO="$ROOT/dft_results/vmd_scripts/render_vbm_cbm.tcl"
TCL_PERIODIC="$ROOT/dft_results/vmd_scripts/render_vbm_cbm_periodic.tcl"
TCL_STRUCT="$ROOT/dft_results/vmd_scripts/render_structure_cpk.tcl"
TCL_CAGE="$ROOT/dft_results/vmd_scripts/render_vbm_cbm_cage.tcl"
# physical = full supercell at DFT coordinates (default); 2x4 / 4x2 = per-cage tile mosaic
N8_LAYOUT="${VBM_N8_LAYOUT:-physical}"
# cpk | cages | auto (cages for n>=4, cpk for n=2)
CPK_MODE="${VMD_CPK_MODE:-cpk}"

cpk_mode_for_n() {
  local n="$1"
  case "${CPK_MODE}" in
    auto) [[ "$n" -ge 4 ]] && echo cages || echo cpk ;;
    *) echo "${CPK_MODE}" ;;
  esac
}


n8_use_tiles() {
  case "${N8_LAYOUT}" in
    2x4|4x2) return 0 ;;
    *) return 1 ;;
  esac
}
EXP7_OUT="$ROOT/dft_results/exp_7_electronic_structure/outputs"
EXP10_INP="$ROOT/experiments/exp_10_size_scaling/inputs"
MO_MANIFEST="$ROOT/experiments/analysis/mo_cubes_exp10.json"
PDOS="$EXP7_OUT/elec_pos0p0_pristine-k1-1.pdos"
PY="${PYTHON:-/opt/homebrew/Caskroom/miniconda/base/bin/python3}"

lookup_mo_cubes() {
  local stem="$1"
  "$PY" -c "
import json, sys
from pathlib import Path
m = Path('$MO_MANIFEST')
if not m.is_file():
    sys.exit(1)
info = json.loads(m.read_text()).get('systems', {}).get('$stem', {})
h, l = info.get('homo_cube'), info.get('lumo_cube')
if h and l and Path(h).is_file() and Path(l).is_file():
    print(h)
    print(l)
    sys.exit(0)
sys.exit(1)
" 2>/dev/null || return 1
}

# shellcheck source=/dev/null
source "$ROOT/scripts/setup_dft_viz_env.sh" 2>/dev/null || true

find_vmd() {
  if [[ -n "${VMD:-}" && -x "${VMD}" ]]; then
    echo "$VMD"
    return 0
  fi
  command -v vmd >/dev/null 2>&1 && { command -v vmd; return 0; }
  local vmddir="/Applications/VMD.app/Contents/vmd2/lib"
  local bin="$vmddir/vmd_MACOSXARM64"
  [[ -x "$bin" ]] && { export VMDDIR="$vmddir"; echo "$bin"; return 0; }
  return 1
}

tga_to_png() {
  "$PY" -c "
from pathlib import Path
from PIL import Image
tga = Path('$1')
png = tga.with_suffix('.png')
Image.open(tga).save(png)
print('converted', png.name)
"
}

render_isosurface_pair() {
  local homo="$1" lumo="$2" tag="$3"
  local vbm_tga="$CACHE/${tag}_vbm.tga"
  local cbm_tga="$CACHE/${tag}_cbm.tga"
  echo "  VMD isosurface $tag ..."
  "$VMD_BIN" -dispdev text -e "$TCL_ISO" -args "$homo" "$lumo" "$vbm_tga" "$cbm_tga" 0.015
  tga_to_png "$vbm_tga"
  tga_to_png "$cbm_tga"
}

render_isosurface_periodic() {
  local homo="$1" lumo="$2" xyz="$3" tag="$4"
  local vbm_tga="$CACHE/${tag}_vbm.tga"
  local cbm_tga="$CACHE/${tag}_cbm.tga"
  echo "  VMD periodic isosurface $tag (physical supercell) ..."
  "$VMD_BIN" -dispdev text -e "$TCL_PERIODIC" -args "$homo" "$xyz" "$vbm_tga" 11 0.015
  "$VMD_BIN" -dispdev text -e "$TCL_PERIODIC" -args "$lumo" "$xyz" "$cbm_tga" 10 0.015
  tga_to_png "$vbm_tga"
  tga_to_png "$cbm_tga"
}

render_structure() {
  local xyz="$1" tag="$2" n="$3"
  local mode
  mode="$(cpk_mode_for_n "$n")"
  local tga="$CACHE/${tag}_struct.tga"
  echo "  VMD CPK structure $tag (mode=$mode) ..."
  "$VMD_BIN" -dispdev text -e "$TCL_STRUCT" -args "$xyz" "$tga" "" "$mode"
  tga_to_png "$tga"
}

render_cage_tile_orbital() {
  local cube="$1" cage_xyz="$2" out_tga="$3" color_id="$4"
  "$VMD_BIN" -dispdev text -e "$TCL_CAGE" -args "$cube" "$cage_xyz" "$out_tga" "$color_id" 0.015
  tga_to_png "$out_tga"
}

render_cage_tile_struct() {
  local cage_xyz="$1" out_tga="$2"
  "$VMD_BIN" -dispdev text -e "$TCL_STRUCT" -args "$cage_xyz" "$out_tga"
  tga_to_png "$out_tga"
}

export_n8_cage_xyzs() {
  local inp="$1" cage_dir="$2"
  mkdir -p "$cage_dir"
  "$PY" << PY
import sys
sys.path.insert(0, "$ROOT/dft_results")
sys.path.insert(0, "$ROOT/paper/figures")
from pathlib import Path
from export_xyz_files import extract_coords_from_inp
from vbm_cbm_dos_panel import export_cage_xyzs, parse_tile_grid

nrow, ncol = parse_tile_grid("$N8_LAYOUT")
coords = extract_coords_from_inp(Path("$inp"))
export_cage_xyzs(coords, Path("$cage_dir"), nrow=nrow, ncol=ncol)
print(f"  cages {nrow}x{ncol} -> $cage_dir")
PY
}

render_n8_tiles_orbital() {
  local homo="$1" lumo="$2" inp="$3" tag="$4"
  local cage_dir="$CACHE/cages_${tag}"
  echo "  n=8 orbital tiles ($N8_LAYOUT) $tag ..."
  export_n8_cage_xyzs "$inp" "$cage_dir"
  local k
  for k in $(seq 0 7); do
    render_cage_tile_orbital "$homo" "$cage_dir/cage${k}.xyz" "$CACHE/${tag}_cage${k}_vbm.tga" 11
    render_cage_tile_orbital "$lumo" "$cage_dir/cage${k}.xyz" "$CACHE/${tag}_cage${k}_cbm.tga" 10
  done
}

render_n8_tiles_struct() {
  local inp="$1" tag="$2"
  local cage_dir="$CACHE/cages_${tag}"
  echo "  n=8 structure tiles ($N8_LAYOUT) $tag ..."
  export_n8_cage_xyzs "$inp" "$cage_dir"
  local k
  for k in $(seq 0 7); do
    render_cage_tile_struct "$cage_dir/cage${k}.xyz" "$CACHE/${tag}_cage${k}_struct.tga"
  done
}

mkdir -p "$CACHE" "$OUT_DIR"
VMD_BIN="$(find_vmd)" || { echo "VMD not found"; exit 1; }
[[ -f "$PDOS" ]] || { echo "Missing PDOS: $PDOS"; exit 1; }

XYZ_DIR="$CACHE/xyz"
mkdir -p "$XYZ_DIR"

echo "Exporting Exp.10 pristine XYZ ..."
"$PY" << PY
import sys
sys.path.insert(0, "$ROOT/dft_results")
from pathlib import Path
from export_xyz_files import extract_coords_from_inp, write_xyz

inp_dir = Path("$EXP10_INP")
out_dir = Path("$XYZ_DIR")
for n in (2, 4, 6, 8):
    stem = f"size_{n}x60_pristine_pos0pct"
    inp = inp_dir / f"{stem}.inp"
    if not inp.is_file():
        raise SystemExit(f"missing {inp}")
    coords = extract_coords_from_inp(inp)
    write_xyz(coords, out_dir / f"{stem}.xyz", f"{stem}, {len(coords)} atoms")
    print("  xyz", stem, len(coords))
PY

declare -a PANEL_LINES=()
HOMO_N2="$EXP7_OUT/elec_pos0p0_pristine-WFN_00240_1-1_0.cube"
LUMO_N2="$EXP7_OUT/elec_pos0p0_pristine-WFN_00241_1-1_0.cube"

for n in 2 4 6 8; do
  stem="size_${n}x60_pristine_pos0pct"
  inp="$EXP10_INP/${stem}.inp"
  xyz="$XYZ_DIR/${stem}.xyz"
  tag="n${n}"
  echo "Size n=$n ..."
  if [[ "$n" -eq 8 ]] && n8_use_tiles; then
    if _cubes=() && mapfile -t _cubes < <(lookup_mo_cubes "$stem") && [[ ${#_cubes[@]} -ge 2 ]]; then
      render_n8_tiles_orbital "${_cubes[0]}" "${_cubes[1]}" "$inp" "$tag"
      PANEL_LINES+=("8|TILES|${tag}|orbital|orbital|${N8_LAYOUT}")
    else
      render_n8_tiles_struct "$inp" "$tag"
      PANEL_LINES+=("8|TILES|${tag}|struct|struct|${N8_LAYOUT}")
    fi
  elif [[ "$n" -eq 2 && -f "$HOMO_N2" && -f "$LUMO_N2" ]]; then
    render_isosurface_pair "$HOMO_N2" "$LUMO_N2" "$tag"
    PANEL_LINES+=("$n|${CACHE}/${tag}_vbm.png|${CACHE}/${tag}_cbm.png|orbital|orbital")
  elif _cubes=() && mapfile -t _cubes < <(lookup_mo_cubes "$stem") && [[ ${#_cubes[@]} -ge 2 ]]; then
    render_isosurface_periodic "${_cubes[0]}" "${_cubes[1]}" "$xyz" "$tag"
    PANEL_LINES+=("$n|${CACHE}/${tag}_vbm.png|${CACHE}/${tag}_cbm.png|orbital|orbital")
  else
    render_structure "$xyz" "$tag" "$n"
    PANEL_LINES+=("$n|${CACHE}/${tag}_struct.png|${CACHE}/${tag}_struct.png|struct|struct")
  fi
done

OUT_PDF="$OUT_DIR/figureS4_cpk_vbm_cbm_dos.pdf"
echo "Compositing ..."
"$PY" << PY
import sys
sys.path.insert(0, "$ROOT/paper/figures")
from pathlib import Path
from vbm_cbm_dos_panel import build_panel_from_line, compose_size_scaling_vbm_figure, compose_single_size_figure

lines = """$(printf '%s\n' "${PANEL_LINES[@]}")""".strip().splitlines()
cache = Path("$CACHE")
panels = [build_panel_from_line(line, cache) for line in lines if line.strip()]

from vbm_cbm_dos_panel import _cpk_supercell_caption
cpk_mode = "$CPK_MODE"
caption = (lambda: _cpk_supercell_caption(mode="cages")) if cpk_mode in ("cages", "auto") else (lambda: _cpk_supercell_caption(mode="cpk"))
compose_size_scaling_vbm_figure(
    panels,
    Path("$PDOS"),
    Path("$OUT_PDF"),
    supercell_caption=caption,
)

for panel in panels:
    stem = f"figureS4_cpk_n{panel.n}_vbm_cbm"
    out = Path("$OUT_DIR") / f"{stem}.pdf"
    compose_single_size_figure(
        panel,
        out,
        include_pdos=(panel.n == 2),
        pdos_path=Path("$PDOS") if panel.n == 2 else None,
        supercell_caption=caption,
    )
PY

echo "Done: $OUT_PDF + per-size figureS4_cpk_n{2,4,6,8}_vbm_cbm.pdf"
echo "Ball-and-stick (legacy): bash paper/figures/render_vbm_cbm_figure.sh"
echo "Doped CPK panels: bash paper/figures/render_vbm_cbm_doped_figure_cpk.sh"
