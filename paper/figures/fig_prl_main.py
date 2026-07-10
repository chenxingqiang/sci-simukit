#!/usr/bin/env python3
"""PRL composite — Capobianco Electron Fig.2 alignment (1×4 row, purple/teal DOS)."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D

FIG_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(FIG_DIR))

from _load_audit import load_json, load_placement_alpha_pair, load_tetramer_alpha_panel, parse_exp7_gaps, repo_root, synergy_rows
from _pdos import gaussian_dos, parse_pdos
from _style import (
    COLOR_CBM,
    COLOR_TOTAL,
    COLOR_VBM,
    DOPANT_COLORS,
    DOPANT_MARKERS,
    PRL_HEIGHT_IN,
    PRL_WIDTH_IN,
    PRB_HEIGHT_IN,
    PRB_WIDTH_IN,
    apply_prl_style,
    apply_nature_style,
    apply_prb_style,
    apply_si_style,
    NATURE_BLUE,
    NATURE_RED,
    panel_label,
    style_axes,
)


def _dopant_legend_handles() -> list[Line2D]:
    """Shared pristine / B / N / P legend for the full composite figure."""
    handles: list[Line2D] = []
    for dopant in ("pristine", "B", "N", "P"):
        ls = "--" if dopant == "pristine" else "-"
        lw = 0.7 if dopant == "pristine" else 0.85
        handles.append(
            Line2D(
                [0],
                [0],
                ls=ls,
                lw=lw,
                marker=DOPANT_MARKERS.get(dopant, "o"),
                color=DOPANT_COLORS[dopant],
                label=dopant,
            )
        )
    return handles


def _add_unified_dopant_legend(fig: plt.Figure) -> None:
    handles = _dopant_legend_handles()
    fig.legend(
        handles,
        [h.get_label() for h in handles],
        frameon=True,
        fancybox=False,
        edgecolor="#CCCCCC",
        facecolor="white",
        framealpha=0.95,
        loc="upper left",
        ncol=4,
        fontsize=5,
        handlelength=1.2,
        columnspacing=0.9,
        borderpad=0.3,
        bbox_to_anchor=(0.08, 1.0),
    )


def _plot_electronic_row(ax_gap, ax_dos, gaps) -> None:
    """(a) Gap vs strain + (b) aligned π-DOS @ B, ε=0 — Electron energy axis."""
    panel_label(ax_gap, "a", nature=True)
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
            label="_nolegend_",
            clip_on=False,
        )
    # Direct-gap annotation (B @ 0%) — upper-right corner, arrow to data (avoid line overlap).
    b0 = next(p for p in gaps if p.dopant == "B" and p.converged and p.strain_pct == 0.0)
    ax_gap.axhline(0, color="#DDDDDD", lw=0.4, zorder=0)
    ax_gap.annotate(
        rf"$E_g={b0.gap_ev:.2f}$ eV",
        xy=(0, b0.gap_ev),
        xytext=(0.97, 0.90),
        textcoords=ax_gap.transAxes,
        fontsize=5.3,
        color=COLOR_CBM,
        ha="right",
        va="top",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor=COLOR_CBM, alpha=0.95, lw=0.4),
        arrowprops=dict(
            arrowstyle="-|>",
            color=COLOR_CBM,
            lw=0.45,
            shrinkA=2,
            shrinkB=4,
            connectionstyle="arc3,rad=0.25",
        ),
        annotation_clip=True,
        zorder=5,
    )
    ax_gap.set_xlabel(r"strain $\epsilon$ (%)")
    ax_gap.set_ylabel(r"energy gap (eV)")
    ax_gap.set_xlim(-5.5, 5.5)
    ax_gap.set_ylim(-0.22, 1.62)
    style_axes(ax_gap, grid=True, grid_axis="both")

    panel_label(ax_dos, "b", nature=True)
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
    ax_dos.set_ylabel(r"$\pi$-DOS (a.u.)")
    ax_dos.set_xlim(-2.0, 2.0)
    ax_dos.set_ylim(0, dos.max() * 1.08)
    style_axes(ax_dos, grid=True, grid_axis="y")
    ax_dos.text(
        0.97,
        0.95,
        "B, $\\epsilon{=}0$",
        transform=ax_dos.transAxes,
        fontsize=5.5,
        va="top",
        ha="right",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.85),
    )


def _plot_alpha_placement_compare(ax, ref: dict[str, float], alt: dict[str, float]) -> None:
    """Panel (c): paired reference vs alternate alpha — Nature two-condition bars."""
    panel_label(ax, "c", nature=True)
    dopants = ["N", "B", "P"]
    y = np.arange(len(dopants), dtype=float)
    h = 0.34
    ref_vals = [ref[d] for d in dopants]
    alt_vals = [alt[d] for d in dopants]
    ax.barh(y + h / 2, ref_vals, height=h, color=NATURE_BLUE, label="Reference (seed~42)", zorder=3)
    ax.barh(y - h / 2, alt_vals, height=h, color=NATURE_RED, label="Alternate (seed~137)", zorder=3)
    ax.axvline(0, color="#333333", lw=0.65, zorder=1)
    ax.set_yticks(y)
    ax.set_yticklabels(dopants)
    ax.invert_yaxis()
    ax.set_xlabel(r"Linear strain coefficient $\alpha$ (meV/%)", labelpad=3)
    lo, hi = min(ref_vals + alt_vals), max(ref_vals + alt_vals)
    pad = max(abs(lo), abs(hi)) * 0.12 + 18
    ax.set_xlim(lo - pad, hi + pad)
    style_axes(ax, grid=True, grid_axis="x")
    ax.legend(
        loc="lower right",
        frameon=False,
        fontsize=6.5,
        handlelength=1.4,
        borderaxespad=0.4,
    )
    for yi, rv, av in zip(y, ref_vals, alt_vals):
        for val, dy, color in ((rv, h / 2, NATURE_BLUE), (av, -h / 2, NATURE_RED)):
            if abs(val) >= 90:
                x = val * (0.65 if val < 0 else 0.35)
                ax.text(
                    x,
                    yi + dy,
                    f"{val:.0f}",
                    va="center",
                    ha="center",
                    fontsize=5.5,
                    color="white",
                    fontweight="bold",
                    zorder=4,
                )




def _plot_alpha(ax, alphas: dict[str, float], protocol_note: str) -> None:
    """PRL row: same paired placement comparison as PRB panel (c)."""
    ref, alt = load_placement_alpha_pair()
    _plot_alpha_placement_compare(ax, ref, alt)

def _plot_synergy_combo(ax_main, audit, exp4, *, show_inset: bool = False, ax_inset=None) -> None:
    panel_label(ax_main, "d", nature=True)
    ns = np.array([1, 2, 4, 6, 8], dtype=float)
    n4_labels: dict[str, tuple[float, float]] = {}
    for dopant in ("B", "N", "P"):
        rows = synergy_rows(audit, dopant)
        n_pts = np.array([r[0] for r in rows], dtype=float)
        s_pts = np.array([r[1] for r in rows])
        for n, s in zip(n_pts, s_pts):
            if int(n) == 4:
                n4_labels[dopant] = (float(n), float(s))
        ax_main.plot(
            n_pts,
            s_pts,
            marker=DOPANT_MARKERS[dopant],
            color=DOPANT_COLORS[dopant],
            label="_nolegend_",
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
    ax_main.set_xscale("log")
    ax_main.set_xlabel(r"Supercell size $n$ ($n\times\mathrm{C}_{60}$)", labelpad=2)
    ax_main.set_ylabel(r"$\mathcal{S}$ (meV/atom)", labelpad=2)
    ax_main.yaxis.set_label_coords(-0.20, 0.5)
    ax_main.set_xticks([1, 2, 4, 6, 8])
    ax_main.margins(x=0.06, y=0.18)
    style_axes(ax_main, grid=True, grid_axis="both")
    # Compact n=4 values — lower-left to avoid P(n=1) peak annotation (panel d).
    if n4_labels:
        parts = [rf"{d} ${n4_labels[d][1]:+.1f}$" for d in ("B", "N", "P") if d in n4_labels]
        ax_main.text(
            0.03,
            0.06,
            r"$n{=}4$: " + ", ".join(parts) + r" meV/atom",
            transform=ax_main.transAxes,
            fontsize=5.0,
            va="bottom",
            ha="left",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#CCCCCC", alpha=0.96, lw=0.45),
        )
    p_rows = synergy_rows(audit, "P")
    p_n1 = next((s for n, s in p_rows if int(n) == 1), None)
    if p_n1 is not None:
        ax_main.annotate(
            rf"max $|\mathcal{{S}}|={abs(p_n1):.1f}$",
            xy=(1.0, p_n1),
            xytext=(0.97, 0.92),
            textcoords=ax_main.transAxes,
            fontsize=5.3,
            color=DOPANT_COLORS["P"],
            ha="right",
            va="top",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor=DOPANT_COLORS["P"], alpha=0.95, lw=0.4),
            arrowprops=dict(
                arrowstyle="-|>",
                color=DOPANT_COLORS["P"],
                lw=0.45,
                shrinkA=4,
                shrinkB=5,
                connectionstyle="arc3,rad=-0.3",
            ),
            zorder=5,
        )

    if show_inset and ax_inset is not None:
        keys = [
            ("pristine_0pct", DOPANT_COLORS["pristine"], "o"),
            ("pristine_3pct", DOPANT_COLORS["pristine"], "s"),
            ("B_0pct", COLOR_CBM, "^"),
            ("coupled_B_3pct", COLOR_CBM, "D"),
        ]
        for key, color, marker in keys:
            pt = exp4["systems"][key]
            ax_inset.scatter(pt["IPR"], pt["J_meV"], s=16, color=color, marker=marker, zorder=3)
        ax_inset.axhline(50, color="#AAAAAA", ls=":", lw=0.5)
        ax_inset.set_xlabel("IPR", fontsize=4.5, labelpad=1)
        ax_inset.set_ylabel(r"$J$ (meV)", fontsize=4.5, labelpad=1)
        ax_inset.tick_params(labelsize=4, pad=1)
        ax_inset.set_facecolor("white")
        for spine in ax_inset.spines.values():
            spine.set_linewidth(0.45)


def build_prl_figure(out_dir: Path) -> tuple[Path, Path]:
    apply_prl_style()
    table1 = load_json("experiments/analysis/table1_verification.json")
    alpha_panel, alpha_note = load_tetramer_alpha_panel()
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
        top=0.86,
        bottom=0.28,
    )
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[0, 2])
    ax_d = fig.add_subplot(gs[0, 3])

    _plot_electronic_row(ax_a, ax_b, gaps)
    _plot_alpha(ax_c, alpha_panel, alpha_note)
    inset = ax_d.inset_axes([0.50, 0.10, 0.40, 0.34])
    _plot_synergy_combo(ax_d, audit, exp4, show_inset=True, ax_inset=inset)
    _add_unified_dopant_legend(fig)

    out_dir.mkdir(parents=True, exist_ok=True)
    pdf = out_dir / "figure_prl_main.pdf"
    png = out_dir / "figure_prl_main.png"
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.02)
    fig.savefig(png, bbox_inches="tight", pad_inches=0.02, dpi=300)
    plt.close(fig)
    return pdf, png


def build_prb_figure(out_dir: Path) -> tuple[Path, Path]:
    apply_nature_style()
    table1 = load_json("experiments/analysis/table1_verification.json")
    ref_alpha, alt_alpha = load_placement_alpha_pair()
    audit = load_json("experiments/analysis/sdc/sdc_exp10_synergy_audit.json")
    exp4 = load_json("experiments/analysis/exp4_polaron_verification.json")
    gaps = parse_exp7_gaps()

    fig = plt.figure(figsize=(PRB_WIDTH_IN, PRB_HEIGHT_IN))
    gs = GridSpec(
        1,
        4,
        figure=fig,
        width_ratios=[1.08, 0.88, 1.05, 1.08],
        wspace=0.55,
        left=0.10,
        right=0.98,
        top=0.88,
        bottom=0.22,
    )
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[0, 2])
    ax_d = fig.add_subplot(gs[0, 3])
    _plot_electronic_row(ax_a, ax_b, gaps)
    _plot_alpha_placement_compare(ax_c, ref_alpha, alt_alpha)
    _plot_synergy_combo(ax_d, audit, exp4, show_inset=False)
    _add_unified_dopant_legend(fig)
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf = out_dir / "figure_prb_main.pdf"
    png = out_dir / "figure_prb_main.png"
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.02)
    fig.savefig(png, bbox_inches="tight", pad_inches=0.02, dpi=300)
    plt.close(fig)
    return pdf, png


def main() -> None:
    import sys
    out = FIG_DIR / "out"
    if len(sys.argv) > 1 and sys.argv[1] == "--prb":
        pdf, png = build_prb_figure(out)
    else:
        pdf, png = build_prl_figure(out)
    print(f"Wrote {pdf}\nWrote {png}")


if __name__ == "__main__":
    main()
