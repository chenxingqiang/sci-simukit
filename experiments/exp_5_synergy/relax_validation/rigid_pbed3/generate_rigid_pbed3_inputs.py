#!/usr/bin/env python3
"""PBE+D3 rigid single-point four corners for matched-functional Table III benchmark."""

from __future__ import annotations

import re
import sys
import textwrap
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "experiments" / "exp_5_synergy"))
from modernize_cp2k_inp import normalize_kind_potentials  # noqa: E402
from relax_validation.generate_relax_inputs import CASES, extract_subsys_blocks  # noqa: E402

SYNERGY_DIR = REPO / "dft_results" / "exp_5_synergy"
OUT_DIR = Path(__file__).resolve().parent / "inputs"

CASE_MAP = [
    ("rigid_pbed3_pristine_eps0_sp", "C60_strain_+0.0_pristine_synergy.inp"),
    ("rigid_pbed3_pristine_eps3_sp", "C60_strain_+3.0_pristine_synergy.inp"),
    ("rigid_pbed3_P_eps0_sp", "C60_strain_+0.0_P_doped_synergy.inp"),
    ("rigid_pbed3_P_eps3_sp", "C60_strain_+3.0_P_doped_synergy.inp"),
]


def build_energy_inp(project: str, cell: str, coord: str, kinds: list[str]) -> str:
    kind_block = "\n    \n".join(kinds)
    return textwrap.dedent(
        f"""\
        &GLOBAL
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
            &END PRINT
          &END DFT

          &SUBSYS
            {cell}

            {coord}

            {kind_block}
          &END SUBSYS
        &END FORCE_EVAL
        """
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for project, src_name in CASE_MAP:
        src = SYNERGY_DIR / src_name
        if not src.exists():
            raise FileNotFoundError(src)
        text = src.read_text(encoding="utf-8", errors="replace")
        cell, coord, kinds = extract_subsys_blocks(text)
        kinds = [normalize_kind_potentials(k) for k in kinds]
        out = OUT_DIR / f"{project}.inp"
        out.write_text(build_energy_inp(project, cell, coord, kinds), encoding="utf-8")
        print(f"wrote {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
