"""Origin-style design-space triangle for strain-doping coupling."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch

HA_TO_MEV = 27.211386245988 * 1000.0
DOP_COLORS = {"B": "#0055AA", "N": "#CC0033", "P": "#FF8800"}


def _rows(sdc: dict) -> list[dict]:
    out = []
    for r in sdc["synergy_energy_per_atom"]:
        out.append(
            {
                "n": r["n_molecules"],
                "dop": r["dopant"],
                "s": r["strain_only_delta"] * HA_TO_MEV,
                "d": r["doping_only_delta"] * HA_TO_MEV,
                "S": r["synergy_S"] * HA_TO_MEV,
            }
        )
    return out


def plot_synergy_design_triangle(ax, sdc: dict, *, highlight_n: int = 4) -> None:
    """Strain-only (x) vs synergy S (y) with additive-limit framework."""
    ax.set_facecolor("#FAFAFA")
    rows = _rows(sdc)
    s_vals = [r["s"] for r in rows]
    S_vals = [r["S"] for r in rows]
    s_max = max(s_vals) * 1.22
    S_lo, S_hi = min(S_vals) * 1.12, max(S_vals) * 1.18

    ax.axhspan(S_lo, 0, color="#0055AA", alpha=0.08, zorder=0)
    ax.axhspan(0, S_hi, color="#CC0033", alpha=0.08, zorder=0)

    ref = np.array([0.0, 0.0])
    strain_end = np.array([s_max, 0.0])
    coupled_corner = np.array([s_max, S_hi])

    ax.plot([ref[0], strain_end[0]], [ref[1], strain_end[1]], "k--", lw=0.9, dashes=(4, 3), zorder=1)
    ax.plot([ref[0], coupled_corner[0]], [ref[1], coupled_corner[1]], "k--", lw=0.9, dashes=(4, 3), zorder=1)
    ax.plot([strain_end[0], coupled_corner[0]], [strain_end[1], coupled_corner[1]], "k--", lw=0.9, dashes=(4, 3), zorder=1)
    ax.plot([ref[0], coupled_corner[0]], [ref[1], coupled_corner[1]], "k:", lw=0.8, alpha=0.45, zorder=1)

    ax.text(s_max * 0.40, S_hi * 0.90, "coupled\n$(\\epsilon,\\delta)$", fontsize=6.5, ha="center", style="italic", color="#333")
    ax.text(s_max * 0.52, 0.04 * (S_hi - S_lo), "sequential strain scan", fontsize=6.5, style="italic", color="#333")
    ax.text(-0.06 * s_max, S_hi * 0.52, "additive\n$\\mathcal{S}=0$", fontsize=6.5, rotation=90, va="center", style="italic", color="#333")

    ax.axhline(0, color="#555555", lw=0.75, ls=(0, (5, 4)), zorder=1)
    ax.text(s_max * 0.03, 0.03 * (S_hi - S_lo), r"$\mathcal{S}=0$", fontsize=6.5, color="#444444")

    ax.scatter([0], [0], s=200, facecolors="white", edgecolors="#000", linewidths=1.0, zorder=4)
    ax.text(0, 0.055 * (S_hi - S_lo), "Ref", fontsize=7.5, fontweight="bold", ha="center")
    ax.scatter([s_max * 0.88], [0], s=200, facecolors="white", edgecolors="#000", linewidths=1.0, zorder=4)
    ax.text(s_max * 0.88, 0.055 * (S_hi - S_lo), r"$\varepsilon$", fontsize=7.5, fontweight="bold", ha="center")

    for dop in DOP_COLORS:
        pts = sorted([r for r in rows if r["dop"] == dop], key=lambda r: r["n"])
        if len(pts) >= 2:
            ax.plot(
                [p["s"] for p in pts],
                [p["S"] for p in pts],
                color=DOP_COLORS[dop],
                lw=0.9,
                alpha=0.35,
                zorder=2,
                solid_capstyle="round",
            )

    for r in rows:
        ms = 32 + 16 * r["n"]
        ax.scatter(
            r["s"],
            r["S"],
            s=ms,
            c=DOP_COLORS[r["dop"]],
            edgecolors="#000",
            linewidths=0.65,
            alpha=0.94,
            zorder=5,
        )
        if r["n"] == highlight_n:
            ax.annotate(
                f"{r['dop']}\n{r['S']:+.1f}",
                (r["s"], r["S"]),
                textcoords="offset points",
                xytext=(7, 6),
                fontsize=6.5,
                fontweight="bold",
                color=DOP_COLORS[r["dop"]],
                ha="left",
            )
            ax.add_patch(
                FancyArrowPatch(
                    (r["s"], 0),
                    (r["s"], r["S"]),
                    arrowstyle="-|>",
                    mutation_scale=8,
                    lw=0.9,
                    color=DOP_COLORS[r["dop"]],
                    alpha=0.65,
                    zorder=3,
                )
            )

    ax.set_xlabel(r"Strain-only $\Delta E$ (meV/atom)", fontsize=8)
    ax.set_ylabel(r"Synergy $\mathcal{S}$ (meV/atom)", fontsize=8)
    ax.set_xlim(-0.10 * s_max, s_max * 1.06)
    ax.set_ylim(S_lo, S_hi * 1.04)
    ax.grid(True, color="#E8E8E8", lw=0.5, zorder=0)

    ax.text(0.98, 0.07, "cooperative\nstabilization", transform=ax.transAxes, ha="right", fontsize=6, color="#0055AA", linespacing=1.05)
    ax.text(0.98, 0.93, "anti-cooperative\ndestabilization", transform=ax.transAxes, ha="right", fontsize=6, color="#CC0033", linespacing=1.05)

    handles = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markeredgecolor="#000", markersize=7, label=d)
        for d, c in DOP_COLORS.items()
    ]
    handles.append(
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#888", markeredgecolor="#000", markersize=4, label=r"size $\propto n$")
    )
    ax.legend(handles=handles, loc="upper left", fontsize=6.5, frameon=True, edgecolor="#333", framealpha=0.95)
