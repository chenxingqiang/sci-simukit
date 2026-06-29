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
if pgrep -f 'cp2k\.psmp.*pop_n1_P' >/dev/null 2>&1; then
  running="$(ps aux | grep -E 'cp2k\.psmp.*pop_n1_P' | grep -v grep | awk '{for(i=1;i<=NF;i++) if($i=="-i") print $(i+1)}' | head -1 | xargs basename 2>/dev/null | sed 's/\.inp$//' || echo pop_n1_P*)"
fi

status="pending"
if [[ -f "$JSON" ]]; then
  status="$(python3 -c "import json; print(json.load(open('$JSON')).get('status','pending'))" 2>/dev/null || echo pending)"
fi

echo "Population n=1 P ${done}/${total} | status=${status} | running=${running}"
