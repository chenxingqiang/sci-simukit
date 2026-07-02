#!/usr/bin/env python3
"""Emit tetramer B/N/P rigid ENERGY inputs with dopant placement seed 137 (full strain grid)."""

from __future__ import annotations

import json
import os
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from modernize_cp2k_inp import modernize_cp2k_inp

REPO = Path(__file__).resolve().parents[3]
SYNERGY = REPO / "dft_results" / "exp_5_synergy"
OUT = Path(__file__).resolve().parent / "inputs"
HERE = Path(__file__).resolve().parent
OFFSETS_JSON = HERE / "seed137_reroll_offsets.json"
SEED = 137
STRAINS = (-5.0, -2.5, 0.0, 2.5, 3.0, 5.0)
DOPANTS = ("B", "N", "P")
# Tetramer ENERGY: legacy Exp5 used 1e-5; protocol-v2 default 1e-6 is too tight (see R382 diag).
DEFAULT_EPS = "1.0E-5"


def seed137_eps() -> str:
    return os.environ.get("SEED137_EPS", DEFAULT_EPS).strip()


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


def strain_tag(strain: float) -> str:
    return f"strain{strain:+.1f}_rigid".replace("+", "p").replace("-", "m")


def load_reroll_offsets() -> dict[str, int]:
    if not OFFSETS_JSON.is_file():
        return {}
    data = json.loads(OFFSETS_JSON.read_text())
    return {k: int(v) for k, v in data.items() if v is not None}


def reroll_seed(dop: str, strain: float, offsets: dict[str, int], tag: str) -> int:
    if tag in offsets:
        return SEED + int(strain * 10) + offsets[tag]
    env_key = f"SEED137_REROLL_{dop}"
    if os.environ.get(env_key):
        return SEED + int(strain * 10) + int(os.environ[env_key])
    raise RuntimeError(
        f"Missing reroll offset for {tag}; commit seed137_reroll_offsets.json or set {env_key}"
    )


def patch_eps_only(eps: str) -> int:
    """Update EPS_SCF in existing seed137_*_rigid.inp without touching coordinates."""
    count = 0
    for inp in sorted(OUT.glob("seed137_*_rigid.inp")):
        text = inp.read_text()
        new = re.sub(r"EPS_SCF\s+[\d.E+-]+", f"EPS_SCF {eps}", text)
        if new != text:
            inp.write_text(new)
            print("patched EPS", inp.name, "->", eps)
            count += 1
    return count


def main() -> None:
    eps = seed137_eps()
    if os.environ.get("SEED137_EPS_ONLY", "").strip().lower() in ("1", "true", "yes"):
        n = patch_eps_only(eps)
        print(f"done: EPS-only patch on {n} inputs (SEED137_EPS={eps})")
        return

    OUT.mkdir(parents=True, exist_ok=True)
    offsets = load_reroll_offsets()
    count = 0
    for strain in STRAINS:
        tpl = SYNERGY / f"C60_strain_{strain:+.1f}_pristine_synergy.inp"
        if not tpl.exists():
            print(f"skip missing {tpl}", file=sys.stderr)
            continue
        tag = f"seed137_pristine_{strain_tag(strain)}"
        txt = modernize_cp2k_inp(tpl.read_text(), eps_scf=eps)
        txt = re.sub(r"PROJECT \S+", f"PROJECT {tag}", txt, count=1)
        out_path = OUT / f"{tag}.inp"
        out_path.write_text(txt)
        print("wrote", out_path.name, f"EPS_SCF={eps}")
        count += 1
    for dop in DOPANTS:
        for strain in STRAINS:
            tpl = SYNERGY / f"C60_strain_{strain:+.1f}_{dop}_doped_synergy.inp"
            if not tpl.exists():
                print(f"skip missing {tpl}", file=sys.stderr)
                continue
            tag = f"seed137_{dop}_{strain_tag(strain)}"
            roll = reroll_seed(dop, strain, offsets, tag)
            txt = modernize_cp2k_inp(
                reroll_dopant_sites(tpl.read_text(), dop, roll),
                eps_scf=eps,
            )
            proj = tag
            txt = re.sub(r"PROJECT \S+", f"PROJECT {proj}", txt, count=1)
            out_path = OUT / f"{tag}.inp"
            out_path.write_text(txt)
            print("wrote", out_path.name, f"EPS_SCF={eps}")
            count += 1
    print(f"done: {count} inputs in {OUT} (SEED137_EPS={eps})")


if __name__ == "__main__":
    main()
