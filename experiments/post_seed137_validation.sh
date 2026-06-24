#!/bin/bash
# Refresh Table IV seed-137 audit JSON after ENERGY tasks converge.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JSON="$ROOT/experiments/analysis/seed_validation_tetramer.json"

python3 "$ROOT/experiments/exp_5_synergy/seed_validation/analyze_seed137.py" > /dev/null
bash "$ROOT/experiments/exp5_seed137_status_line.sh"

python3 -c "
import json
from pathlib import Path
d = json.loads(Path('$JSON').read_text())
st = d.get('status', 'pending')
print(f'TableIV audit: status={st}')
if st == 'complete':
    for dop in ('B', 'N', 'P'):
        a = d.get('tetramer_alpha_meV_per_pct', {}).get('seed137', {}).get(dop)
        s = d.get('tetramer_S_meV_per_atom_at_eps3', {}).get('seed137', {}).get(dop)
        print(f'  {dop}: alpha137={a} meV/%  S137@+3%={s} meV/atom')
    print('Next: fill paper/tables/tab_IV.tex alternate column from seed_validation_tetramer.json')
"
