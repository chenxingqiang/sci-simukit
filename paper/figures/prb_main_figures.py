#!/usr/bin/env python3
"""Main-text figures 1-4 for the PRB manuscript.

All plotted numbers are read from the archived audit files (see ``_load_audit``)
or from the corner-energy table; nothing is fitted here except the linear
cluster-map slope in Fig. 1(d), which reproduces the tabulated alpha.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Rectangle
from PIL import Image, ImageDraw

FIG_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(FIG_DIR))

from _load_audit import (  # noqa: E402
    SIGMA_S_MEV,
    load_hirshfeld_strain_paths,
    load_json,
    load_local_structure_paths,
    load_local_structure_summary,
    load_periodic_relax_n1_P,
    load_reference_pbed3_alpha_S,
    parse_exp7_gaps,
    repo_root,
    synergy_rows,
)
from _pdos import gaussian_dos, parse_pdos  # noqa: E402
from prb_theme import (  # noqa: E402
    DOPANT,
    DOPANTS,
    HAIR,
    INK,
    MID,
    PRISTINE,
    ROSE_WASH,
    SIGN_CMAP,
    SOFT,
    WASH,
    WIDTH_IN,
    apply_theme,
    bare,
    bubble_area,
    dopant_key,
    floor_band,
    frame,
    halo,
    label,
    subtitle,
    tag,
    trace,
    zero_line,
)

OUT = FIG_DIR / "out"
HA_TO_MEV = 27211.386245988
CORE_N = (1, 2, 4)
REF_N = (6, 8)
NS = (1, 2, 4, 6, 8)
R_COV_C_PM = 77.0
MINUS = "\u2212"


def _fmt(v: float, nd: int = 1, plus: bool = False) -> str:
    s = f"{v:+.{nd}f}" if plus else f"{v:.{nd}f}"
    return s.replace("-", MINUS)


def _save(fig: plt.Figure, stem: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    pdf = OUT / f"{stem}.pdf"
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.04)
    fig.savefig(OUT / f"{stem}.png", bbox_inches="tight", pad_inches=0.04, dpi=300)
    plt.close(fig)
    return pdf


# --------------------------------------------------------------------------- data


def _corner_table() -> dict[tuple[int, str], dict[str, float]]:
    """Per (n, dopant): strain cost on the pristine and on the substituted lattice (meV/atom)."""
    rows: dict[tuple[int, str], dict[str, float]] = {}
    with open(FIG_DIR / "data" / "sdc_corner_energies.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            e00 = float(r["E_00_Ha_per_atom"])
            ee0 = float(r["E_eps0_Ha_per_atom"])
            e0d = float(r["E_0d_Ha_per_atom"])
            eed = float(r["E_epsd_Ha_per_atom"])
            rows[(int(r["n_molecules"]), r["dopant"])] = {
                "E00": 0.0,
                "Ee0": (ee0 - e00) * HA_TO_MEV,
                "E0d": (e0d - e00) * HA_TO_MEV,
                "Eed": (eed - e00) * HA_TO_MEV,
                "cost_pristine": (ee0 - e00) * HA_TO_MEV,
                "cost_doped": (eed - e0d) * HA_TO_MEV,
                "S": float(r["S_meV_per_atom"]),
            }
    return rows


def _systematic_offsets() -> dict[int, float]:
    audit = load_json("experiments/analysis/reference_consistency_audit.json")
    return {int(k): float(v["systematic_uncertainty_meV_per_atom"]) for k, v in audit["per_n"].items()}


def _pdos_path(dop: str, tag_: str) -> Path:
    return repo_root() / "dft_results/exp_7_electronic_structure/outputs" / f"elec_{tag_}_{dop}-k1-1.pdos"


def _pristine_cluster_dE() -> tuple[np.ndarray, np.ndarray, float, float]:
    """Pristine cluster-map energy vs vacuum-box label, meV per 240-atom tetramer cell."""
    ref = load_json("experiments/analysis/reference_placement_pbed3.json")
    e = {float(k): float(v) for k, v in ref["pristine"]["strain_energies_ha"].items()}
    xs = np.array(sorted(e))
    ys = np.array([(e[x] - e[0.0]) * HA_TO_MEV for x in xs])
    alpha, _, _, err = load_reference_pbed3_alpha_S()
    return xs, ys, float(alpha["pristine"]), float(err["pristine"])


def _hirshfeld() -> dict[str, tuple[np.ndarray, np.ndarray]]:
    h = load_hirshfeld_strain_paths()
    return {d: (np.array([p[0] for p in pts]), np.array([p[1] for p in pts])) for d, pts in h.items()}


def _local_paths() -> dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    raw = load_local_structure_paths()
    out = {}
    for d, rows in raw.items():
        rows = sorted(rows)
        out[d] = tuple(np.array([r[i] for r in rows]) for i in range(3))
    return out


def _structure_tiles() -> list[Image.Image]:
    root = FIG_DIR / "final_figures"
    names = ("pristine", "B_doped", "N_doped", "P_doped")
    tiles = []
    for nm in names:
        im = Image.open(root / f"C60_strain_+0.0_{nm}_synergy.png").convert("RGB")
        w, h = im.size
        for xy in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
            ImageDraw.floodfill(im, xy, (255, 255, 255), thresh=40)
        arr = np.asarray(im)
        mask = np.any(arr < 246, axis=2)
        ys, xs = np.where(mask)
        pad = 14
        box = (max(xs.min() - pad, 0), max(ys.min() - pad, 0), min(xs.max() + pad, w), min(ys.max() + pad, h))
        tiles.append(im.crop(box))
    return tiles


# ------------------------------------------------------------------------- Fig. 1


def build_fig1() -> Path:
    apply_theme()
    fig = plt.figure(figsize=(WIDTH_IN, 7.05))
    gs = GridSpec(3, 1, figure=fig, height_ratios=[1.28, 1.55, 2.25], hspace=0.56,
                  left=0.075, right=0.985, top=0.965, bottom=0.07)

    # (a) archived tetramer renders ------------------------------------------------
    local = load_local_structure_summary()
    tiles = _structure_tiles()
    names = [("pristine", PRISTINE, "reference cage", "D")] + [
        (d, DOPANT[d]["color"], rf"$\Delta r_{{\rm cov}}={_fmt(local[d]['radius_delta_pm'], 0, True)}$ pm", DOPANT[d]["marker"])
        for d in DOPANTS
    ]
    ga = gs[0].subgridspec(1, 4, wspace=0.06)
    for i, (im, (nm, col, sub, mk)) in enumerate(zip(tiles, names)):
        ax = fig.add_subplot(ga[i])
        ax.imshow(np.asarray(im), interpolation="lanczos")
        bare(ax)
        ax.set_aspect("equal")
        ax.annotate("", xy=(0.04, -0.035), xycoords="axes fraction", xytext=(0.96, -0.035),
                    textcoords="axes fraction", arrowprops=dict(arrowstyle="-", color=col, lw=1.6, shrinkA=0, shrinkB=0))
        ax.annotate(nm, xy=(0.5, -0.115), xycoords="axes fraction", ha="center", va="top",
                    fontsize=8.0, fontweight="bold", color=col)
        ax.annotate(sub, xy=(0.5, -0.27), xycoords="axes fraction", ha="center", va="top", fontsize=6.4, color=MID)
        if i == 0:
            tag(ax, "a", dx=-6, dy=2)

    # (b) pi-DOS ridgelines ---------------------------------------------------------
    gb = gs[1].subgridspec(1, 4, wspace=0.07)
    grid = np.linspace(-2.45, 2.45, 700)
    specs = (("neg5p0", MINUS + "5", 0.0), ("pos0p0", "0", 1.12), ("pos5p0", "+5", 2.24))
    systems = [("pristine", PRISTINE)] + [(d, DOPANT[d]["color"]) for d in DOPANTS]
    first_ax = None
    for i, (sysname, col) in enumerate(systems):
        ax = fig.add_subplot(gb[i], sharey=first_ax) if first_ax is not None else fig.add_subplot(gb[i])
        first_ax = first_ax or ax
        for tg, _lab, off in specs:
            p = _pdos_path(sysname, tg)
            if not p.is_file():
                continue
            s = parse_pdos(p)
            dos = gaussian_dos(s.energy_ev, s.pi_weight, grid, sigma_ev=0.065)
            dos = dos / (dos.max() + 1e-12) * 0.98
            ax.fill_between(grid, off, off + dos, color=col, alpha=0.20, lw=0, zorder=2)
            ax.plot(grid, off + dos, color=col, lw=1.1, zorder=3)
            ax.plot(grid, np.full_like(grid, off), color=col, lw=0.5, alpha=0.55, zorder=2)
        ax.axvline(0.0, color=INK, lw=0.6, ls=(0, (2.4, 2.0)), zorder=1)
        ax.set_xlim(-2.45, 2.45)
        ax.set_ylim(-0.12, 3.35)
        ax.set_xticks([-2, -1, 0, 1, 2])
        ax.set_xticklabels([MINUS + "2", MINUS + "1", "0", "1", "2"])
        frame(ax, minor=False)
        ax.annotate(sysname, xy=(0.5, 1.0), xycoords="axes fraction", xytext=(0, 3.5), textcoords="offset points",
                    ha="center", va="bottom", fontsize=7.6, fontweight="bold", color=col)
        if i == 0:
            ax.set_yticks([off + 0.0 for _, _, off in specs])
            ax.set_yticklabels([lab for _, lab, _ in specs])
            ax.set_ylabel(r"$\epsilon$ (%)  [$\pi$-DOS, each normalised]")
            tag(ax, "b", dx=-26, dy=14)
        else:
            ax.tick_params(labelleft=False)
        if i == 0:
            ax.annotate(r"$E_{\rm F}$", xy=(0.0, 3.35), xytext=(3, -1), textcoords="offset points", fontsize=6.2,
                        color=MID, va="top", ha="left")
        ax.set_xlabel(r"$E-E_{\rm F}$ (eV)")

    # (c) frontier gap, broken axis ---------------------------------------------------
    gc_all = gs[2].subgridspec(1, 2, width_ratios=[1.12, 1.0], wspace=0.34)
    gc = gc_all[0].subgridspec(2, 1, height_ratios=[1.0, 1.15], hspace=0.09)
    ax_hi = fig.add_subplot(gc[0])
    ax_lo = fig.add_subplot(gc[1], sharex=ax_hi)
    gaps = parse_exp7_gaps()
    pr = sorted((p.strain_pct, p.gap_ev) for p in gaps if p.dopant == "pristine" and p.converged)
    px, py = zip(*pr)
    ax_hi.plot(px, py, "-", color=PRISTINE, lw=1.4, zorder=2)
    ax_hi.plot(px, py, "D", ms=4.6, mfc=PRISTINE, mec="white", mew=0.7, zorder=3)
    for x, y in pr:
        label(ax_hi, x, y, f"{y:.2f}", color=PRISTINE, dy=7, ha="center", va="bottom", fs=6.2)
    ax_hi.set_ylim(0.75, 1.85)
    ax_hi.set_yticks([1.0, 1.5])
    ax_hi.set_ylabel("")
    label(ax_hi, 5, 1.1, "pristine", color=PRISTINE, dx=6, fs=6.8, bold=True)
    ax_lo.axhspan(-0.2, 0.2, color=WASH, lw=0, zorder=0)
    ax_lo.axhline(0.0, color=HAIR, lw=0.7, zorder=1)
    ends = {}
    for d in DOPANTS:
        pts = sorted((p.strain_pct, p.gap_ev) for p in gaps if p.dopant == d and p.converged)
        x, y = map(np.array, zip(*pts))
        trace(ax_lo, x, y, d, lw=1.35)
        ends[d] = (x[-1], y[-1])
    for d, (x, y) in ends.items():
        label(ax_lo, x, y, d, color=DOPANT[d]["color"], dx=6, fs=6.8, bold=True)
    ax_lo.set_ylim(-0.27, 0.30)
    ax_lo.set_yticks([-0.2, 0.0, 0.2])
    ax_lo.set_yticklabels([MINUS + "0.2", "0", "0.2"])
    ax_lo.set_xlim(-6.4, 7.6)
    ax_lo.set_xticks([-5, 0, 5])
    ax_lo.set_xticklabels([MINUS + "5", "0", "+5"])
    ax_lo.set_xlabel(r"$\epsilon$ (%)")
    label(ax_lo, -6.2, 0.2, r"$|E_{\rm H\!-\!L}|<0.2$ eV", color=SOFT, fs=5.8, dy=-1, va="top", halo_on=False)
    frame(ax_hi, minor=False)
    frame(ax_lo, minor=False)
    ax_hi.spines["bottom"].set_visible(False)
    ax_lo.spines["top"].set_visible(False)
    ax_hi.tick_params(labelbottom=False, bottom=False)
    ax_lo.tick_params(top=False)
    for ax_, y0 in ((ax_hi, 0.0), (ax_lo, 1.0)):
        kw = dict(color=INK, lw=0.8, clip_on=False, transform=ax_.transAxes)
        ax_.plot((-0.02, 0.02), (y0 - 0.035, y0 + 0.035), **kw)
        ax_.plot((0.98, 1.02), (y0 - 0.035, y0 + 0.035), **kw)
    ax_hi.annotate(r"$E_{\rm H\!-\!L}$ (eV)", xy=(-0.20, -0.04), xycoords="axes fraction", rotation=90,
                   ha="center", va="center", fontsize=7.4)
    tag(ax_hi, "c", dx=-26, dy=6)

    # (d) pristine cluster map ----------------------------------------------------------
    gd = gc_all[1].subgridspec(2, 1, height_ratios=[3.0, 1.15], hspace=0.10)
    ax_e = fig.add_subplot(gd[0])
    ax_r = fig.add_subplot(gd[1], sharex=ax_e)
    xs, ys, alpha_p, err_p = _pristine_cluster_dE()
    coef = np.polyfit(xs, ys, 1)
    xf = np.linspace(-5.8, 5.8, 50)
    ax_e.plot(xf, coef[0] * xf + coef[1], "-", color=SOFT, lw=1.0, zorder=1)
    ax_e.plot(xs, ys, "D", ms=5.0, mfc=PRISTINE, mec="white", mew=0.7, zorder=3, color=PRISTINE)
    zero_line(ax_e)
    ax_e.set_ylabel(r"$\Delta E_{\rm pris}$ (meV per cell)")
    ax_e.tick_params(labelbottom=False)
    ax_e.text(0.04, 0.95, rf"$\alpha_{{\rm p}}={alpha_p:.2f}\pm{err_p:.2f}$ meV/%", transform=ax_e.transAxes,
              ha="left", va="top", fontsize=6.8, color=INK)
    resid = ys - (coef[0] * xs + coef[1])
    ax_r.axhline(0.0, color=SOFT, lw=0.8)
    ax_r.vlines(xs, 0.0, resid, color=PRISTINE, lw=1.0)
    ax_r.plot(xs, resid, "o", ms=3.4, mfc="white", mec=PRISTINE, mew=1.0, zorder=3)
    rm = max(abs(resid).max() * 1.35, 0.05)
    ax_r.set_ylim(-rm, rm)
    ax_r.set_ylabel("resid.", fontsize=6.4)
    ax_r.set_xlim(-6.0, 6.0)
    ax_r.set_xticks([-5, 0, 5])
    ax_r.set_xticklabels([MINUS + "5", "0", "+5"])
    ax_r.set_xlabel(r"$\epsilon$ (%)")
    frame(ax_e)
    frame(ax_r, minor=False)
    tag(ax_e, "d", dx=-30, dy=6)
    return _save(fig, "figure_prb_1_electronic")


# ------------------------------------------------------------------------- Fig. 2


def _shade_reference_columns(ax, *, label_y: float | None = None) -> None:
    ax.axvspan(2.5, 4.5, color=ROSE_WASH, lw=0, zorder=0)
    ax.axvline(2.5, color=HAIR, lw=0.7, zorder=0)
    if label_y is not None:
        ax.text(3.5, label_y, "350 Ry reference", ha="center", va="top", fontsize=6.2, color="#A66A66", zorder=2)
        ax.text(1.0, label_y, "400 Ry matched core", ha="center", va="top", fontsize=6.2, color=MID, zorder=2)


def build_fig2() -> Path:
    apply_theme()
    audit = load_json("experiments/analysis/sdc/sdc_exp10_synergy_audit.json")
    corners = _corner_table()
    sys_off = _systematic_offsets()
    s_rig, s_rel = load_periodic_relax_n1_P()
    relax = load_json("experiments/analysis/periodic_relax_validation_n1_P.json")
    idx = {n: i for i, n in enumerate(NS)}

    fig = plt.figure(figsize=(WIDTH_IN, 6.9))
    outer = GridSpec(2, 1, figure=fig, height_ratios=[1.52, 1.0], hspace=0.32,
                     left=0.075, right=0.985, top=0.955, bottom=0.07)
    top = outer[0].subgridspec(1, 2, width_ratios=[1.45, 1.0], wspace=0.30)
    left = top[0].subgridspec(2, 1, height_ratios=[3.3, 1.15], hspace=0.07)
    bot = outer[1].subgridspec(1, 3, width_ratios=[0.92, 1.18, 0.95], wspace=0.34)

    # (a) S(n) ---------------------------------------------------------------------
    ax = fig.add_subplot(left[0])
    ax_h = fig.add_subplot(left[1], sharex=ax)
    _shade_reference_columns(ax, label_y=17.2)
    floor_band(ax, SIGMA_S_MEV)
    zero_line(ax)
    for d in DOPANTS:
        rows = synergy_rows(audit, d)
        n = np.array([r[0] for r in rows])
        s = np.array([r[1] for r in rows])
        x = np.array([idx[int(k)] for k in n], dtype=float)
        err = np.array([SIGMA_S_MEV + sys_off.get(int(k), 0.0) for k in n])
        ax.errorbar(x, s, yerr=err, fmt="none", ecolor=DOPANT[d]["color"], elinewidth=0.7, capsize=1.9,
                    capthick=0.6, alpha=0.75, zorder=3)
        core = np.array([int(k) in CORE_N for k in n])
        trace(ax, x[core], s[core], d, lw=1.6, ms=DOPANT[d]["ms"] + 1.2)
        ax.plot(x[~core], s[~core], linestyle="None", marker=DOPANT[d]["marker"], ms=DOPANT[d]["ms"] + 1.2,
                mfc="white", mec=DOPANT[d]["color"], mew=1.3, zorder=5)
    pr = dict(synergy_rows(audit, "P"))
    label(ax, 0, pr[1], _fmt(pr[1]), color=DOPANT["P"]["color"], dx=-4, dy=-10, ha="center", va="top", bold=True, fs=6.6)
    label(ax, 2, pr[4], _fmt(pr[4]), color=DOPANT["P"]["color"], dx=0, dy=-11, ha="center", va="top", bold=True, fs=6.6)
    ax.set_xlim(-0.55, 4.55)
    ax.set_ylim(-42, 18.5)
    ax.set_ylabel(r"$\mathcal{S}$ (meV/atom)")
    ax.tick_params(labelbottom=False)
    frame(ax, minor=False)
    ax.set_yticks(np.arange(-40, 20, 10))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(5))
    dopant_key(ax, loc="lower center", anchor=(0.5, 1.012), ncol=5, extra=(
        Line2D([0], [0], color=INK, marker="o", mfc=INK, mec="white", lw=0, ms=5.0, label="400 Ry"),
        Line2D([0], [0], color=INK, marker="o", mfc="white", mec=INK, mew=1.1, lw=0, ms=5.0, label="350 Ry"),
    ))
    tag(ax, "a", dx=-28, dy=14)

    # heat strip aligned with (a)
    mat = np.array([[dict(synergy_rows(audit, d))[n] for n in NS] for d in DOPANTS])
    norm = TwoSlopeNorm(vmin=-33, vcenter=0, vmax=33)
    ax_h.pcolormesh(np.arange(-0.5, 5.0, 1.0), np.arange(-0.5, 3.0, 1.0), mat, cmap=SIGN_CMAP, norm=norm,
                    edgecolors="white", linewidth=1.4)
    for r, d in enumerate(DOPANTS):
        for c, n in enumerate(NS):
            v = mat[r, c]
            if abs(v) <= SIGMA_S_MEV:
                ax_h.add_patch(Rectangle((c - 0.5, r - 0.5), 1, 1, fill=False, hatch="////", ec=SOFT, lw=0))
            ax_h.text(c, r, _fmt(v), ha="center", va="center", fontsize=6.4,
                      color="white" if abs(v) > 17 else INK, fontweight="bold" if abs(v) > 17 else "normal")
    ax_h.set_ylim(2.5, -0.5)
    ax_h.set_yticks(range(3))
    ax_h.set_yticklabels(DOPANTS)
    for t, d in zip(ax_h.get_yticklabels(), DOPANTS):
        t.set_color(DOPANT[d]["color"])
        t.set_fontweight("bold")
    ax_h.set_xticks(range(5))
    ax_h.set_xticklabels([str(n) for n in NS])
    ax_h.set_xlabel(r"supercell size $n$  ($n\times$C$_{60}$; categorical axis)")
    ax_h.tick_params(length=0, top=False, right=False)
    for sp in ax_h.spines.values():
        sp.set_visible(False)

    # (b) strain cost on pristine vs substituted lattice ---------------------------------
    axb = fig.add_subplot(top[1])
    _shade_reference_columns(axb)
    zero_line(axb)
    xs = np.arange(len(NS), dtype=float)
    pc = np.array([corners[(n, "P")]["cost_pristine"] for n in NS])
    pe_ = np.array([sys_off.get(n, 0.0) for n in NS])
    for d in DOPANTS:
        dc = np.array([corners[(n, d)]["cost_doped"] for n in NS])
        axb.fill_between(xs, pc, dc, color=DOPANT[d]["color"], alpha=0.07, lw=0, zorder=1)
        trace(axb, xs, dc, d, lw=1.35)
        label(axb, xs[-1], dc[-1], d, color=DOPANT[d]["color"], dx=7, fs=6.8, bold=True)
    axb.errorbar(xs, pc, yerr=pe_, fmt="none", ecolor=PRISTINE, elinewidth=0.8, capsize=2.0, capthick=0.7, zorder=3)
    axb.plot(xs, pc, "-", color=PRISTINE, lw=1.5, zorder=3)
    axb.plot(xs, pc, "D", ms=4.4, mfc=PRISTINE, mec="white", mew=0.7, zorder=4)
    label(axb, xs[-1], pc[-1], "pristine", color=PRISTINE, dx=7, dy=7, fs=6.6, bold=True)
    c4 = corners[(4, "P")]
    axb.annotate("", xy=(2.0, c4["cost_doped"]), xytext=(2.0, c4["cost_pristine"]),
                 arrowprops=dict(arrowstyle="<->", color=INK, lw=0.9, shrinkA=0, shrinkB=0, mutation_scale=7), zorder=6)
    label(axb, 2.0, 0.5 * (c4["cost_doped"] + c4["cost_pristine"]), r"$\mathcal{S}$", dx=-6, ha="right", fs=8.0)
    axb.set_xlim(-0.55, 5.35)
    axb.set_ylim(-36, 16.5)
    axb.set_xticks(range(5))
    axb.set_xticklabels([str(n) for n in NS])
    axb.set_xlabel(r"supercell size $n$")
    axb.set_ylabel(r"strain cost $\Delta E(+3\%)$ (meV/atom)")
    frame(axb, minor=False)
    axb.yaxis.set_minor_locator(plt.MultipleLocator(5))
    tag(axb, "b", dx=-30, dy=14)
    subtitle(axb, "lattice responding to +3%", dx=10)

    # (c) rigid vs relaxed -------------------------------------------------------------
    axc = fig.add_subplot(bot[0])
    e = relax["S_rigid"]["energies_ha"]
    er = relax["S_relaxed"]["energies_ha"]
    natoms = float(relax["n_atoms"])

    def cost(en, a, b):
        return (en[b] - en[a]) * HA_TO_MEV / natoms

    state = {
        0: (cost(e, "pristine_eps0", "pristine_eps3"), cost(e, "P_eps0", "P_eps3")),
        1: (cost(er, "pristine_eps0", "pristine_eps3"), cost(er, "P_eps0", "P_eps3")),
    }
    for x, (cp, cd) in state.items():
        axc.add_patch(Rectangle((x - 0.30, cp - SIGMA_S_MEV), 0.60, 2 * SIGMA_S_MEV, color=WASH, lw=0, zorder=0))
        axc.plot([x, x], [cp, cd], "-", color=INK, lw=1.0, zorder=2)
    axc.plot([0, 1], [state[0][0], state[1][0]], "--", color=PRISTINE, lw=0.9, zorder=1)
    axc.plot([0, 1], [state[0][1], state[1][1]], "-", color=DOPANT["P"]["color"], lw=1.9, zorder=2)
    for x, (cp, cd) in state.items():
        axc.plot(x, cp, "D", ms=6.0, mfc=PRISTINE, mec="white", mew=0.8, zorder=4)
        axc.plot(x, cd, "^", ms=7.2, mfc=DOPANT["P"]["color"], mec="white", mew=0.8, zorder=5)
    label(axc, 0, 0.5 * sum(state[0]), rf"$\mathcal{{S}}={_fmt(s_rig)}$", dx=8, dy=12, fs=6.8, bold=True)
    label(axc, 1, state[1][1], r"$|\mathcal{S}|<10^{-3}$", dx=-8, dy=-12, ha="right", fs=6.6, bold=True)
    label(axc, 0, state[0][0], "pristine", color=PRISTINE, dx=8, dy=7, fs=6.4, va="bottom")
    label(axc, 0, state[0][1], "P", color=DOPANT["P"]["color"], dx=-9, ha="right", fs=7.0, bold=True)
    axc.set_xlim(-0.55, 1.55)
    axc.set_ylim(-36, 16.5)
    axc.set_xticks([0, 1])
    axc.set_xticklabels(["rigid\n(fixed coord.)", "relaxed\n(fixed cell)"])
    axc.set_ylabel(r"strain cost $\Delta E(+3\%)$ (meV/atom)")
    zero_line(axc)
    frame(axc, minor=False)
    axc.yaxis.set_minor_locator(plt.MultipleLocator(5))
    tag(axc, "c", dx=-28, dy=14)
    subtitle(axc, r"periodic $n{=}1$ P", dx=10)
    axc.text(1.5, -34.3, r"band: $\pm2$ meV/atom", ha="right", va="bottom", fontsize=5.8, color=SOFT)

    # (d) four-corner definition with the n=4 P corner energies -----------------------------
    axd = fig.add_subplot(bot[1])
    axd.set_xlim(0, 10)
    axd.set_ylim(0, 10)
    axd.axis("off")
    c = corners[(4, "P")]
    x0, x1, y0, y1 = 1.9, 7.0, 1.7, 7.1
    pcol = DOPANT["P"]["color"]

    def edge(p, q, color, lw=1.5):
        axd.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=8, color=color, lw=lw,
                                      shrinkA=5.5, shrinkB=5.5, zorder=2))

    edge((x0, y0), (x1, y0), PRISTINE)
    edge((x0, y1), (x1, y1), pcol)
    edge((x0, y0), (x0, y1), MID)
    edge((x1, y0), (x1, y1), MID)
    for (x, y), val, col, ha, dx, dy, name in (
        ((x0, y0), c["E00"], PRISTINE, "right", -7, -9, r"$E(0,0)$"),
        ((x1, y0), c["Ee0"], PRISTINE, "left", 7, -9, r"$E(\epsilon,0)$"),
        ((x0, y1), c["E0d"], pcol, "right", -7, 9, r"$E(0,\delta)$"),
        ((x1, y1), c["Eed"], pcol, "left", 7, 9, r"$E(\epsilon,\delta)$"),
    ):
        axd.plot(x, y, "o", ms=6.2, mfc=col, mec="white", mew=0.9, zorder=4)
        axd.annotate(name + "\n" + _fmt(val, 1, True if val else False).replace("+0.0", "0"), xy=(x, y),
                     xytext=(dx, dy), textcoords="offset points", ha=ha, va="center", fontsize=6.6,
                     linespacing=1.15, color=INK, zorder=5)
    axd.text(0.5 * (x0 + x1), y0 - 0.55, f"strain, pristine: {_fmt(c['cost_pristine'], 2, True)}", ha="center",
             va="top", fontsize=6.2, color=PRISTINE, fontweight="bold")
    axd.text(0.5 * (x0 + x1), y1 + 0.5, f"strain, substituted: {_fmt(c['cost_doped'], 2, True)}", ha="center",
             va="bottom", fontsize=6.2, color=pcol, fontweight="bold")
    axd.text(0.5 * (x0 + x1), 0.5 * (y0 + y1), rf"$\mathcal{{S}}={_fmt(c['S'])}$" + "\nmeV/atom", ha="center",
             va="center", fontsize=8.0, color=INK, linespacing=1.25)
    axd.text(0.5, 9.9, r"$\mathcal{S}_\delta(\epsilon)=E_{\rm cpl}-E_{\rm add}$", ha="left", va="top", fontsize=7.0)
    axd.text(0.5, 0.15, r"$\epsilon=+3\%$,  P,  $n{=}4$;  meV/atom rel. to $E(0,0)$", ha="left", va="bottom",
             fontsize=5.8, color=MID)
    axd.annotate("", xy=(0.15, y1), xytext=(0.15, y0), arrowprops=dict(arrowstyle="->", color=SOFT, lw=0.8))
    axd.text(0.0, 0.5 * (y0 + y1), "substitution", rotation=90, ha="center", va="center", fontsize=6.2, color=SOFT)
    tag(axd, "d", dx=-4, dy=4)

    # (e) bilinear coupling cartoon -----------------------------------------------------
    axe = fig.add_subplot(bot[2])
    eps = np.linspace(0, 3.0, 50)
    s_p, cx = 0.55, -1.10
    add = s_p * eps
    cpl = (s_p + cx) * eps
    axe.fill_between(eps, add, cpl, color=pcol, alpha=0.12, lw=0)
    axe.plot(eps, add, "--", color=PRISTINE, lw=1.4, zorder=3)
    axe.plot(eps, cpl, "-", color=pcol, lw=2.0, zorder=3)
    axe.annotate("", xy=(2.45, (s_p + cx) * 2.45), xytext=(2.45, s_p * 2.45),
                 arrowprops=dict(arrowstyle="<->", color=INK, lw=0.9, shrinkA=0, shrinkB=0, mutation_scale=7))
    label(axe, 2.45, 0.5 * (s_p + s_p + cx) * 2.45, r"$c\,\epsilon\,x$", dx=-6, ha="right", fs=7.4)
    label(axe, 3.0, s_p * 3.0, "additive", color=PRISTINE, dx=-3, dy=8, ha="right", fs=6.6, bold=True, va="bottom")
    label(axe, 3.0, (s_p + cx) * 3.0, "coupled", color=pcol, dx=-3, dy=-8, ha="right", fs=6.6, bold=True, va="top")
    axe.set_xlim(0, 3.05)
    axe.set_ylim(-2.1, 2.1)
    axe.set_xticks([])
    axe.set_yticks([])
    axe.set_xlabel(r"strain $\epsilon$")
    axe.set_ylabel(r"$E(\epsilon,\delta)-E(0,\delta)$  (arb.)")
    zero_line(axe)
    frame(axe, minor=False)
    tag(axe, "e", dx=-8, dy=14)
    subtitle(axe, "schematic, fixed species", dx=8)
    return _save(fig, "figure_prb_2_synergy")


# ------------------------------------------------------------------------- Fig. 3


def _strain_axis(ax) -> None:
    ax.axvline(3.0, color=DOPANT["P"]["color"], lw=0.8, ls=(0, (3.5, 2.8)), alpha=0.55, zorder=0)
    ax.set_xlim(-6.2, 7.6)
    ax.set_xticks([-5, 0, 5])
    ax.set_xticklabels([MINUS + "5", "0", "+5"])
    ax.set_xlabel(r"$\epsilon$ (%)")


def build_fig3() -> Path:
    apply_theme()
    audit = load_json("experiments/analysis/sdc/sdc_exp10_synergy_audit.json")
    alpha, _, _, alpha_err = load_reference_pbed3_alpha_S()
    q = _hirshfeld()
    loc = _local_paths()
    s4 = {d: abs(dict(synergy_rows(audit, d))[4]) for d in DOPANTS}
    s1 = {d: abs(dict(synergy_rows(audit, d))[1]) for d in DOPANTS}

    fig = plt.figure(figsize=(WIDTH_IN, 6.2))
    gs = GridSpec(2, 1, figure=fig, height_ratios=[1.0, 1.28], hspace=0.50,
                  left=0.08, right=0.985, top=0.925, bottom=0.075)
    top = gs[0].subgridspec(1, 3, wspace=0.42)
    bot = gs[1].subgridspec(1, 2, width_ratios=[1.28, 1.0], wspace=0.34)
    fig.legend(handles=[
        Line2D([0], [0], color=DOPANT[d]["color"], marker=DOPANT[d]["marker"], ms=DOPANT[d]["ms"], mfc=DOPANT[d]["color"],
               mec="white", mew=0.6, lw=1.4, label=d) for d in DOPANTS
    ], loc="upper center", bbox_to_anchor=(0.54, 0.995), ncol=3, fontsize=7.4, handlelength=1.8, columnspacing=1.6)

    ax = fig.add_subplot(top[0])
    zero_line(ax)
    for d in DOPANTS:
        trace(ax, *q[d], d)
    _strain_axis(ax)
    ax.set_ylabel(r"Hirshfeld $q$ at dopant ($e$)")
    frame(ax)
    tag(ax, "a", dx=-26, dy=6)
    subtitle(ax, "periodic $n{=}1$", dx=8)

    ax = fig.add_subplot(top[1])
    zero_line(ax)
    for d in DOPANTS:
        x, dbar, _ = loc[d]
        y = (dbar - dbar[list(x).index(0.0)]) * 1e3
        trace(ax, x, y, d)
    _strain_axis(ax)
    ax.set_ylabel(r"$\bar d(\epsilon)-\bar d(0)$" + " (m\u00c5)")
    frame(ax)
    tag(ax, "b", dx=-26, dy=6)
    subtitle(ax, "cluster map", dx=8)

    ax = fig.add_subplot(top[2])
    for d in DOPANTS:
        x, _, sig = loc[d]
        trace(ax, x, sig * 1e3, d)
    _strain_axis(ax)
    ax.set_ylabel(r"$\sigma(\bar d)$" + " (m\u00c5)")
    ax.set_ylim(bottom=0)
    frame(ax)
    tag(ax, "c", dx=-26, dy=6)
    subtitle(ax, "cluster map", dx=8)

    # (d) alpha vs |S| bubbles -------------------------------------------------------------
    ax = fig.add_subplot(bot[0])
    a = {d: float(alpha[d]) for d in DOPANTS}
    e = {d: float(alpha_err.get(d, 0.0)) for d in DOPANTS}
    lo = min(a[d] - e[d] for d in DOPANTS)
    hi = max(a[d] + e[d] for d in DOPANTS)
    pad = 0.07 * (hi - lo)
    ax.set_xlim(lo - pad, hi + pad)
    ax.set_ylim(-1.5, 30.5)
    ax.axhspan(0, SIGMA_S_MEV, color=WASH, lw=0, zorder=0)
    ax.axvline(0, color=HAIR, lw=0.7, zorder=1)
    vmax = max(s1.values())
    for d in DOPANTS:
        ax.errorbar(a[d], s4[d], xerr=e[d], yerr=SIGMA_S_MEV, fmt="none", ecolor=DOPANT[d]["color"],
                    elinewidth=0.8, capsize=2.2, capthick=0.7, alpha=0.5, zorder=2)
        ax.scatter([a[d]], [s4[d]], s=bubble_area(s1[d], vmax), marker="o", color=DOPANT[d]["color"], alpha=0.88,
                   edgecolor="white", linewidth=0.9, zorder=4)
    off = {"B": (0, 15), "N": (0, 14), "P": (0, 17)}
    for d in DOPANTS:
        label(ax, a[d], s4[d], d, color=DOPANT[d]["color"], dx=off[d][0], dy=off[d][1], ha="center", fs=7.4, bold=True)
    ax.set_xlabel(r"cluster-map $\alpha$ (meV/%)")
    ax.set_ylabel(r"$|\mathcal{S}|_{n=4}$ (meV/atom)")
    frame(ax)
    # bubble key in axes coordinates
    ax.text(0.985, 0.455, r"area $\propto|\mathcal{S}|_{n=1}$", transform=ax.transAxes, ha="right", va="bottom",
            fontsize=6.2, color=MID)
    for xk, v in ((0.665, 2.0), (0.795, 10.0), (0.925, 30.0)):
        ax.scatter([xk], [0.33], s=bubble_area(v, vmax), transform=ax.transAxes, marker="o", color=SOFT, alpha=0.6,
                   edgecolor="white", linewidth=0.6, zorder=5, clip_on=False)
        ax.text(xk, 0.215, f"{v:g}", transform=ax.transAxes, ha="center", va="top", fontsize=6.0, color=MID)
    tag(ax, "d", dx=-30, dy=6)

    # (e) rank slope chart -----------------------------------------------------------------
    ax = fig.add_subplot(bot[1])
    cols = [(r"$|\alpha|$", {d: abs(a[d]) for d in DOPANTS}, "{:.0f}"),
            (r"$|\mathcal{S}|_{n=4}$", s4, "{:.1f}"),
            (r"$|\mathcal{S}|_{n=1}$", s1, "{:.1f}")]
    ranks = []
    for _, vals, _f in cols:
        order = sorted(DOPANTS, key=lambda d: -vals[d])
        ranks.append({d: order.index(d) + 1 for d in DOPANTS})
    for x in range(3):
        ax.axvline(x, color=HAIR, lw=0.8, zorder=0)
    for d in DOPANTS:
        ys = [r[d] for r in ranks]
        ax.plot([0, 1, 2], ys, "-", color=DOPANT[d]["color"], lw=2.0, alpha=0.9, zorder=2)
        ax.plot([0, 1, 2], ys, linestyle="None", marker=DOPANT[d]["marker"], ms=DOPANT[d]["ms"] + 2.2,
                mfc=DOPANT[d]["color"], mec="white", mew=0.9, zorder=4)
        for x, (_, vals, fmt) in enumerate(cols):
            label(ax, x, ys[x], fmt.format(vals[d]), color=DOPANT[d]["color"], dx=0, dy=-11 if d != "N" else 11,
                  ha="center", fs=6.0, va="center")
    ax.set_xlim(-0.35, 2.35)
    ax.set_ylim(3.55, 0.45)
    ax.set_yticks([1, 2, 3])
    ax.set_yticklabels(["1st", "2nd", "3rd"])
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels([c[0] for c in cols], fontsize=7.2)
    ax.xaxis.tick_top()
    ax.tick_params(length=0, top=False, right=False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_ylabel("rank among B, N, P", labelpad=1)
    tag(ax, "e", dx=-30, dy=18)
    return _save(fig, "figure_prb_3_decoupling")


# ------------------------------------------------------------------------- Fig. 4


def build_fig4() -> Path:
    apply_theme()
    audit = load_json("experiments/analysis/sdc/sdc_exp10_synergy_audit.json")
    local = load_local_structure_summary()
    q = _hirshfeld()
    loc = _local_paths()
    s4 = {d: abs(dict(synergy_rows(audit, d))[4]) for d in DOPANTS}
    s1 = {d: abs(dict(synergy_rows(audit, d))[1]) for d in DOPANTS}
    dd = {d: abs(local[d]["delta_d_eps0_to_eps3_ang"]) * 1e3 for d in DOPANTS}
    dq = {}
    for d in DOPANTS:
        m = dict(zip(q[d][0].tolist(), q[d][1].tolist()))
        dq[d] = 100.0 * abs(m[3.0] - m[0.0]) / abs(m[0.0])
    dr = {d: abs(float(local[d]["radius_delta_pm"])) for d in DOPANTS}

    fig = plt.figure(figsize=(WIDTH_IN, 5.5))
    gs = GridSpec(2, 1, figure=fig, height_ratios=[1.0, 0.92], hspace=0.62,
                  left=0.08, right=0.985, top=0.945, bottom=0.085)
    top = gs[0].subgridspec(1, 3, wspace=0.42)
    bot = gs[1].subgridspec(1, 1)

    # (a) response plane -------------------------------------------------------------------
    ax = fig.add_subplot(top[0])
    vmax = max(s4.values())
    ax.set_xlim(-1.2, 11.8)
    ax.set_ylim(0, 23.5)
    for d in DOPANTS:
        ax.scatter([dd[d]], [dq[d]], s=bubble_area(s4[d], vmax, full=460), color=DOPANT[d]["color"], alpha=0.88,
                   edgecolor="white", linewidth=0.9, zorder=4)
    offs = {"B": (0, 17), "N": (0, 17), "P": (0, 17)}
    for d in DOPANTS:
        label(ax, dd[d], dq[d], d, color=DOPANT[d]["color"], dx=offs[d][0], dy=offs[d][1], ha="center", fs=7.4, bold=True)
    ax.set_xlabel(r"$|\Delta\bar d|$" + " (m\u00c5),  " + r"$0\to+3\%$")
    ax.set_ylabel(r"$|\Delta q/q|$ (%),  " + r"$0\to+3\%$")
    ax.text(0.97, 0.05, r"area $\propto|\mathcal{S}|_{n=4}$", transform=ax.transAxes, ha="right", va="bottom",
            fontsize=6.2, color=MID)
    frame(ax)
    tag(ax, "a", dx=-26, dy=6)

    # (b) mismatch vs |S| -------------------------------------------------------------------
    ax = fig.add_subplot(top[1])
    ax.axhspan(0, SIGMA_S_MEV, color=WASH, lw=0, zorder=0)
    for d in DOPANTS:
        c = DOPANT[d]["color"]
        ax.plot([dr[d], dr[d]], [s4[d], s1[d]], "-", color=c, lw=1.0, alpha=0.6, zorder=2)
        ax.errorbar([dr[d]] * 2, [s4[d], s1[d]], yerr=SIGMA_S_MEV, fmt="none", ecolor=c, elinewidth=0.7, capsize=1.9,
                    capthick=0.6, alpha=0.7, zorder=2)
        ax.plot(dr[d], s4[d], linestyle="None", marker=DOPANT[d]["marker"], ms=DOPANT[d]["ms"] + 1.6, mfc=c,
                mec="white", mew=0.8, zorder=4)
        ax.plot(dr[d], s1[d], linestyle="None", marker=DOPANT[d]["marker"], ms=DOPANT[d]["ms"] + 1.6, mfc="white",
                mec=c, mew=1.3, zorder=4)
        side = {"B": (11, "left"), "N": (-11, "right"), "P": (11, "left")}[d]
        label(ax, dr[d], max(s4[d], s1[d]) if d == "P" else 0.5 * (s4[d] + s1[d]), d, color=c, dx=side[0], ha=side[1], fs=7.2, bold=True)
    ax.set_xlim(0, 36)
    ax.set_ylim(-1.5, 40)
    ax.set_xlabel(r"$|\Delta r_{\rm cov}|$ (pm)")
    ax.set_ylabel(r"$|\mathcal{S}|$ (meV/atom)")
    ax.legend(handles=[
        Line2D([0], [0], marker="o", ls="none", ms=5.0, mfc=INK, mec="white", label=r"$n{=}4$"),
        Line2D([0], [0], marker="o", ls="none", ms=5.0, mfc="white", mec=INK, mew=1.1, label=r"$n{=}1$"),
    ], loc="upper left", fontsize=6.4, handletextpad=0.2)
    sec = ax.secondary_xaxis("top", functions=(lambda x: x / R_COV_C_PM * 100, lambda p: p * R_COV_C_PM / 100))
    sec.set_xlabel(r"$|\Delta r_{\rm cov}|/r_{\rm C}$ (%)", fontsize=6.6, labelpad=2)
    sec.tick_params(labelsize=6.0, length=2.4)
    frame(ax, minor=False)
    ax.tick_params(top=False)
    tag(ax, "b", dx=-26, dy=22)

    # (c) linked paths -----------------------------------------------------------------------
    ax = fig.add_subplot(top[2])
    zero_line(ax)
    ax.axhline(1.0, color=HAIR, lw=0.8, zorder=1)
    for d in DOPANTS:
        xq, yq = q[d]
        q0 = float(yq[list(xq).index(0.0)])
        xd, dbar, _ = loc[d]
        d0 = float(dbar[list(xd).index(0.0)])
        trace(ax, xq, yq / q0, d, lw=1.45)
        ax.plot(xd, dbar / d0, "--", color=DOPANT[d]["color"], lw=1.2, zorder=3)
        label(ax, xq[-1], yq[-1] / q0, d, color=DOPANT[d]["color"], dx=6, fs=6.8, bold=True)
    _strain_axis(ax)
    ax.set_ylabel(r"value / value at $\epsilon=0$")
    ax.legend(handles=[
        Line2D([0], [0], color=MID, lw=1.5, label=r"$q/q_0$"),
        Line2D([0], [0], color=MID, lw=1.3, ls="--", label=r"$\bar d/\bar d_0$"),
    ], loc="lower right", fontsize=6.4, handlelength=1.8)
    frame(ax)
    tag(ax, "c", dx=-26, dy=6)

    # (d) parallel coordinates --------------------------------------------------------------
    ax = fig.add_subplot(bot[0])
    metrics = [
        (r"$|\Delta r_{\rm cov}|$", dr, "pm", "{:.0f}"),
        (r"$|\Delta\bar d|$", dd, "m\u00c5", "{:.1f}"),
        (r"$|\Delta q/q|$", dq, "%", "{:.1f}"),
        (r"$|\mathcal{S}|_{n=4}$", s4, "meV/atom", "{:.1f}"),
        (r"$|\mathcal{S}|_{n=1}$", s1, "meV/atom", "{:.1f}"),
    ]
    for x, (_, vals, unit, fmt) in enumerate(metrics):
        ax.plot([x, x], [0, 1], "-", color=HAIR, lw=1.0, zorder=0)
        ax.text(x, 1.075, fmt.format(max(vals.values())) + " " + unit, ha="center", va="bottom", fontsize=5.8, color=MID)
    for d in DOPANTS:
        y = [metrics[i][1][d] / max(metrics[i][1].values()) for i in range(5)]
        ax.plot(range(5), y, "-", color=DOPANT[d]["color"], lw=1.9, alpha=0.9, zorder=2)
        ax.plot(range(5), y, linestyle="None", marker=DOPANT[d]["marker"], ms=DOPANT[d]["ms"] + 1.6,
                mfc=DOPANT[d]["color"], mec="white", mew=0.8, zorder=4)
        label(ax, 4, y[-1], d, color=DOPANT[d]["color"], dx=9, fs=7.2, bold=True)
    ax.set_xlim(-0.35, 4.35)
    ax.set_ylim(-0.04, 1.14)
    ax.set_xticks(range(5))
    ax.set_xticklabels([m[0] for m in metrics], fontsize=7.2)
    ax.set_yticks([0, 0.5, 1.0])
    ax.set_yticklabels(["0", "0.5", "1"])
    ax.set_ylabel("normalised to max over B, N, P")
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    ax.tick_params(top=False, right=False)
    frame(ax, minor=False)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    tag(ax, "d", dx=-28, dy=14)

    return _save(fig, "figure_prb_4_mechanism")


def main() -> None:
    for fn, name in ((build_fig1, "Fig.1"), (build_fig2, "Fig.2"), (build_fig3, "Fig.3"), (build_fig4, "Fig.4")):
        print(name, fn())


if __name__ == "__main__":
    main()
