#!/usr/bin/env python3
"""Check committed CP2K inputs against canonical PBE+D3@400 Ry protocol."""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# (label, directory, glob, rules)
CHECKS = [
    (
        "seed137",
        REPO / "experiments/exp_5_synergy/seed_validation/inputs",
        "seed137_*_rigid.inp",
        {
            "mgrid": True,
            "d3": True,
            "no_dup_basis": True,
            "kind_q": True,
            "no_forces": True,
            "no_energy_gap": True,
            "max_scf_300": True,
        },
    ),
    (
        "placement",
        REPO / "experiments/exp_10_size_scaling/placement_validation/inputs",
        "place_*.inp",
        {"mgrid": True, "d3": True, "kind_q": True, "no_forces": True, "no_energy_gap": True},
    ),
    (
        "rigid_pbed3",
        REPO / "experiments/exp_5_synergy/relax_validation/rigid_pbed3/inputs",
        "rigid_pbed3_*.inp",
        {"mgrid": True, "d3": True, "kind_q": True, "no_forces": True, "no_energy_gap": True},
    ),
    (
        "population",
        REPO / "experiments/exp_7_electronic_structure/population_validation/inputs",
        "pop_n1_P_*.inp",
        {"mgrid": True, "d3": True, "kind_q": True, "require_lsd": True, "no_forces": True, "no_energy_gap": True},
    ),
    (
        "exp7",
        REPO / "experiments/exp_7_electronic_structure/inputs",
        "elec_*.inp",
        {"mgrid": True, "d3": True, "kind_q": True, "no_forces": True, "no_energy_gap": True, "neutral_ks": True},
    ),
    (
        "exp8",
        REPO / "experiments/exp_8_geometry_opt/inputs",
        "geoopt_*.inp",
        {"mgrid": True, "d3": True, "kind_q": True, "no_forces": True, "no_energy_gap": True, "neutral_ks": True},
    ),
    (
        "exp8_sp",
        REPO / "experiments/exp_8_geometry_opt/inputs",
        "geoopt_*_sp.inp",
        {
            "mgrid_min": 400,
            "d3": True,
            "kind_q": True,
            "no_forces": True,
            "no_energy_gap": True,
            "neutral_ks": True,
        },
    ),
    (
        "exp9_geo",
        REPO / "experiments/exp_9_charged_polaron/inputs",
        "polaron_*_opt.inp",
        {
            "mgrid": True,
            "d3": True,
            "kind_q": True,
            "no_forces": True,
            "no_energy_gap": True,
            "exp9_charge_ks": True,
        },
    ),
    (
        "exp9_vert",
        REPO / "experiments/exp_9_charged_polaron/inputs/vertical",
        "*.inp",
        {
            "mgrid": True,
            "d3": True,
            "kind_q": True,
            "no_forces": True,
            "no_energy_gap": True,
            "exp9_charge_ks": True,
        },
    ),
]


def _charge_and_uks(text: str) -> tuple[int | None, bool | None]:
    m_c = re.search(r"^\s*CHARGE\s+(-?\d+)", text, re.M)
    m_u = re.search(r"^\s*UKS\s+\.(TRUE|FALSE)\.", text, re.M)
    charge = int(m_c.group(1)) if m_c else None
    uks = m_u.group(1) == "TRUE" if m_u else None
    return charge, uks


def check_file(path: Path, rules: dict) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    errs: list[str] = []
    if rules.get("mgrid"):
        if "&MGRID" not in text:
            errs.append("missing &MGRID")
        elif not re.search(r"CUTOFF\s+400", text):
            errs.append("CUTOFF not 400")
    if rules.get("mgrid_min"):
        if "&MGRID" not in text:
            errs.append("missing &MGRID")
        else:
            m = re.search(r"CUTOFF\s+(\d+)", text)
            if not m or int(m.group(1)) < rules["mgrid_min"]:
                errs.append(f"CUTOFF < {rules['mgrid_min']}")
    if rules.get("d3") and "DFTD3" not in text:
        errs.append("missing DFTD3")
    if rules.get("no_dup_basis"):
        n = len(re.findall(r"^\s*BASIS_SET_FILE_NAME\s+", text, re.M))
        if n != 1:
            errs.append(f"BASIS_SET_FILE_NAME count={n}")
    if rules.get("kind_q") and re.search(r"POTENTIAL GTH-PBE\s*$", text, re.M):
        errs.append("bare GTH-PBE in KIND")
    if rules.get("no_forces") and "&FORCES" in text:
        errs.append("contains &FORCES")
    if rules.get("no_lsd") and re.search(r"^\s*LSD\s+\.TRUE\.", text, re.M):
        errs.append("LSD .TRUE.")
    if rules.get("require_lsd") and not re.search(r"^\s*LSD\s+\.TRUE\.", text, re.M):
        errs.append("missing LSD .TRUE. (odd electron count)")
    if rules.get("no_energy_gap") and re.search(r"^\s*ENERGY_GAP\s+", text, re.M):
        errs.append("ENERGY_GAP present")
    if rules.get("max_scf_300"):
        if re.search(r"^\s*MAX_SCF\s+200\s*$", text, re.M):
            errs.append("inner MAX_SCF still 200")
    if rules.get("neutral_ks"):
        charge, uks = _charge_and_uks(text)
        if charge not in (0, None):
            errs.append(f"expected neutral CHARGE 0, got {charge}")
        if uks is True:
            errs.append("UKS .TRUE. on neutral task")
    if rules.get("exp9_charge_ks"):
        charge, uks = _charge_and_uks(text)
        if charge is None:
            errs.append("missing CHARGE")
        elif charge == 0 and uks is not False:
            errs.append("neutral Exp9 must have UKS .FALSE.")
        elif charge != 0 and uks is not True:
            errs.append("charged Exp9 must have UKS .TRUE.")
    return errs


def _cell_and_coords(path: Path) -> tuple[float | None, list[tuple[str, float, float, float]]]:
    """In-plane lattice constant and the atom list of a CP2K input."""
    a: float | None = None
    atoms: list[tuple[str, float, float, float]] = []
    inside = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if a is None:
            m = re.match(r"ABC\s+([\d.]+)", s) or re.match(r"A\s+([\d.]+)\s", s)
            if m:
                a = float(m.group(1))
        if "&COORD" in line:
            inside = True
            continue
        if "&END COORD" in line:
            inside = False
            continue
        if inside:
            f = line.split()
            if len(f) == 4:
                atoms.append((f[0], float(f[1]), float(f[2]), float(f[3])))
    return a, atoms


def check_strain_pair(zero: Path, strained: Path, tol: float = 2e-4) -> list[str]:
    """A strained input must scale the coordinates with the cell and keep the sites.

    Two protocol errors are invisible to the per-file rules above and both
    silently destroy a four-corner evaluation: scaling only the cell (so the
    material is never strained, and the energy change is a periodic-image
    artifact) and re-drawing the dopant sites between corners (so the difference
    measures configuration, not strain).
    """
    a0, x = _cell_and_coords(zero)
    a1, y = _cell_and_coords(strained)
    errs: list[str] = []
    if a0 is None or a1 is None:
        return ["cell not parsed"]
    if len(x) != len(y):
        return [f"atom count {len(x)} vs {len(y)}"]
    cell_ratio = a1 / a0
    if abs(cell_ratio - 1.0) < 1e-9:
        return []
    ratios = []
    for p, q in zip(x, y):
        for i in (1, 2):  # in-plane x, y
            if abs(p[i]) > 1e-6:
                ratios.append(q[i] / p[i])
    if not ratios:
        return ["no in-plane coordinates"]
    if abs(min(ratios) - cell_ratio) > tol or abs(max(ratios) - cell_ratio) > tol:
        errs.append(
            f"coordinates not scaled with cell (cell x{cell_ratio:.6f}, "
            f"coords x{min(ratios):.6f}-{max(ratios):.6f})"
        )
    sites0 = {s for s, *_ in ((a[0], a) for a in x) if s not in ("C", "H")}
    if sites0:
        def dopant_sites(atoms, scale):
            return {
                (round(a[1] / scale, 3), round(a[2] / scale, 3), round(a[3], 3))
                for a in atoms
                if a[0] not in ("C", "H")
            }

        d0 = dopant_sites(x, 1.0)
        d1 = dopant_sites(y, cell_ratio)
        if d0 != d1:
            errs.append(f"dopant sites differ between corners ({len(d0 & d1)}/{len(d0)} shared)")
    return errs


# (label, directory, eps0 glob, strained-name substitution)
STRAIN_PAIRS = [
    (
        "exp10 periodic",
        REPO / "experiments/exp_10_size_scaling/inputs",
        "size_*_pos0pct.inp",
        ("pos0pct", "pos3pct"),
    ),
    (
        "periodic placement",
        REPO / "experiments/exp_10_size_scaling/placement_validation/inputs",
        "place_*_pos0pct.inp",
        ("pos0pct", "pos3pct"),
    ),
    (
        "periodic relaxation",
        REPO / "experiments/exp_10_size_scaling/periodic_relax_validation/inputs",
        "per_relax_*_eps0_geo.inp",
        ("eps0", "eps3"),
    ),
    (
        "Hirshfeld population",
        REPO / "experiments/exp_7_electronic_structure/population_validation/inputs",
        "pop_*_strainp0.0pct.inp",
        ("strainp0.0pct", "strainp3.0pct"),
    ),
]

# Documented-invalid tetramer pairs: vacuum-cell or dopant-site redraws.
# They MUST fail check_strain_pair; a pass is a checker bug.
INVALID_STRAIN_PAIRS = [
    (
        REPO / "experiments/exp_5_synergy/reference_pbed3/inputs"
        / "refpbed3_pristine_strainp0.0_rigid.inp",
        REPO / "experiments/exp_5_synergy/reference_pbed3/inputs"
        / "refpbed3_pristine_strainp3.0_rigid.inp",
    ),
    (
        REPO / "experiments/exp_5_synergy/reference_pbed3/inputs"
        / "refpbed3_P_strainp0.0_rigid.inp",
        REPO / "experiments/exp_5_synergy/reference_pbed3/inputs"
        / "refpbed3_P_strainp3.0_rigid.inp",
    ),
    (
        REPO / "experiments/exp_5_synergy/seed_validation/inputs"
        / "seed137_pristine_strainp0.0_rigid.inp",
        REPO / "experiments/exp_5_synergy/seed_validation/inputs"
        / "seed137_pristine_strainp3.0_rigid.inp",
    ),
    (
        REPO / "experiments/exp_5_synergy/seed_validation/inputs"
        / "seed137_P_strainp0.0_rigid.inp",
        REPO / "experiments/exp_5_synergy/seed_validation/inputs"
        / "seed137_P_strainp3.0_rigid.inp",
    ),
    (
        REPO / "experiments/exp_5_synergy/relax_validation/inputs"
        / "relax_pristine_eps0_geo.inp",
        REPO / "experiments/exp_5_synergy/relax_validation/inputs"
        / "relax_pristine_eps3_geo.inp",
    ),
    (
        REPO / "experiments/exp_5_synergy/relax_validation/inputs"
        / "relax_P_eps0_geo.inp",
        REPO / "experiments/exp_5_synergy/relax_validation/inputs"
        / "relax_P_eps3_geo.inp",
    ),
]


def check_strain_protocol() -> tuple[int, int, int]:
    failed = checked = 0
    for label, directory, pattern, (old, new) in STRAIN_PAIRS:
        if not directory.is_dir():
            print(f"SKIP {label}: missing {directory.relative_to(REPO)}")
            continue
        for zero in sorted(directory.glob(pattern)):
            strained = zero.with_name(zero.name.replace(old, new))
            if not strained.is_file():
                continue
            checked += 1
            errs = check_strain_pair(zero, strained)
            if errs:
                print(f"FAIL {strained.relative_to(REPO)}: {', '.join(errs)}")
                failed += 1
            else:
                print(f"PASS affine strain: {zero.name} -> {strained.name}")
    invalid_ok = 0
    for zero, strained in INVALID_STRAIN_PAIRS:
        if not (zero.is_file() and strained.is_file()):
            print(f"SKIP invalid pair missing: {zero.name}")
            continue
        errs = check_strain_pair(zero, strained)
        if not errs:
            print(f"FAIL expected-invalid pair passed: {zero.name}")
            failed += 1
            checked += 1
        else:
            invalid_ok += 1
            print(f"PASS expected-fail: {zero.name} ({errs[0]})")
    return failed, checked, invalid_ok


def main() -> int:
    failed = 0
    checked = 0
    for label, directory, pattern, rules in CHECKS:
        if not directory.is_dir():
            print(f"SKIP {label}: missing {directory.relative_to(REPO)}")
            continue
        paths = sorted(directory.glob(pattern))
        if not paths:
            print(f"SKIP {label}: no files for {pattern}")
            continue
        for path in paths:
            if label == "exp8" and path.name.endswith("_sp.inp"):
                continue
            checked += 1
            errs = check_file(path, rules)
            if errs:
                print(f"FAIL {path.relative_to(REPO)}: {', '.join(errs)}")
                failed += 1
    strain_failed, strain_checked, invalid_ok = check_strain_protocol()
    checked += strain_checked
    failed += strain_failed
    affine_ok = strain_checked - strain_failed

    if failed:
        print(f"\n{failed}/{checked} check(s) failed")
        return 1
    print(
        f"verify_dft_protocol: OK ({checked} files; "
        f"{affine_ok}/{strain_checked} affine pairs PASS; "
        f"{invalid_ok} expected-fail tetramer pairs)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
