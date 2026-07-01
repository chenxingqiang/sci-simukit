#!/usr/bin/env python3
"""Parse seed137 ENERGY outputs; compare alpha and tetramer S vs seed 42."""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
INP_DIR = Path(__file__).resolve().parent / "inputs"
OUT_JSON = REPO / "experiments/analysis/seed_validation_tetramer.json"
TABLE1 = REPO / "experiments/analysis/table1_verification.json"
N_ATOMS = 240
HA_TO_MEV = 27.2114e3


def parse_energy(out: Path) -> float | None:
    if not out.exists():
        return None
    text = out.read_text(errors="replace")
    if "SCF run converged" not in text:
        return None
    m = re.findall(r"ENERGY\| Total FORCE_EVAL.*?(-?\d+\.\d+)", text)
    return float(m[-1]) if m else None


def synergy_s(e_p0: float, e_p3: float, e_d0: float, e_d3: float) -> float:
    delta_strain = e_p3 - e_p0
    delta_dop = e_d0 - e_p0
    delta_combined = e_d3 - e_p0
    return (delta_combined - delta_strain - delta_dop) / N_ATOMS * HA_TO_MEV


def fit_alpha(strains: list[float], energies: list[float]) -> float | None:
    if len(strains) < 3:
        return None
    c = np.polyfit(strains, energies, 1)
    return float(c[0] * HA_TO_MEV)


def parse_scf_tail(out: Path) -> tuple[str | None, str | None]:
    if not out.exists():
        return None, None
    text = out.read_text(errors="replace")
    if "PROGRAM STARTED" in text:
        text = text.split("PROGRAM STARTED")[-1]
    text = text[-80000:]
    ots = re.findall(r"^\s+(\d+)\s+OT\s", text, re.M)
    grs = re.findall(
        r"OT\s+(?:SD|DIIS|CG|BROYDEN)\s+[\d.E+-]+\s+[\d.E+-]+\s+([\d.E+-]+)",
        text,
    )
    if not grs:
        rms = re.findall(r"outer SCF iter =\s+\d+\s+RMS gradient =\s+([\d.E+-]+)", text)
        grs = rms
    return (ots[-1] if ots else None, grs[-1] if grs else None)


def parse_outer_scf(out: Path) -> tuple[int | None, float | None]:
    if not out.exists():
        return None, None
    text = out.read_text(errors="replace")
    if "PROGRAM STARTED" in text:
        text = text.split("PROGRAM STARTED")[-1]
    text = text[-120000:]
    outers = re.findall(
        r"outer SCF iter =\s+(\d+)\s+RMS gradient =\s+([\d.E+-]+)",
        text,
    )
    if not outers:
        return None, None
    it, gr = outers[-1]
    return int(it), float(gr)


def eps_scf_from_inp(inp: Path) -> float:
    if not inp.exists():
        return 1e-6
    m = re.search(r"EPS_SCF\s+([\d.E+-]+)", inp.read_text(errors="replace"))
    return float(m.group(1)) if m else 1e-6


def max_inner_ot_from_inp(inp: Path) -> int:
    if not inp.exists():
        return 300
    m = re.search(r"MAX_SCF\s+(\d+)", inp.read_text(errors="replace"))
    return int(m.group(1)) if m else 300


def main() -> None:
    seed42 = json.loads(TABLE1.read_text())["systems"]
    result = {
        "seed_primary": 42,
        "seed_validation": 137,
        "status": "pending",
        "functional_note": "Seed137 inputs use PBE+D3 (modernize_cp2k_inp); compare only after modern pristine outs exist.",
        "tetramer_alpha_meV_per_pct": {"seed42": {}, "seed137": {}},
        "tetramer_S_meV_per_atom_at_eps3": {"seed42": {}, "seed137": {}},
        "relative_deviation_pct": {},
    }
    for dop in ("B", "N", "P"):
        result["tetramer_alpha_meV_per_pct"]["seed42"][dop] = seed42[dop]["alpha_meV_per_pct"]

    by_dop: dict[str, dict[float, float]] = {d: {} for d in ("B", "N", "P")}
    for inp in sorted(INP_DIR.glob("seed137_*_rigid.inp")):
        m = re.search(r"seed137_([BNP])_strain([pm])(\d+\.\d)_rigid", inp.stem)
        if not m:
            continue
        dop, sign, val = m.group(1), m.group(2), m.group(3)
        strain = float(val) if sign == "p" else -float(val)
        e = parse_energy(inp.with_suffix(".out"))
        if e is not None:
            by_dop[dop][strain] = e

    def strain_tag(strain: float) -> str:
        return f"strain{strain:+.1f}_rigid".replace("+", "p").replace("-", "m")

    pristine: dict[float, float] = {}
    pristine_protocol = "legacy_pbe_no_d3"
    for strain in (-5.0, -2.5, 0.0, 2.5, 3.0, 5.0):
        modern = INP_DIR / f"seed137_pristine_{strain_tag(strain)}.out"
        legacy = REPO / "dft_results/exp_5_synergy" / f"C60_strain_{strain:+.1f}_pristine_synergy.out"
        e = parse_energy(modern) if modern.exists() else None
        if e is not None:
            pristine_protocol = "pbe_d3_modern"
        else:
            e = parse_energy(legacy)
        if e is not None:
            pristine[strain] = e
    result["pristine_energy_protocol"] = pristine_protocol

    converged = sum(len(v) for v in by_dop.values())
    pri_conv = sum(
        1
        for strain in (-5.0, -2.5, 0.0, 2.5, 3.0, 5.0)
        if parse_energy(INP_DIR / f"seed137_pristine_{strain_tag(strain)}.out") is not None
    )
    running = None
    try:
        import subprocess

        ps = subprocess.run(
            ["pgrep", "-lf", "cp2k.psmp.*seed137_"],
            capture_output=True,
            text=True,
        )
        if ps.stdout.strip():
            for line in ps.stdout.strip().splitlines():
                if "-i" in line:
                    parts = line.split()
                    idx = parts.index("-i")
                    running = Path(parts[idx + 1]).stem
                    break
    except Exception:
        pass
    result["running_snapshot"] = {
        "dop_converged": converged,
        "dop_total": 18,
        "pristine_modern_converged": pri_conv,
        "pristine_modern_total": 6,
        "running_task": running,
    }
    if running:
        ot, grad = parse_scf_tail(INP_DIR / f"{running}.out")
        if ot is not None:
            oti = int(ot)
            result["running_snapshot"]["last_ot"] = oti
            cap = max_inner_ot_from_inp(INP_DIR / f"{running}.inp")
            result["running_snapshot"]["max_inner_ot"] = cap
            result["running_snapshot"]["ot_progress_pct"] = round(100 * oti / cap, 1) if cap else None
            if oti >= max(250, cap - 50):
                result["running_snapshot"]["escalation_hint"] = (
                    "inner OT near MAX_SCF; if ABORT retry EPS_SCF=1e-5 or archive+continue"
                )
        outer_it, outer_rms = parse_outer_scf(INP_DIR / f"{running}.out")
        if outer_it is not None:
            result["running_snapshot"]["outer_scf_iter"] = outer_it
        if outer_rms is not None:
            result["running_snapshot"]["outer_rms_grad_Ha_bohr"] = outer_rms
        if grad is not None:
            g = float(grad)
            result["running_snapshot"]["last_grad_Ha_bohr"] = g
            eps = eps_scf_from_inp(INP_DIR / f"{running}.inp")
            result["running_snapshot"]["eps_scf"] = eps
            ratio = g / eps if eps else None
            if ratio is not None:
                result["running_snapshot"]["grad_ratio_to_eps"] = round(ratio, 1)
                if ratio <= 15:
                    result["running_snapshot"]["critical_zone"] = True
    result["strain_points_per_dop"] = {d: len(by_dop[d]) for d in ("B", "N", "P")}
    result["alpha_provisional"] = {
        d: len(by_dop[d]) < 6 for d in ("B", "N", "P")
    }
    for dop in ("B", "N", "P"):
        strains = sorted(by_dop[dop].keys())
        es = [by_dop[dop][s] for s in strains]
        result["tetramer_alpha_meV_per_pct"]["seed137"][dop] = fit_alpha(strains, es)
        if 0.0 in pristine and 3.0 in pristine and 0.0 in by_dop[dop] and 3.0 in by_dop[dop]:
            s = synergy_s(pristine[0.0], pristine[3.0], by_dop[dop][0.0], by_dop[dop][3.0])
            result["tetramer_S_meV_per_atom_at_eps3"]["seed137"][dop] = round(s, 2)
        a42 = result["tetramer_alpha_meV_per_pct"]["seed42"][dop]
        a137 = result["tetramer_alpha_meV_per_pct"]["seed137"].get(dop)
        if a42 and a137 and abs(a42) > 1e-6:
            result["relative_deviation_pct"][f"alpha_{dop}"] = round(100 * (a137 - a42) / abs(a42), 1)

    if converged >= 18:
        result["status"] = "complete"
    elif converged > 0:
        result["status"] = "partial"

    OUT_JSON.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Wrote {OUT_JSON} converged_points={converged}")


if __name__ == "__main__":
    main()
