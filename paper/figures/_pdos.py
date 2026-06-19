"""Parse CP2K MO-projected PDOS files (Exp.7) for Electron-style DOS panels."""
from __future__ import annotations
import re
from dataclasses import dataclass
from pathlib import Path
import numpy as np

HA_TO_EV = 27.211386245988

@dataclass(frozen=True)
class PdosSeries:
    energy_ev: np.ndarray
    pi_weight: np.ndarray
    fermi_ev: float
    source: str

def parse_pdos(path: Path) -> PdosSeries:
    fermi_ha = 0.0
    energies_ha: list[float] = []
    pi_weights: list[float] = []
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("#") and "E(Fermi)" in line:
            m = re.search(r"E\(Fermi\)\s*=\s*([-+]?\d+\.\d+)", line)
            if m:
                fermi_ha = float(m.group(1))
            continue
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        if len(parts) < 8:
            continue
        try:
            e_ha = float(parts[1])
            py, pz, px = float(parts[4]), float(parts[5]), float(parts[6])
        except ValueError:
            continue
        energies_ha.append(e_ha)
        pi_weights.append(px + py + pz)
    e_ha = np.array(energies_ha)
    pi = np.array(pi_weights)
    order = np.argsort(e_ha)
    e_ha, pi = e_ha[order], pi[order]
    fermi_ev = fermi_ha * HA_TO_EV
    energy_ev = e_ha * HA_TO_EV - fermi_ev
    return PdosSeries(energy_ev=energy_ev, pi_weight=pi, fermi_ev=fermi_ev, source=path.name)

def gaussian_dos(energy_ev, weights, grid, sigma_ev=0.08):
    dos = np.zeros_like(grid, dtype=float)
    norm = 1.0 / (sigma_ev * np.sqrt(2 * np.pi))
    for e, w in zip(energy_ev, weights):
        dos += w * norm * np.exp(-0.5 * ((grid - e) / sigma_ev) ** 2)
    return dos
