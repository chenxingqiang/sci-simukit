#!/bin/bash
# Local CP2K resource policy: use a fraction of logical CPUs (default 2/3).
# Source before simukit-run / run_pending_local.sh. Override:
#   SIMUKIT_CPU_FRACTION=0.5  SIMUKIT_MAX_CORES=6

export SIMUKIT_CPU_FRACTION="${SIMUKIT_CPU_FRACTION:-0.67}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export OMP_STACKSIZE="${OMP_STACKSIZE:-512M}"

_ncpu="$(sysctl -n hw.logicalcpu 2>/dev/null || echo 4)"
export SIMUKIT_MAX_CORES="${SIMUKIT_MAX_CORES:-$(
  python3 -c "import os; n=int('${_ncpu}'); f=float(os.environ.get('SIMUKIT_CPU_FRACTION','0.67')); print(max(1,int(n*f)))"
)}"

cp2k_cap_np() {
  local suggested="$1"
  local cap="${SIMUKIT_MAX_CORES}"
  if (( suggested > cap )); then
    echo "$cap"
  else
    echo "$suggested"
  fi
}
