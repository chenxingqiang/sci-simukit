#!/usr/bin/env bash
# PRB major-revision DFT queue (sequential, ≤2/3 CPU via cp2k_resource.sh).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=cp2k_resource.sh
source "$ROOT/experiments/cp2k_resource.sh"

if pgrep -f 'cp2k\.psmp' >/dev/null 2>&1; then
  echo "CP2K already running; abort (single batch policy)." >&2
  exit 1
fi

relax_json="$ROOT/experiments/analysis/relax_validation_tetramer.json"
relax_done=0
if [[ -f "$relax_json" ]]; then
  relax_done="$(python3 -c "import json; d=json.load(open('$relax_json')); print(sum(1 for v in d.get('geo_opt_completed',{}).values() if v))")"
fi

if [[ "$relax_done" -ge 4 ]]; then
  echo "=== Table III relax: skip (4/4 complete) ==="
else
  echo "=== PRB revision DFT: ionic relaxation (Table III) ==="
  bash "$ROOT/experiments/exp_5_synergy/relax_validation/run_relax_validation.sh"
fi

echo "=== PRB revision DFT: seed137 tetramer grid (Table IV) ==="
bash "$ROOT/experiments/exp_5_synergy/seed_validation/run_seed137_validation.sh"

echo "=== PRB revision DFT: matched-functional rigid PBE+D3 (Table III quantitative) ==="
bash "$ROOT/experiments/exp_5_synergy/relax_validation/rigid_pbed3/run_rigid_pbed3_validation.sh"

echo "=== PRB revision DFT: periodic n=4 placement (seeds 137, 271) ==="
bash "$ROOT/experiments/exp_10_size_scaling/placement_validation/run_periodic_placement_validation.sh"

echo "=== PRB revision DFT: 6x60 N cutoff400 control (Table II) ==="
export CP2K_DATA="${CP2K_DATA:-/opt/homebrew/share/cp2k/data}"
if [[ -x "$ROOT/c/simukit-run" ]]; then
  "$ROOT/c/simukit-run" --one size_6x60_N_pos3pct_cutoff400 \
    "$ROOT/experiments/exp_10_size_scaling/inputs"
else
  INP="$ROOT/experiments/exp_10_size_scaling/inputs/size_6x60_N_pos3pct_cutoff400.inp"
  OUT="${INP%.inp}.out"
  NP="$(cp2k_cap_np 4)"
  (cd "$(dirname "$INP")" && /opt/homebrew/bin/mpirun -np "$NP" /opt/homebrew/bin/cp2k.psmp -i "$(basename "$INP")" -o "$(basename "$OUT")")
fi
bash "$ROOT/experiments/post_exp10_converged.sh"

echo "=== PRB revision DFT: n=1 P population strain path ==="
bash "$ROOT/experiments/exp_7_electronic_structure/population_validation/run_population_validation.sh"

echo "PRB revision DFT queue finished."
