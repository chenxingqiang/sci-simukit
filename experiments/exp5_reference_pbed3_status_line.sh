#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIR="$ROOT/experiments/exp_5_synergy/reference_pbed3/inputs"
JSON="$ROOT/experiments/analysis/reference_placement_pbed3.json"

done=0
total=0
for inp in "$DIR"/C60_strain_*_refpbed3.inp; do
  [[ -f "$inp" ]] || continue
  total=$((total + 1))
  out="${inp%.inp}.out"
  if [[ -f "$out" ]] && grep -q 'SCF run converged' "$out"; then
    done=$((done + 1))
  fi
done

running=none
if pgrep -f 'cp2k\.psmp.*refpbed3' >/dev/null 2>&1; then
  running="$(ps aux | grep -E 'cp2k\.psmp.*refpbed3' | grep -v grep | awk '{for(i=1;i<=NF;i++) if($i=="-i") print $(i+1)}' | head -1 | xargs basename 2>/dev/null | sed 's/\.inp$//' || echo refpbed3*)"
fi

status=pending
if [[ -f "$JSON" ]]; then
  status="$(python3 -c "import json; print(json.load(open('$JSON')).get('status','pending'))" 2>/dev/null || echo pending)"
fi

line="ReferencePBE+D3 ${done}/${total} | status=${status} | running=${running}"

if [[ "$running" != none ]]; then
  snap="$(python3 - "$DIR/${running}.out" <<'PY'
import re, sys
from pathlib import Path
p = Path(sys.argv[1])
if not p.exists():
    sys.exit(0)
text = p.read_text(errors="replace")
# Last inner OT block after final PROGRAM STARTED
starts = [m.start() for m in re.finditer(r"PROGRAM STARTED", text)]
chunk = text[starts[-1]:] if starts else text
ots = [ln for ln in chunk.splitlines() if re.match(r"\s+\d+ OT ", ln)]
if not ots:
    sys.exit(0)
parts = ots[-1].split()
step, grad = parts[0], parts[5] if len(parts) > 5 else "?"
eps = 1.0e-6
try:
    g = float(grad)
    ratio = g / eps
    crit = " CRIT" if ratio <= 15 else ""
    print(f"OT~{step}/300 grad~{grad}{crit}")
except ValueError:
    print(f"OT~{step} grad~{grad}")
PY
)"
  [[ -n "$snap" ]] && line="$line | $snap"
fi

echo "$line"
