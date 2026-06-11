#!/bin/bash
# Run after an Exp10 task converges: archive, refresh SDC JSON, report counts.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INPUTS="$ROOT/experiments/exp_10_size_scaling/inputs"
SDC="$ROOT/c/simukit-sdc"

bash "$ROOT/experiments/sync_exp10_archive.sh"
python3 "$ROOT/experiments/update_exp10_status.py"

if [[ -x "$SDC" ]]; then
  "$SDC" "$INPUTS"
elif [[ -x "$ROOT/c/build/simukit-sdc" ]]; then
  "$ROOT/c/build/simukit-sdc" "$INPUTS"
else
  echo "simukit-sdc not built; run: cd c && make" >&2
  exit 1
fi

n=$(grep -l 'SCF run converged' "$INPUTS"/size_*.out 2>/dev/null | wc -l | tr -d ' ')
echo "Exp10 converged: ${n}/40"
echo "SDC JSON: $ROOT/experiments/analysis/sdc/sdc_exp10_results.json"
echo "SDC audit: $ROOT/experiments/analysis/sdc/sdc_exp10_synergy_audit.json"

CANON="$ROOT/experiments/analysis/sdc/sdc_exp10_results.json"
PENDING="$ROOT/paper/figures/pending"
if [[ -f "$CANON" ]] && command -v python3 >/dev/null; then
  python3 "$ROOT/src/sdc_coupling_analysis.py" --plots-from-json "$CANON" || true
  mkdir -p "$PENDING"
  cp "$ROOT/experiments/analysis/sdc/figures/sdc_synergy_vs_size_eps3pct_epa.pdf" "$PENDING/" 2>/dev/null || true
  cp "$ROOT/experiments/analysis/sdc/figures/sdc_synergy_vs_size_eps3pct_epa.png" "$PENDING/" 2>/dev/null || true
fi
