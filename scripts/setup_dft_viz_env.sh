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

vesta_ok=no; ovito_ok=no
[[ -d /Applications/VESTA.app ]] && vesta_ok=yes
[[ -d /Applications/Ovito.app ]] && ovito_ok=yes

echo "DFT viz: VMD=$([[ -x ${VMD_ARM:-} ]] && echo ok || echo missing) VESTA=$vesta_ok OVITO=$ovito_ok"
