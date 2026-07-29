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
    draw_physics_coupling_schematic,
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


def _trim_white_margins(img: Image.Image, *, threshold: int = 248, pad: int = 12) -> Image.Image:
    arr = np.asarray(img.convert("RGB"))
    mask = np.any(arr < threshold, axis=2)
    if not mask.any():
        return img
    ys, xs = np.where(mask)
    y0, y1 = max(int(ys.min()) - pad, 0), min(int(ys.max()) + pad + 1, arr.shape[0])
    x0, x1 = max(int(xs.min()) - pad, 0), min(int(xs.max()) + pad + 1, arr.shape[1])
    return img.crop((x0, y0, x1, y1))


def _structure_tetraptych() -> np.ndarray:
    root = repo_root() / "paper/figures/final_figures"
    specs = [
        ("Pristine", "C60_strain_+0.0_pristine_synergy.png"),
        ("B", "C60_strain_+0.0_B_doped_synergy.png"),
        ("N", "C60_strain_+0.0_N_doped_synergy.png"),
        ("P", "C60_strain_+0.0_P_doped_synergy.png"),
    ]
    imgs = []
    for _, name in specs:
        path = root / name
        if not path.is_file():
            raise FileNotFoundError(path)
        imgs.append(_trim_white_margins(Image.open(path)))
    h = max(im.size[1] for im in imgs)
    resized = []
    for im in imgs:
        w = int(round(im.size[0] * h / im.size[1]))
        resized.append(im.resize((w, h), Image.Resampling.LANCZOS))
    gutter = max(10, h // 36)
    total_w = sum(im.size[0] for im in resized) + gutter * (len(resized) - 1)
    canvas = Image.new("RGB", (total_w, h), (255, 255, 255))
    x = 0
    for im in resized:
        canvas.paste(im, (x, 0))
        x += im.size[0] + gutter
    return np.asarray(canvas)


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
    alpha_ref, _, _ = load_reference_pbed3_alpha_S()

    fig = plt.figure(figsize=(PRB_WIDTH_IN, 7.2), facecolor="white")
    gs = GridSpec(3, 2, figure=fig, height_ratios=[0.82, 1.32, 1.18],
                  hspace=0.38, wspace=0.26, left=0.08, right=0.97, top=0.96, bottom=0.08)
    ax_a = fig.add_subplot(gs[0, :])
    ax_b = fig.add_subplot(gs[1, 0])
    ax_c = fig.add_subplot(gs[1, 1])
    ax_d = fig.add_subplot(gs[2, 0])
    ax_e = fig.add_subplot(gs[2, 1])

    panel_label(ax_a, "a", nature=True)
    ax_a.set_facecolor("#FAFAFA")
    ax_a.imshow(_structure_tetraptych(), aspect="equal", interpolation="lanczos")
    ax_a.axis("off")
    structure_gallery_labels(ax_a, ("Pristine", "B", "N", "P"))

    panel_label(ax_b, "b", nature=True)
    grid = np.linspace(-2.5, 2.5, 600)
    strain_specs = [("-5%", "neg5p0", 0.0, 0.30), ("0%", "pos0p0", 1.20, 0.55), ("+5%", "pos5p0", 2.35, 0.85)]
    for lab, tag, yoff, alpha in strain_specs:
        path = _pdos_path("N", tag)
        if not path.is_file():
            continue
        series = parse_pdos(path)
        dos = gaussian_dos(series.energy_ev, series.pi_weight, grid, sigma_ev=0.065)
        dos = dos / (np.max(dos) + 1e-12)
        curve = yoff + dos * 0.92
        ax_b.fill_between(grid, yoff, curve, color=DOPANT_COLORS["N"], alpha=alpha * 0.35, lw=0, zorder=1)
        ax_b.plot(grid, curve, color=DOPANT_COLORS["N"], lw=1.35, alpha=alpha, zorder=3)
        ax_b.text(2.35, yoff + 0.48, lab, fontsize=7, fontweight="bold", color=DOPANT_COLORS["N"], ha="right")
    ax_b.axvspan(-2.5, 0, color="#F3F3F3", zorder=0)
    ax_b.axvline(0, color=INK, lw=0.85, alpha=0.55, zorder=2)
    ax_b.set_xlim(-2.35, 2.45)
    ax_b.set_ylim(-0.08, 3.5)
    ax_b.set_yticks([])
    ax_b.set_xlabel("Energy (eV)")
    style_axes(ax_b)
    panel_subtitle(ax_b, r"N $\pi$-DOS along $\epsilon$")

    panel_label(ax_c, "c", nature=True)
    for dop in ("pristine", "B", "N", "P"):
        pts = sorted([(p.strain_pct, p.gap_ev) for p in gaps if p.dopant == dop and p.converged])
        if len(pts) < 2:
            continue
        xs, ys = map(np.array, zip(*pts))
        plot_trajectory(ax_c, xs, ys, DOPANT_COLORS[dop], label=dop, fill_to=min(0, ys.min()))
    add_reference_lines(ax_c)
    ax_c.set_xlabel(r"$\epsilon$ (%)")
    ax_c.set_ylabel(r"$E_g$ (eV)")
    style_axes(ax_c)
    _legend_in(ax_c, loc="upper right", ncol=2, fontsize=6.8)

    panel_label(ax_d, "d", nature=True)
    xs, ys = _ref_pristine_dE_meV_atom()
    plot_trajectory(ax_d, xs, ys, INK, label="DFT", fill_to=0)
    coef = np.polyfit(xs, ys, 1)
    xfit = np.linspace(xs.min(), xs.max(), 80)
    ax_d.plot(xfit, coef[0] * xfit + coef[1], "--", color=DOPANT_COLORS["P"], lw=1.25, alpha=0.85,
              label=rf"linear fit, $\alpha_{{\mathrm{{p}}}}\approx{float(alpha_ref['pristine']):.1f}$ meV/%")
    add_reference_lines(ax_d)
    ax_d.set_xlabel(r"$\epsilon$ (%)")
    ax_d.set_ylabel(r"$\Delta E_{\mathrm{pris}}$ (meV/atom)")
    style_axes(ax_d)
    _legend_in(ax_d, loc="upper left", fontsize=6.8)

    panel_label(ax_e, "e", nature=True)
    draw_physics_coupling_schematic(ax_e)
    return _save(fig, "figure_prb_1_electronic")


def build_fig2() -> tuple[Path, Path]:
    apply_nature_style()
    audit = load_json("experiments/analysis/sdc/sdc_exp10_synergy_audit.json")
    fits = audit.get("size_scaling_fits", {})
    s_rig, s_rel = load_periodic_relax_n1_P()

    fig = plt.figure(figsize=(PRB_WIDTH_IN, 5.2), facecolor="white")
    gs = GridSpec(2, 3, figure=fig, height_ratios=[1.12, 1.0],
                  hspace=0.36, wspace=0.34, left=0.08, right=0.97, top=0.93, bottom=0.11)
    ax_a, ax_b = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1:])
    ax_c, ax_d, ax_e = fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1]), fig.add_subplot(gs[1, 2])

    dopants = ["B", "N", "P"]
    ns = [1, 2, 4, 6, 8]
    mat = np.full((len(dopants), len(ns)), np.nan)
    for i, dop in enumerate(dopants):
        rows = dict(synergy_rows(audit, dop))
        for j, n in enumerate(ns):
            if n in rows:
                mat[i, j] = rows[n]

    panel_label(ax_a, "a", nature=True)
    vmax = float(np.nanmax(np.abs(mat)))
    im = ax_a.imshow(mat, aspect="auto", cmap=SYNERGY_CMAP, vmin=-vmax, vmax=vmax, interpolation="nearest")
    ax_a.set_xticks(range(len(ns)))
    ax_a.set_xticklabels([str(n) for n in ns])
    ax_a.set_yticks(range(len(dopants)))
    ax_a.set_yticklabels(dopants)
    ax_a.set_xlabel(r"$n$")
    for i in range(len(dopants)):
        for j in range(len(ns)):
            v = mat[i, j]
            if np.isnan(v):
                continue
            tc = "white" if abs(v) > 0.42 * vmax else INK
            ax_a.text(j, i, f"{v:+.1f}", ha="center", va="center", fontsize=7, fontweight="bold", color=tc)
    ax_a.set_xticks(np.arange(-0.5, len(ns), 1), minor=True)
    ax_a.set_yticks(np.arange(-0.5, len(dopants), 1), minor=True)
    ax_a.grid(which="minor", color="white", linewidth=1.2)
    ax_a.tick_params(which="minor", bottom=False, left=False)
    cbar = fig.colorbar(im, ax=ax_a, fraction=0.05, pad=0.03)
    style_colorbar(cbar, label=r"$\mathcal{S}$ (meV/atom)")
    style_axes(ax_a)

    panel_label(ax_b, "b", nature=True)
    ax_b.axvspan(3.4, 4.6, color="#F4F4F4", zorder=0)
    n_fit = np.linspace(1.0, 8.5, 120)
    for dop in dopants:
        rows = synergy_rows(audit, dop)
        n_all = np.array([r[0] for r in rows], dtype=float)
        s_all = np.array([r[1] for r in rows])
        plot_trajectory(ax_b, n_all, s_all, DOPANT_COLORS[dop], label=dop, fill_to=0)
        if dop in fits:
            s_inf, a_coef = float(fits[dop]["S_infinity"]), float(fits[dop]["A"])
            ax_b.plot(n_fit, s_inf + a_coef / n_fit, "--", color=DOPANT_COLORS[dop], lw=1.1, alpha=0.75)
            ax_b.axhline(s_inf, color=DOPANT_COLORS[dop], lw=0.55, ls=":", alpha=0.45)
    add_reference_lines(ax_b)
    ax_b.set_xscale("log")
    ax_b.set_xticks(ns)
    ax_b.get_xaxis().set_minor_formatter(plt.NullFormatter())
    ax_b.minorticks_off()
    ax_b.set_xlabel(r"Supercell size $n$")
    ax_b.set_ylabel(r"$\mathcal{S}$ (meV/atom)")
    style_axes(ax_b)
    _legend_in(ax_b, loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=3)

    sdc = load_json("experiments/analysis/sdc/sdc_exp10_results.json")

    panel_label(ax_c, "c", nature=True)
    xpos = np.arange(len(dopants))
    width = 0.34
    seq_mev = [n4_decomposition(sdc, d)["sequential_meV"] for d in dopants]
    cpl_mev = [n4_decomposition(sdc, d)["coupled_meV"] for d in dopants]
    s_mev = [n4_decomposition(sdc, d)["synergy_meV"] for d in dopants]
    ax_c.bar(
        xpos - width / 2,
        seq_mev,
        width,
        label="additive prediction",
        color=NATURE_GRAY,
        alpha=0.45,
        edgecolor=INK,
        linewidth=0.6,
        zorder=2,
    )
    ax_c.bar(
        xpos + width / 2,
        cpl_mev,
        width,
        label="coupled corner",
        color=[DOPANT_COLORS[d] for d in dopants],
        alpha=0.88,
        edgecolor=INK,
        linewidth=0.6,
        zorder=3,
    )
    for i, (d, sm) in enumerate(zip(dopants, s_mev)):
        y0, y1 = seq_mev[i], cpl_mev[i]
        eta_pct = abs(sm) / abs(cpl_mev[i]) * 100 if cpl_mev[i] else 0.0
        ax_c.annotate(
            "",
            xy=(xpos[i] + width / 2, y1),
            xytext=(xpos[i] - width / 2, y0),
            arrowprops=dict(arrowstyle="<->", color=INK, lw=0.9, shrinkA=0, shrinkB=0),
            zorder=4,
        )
        ax_c.text(
            xpos[i],
            max(y0, y1) + 0.55,
            rf"$\mathcal{{S}}={sm:+.1f}$",
            ha="center",
            fontsize=6.5,
            color=DOPANT_COLORS[d],
            fontweight="bold",
        )
        ax_c.text(
            xpos[i],
            max(y0, y1) + 2.2,
            rf"$\eta={eta_pct:.0f}\%$",
            ha="center",
            fontsize=5.8,
            color=INK,
        )
    ax_c.set_xticks(xpos)
    ax_c.set_xticklabels(dopants)
    ax_c.set_ylabel(r"$\Delta E$ (meV/atom)")
    ax_c.axhline(0, color="#D8D8D8", lw=0.7)
    style_axes(ax_c)
    _legend_in(ax_c, loc="upper left", fontsize=6.5)
    panel_subtitle(ax_c, r"$n{=}4$, $+3$\%: additive vs.\ coupled", ha="right")

    panel_label(ax_d, "d", nature=True)
    s_all_abs = np.array([abs(r["synergy_S_meV_per_atom"]) for r in audit["synergy_table"]])
    med_s = float(np.median(s_all_abs))
    bins = np.linspace(0, max(s_all_abs) * 1.08, 9)
    ax_d.hist(
        s_all_abs,
        bins=bins,
        color=NATURE_BLUE,
        alpha=0.72,
        edgecolor=INK,
        linewidth=0.55,
        zorder=2,
    )
    ax_d.axvline(float(np.max(s_all_abs)), color=DOPANT_COLORS["P"], ls="--", lw=1.1,
                 label=f"max ({float(np.max(s_all_abs)):.1f})")
    ax_d.axvline(med_s, color=INK, ls=":", lw=1.0, label=f"median ({med_s:.1f})")
    ax_d.set_xlabel(r"$|\mathcal{S}|$ (meV/atom)")
    ax_d.set_ylabel("count")
    style_axes(ax_d)
    _legend_in(ax_d, loc="upper right", fontsize=6.2)
    panel_subtitle(ax_d, "15 periodic points @ $+3$%", ha="right")

    panel_label(ax_e, "e", nature=True)
    ax_e.fill_between([0, 1], [s_rig, s_rel], color=DOPANT_COLORS["P"], alpha=0.12, zorder=1)
    ax_e.plot([0, 1], [s_rig, s_rel], "-o", color=DOPANT_COLORS["P"], markersize=8,
              markerfacecolor="white", markeredgewidth=1.25, lw=1.7, zorder=3)
    add_reference_lines(ax_e)
    ax_e.set_xticks([0, 1])
    ax_e.set_xticklabels(["rigid\n(misfit + load)", "relaxed\n(stress release)"])
    ax_e.set_ylabel(r"$\mathcal{S}$ (meV/atom)")
    style_axes(ax_e)
    ax_e.annotate(
        "upper-bound\nprotocol",
        xy=(0, s_rig),
        xytext=(-0.18, s_rig + 4.5),
        fontsize=6.5,
        color=DOPANT_COLORS["P"],
        arrowprops=dict(arrowstyle="-|>", color=DOPANT_COLORS["P"], lw=0.85),
        ha="center",
    )
    panel_subtitle(ax_e, r"$n{=}1$ P @ $+3$\%", ha="right")
    return _save(fig, "figure_prb_2_synergy")


def build_fig3() -> tuple[Path, Path]:
    apply_nature_style()
    alpha_ref, _, _ = load_reference_pbed3_alpha_S()
    audit_mev = load_json("experiments/analysis/sdc/sdc_exp10_synergy_audit.json")
    qpaths, dpaths = _hirsh_paths(), _local_d_sigma_paths()
    dopants = ["B", "N", "P"]

    fig = plt.figure(figsize=(PRB_WIDTH_IN, 5.4), facecolor="white")
    gs = GridSpec(2, 2, figure=fig, hspace=0.34, wspace=0.28, left=0.09, right=0.97, top=0.94, bottom=0.11)
    ax_a, ax_b, ax_c, ax_d = [fig.add_subplot(gs[i, j]) for i in range(2) for j in range(2)]

    panel_label(ax_a, "a", nature=True)
    for d in dopants:
        xs, ys = qpaths[d]
        plot_trajectory(ax_a, xs, ys, DOPANT_COLORS[d], label=d, fill_mode="band")
    add_reference_lines(ax_a, vzero=True)
    strain_guide(ax_a)
    ax_a.set_xlabel(r"$\epsilon$ (%)")
    ax_a.set_ylabel(r"$q_{\mathrm{Hirsh}}$ ($e$)")
    style_axes(ax_a)
    _legend_in(ax_a, loc="upper right")

    panel_label(ax_b, "b", nature=True)
    lo, hi = np.inf, -np.inf
    for d in dopants:
        xs, dbar, sig = dpaths[d]
        plot_error_band(ax_b, xs, dbar, sig, DOPANT_COLORS[d], label=d)
        lo = min(lo, float(np.min(dbar - sig)))
        hi = max(hi, float(np.max(dbar + sig)))
    pad = 0.004 * (hi - lo + 1e-9)
    ax_b.set_ylim(lo - pad, hi + pad)
    add_reference_lines(ax_b, vzero=True)
    strain_guide(ax_b)
    ax_b.set_xlabel(r"$\epsilon$ (%)")
    ax_b.set_ylabel(r"$\bar{d}$ (Å)")
    style_axes(ax_b)
    _legend_in(ax_b, loc="best", fontsize=6.8)

    panel_label(ax_c, "c", nature=True)
    for d in dopants:
        xs, _, sig = dpaths[d]
        plot_trajectory(ax_c, xs, sig * 1e3, DOPANT_COLORS[d], label=d, fill_to=0)
    strain_guide(ax_c)
    ax_c.set_xlabel(r"$\epsilon$ (%)")
    ax_c.set_ylabel(r"$\sigma(\bar{d})$ (mÅ)")
    style_axes(ax_c)
    _legend_in(ax_c, loc="upper right", fontsize=6.8)

    panel_label(ax_d, "d", nature=True)
    abs_alpha = {d: abs(float(alpha_ref[d])) for d in dopants}
    abs_s4 = {d: abs(dict(synergy_rows(audit_mev, d))[4]) for d in dopants}
    abs_s1 = {d: abs(dict(synergy_rows(audit_mev, d))[1]) for d in dopants}
    amax, smax = max(abs_alpha.values()) * 1.15, max(abs_s4.values()) * 1.25
    s1_ref = max(abs_s1.values())
    ax_d.set_xlim(0, amax)
    ax_d.set_ylim(-smax * 0.08, smax)
    ax_d.axhspan(0, 8, xmin=0.42, xmax=1.0, color=DOPANT_FILLS["N"], alpha=0.45, zorder=0)
    ax_d.axhspan(12, smax, xmin=0.0, xmax=1.0, color=DOPANT_FILLS["P"], alpha=0.35, zorder=0)
    for d in dopants:
        scatter_dopant(ax_d, abs_alpha[d], abs_s4[d], d, size=80 + 340 * (abs_s1[d] / s1_ref))
    ax_d.set_xlabel(r"$|\alpha|$ (meV/%)")
    ax_d.set_ylabel(r"$|\mathcal{S}|_{n=4}$ (meV/atom)")
    style_axes(ax_d)
    ax_d.text(0.98, 0.04, r"cloud size $\propto|\mathcal{S}|_{n=1}$", transform=ax_d.transAxes,
              ha="right", va="bottom", fontsize=6.8, color=NATURE_GRAY)
    a_arr = np.array([abs_alpha[d] for d in dopants], dtype=float)
    s_arr = np.array([abs_s4[d] for d in dopants], dtype=float)
    r_pearson = float(np.corrcoef(a_arr, s_arr)[0, 1])
    rank_a = np.argsort(np.argsort(a_arr))
    rank_s = np.argsort(np.argsort(s_arr))
    r_spear = float(np.corrcoef(rank_a, rank_s)[0, 1])
    ax_d.text(
        0.03,
        0.97,
        f"Pearson r={r_pearson:+.2f}, R²={r_pearson**2:.2f}; Spearman ρ={r_spear:+.2f} (n=3)",
        transform=ax_d.transAxes,
        ha="left",
        va="top",
        fontsize=6.5,
        color=NATURE_GRAY,
        bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#DDDDDD", alpha=0.92),
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
        scatter_dopant(ax_a, dd[d], dq_frac[d], d, size=90 + 420 * (s_abs[d] / sref),
                       offset={"B": (14, -14), "N": (-18, 12), "P": (14, 12)}[d])
    ax_a.set_xlabel(r"$|\Delta\bar{d}|_{0\to+3\%}$ (mÅ)")
    ax_a.set_ylabel(r"$|\Delta q/q|_{0\to+3\%}$ (%)")
    style_axes(ax_a)

    panel_label(ax_b, "b", nature=True)
    ax_b.set_xlim(-2, max(dr.values()) * 1.22)
    ax_b.set_ylim(-max(s_abs.values()) * 0.1, max(s_abs.values()) * 1.28)
    ax_b.axvspan(20, 45, color=DOPANT_FILLS["P"], alpha=0.40, zorder=0)
    ax_b.axvline(20, color=DOPANT_COLORS["P"], ls="--", lw=0.95, alpha=0.75)
    for d in dopants:
        scatter_dopant(ax_b, dr[d], s_abs[d], d, size=130,
                       offset={"B": (14, -16), "N": (14, 14), "P": (-20, 0)}[d])
    ax_b.set_xlabel(r"$|\Delta r_{\mathrm{cov}}|$ (pm)")
    ax_b.set_ylabel(r"$|\mathcal{S}|_{n=4}$ (meV/atom)")
    style_axes(ax_b)

    panel_label(ax_c, "c", nature=True)
    for d in dopants:
        xs_q, ys_q = qpaths[d]
        xs_d, ys_d, _ = dpaths[d]
        q0, d0 = float(dict(zip(xs_q, ys_q))[0.0]), float(dict(zip(xs_d, ys_d))[0.0])
        ax_c.plot(xs_q, ys_q / q0, "-o", color=DOPANT_COLORS[d], markersize=4.8,
                  markerfacecolor="white", markeredgewidth=1.05, lw=1.35, label=rf"$q/q_0$ ({d})")
        ax_c.plot(xs_d, ys_d / d0, "--o", color=DOPANT_COLORS[d], markersize=4.2,
                  markerfacecolor="white", markeredgewidth=0.85, lw=1.1, alpha=0.72)
    ax_c.axhline(1.0, color="#D5D5D5", lw=0.7)
    strain_guide(ax_c)
    ax_c.set_xlabel(r"$\epsilon$ (%)")
    ax_c.set_ylabel("Normalized to $\\epsilon{=}0$")
    style_axes(ax_c)
    _legend_in(ax_c, fontsize=6.2, ncol=1)

    panel_label(ax_d, "d", nature=True)
    mfs = {d: 100.0 * float(mm[d]["mismatch_fraction"]) for d in dopants}
    s1s = {d: abs(float(mm[d]["S_meV_per_atom_n1"])) for d in dopants}
    ax_d.set_xlim(-2, max(mfs.values()) * 1.22)
    ax_d.set_ylim(-max(s1s.values()) * 0.1, max(s1s.values()) * 1.28)
    for d in dopants:
        scatter_dopant(ax_d, mfs[d], s1s[d], d, size=140,
                       offset={"B": (14, -14), "N": (14, 14), "P": (-20, 0)}[d])
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
