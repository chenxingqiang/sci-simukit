#!/usr/bin/env python3
"""Audit Exp9 charged-polaron GEO_OPT outputs and write verification JSON."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

HA_TO_EV = 27.2114
REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "dft_results" / "exp_9_charged_polaron" / "outputs"
ANALYSIS_DIR = REPO / "experiments" / "analysis"

DOPANTS = ("pristine", "N", "B", "P")
CHARGES = (0, 1, -1)


def charge_tag(charge: int) -> str:
    if charge == 0:
        return "qpos0"
    if charge == 1:
        return "qpos1"
    return "qneg1"


def extract_energy(text: str) -> float | None:
    matches = re.findall(r"ENERGY\|\ Total FORCE_EVAL.*?(-?\d+\.\d+)", text)
    return float(matches[-1]) if matches else None


def load_run(dopant: str, charge: int) -> dict:
    project = f"polaron_{dopant}_{charge_tag(charge)}_opt"
    out_path = OUT_DIR / f"{project}.out"
    xyz_path = OUT_DIR / f"{project}-pos-1.xyz"
    if not out_path.exists():
        return {
            "project": project,
            "out_exists": False,
            "program_ended": False,
            "energy_ha": None,
            "xyz_exists": xyz_path.exists(),
        }
    text = out_path.read_text(errors="ignore")
    return {
        "project": project,
        "out_exists": True,
        "program_ended": "PROGRAM ENDED" in text,
        "energy_ha": extract_energy(text),
        "xyz_exists": xyz_path.exists(),
    }


def main() -> None:
    systems: dict[str, dict] = {}
    converged = 0
    total = len(DOPANTS) * len(CHARGES)

    for dopant in DOPANTS:
        systems[dopant] = {}
        for charge in CHARGES:
            run = load_run(dopant, charge)
            systems[dopant][str(charge)] = run
            if run["program_ended"] and run["energy_ha"] is not None:
                converged += 1

    derived: dict[str, object] = {"adiabatic_eV": {}, "fundamental_gap_eV": {}}
    for dopant in DOPANTS:
        ok = {
            int(q): systems[dopant][q]
            for q in ("0", "1", "-1")
            if systems[dopant][q]["program_ended"] and systems[dopant][q]["energy_ha"] is not None
        }
        block: dict[str, float | None] = {"IP": None, "EA": None}
        if 0 in ok and 1 in ok:
            block["IP"] = (ok[1]["energy_ha"] - ok[0]["energy_ha"]) * HA_TO_EV
        if 0 in ok and -1 in ok:
            block["EA"] = (ok[0]["energy_ha"] - ok[-1]["energy_ha"]) * HA_TO_EV
        derived["adiabatic_eV"][dopant] = block
        if block["IP"] is not None and block["EA"] is not None:
            derived["fundamental_gap_eV"][dopant] = block["IP"] - block["EA"]

    vertical_dir = REPO / "experiments" / "exp_9_charged_polaron" / "inputs" / "vertical"
    vertical_pending = sorted(p.stem for p in vertical_dir.glob("*.inp")) if vertical_dir.exists() else []
    vertical_done = sorted(
        p.stem.replace("_sp", "")
        for p in OUT_DIR.glob("polaron_*_vert_*.out")
        if "PROGRAM ENDED" in p.read_text(errors="ignore")
    )

    payload = {
        "source": str(OUT_DIR.relative_to(REPO)),
        "verified_date": date.today().isoformat(),
        "converged": converged,
        "total": total,
        "note": (
            "Adiabatic IP/EA from last GEO_OPT ENERGY line. "
            "Marcus lambda requires vertical ENERGY at neutral geometry "
            "(inputs/vertical/, not yet in outputs)."
        ),
        "systems": systems,
        "derived": derived,
        "vertical_sp": {
            "inputs_dir": str(vertical_dir.relative_to(REPO)) if vertical_dir.exists() else None,
            "inputs_pending": vertical_pending,
            "outputs_converged": vertical_done,
        },
        "pending_geo_opt": [
            systems[d][str(c)]["project"]
            for d in DOPANTS
            for c in CHARGES
            if not systems[d][str(c)]["program_ended"]
        ],
    }

    out_json = ANALYSIS_DIR / "exp9_polaron_verification.json"
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2) + "\n")

    print(f"Exp9 GEO_OPT: {converged}/{total} PROGRAM ENDED with energy")
    for dopant in DOPANTS:
        ad = derived["adiabatic_eV"][dopant]
        ip = ad["IP"]
        ea = ad["EA"]
        if ip is not None or ea is not None:
            ip_s = f"{ip:.3f}" if ip is not None else "—"
            ea_s = f"{ea:.3f}" if ea is not None else "—"
            print(f"  {dopant:8} IP={ip_s} eV  EA={ea_s} eV")
    print(f"Wrote {out_json.relative_to(REPO)}")


if __name__ == "__main__":
    main()
