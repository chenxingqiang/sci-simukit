#!/usr/bin/env python3
"""Emit tetramer B/N/P rigid ENERGY inputs with dopant placement seed 137 (full strain grid)."""

from __future__ import annotations

import random
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SYNERGY = REPO / "dft_results" / "exp_5_synergy"
OUT = Path(__file__).resolve().parent / "inputs"
SEED = 137
STRAINS = (-5.0, -2.5, 0.0, 2.5, 3.0, 5.0)
DOPANTS = ("B", "N", "P")


def reroll_dopant_sites(text: str, element: str, seed: int) -> str:
    coord_m = re.search(r"(&COORD\n)(.*?)(\n    &END COORD)", text, re.S)
    if not coord_m:
        raise ValueError("COORD block not found")
    lines = coord_m.group(2).splitlines()
    c_idx = [i for i, ln in enumerate(lines) if ln.strip().startswith("C ")]
    dop_idx = [i for i, ln in enumerate(lines) if ln.strip().startswith(f"{element} ")]
    if not dop_idx:
        raise ValueError(f"No {element} sites in template")
    for i in dop_idx:
        lines[i] = lines[i].replace(f"{element} ", "C ", 1)
    random.seed(seed)
    pick = sorted(random.sample(c_idx, len(dop_idx)))
    for i, ci in zip(dop_idx, pick):
        lines[ci] = lines[ci].replace("C ", f"{element} ", 1)
    new_coord = coord_m.group(1) + "\n".join(lines) + coord_m.group(3)
    return text[: coord_m.start()] + new_coord + text[coord_m.end() :]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    count = 0
    for dop in DOPANTS:
        for strain in STRAINS:
            tpl = SYNERGY / f"C60_strain_{strain:+.1f}_{dop}_doped_synergy.inp"
            if not tpl.exists():
                print(f"skip missing {tpl}", file=sys.stderr)
                continue
            txt = reroll_dopant_sites(tpl.read_text(), dop, SEED + int(strain * 10) + hash(dop) % 1000)
            tag = f"seed137_{dop}_strain{strain:+.1f}_rigid".replace("+", "p").replace("-", "m")
            proj = tag
            txt = re.sub(r"PROJECT \S+", f"PROJECT {proj}", txt, count=1)
            out_path = OUT / f"{tag}.inp"
            out_path.write_text(txt)
            print("wrote", out_path.name)
            count += 1
    print(f"done: {count} inputs in {OUT}")


if __name__ == "__main__":
    main()
