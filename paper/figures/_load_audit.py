"""Load verified audit JSON and parse Exp.7 HOMO–LUMO gaps from converged .out files."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

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
    """Alpha for Fig.~1(c): reference placement PBE+D3 when 24/24; else alternate."""
    root = repo_root()
    ref_path = root / "experiments/analysis/reference_placement_pbed3.json"
    if ref_path.is_file():
        ref = json.loads(ref_path.read_text())
        if (
            ref.get("status") == "complete"
            and not ref.get("alpha_provisional", True)
            and "systems" in ref
        ):
            alpha = {
                "B": float(ref["systems"]["B"]["alpha_meV_per_pct"]),
                "N": float(ref["systems"]["N"]["alpha_meV_per_pct"]),
                "P": float(ref["systems"]["P"]["alpha_meV_per_pct"]),
                "pristine": float(ref["pristine"]["alpha_meV_per_pct"]),
            }
            return alpha, "reference placement (seed~42), PBE+D3 rigid"

    alt = {
        "B": 21.4,
        "N": 45.4,
        "P": 989.6,
        "pristine": 1.0,
    }
    return alt, "alternate placement (seed~137), PBE+D3 rigid"



def load_placement_alpha_pair() -> tuple[dict[str, float], dict[str, float]]:
    """Reference (seed~42) vs alternate (seed~137) PBE+D3 rigid tetramer alpha."""
    ref, _ = load_tetramer_alpha_panel()
    alt = {"B": 21.4, "N": 45.4, "P": 989.6, "pristine": 1.0}
    return ref, alt

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


def _alpha_fit_stderr(strains: list[float], energies_ha: list[float]) -> float:
    """Standard error of least-squares slope (meV/%) on total-cell energies."""
    ha_to_mev = 27.211386245988 * 1000.0
    x = np.array(strains, dtype=float)
    y = np.array(energies_ha, dtype=float)
    if len(x) < 3:
        return float("nan")
    a = np.vstack([x, np.ones(len(x))]).T
    coef, _, _, _ = np.linalg.lstsq(a, y, rcond=None)
    yhat = a @ coef
    se = np.sqrt(np.sum((y - yhat) ** 2) / (len(x) - 2))
    return float(se * np.sqrt(1.0 / np.sum((x - x.mean()) ** 2)) * ha_to_mev)


def load_reference_pbed3_alpha_S() -> tuple[
    dict[str, float], dict[str, float], float, dict[str, float]
]:
    """Reference-placement PBE+D3 tetramer alpha, S@+3%, and linear-fit slope SEs."""
    ref = load_json("experiments/analysis/reference_placement_pbed3.json")
    if ref.get("status") != "complete":
        raise RuntimeError("reference_placement_pbed3 not complete")
    alpha = {d: float(ref["systems"][d]["alpha_meV_per_pct"]) for d in ("B", "N", "P")}
    alpha["pristine"] = float(ref["pristine"]["alpha_meV_per_pct"])
    s_tet = {d: float(ref["systems"][d]["S_meV_per_atom_at_eps3"]) for d in ("B", "N", "P")}
    alpha_err: dict[str, float] = {}
    for key in ("B", "N", "P"):
        se = ref["systems"][key]["strain_energies_ha"]
        strains = sorted(float(k) for k in se)
        es = [v for s in strains for k, v in se.items() if abs(float(k) - s) < 1e-9]
        alpha_err[key] = _alpha_fit_stderr(strains, es)
    pri_se = ref["pristine"]["strain_energies_ha"]
    pri_strains = sorted(float(k) for k in pri_se)
    pri_es = [v for s in pri_strains for k, v in pri_se.items() if abs(float(k) - s) < 1e-9]
    alpha_err["pristine"] = _alpha_fit_stderr(pri_strains, pri_es)
    return alpha, s_tet, float(ref["pristine"]["alpha_meV_per_pct"]), alpha_err


def load_alternate_alpha_S() -> tuple[dict[str, float], dict[str, float]]:
    """Alternate-placement PBE+D3 values matching main-text Table I."""
    alpha = {"B": 21.4, "N": 45.4, "P": 989.6, "pristine": 1.0}
    s_tet = {"B": -2.6, "N": 12.6, "P": 41.4}
    return alpha, s_tet


def load_local_structure_summary() -> dict[str, dict[str, float]]:
    data = load_json("experiments/analysis/local_structure_tetramer.json")
    return data["summary_by_dopant"]


def load_local_structure_paths() -> dict[str, list[tuple[float, float, float]]]:
    """dopant -> [(strain_pct, mean_d_ang, std_d_ang), ...] from tetramer XYZ."""
    data = load_json("experiments/analysis/local_structure_tetramer.json")
    out: dict[str, list[tuple[float, float, float]]] = {}
    for row in data["records"]:
        dop = str(row["dopant"])
        out.setdefault(dop, []).append(
            (float(row["strain_pct"]), float(row["mean_d_ang"]), float(row["std_d_ang"]))
        )
    for dop in out:
        out[dop] = sorted(out[dop], key=lambda x: x[0])
    return out


def load_hirshfeld_strain_paths() -> dict[str, list[tuple[float, float]]]:
    """dopant -> list of (strain_pct, hirshfeld_charge)."""
    out: dict[str, list[tuple[float, float]]] = {}
    for dop in ("B", "N", "P"):
        data = load_json(f"experiments/analysis/population_{dop}_n1_strain.json")
        key = f"hirshfeld_charge_{dop}"
        pts = [
            (float(row["strain_pct"]), float(row[key]))
            for row in data["strain_path"]
            if row.get("converged") and key in row
        ]
        out[dop] = sorted(pts, key=lambda x: x[0])
    return out


def load_periodic_relax_n1_P() -> tuple[float, float]:
    data = load_json("experiments/analysis/periodic_relax_validation_n1_P.json")
    return float(data["S_rigid"]["S_meV_per_atom"]), float(data["S_relaxed"]["S_meV_per_atom"])


def load_mismatch_rows() -> list[dict[str, float]]:
    data = load_json("experiments/analysis/mismatch_synergy_scaling.json")
    return data["rows"]
