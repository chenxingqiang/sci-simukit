#!/bin/bash
# =============================================================================
# Experiment 1: Structural Characterization
# qHP C60 network lattice parameters and strain response
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/setup_hpc_env.sh"

EXP_DIR="$(dirname "$SCRIPT_DIR")/experiments/exp_1_structure"
LOG_FILE="$(dirname "$SCRIPT_DIR")/logs/exp1_structure_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "$(dirname "$LOG_FILE")"

echo "============================================="
echo "Experiment 1: Structural Characterization"
echo "Start: $(date)"
echo "Log: $LOG_FILE"
echo "============================================="

cd "$EXP_DIR"
python run_structure_experiment.py 2>&1 | tee "$LOG_FILE"

echo "Completed at $(date)"

