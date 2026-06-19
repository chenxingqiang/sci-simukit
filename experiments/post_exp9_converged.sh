#!/bin/bash
# Refresh Exp9 audit JSON after GEO_OPT or vertical SP completes.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/experiments/analysis/analyze_exp9_polaron.py"
bash "$ROOT/experiments/exp9_status_line.sh"

# Regenerate Fig. S5 when any Marcus lambda is available (vertical SP converged).
n_lambda="$(python3 -c "
import json
d = json.load(open('$ROOT/experiments/analysis/exp9_polaron_verification.json'))
lam = d.get('derived', {}).get('lambda_eV', {})
print(sum(1 for dop in lam.values() for v in dop.values() if v is not None))
" 2>/dev/null || echo 0)"
if [[ "${n_lambda:-0}" -gt 0 ]]; then
  echo "Exp9: ${n_lambda} lambda value(s) — refreshing figure5_polaron_reorganization"
  python3 "$ROOT/paper/figures/polaron_lambda_diagram.py" || true
fi
