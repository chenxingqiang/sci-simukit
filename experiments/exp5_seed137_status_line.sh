#!/bin/bash
# One-line Table IV seed-137 alternate-placement snapshot (18 B/N/P ENERGY + 6 pristine).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INP="$ROOT/experiments/exp_5_synergy/seed_validation/inputs"
JSON="$ROOT/experiments/analysis/seed_validation_tetramer.json"

python3 "$ROOT/experiments/exp_5_synergy/seed_validation/analyze_seed137.py" >/dev/null 2>&1 || true
dop_tasks=0
dop_done=0
for inp in "$INP"/seed137_{B,N,P}_*_rigid.inp; do
  [[ -f "$inp" ]] || continue
  dop_tasks=$((dop_tasks + 1))
  out="${inp%.inp}.out"
  if [[ -f "$out" ]] && grep -q 'SCF run converged' "$out"; then
    dop_done=$((dop_done + 1))
  fi
done

pri_done=0
pri_total=0
for strain in m5.0 m2.5 p0.0 p2.5 p3.0 p5.0; do
  pri_total=$((pri_total + 1))
  out="$INP/seed137_pristine_strain${strain}_rigid.out"
  if [[ -f "$out" ]] && grep -q 'SCF run converged' "$out"; then
    pri_done=$((pri_done + 1))
  fi
done

running="none"
next_task="none"
if pgrep -f 'cp2k\.psmp.*seed137_' >/dev/null 2>&1; then
  running="$(ps aux | grep -E 'cp2k\.psmp.*seed137_' | grep -v grep | awk '{for(i=1;i<=NF;i++) if($i=="-i") print $(i+1)}' | head -1 | xargs basename 2>/dev/null | sed 's/\.inp$//' || echo seed137_*)"
fi

for inp in "$INP"/seed137_*_rigid.inp; do
  [[ -f "$inp" ]] || continue
  base="$(basename "$inp" .inp)"
  out="$INP/${base}.out"
  if [[ ! -f "$out" ]] || ! grep -q 'SCF run converged' "$out"; then
    if [[ "$next_task" == none ]]; then
      next_task="$base"
    fi
  fi
done

ot=""
grad=""
if [[ "$running" != none && -f "$INP/${running}.out" ]]; then
  read -r ot grad <<< "$(python3 -c "
import re
from pathlib import Path
t = Path('$INP/${running}.out').read_text(errors='replace')[-80000:]
ots = re.findall(r'^\s+(\d+)\s+OT\s', t, re.M)
grs = re.findall(r'OT\s+DIIS\s+[\d.E+-]+\s+[\d.E+-]+\s+([\d.E+-]+)', t)
print(ots[-1] if ots else '', f'grad={grs[-1]}' if grs else '')
" 2>/dev/null || echo ' ')"
fi

extra=""
[[ -n "$ot" ]] && extra=" OT=${ot}"
[[ -n "$grad" ]] && extra="${extra} ${grad}"

status="pending"
provisional=""
if [[ -f "$JSON" ]]; then
  read -r status provisional <<< "$(python3 -c "
import json
d=json.load(open('$JSON'))
st=d.get('status','pending')
prov=any(d.get('alpha_provisional',{}).values())
print(st, 'provisional-alpha' if prov else '')
" 2>/dev/null || echo 'pending ')"
fi

echo "TableIV seed137 dop ${dop_done}/${dop_tasks} pri ${pri_done}/${pri_total} | status=${status} | running=${running} | next=${next_task}${extra}${provisional:+ | ${provisional}}"
