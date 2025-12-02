#!/bin/bash
# =============================================================================
# Master script to run all DFT experiments on HPC server
# Uses 32 CPUs with MPI parallelization
# =============================================================================

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
EXPERIMENTS_DIR="$PROJECT_ROOT/experiments"
LOG_DIR="$PROJECT_ROOT/logs"
NPROCS=${NPROCS:-32}

# Create log directory
mkdir -p "$LOG_DIR"

# Setup CP2K environment
setup_cp2k_env() {
    echo "Setting up CP2K environment..."
    
    # Source toolchain if available
    if [ -f "/opt/cp2k/tools/toolchain/install/setup" ]; then
        source /opt/cp2k/tools/toolchain/install/setup
    fi
    
    # Set CP2K paths
    export CP2K_DATA_DIR="${CP2K_DATA_DIR:-/opt/cp2k/data}"
    export PATH="/opt/cp2k/exe/local:$PATH"
    
    # MPI settings for full CPU utilization
    export OMP_NUM_THREADS=1
    export OMP_STACKSIZE=512M
    
    echo "CP2K environment configured"
    echo "  NPROCS: $NPROCS"
    echo "  CP2K_DATA_DIR: $CP2K_DATA_DIR"
}

# Run a single experiment
run_experiment() {
    local exp_name=$1
    local exp_dir="$EXPERIMENTS_DIR/$exp_name"
    local log_file="$LOG_DIR/${exp_name}.log"
    
    if [ ! -d "$exp_dir" ]; then
        echo "Warning: $exp_dir not found, skipping"
        return 1
    fi
    
    echo "=========================================="
    echo "Running $exp_name"
    echo "Start time: $(date)"
    echo "=========================================="
    
    cd "$exp_dir"
    
    # Find the main run script
    local run_script=$(ls run_*_experiment.py 2>/dev/null | head -1)
    
    if [ -z "$run_script" ]; then
        echo "No run script found in $exp_dir"
        return 1
    fi
    
    # Run the experiment
    python "$run_script" 2>&1 | tee "$log_file"
    
    echo "Completed $exp_name at $(date)"
    echo ""
}

# Main execution
main() {
    echo "============================================="
    echo "DFT Experiment Suite - Full Run"
    echo "Start time: $(date)"
    echo "Using $NPROCS CPU cores"
    echo "============================================="
    echo ""
    
    # Setup environment
    setup_cp2k_env
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Run experiments in order
    local experiments=(
        "exp_1_structure"
        "exp_2_doping"
        "exp_3_electronic"
        "exp_4_polaron"
        "exp_5_synergy"
        "exp_6_optimal"
    )
    
    local start_time=$(date +%s)
    
    for exp in "${experiments[@]}"; do
        run_experiment "$exp" || echo "Warning: $exp had errors"
        echo ""
    done
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo "============================================="
    echo "All experiments completed"
    echo "Total time: $((duration / 3600))h $((duration % 3600 / 60))m $((duration % 60))s"
    echo "End time: $(date)"
    echo "============================================="
}

# Run main function
main "$@"

