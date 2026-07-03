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
    if failed:
        print(f"\n{failed}/{checked} file(s) failed")
        return 1
    print(f"verify_dft_protocol: OK ({checked} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
