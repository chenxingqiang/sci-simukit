#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
VENV="${SCI_SIMUKIT_VENV:-$ROOT/.venv-analysis}"
REQ="$ROOT/requirements-analysis.txt"
echo "==> sci-simukit DFT analysis install"
echo "    repo: $ROOT"
echo "    venv: $VENV"
if [[ ! -d "$VENV" ]]; then
  python3 -m venv "$VENV"
fi
source "$VENV/bin/activate"
python -m pip install --upgrade pip wheel
python -m pip install -r "$REQ"
echo "==> build C tools"
make -C "$ROOT/c"
echo "==> smoke tests"
python -c "import numpy, pandas, scipy, matplotlib, seaborn, ase; print('python packages OK')"
"$ROOT/c/simukit-sdc" "$ROOT/experiments/exp_10_size_scaling/inputs" >/dev/null
python "$ROOT/paper/figures/fig_si_s3_j_exp4.py"
test -f "$ROOT/paper/figures/out/figure_si_s3_j_exp4.pdf"
echo "Done. Activate: source $VENV/bin/activate"
