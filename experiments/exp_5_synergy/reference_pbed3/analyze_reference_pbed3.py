#!/usr/bin/env python3
"""Parse reference-placement PBE+D3 tetramer grid; emit alpha, S, E_sub."""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
INP_DIR = Path(__file__).resolve().parent / "inputs"
OUT_JSON = REPO / "experiments/analysis/reference_placement_pbed3.json"
N_ATOMS = 240
HA_TO_MEV = 27.211386245988 * 1000.0
STRAINS = (-5.0, -2.5, 0.0, 2.5, 3.0, 5.0)


def strain_tag(eps: float) -> str:
    return f"{eps:+.1f}"


def parse_energy(out: Path) -> float | None:
    if not out.exists() or "SCF run converged" not in out.read_text(errors="replace"):
        return None
    m = re.findall(r"ENERGY\| Total FORCE_EVAL.*?(-?\d+\.\d+)", out.read_text(errors="replace"))
    return float(m[-1]) if m else None


def fit_alpha(strains: list[float], energies: list[float]) -> float | None:
    if len(strains) < 3:
        return None
    return float(np.polyfit(strains, energies, 1)[0] * HA_TO_MEV)


def synergy_s(e_p0, e_p3, e_d0, e_d3) -> float:
    return ((e_d3 - e_p0) - (e_p3 - e_p0) - (e_d0 - e_p0)) / N_ATOMS * HA_TO_MEV


def main() -> None:
    pristine: dict[float, float] = {}
    for eps in STRAINS:
        tag = strain_tag(eps)
        out = INP_DIR / f"C60_strain_{tag}_pristine_refpbed3.out"
        e = parse_energy(out)
        if e is not None:
            pristine[eps] = e

    report = {
        "placement": "reference (seed 42 archive map)",
        "functional": "PBE+D3",
        "n_atoms": N_ATOMS,
        "status": "pending",
        "systems": {},
    }
    done = 0
    total = 0
    for dop in ("B", "N", "P"):
        energies: dict[float, float] = {}
        for eps in STRAINS:
            total += 1
            tag = strain_tag(eps)
            out = INP_DIR / f"C60_strain_{tag}_{dop}_doped_refpbed3.out"
            e = parse_energy(out)
            if e is not None:
                energies[eps] = e
                done += 1
        strains = sorted(energies)
        alpha = fit_alpha(strains, [energies[s] for s in strains]) if len(strains) >= 3 else None
        e0 = energies.get(0.0)
        e5 = energies.get(5.0)
        n_dop = {"B": 13, "N": 12, "P": 12}[dop]
        e_sub = None
        if e0 is not None and pristine.get(0.0) is not None:
            e_sub = (e0 - pristine[0.0]) / n_dop * HA_TO_MEV / 1000.0 * 1000  # eV/dopant
            e_sub = (e0 - pristine[0.0]) / n_dop * 27.211386245988
        s3 = None
        if all(x in energies for x in (0.0, 3.0)) and all(x in pristine for x in (0.0, 3.0)):
            s3 = synergy_s(pristine[0.0], pristine[3.0], energies[0.0], energies[3.0])
        report["systems"][dop] = {
            "alpha_meV_per_pct": alpha,
            "E_sub_eV_per_dopant": e_sub,
            "S_meV_per_atom_at_eps3": s3,
            "strain_energies_ha": {str(k): v for k, v in energies.items()},
            "converged_strain_points": len(strains),
        }
    pri_alpha = None
    if len(pristine) >= 3:
        ss = sorted(pristine)
        pri_alpha = fit_alpha(ss, [pristine[s] for s in ss])
    report["pristine"] = {
        "alpha_meV_per_pct": pri_alpha,
        "strain_energies_ha": {str(k): v for k, v in pristine.items()},
    }
    report["converged_tasks"] = done + len(pristine)
    report["total_tasks"] = total + len(STRAINS)
    if report["converged_tasks"] == report["total_tasks"]:
        report["status"] = "complete"
    elif report["converged_tasks"]:
        report["status"] = "partial"
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
