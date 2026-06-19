#!/usr/bin/env python3
"""Emit tetramer P@+3% rigid ENERGY inputs with dopant placement seed 137."""

from __future__ import annotations

import random
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SYNERGY_OUT = REPO / "dft_results" / "exp_5_synergy"
OUT = Path(__file__).resolve().parent / "inputs"
SEED = 137

# Reuse archived +3% P template (strain cell + coords) and re-roll P sites.
TEMPLATE = SYNERGY_OUT / "C60_strain_+3.0_P_doped_synergy.inp"
if not TEMPLATE.exists():
    raise SystemExit(f"Missing template: {TEMPLATE}")

def reroll_p_sites(text: str, seed: int) -> str:
    coord_m = re.search(r"(&COORD\n)(.*?)(\n    &END COORD)", text, re.S)
    if not coord_m:
        raise ValueError("COORD block not found")
    lines = coord_m.group(2).splitlines()
    c_idx = [i for i, ln in enumerate(lines) if ln.strip().startswith("C ")]
    p_idx = [i for i, ln in enumerate(lines) if ln.strip().startswith("P ")]
    # restore C from template by stripping P lines back to C at those indices
    for i in p_idx:
        lines[i] = lines[i].replace("P ", "C ", 1)
    random.seed(seed)
    pick = sorted(random.sample(c_idx, len(p_idx)))
    for i, ci in zip(p_idx, pick):
        lines[ci] = lines[ci].replace("C ", "P ", 1)
    new_coord = coord_m.group(1) + "\n".join(lines) + coord_m.group(3)
    return text[: coord_m.start()] + new_coord + text[coord_m.end() :]

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for strain, tag in ((0.0, "eps0"), (3.0, "eps3")):
        tpl = SYNERGY_OUT / f"C60_strain_{strain:+.1f}_P_doped_synergy.inp"
        if not tpl.exists():
            print(f"skip missing {tpl}")
            continue
        txt = reroll_p_sites(tpl.read_text(), SEED + int(strain))
        proj = f"seed137_P_{tag}_rigid"
        txt = re.sub(r"PROJECT \S+", f"PROJECT {proj}", txt, count=1)
        (OUT / f"{proj}.inp").write_text(txt)
        print("wrote", OUT / f"{proj}.inp")

if __name__ == "__main__":
    main()
