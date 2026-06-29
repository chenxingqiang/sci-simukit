#!/usr/bin/env python3
"""Matched-functional PBE+D3 rigid S vs relaxed S (Table III quantitative retention)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "experiments" / "exp_5_synergy" / "relax_validation"))
from analyze_relax_s import AUDIT_OUT, load_corner_energies, synergy_s  # noqa: E402

RIGID_DIR = Path(__file__).resolve().parent / "inputs"
MATCHED_OUT = REPO / "experiments" / "analysis" / "relax_validation_matched_functional.json"

RIGID_PBED3 = {
    "pristine_eps0": "rigid_pbed3_pristine_eps0_sp.out",
    "pristine_eps3": "rigid_pbed3_pristine_eps3_sp.out",
    "P_eps0": "rigid_pbed3_P_eps0_sp.out",
    "P_eps3": "rigid_pbed3_P_eps3_sp.out",
}


def main() -> None:
    rigid_pbed3 = load_corner_energies(RIGID_DIR, RIGID_PBED3)
    base = json.loads(AUDIT_OUT.read_text()) if AUDIT_OUT.exists() else {}

    report = {
        "n_atoms": 240,
        "dopant": "P",
        "strain_pct": 3.0,
        "rigid_protocol": "PBE+D3 rigid single-point (matched functional), 400 Ry",
        "relaxed_protocol": base.get("relaxed_protocol", "PBE+D3 fixed-cell GEO_OPT"),
        "quantitative_ratio_valid": False,
        "energies_ha": {"rigid_pbed3": rigid_pbed3, "relaxed": base.get("energies_ha", {}).get("relaxed", {})},
        "scf_converged": {
            k: (RIGID_DIR / RIGID_PBED3[k]).exists()
            and "SCF run converged" in (RIGID_DIR / RIGID_PBED3[k]).read_text(errors="replace")
            for k in RIGID_PBED3
        },
    }

    if all(rigid_pbed3[k] is not None for k in rigid_pbed3):
        report["S_rigid_pbed3"] = synergy_s(
            rigid_pbed3["pristine_eps0"],
            rigid_pbed3["pristine_eps3"],
            rigid_pbed3["P_eps0"],
            rigid_pbed3["P_eps3"],
        )

    if "S_relaxed" in base and "S_rigid_pbed3" in report:
        sr = report["S_rigid_pbed3"]["S_meV_per_atom"]
        sl = base["S_relaxed"]["S_meV_per_atom"]
        report["delta_S_meV_matched"] = sl - sr
        report["sign_preserved_matched"] = (sr == 0) or (sr * sl > 0)
        if abs(sr) > 1e-6:
            report["retention_ratio_abs"] = round(abs(sl) / abs(sr), 3)
        report["quantitative_ratio_valid"] = True

    MATCHED_OUT.parent.mkdir(parents=True, exist_ok=True)
    MATCHED_OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
