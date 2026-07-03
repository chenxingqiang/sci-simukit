#!/usr/bin/env python3
"""n=1 periodic supercell: Hirshfeld population along strain path (B/N/P)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "experiments"))

from qhp_c60_structures import (  # noqa: E402
    create_substitutional_doped_structure,
    format_coords_for_cp2k,
    get_multi_c60_coordinates,
)

OUT = Path(__file__).resolve().parent / "inputs"
STRAINS = (-5.0, -2.5, 0.0, 2.5, 3.0, 5.0)
SEED = 42

DOPANT_KIND = {
    "B": ("GTH-PBE-q3", 3),
    "N": ("GTH-PBE-q5", 5),
    "P": ("GTH-PBE-q5", 5),
}


def build_inp(project: str, coords_str: str, a: float, b: float, c: float, dopant: str) -> str:
    pot, q = DOPANT_KIND[dopant]
    return f"""&GLOBAL
  PROJECT {project}
  RUN_TYPE ENERGY
  PRINT_LEVEL MEDIUM
&END GLOBAL

&FORCE_EVAL
  METHOD Quickstep

  &DFT
    BASIS_SET_FILE_NAME BASIS_MOLOPT
    POTENTIAL_FILE_NAME GTH_POTENTIALS
    LSD .TRUE.

    &MGRID
      CUTOFF 400
      REL_CUTOFF 50
    &END MGRID

    &QS
      METHOD GPW
      EPS_DEFAULT 1.0E-10
    &END QS

    &SCF
      SCF_GUESS ATOMIC
      EPS_SCF 1.0E-6
      MAX_SCF 300

      &OT
        MINIMIZER DIIS
        PRECONDITIONER FULL_ALL
      &END OT

      &OUTER_SCF
        MAX_SCF 20
        EPS_SCF 1.0E-6
      &END OUTER_SCF
    &END SCF

    &XC
      &XC_FUNCTIONAL PBE
      &END XC_FUNCTIONAL

      &VDW_POTENTIAL
        POTENTIAL_TYPE PAIR_POTENTIAL
        &PAIR_POTENTIAL
          TYPE DFTD3
          PARAMETER_FILE_NAME dftd3.dat
          REFERENCE_FUNCTIONAL PBE
        &END PAIR_POTENTIAL
      &END VDW_POTENTIAL
    &END XC

    &PRINT
      &MULLIKEN
      &END MULLIKEN

      &HIRSHFELD
      &END HIRSHFELD
    &END PRINT
  &END DFT

  &SUBSYS
    &CELL
      ABC {a:.4f} {b:.4f} {c:.4f}
      PERIODIC XYZ
    &END CELL

    &COORD
{coords_str}
    &END COORD

    &KIND C
      BASIS_SET DZVP-MOLOPT-SR-GTH
      POTENTIAL GTH-PBE-q4
    &END KIND

    &KIND {dopant}
      BASIS_SET DZVP-MOLOPT-SR-GTH
      POTENTIAL {pot}
    &END KIND
  &END SUBSYS
&END FORCE_EVAL
"""


def strain_tag(eps: float) -> str:
    s = f"{eps:+.1f}".replace("+", "p").replace("-", "m")
    return f"strain{s}pct"


def write_dopant_grid(dopant: str) -> int:
    coords, cell = get_multi_c60_coordinates(1)
    atoms, info = create_substitutional_doped_structure(coords, dopant, 1 / len(coords), seed=SEED)
    dop_idx = info["dopant_indices"][0] if info.get("dopant_indices") else 0
    for strain in STRAINS:
        scale = 1.0 + strain / 100.0
        scaled = [(e, x * scale, y * scale, z) for e, x, y, z in atoms]
        coords_str = format_coords_for_cp2k(scaled)
        a, b, c = cell["a"] * scale, cell["b"] * scale, cell["c"]
        tag = f"pop_n1_{dopant}_{strain_tag(strain)}"
        (OUT / f"{tag}.inp").write_text(build_inp(tag, coords_str, a, b, c, dopant), encoding="utf-8")
        print("wrote", f"{tag}.inp")
    meta = OUT / f"dopant_site_index_{dopant}.json"
    meta.write_text(
        json.dumps({"dopant_element": dopant, "dopant_index": int(dop_idx), "seed": SEED}, indent=2) + "\n"
    )
    # Legacy single-P meta for backward compatibility
    if dopant == "P":
        (OUT / "dopant_site_index.json").write_text(meta.read_text(encoding="utf-8"), encoding="utf-8")
    return int(dop_idx)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    targets = sys.argv[1:] if len(sys.argv) > 1 else ["B", "N", "P"]
    for dop in targets:
        if dop not in DOPANT_KIND:
            raise SystemExit(f"unknown dopant {dop}")
        write_dopant_grid(dop)


if __name__ == "__main__":
    main()
