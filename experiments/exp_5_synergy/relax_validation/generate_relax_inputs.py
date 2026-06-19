#!/usr/bin/env python3
"""Build fixed-cell GEO_OPT inputs for tetramer relaxation validation (PRL)."""

from __future__ import annotations

import re
import textwrap
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SYNERGY_DIR = REPO / "dft_results" / "exp_5_synergy"
OUT_DIR = Path(__file__).resolve().parent / "inputs"

CASES = [
    ("relax_pristine_eps0_geo", "C60_strain_+0.0_pristine_synergy.inp"),
    ("relax_pristine_eps3_geo", "C60_strain_+3.0_pristine_synergy.inp"),
    ("relax_P_eps0_geo", "C60_strain_+0.0_P_doped_synergy.inp"),
    ("relax_P_eps3_geo", "C60_strain_+3.0_P_doped_synergy.inp"),
]

BLOCK_RE = re.compile(
    r"(&CELL.*?&END CELL)|(&COORD.*?&END COORD)|(&KIND .*?&END KIND)",
    re.DOTALL,
)


def extract_subsys_blocks(inp_text: str) -> tuple[str, str, list[str]]:
    cell = coord = None
    kinds: list[str] = []
    for m in BLOCK_RE.finditer(inp_text):
        block = m.group(0)
        if block.startswith("&CELL"):
            cell = block
        elif block.startswith("&COORD"):
            coord = block
        elif block.startswith("&KIND"):
            kinds.append(block)
    if cell is None or coord is None:
        raise ValueError("Missing CELL or COORD in source inp")
    if not kinds:
        kinds = [
            textwrap.dedent(
                """\
                &KIND C
                  BASIS_SET DZVP-MOLOPT-SR-GTH
                  POTENTIAL GTH-PBE
                &END KIND"""
            )
        ]
    return cell, coord, kinds


def build_geo_inp(project: str, cell: str, coord: str, kinds: list[str]) -> str:
    kind_block = "\n    \n".join(kinds)
    return textwrap.dedent(
        f"""\
        &GLOBAL
          PROJECT {project}
          RUN_TYPE GEO_OPT
          PRINT_LEVEL MEDIUM
        &END GLOBAL

        &MOTION
          &GEO_OPT
            TYPE MINIMIZATION
            OPTIMIZER BFGS
            MAX_ITER 300
            MAX_DR 3.0E-3
            MAX_FORCE 4.5E-4
            RMS_DR 1.5E-3
            RMS_FORCE 3.0E-4
          &END GEO_OPT

          &PRINT
            &TRAJECTORY
              FORMAT XYZ
              &EACH
                GEO_OPT 1
              &END EACH
            &END TRAJECTORY

            &RESTART
              &EACH
                GEO_OPT 10
              &END EACH
            &END RESTART
          &END PRINT
        &END MOTION

        &FORCE_EVAL
          METHOD Quickstep

          &DFT
            BASIS_SET_FILE_NAME BASIS_MOLOPT
            POTENTIAL_FILE_NAME GTH_POTENTIALS

            &MGRID
              CUTOFF 300
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
    for project, src_name in CASES:
        src = SYNERGY_DIR / src_name
        if not src.exists():
            raise FileNotFoundError(src)
        text = src.read_text(encoding="utf-8", errors="replace")
        cell, coord, kinds = extract_subsys_blocks(text)
        out = OUT_DIR / f"{project}.inp"
        out.write_text(build_geo_inp(project, cell, coord, kinds), encoding="utf-8")
        print(f"wrote {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
