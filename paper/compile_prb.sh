#!/bin/bash
# PRB submission bundle: REVTeX from revtex-tds + main + SI PDFs.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$ROOT/.." && pwd)"
export PATH="/Library/TeX/texbin:/opt/homebrew/bin:/usr/local/bin:$PATH"
export TEXINPUTS="$REPO/revtex-tds/tex/latex//:${TEXINPUTS:-}"
export BSTINPUTS="$REPO/revtex-tds/bibtex/bst//:${BSTINPUTS:-}"

if ! command -v latexmk >/dev/null; then
  echo "latexmk not found." >&2
  exit 1
fi

bash "$ROOT/figures/render_prb.sh"
bash "$ROOT/figures/render_si_figures.sh"
cd "$ROOT"
latexmk -pdf -interaction=nonstopmode -file-line-error -f strain_doped_graphullerene.tex
latexmk -pdf -interaction=nonstopmode -file-line-error -f supplementary_figures.tex
bash "$ROOT/scripts/prb_wordcount.sh" 2>/dev/null || true
echo "OK: $ROOT/strain_doped_graphullerene.pdf + supplementary_figures.pdf"
