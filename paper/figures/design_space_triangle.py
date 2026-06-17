"""Origin-style design-space triangle for strain-doping coupling."""

from __future__ import annotations

from typing import Iterable, Sequence

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
    rows = _rows(sdc)
    s_vals = [r["s"] for r in rows]
    S_vals = [r["S"] for r in rows]
    s_max = max(s_vals) * 1.25
    S_lo, S_hi = min(S_vals) * 1.15, max(S_vals) * 1.2

    # Triangle vertices (Ref, strain end-member, coupled corner)
    ref = np.array([0.0, 0.0])
    strain_end = np.array([s_max, 0.0])
    coupled_corner = np.array([s_max, S_hi])

    ax.plot([ref[0], strain_end[0]], [ref[1], strain_end[1]], "k--", lw=1.0, dashes=(4, 3), zorder=1)
    ax.plot([ref[0], coupled_corner[0]], [ref[1], coupled_corner[1]], "k--", lw=1.0, dashes=(4, 3), zorder=1)
    ax.plot([strain_end[0], coupled_corner[0]], [strain_end[1], coupled_corner[1]], "k--", lw=1.0, dashes=(4, 3), zorder=1)
    ax.plot([ref[0], coupled_corner[0]], [ref[1], coupled_corner[1]], "k:", lw=0.9, alpha=0.55, zorder=1)

    ax.text(s_max * 0.42, S_hi * 0.92, "coupled\n$(\\epsilon,\\delta)$", fontsize=7, ha="center", style="italic")
    ax.text(s_max * 0.55, -0.04 * (S_hi - S_lo), "sequential strain scan", fontsize=7, style="italic")
    ax.text(-0.08 * s_max, S_hi * 0.55, "additive\n$\\mathcal{S}=0$", fontsize=7, rotation=90, va="center", style="italic")

    ax.axhline(0, color="#666666", lw=0.8, ls=(0, (5, 4)), zorder=1)
    ax.text(s_max * 0.02, 0.02 * (S_hi - S_lo), r"$\mathcal{S}=0$", fontsize=7, color="#444444")

    # Reference reservoirs (Origin-style large markers)
    ax.scatter([0], [0], s=220, facecolors="white", edgecolors="#000", linewidths=1.2, zorder=4)
    ax.text(0, 0.06 * (S_hi - S_lo), "Ref", fontsize=8, fontweight="bold", ha="center")
    ax.scatter([s_max * 0.85], [0], s=220, facecolors="white", edgecolors="#000", linewidths=1.2, zorder=4)
    ax.text(s_max * 0.85, 0.06 * (S_hi - S_lo), r"$\varepsilon$", fontsize=8, fontweight="bold", ha="center")

    # Data: strain vs S; marker size ~ n
    for r in rows:
        ms = 35 + 18 * r["n"]
        ax.scatter(
            r["s"],
            r["S"],
            s=ms,
            c=DOP_COLORS[r["dop"]],
            edgecolors="#000",
            linewidths=0.7,
            alpha=0.92,
            zorder=5,
        )
        if r["n"] == highlight_n:
            ax.annotate(
                r["dop"],
                (r["s"], r["S"]),
                textcoords="offset points",
                xytext=(6, 5),
                fontsize=7,
                fontweight="bold",
                color=DOP_COLORS[r["dop"]],
            )
            # Vertical arrow: additive point (S=0) -> actual S
            ax.add_patch(
                FancyArrowPatch(
                    (r["s"], 0),
                    (r["s"], r["S"]),
                    arrowstyle="-|>",
                    mutation_scale=9,
                    lw=1.0,
                    color=DOP_COLORS[r["dop"]],
                    alpha=0.75,
                    zorder=3,
                )
            )

    ax.set_xlabel(r"Strain-only $\Delta E$ (meV/atom)")
    ax.set_ylabel(r"Synergy $\mathcal{S}$ (meV/atom)")
    ax.set_xlim(-0.12 * s_max, s_max * 1.08)
    ax.set_ylim(S_lo, S_hi * 1.05)

    # Shaded physics zones
    ax.axhspan(S_lo, 0, color="#0055AA", alpha=0.06, zorder=0)
    ax.axhspan(0, S_hi, color="#CC0033", alpha=0.06, zorder=0)
    ax.text(0.98, 0.08, "cooperative\nstabilization", transform=ax.transAxes, ha="right", fontsize=6.5, color="#0055AA")
    ax.text(0.98, 0.92, "cooperative\ndestabilization", transform=ax.transAxes, ha="right", fontsize=6.5, color="#CC0033")

    handles = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markeredgecolor="#000", markersize=7, label=d)
        for d, c in DOP_COLORS.items()
    ]
    handles.append(plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#888", markeredgecolor="#000", markersize=4, label="size $\\propto n$"))
    ax.legend(handles=handles, loc="lower left", fontsize=7, frameon=True, edgecolor="#333")
