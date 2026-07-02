#!/usr/bin/env bash
# Set EPS_SCF=1e-5 on one seed137 rigid inp after repeated SCF ABORT (single task only).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TASK="${1:?usage: relax_seed137_eps.sh seed137_B_strainm2.5_rigid}"
INP="$ROOT/experiments/exp_5_synergy/seed_validation/inputs/${TASK}.inp"
[[ -f "$INP" ]] || { echo "missing $INP" >&2; exit 1; }
python3 -c "
import re, sys
from pathlib import Path
p = Path(sys.argv[1])
t = p.read_text()
t2 = re.sub(r'EPS_SCF\s+[\d.E+-]+', 'EPS_SCF 1.0E-5', t)
p.write_text(t2)
print('patched', p.name, '-> EPS_SCF 1.0E-5')
" "$INP"
