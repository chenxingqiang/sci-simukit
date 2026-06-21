#!/bin/bash
# One-line Table S3 ionic-relaxation snapshot (four fixed-cell GEO_OPT corners).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INP="$ROOT/experiments/exp_5_synergy/relax_validation/inputs"
JSON="$ROOT/experiments/analysis/relax_validation_tetramer.json"

TASKS=(relax_pristine_eps0_geo relax_pristine_eps3_geo relax_P_eps0_geo relax_P_eps3_geo)
done=0
total=${#TASKS[@]}
running="none"
next_task="none"

for t in "${TASKS[@]}"; do
  out="$INP/${t}.out"
  if [[ -f "$out" ]] && grep -q 'GEOMETRY OPTIMIZATION COMPLETED' "$out"; then
    done=$((done + 1))
  elif [[ "$next_task" == none ]]; then
    next_task="$t"
  fi
done

if pgrep -f 'cp2k\.psmp.*relax_' >/dev/null 2>&1; then
  running="$(ps aux | grep -E 'cp2k\.psmp.*relax_' | grep -v grep | awk '{for(i=1;i<=NF;i++) if($i=="-i") print $(i+1)}' | head -1 | xargs basename 2>/dev/null | sed 's/\.inp$//' || echo relax_*)"
fi

ot=""
grad=""
if [[ "$running" != none && -f "$INP/${running}.out" ]]; then
  read -r ot grad <<< "$(python3 -c "
import re
from pathlib import Path
t = Path('$INP/${running}.out').read_text(errors='replace')[-120000:]
ots = re.findall(r'^\s+(\d+)\s+OT\s', t, re.M)
grs = re.findall(r'OT\s+DIIS\s+[\d.E+-]+\s+[\d.E+-]+\s+([\d.E+-]+)', t)
print(ots[-1] if ots else '', f'grad={grs[-1]}' if grs else '')
" 2>/dev/null || echo ' ')"
fi

s_rigid=""
if [[ -f "$JSON" ]]; then
  s_rigid="$(python3 -c "
import json
d=json.load(open('$JSON'))
sr=d.get('S_rigid',{}).get('S_meV_per_atom')
print(f'S_rigid={sr:.2f} meV/atom' if sr is not None else '')
" 2>/dev/null || true)"
fi

extra=""
crit=""
[[ -n "$ot" ]] && extra=" OT=${ot}"
[[ -n "$grad" ]] && extra="${extra} ${grad}"
[[ -n "$s_rigid" ]] && extra="${extra} | ${s_rigid}"
if [[ -n "$grad" ]]; then
  g="${grad#grad=}"
  if python3 -c "import sys; sys.exit(0 if float('$g') <= 1.5e-5 else 1)" 2>/dev/null; then
    crit=" CRIT"
  fi
fi

echo "TableS3 relax ${done}/${total} | running=${running}${crit} | next=${next_task}${extra}"
