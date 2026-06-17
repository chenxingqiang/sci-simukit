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


def plot_alpha_synergy_phase_map(ax, table1: dict, audit: dict, *, n: int = 4, strain_pct: float = 3.0) -> None:
    """Mechanics (alpha) vs non-additivity (S) phase map at fixed n, strain."""
    ax.set_facecolor("#FAFAFA")
    rows = [r for r in audit["synergy_table"] if r["n_molecules"] == n and abs(r["strain_pct"] - strain_pct) < 0.01]
    if not rows:
        return

    alphas, ss, dops = [], [], []
    for r in sorted(rows, key=lambda x: x["dopant"]):
        dop = r["dopant"]
        sys_key = dop if dop in table1["systems"] else dop
        alphas.append(table1["systems"][sys_key]["alpha_meV_per_pct"])
        ss.append(r["synergy_S_meV_per_atom"])
        dops.append(dop)

    xlim = (-340, 75)
    ylo, yhi = min(ss) * 1.15, max(max(ss) * 1.22, 4.5)

    ax.axhline(0, color="#333333", lw=0.85, zorder=1)
    ax.axvline(0, color="#333333", lw=0.85, zorder=1)
    ax.fill_between(xlim, 0, yhi, color="#CC0033", alpha=0.07, zorder=0)
    ax.fill_between(xlim, ylo, 0, color="#0055AA", alpha=0.07, zorder=0)
    ax.grid(True, color="#E8E8E8", lw=0.5, zorder=0)

    ax.text(0.04, 0.96, r"$\mathcal{S}>0$ (anti-cooperative)", transform=ax.transAxes, fontsize=6, color="#CC0033", va="top", fontweight="bold")
    ax.text(0.04, 0.04, r"$\mathcal{S}<0$ (cooperative)", transform=ax.transAxes, fontsize=6, color="#0055AA", va="bottom", fontweight="bold")
    ax.text(0.78, 0.54, r"$\alpha>0$", transform=ax.transAxes, fontsize=6.5, color="#444", fontweight="bold")
    ax.text(0.12, 0.54, r"$\alpha<0$", transform=ax.transAxes, fontsize=6.5, color="#444", fontweight="bold")

    colors = {"B": "#0055AA", "N": "#CC0033", "P": "#FF8800"}
    offsets = {"B": (8, 4), "N": (8, -12), "P": (-42, 6)}
    for a, s, dop in zip(alphas, ss, dops):
        ax.scatter(a, s, s=120, c=colors[dop], edgecolors="#000", linewidths=0.85, zorder=4)
        ox, oy = offsets.get(dop, (7, 5))
        ax.annotate(
            f"{dop}\n$\\alpha={a:.0f}$\n$\\mathcal{{S}}={s:+.1f}$",
            (a, s),
            textcoords="offset points",
            xytext=(ox, oy),
            fontsize=6,
            fontweight="bold",
            color=colors[dop],
            ha="left",
            linespacing=1.05,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#CCCCCC", alpha=0.92, lw=0.5),
        )

    ax.set_xlim(xlim)
    ax.set_ylim(ylo, yhi)
    ax.set_xlabel(r"Strain stiffness $\alpha$ (meV/\%)", fontsize=8)
    ax.set_ylabel(r"$\mathcal{S}$ at $n=4$, $\varepsilon=+3$\% (meV/atom)", fontsize=8)
    ax.set_title(r"Mechanical–non-additive phase map", fontsize=8.5, fontweight="bold", loc="left", pad=6)

