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


def plot_pdos_deconvolution_xps(
    ax,
    records: Iterable[PdosRecord],
    *,
    dopant: str = "N",
    strain_pct: float = 5.0,
    e_min: float = -5.0,
    e_max: float = 1.5,
    sigma: float = 0.09,
) -> None:
    """XPS-style π-PDOS deconvolution: C framework + dopant site + Sum."""
    r_c = records_for(records, dopant=dopant, strain_pct=strain_pct, kind="C")
    r_d = records_for(records, dopant=dopant, strain_pct=strain_pct, kind=dopant)
    if not r_c:
        return
    grid = np.linspace(e_min, e_max, 500)
    ev_c = (r_c.eigenvalues_au - r_c.e_fermi_au) * HA_TO_EV
    dos_c_val = gaussian_dos(ev_c, r_c.p_pi_weight, r_c.occupations, grid, sigma=sigma, mode="occupied")
    dos_c_cond = gaussian_dos(ev_c, r_c.p_pi_weight, r_c.occupations, grid, sigma=sigma, mode="unoccupied")
    dos_dop = np.zeros_like(grid)
    if r_d:
        ev_d = (r_d.eigenvalues_au - r_d.e_fermi_au) * HA_TO_EV
        dos_dop = gaussian_dos(ev_d, r_d.p_pi_weight, r_d.occupations, grid, sigma=sigma, mode="all")
    dos_sum = dos_c_val + dos_c_cond + dos_dop
    ymax = max(dos_sum.max(), 1e-6) * 1.18

    # Raw MO sticks as scatter (occupied, near window)
    occ = r_c.occupations > 0.5
    mask = occ & (ev_c >= e_min) & (ev_c <= e_max)
    raw_y = r_c.p_pi_weight[mask] * ymax * 0.85
    ax.scatter(ev_c[mask], raw_y, s=8, c="#999999", edgecolors="none", alpha=0.55, zorder=2, label="Raw")

    # Component peaks with shaded fills (XPS style)
    ax.fill_between(grid, 0, dos_c_val, color="#0055AA", alpha=0.32, zorder=3)
    ax.plot(grid, dos_c_val, color="#0055AA", lw=1.2, label=r"C $\pi$ (valence)")
    if r_d and dos_dop.max() > 0:
        ax.fill_between(grid, 0, dos_dop, color="#2E8B57", alpha=0.32, zorder=4)
        ax.plot(grid, dos_dop, color="#2E8B57", lw=1.2, label=f"{dopant} site $\\pi$")
    ax.fill_between(grid, 0, dos_c_cond, color="#7B68EE", alpha=0.25, zorder=3)
    ax.plot(grid, dos_c_cond, color="#7B68EE", lw=1.0, ls="--", label=r"C $\pi$ (conduction)")
    ax.plot(grid, dos_sum, color="#CC0033", lw=2.2, label="Sum", zorder=6)
    ax.axhline(0, color="#555555", lw=1.0, zorder=1, label="BG")

    homo, lumo = homo_lumo_ev(r_c)
    ax.axvline(0, color="#000", ls=(0, (4, 4)), lw=0.7, alpha=0.6)
    if e_min < homo < e_max:
        ax.axvline(homo, color="#0055AA", ls=":", lw=0.8, alpha=0.7)
    if e_min < lumo < e_max:
        ax.axvline(lumo, color="#7B68EE", ls=":", lw=0.8, alpha=0.7)

    ax.set_xlabel(r"Binding energy $E-E_F$ (eV)")
    ax.set_ylabel(r"Intensity (arb.)")
    ax.set_xlim(e_min, e_max)
    ax.set_ylim(0, ymax)
    ax.set_title(f"{dopant}-doped, $\\varepsilon={strain_pct:+.0f}$\\%", fontsize=8, fontweight="bold", pad=3)
    ax.legend(loc="upper right", fontsize=6, frameon=True, edgecolor="#333", ncol=2, handlelength=1.4)


def plot_pdos_waterfall_stack(
    ax,
    records: Iterable[PdosRecord],
    *,
    dopants: Sequence[str] = ("pristine", "B", "N", "P"),
    strains: Sequence[float] = (-5.0, 0.0, 5.0),
    e_min: float = -4.2,
    e_max: float = 1.2,
    sigma: float = 0.09,
) -> None:
    """XRD-style stacked pi-PDOS: dopant x strain series with color gradient."""
    grid = np.linspace(e_min, e_max, 650)
    series: list[tuple[str, np.ndarray, str]] = []
    dop_short = {"pristine": "Pri", "B": "B", "N": "N", "P": "P"}
    for dop in dopants:
        for eps in strains:
            r = records_for(records, dopant=dop, strain_pct=float(eps), kind="C")
            if not r:
                continue
            ev = (r.eigenvalues_au - r.e_fermi_au) * HA_TO_EV
            dos = gaussian_dos(ev, r.p_pi_weight, r.occupations, grid, sigma=sigma, mode="all")
            tag = f"{dop_short.get(dop, dop)} $\\varepsilon={eps:+.0f}$\\%"
            series.append((tag, dos, dop))

    if not series:
        return

    peak = max(float(d.max()) for _, d, _ in series) or 1.0
    step = peak * 1.25
    cmap = plt.cm.plasma
    n = len(series)

    for i, (tag, dos, dop) in enumerate(series):
        y0 = i * step
        color = cmap(i / max(n - 1, 1))
        curve = dos / peak + y0
        ax.plot(grid, curve, color=color, lw=0.85, solid_capstyle="round", zorder=2)
        ax.text(e_max + 0.06, y0 + 0.45, tag, fontsize=5.2, va="center", color=color, clip_on=False)

    ax.axvline(0, color="#444444", ls=(0, (4, 3)), lw=0.7, zorder=1)
    ax.set_xlim(e_min, e_max)
    ax.set_ylim(-step * 0.15, n * step + step * 0.35)
    ax.set_yticks([])
    ax.set_xlabel(r"$E-E_F$ (eV)")
    ax.spines["left"].set_visible(False)
    ax.tick_params(left=False)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=n - 1))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, fraction=0.025, pad=0.02, aspect=18)
    cbar.set_ticks([0, n - 1])
    cbar.set_ticklabels(["Pri $-5$\\%", f"P $+5$\\%"])
    cbar.ax.tick_params(labelsize=6)
    cbar.set_label("dopant $\\times$ strain", fontsize=7)


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
