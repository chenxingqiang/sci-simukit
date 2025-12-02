#!/bin/bash
# =============================================================================
# Experiment 3: Electronic Properties
# Band gap, electronic coupling, and mobility calculations
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/setup_hpc_env.sh"

EXP_DIR="$(dirname "$SCRIPT_DIR")/experiments/exp_3_electronic"
LOG_FILE="$(dirname "$SCRIPT_DIR")/logs/exp3_electronic_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "$(dirname "$LOG_FILE")"

echo "============================================="
echo "Experiment 3: Electronic Properties"
echo "Start: $(date)"
echo "Log: $LOG_FILE"
echo "============================================="

cd "$EXP_DIR"
python run_electronic_experiment.py 2>&1 | tee "$LOG_FILE"

echo "Completed at $(date)"

