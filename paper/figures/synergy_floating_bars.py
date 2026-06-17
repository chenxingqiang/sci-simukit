"""Origin-style floating range bars for non-additive energy decomposition."""

from __future__ import annotations

from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.transforms import blended_transform_factory

HA_TO_MEV = 27.211386245988 * 1000.0
COLOR_LARGE = "#555555"
COLOR_SMALL = "#CC0033"
DOP_COLORS = {"B": "#0055AA", "N": "#CC0033", "P": "#FF8800"}


def _row_mev(row: dict) -> tuple[float, float, float]:
    eps = row["strain_only_delta"] * HA_TO_MEV
    dop = row["doping_only_delta"] * HA_TO_MEV
    s_val = row["synergy_S"] * HA_TO_MEV
    return eps, dop, s_val


def _draw_bracket(ax, x0: float, x1: float, y: float, label: str, *, fs: float = 6.5) -> None:
    trans = blended_transform_factory(ax.transData, ax.transAxes)
    h = 0.025
    ax.plot([x0, x0, x1, x1], [y, y + h, y + h, y], transform=trans, color="#222", lw=0.9, clip_on=False)
    ax.text((x0 + x1) / 2, y + h + 0.012, label, transform=trans, ha="center", va="bottom", fontsize=fs, style="italic")


def _draw_split_bar(
    ax,
    x: float,
    eps: float,
    y_add: float,
    y_cpl: float,
    *,
    width: float = 0.36,
    label_ends: bool = True,
) -> None:
    """Grey = sequential span; red = synergy gap between additive and coupled endpoints."""
    y_bot = min(eps, y_add, y_cpl)
    y_top = max(eps, y_add, y_cpl)
    s_lo, s_hi = sorted([y_add, y_cpl])
    if s_hi - s_lo < 1e-9:
        s_hi = s_lo + 1e-6
    if s_lo - y_bot > 1e-9:
        ax.add_patch(Rectangle((x - width / 2, y_bot), width, s_lo - y_bot, facecolor=COLOR_LARGE, edgecolor="#111", lw=0.75, zorder=3))
    ax.add_patch(Rectangle((x - width / 2, s_lo), width, s_hi - s_lo, facecolor=COLOR_SMALL, edgecolor="#111", lw=0.75, zorder=3))
    if y_top - s_hi > 1e-9:
        ax.add_patch(Rectangle((x - width / 2, s_hi), width, y_top - s_hi, facecolor=COLOR_LARGE, edgecolor="#111", lw=0.75, zorder=3))
    ax.axhline(y_add, color="#111", lw=0.45, ls=(0, (3, 2)), zorder=4)
    if label_ends:
        ax.text(x, y_top, f"{y_top:.1f}", ha="center", va="bottom", fontsize=5.5, fontweight="bold")
        ax.text(x, y_bot, f"{y_bot:.1f}", ha="center", va="top", fontsize=5.5, fontweight="bold")


def _draw_solid_bar(ax, x: float, y0: float, y1: float, *, color: str, width: float = 0.36) -> None:
    lo, hi = sorted([y0, y1])
    if hi - lo < 1e-9:
        hi = lo + 1e-6
    ax.add_patch(Rectangle((x - width / 2, lo), width, hi - lo, facecolor=color, edgecolor="#111", lw=0.75, zorder=3))
    ax.text(x, hi, f"{hi:.1f}", ha="center", va="bottom", fontsize=5.5, fontweight="bold")
    ax.text(x, lo, f"{lo:.1f}", ha="center", va="top", fontsize=5.5, fontweight="bold")


def _style_dual_y(ax) -> None:
    ax.tick_params(axis="y", which="both", labelleft=True, labelright=True, left=True, right=True)
    for sp in ax.spines.values():
        sp.set_linewidth(1.0)


def plot_nonadditive_floating_bars(
    ax,
    sdc: dict,
    *,
    n: int = 4,
    dopants: Sequence[str] = ("B", "N", "P"),
    strain_pct: float = 3.0,
) -> None:
    """
    Maize-yield-gap layout: 3 regions x (Sequential | Coupled DFT) x (R=eps, NR=delta).

    Broken y-axis: lower = sequential legs; upper zoom = synergy gap on coupled NR bar.
    """
    rows = {
        r["dopant"]: r
        for r in sdc["synergy_energy_per_atom"]
        if r["n_molecules"] == n and abs(r["strain_pct"] - strain_pct) < 0.01
    }
    if not rows:
        return

    ax.set_axis_off()
    ax_lo = ax.inset_axes([0.06, 0.08, 0.90, 0.52])
    ax_hi = ax.inset_axes([0.06, 0.68, 0.90, 0.26])
    _style_dual_y(ax_lo)
    _style_dual_y(ax_hi)

    group_w = 5.0
    gap = 0.75
    x_base = 0.0
    all_lo: list[float] = [0.0]
    gap_ranges: list[tuple[float, float, float]] = []

    for dop in dopants:
        row = rows.get(dop)
        if not row:
            continue
        eps, dop_m, s_val = _row_mev(row)
        y_add = eps + dop_m
        y_cpl = y_add + s_val
        all_lo.extend([0.0, eps, y_add])
        gap_ranges.append((y_add, y_cpl, s_val))

        xs = x_base + np.array([0.55, 1.30, 3.05, 3.80])
        _draw_solid_bar(ax_lo, xs[0], 0.0, eps, color=COLOR_LARGE)
        _draw_solid_bar(ax_lo, xs[1], eps, y_add, color=COLOR_LARGE)
        _draw_solid_bar(ax_lo, xs[2], 0.0, eps, color=COLOR_LARGE)
        _draw_split_bar(ax_lo, xs[3], eps, y_add, y_cpl)

        _draw_split_bar(ax_hi, xs[3], y_add, y_add, y_cpl, label_ends=True)
        ax_hi.text(
            xs[3],
            y_cpl + np.sign(s_val or 1) * 0.35,
            rf"$\mathcal{{S}}={s_val:+.1f}$",
            ha="center",
            va="bottom" if s_val >= 0 else "top",
            fontsize=5.5,
            color=COLOR_SMALL,
            fontweight="bold",
        )

        mid = x_base + group_w / 2
        ax_lo.text(mid, 1.11, dop, transform=ax_lo.get_xaxis_transform(), ha="center", fontsize=9, fontweight="bold", color=DOP_COLORS[dop])
        _draw_bracket(ax_lo, x_base + 0.12, x_base + 1.75, 1.04, "Sequential")
        _draw_bracket(ax_lo, x_base + 2.62, x_base + 4.25, 1.04, "Coupled DFT")

        for xi, lab in zip(xs[:2], [r"$\varepsilon$", r"$\delta$"]):
            ax_lo.text(xi, -0.10, lab, transform=ax_lo.get_xaxis_transform(), ha="center", fontsize=6)
        for xi, lab in zip(xs[2:], [r"$\varepsilon$", r"$\delta$"]):
            ax_lo.text(xi, -0.10, lab, transform=ax_lo.get_xaxis_transform(), ha="center", fontsize=6)

        x_base += group_w + gap

    ypad = max(abs(min(all_lo)), abs(max(all_lo))) * 0.06 + 8
    ax_lo.axhline(0, color="#333", lw=0.8, zorder=1)
    ax_lo.set_xlim(-0.2, x_base - gap + 0.2)
    ax_lo.set_ylim(min(all_lo) - ypad, max(all_lo) + ypad)
    ax_lo.set_ylabel(r"$\Delta E/N_{\mathrm{atom}}$ (meV/atom)", fontsize=7.5)
    ax_lo.set_xticks([])

    y_adds = [g[0] for g in gap_ranges]
    smax = max(abs(g[2]) for g in gap_ranges) if gap_ranges else 1.0
    zoom = max(smax * 2.2, 10.0)
    ax_hi.set_xlim(ax_lo.get_xlim())
    ax_hi.set_ylim(min(y_adds) - zoom, max(y_adds) + zoom)
    ax_hi.set_ylabel(r"Gap zoom", fontsize=7)
    ax_hi.set_xticks([])

    for a in (ax_lo, ax_hi):
        a.spines["top"].set_visible(False if a is ax_lo else True)
    ax_lo.spines["top"].set_visible(False)
    ax_hi.spines["bottom"].set_visible(False)
    ax_lo.tick_params(labeltop=False)
    ax_hi.tick_params(labelbottom=False)

    d = 0.012
    kwargs = dict(transform=ax_lo.transAxes, color="#333", clip_on=False, lw=0.9)
    ax_lo.plot((-d, +d), (1, 1), **kwargs)
    ax_lo.plot((-d, +d), (0, 0), **kwargs)
    ax_hi.plot((-d, +d), (0, 0), **kwargs)
    ax_hi.plot((-d, +d), (1, 1), **kwargs)

    leg = [
        plt.Rectangle((0, 0), 1, 1, facecolor=COLOR_LARGE, edgecolor="#111", label=r"Large sequential ($\varepsilon+\delta$)"),
        plt.Rectangle((0, 0), 1, 1, facecolor=COLOR_SMALL, edgecolor="#111", label=r"Small synergy gap $\mathcal{S}$"),
    ]
    ax_lo.legend(handles=leg, loc="lower right", fontsize=6, frameon=True, edgecolor="#333")
    ax.text(0.5, 0.98, rf"Non-additive energy gap ($n={n}$, $\varepsilon=+{strain_pct:.0f}$%)", transform=ax.transAxes, ha="center", va="top", fontsize=8, fontweight="bold")
