"""Phase-diagram style maps for strain-doping-electronic coupling."""

from __future__ import annotations

from typing import Iterable, Sequence

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata

from pdos_parser import records_for

REGIME_COLORS = {"metallic": "#FFE566", "narrow": "#8FD18E", "wide": "#6BAED6"}
REGIME_BOUNDS = (0.08, 0.45)


def plot_gap_strain_phase_diagram(
    ax,
    records: Iterable,
    *,
    dopants: Sequence[str] = ("pristine", "B", "N", "P"),
    strains: Sequence[float] = (-5.0, 0.0, 5.0),
    dop_colors: dict | None = None,
) -> None:
    dop_colors = dop_colors or {"pristine": "#666666", "B": "#0055AA", "N": "#CC0033", "P": "#FF8800"}
    dop_labels = {"pristine": "Pristine", "B": "B", "N": "N", "P": "P"}

    xs, ys, gs = [], [], []
    series: dict[str, list[tuple[float, float]]] = {}
    for dop in dopants:
        series[dop] = []
        for eps in strains:
            r = records_for(records, dopant=dop, strain_pct=float(eps), kind="C")
            if not r:
                continue
            g = r.gap_ev
            xs.append(float(eps))
            ys.append(list(dopants).index(dop))
            gs.append(g)
            series[dop].append((float(eps), g))

    if not xs:
        return

    xg = np.linspace(-5.5, 5.5, 220)
    yg = np.linspace(-0.35, len(dopants) - 0.65, 220)
    XI, YI = np.meshgrid(xg, yg)
    ZI = griddata((xs, ys), gs, (XI, YI), method="cubic")
    ZI = np.clip(np.nan_to_num(ZI, nan=0.0), 0.0, 1.8)

    lo, hi = REGIME_BOUNDS
    ax.contourf(XI, YI, ZI, levels=[0, lo, hi, 1.8], colors=[REGIME_COLORS["metallic"], REGIME_COLORS["narrow"], REGIME_COLORS["wide"]], alpha=0.55, zorder=0)
    cs = ax.contour(XI, YI, ZI, levels=[lo, hi], colors="#222222", linewidths=1.0, zorder=1)
    ax.clabel(cs, inline=True, fontsize=6, fmt=lambda v: f"{v:.2f} eV")

    for dop, pts in series.items():
        if not pts:
            continue
        ex = np.array([p[0] for p in pts])
        gy = np.full_like(ex, list(dopants).index(dop), dtype=float)
        ax.plot(ex, gy, "o-", color=dop_colors[dop], lw=1.6, ms=7, mfc="white", mew=1.2, zorder=4)
        for e, g in zip(ex, [p[1] for p in pts]):
            ax.annotate(f"{g:.2f}", (e, list(dopants).index(dop)), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=5.5, color=dop_colors[dop])

    b0 = next((g for e, g in series.get("B", []) if abs(e) < 0.01), None)
    if b0 is not None and b0 < lo:
        idx = list(dopants).index("B")
        ax.scatter([0], [idx], s=120, facecolors="none", edgecolors="#CC0033", linewidths=1.5, zorder=5)
        ax.text(0.3, idx + 0.35, f"near-gap B\n$g={b0:.2f}$ eV", fontsize=6, color="#CC0033", fontweight="bold")

    ax.axvline(3.0, color="#CC0033", ls=(0, (4, 3)), lw=0.9, zorder=2)
    ax.text(3.05, len(dopants) - 0.55, r"Exp.~10 ($+3$\%)", fontsize=6, color="#CC0033", rotation=90, va="top")

    ax.set_xlim(-5.8, 5.8)
    ax.set_ylim(-0.45, len(dopants) - 0.55)
    ax.set_xlabel(r"Biaxial strain $\varepsilon$ (\%)")
    ax.set_yticks(range(len(dopants)))
    ax.set_yticklabels([dop_labels[d] for d in dopants])
    ax.set_ylabel("Dopant channel")
    ax.legend(
        [plt.Line2D([0], [0], color=c, lw=6) for c in REGIME_COLORS.values()],
        [r"$g<0.08$ eV", r"$0.08$–$0.45$ eV", r"$g>0.45$ eV"],
        loc="upper right",
        fontsize=6,
        frameon=True,
        edgecolor="#333",
        title="Gap regime",
        title_fontsize=6.5,
    )
