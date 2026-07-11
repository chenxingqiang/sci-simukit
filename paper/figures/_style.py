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

# Nature/Science reference palette (high-contrast, print-safe)
NATURE_BLUE = "#2E6DB4"   # primary / Optimal / Reference
NATURE_RED = "#C0392B"    # contrast / Random / Alternate
NATURE_GREEN = "#2E8B57"  # tertiary / Baseline accent
NATURE_GRAY = "#7A7A7A"
NATURE_LIGHT = "#F2F2F2"
NATURE_GRID = "#E8E8E8"
INK = "#1A1A1A"

DOPANT_COLORS = {
    "pristine": NATURE_GRAY,
    "B": NATURE_BLUE,
    "N": NATURE_RED,
    "P": "#6B4C9A",  # purple — distinct from green baseline; size-mismatch channel
}

DOPANT_MARKERS = {"B": "o", "N": "s", "P": "^", "pristine": "D"}


def apply_nature_style() -> None:
    """Nature/Science reference: Helvetica, outward ticks, no grid, generous type."""
    apply_prb_style()
    mpl.rcParams.update(
        {
            "axes.edgecolor": INK,
            "axes.labelcolor": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "text.color": INK,
            "axes.linewidth": 0.9,
            "lines.linewidth": 1.4,
            "lines.markersize": 6.0,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "xtick.major.size": 3.5,
            "ytick.major.size": 3.5,
            "xtick.major.width": 0.9,
            "ytick.major.width": 0.9,
            "xtick.minor.size": 2.0,
            "ytick.minor.size": 2.0,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": False,
            "legend.frameon": False,
            "legend.borderpad": 0.2,
            "legend.handlelength": 1.4,
            "legend.handletextpad": 0.4,
            "legend.labelspacing": 0.25,
            "axes.facecolor": "white",
            "figure.facecolor": "white",
            "figure.edgecolor": "white",
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
            "xtick.direction": "out",
            "ytick.direction": "out",
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
            "font.size": 8.5,
            "mathtext.fontset": "dejavusans",
            "axes.labelsize": 9,
            "axes.titlesize": 8.5,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "legend.fontsize": 7,
            "axes.linewidth": 0.9,
            "lines.linewidth": 1.3,
            "lines.markersize": 5.5,
            "xtick.major.width": 0.9,
            "ytick.major.width": 0.9,
            "xtick.major.size": 3.5,
            "ytick.major.size": 3.5,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def apply_si_style() -> None:
    """Supplemental Material figures — match PRB readability."""
    apply_prb_style()


def style_axes(ax: Axes, grid: bool = False, *, grid_axis: str = "y") -> None:
    """Clean Nature axes: L/B spines only; outward ticks; grid off by default."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.9)
    ax.spines["bottom"].set_linewidth(0.9)
    ax.spines["left"].set_color(INK)
    ax.spines["bottom"].set_color(INK)
    ax.tick_params(direction="out", length=3.5, width=0.9, colors=INK)
    if grid:
        ax.grid(True, axis=grid_axis, color=NATURE_GRID, linewidth=0.5, zorder=0)
    else:
        ax.grid(False)
    ax.set_axisbelow(True)


def panel_label(
    ax: Axes,
    label: str,
    *,
    fontsize: float | None = None,
    nature: bool = False,
) -> None:
    """Panel tag: bold lowercase a (Nature) or (a) (Electron)."""
    fs = fontsize if fontsize is not None else (12.0 if nature else mpl.rcParams["font.size"] + 0.5)
    text = label if nature else f"({label})"
    ax.text(
        -0.12 if nature else 0.03,
        1.06 if nature else 0.97,
        text,
        transform=ax.transAxes,
        fontsize=fs,
        fontweight="bold",
        fontfamily="sans-serif",
        va="bottom" if nature else "top",
        ha="left",
        color=INK,
        zorder=10,
        clip_on=False,
    )


def annotate_box(ax: Axes, text: str, xy=(0.97, 0.05), *, fontsize: float = 6.5, ha: str = "right", va: str = "bottom") -> None:
    """White metadata box like Nature panel insets."""
    ax.text(
        xy[0],
        xy[1],
        text,
        transform=ax.transAxes,
        fontsize=fontsize,
        ha=ha,
        va=va,
        color=INK,
        bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#CCCCCC", linewidth=0.5, alpha=0.92),
        zorder=8,
    )
