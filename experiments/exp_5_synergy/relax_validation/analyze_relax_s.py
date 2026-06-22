#!/usr/bin/env python3
"""Compare tetramer synergy S: rigid (legacy PBE) vs ionic-relaxed (PBE+D3 GEO_OPT)."""

from __future__ import annotations

import json
import re
from pathlib import Path
import subprocess

HA_TO_MEV = 27.211386245988 * 1000.0
N_ATOMS = 240

REPO = Path(__file__).resolve().parents[3]
SYNERGY_DIR = REPO / "dft_results" / "exp_5_synergy"
RELAX_DIR = Path(__file__).resolve().parent / "inputs"
AUDIT_OUT = REPO / "experiments" / "analysis" / "relax_validation_tetramer.json"

RIGID_OUTS = {
    "pristine_eps0": "C60_strain_+0.0_pristine_synergy.out",
    "pristine_eps3": "C60_strain_+3.0_pristine_synergy.out",
    "P_eps0": "C60_strain_+0.0_P_doped_synergy.out",
    "P_eps3": "C60_strain_+3.0_P_doped_synergy.out",
}

RELAX_OUTS = {
    "pristine_eps0": "relax_pristine_eps0_geo.out",
    "pristine_eps3": "relax_pristine_eps3_geo.out",
    "P_eps0": "relax_P_eps0_geo.out",
    "P_eps3": "relax_P_eps3_geo.out",
}


def parse_energy_ha(path: Path, *, require_geo_complete: bool = False) -> float | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    geo_done = "GEOMETRY OPTIMIZATION COMPLETED" in text
    if require_geo_complete and not geo_done:
        return None
    if geo_done:
        m = re.findall(r"ENERGY\|\s*Total FORCE_EVAL.*?([-]?\d+\.\d+)", text)
        if m:
            return float(m[-1])
    if require_geo_complete:
        return None
    m = re.findall(r"ENERGY\|\s*Total FORCE_EVAL.*?([-]?\d+\.\d+)", text)
    if m:
        return float(m[-1])
    m = re.findall(r"Total FORCE_EVAL.*?([-]?\d+\.\d+)", text)
    return float(m[-1]) if m else None


def synergy_s(e_pri0, e_pri3, e_dop0, e_dop3, n_atoms=N_ATOMS):
    d_eps = (e_pri3 - e_pri0) / n_atoms
    d_dop = (e_dop0 - e_pri0) / n_atoms
    d_combined = (e_dop3 - e_pri0) / n_atoms
    s_ha = d_combined - d_eps - d_dop
    return {
        "S_ha_per_atom": s_ha,
        "S_meV_per_atom": s_ha * HA_TO_MEV,
        "delta_strain_ha": d_eps,
        "delta_doping_ha": d_dop,
        "delta_combined_ha": d_combined,
    }



def _running_snapshot(relax_dir: Path, mapping: dict[str, str]) -> dict:
    tasks = list(mapping.items())
    completed = sum(
        1
        for _, name in tasks
        if (relax_dir / name).exists()
        and "GEOMETRY OPTIMIZATION COMPLETED" in (relax_dir / name).read_text(errors="replace")
    )
    running_task = None
    try:
        out = subprocess.check_output(
            ["pgrep", "-lf", "cp2k.psmp.*relax_"], text=True, stderr=subprocess.DEVNULL
        )
        for line in out.splitlines():
            if "-i" in line:
                running_task = line.split("-i", 1)[1].strip().split()[0].replace(".inp", "")
                break
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    snap = {"geo_completed": completed, "geo_total": len(tasks), "running_task": running_task}
    if running_task:
        out_path = relax_dir / f"{running_task}.out"
        if out_path.exists():
            tail = out_path.read_text(errors="replace")[-120000:]
            ots = re.findall(r"^\s+(\d+)\s+OT\s", tail, re.M)
            grs = re.findall(r"OT\s+DIIS\s+[\d.E+-]+\s+[\d.E+-]+\s+([\d.E+-]+)", tail)
            if ots:
                snap["last_ot_step"] = int(ots[-1])
            if grs:
                snap["last_ot_grad_ha_bohr"] = float(grs[-1])
    pending = [
        k for k, name in tasks
        if not (
            (relax_dir / name).exists()
            and "GEOMETRY OPTIMIZATION COMPLETED" in (relax_dir / name).read_text(errors="replace")
        )
    ]
    snap["next_after_running"] = pending[0] if pending else None
    return snap


def load_corner_energies(base: Path, mapping: dict[str, str], *, require_geo_complete: bool = False):
    return {
        k: parse_energy_ha(base / name, require_geo_complete=require_geo_complete)
        for k, name in mapping.items()
    }


def main() -> None:
    rigid = load_corner_energies(SYNERGY_DIR, RIGID_OUTS)
    relaxed = load_corner_energies(RELAX_DIR, RELAX_OUTS, require_geo_complete=True)

    report = {
        "n_atoms": N_ATOMS,
        "dopant": "P",
        "strain_pct": 3.0,
        "rigid_protocol": "PBE without D3, rigid single-point total energy (archived tetramer synergy grid)",
        "relaxed_protocol": "PBE+D3, fixed-cell geometry optimization, 400 Ry cutoff",
        "scientific_note": "Rigid reference is legacy PBE without D3; |S_relaxed|/|S_rigid| is sign-qualitative only, not a quantitative retention ratio.",
        "quantitative_ratio_valid": False,
        "energies_ha": {"rigid": rigid, "relaxed": relaxed},
        "geo_opt_completed": {
            k: (RELAX_DIR / RELAX_OUTS[k]).exists()
            and "GEOMETRY OPTIMIZATION COMPLETED"
            in (RELAX_DIR / RELAX_OUTS[k]).read_text(errors="replace")
            for k in RELAX_OUTS
        },
        "running_snapshot": _running_snapshot(RELAX_DIR, RELAX_OUTS),
    }

    if all(rigid[k] is not None for k in rigid):
        report["S_rigid"] = synergy_s(
            rigid["pristine_eps0"],
            rigid["pristine_eps3"],
            rigid["P_eps0"],
            rigid["P_eps3"],
        )

    if all(relaxed[k] is not None for k in relaxed):
        report["S_relaxed"] = synergy_s(
            relaxed["pristine_eps0"],
            relaxed["pristine_eps3"],
            relaxed["P_eps0"],
            relaxed["P_eps3"],
        )
        if "S_rigid" in report:
            sr = report["S_rigid"]["S_meV_per_atom"]
            sl = report["S_relaxed"]["S_meV_per_atom"]
            report["delta_S_meV"] = sl - sr
            report["sign_preserved"] = (sr == 0) or (sr * sl > 0)

    AUDIT_OUT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
