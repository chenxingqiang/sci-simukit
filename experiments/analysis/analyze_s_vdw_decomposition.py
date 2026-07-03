#!/usr/bin/env python3
"""Compute dispersion (D3) contribution to synergy S from four-corner CP2K outputs."""

from __future__ import annotations

import json
import re
from pathlib import Path

HA_TO_MEV = 27.211386245988 * 1000.0
REPO = Path(__file__).resolve().parents[2]


def parse_dispersion_ha(path: Path) -> float | None:
    if not path.exists():
        return None
    text = path.read_text(errors="replace")
    if "SCF run converged" not in text and "GEOMETRY OPTIMIZATION COMPLETED" not in text:
        return None
    ms = re.findall(r"Dispersion energy:\s+([-]?\d+\.\d+)", text)
    return float(ms[-1]) if ms else None


def synergy_from_corners(corners: dict[str, float], n_atoms: int) -> float:
    e_p0, e_p3, e_d0, e_d3 = (corners[k] for k in ("pristine_eps0", "pristine_eps3", "P_eps0", "P_eps3"))
    s_ha = (e_d3 - e_p0) - (e_p3 - e_p0) - (e_d0 - e_p0)
    return s_ha / n_atoms * HA_TO_MEV


def analyze_rigid_pbed3_tetramer() -> dict:
    d = REPO / "experiments/exp_5_synergy/relax_validation/rigid_pbed3/inputs"
    corners = {
        "pristine_eps0": parse_dispersion_ha(d / "rigid_pbed3_pristine_eps0_sp.out"),
        "pristine_eps3": parse_dispersion_ha(d / "rigid_pbed3_pristine_eps3_sp.out"),
        "P_eps0": parse_dispersion_ha(d / "rigid_pbed3_P_eps0_sp.out"),
        "P_eps3": parse_dispersion_ha(d / "rigid_pbed3_P_eps3_sp.out"),
    }
    if any(v is None for v in corners.values()):
        return {"system": "tetramer P rigid_pbed3", "status": "partial", "corners": corners}
    s_vdw = synergy_from_corners(corners, 240)
    return {
        "system": "tetramer P rigid_pbed3 (matched-functional four corners)",
        "n_atoms": 240,
        "status": "complete",
        "dispersion_ha_per_corner": corners,
        "S_vdW_meV_per_atom": s_vdw,
        "note": "D3 dispersion energy only; S_vdW uses same four-corner formula on Grimme terms",
    }


def main() -> None:
    report = {"analyses": [analyze_rigid_pbed3_tetramer()]}
    out = REPO / "experiments/analysis/s_vdw_decomposition.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
