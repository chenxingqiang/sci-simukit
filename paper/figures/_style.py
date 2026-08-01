"""PRL + Electron + Nature-style panel aesthetics."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import matplotlib as mpl
import numpy as np
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
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

DOPANT_FILLS = {
    "pristine": "#F0F0F0",
    "B": "#E8F1FA",
    "N": "#FBEAEA",
    "P": "#EDE8F5",
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

# Colorblind-friendly diverging map (Nature Methods style)
SYNERGY_CMAP = LinearSegmentedColormap.from_list(
    "synergy_div", ["#2166AC", "#F7F7F7", "#B2182B"], N=256
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
            "lines.linewidth": 1.3,
            "lines.markersize": 5.5,
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


def panel_subtitle(ax: Axes, text: str, *, ha: str = "left") -> None:
    """Light panel descriptor — avoids heavy annotation boxes."""
    ax.text(
        0.02 if ha == "left" else 0.98,
        0.98,
        text,
        transform=ax.transAxes,
        fontsize=7.2,
        fontweight="medium",
        ha=ha,
        va="top",
        color="#505050",
        style="italic",
        zorder=10,
    )


def style_colorbar(cbar, *, label: str = "") -> None:
    cbar.outline.set_linewidth(0.55)
    cbar.outline.set_edgecolor("#BBBBBB")
    if label:
        cbar.set_label(label, fontsize=8, labelpad=4)
    cbar.ax.tick_params(labelsize=6.5, width=0.55, length=2.5)


def add_reference_lines(ax: Axes, *, hzero: bool = True, vzero: bool = True) -> None:
    if hzero:
        ax.axhline(0, color="#D5D5D5", lw=0.65, zorder=0)
    if vzero:
        ax.axvline(0, color="#D5D5D5", lw=0.65, zorder=0)


def strain_guide(ax: Axes, x: float = 3.0) -> None:
    ax.axvline(x, color=DOPANT_COLORS["P"], lw=0.85, ls=(0, (4, 3)), alpha=0.5, zorder=0)


def plot_trajectory(
    ax: Axes,
    x,
    y,
    color: str,
    *,
    label: str | None = None,
    fill: bool = True,
    fill_to: float | None = None,
    fill_mode: str = "baseline",
    lw: float = 1.5,
    ms: float = 5.8,
    alpha_line: float = 0.72,
    zorder: int = 3,
) -> None:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if fill and len(x) >= 2:
        if fill_mode == "band":
            pad = max(0.06 * (np.nanmax(y) - np.nanmin(y)), 1e-6)
            ax.fill_between(x, y - pad, y + pad, color=color, alpha=0.14, linewidth=0, zorder=1)
        else:
            base = float(fill_to) if fill_to is not None else float(np.nanmin(y))
            ax.fill_between(x, y, base, color=color, alpha=0.11, linewidth=0, zorder=1)
    ax.plot(x, y, "-", color=color, lw=lw, alpha=alpha_line, zorder=2)
    ax.plot(
        x,
        y,
        "o",
        color=color,
        markersize=ms,
        markerfacecolor="white",
        markeredgewidth=1.2,
        lw=0,
        label=label,
        zorder=zorder,
    )


def plot_error_band(
    ax: Axes,
    x,
    y,
    yerr,
    color: str,
    *,
    label: str | None = None,
) -> None:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    yerr = np.asarray(yerr, dtype=float)
    ax.fill_between(x, y - yerr, y + yerr, color=color, alpha=0.20, linewidth=0, zorder=1)
    ax.plot(
        x,
        y,
        "-o",
        color=color,
        markersize=5.5,
        markerfacecolor="white",
        markeredgewidth=1.15,
        lw=1.45,
        label=label,
        zorder=3,
    )


@lru_cache(maxsize=8)
def _orbital_rgba(dop: str, diam_px: int = 180) -> np.ndarray:
    """Load dopant orbital PNG, crop whitespace, soft circular alpha + dopant tint."""
    path = DOPANT_ORBITAL_PNG.get(dop)
    if path is None or not path.is_file():
        raise FileNotFoundError(f"orbital PNG missing for {dop}: {path}")
    im = Image.open(path).convert("RGBA")
    arr = np.asarray(im)
    rgb = arr[..., :3].astype(np.float32)
    mask = np.any(rgb < 245.0, axis=-1)
    ys, xs = np.where(mask)
    if len(xs) == 0:
        crop = im
    else:
        pad = 6
        y0, y1 = max(0, ys.min() - pad), min(arr.shape[0], ys.max() + pad + 1)
        x0, x1 = max(0, xs.min() - pad), min(arr.shape[1], xs.max() + pad + 1)
        crop = im.crop((x0, y0, x1, y1))
    side = max(crop.size)
    canvas = Image.new("RGBA", (side, side), (255, 255, 255, 0))
    ox, oy = (side - crop.size[0]) // 2, (side - crop.size[1]) // 2
    canvas.paste(crop, (ox, oy), crop)
    canvas = canvas.resize((diam_px, diam_px), Image.Resampling.LANCZOS)
    out = np.asarray(canvas).astype(np.float32)
    # Soft circular mask
    yy, xx = np.ogrid[:diam_px, :diam_px]
    cx = cy = (diam_px - 1) / 2.0
    r = diam_px / 2.0 - 1.0
    rr = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    alpha = np.clip((r - rr) / 2.0, 0.0, 1.0)
    # Mild dopant-color wash so B/N/P stay distinct at thumbnail size
    hex_c = DOPANT_COLORS[dop].lstrip("#")
    tint = np.array([int(hex_c[i:i+2], 16) for i in (0, 2, 4)], dtype=np.float32)
    ink = out[..., :3].mean(axis=-1, keepdims=True)
    mix = np.clip((255.0 - ink) / 180.0, 0.0, 1.0)  # stronger on dark atoms/clouds
    out[..., :3] = (1.0 - 0.35 * mix) * out[..., :3] + 0.35 * mix * tint
    out[..., 3] = out[..., 3] * alpha
    return out.astype(np.uint8)


def scatter_dopant(
    ax: Axes,
    x: float,
    y: float,
    dop: str,
    *,
    size: float = 120,
    annotate: bool = True,
    offset: tuple[float, float] = (7, 4),
    use_orbital: bool = True,
) -> None:
    """Place dopant glyph. Default: electron-cloud thumbnail (not triangle/square)."""
    if use_orbital and dop in DOPANT_ORBITAL_PNG:
        # Matplotlib scatter ``s`` is area in points^2; map to OffsetImage zoom.
        zoom = 0.14 + 0.00020 * float(size)
        rgba = _orbital_rgba(dop)
        imagebox = OffsetImage(rgba, zoom=zoom)
        # Colored under-dot (identity) + frameless orbital cloud (no square/triangle markers)
        ax.scatter(
            [x], [y], s=max(size * 0.55, 70),
            color=DOPANT_COLORS[dop], alpha=0.22, linewidths=0, zorder=4,
        )
        ab = AnnotationBbox(
            imagebox,
            (x, y),
            xycoords=ax.transData,
            frameon=False,
            pad=0.0,
            box_alignment=(0.5, 0.5),
            zorder=5,
            annotation_clip=True,
        )
        ax.add_artist(ab)
        ax.autoscale(enable=False)
    else:
        ax.scatter(
            x,
            y,
            s=size,
            color=DOPANT_COLORS[dop],
            marker="o",
            edgecolors=INK,
            linewidths=0.85,
            zorder=4,
        )
    if annotate:
        ax.annotate(
            dop,
            (x, y),
            textcoords="offset points",
            xytext=offset,
            fontsize=8.5,
            fontweight="bold",
            color=DOPANT_COLORS[dop],
            zorder=6,
        )


def structure_gallery_labels(ax: Axes, labels: tuple[str, ...]) -> None:
    n = len(labels)
    for i, lab in enumerate(labels):
        if i > 0:
            ax.axvline(i / n, color="#DDDDDD", lw=0.9, ymin=0.03, ymax=0.97, clip_on=False)
        color = DOPANT_COLORS.get("pristine" if lab == "Pristine" else lab, INK)
        ax.text(
            (i + 0.5) / n,
            -0.04,
            lab,
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=8.5,
            fontweight="bold",
            color=color,
        )


def draw_research_schematic(ax: Axes) -> None:
    """Publication-quality schematic: paths → channels → S."""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 2.35)
    ax.axis("off")

    def box(x, y, w, h, text, edge, face):
        patch = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.09",
            linewidth=1.05,
            edgecolor=edge,
            facecolor=face,
            zorder=2,
        )
        ax.add_patch(patch)
        ax.text(
            x + w / 2,
            y + h / 2,
            text,
            ha="center",
            va="center",
            fontsize=7.2,
            color=edge,
            fontweight="bold",
            linespacing=1.28,
            zorder=3,
        )

    def arrow(p0, p1, rad: float = 0.0):
        ax.add_patch(
            FancyArrowPatch(
                p0,
                p1,
                arrowstyle="-|>",
                mutation_scale=9.5,
                lw=0.95,
                color="#555555",
                shrinkA=3,
                shrinkB=3,
                connectionstyle=f"arc3,rad={rad}",
                zorder=1,
            )
        )

    box(0.22, 1.02, 1.58, 0.82, "strain paths\n$E_g,\\,q,\\,\\bar{d}$", NATURE_GRAY, "#F6F6F6")
    box(0.22, 0.10, 1.58, 0.82, "size paths\n$\\mathcal{S}(n)$", DOPANT_COLORS["P"], DOPANT_FILLS["P"])
    box(2.48, 0.52, 1.92, 1.10, "joint load\n$(\\epsilon,\\delta)$", NATURE_GREEN, "#ECF5EE")
    box(5.18, 1.14, 1.50, 0.68, "$\\pi$ electronic", DOPANT_COLORS["N"], DOPANT_FILLS["N"])
    box(5.18, 0.14, 1.50, 0.68, "P geometric", DOPANT_COLORS["P"], DOPANT_FILLS["P"])
    box(7.48, 0.52, 2.05, 1.10, "$\\mathcal{S}$\nnon-additive", INK, "#F4F4F4")

    arrow((1.8, 1.42), (2.48, 1.28), 0.05)
    arrow((1.8, 0.50), (2.48, 0.88), -0.05)
    arrow((4.4, 1.28), (5.18, 1.48))
    arrow((4.4, 0.92), (5.18, 0.48))
    arrow((6.68, 1.48), (7.48, 1.22), 0.04)
    arrow((6.68, 0.48), (7.48, 0.92), -0.04)

    ax.text(
        5.0,
        2.22,
        "paths  $\\rightarrow$  channels  $\\rightarrow$  $\\mathcal{S}$",
        ha="center",
        va="top",
        fontsize=7.5,
        color=NATURE_GRAY,
    )


def draw_additive_screening_schematic(ax: Axes) -> None:
    """Graphical summary: when separate DFT scans fail additive screening."""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 1.05)
    ax.axis("off")

    def box(x, y, w, h, text, edge, face):
        patch = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            linewidth=0.95,
            edgecolor=edge,
            facecolor=face,
            zorder=2,
        )
        ax.add_patch(patch)
        ax.text(
            x + w / 2,
            y + h / 2,
            text,
            ha="center",
            va="center",
            fontsize=6.8,
            color=edge,
            fontweight="bold",
            linespacing=1.22,
            zorder=3,
        )

    def arrow(p0, p1):
        ax.add_patch(
            FancyArrowPatch(
                p0,
                p1,
                arrowstyle="-|>",
                mutation_scale=9.0,
                lw=0.9,
                color="#555555",
                shrinkA=3,
                shrinkB=3,
                zorder=1,
            )
        )

    box(0.15, 0.22, 1.55, 0.62, "separate\nstrain / dopant DFT", NATURE_GRAY, "#F6F6F6")
    box(2.05, 0.22, 1.35, 0.62, "additive\nprediction", NATURE_GRAY, "#EEEEEE")
    box(3.75, 0.22, 1.55, 0.62, "coupled\nfour-corner DFT", NATURE_BLUE, "#E8F1FA")
    box(5.65, 0.22, 1.15, 0.62, r"$\mathcal{S}$ gap", INK, "#F4F4F4")
    box(7.15, 0.22, 2.05, 0.62, "screening\ndecision changes", DOPANT_COLORS["P"], DOPANT_FILLS["P"])
    arrow((1.7, 0.53), (2.05, 0.53))
    arrow((3.4, 0.53), (3.75, 0.53))
    arrow((5.3, 0.53), (5.65, 0.53))
    arrow((6.8, 0.53), (7.15, 0.53))
    ax.text(
        5.0,
        0.98,
        "additive screening fails when $|\\mathcal{S}|$ exceeds protocol band",
        ha="center",
        va="top",
        fontsize=7.2,
        color=NATURE_GRAY,
    )

