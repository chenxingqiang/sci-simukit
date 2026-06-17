"""Origin-style floating range bars for non-additive energy decomposition."""

from __future__ import annotations

from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

HA_TO_MEV = 27.211386245988 * 1000.0
COLOR_SEQ = "#666666"
COLOR_SYN = "#CC0033"
DOP_COLORS = {"B": "#0055AA", "N": "#CC0033", "P": "#FF8800"}


def _row_mev(row: dict) -> tuple[float, float, float]:
    eps = row["strain_only_delta"] * HA_TO_MEV
    dop = row["doping_only_delta"] * HA_TO_MEV
    s_val = row["synergy_S"] * HA_TO_MEV
    return eps, dop, s_val


def _draw_floating_bar(
    ax,
    x: float,
    y0: float,
    y1: float,
    *,
    color: str,
    width: float = 0.34,
) -> None:
    lo, hi = (y0, y1) if y0 <= y1 else (y1, y0)
    if hi - lo < 1e-9:
        hi = lo + 1e-6
    ax.add_patch(
        Rectangle(
            (x - width / 2, lo),
            width,
            hi - lo,
            facecolor=color,
            edgecolor="#111111",
            linewidth=0.75,
            zorder=3,
        )
    )
    ax.text(x, hi, f"{hi:.1f}", ha="center", va="bottom", fontsize=5.5, fontweight="bold")
    ax.text(x, lo, f"{lo:.1f}", ha="center", va="top", fontsize=5.5, fontweight="bold")


def plot_nonadditive_floating_bars(
    ax,
    sdc: dict,
    *,
    n: int = 4,
    dopants: Sequence[str] = ("B", "N", "P"),
    strain_pct: float = 3.0,
) -> None:
    """
    Yield-gap style dual-panel floating bars (Origin paradigm).

    Upper: sequential strain + doping legs (large energy scale).
    Lower: synergy gap S floating from additive endpoint (meV scale, readable).
    """
    rows = {
        r["dopant"]: r
        for r in sdc["synergy_energy_per_atom"]
        if r["n_molecules"] == n and abs(r["strain_pct"] - strain_pct) < 0.01
    }
    if not rows:
        return

    ax.axis("off")
    ax_main = ax.inset_axes([0.02, 0.46, 0.96, 0.50])
    ax_gap = ax.inset_axes([0.02, 0.06, 0.96, 0.34])

    group_w = 5.2
    x_base = 0.0
    all_y: list[float] = [0.0]
    s_by_dop: dict[str, tuple[float, float, float]] = {}

    for dop in dopants:
        row = rows.get(dop)
        if not row:
            continue
        eps, dop_m, s_val = _row_mev(row)
        y_add = eps + dop_m
        y_cpl = y_add + s_val
        s_by_dop[dop] = (y_add, y_cpl, s_val)
        all_y.extend([0.0, eps, y_add])

        gx = x_base + np.array([0.6, 1.35, 3.0, 3.75])
        _draw_floating_bar(ax_main, gx[0], 0.0, eps, color=COLOR_SEQ)
        _draw_floating_bar(ax_main, gx[1], eps, y_add, color=COLOR_SEQ)
        _draw_floating_bar(ax_main, gx[2], 0.0, eps, color=COLOR_SEQ)
        _draw_floating_bar(ax_main, gx[3], eps, y_add, color=COLOR_SEQ)

        mid = x_base + group_w / 2
        for a, yfrac, label in [(ax_main, 1.06, dop), (ax_gap, 1.08, dop)]:
            a.text(mid, yfrac, label, transform=a.get_xaxis_transform(), ha="center", fontsize=8, fontweight="bold", color=DOP_COLORS[dop])

        ax_main.plot([x_base + 0.15, x_base + 2.1], [1.0, 1.0], transform=ax_main.get_xaxis_transform(), color="#333", lw=0.8, clip_on=False)
        ax_main.text(x_base + 1.1, 1.04, "Sequential", transform=ax_main.get_xaxis_transform(), ha="center", fontsize=6, style="italic")
        ax_main.plot([x_base + 2.55, x_base + 4.5], [1.0, 1.0], transform=ax_main.get_xaxis_transform(), color="#333", lw=0.8, clip_on=False)
        ax_main.text(x_base + 3.55, 1.04, "Additive total", transform=ax_main.get_xaxis_transform(), ha="center", fontsize=6, style="italic")

        for xi, lab in zip([gx[0], gx[1]], [r"$\varepsilon$", r"$\delta$"]):
            ax_main.text(xi, -0.12, lab, transform=ax_main.get_xaxis_transform(), ha="center", fontsize=6)
        for xi, lab in zip([gx[2], gx[3]], [r"$\varepsilon$", r"$\delta$"]):
            ax_main.text(xi, -0.12, lab, transform=ax_main.get_xaxis_transform(), ha="center", fontsize=6)

        x_base += group_w + 0.8

    ypad = max(abs(min(all_y)), abs(max(all_y))) * 0.08 + 5
    ax_main.axhline(0, color="#333333", lw=0.8, zorder=1)
    ax_main.set_xlim(-0.3, x_base - 0.5)
    ax_main.set_ylim(min(all_y) - ypad, max(all_y) + ypad)
    ax_main.set_ylabel(r"$\Delta E$ (meV/atom)", fontsize=7)
    ax_main.set_xticks([])
    ax_main.set_title(rf"Sequential decomposition @ $n={n}$, $\varepsilon=+{strain_pct:.0f}$\%", fontsize=7.5, pad=14)

    x_base = 0.0
    s_vals = []
    for dop in dopants:
        if dop not in s_by_dop:
            continue
        y_add, y_cpl, s_val = s_by_dop[dop]
        s_vals.append(s_val)
        gx = x_base + np.array([1.0, 3.2])
        _draw_floating_bar(ax_gap, gx[0], y_add, y_add, color=COLOR_SEQ, width=0.2)
        ax_gap.text(gx[0], y_add, rf"${y_add:.0f}$", ha="center", va="top", fontsize=5, color="#444")
        _draw_floating_bar(ax_gap, gx[1], y_add, y_cpl, color=COLOR_SYN)
        ax_gap.text(gx[1], y_cpl + (0.8 if s_val >= 0 else -0.8), rf"$\mathcal{{S}}={s_val:+.1f}$", ha="center", va="bottom" if s_val >= 0 else "top", fontsize=6, color=COLOR_SYN, fontweight="bold")

        ax_gap.plot([x_base + 0.2, x_base + 1.8], [1.0, 1.0], transform=ax_gap.get_xaxis_transform(), color="#333", lw=0.8, clip_on=False)
        ax_gap.text(x_base + 1.0, 1.04, "Additive end", transform=ax_gap.get_xaxis_transform(), ha="center", fontsize=6, style="italic")
        ax_gap.plot([x_base + 2.4, x_base + 4.0], [1.0, 1.0], transform=ax_gap.get_xaxis_transform(), color="#333", lw=0.8, clip_on=False)
        ax_gap.text(x_base + 3.2, 1.04, "Coupled DFT gap", transform=ax_gap.get_xaxis_transform(), ha="center", fontsize=6, style="italic")

        x_base += group_w + 0.8

    smax = max(abs(v) for v in s_vals) if s_vals else 1.0
    y_adds = [v[0] for v in s_by_dop.values()]
    zoom = max(smax * 2.8, 12.0)
    ax_gap.set_xlim(-0.3, x_base - 0.5)
    ax_gap.set_ylim(min(y_adds) - zoom, max(y_adds) + zoom)
    ax_gap.set_ylabel(r"Gap (meV/atom)", fontsize=7)
    ax_gap.set_xticks([])
    ax_gap.axhline(0, color="#333333", lw=0.6, zorder=1)

    leg = [
        plt.Rectangle((0, 0), 1, 1, facecolor=COLOR_SEQ, edgecolor="#111", label=r"Sequential ($\varepsilon+\delta$)"),
        plt.Rectangle((0, 0), 1, 1, facecolor=COLOR_SYN, edgecolor="#111", label=r"Synergy gap $\mathcal{S}$"),
    ]
    ax_gap.legend(handles=leg, loc="lower right", fontsize=5.5, frameon=True, edgecolor="#333")
