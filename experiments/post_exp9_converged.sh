#!/bin/bash
# Refresh Exp9 audit JSON after GEO_OPT or vertical SP completes.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/experiments/analysis/analyze_exp9_polaron.py"
bash "$ROOT/experiments/exp9_status_line.sh"

# Refresh SI transport figures (S5 picks up lambda_eV when vertical SP converged).
if [[ -f "$ROOT/paper/figures/render_si_figures.sh" ]]; then
  bash "$ROOT/paper/figures/render_si_figures.sh" || true
else
  python3 "$ROOT/paper/figures/fig_si_s5_marcus_pending.py" || true
fi

n_lambda="$(python3 -c "
import json
d = json.load(open('$ROOT/experiments/analysis/exp9_polaron_verification.json'))
lam = d.get('derived', {}).get('lambda_eV', {})
print(sum(1 for dop in lam.values() for v in dop.values() if v is not None))
" 2>/dev/null || echo 0)"
echo "Exp9 audit refreshed; lambda values in JSON: ${n_lambda:-0}"
