#!/usr/bin/env bash
# Regenerate inputs after protocol fix, verify, rerun seed137 + population (+ rigid_pbed3 if flagged).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export RERUN_PROTOCOL_FIX=1
export CP2K_DATA="${CP2K_DATA:-/opt/homebrew/share/cp2k/data}"

echo "=== Regenerate inputs ==="
python3 "$ROOT/experiments/exp_5_synergy/seed_validation/generate_seed137_inputs.py"
python3 "$ROOT/experiments/exp_5_synergy/relax_validation/generate_relax_inputs.py"
python3 "$ROOT/experiments/exp_5_synergy/relax_validation/rigid_pbed3/generate_rigid_pbed3_inputs.py"
python3 "$ROOT/experiments/exp_7_electronic_structure/population_validation/generate_population_inputs.py"
python3 "$ROOT/experiments/exp_9_charged_polaron/generate_vertical_sp.py" 2>/dev/null || true

echo "=== Verify protocol ==="
python3 "$ROOT/experiments/verify_dft_protocol.py"

if pgrep -f 'cp2k\.psmp' >/dev/null 2>&1; then
  echo "CP2K already running; inputs fixed. Run when idle:" >&2
  echo "  RERUN_PROTOCOL_FIX=1 bash experiments/exp_5_synergy/seed_validation/run_seed137_validation.sh" >&2
  exit 0
fi

echo "=== Rerun seed137 (Table IV) ==="
bash "$ROOT/experiments/exp_5_synergy/seed_validation/run_seed137_validation.sh"

echo "=== Rerun rigid_pbed3 (matched functional) ==="
bash "$ROOT/experiments/exp_5_synergy/relax_validation/rigid_pbed3/run_rigid_pbed3_validation.sh"

echo "=== Rerun population n=1 P ==="
bash "$ROOT/experiments/exp_7_electronic_structure/population_validation/run_population_validation.sh"

echo "Protocol fix rerun complete."
