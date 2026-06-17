#!/bin/bash
# Exp9 charged polaron — analysis and input prep (does not launch CP2K by default).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "=== Experiment 9: charged polaron ==="
echo "GEO_OPT outputs: dft_results/exp_9_charged_polaron/outputs/"
echo ""

python3 experiments/analysis/analyze_exp9_polaron.py
echo ""
python3 experiments/exp_9_charged_polaron/generate_vertical_sp.py

cat <<'EOF'

Next steps (manual / on request only):
  • Pending GEO_OPT: experiments/exp_9_charged_polaron/run_workflow.sh
  • Vertical lambda inputs: experiments/exp_9_charged_polaron/inputs/vertical/*.inp
  • Legacy mpirun names (*_qpos0.inp) are obsolete — use *_qpos0_opt.inp

Do NOT start new CP2K jobs unless explicitly requested (AGENTS Track A).
EOF
