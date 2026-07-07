#!/usr/bin/env bash
# Set EPS_SCF=1e-5 on one reference_pbed3 inp after SCF ABORT / outer-SCF stall.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TASK="${1:?usage: relax_reference_pbed3_eps.sh C60_strain_+2.5_B_doped_refpbed3}"
INP="$ROOT/experiments/exp_5_synergy/reference_pbed3/inputs/${TASK}.inp"
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
