#!/bin/bash
# PRB word count (informational). Regular Articles: no limit; Rapid/Letter: 4500.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if command -v texcount >/dev/null; then
  texcount -1 -sum strain_doped_graphullerene.tex 2>/dev/null | tail -1
  echo "PRB Rapid Communications limit: 4500 words (Regular Article: no limit)"
else
  bash scripts/prl_wordcount.sh 2>/dev/null || true
fi
