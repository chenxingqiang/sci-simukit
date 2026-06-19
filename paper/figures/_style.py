"""PRL + Capobianco Electron (Nano Lett.) visual style."""

from __future__ import annotations

import matplotlib as mpl
from matplotlib.axes import Axes

# Single-column PRL width
PRL_WIDTH_IN = 3.375
PRL_HEIGHT_IN = 1.95
PRB_WIDTH_IN = 7.0
PRB_HEIGHT_IN = 2.15

# Electron Fig. 2 palette — valence purple, conduction teal
COLOR_VBM = "#7B4FB3"
COLOR_CBM = "#2BAFA3"
COLOR_TOTAL = "#333333"

DOPANT_COLORS = {
    "pristine": "#666666",
    "B": COLOR_CBM,
    "N": "#C45C26",
    "P": "#5C8A3C",
}

DOPANT_MARKERS = {"B": "o", "N": "s", "P": "^", "pristine": "D"}


def apply_prl_style() -> None:
    mpl.rcParams.update(
        {
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "font.family": "sans-serif",
            "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
            "font.size": 7,
            "mathtext.fontset": "dejavusans",
            "axes.labelsize": 7,
            "axes.titlesize": 6.5,
            "xtick.labelsize": 6,
            "ytick.labelsize": 6,
            "legend.fontsize": 5.5,
            "axes.linewidth": 0.55,
            "lines.linewidth": 0.85,
            "lines.markersize": 3.5,
            "xtick.major.width": 0.55,
            "ytick.major.width": 0.55,
            "xtick.major.size": 2.2,
            "ytick.major.size": 2.2,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def apply_prb_style() -> None:
    """PRB reprint width (~7 in) — larger type and markers for print legibility."""
    mpl.rcParams.update(
        {
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "font.family": "sans-serif",
            "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
            "font.size": 8,
            "mathtext.fontset": "dejavusans",
            "axes.labelsize": 8.5,
            "axes.titlesize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 6.5,
            "axes.linewidth": 0.65,
            "lines.linewidth": 1.0,
            "lines.markersize": 4.5,
            "xtick.major.width": 0.65,
            "ytick.major.width": 0.65,
            "xtick.major.size": 2.8,
            "ytick.major.size": 2.8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def apply_si_style() -> None:
    """Supplemental Material figures — match PRB readability."""
    apply_prb_style()


def style_axes(ax: Axes, grid: bool = False) -> None:
    """Nano Lett. clean axes — L/B spines only."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.55)
    ax.spines["bottom"].set_linewidth(0.55)
    if grid:
        ax.grid(True, axis="y", color="#EBEBEB", linewidth=0.35, zorder=0)
    ax.set_axisbelow(True)


def panel_label(ax: Axes, label: str, *, fontsize: float | None = None) -> None:
    """Bold (a)–(d) at top-left inside panel — Electron alignment."""
    fs = fontsize if fontsize is not None else mpl.rcParams["font.size"] + 0.5
    ax.text(
        0.03,
        0.97,
        f"({label})",
        transform=ax.transAxes,
        fontsize=fs,
        fontweight="bold",
        va="top",
        ha="left",
        zorder=10,
        bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none", alpha=0.75),
    )
