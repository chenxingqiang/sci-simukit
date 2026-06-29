#!/usr/bin/env bash
# Resume PRB revision DFT queue when no CP2K is running.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if pgrep -f 'cp2k\.psmp' >/dev/null 2>&1; then
  echo "CP2K running; exit." >&2
  bash "$ROOT/experiments/exp5_seed137_status_line.sh" 2>/dev/null || true
  bash "$ROOT/experiments/exp10_placement_status_line.sh" 2>/dev/null || true
  exit 0
fi
exec bash "$ROOT/experiments/run_prb_revision_dft.sh"
