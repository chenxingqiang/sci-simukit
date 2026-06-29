#!/usr/bin/env python3
"""Analyze periodic n=4 placement validation vs reference map (seed 42)."""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
INP_DIR = Path(__file__).resolve().parent / "inputs"
EXP10 = REPO / "experiments" / "exp_10_size_scaling" / "inputs"
SDC = REPO / "experiments" / "analysis" / "sdc" / "sdc_exp10_synergy_audit.json"
OUT = REPO / "experiments" / "analysis" / "periodic_placement_validation.json"

HA_TO_MEV = 27.211386245988 * 1000.0
N_MOL = 4
N_ATOMS = 60 * N_MOL


def parse_energy(out: Path) -> float | None:
    if not out.exists():
        return None
    text = out.read_text(errors="replace")
    if "SCF run converged" not in text:
        return None
    m = re.findall(r"ENERGY\|\s*Total FORCE_EVAL.*?([-]?\d+\.\d+)", text)
    return float(m[-1]) if m else None


def synergy_s(e_p0, e_p3, e_d0, e_d3) -> float:
    d_eps = (e_p3 - e_p0) / N_ATOMS
    d_dop = (e_d0 - e_p0) / N_ATOMS
    d_combined = (e_d3 - e_p0) / N_ATOMS
    return (d_combined - d_eps - d_dop) * HA_TO_MEV


def load_placement(seed: int) -> dict[str, float | None]:
    energies: dict[str, float | None] = {}
    for strain in (0.0, 3.0):
        st = f"pos{strain:.0f}pct"
        for dop in ("pristine", "B", "N", "P"):
            key = f"{dop}_eps{int(strain)}"
            out = INP_DIR / f"place_seed{seed}_{dop}_{st}.out"
            energies[key] = parse_energy(out)
    return energies


def s_for_dop(e: dict[str, float | None], dop: str) -> float | None:
    keys = ("pristine_eps0", "pristine_eps3", f"{dop}_eps0", f"{dop}_eps3")
    if any(e.get(k) is None for k in keys):
        return None
    return synergy_s(e["pristine_eps0"], e["pristine_eps3"], e[f"{dop}_eps0"], e[f"{dop}_eps3"])


def reference_n4() -> dict[str, float]:
    if not SDC.exists():
        return {}
    data = json.loads(SDC.read_text())
    out = {}
    for row in data.get("synergy_table", []):
        if row.get("n_molecules") == N_MOL:
            out[row["dopant"]] = row["synergy_S_meV_per_atom"]
    return out


def rank_abs(s: dict[str, float | None]) -> list[str]:
    valid = {k: abs(v) for k, v in s.items() if v is not None}
    return sorted(valid, key=lambda k: valid[k], reverse=True)


def main() -> None:
    ref = reference_n4()
    seeds_report = {}
    for seed in (137, 271):
        e = load_placement(seed)
        s = {d: s_for_dop(e, d) for d in ("B", "N", "P")}
        converged = sum(1 for v in e.values() if v is not None)
        seeds_report[str(seed)] = {
            "energies_ha": e,
            "S_meV_per_atom_eps3": s,
            "converged_points": converged,
            "total_points": len(e),
            "rank_by_abs_S": rank_abs(s) if all(s[d] is not None for d in s) else None,
            "P_largest_abs_S": (
                rank_abs(s)[0] == "P" if all(s[d] is not None for d in s) else None
            ),
        }

    ref_rank = rank_abs(ref) if len(ref) == 3 else None
    report = {
        "n_molecules": N_MOL,
        "reference_map": {"seed": 42, "S_meV_per_atom_eps3": ref, "rank_by_abs_S": ref_rank},
        "alternate_placements": seeds_report,
        "status": "pending",
    }
    all_done = all(
        seeds_report[str(s)]["converged_points"] == seeds_report[str(s)]["total_points"]
        for s in (137, 271)
        if str(s) in seeds_report
    )
    if all_done and all(seeds_report[str(s)]["S_meV_per_atom_eps3"]["P"] is not None for s in (137, 271)):
        report["status"] = "complete"

    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
