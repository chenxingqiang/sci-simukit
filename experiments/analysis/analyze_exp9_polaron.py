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
TAIL_BYTES = 3_000_000


def read_out_tail(path: Path, max_bytes: int = TAIL_BYTES) -> str:
    """Read trailing bytes of a CP2K .out (fast path for running-job progress)."""
    with path.open("rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - max_bytes))
        return f.read().decode("utf-8", errors="ignore")

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



def parse_scf_progress(text: str) -> dict:
    """Last inner OT progress for ENERGY / vertical SP (no GEO_OPT steps)."""
    ot_lines = re.findall(
        r"^\s+(\d+)\s+OT (?:DIIS|SD)\s+\S+\s+\S+\s+([\d.E+-]+)\s+-?\d+\.\d+",
        text,
        re.MULTILINE,
    )
    last_ot = int(ot_lines[-1][0]) if ot_lines else None
    last_conv = float(ot_lines[-1][1]) if ot_lines else None
    return {
        "kind": "vertical_sp",
        "last_ot_step": last_ot,
        "last_ot_convergence": last_conv,
    }

def parse_geo_progress(text: str) -> dict:
    """Last GEO_OPT block progress from CP2K output (handles restarts after ABORT)."""
    abort_seen = "[ABORT]" in text
    # After ABORT restart, ignore pre-abort OPTIMIZATION STEP counts.
    segment = text.split("[ABORT]")[-1] if abort_seen else text
    geo_steps = re.findall(r"OPTIMIZATION STEP:\s+(\d+)", segment)
    geo_step = int(geo_steps[-1]) if geo_steps else None
    restarted_after_abort = bool(abort_seen and geo_step is not None)

    ot_lines = re.findall(
        r"^\s+(\d+)\s+OT (?:DIIS|SD)\s+\S+\s+\S+\s+([\d.E+-]+)\s+-?\d+\.\d+",
        segment,
        re.MULTILINE,
    )
    last_ot = int(ot_lines[-1][0]) if ot_lines else None
    last_conv = float(ot_lines[-1][1]) if ot_lines else None

    return {
        "geo_step": geo_step,
        "geo_max_iter": 300,
        "last_ot_step": last_ot,
        "last_ot_convergence": last_conv,
        "abort_seen": abort_seen,
        "restarted_after_abort": restarted_after_abort,
    }


def detect_running_task(candidates: list[str]) -> str | None:
    """Return polaron task stem if cp2k.psmp is running it; else first candidate."""
    import subprocess

    try:
        r = subprocess.run(
            ["pgrep", "-lf", "cp2k.psmp.*polaron_"],
            capture_output=True,
            text=True,
            check=False,
        )
        for line in r.stdout.splitlines():
            if "cp2k.psmp" not in line or "polaron_" not in line:
                continue
            parts = line.split(None, 1)[-1].split() if line else []
            for i, tok in enumerate(parts):
                if tok == "-i" and i + 1 < len(parts):
                    return Path(parts[i + 1]).stem
    except OSError:
        pass
    return candidates[0] if candidates else None


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
    text = read_out_tail(out_path)
    program_ended = "PROGRAM ENDED" in text
    if not program_ended:
        full = out_path.read_text(errors="ignore")
        program_ended = "PROGRAM ENDED" in full
        text = full
    return {
        "project": project,
        "out_exists": True,
        "program_ended": program_ended,
        "energy_ha": extract_energy(text),
        "xyz_exists": xyz_path.exists(),
    }



def load_vertical_sp(dopant: str, charge: int) -> dict:
    tag = charge_tag(charge)
    project = f"polaron_{dopant}_{tag}_vert_neutral_geom_sp"
    out_path = OUT_DIR / f"{project}.out"
    if not out_path.exists():
        return {"project": project, "out_exists": False, "scf_converged": False, "energy_ha": None}
    body = out_path.read_text(errors="ignore")
    return {
        "project": project,
        "out_exists": True,
        "scf_converged": "SCF run converged" in body,
        "energy_ha": extract_energy(body) if "SCF run converged" in body else None,
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
    vertical_done = sorted(
        p.stem
        for p in OUT_DIR.glob("polaron_*_vert_*.out")
        if "SCF run converged" in p.read_text(errors="ignore")
    )
    vertical_done_set = set(vertical_done)
    vertical_pending = (
        sorted(
            p.stem
            for p in vertical_dir.glob("*.inp")
            if p.stem not in vertical_done_set
        )
        if vertical_dir.exists()
        else []
    )

    lambda_eV: dict[str, dict[str, float | None]] = {}
    for dopant in DOPANTS:
        lambda_eV[dopant] = {"lambda_IP_eV": None, "lambda_EA_eV": None}
        adia1 = systems[dopant]["1"]
        adian = systems[dopant]["-1"]
        vert1 = load_vertical_sp(dopant, 1)
        vertn = load_vertical_sp(dopant, -1)
        if adia1["program_ended"] and adia1["energy_ha"] is not None and vert1["energy_ha"] is not None:
            lambda_eV[dopant]["lambda_IP_eV"] = (vert1["energy_ha"] - adia1["energy_ha"]) * HA_TO_EV
        if adian["program_ended"] and adian["energy_ha"] is not None and vertn["energy_ha"] is not None:
            lambda_eV[dopant]["lambda_EA_eV"] = (vertn["energy_ha"] - adian["energy_ha"]) * HA_TO_EV
    derived["lambda_eV"] = lambda_eV

    payload = {
        "source": str(OUT_DIR.relative_to(REPO)),
        "verified_date": date.today().isoformat(),
        "converged": converged,
        "total": total,
        "note": (
            "Adiabatic IP/EA from last GEO_OPT ENERGY line. "
            "Marcus lambda requires vertical ENERGY at neutral geometry "
            "(inputs/vertical/ -> dft_results/exp_9_charged_polaron/outputs/)."
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

    pending_vert = [x for x in vertical_pending if x not in vertical_done]
    candidates = payload["pending_geo_opt"] + pending_vert
    running = detect_running_task(candidates)
    if running:
        out_path = OUT_DIR / f"{running}.out"
        if out_path.exists():
            if "_vert_" in running:
                snap = parse_scf_progress(read_out_tail(out_path))
            else:
                snap = parse_geo_progress(read_out_tail(out_path))
                gs, gmax = snap.get("geo_step"), snap.get("geo_max_iter") or 300
                if gs is not None and gmax:
                    snap["geo_progress_pct"] = round(100.0 * gs / gmax, 1)
            snap["task"] = running
            payload["running_snapshot"] = snap
            payload["running_task"] = running

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
    n_lambda = sum(
        1
        for d in DOPANTS
        for k in ("lambda_IP_eV", "lambda_EA_eV")
        if derived["lambda_eV"][d][k] is not None
    )
    if n_lambda:
        print(f"Marcus lambda (vertical − adiabatic): {n_lambda} values")
        for dopant in DOPANTS:
            lam = derived["lambda_eV"][dopant]
            if lam["lambda_IP_eV"] is not None or lam["lambda_EA_eV"] is not None:
                ip_l = f"{lam['lambda_IP_eV']:.3f}" if lam["lambda_IP_eV"] is not None else "—"
                ea_l = f"{lam['lambda_EA_eV']:.3f}" if lam["lambda_EA_eV"] is not None else "—"
                print(f"  {dopant:8} λ_IP={ip_l} eV  λ_EA={ea_l} eV")
    snap = payload.get("running_snapshot")
    if snap:
        print(
            f"  running={snap['task']} step={snap.get('geo_step')}/{snap.get('geo_max_iter')} "
            f"OT={snap.get('last_ot_step')} abort={snap.get('abort_seen')} restarted={snap.get('restarted_after_abort')}"
        )
    print(f"Wrote {out_json.relative_to(REPO)}")


if __name__ == "__main__":
    main()
