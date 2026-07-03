#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/experiments/exp_10_size_scaling/periodic_relax_validation/analyze_periodic_relax_s.py"
bash "$ROOT/experiments/exp10_periodic_relax_status_line.sh"
