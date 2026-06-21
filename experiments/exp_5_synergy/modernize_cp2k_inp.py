"""Upgrade legacy Exp5 tetramer ENERGY inputs to PBE+D3 protocol (400 Ry, MOLOPT-SR-GTH)."""

from __future__ import annotations

import re


def modernize_cp2k_inp(text: str, *, cutoff: int = 400, eps_scf: str = "1.0E-6") -> str:
    """Inject D3, standardize basis paths, and set MGRID — idempotent on re-run."""
    text = re.sub(
        r"BASIS_SET_FILE_NAME\s+\S+",
        "BASIS_SET_FILE_NAME BASIS_MOLOPT",
        text,
    )
    text = re.sub(
        r"POTENTIAL_FILE_NAME\s+\S+",
        "POTENTIAL_FILE_NAME GTH_POTENTIALS",
        text,
    )
    if "DFTD3" not in text and "&XC_FUNCTIONAL PBE" in text:
        text = text.replace(
            "      &XC_FUNCTIONAL PBE\n      &END XC_FUNCTIONAL\n    &END XC",
            (
                "      &XC_FUNCTIONAL PBE\n      &END XC_FUNCTIONAL\n\n"
                "      &VDW_POTENTIAL\n"
                "        POTENTIAL_TYPE PAIR_POTENTIAL\n"
                "        &PAIR_POTENTIAL\n"
                "          TYPE DFTD3\n"
                "          PARAMETER_FILE_NAME dftd3.dat\n"
                "          REFERENCE_FUNCTIONAL PBE\n"
                "        &END PAIR_POTENTIAL\n"
                "      &END VDW_POTENTIAL\n"
                "    &END XC"
            ),
        )
    if "&MGRID" not in text:
        text = text.replace(
            "    &DFT\n",
            (
                "    &DFT\n"
                f"    &MGRID\n"
                f"      CUTOFF {cutoff}\n"
                f"      REL_CUTOFF 50\n"
                f"    &END MGRID\n\n"
            ),
            1,
        )
    else:
        text = re.sub(r"CUTOFF\s+\d+", f"CUTOFF {cutoff}", text, count=1)
    text = re.sub(r"EPS_SCF\s+[\d.E+-]+", f"EPS_SCF {eps_scf}", text)
    text = re.sub(
        r"PRECONDITIONER\s+\S+",
        "PRECONDITIONER FULL_ALL",
        text,
    )
    return text
