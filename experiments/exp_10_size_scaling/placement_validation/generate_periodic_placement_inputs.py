#!/usr/bin/env python3
"""Periodic n=4 alternate dopant placements (seeds 137, 271) for Table IV periodic audit."""

from __future__ import annotations

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
N_MOL = 4
SEEDS = (137, 271)
STRAINS = (0.0, 3.0)
DOPANTS = ("pristine", "B", "N", "P")


def build_inp(project: str, coords_str: str, a: float, b: float, c: float) -> str:
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
        MAX_SCF 30
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

    &KIND B
      BASIS_SET DZVP-MOLOPT-SR-GTH
      POTENTIAL GTH-PBE-q3
    &END KIND

    &KIND N
      BASIS_SET DZVP-MOLOPT-SR-GTH
      POTENTIAL GTH-PBE-q5
    &END KIND

    &KIND P
      BASIS_SET DZVP-MOLOPT-SR-GTH
      POTENTIAL GTH-PBE-q5
    &END KIND
  &END SUBSYS
&END FORCE_EVAL
"""


def strain_tag(eps: float) -> str:
    return f"pos{eps:.0f}pct" if eps >= 0 else f"neg{abs(eps):.0f}pct"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    count = 0
    for seed in SEEDS:
        for strain in STRAINS:
            scale = 1.0 + strain / 100.0
            coords, cell = get_multi_c60_coordinates(N_MOL)
            for dop in DOPANTS:
                if dop == "pristine":
                    atoms = [("C", x, y, z) for x, y, z in coords]
                else:
                    atoms, _ = create_substitutional_doped_structure(
                        coords, dop, N_MOL / len(coords), seed=seed
                    )
                scaled = [(e, x * scale, y * scale, z) for e, x, y, z in atoms]
                coords_str = format_coords_for_cp2k(scaled)
                a, b, c = cell["a"] * scale, cell["b"] * scale, cell["c"]
                tag = f"place_seed{seed}_{dop}_{strain_tag(strain)}"
                path = OUT / f"{tag}.inp"
                path.write_text(build_inp(tag, coords_str, a, b, c), encoding="utf-8")
                print("wrote", path.name)
                count += 1
    print(f"done: {count} inputs")


if __name__ == "__main__":
    main()
