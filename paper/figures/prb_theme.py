"""Typography, palette and small drawing primitives for the PRB main figures."""

from __future__ import annotations

import matplotlib as mpl
import numpy as np
from matplotlib import patheffects as pe
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.ticker import AutoMinorLocator

WIDTH_IN = 7.0

INK = "#15181C"
MID = "#566070"
SOFT = "#9AA3AE"
HAIR = "#D5DAE0"
WASH = "#EEF1F4"
PAPER = "#FFFFFF"
ROSE_WASH = "#F9EDEC"

PRISTINE = "#6B7683"
DOPANT = {
    "B": {"color": "#2D69B0", "marker": "o", "ms": 5.0, "name": "B"},
    "N": {"color": "#D2502B", "marker": "s", "ms": 4.5, "name": "N"},
    "P": {"color": "#78479F", "marker": "^", "ms": 5.4, "name": "P"},
}
DOPANTS = ("B", "N", "P")

SIGN_CMAP = LinearSegmentedColormap.from_list(
    "sign_div", ["#8E4F16", "#C98A4B", "#F6F4F0", "#52A39B", "#13706A"], N=256
)


def apply_theme() -> None:
    mpl.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "font.family": "sans-serif",
            "font.sans-serif": ["Arimo", "Liberation Sans", "Helvetica", "Arial", "DejaVu Sans"],
            "mathtext.fontset": "stixsans",
            "font.size": 7.0,
            "axes.labelsize": 7.4,
            "axes.titlesize": 7.4,
            "xtick.labelsize": 6.6,
            "ytick.labelsize": 6.6,
            "legend.fontsize": 6.6,
            "axes.linewidth": 0.65,
            "axes.edgecolor": INK,
            "axes.labelcolor": INK,
            "text.color": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.major.size": 3.0,
            "ytick.major.size": 3.0,
            "xtick.minor.size": 1.6,
            "ytick.minor.size": 1.6,
            "xtick.major.width": 0.65,
            "ytick.major.width": 0.65,
            "xtick.minor.width": 0.45,
            "ytick.minor.width": 0.45,
            "xtick.top": True,
            "ytick.right": True,
            "xtick.major.pad": 2.2,
            "ytick.major.pad": 2.2,
            "axes.labelpad": 2.0,
            "axes.grid": False,
            "lines.solid_capstyle": "round",
            "lines.dash_capstyle": "round",
            "legend.frameon": False,
            "legend.borderaxespad": 0.2,
            "legend.handletextpad": 0.4,
            "legend.columnspacing": 1.1,
            "figure.facecolor": PAPER,
            "axes.facecolor": PAPER,
            "savefig.facecolor": PAPER,
        }
    )


def frame(ax: Axes, *, minor: bool = True, grid: str | None = None) -> None:
    for side in ax.spines.values():
        side.set_linewidth(0.65)
        side.set_color(INK)
    if minor:
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    if grid:
        ax.grid(True, axis=grid, color=WASH, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)


def bare(ax: Axes) -> None:
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ax.spines.values():
        side.set_visible(False)


def tag(ax: Axes, letter: str, *, dx: float = -2.0, dy: float = 4.0) -> None:
    ax.annotate(
        letter,
        xy=(0, 1),
        xycoords="axes fraction",
        xytext=(dx, dy),
        textcoords="offset points",
        ha="left",
        va="bottom",
        fontsize=10.0,
        fontweight="bold",
        color=INK,
        annotation_clip=False,
    )


def subtitle(ax: Axes, text: str, *, dx: float = 14.0, dy: float = 4.2) -> None:
    ax.annotate(
        text,
        xy=(0, 1),
        xycoords="axes fraction",
        xytext=(dx, dy),
        textcoords="offset points",
        ha="left",
        va="bottom",
        fontsize=6.9,
        color=MID,
        annotation_clip=False,
    )


def halo(width: float = 2.2):
    return [pe.withStroke(linewidth=width, foreground="white")]


def label(ax: Axes, x, y, text, *, color=INK, fs=6.6, dx=0.0, dy=0.0, ha="left", va="center",
          bold=False, transform=None, halo_on=True, **kw) -> None:
    ax.annotate(
        text,
        xy=(x, y),
        xycoords=transform if transform is not None else "data",
        xytext=(dx, dy),
        textcoords="offset points",
        ha=ha,
        va=va,
        fontsize=fs,
        color=color,
        fontweight="bold" if bold else "normal",
        path_effects=halo() if halo_on else None,
        annotation_clip=False,
        zorder=8,
        **kw,
    )


def trace(ax: Axes, x, y, dop: str, *, lw=1.35, ms=None, filled=True, zorder=4, alpha=1.0,
          line=True, label_text=None) -> None:
    st = DOPANT[dop]
    ms = st["ms"] if ms is None else ms
    c = st["color"]
    if line:
        ax.plot(x, y, "-", color=c, lw=lw, alpha=alpha, zorder=zorder - 1)
    ax.plot(
        x, y, linestyle="None", marker=st["marker"], ms=ms,
        mfc=c if filled else "white", mec="white" if filled else c,
        mew=0.7 if filled else 1.2, color=c, alpha=alpha, zorder=zorder, label=label_text,
    )


def floor_band(ax: Axes, half: float, *, axis: str = "y", text: str | None = None, text_x: float = 0.985) -> None:
    if axis == "y":
        ax.axhspan(-half, half, color=WASH, lw=0, zorder=0)
        if text:
            ax.text(text_x, half, text, transform=ax.get_yaxis_transform(), ha="right", va="bottom",
                    fontsize=5.8, color=SOFT, zorder=1)
    else:
        ax.axvspan(-half, half, color=WASH, lw=0, zorder=0)


def zero_line(ax: Axes, *, axis: str = "y") -> None:
    (ax.axhline if axis == "y" else ax.axvline)(0.0, color=HAIR, lw=0.7, zorder=1)


def dopant_key(ax: Axes, *, loc="upper left", anchor=None, ncol=3, extra=()) -> None:
    handles = [
        Line2D([0], [0], color=DOPANT[d]["color"], marker=DOPANT[d]["marker"], ms=DOPANT[d]["ms"],
               mfc=DOPANT[d]["color"], mec="white", mew=0.6, lw=1.3, label=d)
        for d in DOPANTS
    ]
    handles += list(extra)
    kw = dict(handles=handles, loc=loc, ncol=ncol, handlelength=1.5, fontsize=6.6)
    if anchor is not None:
        kw["bbox_to_anchor"] = anchor
    ax.legend(**kw)


def bubble_area(value: float, vmax: float, *, full: float = 420.0) -> float:
    """Marker area (pt^2) strictly proportional to value; the largest value gets `full`."""
    return full * abs(float(value)) / float(vmax)
