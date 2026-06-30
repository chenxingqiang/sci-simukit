#!/usr/bin/env bash
# Remove stale CP2K artifacts (failed logs, backups, converged checkpoints).
# Safe while batch runs — skips .out files held open by lsof.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== cleanup_stale_cp2k ==="
find "$ROOT" -type f \( \
  -name '*.out.failed_*' -o \
  -name '*.out.failed_spin' -o \
  -name '*failed_partial*' -o \
  -name '*.restart.bak-*' -o \
  -name '*-RESTART.wfn.bak-*' -o \
  -name '*-BFGS.Hessian' -o \
  -name '.DS_Store' \
\) -print -delete 2>/dev/null || true

python3 << 'PY'
from pathlib import Path
import subprocess

REPO = Path(".")

def is_active(path: Path) -> bool:
    try:
        return subprocess.run(["lsof", str(path)], capture_output=True).returncode == 0
    except FileNotFoundError:
        return False

def converged_out(out: Path) -> bool:
    if not out.exists() or is_active(out):
        return False
    t = out.read_text(errors="ignore")
    return "SCF run converged" in t or "PROGRAM ENDED" in t

n = 0
for p in list(REPO.rglob("*-RESTART.wfn")) + list(REPO.rglob("*-1.restart")):
    if "bak" in p.name:
        continue
    stem = p.name.replace("-RESTART.wfn", "").replace("-1.restart", "")
    out = p.parent / f"{stem}.out"
    if converged_out(out):
        p.unlink()
        print("  removed", p)
        n += 1
print(f"stale checkpoints: {n}")
PY
echo "=== done ==="
