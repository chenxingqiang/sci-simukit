#!/bin/bash
# =============================================================================
# Experiment 4: Polaron Transition
# Polaron binding energy and charge localization
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/setup_hpc_env.sh"

EXP_DIR="$(dirname "$SCRIPT_DIR")/experiments/exp_4_polaron"
LOG_FILE="$(dirname "$SCRIPT_DIR")/logs/exp4_polaron_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "$(dirname "$LOG_FILE")"

echo "============================================="
echo "Experiment 4: Polaron Transition"
echo "Start: $(date)"
echo "Log: $LOG_FILE"
echo "============================================="

cd "$EXP_DIR"
python run_polaron_experiment.py 2>&1 | tee "$LOG_FILE"

echo "Completed at $(date)"

