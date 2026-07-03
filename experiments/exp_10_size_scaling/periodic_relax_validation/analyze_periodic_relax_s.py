#!/usr/bin/env python3
"""Periodic n=1 P: rigid vs ionic-relaxed synergy S (PBE+D3 four corners)."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

HA_TO_MEV = 27.211386245988 * 1000.0
N_ATOMS = 60
REPO = Path(__file__).resolve().parents[3]
INP_DIR = Path(__file__).resolve().parent / "inputs"
SDC_JSON = REPO / "experiments/analysis/sdc/sdc_exp10_results.json"
OUT_JSON = REPO / "experiments/analysis/periodic_relax_validation_n1_P.json"

GEO_OUTS = {
    "pristine_eps0": "per_relax_n1_pristine_eps0_geo.out",
    "pristine_eps3": "per_relax_n1_pristine_eps3_geo.out",
    "P_eps0": "per_relax_n1_P_eps0_geo.out",
    "P_eps3": "per_relax_n1_P_eps3_geo.out",
}


def parse_geo_energy_ha(path: Path) -> float | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    if "GEOMETRY OPTIMIZATION COMPLETED" not in text:
        return None
    m = re.findall(r"ENERGY\|\s*Total FORCE_EVAL.*?([-]?\d+\.\d+)", text)
    return float(m[-1]) if m else None


def rigid_corners_from_sdc() -> dict[str, float] | None:
    if not SDC_JSON.exists():
        return None
    data = json.loads(SDC_JSON.read_text())
    p_row = next(
        (
            r
            for r in data.get("synergy_energy_per_atom", [])
            if r.get("n_molecules") == 1 and r.get("dopant") == "P" and r.get("strain_pct") == 3.0
        ),
        None,
    )
    if not p_row:
        return None
    ref = float(p_row["reference"])
    d_eps = float(p_row["strain_only_delta"])
    d_dop = float(p_row["doping_only_delta"])
    comb = float(p_row["combined"])
    return {
        "pristine_eps0": ref * N_ATOMS,
        "pristine_eps3": (ref + d_eps) * N_ATOMS,
        "P_eps0": (ref + d_dop) * N_ATOMS,
        "P_eps3": comb * N_ATOMS,
    }


def synergy_s(e_pri0, e_pri3, e_dop0, e_dop3, n_atoms=N_ATOMS):
    d_eps = (e_pri3 - e_pri0) / n_atoms
    d_dop = (e_dop0 - e_pri0) / n_atoms
    d_combined = (e_dop3 - e_pri0) / n_atoms
    s_ha = d_combined - d_eps - d_dop
    return {
        "S_ha_per_atom": s_ha,
        "S_meV_per_atom": s_ha * HA_TO_MEV,
    }


def _running_snapshot() -> dict:
    snap: dict = {"running_task": None}
    try:
        out = subprocess.check_output(
            ["pgrep", "-lf", "cp2k.psmp.*per_relax_n1"], text=True, stderr=subprocess.DEVNULL
        )
        for line in out.splitlines():
            if "-i" in line:
                snap["running_task"] = line.split("-i", 1)[1].strip().split()[0].replace(".inp", "")
                break
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return snap


def main() -> None:
    rigid = rigid_corners_from_sdc()
    relaxed = {k: parse_geo_energy_ha(INP_DIR / v) for k, v in GEO_OUTS.items()}
    geo_done = sum(1 for v in relaxed.values() if v is not None)

    report: dict = {
        "system": "periodic 1xC60 P substitutional",
        "n_atoms": N_ATOMS,
        "functional": "PBE+D3",
        "protocol": "fixed-cell GEO_OPT",
        "geo_completed": geo_done,
        "geo_total": 4,
        "status": "complete" if geo_done == 4 else ("partial" if geo_done else "pending"),
        "running_snapshot": _running_snapshot(),
        "corners": {},
    }

    if rigid:
        s_rig = synergy_s(
            rigid["pristine_eps0"],
            rigid["pristine_eps3"],
            rigid["P_eps0"],
            rigid["P_eps3"],
        )
        report["S_rigid"] = {
            **s_rig,
            "source": "rigid fixed-coordinates SP (SDC audit n=1 P @ +3%)",
            "energies_ha": rigid,
        }

    if geo_done == 4:
        s_rel = synergy_s(
            relaxed["pristine_eps0"],
            relaxed["pristine_eps3"],
            relaxed["P_eps0"],
            relaxed["P_eps3"],
        )
        report["S_relaxed"] = {**s_rel, "energies_ha": relaxed}
        if rigid and s_rig["S_meV_per_atom"] != 0:
            report["retention"] = {
                "ratio_abs": abs(s_rel["S_meV_per_atom"]) / abs(s_rig["S_meV_per_atom"]),
                "sign_preserved": (s_rig["S_meV_per_atom"] * s_rel["S_meV_per_atom"]) > 0,
            }

    for k in GEO_OUTS:
        report["corners"][k] = {
            "relaxed_energy_ha": relaxed.get(k),
            "geo_converged": relaxed.get(k) is not None,
        }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
