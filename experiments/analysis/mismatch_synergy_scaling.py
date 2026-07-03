#!/usr/bin/env python3
"""Mismatch index vs periodic |S| at n=1 (+3% strain) for design-rule audit."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SDC = ROOT / "experiments/analysis/sdc/sdc_exp10_synergy_audit.json"
OUT = ROOT / "experiments/analysis/mismatch_synergy_scaling.json"

# Covalent radii excess (pm vs C) from paper/tables/tab_V.tex
MISMATCH_PM = {"B": 7, "N": -6, "P": 30}
R_C_PM = 77  # C (Pauling), for relative mismatch only


def main() -> None:
    audit = json.loads(SDC.read_text())
    n1 = {
        row["dopant"]: abs(row["synergy_S_meV_per_atom"])
        for row in audit["synergy_table"]
        if row["n_molecules"] == 1 and row["strain_pct"] == 3.0
    }
    rows = []
    for dop in ("B", "N", "P"):
        dr = MISMATCH_PM[dop]
        rows.append(
            {
                "dopant": dop,
                "delta_r_cov_pm": dr,
                "abs_delta_r_cov_pm": abs(dr),
                "mismatch_fraction": abs(dr) / R_C_PM,
                "S_meV_per_atom_n1": n1[dop],
            }
        )
    # Two-regime heuristic (audit only; not a fitted universal law)
    large_mismatch = [r for r in rows if r["abs_delta_r_cov_pm"] >= 20]
    small_mismatch = [r for r in rows if r["abs_delta_r_cov_pm"] < 15]
    payload = {
        "strain_pct": 3.0,
        "n_molecules": 1,
        "source_S": str(SDC.relative_to(ROOT)),
        "source_delta_r": "paper/tables/tab_V.tex",
        "rows": rows,
        "heuristic": {
            "large_abs_dr_pm_ge_20": {
                "dopants": [r["dopant"] for r in large_mismatch],
                "max_S_meV_per_atom": max(r["S_meV_per_atom_n1"] for r in large_mismatch)
                if large_mismatch
                else None,
            },
            "small_abs_dr_pm_lt_15": {
                "dopants": [r["dopant"] for r in small_mismatch],
                "S_range_meV_per_atom": [
                    min(r["S_meV_per_atom_n1"] for r in small_mismatch),
                    max(r["S_meV_per_atom_n1"] for r in small_mismatch),
                ]
                if small_mismatch
                else None,
            },
            "note": "N breaks pure size-mismatch scaling (electronic channel); P is geometric-regime anchor.",
        },
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
