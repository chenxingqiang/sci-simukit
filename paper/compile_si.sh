#!/bin/bash
# Compile supplementary-figures PDF (requires MacTeX / TeX Live).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PATH="/Library/TeX/texbin:/opt/homebrew/bin:/usr/local/bin:$PATH"

if ! command -v latexmk >/dev/null; then
  echo "latexmk not found. Install MacTeX: https://www.tug.org/mactex/" >&2
  exit 1
fi

cd "$ROOT"
latexmk -pdf -interaction=nonstopmode -file-line-error -f supplementary_figures.tex
echo "OK: $ROOT/supplementary_figures.pdf"
