"""Load verified audit JSON and parse Exp.7 HOMO–LUMO gaps from converged .out files."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HA_TO_MEV = 27.211386245988 * 1000.0


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(rel: str) -> dict[str, Any]:
    path = repo_root() / rel
    if not path.is_file():
        raise FileNotFoundError(f"Missing audit JSON: {path}")
    return json.loads(path.read_text())


@dataclass(frozen=True)
class Exp7GapPoint:
    dopant: str
    strain_pct: float
    gap_ev: float
    out_file: str
    converged: bool


def parse_exp7_gaps() -> list[Exp7GapPoint]:
    out_dir = repo_root() / "dft_results/exp_7_electronic_structure/outputs"
    points: list[Exp7GapPoint] = []
    pat = re.compile(r"^elec_(neg|pos)(\d+)p(\d+)_(.+)\.out$")
    gap_re = re.compile(r"HOMO - LUMO gap \[eV\]\s*:\s*([-+]?\d+\.\d+)")

    for path in sorted(out_dir.glob("elec_*.out")):
        m = pat.match(path.name)
        if not m:
            continue
        sign, whole, frac, dopant = m.groups()
        strain = float(f"{whole}.{frac}")
        if sign == "neg":
            strain = -strain
        text = path.read_text(errors="replace")
        converged = "SCF run converged" in text
        gm = gap_re.search(text)
        if not gm:
            continue
        points.append(
            Exp7GapPoint(
                dopant=dopant,
                strain_pct=strain,
                gap_ev=float(gm.group(1)),
                out_file=path.name,
                converged=converged,
            )
        )
    return points


def ha_per_atom_to_meV(ha_per_atom: float) -> float:
    return ha_per_atom * HA_TO_MEV


def load_tetramer_alpha_panel() -> tuple[dict[str, float], str]:
    """Alpha for Fig.~1(c): prefer matched-functional PBE+D3; fallback alternate placement."""
    root = repo_root()
    ref_path = root / "experiments/analysis/reference_placement_pbed3.json"
    if ref_path.is_file():
        ref = json.loads(ref_path.read_text())
        if ref.get("status") == "complete" and "alpha_meV_per_pct" in ref:
            alpha = dict(ref["alpha_meV_per_pct"])
            alpha.setdefault("pristine", 1.0)
            return alpha, "reference placement, PBE+D3"

    alt = {
        "B": 21.4,
        "N": 45.4,
        "P": 989.6,
        "pristine": 1.0,
    }
    return alt, "alternate placement (seed~137), PBE+D3 rigid"


def synergy_rows(audit: dict[str, Any], dopant: str) -> list[tuple[int, float]]:
    rows = [
        (r["n_molecules"], r["synergy_S_meV_per_atom"])
        for r in audit["synergy_table"]
        if r["dopant"] == dopant
    ]
    return sorted(rows, key=lambda x: x[0])


def n4_decomposition(sdc: dict[str, Any], dopant: str) -> dict[str, float]:
    """Sequential vs coupled energy shifts @ n=4, +3% strain (meV/atom)."""
    for row in sdc["synergy_energy_per_atom"]:
        if row["dopant"] == dopant and row["n_molecules"] == 4:
            seq_ha = row["strain_only_delta"] + row["doping_only_delta"]
            coupled_ha = row["combined"] - row["reference"]
            s_ha = row["synergy_S"]
            return {
                "sequential_meV": ha_per_atom_to_meV(seq_ha),
                "coupled_meV": ha_per_atom_to_meV(coupled_ha),
                "synergy_meV": ha_per_atom_to_meV(s_ha),
            }
    raise KeyError(f"No n=4 decomposition for dopant {dopant}")
