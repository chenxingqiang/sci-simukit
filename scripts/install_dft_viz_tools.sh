#!/usr/bin/env bash
# Professional DFT visualization tools (VMD / VESTA / OVITO) for sci-simukit.
# Not Python — structure, cube/MO, trajectory analysis.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== sci-simukit DFT visualization tools ==="

# 1) VMD — usually manual from https://www.ks.uiuc.edu/Research/vmd/
if [[ -d /Applications/VMD.app ]]; then
  echo "[OK] VMD already at /Applications/VMD.app"
else
  echo "[ ] VMD: download Apple Silicon build from VMD site, drag to Applications"
fi

# 2) VESTA — crystal / charge density
if [[ -d /Applications/VESTA.app ]]; then
  echo "[OK] VESTA"
elif command -v brew >/dev/null; then
  echo "[..] Installing VESTA via Homebrew..."
  HOMEBREW_NO_AUTO_UPDATE=1 brew install --cask vesta
else
  echo "[ ] VESTA: https://jp-minerals.org/vesta/en/download.html"
fi

# 3) OVITO — trajectory / atomistic analysis (~170MB)
if [[ -d /Applications/Ovito.app ]]; then
  echo "[OK] OVITO"
elif command -v brew >/dev/null; then
  echo "[..] Installing OVITO via Homebrew (large download)..."
  HOMEBREW_NO_AUTO_UPDATE=1 brew install --cask ovito
else
  echo "[ ] OVITO: https://www.ovito.org/download/"
fi

echo ""
echo "Configure shell (add to ~/.zshrc):"
echo "  source $ROOT/scripts/setup_dft_viz_env.sh"
echo ""
echo "Project usage:"
echo "  dft_results/vmd_scripts/README.md"
echo "  bash paper/figures/render_vbm_cbm_figure.sh   # needs VMD + HOMO/LUMO cube"
