#!/bin/bash
# =============================================================================
# Experiment 6: Optimal Conditions
# Best strain-doping combinations for maximum mobility
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/setup_hpc_env.sh"

EXP_DIR="$(dirname "$SCRIPT_DIR")/experiments/exp_6_optimal"
LOG_FILE="$(dirname "$SCRIPT_DIR")/logs/exp6_optimal_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "$(dirname "$LOG_FILE")"

echo "============================================="
echo "Experiment 6: Optimal Conditions"
echo "Start: $(date)"
echo "Log: $LOG_FILE"
echo "============================================="

cd "$EXP_DIR"
python run_optimal_experiment.py 2>&1 | tee "$LOG_FILE"

echo "Completed at $(date)"

