#!/bin/bash
# Refresh n=1 P population-strain audit JSON after ENERGY tasks converge.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JSON="$ROOT/experiments/analysis/population_P_n1_strain.json"

bash "$ROOT/experiments/guard_unlinked_cp2k_out.sh" || true
python3 "$ROOT/experiments/exp_7_electronic_structure/population_validation/analyze_population_strain.py" > /dev/null
bash "$ROOT/experiments/exp7_population_status_line.sh"

python3 -c "
import json
from pathlib import Path
d = json.loads(Path('$JSON').read_text())
st = d.get('status', 'pending')
n = sum(1 for p in d.get('strain_path', []) if p.get('converged'))
print(f'Population audit: status={st} ({n}/6 converged)')
for p in d.get('strain_path', []):
    if p.get('converged') and p.get('hirshfeld_charge_P') is not None:
        print(f\"  eps={p['strain_pct']:+.1f}%  q_P={p['hirshfeld_charge_P']}\")
if st == 'complete':
    print('Next: Discussion (iv) Hirshfeld mechanism; do not quote partial charges in main text until reviewed.')
"
