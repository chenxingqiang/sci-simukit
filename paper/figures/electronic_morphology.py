"""Electronic-structure morphology panels (PDOS, band edges, gap maps)."""

from __future__ import annotations

from typing import Iterable, Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch

from pdos_parser import HA_TO_EV, PdosRecord, gaussian_dos, homo_lumo_ev, records_for


def plot_gap_heatmap(ax, matrix, dopant_labels, strain_labels, *, vmax=None):
    cmap = LinearSegmentedColormap.from_list("gap", ["#CC0033", "#FFDD88", "#0055AA"], N=256)
    vmax = float(vmax if vmax is not None else np.nanmax(matrix) * 1.05)
    im = ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=0.0, vmax=max(vmax, 0.05), origin="upper")
    ax.set_xticks(np.arange(len(strain_labels)))
    ax.set_xticklabels(strain_labels)
    ax.set_yticks(np.arange(len(dopant_labels)))
    ax.set_yticklabels(dopant_labels)
    ax.set_xlabel(r"Biaxial strain $\varepsilon$ (\%)")
    ax.set_ylabel("System")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = matrix[i, j]
            if np.isnan(val):
                continue
            color = "white" if val > 0.55 * vmax else "#111111"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=7, fontweight="bold", color=color)
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label(r"Gap (eV)", fontsize=8)


def plot_band_edge_morph(ax, record, *, color, title=""):
    homo, lumo = homo_lumo_ev(record)
    gap = lumo - homo
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(homo - 0.35, lumo + 0.35)
    ax.axhline(0, color="#000000", ls=(0, (4, 4)), lw=0.8, zorder=1)
    ax.plot([0.35, 0.65], [homo, homo], color=color, lw=3.2, solid_capstyle="round", zorder=3)
    ax.plot([0.35, 0.65], [lumo, lumo], color=color, lw=3.2, ls=(0, (1, 1.2)), zorder=3)
    ax.add_patch(FancyArrowPatch((1.05, homo), (1.05, lumo), arrowstyle="<->", mutation_scale=10, lw=1.1, color="#333333"))
    ax.text(1.12, (homo + lumo) / 2, f"{gap:.2f}", va="center", fontsize=7, fontweight="bold")
    ax.text(0.5, lumo + 0.18, "LUMO", ha="center", fontsize=6.5, color=color)
    ax.text(0.5, homo - 0.18, "HOMO", ha="center", fontsize=6.5, color=color)
    ax.set_xticks([])
    ax.set_ylabel(r"$E-E_F$ (eV)")
    if title:
        ax.set_title(title, fontsize=7.5, fontweight="bold", color=color, pad=2)
    ax.spines["bottom"].set_visible(False)


def plot_pdos_with_gap(ax, record, *, color, label, grid_ev=None, sigma=0.10):
    if grid_ev is None:
        grid_ev = np.linspace(-3.0, 1.2, 400)
    ev = (record.eigenvalues_au - record.e_fermi_au) * HA_TO_EV
    dos = gaussian_dos(ev, record.p_pi_weight, record.occupations, grid_ev, sigma=sigma)
    homo, lumo = homo_lumo_ev(record)
    ax.fill_between(grid_ev, 0, dos, color=color, alpha=0.22, zorder=1)
    ax.plot(grid_ev, dos, color=color, lw=1.5, label=label, zorder=2)
    ax.axvspan(homo, lumo, color=color, alpha=0.12, zorder=0)
    ax.axvline(homo, color=color, lw=0.9, ls=":", alpha=0.9)
    ax.axvline(lumo, color=color, lw=0.9, ls=":", alpha=0.9)


def plot_mo_stick_spectrum(ax, records, *, strain_pct=0.0, dopants=("N", "B", "P"), kind_map=None):
    kind_map = kind_map or {"N": "N", "B": "B", "P": "P"}
    offsets = {"N": 0.0, "B": 0.35, "P": 0.70}
    colors = {"N": "#CC0033", "B": "#0055AA", "P": "#FF8800"}
    for dop in dopants:
        r = records_for(records, dopant=dop, strain_pct=strain_pct, kind=kind_map[dop])
        if not r:
            continue
        ev = (r.eigenvalues_au - r.e_fermi_au) * HA_TO_EV
        y0 = offsets.get(dop, 0.0)
        for e, occ, w in zip(ev, r.occupations, r.p_pi_weight):
            if abs(e) > 6.5:
                continue
            lw = 0.6 + 2.8 * min(w, 1.0)
            ls = "-" if occ > 0.5 else (0, (2, 1.5))
            alpha = 0.95 if occ > 0.5 else 0.55
            ax.plot([e, e], [y0, y0 + 0.22], color=colors[dop], lw=lw, ls=ls, alpha=alpha, solid_capstyle="round")
        ax.text(-5.8, y0 + 0.11, dop, fontsize=7, fontweight="bold", color=colors[dop], va="center")
    ax.axvline(0, color="#000", ls=(0, (4, 4)), lw=0.8)
    ax.set_xlabel(r"Dopant MO $E-E_F$ (eV)")
    ax.set_yticks([])
    ax.set_xlim(-6.5, 2.2)
    ax.set_ylim(-0.1, 1.05)
