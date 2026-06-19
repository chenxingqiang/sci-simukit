#!/usr/bin/env python3
"""Local bond metrics from Exp5 tetramer xyz archives (mechanism support, no new DFT)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
XYZ_DIR = REPO / "dft_results" / "exp_5_synergy" / "xyz_structures"
OUT = REPO / "experiments" / "analysis" / "local_structure_tetramer.json"

STRAINS = (-5.0, -2.5, 0.0, 2.5, 3.0, 5.0)
DOPANTS = ("B", "N", "P")
COVALENT_R = {"C": 77, "B": 84, "N": 71, "P": 107}


def read_xyz(path: Path) -> tuple[list[str], np.ndarray]:
    lines = path.read_text().splitlines()
    n = int(lines[0].strip())
    symbols, coords = [], []
    for ln in lines[2 : 2 + n]:
        parts = ln.split()
        symbols.append(parts[0])
        coords.append([float(parts[1]), float(parts[2]), float(parts[3])])
    return symbols, np.array(coords, dtype=float)


def dopant_c_bonds(symbols: list[str], coords: np.ndarray, dopant: str) -> dict:
    sym = np.array(symbols)
    d_idx = np.where(sym == dopant)[0]
    c_idx = np.where(sym == "C")[0]
    if len(d_idx) == 0:
        return {"n_dopant": 0, "mean_d_ang": None, "std_d_ang": None}
    dists = [float(np.sqrt(((coords[c_idx] - coords[i]) ** 2).sum(axis=1)).min()) for i in d_idx]
    arr = np.array(dists)
    return {"n_dopant": int(len(d_idx)), "mean_d_ang": float(arr.mean()), "std_d_ang": float(arr.std())}


def main() -> None:
    records, by_dopant = [], {}
    for dop in DOPANTS:
        d0 = d3 = None
        for eps in STRAINS:
            path = XYZ_DIR / f"C60_strain_{eps:+.1f}_{dop}_doped_synergy.xyz"
            if not path.exists():
                continue
            sym, crd = read_xyz(path)
            bonds = dopant_c_bonds(sym, crd, dop)
            records.append({"dopant": dop, "strain_pct": eps, **bonds, "radius_delta_pm": COVALENT_R[dop] - COVALENT_R["C"]})
            if eps == 0.0:
                d0 = bonds["mean_d_ang"]
            if eps == 3.0:
                d3 = bonds["mean_d_ang"]
        by_dopant[dop] = {
            "mean_d_at_eps0_ang": d0,
            "mean_d_at_eps3_ang": d3,
            "delta_d_eps0_to_eps3_ang": (d3 - d0) if d0 and d3 else None,
            "radius_delta_pm": COVALENT_R[dop] - COVALENT_R["C"],
        }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"records": records, "summary_by_dopant": by_dopant}, indent=2) + "\n")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
