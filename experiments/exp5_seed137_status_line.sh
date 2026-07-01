#!/bin/bash
# One-line Table IV seed-137 alternate-placement snapshot (18 B/N/P ENERGY + 6 pristine).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INP="$ROOT/experiments/exp_5_synergy/seed_validation/inputs"
JSON="$ROOT/experiments/analysis/seed_validation_tetramer.json"
# shellcheck source=cp2k_resource.sh
source "$ROOT/experiments/cp2k_resource.sh"

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
unlinked=""
next_task="none"
if pgrep -f 'cp2k\.psmp.*seed137_' >/dev/null 2>&1; then
  running="$(ps aux | grep -E 'cp2k\.psmp.*seed137_' | grep -v grep | awk '{for(i=1;i<=NF;i++) if($i=="-i") print $(i+1)}' | head -1 | xargs basename 2>/dev/null | sed 's/\.inp$//' || echo seed137_*)"
fi
if [[ "$running" != none ]] && lsof +L1 2>/dev/null | grep -q "cp2k.*${running}\.out"; then
  if lsof +L1 2>/dev/null | grep "cp2k.*${running}\.out" | grep -q ' 0 '; then
    unlinked="UNLINKED"
  fi
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
out_read="$INP/${running}.out"
[[ -f "${out_read}.mirror" ]] && out_read="${out_read}.mirror"
if [[ "$running" != none && -f "$out_read" ]]; then
  read -r ot grad <<< "$(python3 -c "
import re
from pathlib import Path
raw = Path('$out_read').read_text(errors='replace')
if 'PROGRAM STARTED' in raw:
    raw = raw.split('PROGRAM STARTED')[-1]
t = raw[-80000:]
ots = re.findall(r'^\s+(\d+)\s+OT\s', t, re.M)
grs = re.findall(r'OT\s+(?:SD|DIIS|CG|BROYDEN)\s+[\d.E+-]+\s+[\d.E+-]+\s+([\d.E+-]+)', t)
print(ots[-1] if ots else '', f'grad={grs[-1]}' if grs else '')
" 2>/dev/null || echo ' ')"
fi

crit=""
if [[ "$running" != none && -n "$grad" ]]; then
  crit="$(python3 -c "
import re
g=float(re.sub(r'grad=','','$grad'))
eps=1e-6
from pathlib import Path
inp=Path('$INP/${running}.inp')
if inp.exists():
    m=re.search(r'EPS_SCF\s+([\d.E+-]+)', inp.read_text())
    if m: eps=float(m.group(1))
r=g/eps
print('CRIT' if r<=15 else '')
" 2>/dev/null || true)"
fi
extra=""
ot_max=""
if [[ -f "$JSON" && -n "$ot" ]]; then
  ot_max="$(python3 -c "import json; s=json.load(open('$JSON')).get('running_snapshot',{}); print(s.get('max_inner_ot',''))" 2>/dev/null || true)"
fi
[[ -n "$ot" && -n "$ot_max" ]] && extra=" OT=${ot}/${ot_max}" || { [[ -n "$ot" ]] && extra=" OT=${ot}"; }
ratio_eps=""
if [[ -f "$JSON" ]]; then
  read -r ratio_eps crit_json <<< "$(python3 -c "
import json
s=json.load(open('$JSON')).get('running_snapshot',{})
r=s.get('grad_ratio_to_eps')
print(f'{r}x' if r is not None else '', 'CRIT' if s.get('critical_zone') else '')
" 2>/dev/null || echo ' ')"
  [[ -n "$crit_json" ]] && crit="$crit_json"
fi
if [[ -n "$grad" ]]; then
  if [[ -n "$ratio_eps" ]]; then
    extra="${extra} ${grad} (${ratio_eps} EPS)"
  else
    extra="${extra} ${grad}"
  fi
fi

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

np_live=""
if [[ "$running" != none ]]; then
  np_live="$(ps aux | grep -E "prterun.*${running}" | grep -v grep | sed -n 's/.*-np \([0-9]*\).*/\1/p' | head -1)"
fi
ot_warn=""
if [[ -n "$ot" && -n "$ot_max" ]]; then
  ot_warn="$(python3 -c "o=int('$ot'); m=int('$ot_max'); print('OT_WARN' if o>=m-10 else '')" 2>/dev/null || true)"
fi
cpu_note="cap=${SIMUKIT_MAX_CORES}"
[[ -n "$np_live" ]] && cpu_note="${cpu_note} np=${np_live}"

echo "TableIV seed137 dop ${dop_done}/${dop_tasks} pri ${pri_done}/${pri_total} | status=${status} | running=${running}${unlinked:+ | ${unlinked}} | next=${next_task}${extra} | ${cpu_note}${ot_warn:+ | ${ot_warn}}${crit:+ | ${crit}}${provisional:+ | ${provisional}}"
