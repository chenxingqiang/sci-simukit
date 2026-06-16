"""
Nature-family figure style (Nature / Nat. Commun. layout).

Reference: full axis box, bold (a)/(b) panel labels, top-centered legend,
muted palette with one accent, dashed reference lines, faint y-grid.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt

NATURE_SINGLE_COL = 89.0 / 25.4
NATURE_ONE_HALF_COL = 120.0 / 25.4
NATURE_DOUBLE_COL = 183.0 / 25.4
NATURE_MAX_HEIGHT = 170.0 / 25.4

# Muted Nature-like palette (accent purple + grays + one warm accent)
NATURE_RCPARAMS = {
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "mathtext.fontset": "dejavusans",
    "font.size": 7,
    "axes.labelsize": 7,
    "axes.titlesize": 7,
    "xtick.labelsize": 6,
    "ytick.labelsize": 6,
    "legend.fontsize": 6,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.05,
    "axes.linewidth": 0.75,
    "xtick.major.width": 0.75,
    "ytick.major.width": 0.75,
    "xtick.minor.width": 0.5,
    "ytick.minor.width": 0.5,
    "xtick.major.size": 3.5,
    "ytick.major.size": 3.5,
    "xtick.minor.size": 2.0,
    "ytick.minor.size": 2.0,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "xtick.top": True,
    "ytick.right": True,
    "lines.linewidth": 1.0,
    "lines.markersize": 5,
    "axes.grid": False,
    "axes.spines.top": True,
    "axes.spines.right": True,
    "legend.frameon": False,
    "legend.borderpad": 0.25,
    "legend.handlelength": 1.2,
    "legend.handletextpad": 0.4,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
}

COLORS = {
    "pristine": "#7A7A7A",
    "B": "#4D4D4D",
    "N": "#5B2C83",
    "P": "#9A9A9A",
    "B+N": "#0072B2",
    "Li": "#56B4E9",
    "Na": "#E69F00",
    "K": "#000000",
    "accent": "#5B2C83",
    "baseline": "#4D4D4D",
    "muted": "#B0B0B0",
    "reference": "#333333",
}

MARKERS = {
    "pristine": "o",
    "B": "s",
    "N": "s",
    "P": "s",
    "B+N": "D",
    "Li": "v",
    "Na": "<",
    "K": ">",
}


def apply_nature_style() -> None:
    plt.rcParams.update(NATURE_RCPARAMS)


def get_color(dopant: str) -> str:
    return COLORS.get(dopant, "#666666")


def get_marker(dopant: str) -> str:
    return MARKERS.get(dopant, "o")


def style_axes(
    ax,
    panel_label: Optional[str] = None,
    y_grid: bool = True,
) -> None:
    """Full box, optional faint horizontal grid, bold panel tag."""
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.75)
        spine.set_color("#333333")

    ax.tick_params(top=True, right=True, which="both")
    ax.minorticks_on()
    ax.tick_params(which="minor", length=2.0, width=0.5)

    if y_grid:
        ax.yaxis.grid(True, linestyle="-", linewidth=0.4, color="#D8D8D8", alpha=0.9, zorder=0)
        ax.set_axisbelow(True)

    if panel_label:
        tag = panel_label if panel_label.startswith("(") else f"({panel_label})"
        ax.text(
            -0.11,
            1.06,
            tag,
            transform=ax.transAxes,
            fontweight="bold",
            fontsize=9,
            va="top",
            ha="left",
            color="#000000",
        )


def finalize_axes(ax, panel_label: Optional[str] = None) -> None:
    style_axes(ax, panel_label=panel_label)


def add_reference_line(
    ax,
    y: float,
    label: str,
    *,
    color: str = "#333333",
    linestyle: str = "--",
    linewidth: float = 0.8,
    label_x: float = 0.98,
) -> None:
    ax.axhline(y, color=color, linestyle=linestyle, linewidth=linewidth, zorder=1)
    ax.text(
        label_x,
        y,
        label,
        transform=ax.get_yaxis_transform(),
        ha="right",
        va="bottom",
        fontsize=5.5,
        color=color,
        clip_on=False,
    )


def nature_legend(ax, ncol: int = 3, loc: str = "upper center") -> None:
    ax.legend(
        loc=loc,
        bbox_to_anchor=(0.5, 1.02) if loc == "upper center" else None,
        ncol=ncol,
        frameon=False,
        handlelength=1.0,
        columnspacing=0.8,
    )


def save_figure(fig, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, format="pdf")
    fig.savefig(path.with_suffix(".png"))
    plt.close(fig)
    return path
