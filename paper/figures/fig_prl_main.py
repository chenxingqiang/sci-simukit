#!/usr/bin/env python3
"""PRL composite — Capobianco Electron Fig.2 alignment (1×4 row, purple/teal DOS)."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

FIG_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(FIG_DIR))

from _load_audit import load_json, parse_exp7_gaps, repo_root, synergy_rows
from _pdos import gaussian_dos, parse_pdos
from _style import (
    COLOR_CBM,
    COLOR_TOTAL,
    COLOR_VBM,
    DOPANT_COLORS,
    DOPANT_MARKERS,
    PRL_HEIGHT_IN,
    PRL_WIDTH_IN,
    apply_prl_style,
    panel_label,
    style_axes,
)


def _plot_electronic_row(ax_gap, ax_dos, gaps) -> None:
    """(a) Gap vs strain + (b) aligned π-DOS @ B, ε=0 — Electron energy axis."""
    panel_label(ax_gap, "a")
    for dopant in ("pristine", "B", "N", "P"):
        pts = [p for p in gaps if p.dopant == dopant and p.converged]
        if not pts:
            continue
        xs = np.array([p.strain_pct for p in pts])
        ys = np.array([p.gap_ev for p in pts])
        order = np.argsort(xs)
        xs, ys = xs[order], ys[order]
        lw = 0.7 if dopant == "pristine" else 0.85
        ls = "--" if dopant == "pristine" else "-"
        ax_gap.plot(
            xs,
            ys,
            ls=ls,
            lw=lw,
            marker=DOPANT_MARKERS.get(dopant, "o"),
            color=DOPANT_COLORS[dopant],
            label=dopant if dopant != "pristine" else "pristine",
            clip_on=False,
        )
    # Direct-gap annotation (B @ 0%) — offset from data lines
    b0 = next(p for p in gaps if p.dopant == "B" and p.converged and p.strain_pct == 0.0)
    ax_gap.axhline(0, color="#DDDDDD", lw=0.4, zorder=0)
    ax_gap.annotate(
        rf"$E_g={b0.gap_ev:.2f}$ eV",
        xy=(0, b0.gap_ev),
        xytext=(2.0, 0.14),
        fontsize=5.5,
        color=COLOR_CBM,
        ha="left",
        va="center",
        arrowprops=dict(arrowstyle="-|>", color=COLOR_CBM, lw=0.5, shrinkA=2, shrinkB=2),
        annotation_clip=True,
    )
    ax_gap.set_xlabel(r"strain $\varepsilon$ (%)")
    ax_gap.set_ylabel(r"energy gap (eV)")
    ax_gap.set_xlim(-5.5, 5.5)
    ax_gap.set_ylim(-0.22, 1.62)
    style_axes(ax_gap)
    ax_gap.legend(
        frameon=True,
        fancybox=False,
        edgecolor="#CCCCCC",
        facecolor="white",
        framealpha=0.95,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.01),
        ncol=2,
        fontsize=4.8,
        handlelength=1.0,
        borderpad=0.25,
        columnspacing=0.6,
    )

    panel_label(ax_dos, "b")
    pdos_path = repo_root() / "dft_results/exp_7_electronic_structure/outputs/elec_pos0p0_B-k1-1.pdos"
    series = parse_pdos(pdos_path)
    grid = np.linspace(-2.5, 2.5, 400)
    dos = gaussian_dos(series.energy_ev, series.pi_weight, grid, sigma_ev=0.07)
    valence = grid <= 0
    conduction = grid >= 0
    ax_dos.fill_between(grid, 0, dos, where=valence, color=COLOR_VBM, alpha=0.85, lw=0)
    ax_dos.fill_between(grid, 0, dos, where=conduction, color=COLOR_CBM, alpha=0.85, lw=0)
    ax_dos.plot(grid, dos, color=COLOR_TOTAL, lw=0.5, alpha=0.6)
    ax_dos.axvline(0, color="#333333", lw=0.55)
    ax_dos.set_xlabel("energy (eV)")
    ax_dos.set_ylabel("π-DOS (a.u.)")
    ax_dos.set_xlim(-2.0, 2.0)
    ax_dos.set_ylim(0, dos.max() * 1.08)
    style_axes(ax_dos)
    ax_dos.text(
        0.97,
        0.95,
        "B, $\\varepsilon{=}0$",
        transform=ax_dos.transAxes,
        fontsize=5.5,
        va="top",
        ha="right",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.85),
    )


def _plot_alpha(ax, table1) -> None:
    panel_label(ax, "c")
    labels = ["N", "B", "P", "pristine"]
    alphas = [table1["systems"][k]["alpha_meV_per_pct"] for k in labels]
    ypos = np.arange(len(labels))
    ax.barh(ypos, alphas, color=[DOPANT_COLORS[k] for k in labels], height=0.55, edgecolor="none", zorder=2)
    ax.axvline(0, color="#333333", lw=0.55, zorder=1)
    ax.set_yticks(ypos)
    ax.set_yticklabels(labels)
    ax.tick_params(axis="y", pad=1)
    ax.set_xlabel(r"$\alpha$ (meV/%)", labelpad=2)
    ax.invert_yaxis()
    lo, hi = min(alphas), max(alphas)
    span = hi - lo
    pad = max(span * 0.14, 18)
    ax.set_xlim(lo - pad, hi + pad)
    style_axes(ax, grid=True)
    for i, val in enumerate(alphas):
        offset = span * 0.04
        if val >= 0:
            x, ha = val + offset, "left"
        else:
            x, ha = val - offset, "right"
        ax.text(x, i, f"{val:.0f}", va="center", ha=ha, fontsize=5, zorder=3, clip_on=True)


def _plot_synergy_combo(ax_main, ax_inset, audit, exp4) -> None:
    panel_label(ax_main, "d")
    ns = np.array([1, 2, 4, 6, 8], dtype=float)
    for dopant in ("B", "N", "P"):
        rows = synergy_rows(audit, dopant)
        n_pts = np.array([r[0] for r in rows], dtype=float)
        s_pts = np.array([r[1] for r in rows])
        ax_main.plot(
            n_pts,
            s_pts,
            marker=DOPANT_MARKERS[dopant],
            color=DOPANT_COLORS[dopant],
            label=dopant,
            clip_on=False,
        )
        fit = audit["size_scaling_fits"][dopant]
        ax_main.plot(
            ns,
            fit["S_infinity"] + fit["A"] / ns,
            "--",
            color=DOPANT_COLORS[dopant],
            lw=0.65,
            alpha=0.8,
        )
    ax_main.axhline(0, color="#DDDDDD", lw=0.4, zorder=0)
    ax_main.set_xlabel(r"$n\times\mathrm{C}_{60}$", labelpad=2)
    ax_main.set_ylabel(r"$\mathcal{S}$ (meV/atom)", labelpad=2)
    ax_main.yaxis.set_label_coords(-0.20, 0.5)
    ax_main.set_xticks([1, 2, 4, 6, 8])
    ax_main.margins(x=0.06, y=0.18)
    style_axes(ax_main, grid=True)
    ax_main.legend(
        frameon=True,
        fancybox=False,
        edgecolor="#CCCCCC",
        facecolor="white",
        framealpha=0.92,
        ncol=3,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.32),
        fontsize=5,
        handlelength=1.0,
        columnspacing=0.8,
        borderpad=0.25,
    )

    # inset: IPR–J (Exp.4) — lower-right, away from S(n) traces
    p = exp4["systems"]["pristine_0pct"]
    b = exp4["systems"]["coupled_B_3pct"]
    ax_inset.scatter(p["IPR"], p["J_meV"], s=18, color=DOPANT_COLORS["pristine"], zorder=3)
    ax_inset.scatter(b["IPR"], b["J_meV"], s=18, color=COLOR_CBM, marker="^", zorder=3)
    ax_inset.axhline(p["lambda_meV"] / 2, color="#AAAAAA", ls=":", lw=0.5)
    ax_inset.set_xlabel("IPR", fontsize=4.5, labelpad=1)
    ax_inset.set_ylabel(r"$J$ (meV)", fontsize=4.5, labelpad=1)
    ax_inset.tick_params(labelsize=4, pad=1)
    ax_inset.set_facecolor("white")
    for spine in ax_inset.spines.values():
        spine.set_linewidth(0.45)


def build_prl_figure(out_dir: Path) -> tuple[Path, Path]:
    apply_prl_style()
    table1 = load_json("experiments/analysis/table1_verification.json")
    audit = load_json("experiments/analysis/sdc/sdc_exp10_synergy_audit.json")
    exp4 = load_json("experiments/analysis/exp4_polaron_verification.json")
    gaps = parse_exp7_gaps()

    # Electron-style: single horizontal row, aligned panel bottoms
    fig = plt.figure(figsize=(PRL_WIDTH_IN, PRL_HEIGHT_IN))
    gs = GridSpec(
        1,
        4,
        figure=fig,
        width_ratios=[1.05, 0.85, 0.82, 1.05],
        wspace=0.52,
        left=0.09,
        right=0.98,
        top=0.84,
        bottom=0.28,
    )
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[0, 2])
    ax_d = fig.add_subplot(gs[0, 3])

    _plot_electronic_row(ax_a, ax_b, gaps)
    _plot_alpha(ax_c, table1)
    inset = ax_d.inset_axes([0.50, 0.10, 0.40, 0.34])
    _plot_synergy_combo(ax_d, inset, audit, exp4)

    out_dir.mkdir(parents=True, exist_ok=True)
    pdf = out_dir / "figure_prl_main.pdf"
    png = out_dir / "figure_prl_main.png"
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.02)
    fig.savefig(png, bbox_inches="tight", pad_inches=0.02, dpi=300)
    plt.close(fig)
    return pdf, png


def main() -> None:
    pdf, png = build_prl_figure(FIG_DIR / "out")
    print(f"Wrote {pdf}\nWrote {png}")


if __name__ == "__main__":
    main()
