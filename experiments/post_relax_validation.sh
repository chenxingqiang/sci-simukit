#!/bin/bash
# Refresh Table III audit JSON after a relax_validation GEO_OPT corner completes.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JSON="$ROOT/experiments/analysis/relax_validation_tetramer.json"

python3 "$ROOT/experiments/exp_5_synergy/relax_validation/analyze_relax_s.py" > /dev/null
bash "$ROOT/experiments/exp5_relax_status_line.sh"

python3 -c "
import json
from pathlib import Path
d = json.loads(Path('$JSON').read_text())
done = sum(1 for v in d.get('geo_opt_completed', {}).values() if v)
total = len(d.get('geo_opt_completed', {}))
print(f'TableIII audit: {done}/{total} GEO_OPT')
if done == total and 'S_relaxed' in d:
    sr = d['S_relaxed']['S_meV_per_atom']
    sp = d.get('sign_preserved')
    print(f'S_relaxed = {sr:.4f} meV/atom; sign_preserved vs rigid = {sp}')
    print('Next: fill paper/tables/tab_III.tex row 4 + S row from relax_validation_tetramer.json')
elif done < total:
    pending = [k for k, v in d.get('geo_opt_completed', {}).items() if not v]
    print(f'Pending corners: {pending}')
"
