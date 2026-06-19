#!/usr/bin/env bash
# PRB major-revision DFT queue: relax (4 GEO_OPT) -> seed137 (18 ENERGY) -> cutoff400 SP.
# Run only when Exp9 batch is idle (single CP2K path on Mac).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if pgrep -f 'cp2k\.psmp' >/dev/null 2>&1; then
  echo "CP2K already running; abort (wait for Exp9 batch to finish)." >&2
  exit 1
fi

echo "=== PRB revision DFT: ionic relaxation (Table S3) ==="
bash "$ROOT/experiments/exp_5_synergy/relax_validation/run_relax_validation.sh"

echo "=== PRB revision DFT: seed137 full grid (Table S4) ==="
bash "$ROOT/experiments/exp_5_synergy/seed_validation/run_seed137_validation.sh"

echo "=== PRB revision DFT: 6x60 N cutoff400 control (Table S2) ==="
export CP2K_DATA="${CP2K_DATA:-/opt/homebrew/share/cp2k/data}"
if [[ -x "$ROOT/c/simukit-run" ]]; then
  "$ROOT/c/simukit-run" --one size_6x60_N_pos3pct_cutoff400 \
    "$ROOT/experiments/exp_10_size_scaling/inputs"
else
  INP="$ROOT/experiments/exp_10_size_scaling/inputs/size_6x60_N_pos3pct_cutoff400.inp"
  OUT="${INP%.inp}.out"
  (cd "$(dirname "$INP")" && mpirun -np 4 /opt/homebrew/bin/cp2k.psmp -i "$(basename "$INP")" -o "$(basename "$OUT")")
fi
bash "$ROOT/experiments/post_exp10_converged.sh"

echo "PRB revision DFT queue finished."
