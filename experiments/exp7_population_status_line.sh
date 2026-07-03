#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INP="$ROOT/experiments/exp_7_electronic_structure/population_validation/inputs"
JSON="$ROOT/experiments/analysis/population_P_n1_strain.json"

total=0
done=0
for inp in "$INP"/pop_n1_P_*.inp; do
  [[ -f "$inp" ]] || continue
  total=$((total + 1))
  out="${inp%.inp}.out"
  if [[ -f "$out" ]] && grep -q 'SCF run converged' "$out"; then
    done=$((done + 1))
  fi
done

running="none"
running_out=""
if pgrep -f 'cp2k\.psmp.*pop_n1_P' >/dev/null 2>&1; then
  running="$(ps aux | grep -E 'cp2k\.psmp.*pop_n1_P' | grep -v grep | awk '{for(i=1;i<=NF;i++) if($i=="-i") print $(i+1)}' | head -1 | xargs basename 2>/dev/null | sed 's/\.inp$//' || echo pop_n1_P*)"
  running_out="$INP/${running}.out"
fi

status="pending"
if [[ -f "$JSON" ]]; then
  status="$(python3 -c "import json; print(json.load(open('$JSON')).get('status','pending'))" 2>/dev/null || echo pending)"
fi

extra=""
crit=""
if [[ "$running" != none && -f "$running_out" ]]; then
  read -r ot grad <<< "$(python3 -c "
import re
from pathlib import Path
raw = Path('$running_out').read_text(errors='replace')
if 'PROGRAM STARTED' in raw:
    raw = raw.split('PROGRAM STARTED')[-1]
t = raw[-80000:]
ots = re.findall(r'^\s+(\d+)\s+OT\s', t, re.M)
grs = re.findall(r'OT\s+(?:SD|DIIS|CG|BROYDEN)\s+[\d.E+-]+\s+[\d.E+-]+\s+([\d.E+-]+)', t)
print(ots[-1] if ots else '', f'grad={grs[-1]}' if grs else '')
" 2>/dev/null || echo ' ')"
  if [[ -n "$ot" && -n "$grad" ]]; then
    crit="$(python3 -c "
import re
g=float(re.sub(r'grad=','','$grad'))
eps=1e-6
from pathlib import Path
inp=Path('$INP/${running}.inp')
if inp.exists():
    m=re.search(r'EPS_SCF\s+([\d.E+-]+)', inp.read_text())
    if m: eps=float(m.group(1))
print('CRIT' if g/eps<=15 else '')
" 2>/dev/null || true)"
    extra=" | OT=${ot} grad=${grad#grad=}${crit:+ $crit}"
  fi
fi

echo "Population n=1 P ${done}/${total} | status=${status} | running=${running}${extra}"
