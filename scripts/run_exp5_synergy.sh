#!/bin/bash
# =============================================================================
# Experiment 5: Synergistic Effects
# Strain-doping coupling and non-additive enhancements
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/setup_hpc_env.sh"

EXP_DIR="$(dirname "$SCRIPT_DIR")/experiments/exp_5_synergy"
LOG_FILE="$(dirname "$SCRIPT_DIR")/logs/exp5_synergy_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "$(dirname "$LOG_FILE")"

echo "============================================="
echo "Experiment 5: Synergistic Effects"
echo "Start: $(date)"
echo "Log: $LOG_FILE"
echo "============================================="

cd "$EXP_DIR"
python run_synergy_experiment.py 2>&1 | tee "$LOG_FILE"

echo "Completed at $(date)"

