#!/bin/bash
# =============================================================================
# HPC Environment Setup Script
# Configure CP2K and MPI for 32-core ARM64 server
# =============================================================================

# CP2K installation paths
export CP2K_HOME="${CP2K_HOME:-/opt/cp2k}"
export CP2K_DATA_DIR="${CP2K_DATA_DIR:-$CP2K_HOME/data}"
export PATH="$CP2K_HOME/exe/local:$PATH"

# Source toolchain setup if available
if [ -f "$CP2K_HOME/tools/toolchain/install/setup" ]; then
    source "$CP2K_HOME/tools/toolchain/install/setup"
fi

# MPI Configuration for full CPU utilization
export NPROCS=${NPROCS:-32}
export OMP_NUM_THREADS=1
export OMP_STACKSIZE=512M

# Memory settings
export MALLOC_TRIM_THRESHOLD_=0

# Verify CP2K is available
if command -v cp2k.psmp &> /dev/null; then
    echo "CP2K environment loaded"
    echo "  Executable: $(which cp2k.psmp)"
    echo "  Data dir: $CP2K_DATA_DIR"
    echo "  MPI procs: $NPROCS"
elif command -v cp2k.ssmp &> /dev/null; then
    echo "CP2K environment loaded (serial version)"
    echo "  Executable: $(which cp2k.ssmp)"
    echo "  Data dir: $CP2K_DATA_DIR"
else
    echo "Warning: CP2K not found in PATH"
fi

