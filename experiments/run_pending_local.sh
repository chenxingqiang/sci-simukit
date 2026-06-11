#!/bin/bash
# Run unfinished CP2K tasks locally (sequential, memory-safe).
# Prefer C runner when built: c/build/simukit-run [--exp8-sp] experiments/exp_10_size_scaling/inputs
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CP2K="/opt/homebrew/bin/cp2k.psmp"
export CP2K_DATA="/opt/homebrew/share/cp2k/data"
LOG="$ROOT/experiments/local_run.log"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "$LOG"; }

is_done() {
    local out="$1"
    [[ -f "$out" ]] && grep -q 'SCF run converged' "$out" 2>/dev/null
}

run_cp2k() {
    local inp="$1"
    local out="$2"
    local np="$3"
    local dir
    dir="$(dirname "$inp")"
    local base
    base="$(basename "$inp" .inp)"

    if is_done "$out"; then
        log "SKIP (done): $base"
        return 0
    fi

    log "START: $base (np=$np)"
    cd "$dir"
    mpirun -np "$np" "$CP2K" -i "$(basename "$inp")" -o "$(basename "$out")" >> "$LOG" 2>&1

    if is_done "$out"; then
        log "DONE: $base"
        mkdir -p "$ROOT/dft_results_download/exp_10_size_scaling"
        mkdir -p "$ROOT/dft_results_download/exp_8_geometry_opt"
        if [[ "$dir" == *exp_10* ]]; then
            cp -f "$(basename "$out")" "$ROOT/dft_results_download/exp_10_size_scaling/"
        elif [[ "$dir" == *exp_8* ]]; then
            cp -f "$(basename "$out")" "$ROOT/dft_results_download/exp_8_geometry_opt/"
        fi
        return 0
    fi

    log "FAIL: $base (no SCF convergence)"
    return 1
}

np_for() {
    case "$1" in
        size_1x60_*|size_2x60_*) echo 4 ;;
        size_4x60_*) echo 6 ;;
        size_6x60_*) echo 8 ;;
        size_8x60_*) echo 10 ;;
        *) echo 4 ;;
    esac
}

log "========== Local CP2K batch start =========="
log "CP2K: $("$CP2K" --version 2>&1 | head -1)"

EXP10="$ROOT/experiments/exp_10_size_scaling/inputs"
PENDING_EXP10=(
    size_2x60_pristine_pos0pct
    size_2x60_pristine_pos3pct
    size_4x60_P_pos3pct
    size_6x60_B_pos3pct
    size_6x60_N_pos3pct
    size_8x60_B_pos0pct
    size_8x60_B_pos3pct
    size_8x60_N_pos3pct
    size_8x60_P_pos0pct
    size_8x60_P_pos3pct
    size_8x60_pristine_pos0pct
    size_8x60_pristine_pos3pct
)

for base in "${PENDING_EXP10[@]}"; do
    np="$(np_for "$base")"
    run_cp2k "$EXP10/${base}.inp" "$EXP10/${base}.out" "$np" || true
done

EXP8="$ROOT/experiments/exp_8_geometry_opt/inputs"
if ! is_done "$EXP8/geoopt_pristine_sp.out"; then
    if [[ ! -f "$EXP8/geoopt_pristine_sp.inp" ]]; then
        sed -e 's/{project_name}/geoopt_pristine_sp/' \
            -e 's/{optimized_xyz}/geoopt_pristine_optimized.xyz/' \
            -e 's/EPS_SCF 1.0E-7/EPS_SCF 1.0E-6/' \
            "$EXP8/single_point_template.inp" > "$EXP8/geoopt_pristine_sp.inp"
    fi
    run_cp2k "$EXP8/geoopt_pristine_sp.inp" "$EXP8/geoopt_pristine_sp.out" 4 || true
fi

done_count=$(grep -l 'SCF run converged' "$EXP10"/size_*.out 2>/dev/null | wc -l | tr -d ' ')
log "========== Batch finished: Exp10 $done_count/40 converged =========="
