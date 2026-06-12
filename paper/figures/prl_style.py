"""
PRL (Physical Review Letters) figure style for sci-simukit.

Single-column width: 3.375 in (RevTeX \\columnwidth).
Colorblind-safe palette per AGENTS.md (#0173B2 / #DE8F05 family).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt

PRL_SINGLE_COL = 3.375  # inches
PRL_ONE_HALF_COL = 5.0
PRL_DOUBLE_COL = 7.0

PRL_RCPARAMS = {
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif", "Computer Modern Roman", "serif"],
    "mathtext.fontset": "stix",
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
    "xtick.minor.width": 0.35,
    "ytick.minor.width": 0.35,
    "xtick.major.size": 3.0,
    "ytick.major.size": 3.0,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "lines.linewidth": 1.0,
    "lines.markersize": 5,
    "axes.grid": False,
    "axes.spines.top": True,
    "axes.spines.right": True,
    "legend.frameon": False,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
}

# Wong / AGENTS colorblind-safe (avoid red–green alone)
COLORS = {
    "pristine": "#949494",
    "B": "#0173B2",
    "N": "#DE8F05",
    "P": "#CC78BC",
    "B+N": "#029E73",
    "Li": "#56B4E9",
    "Na": "#ECE133",
    "K": "#000000",
}

MARKERS = {
    "pristine": "o",
    "B": "s",
    "N": "^",
    "P": "D",
    "B+N": "p",
    "Li": "v",
    "Na": "<",
    "K": ">",
}


def apply_prl_style() -> None:
    plt.rcParams.update(PRL_RCPARAMS)


def get_color(dopant: str) -> str:
    return COLORS.get(dopant, "#7f7f7f")


def get_marker(dopant: str) -> str:
    return MARKERS.get(dopant, "o")


def finalize_axes(ax, panel_label: Optional[str] = None) -> None:
    ax.minorticks_on()
    ax.tick_params(which="minor", length=1.5, width=0.35)
    if panel_label:
        ax.text(
            -0.14,
            1.04,
            panel_label,
            transform=ax.transAxes,
            fontweight="bold",
            fontsize=9,
            va="top",
            ha="left",
        )


def save_figure(fig, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, format="pdf")
    fig.savefig(path.with_suffix(".png"))
    plt.close(fig)
    return path
