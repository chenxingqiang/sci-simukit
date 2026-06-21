#!/usr/bin/env bash
# Three-layer reliability gate: SETUP (inp) -> PROCESS (workflow) -> RESULTS (.out / JSON).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Refreshing analysis JSON (stale-safe) ==="
python3 "$ROOT/experiments/analysis/analyze_exp9_polaron.py" 2>/dev/null || true

echo "=== Reliability audit ==="
ec=0
python3 "$ROOT/experiments/verify_experiment_reliability.py" --json "$ROOT/experiments/analysis/reliability_audit.json" || ec=$?
exit "$ec"
