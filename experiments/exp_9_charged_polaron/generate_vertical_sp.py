#!/usr/bin/env python3
"""Generate vertical single-point inputs: q=±1 on neutral (q=0) optimized geometry."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "dft_results" / "exp_9_charged_polaron" / "outputs"
VERT_DIR = Path(__file__).resolve().parent / "inputs" / "vertical"

DOPANTS = ("pristine", "N", "B", "P")
CHARGED = (+1, -1)


def charge_tag(charge: int) -> str:
    return "qpos1" if charge == 1 else "qneg1"


def read_cell_from_opt_inp(dopant: str) -> tuple[float, float, float]:
    inp = Path(__file__).resolve().parent / "inputs" / f"polaron_{dopant}_qpos0_opt.inp"
    text = inp.read_text()
    for line in text.splitlines():
        if line.strip().startswith("ABC"):
            parts = line.split()
            return float(parts[1]), float(parts[2]), float(parts[3])
    raise ValueError(f"ABC not found in {inp}")


def sp_inp(
    project: str,
    xyz_rel: str,
    charge: int,
    a: float,
    b: float,
    c: float,
    eps_scf: str = "1.0E-7",
) -> str:
    mult = 1 if charge == 0 else 2
    uks = ".FALSE." if charge == 0 else ".TRUE."
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

    CHARGE {charge}
    MULTIPLICITY {mult}
    UKS {uks}

    &MGRID
      CUTOFF 400
      REL_CUTOFF 50
    &END MGRID

    &QS
      METHOD GPW
      EPS_DEFAULT 1.0E-11
    &END QS

    &SCF
      SCF_GUESS ATOMIC
      EPS_SCF {eps_scf}
      MAX_SCF 1000

      &OT
        MINIMIZER DIIS
        PRECONDITIONER FULL_ALL
      &END OT
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
      &MO
        EIGENVALUES .TRUE.
        OCCUPATION_NUMBERS .TRUE.
        NDIGITS 8
      &END MO
    &END PRINT
  &END DFT

  &SUBSYS
    &CELL
      ABC {a:.4f} {b:.4f} {c:.4f}
      PERIODIC XYZ
    &END CELL

    &TOPOLOGY
      COORD_FILE_NAME {xyz_rel}
      COORD_FILE_FORMAT XYZ
    &END TOPOLOGY

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


def main() -> None:
    VERT_DIR.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    skipped: list[str] = []

    for dopant in DOPANTS:
        neutral_xyz = OUT_DIR / f"polaron_{dopant}_qpos0_opt-pos-1.xyz"
        if not neutral_xyz.exists():
            skipped.append(f"{dopant}: missing {neutral_xyz.name}")
            continue
        a, b, c = read_cell_from_opt_inp(dopant)
        xyz_rel = f"../../../../dft_results/exp_9_charged_polaron/outputs/{neutral_xyz.name}"

        for charge in CHARGED:
            tag = charge_tag(charge)
            project = f"polaron_{dopant}_{tag}_vert_neutral_geom_sp"
            path = VERT_DIR / f"{project}.inp"
            eps = "1.0E-6" if dopant == "B" and charge == -1 else "1.0E-7"
            path.write_text(sp_inp(project, xyz_rel, charge, a, b, c, eps_scf=eps))
            written.append(path.name)

    print(f"Vertical SP inputs: {len(written)} written -> {VERT_DIR.relative_to(REPO)}")
    for name in written:
        print(f"  {name}")
    if skipped:
        print("Skipped (no neutral opt xyz):")
        for s in skipped:
            print(f"  {s}")
    print("Do not submit CP2K unless explicitly requested (AGENTS Track A gate).")


if __name__ == "__main__":
    main()
