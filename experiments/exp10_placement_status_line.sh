#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JSON="$ROOT/experiments/analysis/periodic_placement_validation.json"
INP="$ROOT/experiments/exp_10_size_scaling/placement_validation/inputs"

python3 "$ROOT/experiments/exp_10_size_scaling/placement_validation/analyze_periodic_placement.py" >/dev/null 2>&1 || true

total=0
done=0
for inp in "$INP"/place_seed*.inp; do
  [[ -f "$inp" ]] || continue
  total=$((total + 1))
  out="${inp%.inp}.out"
  if [[ -f "$out" ]] && grep -q 'SCF run converged' "$out"; then
    done=$((done + 1))
  fi
done

running="none"
if pgrep -f 'cp2k\.psmp.*place_seed' >/dev/null 2>&1; then
  running="$(ps aux | grep -E 'cp2k\.psmp.*place_seed' | grep -v grep | awk '{for(i=1;i<=NF;i++) if($i=="-i") print $(i+1)}' | head -1 | xargs basename 2>/dev/null | sed 's/\.inp$//' || echo place_seed*)"
fi

status="pending"
if [[ -f "$JSON" ]]; then
  status="$(python3 -c "import json; print(json.load(open('$JSON')).get('status','pending'))" 2>/dev/null || echo pending)"
fi

extra=""
if [[ "$running" != none && -f "$INP/${running}.out" ]]; then
  read -r ot grad <<< "$(python3 -c "
import re
from pathlib import Path
raw = Path('$INP/${running}.out').read_text(errors='replace')
if 'PROGRAM STARTED' in raw:
    raw = raw.split('PROGRAM STARTED')[-1]
t = raw[-80000:]
ots = re.findall(r'^\s+(\d+)\s+OT\s', t, re.M)
grs = re.findall(r'OT\s+(?:DIIS|SD)\s+[\d.E+-]+\s+[\d.E+-]+\s+([\d.E+-]+)', t)
print(ots[-1] if ots else '', f'grad={grs[-1]}' if grs else '')
" 2>/dev/null || echo ' ')"
  [[ -n "$ot" ]] && extra=" OT=${ot}"
  [[ -n "$grad" ]] && extra="${extra} ${grad}"
  if [[ -n "$ot" ]] && [[ "$ot" -ge 250 ]]; then
    extra="${extra} CRIT(OT>=250)"
  fi
fi

echo "Periodic placement n=4 ${done}/${total} | status=${status} | running=${running}${extra}"
