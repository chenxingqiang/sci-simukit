#!/bin/bash
# Refresh matched-functional Table III JSON after rigid_pbed3 SP converges.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JSON="$ROOT/experiments/analysis/relax_validation_matched_functional.json"

python3 "$ROOT/experiments/exp_5_synergy/relax_validation/rigid_pbed3/analyze_rigid_pbed3.py" > /dev/null

python3 "$ROOT/experiments/update_tab_III_matched_from_json.py" || true

python3 -c "
import json
from pathlib import Path
p = Path('$JSON')
if not p.exists():
    print('matched functional JSON missing')
    raise SystemExit(1)
d = json.loads(p.read_text())
n = sum(1 for v in d.get('scf_converged', {}).values() if v)
print(f'TableIII matched PBE+D3 rigid: {n}/4 SCF')
if d.get('quantitative_ratio_valid'):
    sr = d['S_rigid_pbed3']['S_meV_per_atom']
    sl = json.loads(Path('$ROOT/experiments/analysis/relax_validation_tetramer.json').read_text())['S_relaxed']['S_meV_per_atom']
    rr = d.get('retention_ratio_abs')
    print(f'S_rigid_pbed3={sr:.2f} meV/atom; S_relaxed={sl:.2f}; |S_rel|/|S_rig|={rr}')
"
