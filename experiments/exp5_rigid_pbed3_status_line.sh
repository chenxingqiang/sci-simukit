#!/bin/bash
# One-line matched-functional rigid PBE+D3 snapshot (Table III quantitative benchmark).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INP="$ROOT/experiments/exp_5_synergy/relax_validation/rigid_pbed3/inputs"
JSON="$ROOT/experiments/analysis/relax_validation_matched_functional.json"
# shellcheck source=cp2k_resource.sh
source "$ROOT/experiments/cp2k_resource.sh"

TASKS=(
  rigid_pbed3_pristine_eps0_sp
  rigid_pbed3_pristine_eps3_sp
  rigid_pbed3_P_eps0_sp
  rigid_pbed3_P_eps3_sp
)

done=0
total=${#TASKS[@]}
next_task="none"
for task in "${TASKS[@]}"; do
  out="$INP/${task}.out"
  if [[ -f "$out" ]] && grep -q 'SCF run converged' "$out"; then
    done=$((done + 1))
  elif [[ "$next_task" == none ]]; then
    next_task="$task"
  fi
done

running="none"
if pgrep -f 'cp2k.psmp.*rigid_pbed3_' >/dev/null 2>&1; then
  running="$(ps aux | grep -E 'cp2k.psmp.*rigid_pbed3_' | grep -v grep | awk '{for(i=1;i<=NF;i++) if($i=="-i") print $(i+1)}' | head -1 | xargs basename 2>/dev/null | sed 's/.inp$//' || echo rigid_pbed3_*)"
fi

ot=""
grad=""
if [[ "$running" != none && -f "$INP/${running}.out" ]]; then
  read -r ot grad <<< "$(python3 -c "
import re
from pathlib import Path
raw = Path('$INP/${running}.out').read_text(errors='replace')
if 'PROGRAM STARTED' in raw:
    raw = raw.split('PROGRAM STARTED')[-1]
t = raw[-80000:]
ots = re.findall(r'^\s+(\d+)\s+OT\s', t, re.M)
grs = re.findall(r'OT\s+DIIS\s+[\d.E+-]+\s+[\d.E+-]+\s+([\d.E+-]+)', t)
print(ots[-1] if ots else '', f'grad={grs[-1]}' if grs else '')
" 2>/dev/null || echo ' ')"
fi

ratio="pending"
if [[ -f "$JSON" ]]; then
  ratio="$(python3 -c "import json; d=json.load(open('$JSON')); print('valid' if d.get('quantitative_ratio_valid') else 'pending')" 2>/dev/null || echo pending)"
fi

extra=""
[[ -n "$ot" ]] && extra=" OT=${ot}"
[[ -n "$grad" ]] && extra="${extra} ${grad}"

np_live=""
if [[ "$running" != none ]]; then
  np_live="$(ps aux | grep -E "prterun.*${running}" | grep -v grep | sed -n 's/.*-np \([0-9]*\).*/\1/p' | head -1)"
fi
cpu_note="cap=${SIMUKIT_MAX_CORES}"
[[ -n "$np_live" ]] && cpu_note="${cpu_note} np=${np_live}"

echo "TableIII rigid_pbed3 ${done}/${total} | ratio=${ratio} | running=${running} | next=${next_task}${extra} | ${cpu_note}"
