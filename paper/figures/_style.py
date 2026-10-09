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


def style_colorbar(cbar, *, label: str = "", label_axis: str = "y") -> None:
    cbar.outline.set_linewidth(0.55)
    cbar.outline.set_edgecolor("#BBBBBB")
    if label:
        if label_axis == "x":
            cbar.ax.set_xlabel(label, fontsize=7, labelpad=5)
        elif label_axis == "left":
            cbar.ax.set_ylabel(label, fontsize=7, labelpad=1, rotation=90, va="center")
            cbar.ax.yaxis.set_label_position("left")
        else:
            cbar.set_label(label, fontsize=7, labelpad=6, rotation=270, va="bottom")
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
    lw: float = 1.75,
    ms: float = 6.5,
    alpha_line: float = 0.9,
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
            ax.fill_between(x, y, base, color=color, alpha=0.16, linewidth=0, zorder=1)
    ax.plot(x, y, "-", color=color, lw=lw, alpha=alpha_line, zorder=2)
    ax.plot(
        x,
        y,
        "o",
        color=color,
        markersize=ms,
        markerfacecolor="white",
        markeredgewidth=1.35,
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
    mix = np.clip((255.0 - ink) / 160.0, 0.0, 1.0)
    out[..., :3] = (1.0 - 0.48 * mix) * out[..., :3] + 0.48 * mix * tint
    out[..., 3] = np.clip(out[..., 3] * alpha * 1.05, 0.0, 255.0)
    return out.astype(np.uint8)


def _trim_white(im: Image.Image, *, threshold: int = 248, pad: int = 8) -> Image.Image:
    arr = np.asarray(im.convert("RGBA"))
    mask = np.any(arr[..., :3] < threshold, axis=-1)
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return im
    y0, y1 = max(0, ys.min() - pad), min(arr.shape[0], ys.max() + pad + 1)
    x0, x1 = max(0, xs.min() - pad), min(arr.shape[1], xs.max() + pad + 1)
    return im.crop((x0, y0, x1, y1))


@lru_cache(maxsize=8)
def _c60_rgba(*, doped: bool = False, quad: int | None = None, max_px: int = 220) -> np.ndarray:
    """Load a rendered C60 cage (optionally one quadrant of the 2x2 synergy plate)."""
    path = _C60_P_DOPED if doped else _C60_PRISTINE
    im = Image.open(path).convert("RGBA")
    im = _trim_white(im)
    if quad is not None:
        w, h = im.size
        cw, ch = w // 2, h // 2
        boxes = ((0, 0, cw, ch), (cw, 0, w, ch), (0, ch, cw, h), (cw, ch, w, h))
        im = _trim_white(im.crop(boxes[quad]), pad=4)
    w, h = im.size
    scale = max_px / max(w, h)
    im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.LANCZOS)
    return np.asarray(im)


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
    """Place dopant glyph.

    Uses the electron-cloud thumbnail when the rendered cache is available and
    falls back to the standard per-dopant marker otherwise, so the figure stays
    reproducible from a clean checkout (the thumbnails are VMD products and are
    not tracked).
    """
    if use_orbital and dop in DOPANT_ORBITAL_PNG:
        cached = DOPANT_ORBITAL_PNG.get(dop)
        if cached is None or not cached.is_file():
            use_orbital = False
    if use_orbital and dop in DOPANT_ORBITAL_PNG:
        # Matplotlib scatter ``s`` is area in points^2; map to OffsetImage zoom.
        zoom = min(0.30, 0.129 * np.sqrt(max(float(size), 1.0) / 120.0))
        rgba = _orbital_rgba(dop)
        imagebox = OffsetImage(rgba, zoom=zoom)
        # Colored under-dot (identity) + frameless orbital cloud (no square/triangle markers)
        ax.scatter(
            [x], [y], s=max(size * 0.55, 40.0),
            color=DOPANT_COLORS[dop], alpha=0.32, linewidths=0, zorder=4,
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
            marker=DOPANT_MARKERS.get(dop, "o"),
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
    """ChemDraw-like protocol using rendered C60 cages."""
    ax.set_xlim(0.0, 12.0)
    ax.set_ylim(0.0, 3.05)
    ax.axis("off")

    def pill(cx, cy, w, h, text, face, edge, *, fs=6.0):
        ax.add_patch(
            FancyBboxPatch(
                (cx - w / 2, cy - h / 2),
                w,
                h,
                boxstyle="round,pad=0.018,rounding_size=0.10",
                linewidth=0.90,
                edgecolor=edge,
                facecolor=face,
                zorder=2,
                clip_on=False,
            )
        )
        ax.text(
            cx,
            cy,
            text,
            ha="center",
            va="center",
            fontsize=fs,
            color=INK,
            linespacing=1.15,
            zorder=3,
            clip_on=False,
        )

    def mol(cx, cy, rgba, label, *, zoom=0.20):
        ax.add_artist(
            AnnotationBbox(
                OffsetImage(rgba, zoom=zoom),
                (cx, cy + 0.08),
                xycoords=ax.transData,
                frameon=False,
                pad=0.0,
                box_alignment=(0.5, 0.5),
                zorder=3,
                annotation_clip=False,
            )
        )
        ax.text(
            cx,
            cy - 0.52,
            label,
            ha="center",
            va="top",
            fontsize=5.8,
            color=INK,
            zorder=4,
            clip_on=False,
        )

    def rxn_arrow(xy0, xy1, label="", *, dy=0.20, above=True):
        ax.annotate(
            "",
            xy=xy1,
            xytext=xy0,
            arrowprops=dict(
                arrowstyle="-|>",
                color=INK,
                lw=1.05,
                shrinkA=2.0,
                shrinkB=2.0,
                mutation_scale=10,
            ),
            zorder=1,
        )
        if label:
            mx, my = 0.5 * (xy0[0] + xy1[0]), 0.5 * (xy0[1] + xy1[1])
            ax.text(
                mx,
                my + (dy if above else -dy),
                label,
                ha="center",
                va="bottom" if above else "top",
                fontsize=5.4,
                color=NATURE_GRAY,
                style="italic",
                zorder=3,
                clip_on=False,
            )

    ax.text(
        0.15,
        2.96,
        r"$\mathcal{S}_\delta(\epsilon)=E_{\mathrm{cpl}}-E_{\mathrm{add}}$ at fixed $\delta$",
        ha="left",
        va="top",
        fontsize=6.0,
        color=NATURE_GRAY,
        style="italic",
        clip_on=False,
    )

    y_top, y_bot, y_mid = 1.95, 0.58, 1.26
    cage = _c60_rgba(doped=False, quad=3, max_px=160)
    dop_cage = _c60_rgba(doped=True, quad=0, max_px=160)
    tetramer = _c60_rgba(doped=False, quad=None, max_px=180)

    mol(0.95, y_top, cage, r"strain DFT", zoom=0.12)
    ax.text(1.90, y_top + 0.08, "+", ha="center", va="center", fontsize=11, color=INK, fontweight="bold")
    mol(2.85, y_top, dop_cage, r"dopant DFT", zoom=0.12)
    rxn_arrow((3.45, y_top), (4.15, y_top), "additive", dy=0.28)
    pill(4.90, y_top, 1.18, 0.52, r"$E_{\mathrm{add}}$", "#F8FAFC", NATURE_GRAY, fs=6.4)

    mol(1.90, y_bot, tetramer, r"4-corner, fixed $\delta$", zoom=0.09)
    rxn_arrow((2.70, y_bot), (4.15, y_bot), "coupled", dy=0.28, above=False)
    pill(4.90, y_bot, 1.18, 0.52, r"$E_{\mathrm{cpl}}$", "#DBEAFE", NATURE_BLUE, fs=6.4)

    rxn_arrow((5.52, y_top), (6.55, y_mid + 0.16))
    rxn_arrow((5.52, y_bot), (6.55, y_mid - 0.16))
    ax.add_patch(
        Circle((7.05, y_mid), 0.36, facecolor="#F8FAFC", edgecolor=INK, linewidth=1.05, zorder=2, clip_on=False)
    )
    ax.text(7.05, y_mid, r"$\mathcal{S}$", ha="center", va="center", fontsize=8.6, color=INK, zorder=3)
    ax.text(
        7.05,
        y_mid - 0.48,
        r"$E_{\mathrm{cpl}}-E_{\mathrm{add}}$",
        ha="center",
        va="top",
        fontsize=5.3,
        color=NATURE_GRAY,
        style="italic",
        zorder=3,
        clip_on=False,
    )

    rxn_arrow((7.46, y_mid), (8.35, y_mid), r"$|\mathcal{S}|$", dy=0.20)
    ax.text(
        9.55,
        y_mid,
        r"$\mathcal{S}_\delta(\epsilon)$" + "\n" + r"fixed species $\delta$",
        ha="center",
        va="center",
        fontsize=6.2,
        color=INK,
        clip_on=False,
        zorder=3,
    )


def draw_energy_coupling_schematic(ax: Axes) -> None:
    """Theory panel: additive vs coupled E(epsilon) under joint load (schematic, not DFT)."""
    eps = np.linspace(0.0, 3.0, 80)
    # additive: sum of separate linear strain responses
    e_add = 0.12 * eps + 0.08
    # coupled: bilinear cross term bends the joint-load path
    e_cpl = 0.12 * eps + 0.08 + 0.035 * eps**2
    ax.plot(eps, e_add, "--", color=NATURE_GRAY, lw=1.35, label="additive sum", zorder=2)
    ax.plot(eps, e_cpl, "-", color=NATURE_BLUE, lw=1.65, label="coupled load", zorder=3)
    ax.fill_between(eps, e_add, e_cpl, color=DOPANT_COLORS["P"], alpha=0.12, zorder=1)
    ax.axvline(3.0, color="#DDDDDD", lw=0.7, ls=":", zorder=0)
    ax.set_xlim(0.0, 3.2)
    ax.set_ylim(0.0, 0.82)
    ax.set_xlabel(r"$\epsilon$ (%)")
    ax.set_ylabel(r"$\Delta E$ (arb. units)")
    mid = 0.5 * (e_add + e_cpl)
    idx = int(len(eps) * 0.42)
    ax.text(
        eps[idx],
        mid[idx] + 0.03,
        r"$c\,\epsilon x$",
        ha="center",
        va="bottom",
        fontsize=6.2,
        color=DOPANT_COLORS["P"],
        zorder=4,
    )
    style_axes(ax)
    ax.legend(loc="upper left", fontsize=5.8, frameon=False, borderaxespad=0.35)

