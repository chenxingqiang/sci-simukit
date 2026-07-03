#!/usr/bin/env bash
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIR="$ROOT/experiments/exp_10_size_scaling/periodic_relax_validation/inputs"
JSON="$ROOT/experiments/analysis/periodic_relax_validation_n1_P.json"
done=0
for stem in per_relax_n1_pristine_eps0_geo per_relax_n1_pristine_eps3_geo \
            per_relax_n1_P_eps0_geo per_relax_n1_P_eps3_geo; do
  if grep -q 'GEOMETRY OPTIMIZATION COMPLETED' "$DIR/${stem}.out" 2>/dev/null; then
    done=$((done + 1))
  fi
done
running=none
if pgrep -f 'cp2k\.psmp.*per_relax_n1' >/dev/null 2>&1; then
  running="$(ps aux | grep -E 'cp2k\.psmp.*per_relax_n1' | grep -v grep | awk '{for(i=1;i<=NF;i++) if($i=="-i") print $(i+1)}' | head -1 | xargs basename 2>/dev/null | sed 's/\.inp$//' || echo per_relax_n1*)"
fi
echo "PeriodicRelax n=1 P ${done}/4 | running=${running}"
if [[ -f "$JSON" ]]; then
  python3 -c "import json; d=json.load(open('$JSON')); print('S_rigid', d.get('S_rigid',{}).get('S_meV_per_atom'), 'meV/atom | S_relaxed', d.get('S_relaxed',{}).get('S_meV_per_atom'), 'meV/atom')" 2>/dev/null || true
fi
