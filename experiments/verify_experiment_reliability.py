#!/usr/bin/env python3
"""
Three-layer experiment reliability audit: SETUP (inp + coordinates) → PROCESS (workflow) → RESULTS (outputs).

Usage:
  python3 experiments/verify_experiment_reliability.py
  python3 experiments/verify_experiment_reliability.py --json experiments/analysis/reliability_audit.json

Exit code: 0 if no FAIL; 1 if any FAIL (WARN alone does not fail).
"""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HA_TO_EV = 27.2114
EXP9_NATOMS = 120
EXP9_DOPANT_SPEC = {
    "pristine": {"C": 120},
    "B": {"C": 116, "B": 4},
    "N": {"C": 116, "N": 4},
    "P": {"C": 116, "P": 4},
}
EXP9_CHARGE_TAG = {"qpos0": 0, "qpos1": 1, "qneg1": -1}
TETRAMER_NATOMS = 240
TETRAMER_A0 = 28.52
STRAIN_POS3_RATIO = 1.03
CELL_TOL = 0.02
RMSD_WARN_A = 2.0


@dataclass
class Check:
    layer: str  # setup | process | result
    check_id: str
    status: str  # pass | warn | fail
    message: str
    evidence: str = ""


def add(checks: list[Check], layer: str, cid: str, status: str, msg: str, evidence: str = "") -> None:
    checks.append(Check(layer, cid, status, msg, evidence))


def read_inp(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def inp_has(text: str, *patterns: str) -> bool:
    return all(p in text for p in patterns)


def parse_energy_from_out(path: Path, *, geo: bool = False) -> float | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    if geo and "GEOMETRY OPTIMIZATION COMPLETED" not in text and "PROGRAM ENDED" not in text:
        return None
    if not geo and "SCF run converged" not in text:
        return None
    m = re.findall(r"ENERGY\|\s*Total FORCE_EVAL.*?(-?\d+\.\d+)", text)
    return float(m[-1]) if m else None


def parse_inp_coord_block(text: str) -> list[tuple[str, float, float, float]]:
    m = re.search(r"&COORD\n(.*?)\n\s*&END COORD", text, re.S)
    if not m:
        return []
    atoms: list[tuple[str, float, float, float]] = []
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 4:
            atoms.append((parts[0], float(parts[1]), float(parts[2]), float(parts[3])))
    return atoms


def parse_inp_cell_abc(text: str) -> tuple[float, float, float] | None:
    m = re.search(r"ABC\s+([\d.Ee+-]+)\s+([\d.Ee+-]+)\s+([\d.Ee+-]+)", text)
    if m:
        return float(m.group(1)), float(m.group(2)), float(m.group(3))
    ma = re.search(r"^\s*A\s+([\d.Ee+-]+)\s+([\d.Ee+-]+)\s+([\d.Ee+-]+)", text, re.M)
    mb = re.search(r"^\s*B\s+([\d.Ee+-]+)\s+([\d.Ee+-]+)\s+([\d.Ee+-]+)", text, re.M)
    mc = re.search(r"^\s*C\s+([\d.Ee+-]+)\s+([\d.Ee+-]+)\s+([\d.Ee+-]+)", text, re.M)
    if ma and mb and mc:
        return abs(float(ma.group(1))), abs(float(mb.group(2))), abs(float(mc.group(3)))
    return None


def parse_inp_charge(text: str) -> int | None:
    m = re.search(r"CHARGE\s+(-?\d+)", text)
    return int(m.group(1)) if m else None


def element_counts(atoms: list[tuple[str, float, float, float]]) -> Counter[str]:
    return Counter(el for el, *_ in atoms)


def parse_xyz_last_frame(path: Path) -> list[tuple[str, float, float, float]] | None:
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    frames: list[list[tuple[str, float, float, float]]] = []
    idx = 0
    while idx < len(lines):
        if not lines[idx].strip():
            idx += 1
            continue
        try:
            nat = int(lines[idx].strip())
        except ValueError:
            idx += 1
            continue
        atoms: list[tuple[str, float, float, float]] = []
        for j in range(idx + 2, idx + 2 + nat):
            if j >= len(lines):
                break
            parts = lines[j].split()
            if len(parts) >= 4:
                atoms.append((parts[0], float(parts[1]), float(parts[2]), float(parts[3])))
        if len(atoms) == nat:
            frames.append(atoms)
        idx += 2 + nat
    return frames[-1] if frames else None


def coord_rmsd(
    a: list[tuple[str, float, float, float]],
    b: list[tuple[str, float, float, float]],
) -> float | None:
    if len(a) != len(b):
        return None
    for (ea, *_), (eb, *_) in zip(a, b):
        if ea != eb:
            return None
    acc = 0.0
    for (_, x1, y1, z1), (_, x2, y2, z2) in zip(a, b):
        acc += (x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2
    return math.sqrt(acc / len(a))


def strain_from_seed_tag(name: str) -> float | None:
    m = re.search(r"strain([pm])(\d+\.\d+)", name)
    if not m:
        return None
    val = float(m.group(2))
    return val if m.group(1) == "p" else -val


def audit_coordinates(checks: list[Check]) -> None:
    """Coordinate / cell / composition checks (subset of SETUP layer)."""
    exp9_inp = REPO / "experiments/exp_9_charged_polaron/inputs"
    exp9_out = REPO / "dft_results/exp_9_charged_polaron/outputs"

    for dop in ("pristine", "N", "B", "P"):
        ref_coords: list[tuple[str, float, float, float]] | None = None
        ref_cell: tuple[float, float, float] | None = None
        for ch in ("qpos0", "qpos1", "qneg1"):
            p = exp9_inp / f"polaron_{dop}_{ch}_opt.inp"
            if not p.exists():
                continue
            t = read_inp(p)
            atoms = parse_inp_coord_block(t)
            cell = parse_inp_cell_abc(t)
            charge = parse_inp_charge(t)
            expect_ch = EXP9_CHARGE_TAG[ch]
            counts = element_counts(atoms)
            nat_ok = len(atoms) == EXP9_NATOMS
            spec = EXP9_DOPANT_SPEC[dop]
            comp_ok = all(counts.get(el, 0) == n for el, n in spec.items())
            ch_ok = charge == expect_ch

            add(
                checks,
                "setup",
                f"coord_exp9_natoms_{dop}_{ch}",
                "pass" if nat_ok else "fail",
                f"{len(atoms)} atoms (expect {EXP9_NATOMS})",
                str(p.relative_to(REPO)),
            )
            add(
                checks,
                "setup",
                f"coord_exp9_composition_{dop}_{ch}",
                "pass" if comp_ok else "fail",
                f"elements {dict(counts)} expect {spec}",
                str(p.relative_to(REPO)),
            )
            add(
                checks,
                "setup",
                f"coord_exp9_charge_{dop}_{ch}",
                "pass" if ch_ok else "fail",
                f"CHARGE {charge} expect {expect_ch}",
                str(p.relative_to(REPO)),
            )
            if ref_coords is None:
                ref_coords = atoms
                ref_cell = cell
            else:
                same = atoms == ref_coords
                add(
                    checks,
                    "setup",
                    f"coord_exp9_initial_same_{dop}_{ch}",
                    "pass" if same else "fail",
                    f"initial COORD identical to qpos0 for {dop}",
                    str(p.relative_to(REPO)),
                )
                if cell and ref_cell:
                    cell_match = all(abs(a - b) < 1e-4 for a, b in zip(cell, ref_cell))
                    add(
                        checks,
                        "setup",
                        f"coord_exp9_cell_same_{dop}_{ch}",
                        "pass" if cell_match else "fail",
                        f"cell {cell} vs qpos0 {ref_cell}",
                    )

        qpos0_xyz = exp9_out / f"polaron_{dop}_qpos0_opt-pos-1.xyz"
        if qpos0_xyz.exists():
            xyz_atoms = parse_xyz_last_frame(qpos0_xyz)
            if xyz_atoms:
                xyz_ok = len(xyz_atoms) == EXP9_NATOMS
                xyz_comp = all(
                    element_counts(xyz_atoms).get(el, 0) == n for el, n in EXP9_DOPANT_SPEC[dop].items()
                )
                add(
                    checks,
                    "setup",
                    f"coord_exp9_qpos0_xyz_{dop}",
                    "pass" if xyz_ok and xyz_comp else "fail",
                    f"optimized xyz {len(xyz_atoms)} atoms elements {dict(element_counts(xyz_atoms))}",
                    str(qpos0_xyz.relative_to(REPO)),
                )
                out_path = exp9_out / f"polaron_{dop}_qpos0_opt.out"
                if out_path.exists() and "PROGRAM ENDED" in out_path.read_text(errors="ignore"):
                    inp_atoms = parse_inp_coord_block(read_inp(exp9_inp / f"polaron_{dop}_qpos0_opt.inp"))
                    rmsd = coord_rmsd(inp_atoms, xyz_atoms)
                    if rmsd is not None:
                        add(
                            checks,
                            "setup",
                            f"coord_exp9_geo_displacement_{dop}",
                            "pass" if rmsd < RMSD_WARN_A else "warn",
                            f"GEO_OPT RMSD vs initial inp = {rmsd:.3f} Å",
                            str(qpos0_xyz.relative_to(REPO)),
                        )

    vert_dir = exp9_inp / "vertical"
    if vert_dir.is_dir():
        for inp in sorted(vert_dir.glob("polaron_*_vert_*.inp")):
            t = read_inp(inp)
            m = re.search(r"COORD_FILE_NAME\s+(\S+)", t)
            if not m:
                continue
            rel = m.group(1).replace("../../../../", "")
            xyz_path = REPO / rel
            xyz_atoms = parse_xyz_last_frame(xyz_path)
            vert_cell = parse_inp_cell_abc(t)
            parts = inp.stem.split("_")
            dop = parts[1]
            qtag = parts[2]
            expect_ch = 1 if qtag == "qpos1" else -1
            vert_ch = parse_inp_charge(t)
            qpos0_inp = exp9_inp / f"polaron_{dop}_qpos0_opt.inp"
            qpos0_cell = parse_inp_cell_abc(read_inp(qpos0_inp)) if qpos0_inp.exists() else None

            if xyz_atoms:
                add(
                    checks,
                    "setup",
                    f"coord_exp9_vert_xyz_natoms_{inp.stem}",
                    "pass" if len(xyz_atoms) == EXP9_NATOMS else "fail",
                    f"vertical xyz {len(xyz_atoms)} atoms",
                    rel,
                )
            if vert_ch is not None:
                add(
                    checks,
                    "setup",
                    f"coord_exp9_vert_charge_{inp.stem}",
                    "pass" if vert_ch == expect_ch else "fail",
                    f"vertical CHARGE {vert_ch} expect {expect_ch}",
                    str(inp.relative_to(REPO)),
                )
            if vert_cell and qpos0_cell:
                match = all(abs(a - b) < 1e-4 for a, b in zip(vert_cell, qpos0_cell))
                add(
                    checks,
                    "setup",
                    f"coord_exp9_vert_cell_{inp.stem}",
                    "pass" if match else "fail",
                    f"vertical cell {vert_cell} vs qpos0 {qpos0_cell}",
                    str(inp.relative_to(REPO)),
                )

    exp10 = REPO / "experiments/exp_10_size_scaling/inputs"
    pos0_cells: dict[str, tuple[float, float, float]] = {}
    for inp in sorted(exp10.glob("size_*_pos0pct.inp")):
        key = inp.name.replace("_pos0pct.inp", "")
        cell = parse_inp_cell_abc(read_inp(inp))
        if cell:
            pos0_cells[key] = cell
        n = int(inp.name.split("_")[1].replace("x60", ""))
        atoms = parse_inp_coord_block(read_inp(inp))
        expect_nat = n * 60
        add(
            checks,
            "setup",
            f"coord_exp10_natoms_{inp.stem}",
            "pass" if len(atoms) == expect_nat else "fail",
            f"{len(atoms)} atoms expect {expect_nat} ({n}×C60)",
            str(inp.relative_to(REPO)),
        )

    for inp in sorted(exp10.glob("size_*_pos3pct*.inp")):
        key = inp.name.replace("_pos3pct.inp", "").replace("_pos3pct_cutoff400.inp", "")
        ref = pos0_cells.get(key)
        cell = parse_inp_cell_abc(read_inp(inp))
        if not ref or not cell:
            add(checks, "setup", f"coord_exp10_strain_{inp.stem}", "warn", "no pos0pct reference cell")
            continue
        ratios = [cell[i] / ref[i] if ref[i] > 1e-6 else 1.0 for i in range(3)]
        in_plane = [ratios[0], ratios[1]]
        ok = all(abs(r - STRAIN_POS3_RATIO) < CELL_TOL for r in in_plane) and abs(ratios[2] - 1.0) < CELL_TOL
        add(
            checks,
            "setup",
            f"coord_exp10_strain_cell_{inp.stem}",
            "pass" if ok else "fail",
            f"cell ratios a,b,c = {ratios[0]:.4f},{ratios[1]:.4f},{ratios[2]:.4f} vs +3% biaxial",
            str(inp.relative_to(REPO)),
        )

    seed_dir = REPO / "experiments/exp_5_synergy/seed_validation/inputs"
    ref_counts: dict[str, Counter[str]] = {}
    for inp in sorted(seed_dir.glob("seed137_*_strain*_rigid.inp")):
        atoms = parse_inp_coord_block(read_inp(inp))
        nat_ok = len(atoms) == TETRAMER_NATOMS
        add(
            checks,
            "setup",
            f"coord_seed137_natoms_{inp.stem}",
            "pass" if nat_ok else "fail",
            f"{len(atoms)} atoms expect {TETRAMER_NATOMS}",
            str(inp.relative_to(REPO)),
        )
        strain = strain_from_seed_tag(inp.name)
        cell = parse_inp_cell_abc(read_inp(inp))
        if strain is not None and cell:
            expect_a = TETRAMER_A0 * (1.0 + strain / 100.0)
            a_ok = abs(cell[0] - expect_a) < 0.02
            add(
                checks,
                "setup",
                f"coord_seed137_cell_{inp.stem}",
                "pass" if a_ok else "fail",
                f"A={cell[0]:.4f} expect {expect_a:.4f} ({strain:+.1f}% biaxial)",
                str(inp.relative_to(REPO)),
            )
        dop_key = "pristine"
        for d in ("B", "N", "P"):
            if f"seed137_{d}_" in inp.name:
                dop_key = d
        counts = element_counts(atoms)
        if dop_key not in ref_counts:
            ref_counts[dop_key] = counts
        else:
            same = counts == ref_counts[dop_key]
            add(
                checks,
                "setup",
                f"coord_seed137_composition_consistent_{inp.stem}",
                "pass" if same else "fail",
                f"composition {dict(counts)} vs reference {dict(ref_counts[dop_key])}",
                str(inp.relative_to(REPO)),
            )

    relax_dir = REPO / "experiments/exp_5_synergy/relax_validation/inputs"
    for inp in relax_dir.glob("relax_*_geo.inp"):
        atoms = parse_inp_coord_block(read_inp(inp))
        add(
            checks,
            "setup",
            f"coord_relax_natoms_{inp.stem}",
            "pass" if len(atoms) == TETRAMER_NATOMS else "fail",
            f"{len(atoms)} atoms expect tetramer {TETRAMER_NATOMS}",
            str(inp.relative_to(REPO)),
        )


def audit_setup(checks: list[Check]) -> None:
    """Layer A: input files match declared scientific protocol."""
    exp9_inp = REPO / "experiments/exp_9_charged_polaron/inputs"
    for dop in ("pristine", "N", "B", "P"):
        for ch in ("qpos0", "qpos1", "qneg1"):
            p = exp9_inp / f"polaron_{dop}_{ch}_opt.inp"
            if not p.exists():
                add(checks, "setup", f"exp9_geo_inp_{dop}_{ch}", "fail", "missing GEO_OPT inp", str(p))
                continue
            t = read_inp(p)
            ok = inp_has(t, "DFTD3", "CUTOFF 400", "EPS_SCF 1.0E-6", "RUN_TYPE GEO_OPT")
            add(
                checks,
                "setup",
                f"exp9_geo_contract_{dop}_{ch}",
                "pass" if ok else "fail",
                "GEO_OPT PBE+D3 400 Ry EPS 1e-6" if ok else "GEO_OPT inp contract violation",
                str(p.relative_to(REPO)),
            )

    vert_dir = exp9_inp / "vertical"
    if vert_dir.is_dir():
        for inp in sorted(vert_dir.glob("polaron_*_vert_*.inp")):
            t = read_inp(inp)
            eps = "1.0E-6" if "B_qneg1" in inp.name else "1.0E-7"
            ok = inp_has(t, "DFTD3", "CUTOFF 400", f"EPS_SCF {eps}", "RUN_TYPE ENERGY")
            add(
                checks,
                "setup",
                f"exp9_vert_contract_{inp.stem}",
                "pass" if ok else "fail",
                f"vertical PBE+D3 EPS {eps}" if ok else "vertical inp contract violation",
                str(inp.relative_to(REPO)),
            )

    exp10 = REPO / "experiments/exp_10_size_scaling/inputs"
    for inp in sorted(exp10.glob("size_*.inp")):
        t = read_inp(inp)
        n = int(inp.name.split("_")[1].replace("x60", ""))
        expect = 400 if "cutoff400" in inp.name or n <= 4 else 350
        has_d3 = "DFTD3" in t
        m = re.search(r"CUTOFF\s+(\d+)", t)
        cutoff = int(m.group(1)) if m else None
        ok = has_d3 and cutoff == expect
        add(
            checks,
            "setup",
            f"exp10_cutoff_{inp.stem}",
            "pass" if ok else "fail",
            f"expected CUTOFF {expect} PBE+D3" if ok else f"got CUTOFF {cutoff} D3={has_d3}",
            str(inp.relative_to(REPO)),
        )

    seed_dir = REPO / "experiments/exp_5_synergy/seed_validation/inputs"
    seed_inps = list(seed_dir.glob("seed137_*_strain*_rigid.inp"))
    if not seed_inps:
        add(checks, "setup", "seed137_inputs", "warn", "no seed137 inputs generated yet", str(seed_dir))
    else:
        missing_d3 = [p.name for p in seed_inps if "DFTD3" not in read_inp(p)]
        pristine_n = len(list(seed_dir.glob("seed137_pristine_*_rigid.inp")))
        add(
            checks,
            "setup",
            "seed137_pbe_d3",
            "pass" if not missing_d3 else "fail",
            f"{len(seed_inps)} inps ({pristine_n} pristine); all PBE+D3"
            if not missing_d3
            else f"PBE-only (no D3): {missing_d3[:3]}...",
            str(seed_dir.relative_to(REPO)),
        )

    relax_dir = REPO / "experiments/exp_5_synergy/relax_validation/inputs"
    for name in (
        "relax_pristine_eps0_geo.inp",
        "relax_pristine_eps3_geo.inp",
        "relax_P_eps0_geo.inp",
        "relax_P_eps3_geo.inp",
    ):
        p = relax_dir / name
        if not p.exists():
            add(checks, "setup", f"relax_inp_{name}", "warn", "relax validation inp missing", str(p))
            continue
        t = read_inp(p)
        ok = inp_has(t, "DFTD3", "RUN_TYPE GEO_OPT", "CUTOFF 400")
        add(
            checks,
            "setup",
            f"relax_contract_{name}",
            "pass" if ok else "fail",
            "fixed-cell GEO_OPT PBE+D3" if ok else "relax inp contract violation",
            str(p.relative_to(REPO)),
        )

    legacy = REPO / "dft_results/exp_5_synergy/C60_strain_+0.0_B_doped_synergy.inp"
    if legacy.exists() and "DFTD3" not in read_inp(legacy):
        add(
            checks,
            "setup",
            "table_s1_legacy_functional",
            "warn",
            "Table S1 tetramer alpha/E_sub from legacy PBE (no D3) archive — do not mix with periodic PBE+D3 S",
            str(legacy.relative_to(REPO)),
        )

    s3_script = REPO / "experiments/exp_5_synergy/relax_validation/analyze_relax_s.py"
    if s3_script.exists() and "quantitative_ratio_valid" in s3_script.read_text():
        add(
            checks,
            "setup",
            "table_s3_cross_functional",
            "warn",
            "Table S3 rigid=PBE vs relaxed=PBE+D3 — retention ratio sign-only (documented in analyze_relax_s)",
            "relax_validation/analyze_relax_s.py",
        )

    audit_coordinates(checks)


def audit_process(checks: list[Check]) -> None:
    """Layer B: workflow scripts, paths, and Marcus protocol wiring."""
    hooks = [
        "experiments/continue_exp9_pending.sh",
        "experiments/post_exp9_converged.sh",
        "experiments/run_prb_revision_dft.sh",
        "experiments/exp_9_charged_polaron/generate_vertical_sp.py",
    ]
    for rel in hooks:
        p = REPO / rel
        add(
            checks,
            "process",
            f"hook_exists_{Path(rel).name}",
            "pass" if p.exists() else "fail",
            "workflow script present" if p.exists() else "missing workflow script",
            rel,
        )

    out_dir = REPO / "dft_results/exp_9_charged_polaron/outputs"
    vert_dir = REPO / "experiments/exp_9_charged_polaron/inputs/vertical"
    if vert_dir.is_dir():
        for inp in vert_dir.glob("polaron_*_vert_*.inp"):
            t = read_inp(inp)
            m = re.search(r"COORD_FILE_NAME\s+(\S+)", t)
            if not m:
                add(checks, "process", f"vert_coord_{inp.stem}", "fail", "no COORD_FILE_NAME in vertical inp")
                continue
            rel = m.group(1).replace("../../../../", "")
            xyz = REPO / rel
            if not xyz.exists():
                add(checks, "process", f"vert_xyz_{inp.stem}", "fail", "neutral-geometry XYZ missing", str(rel))
                continue
            if "qpos0_opt" not in xyz.name:
                add(
                    checks,
                    "process",
                    f"vert_xyz_source_{inp.stem}",
                    "fail",
                    "vertical SP must use neutral (q=0) optimized geometry",
                    xyz.name,
                )
            else:
                add(
                    checks,
                    "process",
                    f"vert_marcus_wiring_{inp.stem}",
                    "pass",
                    "vertical at neutral geometry from qpos0 GEO_OPT",
                    str(xyz.relative_to(REPO)),
                )

    prb_path = REPO / "experiments/run_prb_revision_dft.sh"
    if prb_path.exists():
        prb = read_inp(prb_path)
        if "pgrep -f 'cp2k" not in prb:
            add(checks, "process", "prb_mutex", "warn", "run_prb_revision_dft may not guard against parallel CP2K")
        else:
            add(checks, "process", "prb_mutex", "pass", "PRB queue aborts if CP2K already running")

    post9_path = REPO / "experiments/post_exp9_converged.sh"
    if post9_path.exists():
        post9 = read_inp(post9_path)
        chain_ok = "analyze_exp9_polaron.py" in post9 and "render_si_figures" in post9
        add(
            checks,
            "process",
            "post_exp9_chain",
            "pass" if chain_ok else "fail",
            "post_exp9 -> audit JSON -> SI figures" if chain_ok else "incomplete post_exp9 hook",
        )

    lock = REPO / "experiments/.exp9_batch.lock"
    if lock.exists():
        pid = lock.read_text().strip()
        r = subprocess.run(["ps", "-p", pid], capture_output=True)
        alive = r.returncode == 0
        add(
            checks,
            "process",
            "exp9_batch_lock",
            "pass" if alive else "warn",
            f"batch lock pid={pid} {'active' if alive else 'stale'}",
            str(lock.relative_to(REPO)),
        )


def audit_results(checks: list[Check]) -> None:
    """Layer C: converged outputs, audit JSON consistency, re-parse cross-checks."""
    out9 = REPO / "dft_results/exp_9_charged_polaron/outputs"
    geo_ended = sum(
        1
        for p in out9.glob("polaron_*_opt.out")
        if p.is_file() and "PROGRAM ENDED" in p.read_text(errors="ignore")
    )
    add(
        checks,
        "result",
        "exp9_geo_program_ended",
        "pass" if geo_ended == 12 else "fail" if geo_ended < 12 else "warn",
        f"GEO_OPT PROGRAM ENDED {geo_ended}/12",
        str(out9.relative_to(REPO)),
    )

    vert_conv = sum(
        1
        for p in out9.glob("polaron_*_vert_*.out")
        if p.is_file() and "SCF run converged" in p.read_text(errors="ignore")
    )
    json_path = REPO / "experiments/analysis/exp9_polaron_verification.json"
    if json_path.exists():
        d = json.loads(json_path.read_text())
        json_vert = len((d.get("vertical_sp") or {}).get("outputs_converged") or [])
        if json_vert != vert_conv:
            add(
                checks,
                "result",
                "exp9_vert_json_sync",
                "fail",
                f"JSON vertical converged {json_vert} != grep {vert_conv}",
                str(json_path.relative_to(REPO)),
            )
        else:
            add(
                checks,
                "result",
                "exp9_vert_json_sync",
                "pass",
                f"vertical SP converged {vert_conv}/8 matches JSON",
            )
        geo_json = d.get("converged", 0)
        if geo_json != geo_ended:
            add(
                checks,
                "result",
                "exp9_geo_json_sync",
                "fail",
                f"JSON GEO_OPT {geo_json} != PROGRAM ENDED count {geo_ended}",
            )
        else:
            add(checks, "result", "exp9_geo_json_sync", "pass", f"GEO_OPT JSON {geo_json}/12 synced")

        for dop in ("pristine", "N", "B", "P"):
            lam = (d.get("derived") or {}).get("lambda_eV", {}).get(dop, {})
            for key in ("lambda_IP_eV", "lambda_EA_eV"):
                val = lam.get(key)
                if val is None:
                    continue
                ch = 1 if "IP" in key else -1
                tag = "qpos1" if ch == 1 else "qneg1"
                adia = parse_energy_from_out(out9 / f"polaron_{dop}_{tag}_opt.out", geo=True)
                vert = parse_energy_from_out(
                    out9 / f"polaron_{dop}_{tag}_vert_neutral_geom_sp.out", geo=False
                )
                if adia is None or vert is None:
                    add(
                        checks,
                        "result",
                        f"lambda_reparse_{dop}_{key}",
                        "warn",
                        "cannot recompute lambda from .out (missing converged endpoint)",
                    )
                    continue
                recomputed = (vert - adia) * HA_TO_EV
                if abs(recomputed - val) > 0.002:
                    add(
                        checks,
                        "result",
                        f"lambda_reparse_{dop}_{key}",
                        "fail",
                        f"JSON lambda={val:.4f} vs reparse {recomputed:.4f} eV",
                    )
                else:
                    add(
                        checks,
                        "result",
                        f"lambda_reparse_{dop}_{key}",
                        "pass",
                        f"lambda={val:.4f} eV matches adiabatic/vertical difference",
                    )
    else:
        add(checks, "result", "exp9_json", "fail", "exp9_polaron_verification.json missing")

    add(
        checks,
        "result",
        "exp9_vert_converged",
        "pass" if vert_conv == 8 else "warn" if vert_conv >= 7 else "fail",
        f"vertical SP SCF converged {vert_conv}/8",
    )

    t1 = REPO / "experiments/analysis/table1_verification.json"
    synergy = REPO / "dft_results/exp_5_synergy"
    if t1.exists():
        data = json.loads(t1.read_text())
        for dop in ("B", "N", "P"):
            block = data["systems"][dop]
            e0_path = synergy / block["out_0"]
            e0 = parse_energy_from_out(e0_path, geo=False)
            if e0 is None:
                add(checks, "result", f"table1_out_{dop}_e0", "warn", "cannot reparse E(eps=0) from .out")
            elif abs(e0 - block["E_0pct_Ha"]) > 0.01:
                add(
                    checks,
                    "result",
                    f"table1_out_{dop}_e0",
                    "fail",
                    f"JSON E_0={block['E_0pct_Ha']} vs .out {e0}",
                    block["out_0"],
                )
            else:
                add(checks, "result", f"table1_out_{dop}_e0", "pass", f"E(eps=0) matches .out within 0.01 Ha")

    exp10_inp = REPO / "experiments/exp_10_size_scaling/inputs"
    exp10_grep = sum(
        1
        for p in exp10_inp.glob("size_*.out")
        if p.is_file() and "SCF run converged" in p.read_text(errors="ignore")
    )
    add(
        checks,
        "result",
        "exp10_scf_converged",
        "pass" if exp10_grep >= 40 else "warn",
        f"Exp10 SCF converged {exp10_grep}/41 (grep on inputs/*.out)",
    )

    sdc = REPO / "experiments/analysis/sdc/sdc_exp10_synergy_audit.json"
    if sdc.exists():
        n = len(json.loads(sdc.read_text()).get("synergy_table", []))
        add(
            checks,
            "result",
            "sdc_synergy_points",
            "pass" if n == 15 else "warn",
            f"SDC audit {n} synergy points (expect 15)",
            str(sdc.relative_to(REPO)),
        )


def summarize(checks: list[Check]) -> dict:
    by_layer: dict[str, list[Check]] = {"setup": [], "process": [], "result": []}
    for c in checks:
        by_layer.setdefault(c.layer, []).append(c)
    counts = {"pass": 0, "warn": 0, "fail": 0}
    for c in checks:
        counts[c.status] = counts.get(c.status, 0) + 1
    return {
        "date": date.today().isoformat(),
        "summary": counts,
        "layers": {
            layer: {s: sum(1 for c in items if c.status == s) for s in ("pass", "warn", "fail")}
            for layer, items in by_layer.items()
        },
        "checks": [asdict(c) for c in checks],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Three-layer experiment reliability audit")
    parser.add_argument(
        "--json",
        default=str(REPO / "experiments/analysis/reliability_audit.json"),
        help="Write full report JSON",
    )
    args = parser.parse_args()

    checks: list[Check] = []
    audit_setup(checks)
    audit_process(checks)
    audit_results(checks)
    report = summarize(checks)

    out = Path(args.json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print("=== Experiment reliability audit (setup+coords -> process -> result) ===")
    for layer in ("setup", "process", "result"):
        lc = report["layers"][layer]
        print(f"  {layer:7s}: pass={lc['pass']} warn={lc['warn']} fail={lc['fail']}")
    print(f"  TOTAL: pass={s['pass']} warn={s['warn']} fail={s['fail']}")
    print(f"  report: {out.relative_to(REPO)}")

    fails = [c for c in checks if c.status == "fail"]
    warns = [c for c in checks if c.status == "warn"]
    if fails:
        print("\n--- FAIL ---")
        for c in fails[:20]:
            print(f"  [{c.layer}] {c.check_id}: {c.message}")
        if len(fails) > 20:
            print(f"  ... +{len(fails) - 20} more")
    if warns:
        print("\n--- WARN ---")
        for c in warns[:12]:
            print(f"  [{c.layer}] {c.check_id}: {c.message}")
        if len(warns) > 12:
            print(f"  ... +{len(warns) - 12} more")

    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
