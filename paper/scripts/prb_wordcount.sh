#!/bin/bash
# PRB word count (informational). Default: Regular Article (no APS length limit).
# Set PRB_ARTICLE_TYPE=rapid to gate against the 4500-word Rapid Communications cap.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PATH="/Library/TeX/texbin:${PATH:-}"

ARTICLE_TYPE="${PRB_ARTICLE_TYPE:-regular}"
TEX="${1:-strain_doped_graphullerene.tex}"

if ! command -v texcount >/dev/null; then
  echo "texcount not found (install TeX Live)" >&2
  exit 1
fi

raw="$(texcount -inc -sum "$TEX" 2>&1)" || true
words="$(printf '%s\n' "$raw" | awk '/^Sum count:/{w=$3} END{print w}')"
text_words="$(printf '%s\n' "$raw" | awk '/^Words in text:/{t=$4} END{print t}')"

if [[ -z "${words:-}" ]]; then
  words="$(printf '%s\n' "$raw" | grep -E '^[0-9]+$' | tail -1)"
fi

echo "PRB submission: ${ARTICLE_TYPE^} Article"
echo "texcount (with \\input files): ${words:-?} words total; ${text_words:-?} words in body text"
echo "Source: $TEX"

if printf '%s\n' "$raw" | grep -q 'Could not identify document class'; then
  echo "Note: texcount does not recognize revtex4-2 (count still valid)."
fi

case "$ARTICLE_TYPE" in
  regular|Regular)
    echo "OK: Regular Article — no APS length limit."
    echo "Reference only: Rapid Communications Letters <= 4500 words (not this submission)."
    exit 0
    ;;
  rapid|Rapid)
    limit=4500
    if [[ -n "${words:-}" && "$words" -gt "$limit" ]]; then
      echo "FAIL: ${words} words exceeds PRB Rapid Communications limit (${limit})." >&2
      exit 1
    fi
    echo "OK: ${words} words — within Rapid Communications limit (${limit})."
    exit 0
    ;;
  *)
    echo "Unknown PRB_ARTICLE_TYPE=$ARTICLE_TYPE (use regular or rapid)" >&2
    exit 2
    ;;
esac
