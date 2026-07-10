"""PRL + Electron + Nature-style panel aesthetics."""

from __future__ import annotations

import matplotlib as mpl
from matplotlib.axes import Axes

# Single-column PRL width
PRL_WIDTH_IN = 3.375
PRL_HEIGHT_IN = 1.95
PRB_WIDTH_IN = 7.0
PRB_HEIGHT_IN = 2.35

# Electron Fig. 2 palette — valence purple, conduction teal
COLOR_VBM = "#7B4FB3"
COLOR_CBM = "#2BAFA3"
COLOR_TOTAL = "#333333"

# Nature-style semantic palette
NATURE_BLUE = "#3B7CB8"
NATURE_RED = "#C44E52"
NATURE_GREEN = "#55A868"
NATURE_GRAY = "#888888"
NATURE_GRID = "#ECECEC"

DOPANT_COLORS = {
    "pristine": NATURE_GRAY,
    "B": NATURE_BLUE,
    "N": NATURE_RED,
    "P": NATURE_GREEN,
}

DOPANT_MARKERS = {"B": "o", "N": "s", "P": "^", "pristine": "D"}


def apply_nature_style() -> None:
    """Nature/Science-like sans-serif, light grids, print-ready PRB width."""
    apply_prb_style()
    mpl.rcParams.update(
        {
            "axes.edgecolor": "#222222",
            "axes.labelcolor": "#222222",
            "xtick.color": "#222222",
            "ytick.color": "#222222",
            "axes.linewidth": 0.75,
            "lines.linewidth": 1.15,
            "lines.markersize": 5.0,
        }
    )


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


def style_axes(ax: Axes, grid: bool = False, *, grid_axis: str = "y") -> None:
    """Clean axes — L/B spines; optional light grid (Nature-style)."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.55)
    ax.spines["bottom"].set_linewidth(0.55)
    if grid:
        ax.grid(True, axis=grid_axis, color=NATURE_GRID, linewidth=0.45, zorder=0)
    ax.set_axisbelow(True)


def panel_label(
    ax: Axes,
    label: str,
    *,
    fontsize: float | None = None,
    nature: bool = False,
) -> None:
    """Panel tag: bold (a) Electron default; bold a Nature default."""
    fs = fontsize if fontsize is not None else mpl.rcParams["font.size"] + (1.5 if nature else 0.5)
    text = label if nature else f"({label})"
    ax.text(
        -0.14 if nature else 0.03,
        1.08 if nature else 0.97,
        text,
        transform=ax.transAxes,
        fontsize=fs,
        fontweight="bold",
        va="top",
        ha="left",
        zorder=10,
        clip_on=False,
        bbox=None
        if nature
        else dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none", alpha=0.75),
    )
