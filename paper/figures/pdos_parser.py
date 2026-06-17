"""Parse CP2K MO-projected PDOS files (Exp. 7)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import numpy as np

HA_TO_EV = 27.211386245988


@dataclass
class PdosRecord:
    path: Path
    dopant: str
    strain_pct: float
    kind: str
    e_fermi_au: float
    eigenvalues_au: np.ndarray
    occupations: np.ndarray
    p_pi_weight: np.ndarray

    @property
    def homo_au(self) -> float:
        occ = self.occupations > 0.5
        if not np.any(occ):
            return float("nan")
        return float(np.max(self.eigenvalues_au[occ]))

    @property
    def lumo_au(self) -> float:
        occ = self.occupations > 0.5
        unocc = ~occ
        if not np.any(unocc):
            return float("nan")
        homo = self.homo_au
        above = self.eigenvalues_au[unocc & (self.eigenvalues_au > homo - 1e-6)]
        return float(np.min(above)) if len(above) else float("nan")

    @property
    def gap_ev(self) -> float:
        return (self.lumo_au - self.homo_au) * HA_TO_EV

    @property
    def homo_ev_vs_fermi(self) -> float:
        return (self.homo_au - self.e_fermi_au) * HA_TO_EV


def _parse_strain_dopant(stem: str) -> Tuple[float, str]:
    m = re.match(r"elec_(neg|pos)(\d+)p(\d+)_(.+)", stem)
    if not m:
        raise ValueError(stem)
    sign = -1 if m.group(1) == "neg" else 1
    strain = sign * (int(m.group(2)) + int(m.group(3)) / 10.0)
    dop = m.group(4).split("-")[0]
    return strain, dop


def parse_pdos(path: Path) -> PdosRecord:
    path = Path(path)
    base = path.stem.split("-k")[0]
    strain, dop = _parse_strain_dopant(base)
    kind = "C"
    e_fermi = 0.0
    evals, occs, p_pi = [], [], []
    with open(path) as f:
        for line in f:
            if line.startswith("# Projected DOS"):
                m = re.search(r"E\(Fermi\)\s*=\s*([-\d.]+)", line)
                if m:
                    e_fermi = float(m.group(1))
                m2 = re.search(r"atomic kind (\w+)", line)
                if m2:
                    kind = m2.group(1)
            elif line.startswith("#") or not line.strip():
                continue
            else:
                parts = line.split()
                evals.append(float(parts[1]))
                occs.append(float(parts[2]))
                if len(parts) >= 7:
                    p_pi.append(float(parts[4]) + float(parts[5]) + float(parts[6]))
                else:
                    p_pi.append(0.0)
    return PdosRecord(
        path=path,
        dopant=dop,
        strain_pct=strain,
        kind=kind,
        e_fermi_au=e_fermi,
        eigenvalues_au=np.array(evals),
        occupations=np.array(occs),
        p_pi_weight=np.array(p_pi),
    )


def load_exp7_pdos(results_dir: Path) -> List[PdosRecord]:
    return [parse_pdos(p) for p in sorted(Path(results_dir).glob("elec_*.pdos"))]


def gaussian_dos(eigenvalues_ev, weights, occupations, grid_ev, sigma=0.08):
    dos = np.zeros_like(grid_ev)
    for e, w, occ in zip(eigenvalues_ev, weights, occupations):
        if occ < 0.5:
            continue
        dos += w * np.exp(-0.5 * ((grid_ev - e) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))
    return dos


def records_for(records: Iterable[PdosRecord], *, dopant: str, strain_pct: float, kind: str = "C"):
    for r in records:
        if r.dopant == dopant and abs(r.strain_pct - strain_pct) < 0.01 and r.kind == kind:
            return r
    return None


def homo_lumo_ev(record: PdosRecord) -> tuple[float, float]:
    """Return (HOMO, LUMO) in eV relative to Fermi level."""
    ef = record.e_fermi_au
    return (record.homo_au - ef) * HA_TO_EV, (record.lumo_au - ef) * HA_TO_EV


def gap_matrix(
    records: Iterable[PdosRecord],
    dopants: Sequence[str],
    strains: Sequence[float],
    *,
    kind: str = "C",
) -> np.ndarray:
    out = np.full((len(dopants), len(strains)), np.nan)
    for i, dop in enumerate(dopants):
        for j, s in enumerate(strains):
            r = records_for(records, dopant=dop, strain_pct=s, kind=kind)
            if r:
                out[i, j] = r.gap_ev
    return out
