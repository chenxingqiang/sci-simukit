"""
Publication figure style — OriginLab-inspired (PRB / APS layout).

Thick boxed axes, inward ticks, Times serif, saturated palette, no clutter grid.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence

import matplotlib.pyplot as plt
import numpy as np

NATURE_SINGLE_COL = 89.0 / 25.4
NATURE_ONE_HALF_COL = 120.0 / 25.4
NATURE_DOUBLE_COL = 183.0 / 25.4
NATURE_MAX_HEIGHT = 170.0 / 25.4

# Origin-like: Times serif, inward ticks, 1.25 pt frame
ORIGIN_RCPARAMS = {
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "Nimbus Roman", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "font.size": 9,
    "axes.labelsize": 9,
    "axes.titlesize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "figure.dpi": 300,
    "savefig.dpi": 600,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
    "axes.linewidth": 1.25,
    "xtick.major.width": 1.0,
    "ytick.major.width": 1.0,
    "xtick.minor.width": 0.75,
    "ytick.minor.width": 0.75,
    "xtick.major.size": 5.0,
    "ytick.major.size": 5.0,
    "xtick.minor.size": 2.5,
    "ytick.minor.size": 2.5,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "lines.linewidth": 1.6,
    "lines.markersize": 7,
    "axes.grid": False,
    "axes.spines.top": True,
    "axes.spines.right": True,
    "legend.frameon": True,
    "legend.framealpha": 1.0,
    "legend.edgecolor": "#333333",
    "legend.fancybox": False,
    "legend.borderpad": 0.35,
    "legend.handlelength": 1.6,
    "legend.handletextpad": 0.5,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "axes.unicode_minus": False,
}

COLORS = {
    "pristine": "#666666",
    "B": "#0055AA",
    "N": "#CC0033",
    "P": "#FF8800",
    "B+N": "#0055AA",
    "Li": "#009988",
    "Na": "#FF8800",
    "K": "#333333",
    "accent": "#CC0033",
    "baseline": "#333333",
    "muted": "#AAAAAA",
    "reference": "#333333",
    "additive_zone": "#E8E8E8",
}

MARKERS = {
    "pristine": "o",
    "B": "s",
    "N": "o",
    "P": "D",
    "B+N": "D",
    "Li": "v",
    "Na": "<",
    "K": ">",
}

LINE_STYLES = {
    "B": "-",
    "N": "-",
    "P": "-",
    "pristine": "-",
}


def apply_nature_style() -> None:
    plt.rcParams.update(ORIGIN_RCPARAMS)


def get_color(dopant: str) -> str:
    return COLORS.get(dopant, "#666666")


def get_marker(dopant: str) -> str:
    return MARKERS.get(dopant, "o")


def style_axes(
    ax,
    panel_label: Optional[str] = None,
    y_grid: bool = False,
) -> None:
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.25)
        spine.set_color("#000000")

    ax.tick_params(top=True, right=True, which="both", direction="in", length=5, width=1.0)
    ax.minorticks_on()
    ax.tick_params(which="minor", length=2.5, width=0.75)

    if y_grid:
        ax.yaxis.grid(True, linestyle=":", linewidth=0.5, color="#CCCCCC", alpha=0.8, zorder=0)
        ax.set_axisbelow(True)

    if panel_label:
        tag = panel_label if panel_label.startswith("(") else f"({panel_label})"
        ax.text(
            -0.14,
            1.08,
            tag,
            transform=ax.transAxes,
            fontweight="bold",
            fontsize=11,
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
    linestyle=(0, (5, 3)),
    linewidth: float = 1.0,
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
        fontsize=7,
        color=color,
        clip_on=False,
    )


def origin_legend(ax, ncol: int = 1, loc: str = "upper right", bbox=None) -> None:
    kw = dict(
        loc=loc,
        ncol=ncol,
        frameon=True,
        edgecolor="#333333",
        fancybox=False,
        framealpha=1.0,
        handlelength=1.8,
    )
    if bbox is not None:
        kw["bbox_to_anchor"] = bbox
    ax.legend(**kw)


def nature_legend(ax, ncol: int = 3, loc: str = "upper center") -> None:
    origin_legend(ax, ncol=ncol, loc=loc)


def annotate_bar_values(ax, xs, ys, fmt="{:.1f}", dy=0.02, fontsize=8, inside=True):
    ylo, yhi = ax.get_ylim()
    yspan = yhi - ylo
    for x, y in zip(xs, ys):
        if inside and abs(y) > 0.15 * yspan:
            color = "white"
            ytxt = y * 0.55
            va = "center"
        else:
            color = "#111111"
            va = "bottom" if y >= 0 else "top"
            pad = 0.02 * yspan
            ytxt = y + pad if y >= 0 else y - pad
        sign_fmt = fmt if "{" in fmt else "{:+.1f}"
        try:
            txt = sign_fmt.format(y)
        except (ValueError, IndexError):
            txt = f"{y:+.1f}"
        ax.text(x, ytxt, txt, ha="center", va=va, fontsize=fontsize, fontweight="bold", color=color)


def style_line(
    ax,
    x,
    y,
    dopant: str,
    label: str,
    *,
    linewidth: float = 1.6,
    markersize: float = 7.5,
    zorder: int = 4,
    highlight_n: Optional[int] = None,
    x_arr=None,
) -> None:
    color = get_color(dopant)
    ax.plot(
        x,
        y,
        color=color,
        marker=get_marker(dopant),
        linestyle=LINE_STYLES.get(dopant, "-"),
        linewidth=linewidth,
        markersize=markersize,
        markerfacecolor=color,
        markeredgecolor="#000000",
        markeredgewidth=0.8,
        label=label,
        zorder=zorder,
    )
    if highlight_n is not None and x_arr is not None:
        import numpy as np

        mask = np.asarray(x_arr) == highlight_n
        if np.any(mask):
            ax.plot(
                np.asarray(x_arr)[mask],
                np.asarray(y)[mask],
                marker=get_marker(dopant),
                markersize=markersize + 3,
                markerfacecolor=color,
                markeredgecolor="#000000",
                markeredgewidth=1.2,
                linestyle="none",
                zorder=zorder + 1,
            )


def shade_additive_band(
    ax, half_width: float = 1.0, label: str = r"additive ($\mathcal{S}=0$)", *, show_label: bool = True
) -> None:
    ax.axhspan(-half_width, half_width, color=COLORS["additive_zone"], zorder=0, lw=0)
    ax.axhline(0, color="#000000", linestyle=(0, (4, 4)), linewidth=0.9, zorder=1)
    if show_label:
        ax.text(
            0.03,
            half_width * 0.55,
            label,
            transform=ax.get_yaxis_transform(),
            ha="left",
            va="center",
            fontsize=7,
            color="#555555",
        )


def shade_synergy_physics(ax, ylo: float, yhi: float) -> None:
    """Color regions: S<0 cooperative stabilization, S>0 cooperative destabilization."""
    ax.axhspan(ylo, 0, color="#D4E6F1", alpha=0.55, zorder=0, lw=0)
    ax.axhspan(0, yhi, color="#F5B7B1", alpha=0.45, zorder=0, lw=0)
    ax.axhline(0, color="#000000", linestyle=(0, (4, 4)), linewidth=1.0, zorder=1)
    ax.text(
        0.02,
        0.02,
        r"$\mathcal{S}<0$: cooperative stabilization",
        transform=ax.transAxes,
        fontsize=7,
        color="#1A5276",
        va="bottom",
        ha="left",
        fontstyle="italic",
    )
    ax.text(
        0.02,
        0.98,
        r"$\mathcal{S}>0$: cooperative destabilization",
        transform=ax.transAxes,
        fontsize=7,
        color="#922B21",
        va="top",
        ha="left",
        fontstyle="italic",
    )
    ax.text(
        0.98,
        0.0,
        r"two-scan model ($\mathcal{S}=0$)",
        transform=ax.get_yaxis_transform(),
        fontsize=7,
        color="#333333",
        ha="right",
        va="bottom",
    )


def draw_synergy_schematic(ax) -> None:
    """Inset: independent-knob workflow vs coupled cross term."""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.text(5, 9.2, "Energy bookkeeping at fixed $(\\epsilon,\\delta)$", ha="center", fontsize=8, fontweight="bold")
    ax.add_patch(plt.Rectangle((0.3, 4.6), 4.2, 3.8, fill=False, edgecolor="#666666", lw=0.9))
    ax.text(2.4, 7.9, "Sequential design (wrong if coupled)", ha="center", fontsize=7, fontweight="bold")
    ax.text(2.4, 6.8, r"$E \approx E_0 + \Delta E(\epsilon,0) + \Delta E(0,\delta)$", ha="center", fontsize=7)
    ax.text(2.4, 5.9, "strain scan + doping scan", ha="center", fontsize=6.3, color="#555555")
    ax.text(2.4, 5.0, r"assumes cross term $\mathcal{S}=0$", ha="center", fontsize=6.5, color="#922B21", fontstyle="italic")
    ax.add_patch(plt.Rectangle((5.5, 4.6), 4.2, 3.8, fill=False, edgecolor="#000000", lw=1.1))
    ax.text(7.6, 7.9, "Coupled DFT (this work)", ha="center", fontsize=7, fontweight="bold")
    ax.text(7.6, 6.8, r"$E = E_0 + \Delta E(\epsilon,0) + \Delta E(0,\delta) + \mathcal{S}$", ha="center", fontsize=7)
    ax.text(7.6, 5.9, r"same supercell, same $(\epsilon,\delta)$", ha="center", fontsize=6.3, color="#555555")
    ax.text(7.6, 5.0, r"measured $\mathcal{S}\neq 0$", ha="center", fontsize=6.5, color="#1A5276", fontweight="bold")
    ax.annotate("", xy=(5.3, 6.5), xytext=(4.7, 6.5), arrowprops=dict(arrowstyle="->", lw=1.0, color="#333333"))
    ax.text(2.4, 3.5, r"$\mathcal{S}<0$: binds more than predicted", ha="center", fontsize=6.3, color="#1A5276")
    ax.text(7.6, 3.5, r"$\mathcal{S}>0$: binds less than predicted", ha="center", fontsize=6.3, color="#922B21")


def shade_strain_response_physics(ax) -> None:
    ax.axvspan(0, 5.8, color="#FDEBD0", alpha=0.25, zorder=0)
    ax.axvspan(-5.8, 0, color="#D5F5E3", alpha=0.22, zorder=0)
    ax.text(3.8, 0.97, "tension", transform=ax.get_xaxis_transform(), ha="center", fontsize=7, color="#784212")
    ax.text(-3.8, 0.97, "compression", transform=ax.get_xaxis_transform(), ha="center", fontsize=7, color="#145A32")
    ax.axvline(3.0, color="#555555", linestyle=(0, (3, 2)), linewidth=0.9, zorder=1)
    ax.text(
        3.05,
        0.04,
        r"Exp.~10: $\epsilon=+3\%$",
        transform=ax.get_xaxis_transform(),
        fontsize=6.5,
        color="#444444",
        ha="left",
        va="bottom",
    )


def shade_alpha_physics(ax, y_pos, alphas) -> None:
    ax.axvspan(min(alphas) * 1.15, 0, color="#D5F5E3", alpha=0.35, zorder=0)
    ax.axvspan(0, max(alphas) * 1.15, color="#FADBD8", alpha=0.35, zorder=0)
    ax.text(
        0.02,
        0.06,
        r"$\alpha<0$: stabilizes under tension",
        transform=ax.transAxes,
        fontsize=7,
        color="#145A32",
        fontstyle="italic",
    )
    ax.text(
        0.98,
        0.06,
        r"$\alpha>0$: destabilizes under tension",
        transform=ax.transAxes,
        fontsize=7,
        color="#922B21",
        ha="right",
        fontstyle="italic",
    )


def fit_curve_n(S_inf: float, A: float, n_grid) -> np.ndarray:
    return S_inf + A / n_grid


def save_figure(fig, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, format="pdf")
    fig.savefig(path.with_suffix(".png"))
    plt.close(fig)
    return path
