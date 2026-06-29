#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/experiments/exp_10_size_scaling/placement_validation/analyze_periodic_placement.py"
bash "$ROOT/experiments/exp10_placement_status_line.sh"
bash "$ROOT/experiments/exp10_status_line.sh"
