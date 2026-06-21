#!/bin/bash
# Refresh Exp9 audit JSON after GEO_OPT or vertical SP completes.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/experiments/analysis/analyze_exp9_polaron.py"
bash "$ROOT/experiments/exp9_status_line.sh"

# Refresh SI transport figures (S2 picks up lambda_eV when vertical SP converged).
if [[ -f "$ROOT/paper/figures/render_si_figures.sh" ]]; then
  bash "$ROOT/paper/figures/render_si_figures.sh" || true
else
  python3 "$ROOT/paper/figures/fig_si_s2_marcus.py" || true
fi

read -r geo vert n_lambda <<< "$(python3 -c "
import json
d = json.load(open('$ROOT/experiments/analysis/exp9_polaron_verification.json'))
lam = d.get('derived', {}).get('lambda_eV', {})
n_lam = sum(1 for dop in lam.values() for v in dop.values() if v is not None)
geo = d.get('converged', 0)
vert = len((d.get('vertical_sp') or {}).get('outputs_converged') or [])
print(geo, vert, n_lam)
" 2>/dev/null || echo '0 0 0')"
echo "Exp9 audit refreshed; GEO_OPT ${geo}/12 | vertical SP ${vert}/8 | lambda values: ${n_lambda:-0}"
if [[ "$geo" == "12" && "$vert" -lt 8 ]]; then
  if ! pgrep -f 'cp2k\.psmp' >/dev/null 2>&1; then
    echo "GEO_OPT 12/12 — next: bash $ROOT/experiments/continue_exp9_pending.sh (vertical SP queue)"
  else
    echo "GEO_OPT 12/12 — wait for CP2K idle, then: bash $ROOT/experiments/continue_exp9_pending.sh"
  fi
fi

if [[ "$geo" == "12" && "$vert" == "8" ]] && ! pgrep -f 'cp2k\.psmp' >/dev/null 2>&1; then
  echo "Exp9 complete and CP2K idle — next: bash $ROOT/experiments/run_prb_revision_dft.sh"
fi

bash "$ROOT/experiments/cleanup_stale_cp2k.sh" || true
bash "$ROOT/experiments/verify_reliability.sh" || true
