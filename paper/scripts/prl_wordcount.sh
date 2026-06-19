#!/bin/bash
# PRL body word count (excludes abstract, acknowledgments, bibliography).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="/Library/TeX/texbin:$PATH"
if ! command -v texcount >/dev/null; then
  echo "texcount not found" >&2; exit 1
fi
texcount -inc -sum -1 "$ROOT/strain_doped_graphullerene.tex"
echo "PRL limit: 3750 words (body + captions + equations)"
