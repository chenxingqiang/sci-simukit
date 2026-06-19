#!/usr/bin/env python3
"""Parse Exp.4 factorial IPR/J from converged polaron .out files (2x2 grid)."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "dft_results/exp_4_polaron/outputs"
AUDIT_JSON = REPO / "experiments/analysis/exp4_polaron_verification.json"

FACTORIAL = [
    ("pristine_0pct", 0.0, "pristine"),
    ("pristine_3pct", 3.0, "pristine"),
    ("B_0pct", 0.0, "B"),
    ("coupled_B_3pct", 3.0, "B"),
]


def _out_path(strain: float, dopant: str) -> Path:
    return OUT_DIR / f"polaron_{strain:+.1f}_{dopant}_q0.out"


def parse_dft_output(path: Path) -> dict:
    result = {
        "total_energy_Ha": None,
        "homo_eV": None,
        "homo_1_eV": None,
        "J_meV": None,
        "converged": False,
        "out_file": str(path.relative_to(REPO)),
    }
    text = path.read_text(errors="replace")
    if "SCF run converged" not in text:
        return result
    result["converged"] = True

    m = re.search(
        r"ENERGY\| Total FORCE_EVAL \( QS \) energy \[a\.u\.\]:\s*([-+]?\d+\.\d+)",
        text,
    )
    if m:
        result["total_energy_Ha"] = float(m.group(1))

    eigenvalues: list[float] = []
    occupations: list[float] = []
    for line in text.splitlines():
        if not line.strip().startswith("MO|"):
            continue
        if any(x in line for x in ("EIGENVALUES", "Sum", "E(Fermi)", "Index")):
            continue
        parts = line.split()
        if len(parts) < 5:
            continue
        try:
            eigenvalues.append(float(parts[3]))
            occupations.append(float(parts[4]))
        except ValueError:
            continue

    homo_idx = -1
    for i, occ in enumerate(occupations):
        if occ > 0:
            homo_idx = i
    if homo_idx >= 1:
        result["homo_eV"] = eigenvalues[homo_idx]
        result["homo_1_eV"] = eigenvalues[homo_idx - 1]
        result["J_meV"] = abs(result["homo_eV"] - result["homo_1_eV"]) / 2.0 * 1000.0

    return result


def _mulliken_net_charge(parts: list[str]) -> float | None:
    """CP2K Mulliken: closed-shell (5 cols) or spin (7+ cols)."""
    if len(parts) < 5 or not parts[0].isdigit():
        return None
    try:
        if len(parts) >= 7:
            return float(parts[-2])
        return float(parts[-1])
    except ValueError:
        return None


def parse_ipr(path: Path) -> float | None:
    text = path.read_text(errors="replace")
    charges: list[float] = []
    in_mulliken = False
    for line in text.splitlines():
        if "Mulliken Population Analysis" in line:
            in_mulliken = True
            continue
        if in_mulliken and line.strip().startswith("# Total charge"):
            in_mulliken = False
            continue
        if not in_mulliken:
            continue
        if not any(f" {el} " in line for el in ("C", "B", "N", "P")):
            continue
        q = _mulliken_net_charge(line.split())
        if q is not None:
            charges.append(q)
    if not charges:
        return None
    arr = np.abs(np.array(charges) - np.mean(charges))
    s = arr.sum()
    if s <= 0:
        return None
    norm = arr / s
    return float(1.0 / np.sum(norm**2))


def factorial_decomposition(systems: dict) -> dict:
    p0 = systems["pristine_0pct"]
    p3 = systems["pristine_3pct"]
    b0 = systems["B_0pct"]
    b3 = systems["coupled_B_3pct"]

    def deltas(key: str) -> dict:
        j = lambda s: s.get(key)
        d_strain_p = (j(p3) or 0) - (j(p0) or 0)
        d_dope = (j(b0) or 0) - (j(p0) or 0)
        d_coupled = (j(b3) or 0) - (j(p0) or 0)
        interaction = (j(b3) or 0) - (j(b0) or 0) - d_strain_p
        return {
            "strain_on_pristine": round(d_strain_p, 3),
            "doping_at_zero_strain": round(d_dope, 3),
            "coupled_minus_pristine": round(d_coupled, 3),
            "interaction_cross_term": round(interaction, 3),
        }

    return {"J_meV": deltas("J_meV"), "IPR": deltas("IPR")}


def main() -> None:
    systems: dict = {}
    for key, strain, dopant in FACTORIAL:
        path = _out_path(strain, dopant)
        if not path.exists():
            raise FileNotFoundError(path)
        parsed = parse_dft_output(path)
        ipr = parse_ipr(path)
        if not parsed["converged"]:
            raise RuntimeError(f"not converged: {path}")
        if parsed["J_meV"] is None:
            raise RuntimeError(f"no J from MO levels: {path}")
        if ipr is None:
            raise RuntimeError(f"no IPR from Mulliken: {path}")
        systems[key] = {
            "strain_pct": strain,
            "dopant": dopant,
            "IPR": round(ipr, 2),
            "J_meV": round(parsed["J_meV"], 2),
            "total_energy_Ha": parsed["total_energy_Ha"],
            "regime": "small polaron hopping",
            "converged": True,
            "source_out": parsed["out_file"],
        }

    derived = factorial_decomposition(systems)
    j = systems["coupled_B_3pct"]["J_meV"]
    derived["polaron_transition_confirmed"] = False
    derived["validation_J_coupled_gt_lambda_half"] = bool(j > 90.0)

    audit = {
        "source": "dft_results/exp_4_polaron/outputs (factorial 2x2)",
        "verified_date": str(date.today()),
        "note": "Four converged neutral SP points; factorial cross terms in derived.",
        "systems": systems,
        "derived": derived,
    }

    AUDIT_JSON.write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
