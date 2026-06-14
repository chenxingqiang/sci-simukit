#!/bin/bash
# After Exp10 task(s) converge: archive, refresh audits/SDC, resume pending batch.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN="$ROOT/c/simukit-run"
INPUTS="$ROOT/experiments/exp_10_size_scaling/inputs"

if pgrep -f 'cp2k\.psmp.*size_' >/dev/null 2>&1; then
  echo "CP2K still running; wait for convergence before continuing batch." >&2
  exit 1
fi

bash "$ROOT/experiments/post_exp10_converged.sh"

if [[ ! -x "$RUN" ]]; then
  echo "Build simukit-run: cd c && make" >&2
  exit 1
fi

export CP2K_DATA="${CP2K_DATA:-/opt/homebrew/share/cp2k/data}"
# shellcheck source=cp2k_resource.sh
source "$ROOT/experiments/cp2k_resource.sh"
echo "CP2K resources: ${SIMUKIT_MAX_CORES}/${_ncpu} cores (${SIMUKIT_CPU_FRACTION} fraction), OMP_NUM_THREADS=${OMP_NUM_THREADS}" >&2
exec "$RUN" "$INPUTS"
