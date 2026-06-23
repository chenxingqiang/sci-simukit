#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
INP_DIR="$ROOT/experiments/exp_5_synergy/relax_validation/inputs"
LOG="$ROOT/experiments/local_run.log"

export CP2K_DATA="${CP2K_DATA:-/opt/homebrew/share/cp2k/data}"
CP2K="${CP2K:-/opt/homebrew/bin/cp2k.psmp}"
NP="${NP:-4}"

TASKS=(
  relax_pristine_eps0_geo
  relax_pristine_eps3_geo
  relax_P_eps0_geo
  relax_P_eps3_geo
)

mkdir -p "$INP_DIR"
python3 "$ROOT/experiments/exp_5_synergy/relax_validation/generate_relax_inputs.py"

for task in "${TASKS[@]}"; do
  out="$INP_DIR/${task}.out"
  if [[ -f "$out" ]] && grep -q 'GEOMETRY OPTIMIZATION COMPLETED' "$out"; then
    echo "[skip] $task already converged"
    continue
  fi
  if [[ -f "$out" ]] && grep -q '\[ABORT\]' "$out"; then
    ts="$(date +%Y%m%d_%H%M%S)"
    cp "$out" "${out}.failed_${ts}"
    echo "[archive] $task ABORT -> ${out}.failed_${ts}"
    pos="$(ls -1 "$INP_DIR/${task}"-pos-*.xyz 2>/dev/null | tail -1 || true)"
    if [[ -n "$pos" && -f "$INP_DIR/${task}-RESTART.wfn" ]]; then
      python3 - "$task" "$pos" <<'PY'
import re, sys
from pathlib import Path
task, pos = sys.argv[1], Path(sys.argv[2])
inp = pos.parent / f"{task}.inp"
text = inp.read_text()
lines = pos.read_text().splitlines()
nat = int(lines[0].strip())
starts = [i for i, ln in enumerate(lines) if ln.strip().isdigit() and int(ln.strip()) == nat]
i = starts[-1] if starts else 0
rows = [ln.split() for ln in lines[i + 2 : i + 2 + nat]]
coord = "            &COORD\n" + "\n".join(
    f"      {p[0]}  {p[1]}  {p[2]}  {p[3]}" for p in rows
) + "\n    &END COORD"
text, n = re.subn(r"&COORD.*?&END COORD", coord, text, count=1, flags=re.S)
if n != 1:
    raise SystemExit("COORD patch failed")
text = re.sub(r"SCF_GUESS\s+\w+", "SCF_GUESS RESTART", text)
text = re.sub(r"\n\s*WFN_RESTART_FILE_NAME.*", "", text)
if "_P_" in task:
    text = re.sub(r"EPS_SCF\s+1\.0E-6", "EPS_SCF 1.0E-5", text)
    text = re.sub(r"(&OUTER_SCF\s*\n\s*)MAX_SCF\s+20", r"\1MAX_SCF 40", text)
    text = re.sub(r"(&OUTER_SCF[\s\S]*?)EPS_SCF\s+1\.0E-6", r"\1EPS_SCF 1.0E-5", text, count=1)
inp.write_text(text)
print(f"[patch] {inp.name} from {pos.name} ({nat} atoms)")
PY
    fi
  fi
  echo "[$(date -Iseconds)] START $task np=$NP" | tee -a "$LOG"
  (
    cd "$INP_DIR"
    mpirun -np "$NP" "$CP2K" -i "${task}.inp" -o "${task}.out"
  )
  if grep -q 'GEOMETRY OPTIMIZATION COMPLETED' "$out"; then
    echo "[$(date -Iseconds)] DONE $task" | tee -a "$LOG"
    python3 "$ROOT/experiments/exp_5_synergy/relax_validation/analyze_relax_s.py"
  else
    echo "[$(date -Iseconds)] FAIL $task (no GEO_OPT completion)" | tee -a "$LOG"
    exit 1
  fi
done

echo "All relax validation jobs finished."
python3 "$ROOT/experiments/exp_5_synergy/relax_validation/analyze_relax_s.py"
