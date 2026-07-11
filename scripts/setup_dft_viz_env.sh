#!/usr/bin/env bash
# Source: source scripts/setup_dft_viz_env.sh
# Professional DFT visualization CLI (VMD cube/MO, not Python).

VMD_ROOT="/Applications/VMD.app/Contents/vmd2"
VMD_ARM="${VMD_ROOT}/lib/vmd_MACOSXARM64"
if [[ -x "$VMD_ARM" ]]; then
  export VMDDIR="${VMD_ROOT}/lib"
  export VMD="$VMD_ARM"
  # Wrapper in bin/vmd points to another user's path; use ARM binary directly.
  vmd() { "$VMD_ARM" "$@"; }
  export -f vmd 2>/dev/null || true
fi

# MSMS for VMD molecular-surface reps (probe 1.2--1.4 A via VMD_MSMS_PROBE).
if [[ -z "${MSMSSERVER:-}" ]]; then
  _msms=""
  if command -v python3 >/dev/null 2>&1; then
    _msms="$(python3 -c "
import importlib.util
spec = importlib.util.find_spec('msms_binary')
if spec and spec.origin:
    from pathlib import Path
    p = Path(spec.origin).parent / 'bin' / 'msms'
    if p.is_file():
        print(p)
" 2>/dev/null || true)"
  fi
  if [[ -z "$_msms" && -x "${ROOT:-}/dft_results/bin/msms" ]]; then
    _msms="${ROOT}/dft_results/bin/msms"
  fi
  if [[ -n "$_msms" && -x "$_msms" ]]; then
    export MSMSSERVER="$_msms"
    export VMDMSMSUSEFILE=1
  fi
  unset _msms
fi
export VMD_MSMS_PROBE="${VMD_MSMS_PROBE:-1.3}"

vesta_ok=no; ovito_ok=no
[[ -d /Applications/VESTA.app ]] && vesta_ok=yes
[[ -d /Applications/Ovito.app ]] && ovito_ok=yes

echo "DFT viz: VMD=$([[ -x ${VMD_ARM:-} ]] && echo ok || echo missing) MSMS=$([[ -n ${MSMSSERVER:-} ]] && echo ok || echo missing) probe=${VMD_MSMS_PROBE} VESTA=$vesta_ok OVITO=$ovito_ok"
