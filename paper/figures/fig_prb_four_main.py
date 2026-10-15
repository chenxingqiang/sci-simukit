#!/usr/bin/env python3
"""PRB main figures 1–4 — publication-quality process panels."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from PIL import Image

FIG_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(FIG_DIR))

from _load_audit import (
    load_hirshfeld_strain_paths,
    load_json,
    load_local_structure_summary,
    load_mismatch_rows,
    load_periodic_relax_n1_P,
    load_reference_pbed3_alpha_S,
    n4_decomposition,
    parse_exp7_gaps,
    repo_root,
    synergy_rows,
    SIGMA_S_MEV,
)
from _pdos import gaussian_dos, parse_pdos
from _style import (
    DOPANT_COLORS,
    DOPANT_FILLS,
    INK,
    NATURE_BLUE,
    NATURE_GRAY,
    PRB_WIDTH_IN,
    SYNERGY_CMAP,
    add_reference_lines,
    apply_nature_style,
    draw_additive_screening_schematic,
    draw_energy_coupling_schematic,
    panel_label,
    panel_subtitle,
    plot_error_band,
    plot_trajectory,
    scatter_dopant,
    strain_guide,
    structure_gallery_labels,
    style_axes,
    style_colorbar,
)

OUT = FIG_DIR / "out"


def _marker_area(abs_s: float, ref: float, *, lo: float = 70.0, hi: float = 220.0) -> float:
    """Scatter area scales with |S| / max|S| on the panel (audit JSON, not a fit)."""
    if ref <= 0:
        return 130.0
    t = min(max(abs_s / ref, 0.0), 1.0)
    return lo + (hi - lo) * t


def _energy_landscape_inset(ax) -> None:
    """Schematic bilinear corner of E(epsilon, delta) — not from DFT data."""
    inset = ax.inset_axes([0.03, 0.06, 0.36, 0.44])
    eps = np.linspace(0.0, 1.0, 48)
    comp = np.linspace(0.0, 1.0, 48)
    E_grid, X_grid = np.meshgrid(eps, comp)
    z = 0.18 * E_grid + 0.14 * X_grid + 0.42 * E_grid * X_grid
    inset.contourf(E_grid, X_grid, z, levels=14, cmap="viridis", alpha=0.92)
    inset.contour(E_grid, X_grid, z, levels=7, colors="white", linewidths=0.45, alpha=0.55)
    for ex, xv in ((0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0)):
        inset.plot(ex, xv, "o", ms=4.0, mfc="white", mec=INK, mew=0.7, zorder=5)
    inset.set_xticks([0.0, 1.0])
    inset.set_xticklabels([r"$0$", r"$+3\%$"], fontsize=5.5)
    inset.set_yticks([0.0, 1.0])
    inset.set_yticklabels([r"ref.", r"dop."], fontsize=5.5)
    inset.set_xlabel(r"$\epsilon$", fontsize=6, labelpad=0)
    inset.set_ylabel(r"$\delta$", fontsize=6, labelpad=0)
    inset.tick_params(labelsize=5.5, pad=1)
    inset.text(
        0.5,
        1.12,
        r"$E(\epsilon,\delta)$: bilinear corner",
        transform=inset.transAxes,
        fontsize=5.8,
        ha="center",
        color=INK,
    )
    for spine in inset.spines.values():
        spine.set_linewidth(0.6)
        spine.set_color(INK)


def _save(fig: plt.Figure, stem: str) -> tuple[Path, Path]:
    OUT.mkdir(parents=True, exist_ok=True)
    pdf = OUT / f"{stem}.pdf"
    png = OUT / f"{stem}.png"
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.03, facecolor="white")
    fig.savefig(png, bbox_inches="tight", pad_inches=0.03, dpi=300, facecolor="white")
    plt.close(fig)
    return pdf, png


def _legend_in(ax, **kw):
    kw.setdefault("frameon", False)
    kw.setdefault("fontsize", 7)
    kw.setdefault("loc", "best")
    ax.legend(**kw)


def _axis_break(ax_top, ax_bot, size: float = 0.018) -> None:
    """Diagonal ticks marking a broken y-axis between two stacked panels."""
    d = size
    kw = dict(color=INK, clip_on=False, lw=0.9, solid_capstyle="butt", zorder=6)
    ax_top.plot((-d, +d), (-d, +d), transform=ax_top.transAxes, **kw)
    ax_top.plot((1 - d, 1 + d), (-d, +d), transform=ax_top.transAxes, **kw)
    ax_bot.plot((-d, +d), (1 - d, 1 + d), transform=ax_bot.transAxes, **kw)
    ax_bot.plot((1 - d, 1 + d), (1 - d, 1 + d), transform=ax_bot.transAxes, **kw)


def _trim_white_margins(img: Image.Image, *, threshold: int = 248, pad: int = 12) -> Image.Image:
    arr = np.asarray(img.convert("RGB"))
    mask = np.any(arr < threshold, axis=2)
    if not mask.any():
        return img
    ys, xs = np.where(mask)
    y0, y1 = max(int(ys.min()) - pad, 0), min(int(ys.max()) + pad + 1, arr.shape[0])
    x0, x1 = max(int(xs.min()) - pad, 0), min(int(xs.max()) + pad + 1, arr.shape[1])
    return img.crop((x0, y0, x1, y1))


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def _flatten_vmd_floor(img: Image.Image) -> Image.Image:
    """Whiten VMD floor/AO connected to the canvas; keep cage self-shadow."""
    from PIL import ImageDraw

    im = img.convert("RGB")
    w, h = im.size
    for xy in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1)):
        ImageDraw.floodfill(im, xy, (255, 255, 255), thresh=48)
    arr = np.asarray(im)
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    chroma = np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b)
    mx = np.maximum(np.maximum(r, g), b)
    shadow = (chroma < 28) & (mx > 170)
    out = arr.copy()
    out[shadow] = 255
    return Image.fromarray(out)


def _prep_structure_image(path: Path) -> Image.Image:
    from PIL import ImageEnhance

    im = _flatten_vmd_floor(Image.open(path))
    im = _trim_white_margins(im, threshold=252, pad=3)
    im = ImageEnhance.Contrast(im).enhance(1.18)
    im = ImageEnhance.Color(im).enhance(1.12)
    im = ImageEnhance.Sharpness(im).enhance(1.2)
    return im


def _structure_panels() -> list[Image.Image]:
    """ε=0 tetramers in caption order: pristine, B, N, P."""
    root = repo_root() / "paper/figures/final_figures"
    names = (
        "C60_strain_+0.0_pristine_synergy.png",
        "C60_strain_+0.0_B_doped_synergy.png",
        "C60_strain_+0.0_N_doped_synergy.png",
        "C60_strain_+0.0_P_doped_synergy.png",
    )
    return [_prep_structure_image(root / name) for name in names]


def _ref_pristine_dE_meV_atom() -> tuple[np.ndarray, np.ndarray]:
    ref = load_json("experiments/analysis/reference_placement_pbed3.json")
    e = {float(k): float(v) for k, v in ref["pristine"]["strain_energies_ha"].items()}
    e0 = e[0.0]
    ha = 27211.386245988
    n_at = 240
    xs = np.array(sorted(e))
    ys = np.array([(e[x] - e0) * ha / n_at * 1000.0 for x in xs])
    return xs, ys


def _local_d_sigma_paths() -> dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    loc = load_json("experiments/analysis/local_structure_tetramer.json")
    out: dict[str, list] = {}
    for r in loc["records"]:
        out.setdefault(r["dopant"], []).append(
            (float(r["strain_pct"]), float(r["mean_d_ang"]), float(r["std_d_ang"]))
        )
    paths = {}
    for dop, rows in out.items():
        rows = sorted(rows)
        paths[dop] = (
            np.array([r[0] for r in rows]),
            np.array([r[1] for r in rows]),
            np.array([r[2] for r in rows]),
        )
    return paths


def _hirsh_paths() -> dict[str, tuple[np.ndarray, np.ndarray]]:
    h = load_hirshfeld_strain_paths()
    return {
        d: (np.array([p[0] for p in sorted(pts)]), np.array([p[1] for p in sorted(pts)]))
        for d, pts in h.items()
    }


def _pdos_path(dop: str, strain_tag: str) -> Path:
    root = repo_root() / "dft_results/exp_7_electronic_structure/outputs"
    return root / f"elec_{strain_tag}_{dop}-k1-1.pdos"


def build_fig1() -> tuple[Path, Path]:
    apply_nature_style()
    gaps = parse_exp7_gaps()
    alpha_ref, _, _, _alpha_err = load_reference_pbed3_alpha_S()

    fig = plt.figure(figsize=(PRB_WIDTH_IN, 5.45), facecolor="white")
    gs = GridSpec(
        2,
        2,
        figure=fig,
        height_ratios=[1.05, 1.12],
        hspace=0.38,
        wspace=0.30,
        left=0.08,
        right=0.98,
        top=0.96,
        bottom=0.08,
    )
    ax_b = fig.add_subplot(gs[0, 1])
    gap_gs = gs[1, 0].subgridspec(2, 1, height_ratios=[1.05, 1.0], hspace=0.08)
    ax_hi = fig.add_subplot(gap_gs[0])
    ax_lo = fig.add_subplot(gap_gs[1])
    ax_d = fig.add_subplot(gs[1, 1])

    struct_gs = gs[0, 0].subgridspec(2, 2, wspace=0.04, hspace=0.18)
    for i, (im, lab) in enumerate(zip(_structure_panels(), ("pristine", "B", "N", "P"))):
        ax = fig.add_subplot(struct_gs[i // 2, i % 2])
        ax.imshow(np.asarray(im), interpolation="lanczos")
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_xlabel(lab, fontsize=7.6, fontweight="bold", color=INK, labelpad=1)
        if i == 0:
            panel_label(ax, "a", nature=True)

    panel_label(ax_b, "b", nature=True)
    grid = np.linspace(-2.5, 2.5, 600)
    strain_specs = [
        (r"$-5$", "neg5p0", 0.0),
        (r"$0$", "pos0p0", 1.15),
        (r"$+5$", "pos5p0", 2.30),
    ]
    yticks, yticklabels = [], []
    for lab, tag, yoff in strain_specs:
        path = _pdos_path("N", tag)
        if not path.is_file():
            continue
        series = parse_pdos(path)
        dos = gaussian_dos(series.energy_ev, series.pi_weight, grid, sigma_ev=0.065)
        dos = dos / (np.max(dos) + 1e-12)
        curve = yoff + dos * 0.92
        ax_b.fill_between(grid, yoff, curve, color=DOPANT_COLORS["N"], alpha=0.22, linewidth=0, zorder=2)
        ax_b.plot(grid, curve, color=DOPANT_COLORS["N"], lw=1.45, zorder=3, solid_capstyle="round")
        ax_b.plot(grid, np.full_like(grid, yoff), color=DOPANT_COLORS["N"], lw=0.45, alpha=0.35, zorder=1)
        yticks.append(yoff)
        yticklabels.append(lab)
    ax_b.axvline(0.0, color=INK, lw=0.7, ls=(0, (2.2, 1.8)), zorder=2)
    ax_b.text(0.04, 1.02, r"$E_{\mathrm{F}}$", transform=ax_b.transAxes, ha="left", va="bottom", fontsize=6.6, color=NATURE_GRAY)
    ax_b.set_xlim(-2.35, 2.45)
    ax_b.set_ylim(-0.22, 3.42)
    ax_b.set_yticks(yticks)
    ax_b.set_yticklabels(yticklabels)
    ax_b.set_xlabel("Energy (eV)")
    ax_b.set_ylabel(r"$\epsilon$ (%)")
    ax_b.text(
        0.03,
        0.97,
        r"N $\pi$-DOS",
        transform=ax_b.transAxes,
        ha="left",
        va="top",
        fontsize=7.0,
        color=INK,
    )
    style_axes(ax_b)

    panel_label(ax_hi, "c", nature=True)
    pris = sorted([(p.strain_pct, p.gap_ev) for p in gaps if p.dopant == "pristine" and p.converged])
    if len(pris) >= 2:
        xs, ys = map(np.array, zip(*pris))
        plot_trajectory(ax_hi, xs, ys, DOPANT_COLORS["pristine"], fill=False, lw=1.55, ms=5.2, filled=True)
    ax_hi.set_ylim(0.82, 1.72)
    ax_hi.set_ylabel(r"$E_{\mathrm{H-L}}$ (eV)")
    style_axes(ax_hi)
    ax_hi.tick_params(labelbottom=False, bottom=False)
    ax_hi.spines["bottom"].set_visible(False)
    ax_hi.text(0.98, 0.90, "pristine", transform=ax_hi.transAxes, ha="right", va="top", fontsize=7.0, color=DOPANT_COLORS["pristine"])

    for dop in ("B", "N", "P"):
        pts = sorted([(p.strain_pct, p.gap_ev) for p in gaps if p.dopant == dop and p.converged])
        if len(pts) < 2:
            continue
        xs, ys = map(np.array, zip(*pts))
        plot_trajectory(ax_lo, xs, ys, DOPANT_COLORS[dop], fill=False, lw=1.45, ms=4.8, filled=True)
        ax_lo.annotate(
            dop,
            xy=(float(xs[-1]), float(ys[-1])),
            xytext=(6, 0),
            textcoords="offset points",
            fontsize=7.0,
            color=DOPANT_COLORS[dop],
            va="center",
            ha="left",
        )
    ax_lo.axhline(0.0, color="#C5C9CE", lw=0.6, ls=(0, (2, 2)), zorder=0)
    ax_lo.set_ylim(-0.24, 0.32)
    ax_lo.set_xlim(-5.6, 6.6)
    ax_hi.set_xlim(-5.6, 6.6)
    ax_lo.set_xlabel(r"$\epsilon$ (%)")
    style_axes(ax_lo)
    ax_lo.spines["top"].set_visible(False)
    ax_lo.tick_params(top=False)
    _axis_break(ax_hi, ax_lo)

    panel_label(ax_d, "d", nature=True)
    xs, ys = _ref_pristine_dE_meV_atom()
    plot_trajectory(ax_d, xs, ys, INK, label="DFT", fill=False, lw=1.55, ms=5.4, filled=True)
    coef = np.polyfit(xs, ys, 1)
    xfit = np.linspace(float(xs.min()), float(xs.max()), 80)
    ax_d.plot(
        xfit,
        coef[0] * xfit + coef[1],
        "--",
        color=NATURE_GRAY,
        lw=1.0,
        label=rf"linear fit, $\alpha_{{\mathrm{{p}}}}\approx{float(alpha_ref['pristine']):.1f}$ meV/%",
    )
    add_reference_lines(ax_d)
    ax_d.set_xlabel(r"$\epsilon$ (%)")
    ax_d.set_ylabel(r"$\Delta E_{\mathrm{pris}}$ (meV/atom)")
    style_axes(ax_d)
    _legend_in(ax_d, loc="upper left", fontsize=6.4)

    return _save(fig, "figure_prb_1_electronic")


def build_fig2() -> tuple[Path, Path]:
    apply_nature_style()
    audit = load_json("experiments/analysis/sdc/sdc_exp10_synergy_audit.json")
    s_rig, s_rel = load_periodic_relax_n1_P()

    fig = plt.figure(figsize=(PRB_WIDTH_IN, 5.05), facecolor="white")
    gs = GridSpec(
        2,
        2,
        figure=fig,
        width_ratios=[1.55, 1.0],
        height_ratios=[1.15, 0.95],
        hspace=0.40,
        wspace=0.30,
        left=0.08,
        right=0.98,
        top=0.88,
        bottom=0.09,
    )
    ax_a, ax_b = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
    ax_c, ax_d = fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])

    dopants = ["B", "N", "P"]
    ns = [1, 2, 4, 6, 8]

    panel_label(ax_a, "a", nature=True)
    ax_a.axhspan(-SIGMA_S_MEV, SIGMA_S_MEV, color="#E8E8E8", zorder=0)
    ax_a.axhline(0.0, color="#D5D5D5", lw=0.65, zorder=1)
    # Per-size uncertainty: the pristine +3% strain reference must be
    # n-independent, so its deviation from the converged n=1,4,6 plateau is a
    # systematic uncertainty on that row and is added to the reporting floor.
    ref_audit = load_json("experiments/analysis/reference_consistency_audit.json")
    ref_sys = {
        int(k): float(v["systematic_uncertainty_meV_per_atom"])
        for k, v in ref_audit["per_n"].items()
    }
    core_n = {1, 2, 4}
    ref_n = {6, 8}
    for dop in dopants:
        rows = synergy_rows(audit, dop)
        n_all = np.array([r[0] for r in rows], dtype=float)
        s_all = np.array([r[1] for r in rows])
        core = np.array([int(n) in core_n for n in n_all])
        ref = np.array([int(n) in ref_n for n in n_all])
        yerr = np.array([SIGMA_S_MEV + ref_sys.get(int(n), 0.0) for n in n_all])
        # Matched 400 Ry core only: filled markers and a connecting line.
        plot_trajectory(
            ax_a,
            n_all[core],
            s_all[core],
            DOPANT_COLORS[dop],
            label=dop,
            fill=False,
            lw=1.7,
            ms=7.0,
            filled=True,
        )
        # 350 Ry n=6,8: open markers, no connecting line, not used for inference.
        ax_a.plot(
            n_all[ref],
            s_all[ref],
            linestyle="None",
            marker="o",
            markersize=6.4,
            markerfacecolor="white",
            markeredgecolor=DOPANT_COLORS[dop],
            markeredgewidth=1.35,
            zorder=5,
        )
        ax_a.errorbar(
            n_all,
            s_all,
            yerr=yerr,
            fmt="none",
            ecolor=DOPANT_COLORS[dop],
            elinewidth=0.7,
            capsize=2.0,
            capthick=0.65,
            alpha=0.85,
            zorder=4,
        )
    # Pale columns only on the 350 Ry reference sizes, not the 400 Ry n=2 core.
    for n in sorted(ref_n):
        ax_a.axvspan(int(n) - 0.28, int(n) + 0.28, color="#F8EEEE", alpha=1.0, lw=0, zorder=0)
    ax_a.set_xticks(ns)
    ax_a.set_xlim(0.55, 8.70)
    ax_a.set_ylim(-40.0, 17.5)
    ax_a.set_xlabel(r"Supercell size $n$  ($n\times\mathrm{C}_{60}$)", labelpad=1)
    ax_a.set_ylabel(r"$\mathcal{S}$ (meV/atom)", labelpad=4)
    ax_a.tick_params(axis="x", pad=2)
    style_axes(ax_a)
    from matplotlib.lines import Line2D
    key = [
        Line2D([0], [0], color=DOPANT_COLORS[d], marker="o", mfc=DOPANT_COLORS[d], mec="white", mew=0.6, lw=1.6, ms=5.6, label=d)
        for d in dopants
    ] + [
        Line2D([0], [0], color=INK, marker="o", mfc=INK, mec="white", lw=0, ms=5.6, label="400 Ry"),
        Line2D([0], [0], color=INK, marker="o", mfc="white", mec=INK, mew=1.1, lw=0, ms=5.6, label="350 Ry"),
    ]
    ax_a.legend(
        handles=key,
        loc="lower left",
        bbox_to_anchor=(0.16, 1.02),
        ncol=5,
        frameon=False,
        fontsize=6.4,
        borderaxespad=0.0,
        handletextpad=0.3,
        columnspacing=0.7,
    )
    p_rows = dict(synergy_rows(audit, "P"))
    s_p4 = float(p_rows[4])
    s_p1 = float(p_rows[1])
    ax_a.annotate(
        f"{s_p1:.1f}",
        xy=(1.0, s_p1),
        xytext=(8, 7),
        textcoords="offset points",
        fontsize=6.4,
        color=DOPANT_COLORS["P"],
        ha="left",
        va="center",
        zorder=6,
    )
    ax_a.annotate(
        f"{s_p4:.1f}",
        xy=(4.0, s_p4),
        xytext=(0, 7),
        textcoords="offset points",
        fontsize=6.4,
        color=DOPANT_COLORS["P"],
        ha="center",
        va="bottom",
        zorder=6,
    )
    ax_a.text(
        7.0,
        15.2,
        "350 Ry",
        ha="center",
        va="center",
        fontsize=6.4,
        color=NATURE_GRAY,
        zorder=6,
    )

    panel_label(ax_b, "b", nature=True)
    ax_b.axhspan(-SIGMA_S_MEV, SIGMA_S_MEV, color="#F0F2F4", zorder=0)
    ax_b.plot([0, 1], [s_rig, s_rel], "-", color=DOPANT_COLORS["P"], lw=2.0, zorder=2, solid_capstyle="round")
    ax_b.plot(
        [0, 1],
        [s_rig, s_rel],
        "o",
        color=DOPANT_COLORS["P"],
        markersize=9.0,
        markerfacecolor=DOPANT_COLORS["P"],
        markeredgecolor="white",
        markeredgewidth=0.9,
        zorder=3,
    )
    add_reference_lines(ax_b, vzero=False)
    ax_b.set_xlim(-0.35, 1.35)
    ax_b.set_xticks([0, 1])
    ax_b.set_xticklabels(["rigid", "relaxed"])
    ax_b.set_ylabel(r"$\mathcal{S}$ (meV/atom)")
    style_axes(ax_b)
    ax_b.annotate(
        f"{s_rig:.1f}",
        xy=(0, s_rig),
        xytext=(0, 9),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=7.0,
        color=DOPANT_COLORS["P"],
    )
    ax_b.annotate(
        f"{s_rel:.1f}",
        xy=(1, s_rel),
        xytext=(0, 9),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=7.0,
        color=INK,
    )
    ylo, yhi = min(s_rig, s_rel), max(s_rig, s_rel)
    ypad = max(abs(s_rig - s_rel) * 0.28, 2.4)
    ax_b.set_ylim(ylo - ypad * 0.45, yhi + ypad)

    panel_label(ax_c, "c", nature=True)
    draw_additive_screening_schematic(ax_c)
    panel_label(ax_d, "d", nature=True)
    draw_energy_coupling_schematic(ax_d)
    return _save(fig, "figure_prb_2_synergy")


def build_fig3() -> tuple[Path, Path]:
    apply_nature_style()
    alpha_ref, _, _, alpha_err = load_reference_pbed3_alpha_S()
    audit_mev = load_json("experiments/analysis/sdc/sdc_exp10_synergy_audit.json")
    qpaths, dpaths = _hirsh_paths(), _local_d_sigma_paths()
    dopants = ["B", "N", "P"]

    fig = plt.figure(figsize=(PRB_WIDTH_IN, 5.55), facecolor="white")
    gs = GridSpec(2, 2, figure=fig, hspace=0.38, wspace=0.28, left=0.09, right=0.97, top=0.90, bottom=0.10)
    ax_a, ax_b, ax_c, ax_d = [fig.add_subplot(gs[i, j]) for i in range(2) for j in range(2)]

    panel_label(ax_a, "a", nature=True)
    for d in dopants:
        xs, ys = qpaths[d]
        plot_trajectory(ax_a, xs, ys, DOPANT_COLORS[d], label=d, fill=False, lw=1.7, ms=5.6, filled=True)
    add_reference_lines(ax_a, vzero=True)
    strain_guide(ax_a)
    ax_a.set_xlabel(r"$\epsilon$ (%)")
    ax_a.set_ylabel(r"$q_{\mathrm{Hirsh}}$ ($e$)")
    style_axes(ax_a)

    panel_label(ax_b, "b", nature=True)
    for d in dopants:
        xs, dbar, _sig = dpaths[d]
        # sigma(d_bar) is panel (c). Drawing it as y-error here spans the
        # whole axis and hides the mean nearest-neighbor trend.
        plot_trajectory(ax_b, xs, dbar, DOPANT_COLORS[d], label=d, fill=False, lw=1.6, ms=5.2, filled=True)
    d_all = np.concatenate([dpaths[d][1] for d in dopants])
    d_pad = 0.35 * (float(d_all.max()) - float(d_all.min()) + 1e-4)
    ax_b.set_ylim(float(d_all.min()) - d_pad, float(d_all.max()) + d_pad)
    add_reference_lines(ax_b, vzero=False)
    strain_guide(ax_b)
    ax_b.set_xlabel(r"$\epsilon$ (%)")
    ax_b.set_ylabel(r"$\bar{d}$ (Å)")
    style_axes(ax_b)

    panel_label(ax_c, "c", nature=True)
    for d in dopants:
        xs, _, sig = dpaths[d]
        plot_trajectory(ax_c, xs, sig * 1e3, DOPANT_COLORS[d], label=d, fill=False, lw=1.6, ms=5.2, filled=True)
    strain_guide(ax_c)
    ax_c.set_xlabel(r"$\epsilon$ (%)")
    ax_c.set_ylabel(r"$\sigma(\bar{d})$ (mÅ)")
    style_axes(ax_c)

    panel_label(ax_d, "d", nature=True)
    abs_alpha = {d: abs(float(alpha_ref[d])) for d in dopants}
    abs_s4 = {d: abs(dict(synergy_rows(audit_mev, d))[4]) for d in dopants}
    abs_s1 = {d: abs(dict(synergy_rows(audit_mev, d))[1]) for d in dopants}
    amax = max(abs_alpha.values()) * 1.15
    smax = max(abs_s4.values()) * 1.25
    s1_ref = max(abs_s1.values())
    # Signed alpha keeps the donor/acceptor sign split visible and, unlike |alpha|,
    # stays well defined when the fit standard error exceeds the slope.
    signed_alpha = {d: float(alpha_ref[d]) for d in dopants}
    xlo = min(signed_alpha[d] - float(alpha_err.get(d, 0.0)) for d in dopants)
    xhi = max(signed_alpha[d] + float(alpha_err.get(d, 0.0)) for d in dopants)
    xpad = 0.08 * (xhi - xlo)
    ax_d.set_xlim(xlo - xpad, xhi + xpad)
    ax_d.set_ylim(-smax * 0.08, smax)
    ax_d.axhspan(0, SIGMA_S_MEV, color="#F0F2F4", lw=0, zorder=0)
    ax_d.axvline(0.0, color="#D5D5D5", lw=0.65, zorder=0)
    for d in dopants:
        xerr = float(alpha_err.get(d, 0.0))
        ax_d.errorbar(
            signed_alpha[d],
            abs_s4[d],
            xerr=xerr if (np.isfinite(xerr) and xerr > 0) else None,
            yerr=SIGMA_S_MEV,
            fmt="none",
            ecolor=DOPANT_COLORS[d],
            elinewidth=0.55,
            capsize=2.0,
            capthick=0.5,
            alpha=0.45,
            zorder=2,
        )
        scatter_dopant(
            ax_d,
            signed_alpha[d],
            abs_s4[d],
            d,
            size=_marker_area(abs_s1[d], s1_ref),
            offset={"B": (10, 12), "N": (12, 12), "P": (-24, 10)}[d],
        )
    ax_d.set_xlabel(r"$\alpha$ (meV/%)")
    ax_d.set_ylabel(r"$|\mathcal{S}|_{n=4}$ (meV/atom)")
    style_axes(ax_d)
    from matplotlib.lines import Line2D
    fig.legend(
        handles=[
            Line2D([0], [0], color=DOPANT_COLORS[d], marker="o", mfc=DOPANT_COLORS[d], mec="white", mew=0.6, lw=1.6, ms=5.4, label=d)
            for d in dopants
        ],
        loc="upper center",
        bbox_to_anchor=(0.55, 0.985),
        ncol=3,
        frameon=False,
        fontsize=7.2,
        handlelength=1.6,
        columnspacing=1.2,
    )
    return _save(fig, "figure_prb_3_decoupling")


def build_fig4() -> tuple[Path, Path]:
    apply_nature_style()
    local = load_local_structure_summary()
    qpaths, dpaths = _hirsh_paths(), _local_d_sigma_paths()
    audit = load_json("experiments/analysis/sdc/sdc_exp10_synergy_audit.json")
    mm = {row["dopant"]: row for row in load_mismatch_rows()}
    dopants = ["B", "N", "P"]

    fig = plt.figure(figsize=(PRB_WIDTH_IN, 5.5), facecolor="white")
    gs = GridSpec(2, 2, figure=fig, hspace=0.34, wspace=0.28, left=0.09, right=0.97, top=0.94, bottom=0.11)
    ax_a, ax_b, ax_c, ax_d = [fig.add_subplot(gs[i, j]) for i in range(2) for j in range(2)]

    s_abs = {d: abs(dict(synergy_rows(audit, d))[4]) for d in dopants}
    dd = {d: abs(local[d]["delta_d_eps0_to_eps3_ang"]) * 1e3 for d in dopants}
    dq_frac = {}
    for d in dopants:
        xs, ys = qpaths[d]
        qmap = dict(zip(xs.tolist(), ys.tolist()))
        dq_frac[d] = 100.0 * abs(qmap[3.0] - qmap[0.0]) / abs(qmap[0.0])
    dr = {d: abs(float(local[d]["radius_delta_pm"])) for d in dopants}
    sref = max(s_abs.values())

    panel_label(ax_a, "a", nature=True)
    ax_a.set_xlim(-0.8, max(dd.values()) * 1.35)
    ax_a.set_ylim(0, max(dq_frac.values()) * 1.28)
    for d in dopants:
        scatter_dopant(ax_a, dd[d], dq_frac[d], d, size=_marker_area(s_abs[d], sref),
                       offset={"B": (14, -14), "N": (-18, 12), "P": (14, 12)}[d])
    ax_a.set_xlabel(r"$|\Delta\bar{d}|_{0\to+3\%}$ (mÅ)")
    ax_a.set_ylabel(r"$|\Delta q/q|_{0\to+3\%}$ (%)")
    style_axes(ax_a)

    panel_label(ax_b, "b", nature=True)
    ax_b.set_xlim(-2, max(dr.values()) * 1.22)
    ax_b.set_ylim(-max(s_abs.values()) * 0.1, max(s_abs.values()) * 1.28)
    # Reporting floor: values inside the band are not resolved against the
    # protocol uncertainty, which is what separates P from B and N.
    ax_b.axhspan(0, SIGMA_S_MEV, color="#F0F2F4", lw=0, zorder=0)
    ax_b.text(
        0.98, SIGMA_S_MEV, r"$\pm 2$ meV/atom floor",
        transform=ax_b.get_yaxis_transform(), ha="right", va="bottom",
        fontsize=5.8, color=NATURE_GRAY, zorder=1,
    )
    for d in dopants:
        ax_b.errorbar(
            dr[d],
            s_abs[d],
            yerr=SIGMA_S_MEV,
            fmt="none",
            ecolor=DOPANT_COLORS[d],
            elinewidth=0.85,
            capsize=2.2,
            capthick=0.7,
            alpha=0.8,
            zorder=2,
        )
        scatter_dopant(ax_b, dr[d], s_abs[d], d, size=130,
                       offset={"B": (13, 9), "N": (-15, -14), "P": (-22, 8)}[d])
    ax_b.set_xlabel(r"$|\Delta r_{\mathrm{cov}}|$ (pm)")
    ax_b.set_ylabel(r"$|\mathcal{S}|_{n=4}$ (meV/atom)")
    style_axes(ax_b)

    panel_label(ax_c, "c", nature=True)
    for d in dopants:
        xs_q, ys_q = qpaths[d]
        xs_d, ys_d, _ = dpaths[d]
        q0, d0 = float(dict(zip(xs_q, ys_q))[0.0]), float(dict(zip(xs_d, ys_d))[0.0])
        ax_c.plot(
            xs_q, ys_q / q0, "-o", color=DOPANT_COLORS[d], markersize=5.2,
            markerfacecolor=DOPANT_COLORS[d], markeredgecolor="white", markeredgewidth=0.6,
            lw=1.55, label=d, zorder=3,
        )
        ax_c.plot(xs_d, ys_d / d0, "--", color=DOPANT_COLORS[d], lw=1.15, alpha=0.9, zorder=2)
        ax_c.annotate(
            d,
            xy=(float(xs_q[-1]), float(ys_q[-1]) / q0),
            xytext=(5, 0),
            textcoords="offset points",
            fontsize=7.0,
            color=DOPANT_COLORS[d],
            va="center",
            ha="left",
            zorder=4,
        )
    ax_c.axhline(1.0, color="#D5D5D5", lw=0.7)
    strain_guide(ax_c)
    ax_c.set_xlim(-5.8, 6.8)
    ax_c.set_xlabel(r"$\epsilon$ (%)")
    ax_c.set_ylabel(r"value / value$_{\epsilon=0}$")
    ax_c.set_title(
        r"solid $q/q_0$    dashed $\bar{d}/\bar{d}_0$",
        loc="right",
        fontsize=6.5,
        color=NATURE_GRAY,
        pad=2,
    )
    style_axes(ax_c)

    panel_label(ax_d, "d", nature=True)
    mfs = {d: 100.0 * float(mm[d]["mismatch_fraction"]) for d in dopants}
    s1s = {d: abs(float(mm[d]["S_meV_per_atom_n1"])) for d in dopants}
    ax_d.set_xlim(-2, max(mfs.values()) * 1.22)
    ax_d.set_ylim(-max(s1s.values()) * 0.1, max(s1s.values()) * 1.28)
    ax_d.axhspan(0, SIGMA_S_MEV, color="#F0F2F4", lw=0, zorder=0)
    ax_d.text(
        0.98, SIGMA_S_MEV, r"$\pm 2$ meV/atom floor",
        transform=ax_d.get_yaxis_transform(), ha="right", va="bottom",
        fontsize=5.8, color=NATURE_GRAY, zorder=1,
    )
    for d in dopants:
        ax_d.errorbar(
            mfs[d], s1s[d], yerr=SIGMA_S_MEV, fmt="none",
            ecolor=DOPANT_COLORS[d], elinewidth=0.85, capsize=2.2,
            capthick=0.7, alpha=0.8, zorder=2,
        )
        scatter_dopant(ax_d, mfs[d], s1s[d], d, size=140,
                       offset={"B": (13, 10), "N": (-15, -14), "P": (-22, 8)}[d])
    ax_d.set_xlabel("Covalent mismatch (%)")
    ax_d.set_ylabel(r"$|\mathcal{S}|_{n=1}$ (meV/atom)")
    style_axes(ax_d)
    return _save(fig, "figure_prb_4_mechanism")


def main() -> None:
    for builder, name in (
        (build_fig1, "Fig.1"),
        (build_fig2, "Fig.2"),
        (build_fig3, "Fig.3"),
        (build_fig4, "Fig.4"),
    ):
        pdf, _ = builder()
        print(f"{name}: {pdf}")


if __name__ == "__main__":
    main()
