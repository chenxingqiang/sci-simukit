#!/usr/bin/env python3
"""Check committed CP2K inputs against canonical PBE+D3@400 Ry protocol."""
from __future__ import annotations
import re, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
CHECKS = [
    ("seed137", REPO / "experiments/exp_5_synergy/seed_validation/inputs", "seed137_*_rigid.inp",
     {"mgrid": True, "d3": True, "no_dup_basis": True, "kind_q": True, "no_forces": True}),
    ("placement", REPO / "experiments/exp_10_size_scaling/placement_validation/inputs", "place_*.inp",
     {"mgrid": True, "d3": True, "kind_q": True, "no_forces": True}),
    ("rigid_pbed3", REPO / "experiments/exp_5_synergy/relax_validation/rigid_pbed3/inputs", "rigid_pbed3_*.inp",
     {"mgrid": True, "d3": True, "kind_q": True, "no_forces": True}),
    ("population", REPO / "experiments/exp_7_electronic_structure/population_validation/inputs", "pop_n1_P_*.inp",
     {"mgrid": True, "d3": True, "kind_q": True, "no_lsd": True, "no_forces": True}),
]

def check_file(path: Path, rules: dict) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    errs = []
    if rules.get("mgrid"):
        if "&MGRID" not in text: errs.append("missing &MGRID")
        elif not re.search(r"CUTOFF\s+400", text): errs.append("CUTOFF not 400")
    if rules.get("d3") and "DFTD3" not in text: errs.append("missing DFTD3")
    if rules.get("no_dup_basis"):
        n = len(re.findall(r"^\s*BASIS_SET_FILE_NAME\s+", text, re.M))
        if n != 1: errs.append(f"BASIS_SET_FILE_NAME count={n}")
    if rules.get("kind_q") and re.search(r"POTENTIAL GTH-PBE\s*$", text, re.M):
        errs.append("bare GTH-PBE in KIND")
    if rules.get("no_forces") and "&FORCES" in text: errs.append("contains &FORCES")
    if rules.get("no_lsd") and re.search(r"^\s*LSD\s+\.TRUE\.", text, re.M):
        errs.append("LSD .TRUE.")
    return errs

def main() -> int:
    failed = 0
    for label, directory, pattern, rules in CHECKS:
        for path in sorted(directory.glob(pattern)):
            errs = check_file(path, rules)
            if errs:
                print(f"FAIL {path.relative_to(REPO)}: {', '.join(errs)}")
                failed += 1
    if failed:
        print(f"\n{failed} file(s) failed")
        return 1
    print("verify_dft_protocol: OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())
