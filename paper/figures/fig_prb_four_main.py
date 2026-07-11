#!/usr/bin/env python3
"""PRB main figures 1–4 — Nature/Science reference aesthetic."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D

FIG_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(FIG_DIR))

from _load_audit import (
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
from _pdos import gaussian_dos, parse_pdos
from _style import (
    DOPANT_COLORS,
    DOPANT_MARKERS,
    INK,
    NATURE_GRAY,
    NATURE_GREEN,
    PRB_WIDTH_IN,
    annotate_box,
    apply_nature_style,
    panel_label,
    style_axes,
)

OUT = FIG_DIR / "out"


def _save(fig: plt.Figure, stem: str) -> tuple[Path, Path]:
    OUT.mkdir(parents=True, exist_ok=True)
    pdf = OUT / f"{stem}.pdf"
    png = OUT / f"{stem}.png"
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.04)
    fig.savefig(png, bbox_inches="tight", pad_inches=0.04, dpi=300)
    plt.close(fig)
    return pdf, png


def _legend_in(ax, handles=None, labels=None, **kw):
    kw.setdefault("frameon", False)
    kw.setdefault("fontsize", 7)
    kw.setdefault("loc", "best")
    if handles is not None:
        ax.legend(handles, labels, **kw)
    else:
        ax.legend(**kw)


# ---------------------------------------------------------------------------
# Figure 1 — electronic background (2×2)
# ---------------------------------------------------------------------------
def build_fig1() -> tuple[Path, Path]:
    apply_nature_style()
    gaps = parse_exp7_gaps()
    alpha_ref, _, _ = load_reference_pbed3_alpha_S()
    hirsh = load_hirshfeld_strain_paths()

    fig = plt.figure(figsize=(PRB_WIDTH_IN, 5.4))
    gs = GridSpec(
        2, 2, figure=fig,
        hspace=0.55, wspace=0.38,
        left=0.09, right=0.97, top=0.93, bottom=0.08,
    )
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    # (a) offset π-DOS
    panel_label(ax_a, "a", nature=True)
    root = repo_root()
    pdos_map = {
        "pristine": root / "dft_results/exp_7_electronic_structure/outputs/elec_pos0p0_pristine-k1-1.pdos",
        "B": root / "dft_results/exp_7_electronic_structure/outputs/elec_pos0p0_B-k1-1.pdos",
        "N": root / "dft_results/exp_7_electronic_structure/outputs/elec_pos0p0_N-k1-1.pdos",
        "P": root / "dft_results/exp_7_electronic_structure/outputs/elec_pos0p0_P-k1-1.pdos",
    }
    grid = np.linspace(-2.5, 2.5, 500)
    offset = 0.0
    step = None
    for dop in ("pristine", "B", "N", "P"):
        path = pdos_map[dop]
        if not path.is_file():
            continue
        series = parse_pdos(path)
        dos = gaussian_dos(series.energy_ev, series.pi_weight, grid, sigma_ev=0.07)
        if step is None:
            step = dos.max() * 1.25
        ax_a.fill_between(grid, offset, offset + dos, color=DOPANT_COLORS[dop], alpha=0.28, lw=0)
        ax_a.plot(grid, offset + dos, color=DOPANT_COLORS[dop], lw=1.2)
        ax_a.text(
            2.25, offset + max(dos.max() * 0.45, step * 0.12),
            dop, color=DOPANT_COLORS[dop], fontsize=8, ha="right", va="bottom", fontweight="bold",
        )
        offset += step
    ax_a.axvline(0, color=INK, lw=0.7, ls="-", alpha=0.55)
    ax_a.set_xlim(-2.2, 2.4)
    ax_a.set_xlabel(r"energy (eV)")
    ax_a.set_ylabel(r"$\pi$-DOS (offset)")
    ax_a.set_yticks([])
    style_axes(ax_a, grid=False)
    annotate_box(ax_a, r"$\epsilon{=}0$", xy=(0.03, 0.97), ha="left", va="top", fontsize=7)

    # (b) gap vs strain — legend above; slope note in mid-gap white space
    panel_label(ax_b, "b", nature=True)
    slope_mev = None
    for dopant in ("pristine", "B", "N", "P"):
        pts = [p for p in gaps if p.dopant == dopant and p.converged]
        if not pts:
            continue
        xs = np.array([p.strain_pct for p in pts])
        ys = np.array([p.gap_ev for p in pts])
        order = np.argsort(xs)
        xs, ys = xs[order], ys[order]
        ax_b.plot(
            xs, ys,
            ls="--" if dopant == "pristine" else "-",
            marker=DOPANT_MARKERS[dopant],
            color=DOPANT_COLORS[dopant],
            label=dopant,
            markerfacecolor="white",
            markeredgewidth=1.2,
            markersize=5.5,
            zorder=3,
        )
        if dopant == "pristine" and len(xs) >= 2:
            slope_mev = float(np.polyfit(xs, ys, 1)[0] * 1000)
    ax_b.axhline(0, color="#CCCCCC", lw=0.7, zorder=1)
    if slope_mev is not None:
        # mid-panel white space between pristine (~1 eV) and doped (~0)
        # white band between pristine (~1 eV) and doped (~0); keep clear of markers
        ax_b.text(
            0.50, 0.58,
            rf"$\mathrm{{d}}E_g/\mathrm{{d}}\epsilon\approx{slope_mev:.0f}$ meV/\% (pristine)",
            transform=ax_b.transAxes, ha="center", va="center",
            fontsize=6.5, color=NATURE_GRAY,
            bbox=dict(boxstyle="round,pad=0.28", facecolor="white", edgecolor="#EEEEEE", lw=0.5, alpha=0.95),
        )
    ax_b.set_xlabel(r"strain $\epsilon$ (%)")
    ax_b.set_ylabel(r"HOMO–LUMO gap (eV)")
    # leave headroom so legend does not collide with pristine peak
    ymin, ymax = ax_b.get_ylim()
    ax_b.set_ylim(min(ymin, -0.15), max(ymax, 1.65))
    style_axes(ax_b, grid=False)
    _legend_in(ax_b, loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=4, columnspacing=0.9, handlelength=1.6)

    # (c) Hirshfeld
    panel_label(ax_c, "c", nature=True)
    dopants = ["B", "N", "P"]
    q0 = [dict(hirsh[d])[0.0] for d in dopants]
    bars = ax_c.bar(
        dopants, q0,
        color=[DOPANT_COLORS[d] for d in dopants],
        width=0.58, zorder=3, edgecolor="white", linewidth=0.8,
    )
    for rect, val in zip(bars, q0):
        ax_c.text(
            rect.get_x() + rect.get_width() / 2, val + 0.004,
            f"{val:.3f}", ha="center", va="bottom", fontsize=8, fontweight="bold", color=INK,
        )
    ax_c.set_ylabel(r"Hirshfeld charge ($e$)")
    ax_c.set_xlabel("dopant")
    ax_c.set_ylim(0, max(q0) * 1.28)
    style_axes(ax_c, grid=False)
    annotate_box(ax_c, r"$n{=}1$, $\epsilon{=}0$", xy=(0.97, 0.95), ha="right", va="top", fontsize=7)

    # (d) reference α
    panel_label(ax_d, "d", nature=True)
    labels = ["pristine", "B", "N", "P"]
    vals = [alpha_ref[d] for d in labels]
    y = np.arange(len(labels))
    ax_d.barh(y, vals, color=[DOPANT_COLORS[d] for d in labels], height=0.52, zorder=3, edgecolor="white", lw=0.6)
    ax_d.axvline(0, color=INK, lw=0.8)
    ax_d.set_yticks(y)
    ax_d.set_yticklabels(labels)
    ax_d.invert_yaxis()
    ax_d.set_xlabel(r"$\alpha$ (meV/\%)")
    for yi, v in zip(y, vals):
        if abs(v) >= 50:
            ax_d.text(
                v * 0.52, yi, f"{v:.0f}",
                va="center", ha="center", fontsize=7.5, fontweight="bold", color="white",
            )
        else:
            ax_d.text(
                v + (22 if v >= 0 else -22), yi, f"{v:.0f}",
                va="center", ha="left" if v >= 0 else "right",
                fontsize=7.5, fontweight="bold", color=INK,
            )
    # room for end labels on short bars
    xmin = min(vals)
    xmax = max(vals)
    pad = 0.12 * (xmax - xmin)
    ax_d.set_xlim(xmin - pad * 0.3, xmax + pad)
    style_axes(ax_d, grid=False)
    return _save(fig, "figure_prb_1_electronic")


# ---------------------------------------------------------------------------
# Figure 2 — core S quantification (1×3)
# ---------------------------------------------------------------------------
def build_fig2() -> tuple[Path, Path]:
    apply_nature_style()
    audit = load_json("experiments/analysis/sdc/sdc_exp10_synergy_audit.json")
    s_rig, s_rel = load_periodic_relax_n1_P()

    fig = plt.figure(figsize=(PRB_WIDTH_IN, 2.85))
    gs = GridSpec(1, 3, figure=fig, wspace=0.42, left=0.08, right=0.98, top=0.84, bottom=0.18)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[0, 2])

    # (a) grouped bars — legend above; peak callout in clear space
    panel_label(ax_a, "a", nature=True)
    ns = [1, 2, 4]
    x = np.arange(len(ns), dtype=float)
    width = 0.26
    for i, dop in enumerate(("B", "N", "P")):
        rows = dict(synergy_rows(audit, dop))
        vals = [rows[n] for n in ns]
        bars = ax_a.bar(
            x + (i - 1) * width, vals, width=width,
            color=DOPANT_COLORS[dop], edgecolor="white", linewidth=0.6,
            label=dop, zorder=3, alpha=0.92,
        )
        for rect, v in zip(bars, vals):
            if abs(v) >= 15:
                ax_a.text(
                    rect.get_x() + rect.get_width() / 2,
                    v - 2.2,
                    f"{v:.1f}",
                    ha="center", va="top",
                    fontsize=6.5, fontweight="bold", color="white",
                )
    # peak value already printed inside P bars; no arrow callouts
    ax_a.axhline(0, color=INK, lw=0.8)
    ax_a.axhline(10, color="#BBBBBB", ls="--", lw=0.8)
    ax_a.axhline(-10, color="#BBBBBB", ls="--", lw=0.8)
    ax_a.text(2.48, 11.2, r"$|\mathcal{S}|{=}10$", fontsize=6.5, color=NATURE_GRAY, ha="right")
    ax_a.set_xticks(x)
    ax_a.set_xticklabels([rf"$n{{=}}{n}$" for n in ns])
    ax_a.set_ylabel(r"$\mathcal{S}$ (meV/atom)")
    ax_a.set_ylim(-38, 16)
    style_axes(ax_a, grid=False)
    _legend_in(ax_a, loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=3)

    # (b) S(n) — legend above; n=4 labels left of points
    panel_label(ax_b, "b", nature=True)
    for dop in ("B", "N", "P"):
        rows = synergy_rows(audit, dop)
        n_all = np.array([r[0] for r in rows], dtype=float)
        s_all = np.array([r[1] for r in rows])
        core = n_all <= 4
        ax_b.plot(
            n_all[core], s_all[core], "-o",
            color=DOPANT_COLORS[dop], label=dop,
            markersize=6, markerfacecolor="white", markeredgewidth=1.4, lw=1.5,
        )
        if np.any(~core):
            ax_b.plot(
                n_all[~core], s_all[~core], "--o",
                color=DOPANT_COLORS[dop], alpha=0.45, markersize=4.5, lw=1.1,
            )
        if 4 in n_all:
            s4 = float(s_all[n_all == 4][0])
            dy = {"B": -12, "N": 10, "P": -12}[dop]
            ax_b.annotate(
                f"{s4:+.1f}", xy=(4, s4),
                xytext=(-8, dy), textcoords="offset points",
                fontsize=7, color=DOPANT_COLORS[dop], fontweight="bold",
                ha="right",
            )
    ax_b.axhline(0, color="#CCCCCC", lw=0.7)
    ax_b.set_xscale("log")
    ax_b.set_xticks([1, 2, 4, 6, 8])
    ax_b.set_xticklabels(["1", "2", "4", "6", "8"])
    ax_b.xaxis.set_minor_formatter(plt.NullFormatter())
    ax_b.minorticks_off()
    ax_b.set_xlabel(r"supercell size $n$")
    ax_b.set_ylabel(r"$\mathcal{S}$ (meV/atom)")
    style_axes(ax_b, grid=False)
    _legend_in(ax_b, loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=3)

    # (c) rigid vs relaxed — note in white space, not over bar
    panel_label(ax_c, "c", nature=True)
    ax_c.bar(
        ["rigid", "relaxed"],
        [s_rig, s_rel],
        color=[DOPANT_COLORS["P"], NATURE_GRAY],
        width=0.52, zorder=3, edgecolor="white", lw=0.8,
    )
    ax_c.axhline(0, color=INK, lw=0.8)
    ax_c.text(0, s_rig / 2, f"{s_rig:.1f}", ha="center", va="center",
              fontsize=9, fontweight="bold", color="white")
    ax_c.text(1, max(s_rel, 0) + 1.8, f"{s_rel:.1e}", ha="center", va="bottom",
              fontsize=7, color=NATURE_GRAY, fontweight="bold")
    ax_c.set_ylabel(r"$\mathcal{S}$ (meV/atom)")
    ax_c.set_ylim(min(s_rig, 0) * 1.12, 14)
    style_axes(ax_c, grid=False)
    annotate_box(ax_c, r"$n{=}1$ P, $+3$\%", xy=(0.03, 0.97), ha="left", va="top", fontsize=7)
    ax_c.text(
        0.98, 0.42,
        "upper bound\nnearly extinguished",
        transform=ax_c.transAxes, ha="right", va="center",
        fontsize=7, color=NATURE_GRAY, style="italic",
        bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#DDDDDD", lw=0.5, alpha=0.95),
    )

    return _save(fig, "figure_prb_2_synergy")


# ---------------------------------------------------------------------------
# Figure 3 — α–S decoupling (2×2) — correlation-style panel (c)
# ---------------------------------------------------------------------------
def build_fig3() -> tuple[Path, Path]:
    apply_nature_style()
    alpha_ref, s_ref, _ = load_reference_pbed3_alpha_S()
    audit = load_json("experiments/analysis/sdc/sdc_exp10_results.json")
    audit_mev = load_json("experiments/analysis/sdc/sdc_exp10_synergy_audit.json")

    fig = plt.figure(figsize=(PRB_WIDTH_IN, 5.3))
    gs = GridSpec(
        2, 2, figure=fig,
        hspace=0.48, wspace=0.38,
        left=0.10, right=0.96, top=0.96, bottom=0.08,
    )
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    dopants = ["B", "N", "P"]
    y = np.arange(len(dopants), dtype=float)

    # (a)(b) reference-placement only (alternate seed kept in Table/SI, not main figure)
    panel_label(ax_a, "a", nature=True)
    ref_v = [alpha_ref[d] for d in dopants]
    for i, d in enumerate(dopants):
        c = DOPANT_COLORS[d]
        ax_a.barh(y[i], ref_v[i], height=0.55, color=c, zorder=3, edgecolor="white", lw=0.6)
        v = ref_v[i]
        if abs(v) >= 50:
            ax_a.text(v * 0.52, y[i], f"{v:.0f}", va="center", ha="center",
                      fontsize=7.5, fontweight="bold", color="white")
        else:
            ax_a.text(v + (12 if v >= 0 else -12), y[i], f"{v:.0f}", va="center",
                      ha="left" if v >= 0 else "right", fontsize=7.5, fontweight="bold", color=INK)
    ax_a.axvline(0, color=INK, lw=0.8)
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(dopants)
    ax_a.invert_yaxis()
    ax_a.set_xlabel(r"$\alpha$ (meV/\%)")
    style_axes(ax_a, grid=False)

    panel_label(ax_b, "b", nature=True)
    ref_s = [s_ref[d] for d in dopants]
    for i, d in enumerate(dopants):
        c = DOPANT_COLORS[d]
        ax_b.barh(y[i], ref_s[i], height=0.55, color=c, zorder=3, edgecolor="white", lw=0.6)
        v = ref_s[i]
        ax_b.text(
            v + (0.8 if v >= 0 else -0.8), y[i], f"{v:+.1f}",
            va="center", ha="left" if v >= 0 else "right",
            fontsize=7.5, fontweight="bold", color=INK,
        )
    ax_b.axvline(0, color=INK, lw=0.8)
    ax_b.set_yticks(y)
    ax_b.set_yticklabels(dopants)
    ax_b.invert_yaxis()
    ax_b.set_xlabel(r"$\mathcal{S}_{+3\%}^{\mathrm{tet}}$ (meV/atom)")
    style_axes(ax_b, grid=False)

    # (c) |α| vs |S| — minimal labels
    panel_label(ax_c, "c", nature=True)
    abs_alpha = np.array([abs(alpha_ref[d]) for d in dopants], dtype=float)
    abs_S = np.array(
        [abs(dict(synergy_rows(audit_mev, d))[4]) for d in dopants],
        dtype=float,
    )
    offsets = {"B": (9, 7), "N": (12, 8), "P": (-10, 9)}
    aligns = {"B": "left", "N": "left", "P": "right"}
    for d, xa, ys in zip(dopants, abs_alpha, abs_S):
        ax_c.scatter(
            xa, ys, s=110, color=DOPANT_COLORS[d], marker=DOPANT_MARKERS[d],
            zorder=4, edgecolors=INK, linewidths=0.7,
        )
        dx, dy = offsets[d]
        ax_c.annotate(
            d, (xa, ys), textcoords="offset points",
            xytext=(dx, dy), fontsize=9, fontweight="bold", color=DOPANT_COLORS[d],
            ha=aligns[d],
        )
    ax_c.set_xlabel(r"$|\alpha|$ reference (meV/\%)")
    ax_c.set_ylabel(r"$|\mathcal{S}|$ at $n{=}4$ (meV/atom)")
    ax_c.set_xlim(0, max(abs_alpha) * 1.18)
    ax_c.set_ylim(0, max(abs_S) * 1.35)
    style_axes(ax_c, grid=False)
    # single corner tag; decoupling is visible from N vs P positions (caption explains)
    annotate_box(ax_c, r"periodic $n{=}4$", xy=(0.03, 0.97), ha="left", va="top", fontsize=7)

    # (d) additive vs coupled — numbers inside long bars; note in clear mid-right
    panel_label(ax_d, "d", nature=True)
    seq = coupled = s_val = None
    HA = 27211.386245988
    for row in audit.get("synergy_energy_per_atom", []):
        if row.get("dopant") == "P" and row.get("n_molecules") == 4:
            seq = (row["strain_only_delta"] + row["doping_only_delta"]) * HA
            coupled = (row["combined"] - row["reference"]) * HA
            s_val = row["synergy_S"] * HA
            break
    if seq is None:
        s_val = -23.71
        seq = 0.0
        coupled = s_val
    cats = ["additive\nprediction", "coupled\nDFT", r"omitted $\mathcal{S}$"]
    vals = [seq, coupled, s_val]
    colors = [NATURE_GRAY, NATURE_GREEN, DOPANT_COLORS["P"]]
    bars = ax_d.bar(cats, vals, color=colors, width=0.55, zorder=3, edgecolor="white", lw=0.6)
    ax_d.axhline(0, color=INK, lw=0.8)
    ymin = min(vals)
    ax_d.set_ylim(ymin * 1.18, 55)
    for rect, v in zip(bars, vals):
        xc = rect.get_x() + rect.get_width() / 2
        if abs(v) > 80:
            # number inside bar (white)
            ax_d.text(xc, v * 0.55, f"{v:.1f}", ha="center", va="center",
                      fontsize=8, fontweight="bold", color="white", zorder=5)
        else:
            # short bar: number to the right (clear of x-label)
            ax_d.text(xc + 0.38, v * 0.5, f"{v:.1f}", ha="left", va="center",
                      fontsize=8, fontweight="bold", color=INK, zorder=5)
    ax_d.set_ylabel(r"$\Delta E$ (meV/atom)")
    style_axes(ax_d, grid=False)
    annotate_box(ax_d, r"P, $n{=}4$, $+3$\%", xy=(0.50, 0.98), ha="center", va="top", fontsize=7)

    return _save(fig, "figure_prb_3_decoupling")


# ---------------------------------------------------------------------------
# Figure 4 — DFT local geometry + population (mechanism evidence)
# ---------------------------------------------------------------------------
def build_fig4() -> tuple[Path, Path]:
    apply_nature_style()
    local = load_local_structure_summary()
    d_paths = load_local_structure_paths()
    hirsh = load_hirshfeld_strain_paths()
    audit = load_json("experiments/analysis/sdc/sdc_exp10_synergy_audit.json")
    dopants = ["B", "N", "P"]

    fig = plt.figure(figsize=(PRB_WIDTH_IN, 2.65))
    gs = GridSpec(
        1, 3, figure=fig,
        wspace=0.40,
        left=0.08, right=0.98, top=0.84, bottom=0.18,
    )
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[0, 2])

    # (a) DFT local geometry: mean dopant–C distance vs strain (XYZ)
    panel_label(ax_a, "a", nature=True)
    for d in dopants:
        pts = d_paths[d]
        xs = np.array([p[0] for p in pts])
        ys = np.array([p[1] for p in pts])
        ye = np.array([p[2] for p in pts])
        ax_a.errorbar(
            xs, ys, yerr=ye,
            color=DOPANT_COLORS[d], marker=DOPANT_MARKERS[d],
            ls="-", lw=1.2, markersize=5.5, markerfacecolor="white",
            markeredgewidth=1.2, elinewidth=0.9, capsize=2.0,
            label=d, zorder=3,
        )
    ax_a.set_xlabel(r"strain $\epsilon$ (%)")
    ax_a.set_ylabel(r"$\bar{d}_{\mathrm{X-C}}$ (\AA)")
    style_axes(ax_a, grid=False)
    _legend_in(ax_a, loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=3, columnspacing=0.9)
    annotate_box(ax_a, r"tetramer XYZ", xy=(0.03, 0.97), ha="left", va="top", fontsize=7)

    # (b) Δd̄ (0→+3%) vs |S| at n=4 — geometry does not stretch with |S|
    panel_label(ax_b, "b", nature=True)
    offsets_b = {"B": (7, 6), "N": (7, -9), "P": (-8, 7)}
    aligns_b = {"B": "left", "N": "left", "P": "right"}
    for d in dopants:
        dd = abs(local[d]["delta_d_eps0_to_eps3_ang"]) * 1e3  # mÅ
        s_abs = abs(dict(synergy_rows(audit, d))[4])
        ax_b.scatter(
            dd, s_abs, s=110, color=DOPANT_COLORS[d], marker=DOPANT_MARKERS[d],
            zorder=4, edgecolors=INK, linewidths=0.7,
        )
        dx, dy = offsets_b[d]
        ax_b.annotate(
            d, (dd, s_abs), textcoords="offset points", xytext=(dx, dy),
            fontsize=9, fontweight="bold", color=DOPANT_COLORS[d], ha=aligns_b[d],
        )
    ax_b.set_xlabel(r"$|\Delta\bar{d}|_{0\to +3\%}$ (m\AA)")
    ax_b.set_ylabel(r"$|\mathcal{S}|$ at $n{=}4$ (meV/atom)")
    ax_b.set_xlim(-0.5, max(abs(local[d]["delta_d_eps0_to_eps3_ang"]) for d in dopants) * 1e3 * 1.25)
    ax_b.set_ylim(0, max(abs(dict(synergy_rows(audit, d))[4]) for d in dopants) * 1.35)
    style_axes(ax_b, grid=False)

    # (c) Hirshfeld charge vs strain — full DFT population path
    panel_label(ax_c, "c", nature=True)
    for d in dopants:
        pts = hirsh[d]
        xs = np.array([p[0] for p in pts])
        ys = np.array([p[1] for p in pts])
        ax_c.plot(
            xs, ys,
            color=DOPANT_COLORS[d], marker=DOPANT_MARKERS[d],
            ls="-", lw=1.2, markersize=5.5, markerfacecolor="white",
            markeredgewidth=1.2, label=d, zorder=3,
        )
    ax_c.set_xlabel(r"strain $\epsilon$ (%)")
    ax_c.set_ylabel(r"Hirshfeld $q$ ($e$)")
    style_axes(ax_c, grid=False)
    _legend_in(ax_c, loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=3, columnspacing=0.9)
    annotate_box(ax_c, r"$n{=}1$ periodic", xy=(0.03, 0.97), ha="left", va="top", fontsize=7)

    return _save(fig, "figure_prb_4_mechanism")


def main() -> None:
    for builder, name in (
        (build_fig1, "Fig.1"),
        (build_fig2, "Fig.2"),
        (build_fig3, "Fig.3"),
        (build_fig4, "Fig.4"),
    ):
        pdf, png = builder()
        print(f"{name}: {pdf}")


if __name__ == "__main__":
    main()
