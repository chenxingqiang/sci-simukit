#!/bin/bash
# =============================================================================
# Experiment 2: Doping Effects
# B/N/P substitutional doping formation energy and stability
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/setup_hpc_env.sh"

EXP_DIR="$(dirname "$SCRIPT_DIR")/experiments/exp_2_doping"
LOG_FILE="$(dirname "$SCRIPT_DIR")/logs/exp2_doping_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "$(dirname "$LOG_FILE")"

echo "============================================="
echo "Experiment 2: Doping Effects"
echo "Start: $(date)"
echo "Log: $LOG_FILE"
echo "============================================="

cd "$EXP_DIR"
python run_doping_experiment.py 2>&1 | tee "$LOG_FILE"

echo "Completed at $(date)"

