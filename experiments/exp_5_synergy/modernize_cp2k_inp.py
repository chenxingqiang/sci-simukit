"""Upgrade legacy Exp5 tetramer ENERGY inputs to PBE+D3 protocol (400 Ry, MOLOPT-SR-GTH)."""

from __future__ import annotations

import re

_KIND_Q = {"C": "q4", "B": "q3", "N": "q5", "P": "q5"}

VDW_BLOCK = """
      &VDW_POTENTIAL
        POTENTIAL_TYPE PAIR_POTENTIAL
        &PAIR_POTENTIAL
          TYPE DFTD3
          PARAMETER_FILE_NAME dftd3.dat
          REFERENCE_FUNCTIONAL PBE
        &END PAIR_POTENTIAL
      &END VDW_POTENTIAL"""


def _dedupe_basis_and_potential_lines(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    seen_basis = seen_pot = False
    for line in lines:
        if re.match(r"^\s*BASIS_SET_FILE_NAME\s+", line):
            if seen_basis:
                continue
            seen_basis = True
            indent = re.match(r"^(\s*)", line).group(1)
            out.append(f"{indent}BASIS_SET_FILE_NAME BASIS_MOLOPT")
            continue
        if re.match(r"^\s*POTENTIAL_FILE_NAME\s+", line):
            if seen_pot:
                continue
            seen_pot = True
            indent = re.match(r"^(\s*)", line).group(1)
            out.append(f"{indent}POTENTIAL_FILE_NAME GTH_POTENTIALS")
            continue
        out.append(line)
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def _inject_dftd3(text: str) -> str:
    if "DFTD3" in text:
        return text
    return re.sub(
        r"(\s*&XC_FUNCTIONAL PBE\s*\n\s*&END XC_FUNCTIONAL)(\s*\n)(\s*&END XC)",
        r"\1\2" + VDW_BLOCK + r"\2\3",
        text,
        count=1,
    )


def _inject_mgrid(text: str, cutoff: int) -> str:
    if "&MGRID" in text:
        return re.sub(r"CUTOFF\s+\d+", f"CUTOFF {cutoff}", text, count=1)
    m = re.search(r"^(\s*)&DFT\s*$", text, re.M)
    if not m:
        return text
    indent = m.group(1)
    child = indent + "  "
    block = (
        f"{indent}&DFT\n"
        f"{child}&MGRID\n"
        f"{child}  CUTOFF {cutoff}\n"
        f"{child}  REL_CUTOFF 50\n"
        f"{child}&END MGRID\n"
        "\n"
    )
    return re.sub(r"^\s*&DFT\s*$", block.rstrip("\n"), text, count=1, flags=re.M)


def normalize_kind_potentials(text: str) -> str:
    for elem, q in _KIND_Q.items():
        text = re.sub(
            rf"(&KIND {elem}\b.*?POTENTIAL )GTH-PBE(?:-q\d+)?",
            rf"\1GTH-PBE-{q}",
            text,
            flags=re.S,
        )
    return text


def modernize_cp2k_inp(text: str, *, cutoff: int = 400, eps_scf: str = "1.0E-6") -> str:
    text = _dedupe_basis_and_potential_lines(text)
    text = _inject_dftd3(text)
    text = _inject_mgrid(text, cutoff)
    text = re.sub(r"EPS_SCF\s+[\d.E+-]+", f"EPS_SCF {eps_scf}", text)
    text = re.sub(r"PRECONDITIONER\s+\S+", "PRECONDITIONER FULL_ALL", text)
    text = normalize_kind_potentials(text)
    return text
