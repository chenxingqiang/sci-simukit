#!/usr/bin/env python3
"""Generate Exp.10 MO_CUBES single-point inputs from converged pos0pct geometries."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SRC_DIR = REPO / "experiments" / "exp_10_size_scaling" / "inputs"
OUT_DIR = Path(__file__).resolve().parent / "inputs"

SIZES = (4, 6, 8)
DOPANTS = ("pristine", "B", "N", "P")

MO_PRINT_BLOCK = """
    &PRINT
      &MO
        EIGENVALUES .TRUE.
        OCCUPATION_NUMBERS .TRUE.
        NDIGITS 8
        &EACH
          QS_SCF 0
        &END EACH
      &END MO

      &MO_CUBES
        NHOMO 1
        NLUMO 1
        WRITE_CUBE .TRUE.
      &END MO_CUBES

      &MULLIKEN
      &END MULLIKEN
    &END PRINT"""


def patch_inp(text: str, project: str) -> str:
    text = re.sub(
        r"^\s*PROJECT\s+\S+",
        f"  PROJECT {project}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if "&MO_CUBES" in text:
        return text
    if re.search(r"&PRINT\s*\n\s*&MULLIKEN", text):
        text = re.sub(
            r"&PRINT\s*\n\s*&MULLIKEN\s*\n\s*&END MULLIKEN\s*\n\s*&END PRINT",
            MO_PRINT_BLOCK.strip(),
            text,
            count=1,
        )
    elif "&PRINT" in text:
        text = re.sub(r"&PRINT.*?&END PRINT", MO_PRINT_BLOCK.strip(), text, count=1, flags=re.DOTALL)
    else:
        text = text.replace("&END XC", f"&END XC{MO_PRINT_BLOCK}", 1)
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", type=int, nargs="*", default=list(SIZES))
    parser.add_argument("--dopants", nargs="*", default=list(DOPANTS))
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written: list[str] = []

    for n in args.sizes:
        for dop in args.dopants:
            stem = f"size_{n}x60_{dop}_pos0pct"
            src = SRC_DIR / f"{stem}.inp"
            if not src.is_file():
                raise SystemExit(f"missing source geometry: {src}")
            out_stem = f"{stem}_mo"
            out_inp = OUT_DIR / f"{out_stem}.inp"
            patched = patch_inp(src.read_text(), out_stem)
            out_inp.write_text(patched)
            written.append(out_stem)
            print(f"  {out_stem}.inp")

    print(f"Wrote {len(written)} MO_CUBES SP inputs -> {OUT_DIR}")


if __name__ == "__main__":
    main()
