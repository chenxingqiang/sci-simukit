"""PRL + Electron + Nature-style panel aesthetics."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import matplotlib as mpl
import numpy as np
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch
from PIL import Image

# Single-column PRL width
PRL_WIDTH_IN = 3.375
PRL_HEIGHT_IN = 1.95
PRB_WIDTH_IN = 7.0
PRB_HEIGHT_IN = 2.35

# Electron Fig. 2 palette — valence purple, conduction teal
COLOR_VBM = "#7B4FB3"
COLOR_CBM = "#2BAFA3"
COLOR_TOTAL = "#333333"

# Nature/Science reference palette (high-contrast, print-safe, slightly boosted saturation)
NATURE_BLUE = "#2563EB"   # primary / B channel
NATURE_RED = "#DC2626"    # N donor channel
NATURE_GREEN = "#059669"  # tertiary accent
NATURE_GRAY = "#64748B"
NATURE_LIGHT = "#F4F6F8"
NATURE_GRID = "#E2E8F0"
INK = "#0F172A"

DOPANT_COLORS = {
    "pristine": NATURE_GRAY,
    "B": NATURE_BLUE,
    "N": NATURE_RED,
    "P": "#7C3AED",  # vivid purple — P size-mismatch channel
}

DOPANT_MARKERS = {"B": "o", "N": "s", "P": "^", "pristine": "D"}

DOPANT_FILLS = {
    "pristine": "#F1F5F9",
    "B": "#DBEAFE",
    "N": "#FEE2E2",
    "P": "#EDE9FE",
}

# Distinct orbital / electron-cloud glyphs (no geometric markers).
# B acceptor → VBM; N donor → CBM; P size-mismatch → CBM (distinct localization).
_FIG_DIR = Path(__file__).resolve().parent
_ORB_CACHE = _FIG_DIR / "final_figures" / "_vbm_cbm_cache_surf_doped"
DOPANT_ORBITAL_PNG = {
    "B": _ORB_CACHE / "B_n4_vbm.png",
    "N": _ORB_CACHE / "N_n4_cbm.png",
    "P": _ORB_CACHE / "P_n4_cbm.png",
}

_C60_PRISTINE = _FIG_DIR / "final_figures" / "C60_strain_+0.0_pristine_synergy.png"
_C60_P_DOPED = _FIG_DIR / "final_figures" / "C60_strain_+0.0_P_doped_synergy.png"

# Colorblind-friendly diverging map — stronger blue/red wings for heatmaps
SYNERGY_CMAP = LinearSegmentedColormap.from_list(
    "synergy_div", ["#1D4ED8", "#F8FAFC", "#DC2626"], N=256
)


def apply_nature_style() -> None:
    """Journal reference: Helvetica, inward ticks, boxed spines, no grid."""
    apply_prb_style()
    mpl.rcParams.update(
        {
            "axes.edgecolor": INK,
            "axes.labelcolor": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "text.color": INK,
            "axes.linewidth": 0.9,
            "lines.linewidth": 1.55,
            "lines.markersize": 6.0,
            "lines.solid_capstyle": "round",
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.major.size": 3.5,
            "ytick.major.size": 3.5,
            "xtick.major.width": 0.9,
            "ytick.major.width": 0.9,
            "xtick.minor.size": 2.0,
            "ytick.minor.size": 2.0,
            "xtick.top": True,
            "ytick.right": True,
            "axes.spines.top": True,
            "axes.spines.right": True,
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
            "lines.linewidth": 1.55,
            "lines.markersize": 6.0,
            "xtick.major.width": 0.9,
            "ytick.major.width": 0.9,
            "xtick.major.size": 3.5,
            "ytick.major.size": 3.5,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.top": True,
            "ytick.right": True,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def apply_si_style() -> None:
    """Supplemental Material figures — match PRB readability."""
    apply_prb_style()


def style_axes(ax: Axes, grid: bool = False, *, grid_axis: str = "y", box: bool = True) -> None:
    """Journal axes: boxed spines + inward ticks (ρ–T reference style); grid off by default."""
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(True if box or side in ("left", "bottom") else False)
        ax.spines[side].set_linewidth(0.9)
        ax.spines[side].set_color(INK)
    if not box:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    ax.tick_params(
        direction="in", length=3.5, width=0.9, colors=INK,
        top=box, right=box, which="major",
    )
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































