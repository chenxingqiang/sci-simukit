#!/usr/bin/env python3
"""Parse MO_CUBES SP outputs and build homo/lumo cube manifest for figure rendering."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
INP_DIR = Path(__file__).resolve().parent / "inputs"
ARCHIVE = REPO / "dft_results" / "exp_10_size_scaling" / "mo_cubes"
MANIFEST = REPO / "experiments/analysis/mo_cubes_exp10.json"

WFN_RE = re.compile(r"-WFN_(\d+)_1-1_0\.cube$")


def converged(out_path: Path) -> bool:
    if not out_path.is_file():
        return False
    return "SCF run converged" in out_path.read_text(errors="replace")


def homo_lumo_indices_from_mo(text: str) -> tuple[int, int] | None:
    lines = text.splitlines()
    occ_vals: list[tuple[float, int]] = []
    in_block = False
    orb = 0
    for line in lines:
        if "Occupation" in line and "Eigenvalues" in line:
            in_block = True
            orb = 0
            continue
        if not in_block:
            continue
        if line.strip().startswith("---") or "Fermi" in line:
            break
        parts = line.split()
        if len(parts) < 2:
            continue
        try:
            occ = float(parts[0])
            orb += 1
            occ_vals.append((occ, orb))
        except ValueError:
            continue
    if not occ_vals:
        return None
    occupied = [i for o, i in occ_vals if o > 0.5]
    unoccupied = [i for o, i in occ_vals if o < 0.5]
    if not occupied or not unoccupied:
        return None
    return max(occupied), min(unoccupied)


def find_cube(workdir: Path, project: str, orb_index: int) -> Path | None:
    for prefix in (f"{project}-WFN_{orb_index:05d}", f"{project}-WFN_{orb_index}"):
        matches = sorted(workdir.glob(f"{prefix}*_1-1_0.cube"))
        if matches:
            return matches[0]
    return None


def analyze_task(stem: str) -> dict:
    project = stem
    out_path = INP_DIR / f"{stem}.out"
    entry: dict = {
        "stem": stem,
        "base_stem": stem.removesuffix("_mo"),
        "converged": False,
        "homo_index": None,
        "lumo_index": None,
        "homo_cube": None,
        "lumo_cube": None,
        "archive_dir": str(ARCHIVE / stem),
    }
    if not converged(out_path):
        return entry

    text = out_path.read_text(errors="replace")
    entry["converged"] = True
    indices = homo_lumo_indices_from_mo(text)
    if indices:
        homo_i, lumo_i = indices
    else:
        cubes = sorted(
            INP_DIR.glob(f"{project}-WFN_*.cube"),
            key=lambda p: int(WFN_RE.search(p.name).group(1)),
        )
        if len(cubes) < 2:
            return entry
        nums = [int(WFN_RE.search(c.name).group(1)) for c in cubes]
        homo_i, lumo_i = nums[0], nums[1]

    entry["homo_index"] = homo_i
    entry["lumo_index"] = lumo_i
    homo_cube = find_cube(INP_DIR, project, homo_i)
    lumo_cube = find_cube(INP_DIR, project, lumo_i)
    if homo_cube:
        entry["homo_cube"] = str(homo_cube.resolve())
    if lumo_cube:
        entry["lumo_cube"] = str(lumo_cube.resolve())
    return entry


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write JSON manifest")
    args = parser.parse_args()

    systems: dict[str, dict] = {}
    converged_n = 0
    for inp in sorted(INP_DIR.glob("size_*_mo.inp")):
        stem = inp.stem
        info = analyze_task(stem)
        systems[info["base_stem"]] = info
        if info["converged"]:
            converged_n += 1
        print(
            f"{stem}: converged={info['converged']} "
            f"homo={info.get('homo_index')} lumo={info.get('lumo_index')}"
        )

    payload = {
        "status": "complete" if converged_n == len(systems) else "partial",
        "converged": converged_n,
        "total": len(systems),
        "systems": systems,
    }
    if args.write:
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(payload, indent=2) + "\n")
        print(f"manifest -> {MANIFEST}")


if __name__ == "__main__":
    main()
