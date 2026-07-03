#!/usr/bin/env python3
"""Modernize archived reference-placement (seed 42) tetramer synergy inputs to PBE+D3."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "experiments/exp_5_synergy"))

from modernize_cp2k_inp import modernize_cp2k_inp  # noqa: E402

SRC = REPO / "dft_results/exp_5_synergy"
OUT = Path(__file__).resolve().parent / "inputs"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for src in sorted(SRC.glob("C60_strain_*_synergy.inp")):
        dst = OUT / src.name.replace("_synergy", "_refpbed3")
        txt = modernize_cp2k_inp(src.read_text(encoding="utf-8", errors="replace"))
        dst.write_text(txt, encoding="utf-8")
        print("wrote", dst.name)
        n += 1
    print(f"generated {n} reference PBE+D3 inputs")


if __name__ == "__main__":
    main()
