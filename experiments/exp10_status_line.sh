#!/bin/bash
# One-line Exp10 status for agent loops (refresh + print).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/experiments/update_exp10_status.py" >/dev/null
python3 - "$ROOT" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
p = root / "experiments/analysis/exp10_status.json"
d = json.loads(p.read_text())
snap = d.get("running_snapshot") or {}
ref = snap.get("reference_ot_steps", "?")
pct = snap.get("ot_progress_pct", "?")
grad = snap.get("last_grad")
ratio = snap.get("grad_ratio_to_eps")
grad_s = f"{grad:.2e}" if isinstance(grad, (int, float)) else "?"
ratio_s = f"{ratio}x" if ratio is not None else "?"
next_task = d.get("next_after_running", "none")
eta = snap.get("eta_minutes_to_ref_ot")
eta_s = f"~{int(eta)}min" if isinstance(eta, (int, float)) else "?"
print(
    f"Exp10 {d['converged']}/{d['total']} | "
    f"running={d.get('running_task', 'none')} | "
    f"OT {snap.get('last_ot_step', '?')}/{ref} ({pct}%) | "
    f"grad={grad_s} ({ratio_s} EPS) | "
    f"next={next_task} | eta_ref={eta_s}"
)
PY
