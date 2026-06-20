#!/bin/bash
# One-line Exp9 charged-polaron snapshot (GEO_OPT + vertical SP).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/dft_results/exp_9_charged_polaron/outputs"
JSON="$ROOT/experiments/analysis/exp9_polaron_verification.json"

geo_done=0
geo_total=12
if [[ -f "$JSON" ]]; then
  geo_done="$(python3 -c "import json; d=json.load(open('$JSON')); print(d.get('converged',0))")"
  geo_total="$(python3 -c "import json; d=json.load(open('$JSON')); print(d.get('total',12))")"
fi

running="none"
if pgrep -f 'cp2k\.psmp.*polaron_' >/dev/null 2>&1; then
  running="$(ps aux | grep -E 'cp2k\.psmp.*polaron_' | grep -v grep | awk '{for(i=1;i<=NF;i++) if($i=="-i") print $(i+1)}' | head -1 | xargs basename 2>/dev/null || echo polaron_*)"
fi

vert_done=0
vert_total=8
if [[ -d "$OUT" ]]; then
  vert_done="$(grep -l 'SCF run converged' "$OUT"/polaron_*_vert_*.out 2>/dev/null | wc -l | tr -d ' ' || true)"
fi


geo_num=""
geo_max="300"
ot_step=""
grad_hint=""
abort_hint=""
# Live .out first (post-ABORT segment); JSON fallback when idle.
if [[ "$running" != none && "$running" == *"_opt"* ]]; then
  base="${running%.inp}"
  out="$OUT/${base}.out"
  if [[ -f "$out" ]]; then
    read -r geo_num geo_max ot_step grad_hint abort_hint <<< "$(python3 -c "
import sys
sys.path.insert(0, '$ROOT/experiments/analysis')
from analyze_exp9_polaron import parse_geo_progress, read_out_tail
from pathlib import Path
snap = parse_geo_progress(read_out_tail(Path('$OUT') / ('${base}.out')))
gs = snap.get('geo_step')
mx = snap.get('geo_max_iter') or 300
ot = snap.get('last_ot_step')
gr = snap.get('last_ot_convergence')
ab = 'restarted-after-ABORT' if snap.get('restarted_after_abort') else ''
print(gs if gs is not None else '', mx, ot or '', f'conv={gr:.2e}' if gr else '', ab)
" 2>/dev/null || echo ' 300   ')"
  fi
elif [[ "$running" != none && "$running" == *"_vert"* ]]; then
  base="${running%.inp}"
  out="$OUT/${base}.out"
  if [[ -f "$out" ]]; then
    read -r ot_step grad_hint <<< "$(python3 -c "
import sys
sys.path.insert(0, '$ROOT/experiments/analysis')
from analyze_exp9_polaron import parse_scf_progress, read_out_tail
from pathlib import Path
snap = parse_scf_progress(read_out_tail(Path('$OUT') / ('${base}.out')))
ot = snap.get('last_ot_step')
gr = snap.get('last_ot_convergence')
print(ot or '', f'conv={gr:.2e}' if gr else '')
" 2>/dev/null || echo '  ')"
  fi
fi
if [[ -z "$geo_num" && "$running" == none && -f "$JSON" ]]; then
  read -r geo_num geo_max ot_step grad_hint abort_hint <<< "$(python3 -c "
import json
d=json.load(open('$JSON'))
s=d.get('running_snapshot') or {}
gs=s.get('geo_step')
mx=s.get('geo_max_iter') or 300
ot=s.get('last_ot_step')
gr=s.get('last_ot_convergence') or s.get('last_grad_ha_bohr')
ab='restarted-after-ABORT' if s.get('restarted_after_abort') else ''
print(gs if gs is not None else '', mx, ot or '', f'conv={gr:.2e}' if gr else '', ab)
" 2>/dev/null || echo ' 300   ')"
fi

next="none"
if [[ -f "$JSON" ]]; then
  next="$(python3 -c "
import json
d=json.load(open('$JSON'))
pending=d.get('pending_geo_opt') or []
if pending:
    print(pending[0])
else:
    vp=(d.get('vertical_sp') or {}).get('inputs_pending') or []
    print(vp[0] if vp else 'none')
")"
fi

if [[ "$running" != none && "$running" == *"_vert"* ]]; then
  extra=""
  [[ -n "$ot_step" ]] && extra=" OT=${ot_step}"
  [[ -n "$grad_hint" ]] && extra="${extra} ${grad_hint}"
  echo "Exp9 GEO_OPT ${geo_done}/${geo_total} | vertical SP ${vert_done}/${vert_total} | running=${running%.inp}${extra} | next=${next}"
elif [[ -n "$geo_num" ]]; then
  extra=""
  [[ -n "$ot_step" ]] && extra=" OT=${ot_step}"
  [[ -n "$grad_hint" ]] && extra="${extra} ${grad_hint}"
  [[ -n "$abort_hint" ]] && extra="${extra} ${abort_hint}"
  pct="$(python3 -c "g='$geo_num'; m='$geo_max'; print(round(100*float(g)/float(m),1) if g and m else '')" 2>/dev/null || true)"
  [[ -n "$pct" ]] && extra="${extra} pct=${pct}%"
  echo "Exp9 GEO_OPT ${geo_done}/${geo_total} | vertical SP ${vert_done}/${vert_total} | running=${running%.inp} step=${geo_num}/${geo_max}${extra} | next=${next}"
else
  echo "Exp9 GEO_OPT ${geo_done}/${geo_total} | vertical SP ${vert_done}/${vert_total} | running=${running} | next=${next}"
fi
