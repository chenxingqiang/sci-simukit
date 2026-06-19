#!/bin/bash
# Exp9 charged polaron — audit, vertical SP input prep, status (no CP2K launch).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "=== Experiment 9: charged polaron ==="
bash experiments/exp9_status_line.sh
echo "GEO_OPT outputs: dft_results/exp_9_charged_polaron/outputs/"
echo ""

python3 experiments/analysis/analyze_exp9_polaron.py
echo ""
python3 experiments/exp_9_charged_polaron/generate_vertical_sp.py

cat <<'EOF2'

Commands:
  • Status:     bash experiments/exp9_status_line.sh
  • Run batch:  bash experiments/continue_exp9_pending.sh   # GEO_OPT pending → vertical SP
  • After job:  bash experiments/post_exp9_converged.sh
  • Audit JSON: experiments/analysis/exp9_polaron_verification.json

Legacy run_workflow.sh uses cp2k.popt (server); Mac local uses cp2k.psmp via continue_exp9_pending.sh.
EOF2
