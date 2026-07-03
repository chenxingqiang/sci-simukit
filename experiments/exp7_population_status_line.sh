#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INP="$ROOT/experiments/exp_7_electronic_structure/population_validation/inputs"

for dop in B N P; do
  total=0
  done=0
  for inp in "$INP"/pop_n1_${dop}_*.inp; do
    [[ -f "$inp" ]] || continue
    total=$((total + 1))
    out="${inp%.inp}.out"
    if [[ -f "$out" ]] && grep -q 'SCF run converged' "$out"; then
      done=$((done + 1))
    fi
  done
  JSON="$ROOT/experiments/analysis/population_${dop}_n1_strain.json"
  status="pending"
  if [[ -f "$JSON" ]]; then
    status="$(python3 -c "import json; print(json.load(open('$JSON')).get('status','pending'))" 2>/dev/null || echo pending)"
  fi
  running="none"
  if pgrep -f "cp2k\.psmp.*pop_n1_${dop}" >/dev/null 2>&1; then
    running="$(ps aux | grep -E "cp2k\.psmp.*pop_n1_${dop}" | grep -v grep | awk '{for(i=1;i<=NF;i++) if($i=="-i") print $(i+1)}' | head -1 | xargs basename 2>/dev/null | sed 's/\.inp$//' || echo pop_n1_${dop}*)"
  fi
  echo "Population n=1 ${dop} ${done}/${total} | status=${status} | running=${running}"
done
