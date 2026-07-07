#!/usr/bin/env bash
# Refresh reference-placement PBE+D3 audit JSON after converged task(s).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/experiments/exp_5_synergy/reference_pbed3/analyze_reference_pbed3.py"
bash "$ROOT/experiments/exp5_reference_pbed3_status_line.sh"
