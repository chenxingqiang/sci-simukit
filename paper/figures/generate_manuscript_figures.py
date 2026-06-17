#!/usr/bin/env python3
"""Main-text figures — physics-first narrative, verified JSON only."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from nature_style import (  # noqa: E402
    NATURE_DOUBLE_COL,
    annotate_bar_values,
    apply_nature_style,
    finalize_axes,
    fit_curve_n,
    get_color,
    origin_legend,
    save_figure,
    shade_alpha_physics,
    shade_strain_response_physics,
    shade_synergy_physics,
    style_line,
)
from pdos_parser import HA_TO_EV, gaussian_dos, gap_matrix, load_exp7_pdos, records_for  # noqa: E402
from electronic_morphology import (  # noqa: E402
    plot_band_edge_morph,
    plot_gap_heatmap,
    plot_pdos_deconvolution_xps,
)
from structure_morphology import (  # noqa: E402
    plot_dopant_triptych,
    plot_ipr_localization_morph,
    plot_strain_cell_morph,
    plot_tetramer_topview,
)
from design_space_triangle import plot_synergy_design_triangle  # noqa: E402

HA_TO_MEV = 27.211386245988 * 1000.0
EXP5_DOPANTS = ("B", "N", "P")
P_EXCLUDE_STRAIN = 2.5
TETRAMER_N = 4
EXP10_STRAIN = 3.0

# Physical one-line interpretation at n=4, +3% (verified synergy signs)
S_PHYSICS = {
    "B": "cooperative\nstabilization",
    "N": "anti-cooperative\nunder tension",
    "P": "strongest\nstrain–dopant\nbinding",
}


def load_json(path: Path) -> dict | list:
    with open(path) as f:
        return json.load(f)


def group_exp5(data: dict) -> Dict[str, List[dict]]:
    out: Dict[str, List[dict]] = defaultdict(list)
    for val in data.values():
        if val.get("status") != "success":
            continue
        out[val["dopant"]].append(val)
    for dop in out:
        out[dop].sort(key=lambda r: r["strain"])
    return out


def _synergy_by_dopant(audit: dict) -> Dict[str, List[dict]]:
    by_dop: Dict[str, List[dict]] = defaultdict(list)
    for row in audit["synergy_table"]:
        by_dop[row["dopant"]].append(row)
    for dop in by_dop:
        by_dop[dop].sort(key=lambda r: r["n_molecules"])
    return by_dop


def _delta_e_at_strain(grouped: dict, dop: str, strain: float) -> float:
    recs = grouped[dop]
    e0 = next(r["total_energy_Ha"] for r in recs if r["strain"] == 0.0)
    n_atoms = recs[0]["n_atoms"]
    for r in recs:
        if abs(r["strain"] - strain) < 0.01:
            return (r["total_energy_Ha"] - e0) * HA_TO_MEV / n_atoms
    raise KeyError(f"{dop} @ {strain}%")


XYZ_DIR = ROOT / "dft_results/exp_5_synergy/xyz_structures"
INP_DIR = ROOT / "dft_results/exp_5_synergy"
PDOS_DIR = ROOT / "experiments/exp_7_electronic_structure/results"


def figure1_strain_coupling(exp5: dict, table1: dict, out_dir: Path) -> Path:
    """Fig. 1: morphology (structure + strain cell) + mechanical response."""
    apply_nature_style()
    grouped = group_exp5(exp5)
    fig = plt.figure(figsize=(NATURE_DOUBLE_COL, NATURE_DOUBLE_COL * 0.72))
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.28)

    ax0 = fig.add_subplot(gs[0, 0])
    plot_dopant_triptych(ax0, XYZ_DIR, strain_tag="+0.0")
    finalize_axes(ax0, panel_label="a")

    ax1 = fig.add_subplot(gs[0, 1])
    plot_strain_cell_morph(
        ax1,
        XYZ_DIR / "C60_strain_+0.0_N_doped_synergy.xyz",
        XYZ_DIR / "C60_strain_+5.0_N_doped_synergy.xyz",
    )
    finalize_axes(ax1, panel_label="b")

    ax = fig.add_subplot(gs[1, 0])
    shade_strain_response_physics(ax)
    for dop in ("pristine", *EXP5_DOPANTS):
        recs = grouped[dop]
        e0 = next(r["total_energy_Ha"] for r in recs if r["strain"] == 0.0)
        n_atoms = recs[0]["n_atoms"]
        strains, ys = [], []
        for r in recs:
            if dop == "P" and abs(r["strain"] - P_EXCLUDE_STRAIN) < 0.01:
                continue
            strains.append(r["strain"])
            ys.append((r["total_energy_Ha"] - e0) * HA_TO_MEV / n_atoms)
        label = "Pristine" if dop == "pristine" else dop
        style_line(ax, np.array(strains), np.array(ys), dop, label, linewidth=1.8, markersize=7)
    ax.axhline(0, color="#999999", linewidth=0.6, zorder=0)
    ax.set_xlabel(r"Biaxial strain $\varepsilon$ (\%)")
    ax.set_ylabel(r"$\Delta E/N_{\mathrm{atom}}$ (meV/atom)")
    ax.set_xlim(-5.8, 5.8)
    finalize_axes(ax, panel_label="c")
    origin_legend(ax, ncol=4, loc="upper center", bbox=(0.5, 1.22))

    ax = fig.add_subplot(gs[1, 1])
    keys = ("pristine", "B", "N", "P")
    labels = ["Pristine", "B", "N", "P"]
    alphas = [table1["systems"][k]["alpha_meV_per_pct"] for k in keys]
    y_pos = np.arange(len(labels))
    shade_alpha_physics(ax, y_pos, alphas)
    bars = ax.barh(y_pos, alphas, color=[get_color(k) for k in keys], edgecolor="#000", lw=0.9, height=0.62, zorder=3)
    ax.axvline(0, color="#000", linewidth=1.0)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.set_xlabel(r"$\alpha=\mathrm{d}E/\mathrm{d}\varepsilon$ (meV/\%)")
    for rect, a in zip(bars, alphas):
        ha = "left" if a >= 0 else "right"
        dx = 14 if a >= 0 else -14
        ax.text(a + dx, rect.get_y() + rect.get_height() / 2, f"{a:.1f}", va="center", ha=ha, fontsize=8, fontweight="bold")
    finalize_axes(ax, panel_label="d")

    fig.subplots_adjust(left=0.07, right=0.98, top=0.94, bottom=0.08)
    return save_figure(fig, out_dir / "figure1_strain_coupling.pdf")


def _waterfall_row(ax, dop: str, sdc: dict) -> None:
    row = next(r for r in sdc["synergy_energy_per_atom"] if r["n_molecules"] == 4 and r["dopant"] == dop)
    s_val = row["synergy_S"] * HA_TO_MEV
    vals = [
        row["strain_only_delta"] * HA_TO_MEV,
        row["doping_only_delta"] * HA_TO_MEV,
        s_val,
    ]
    xs = np.arange(3)
    labs = ["strain", "doping", r"$\mathcal{S}$"]
    colors = ["#BBBBBB", "#888888", get_color(dop)]
    ymax = max(abs(v) for v in vals) * 1.15
    for i, (lab, c, h) in enumerate(zip(labs, colors, vals)):
        if i < 2:
            ax.bar(i, h, color=c, edgecolor="#000", lw=0.8, width=0.55, zorder=3)
            ax.text(i, h + (8 if h >= 0 else -8), f"{h:+.0f}", ha="center", va="bottom" if h >= 0 else "top", fontsize=6, fontweight="bold")
        else:
            ax_in = ax.inset_axes([0.52, 0.08, 0.44, 0.82])
            ax_in.bar(0, h, color=c, edgecolor="#000", lw=0.8, width=0.55, zorder=3)
            ax_in.axhline(0, color="#000", lw=0.5)
            pad = max(abs(h) * 0.35, 2.0)
            ax_in.set_ylim(min(h - pad, -pad), max(h + pad, pad))
            ax_in.set_xticks([])
            ax_in.set_yticks([])
            for sp in ax_in.spines.values():
                sp.set_linewidth(0.8)
            ax_in.text(0, h + (0.4 if h >= 0 else -0.4), f"{h:+.2f}", ha="center", va="bottom" if h >= 0 else "top", fontsize=7, fontweight="bold")
            ax_in.set_title(r"$\mathcal{S}$ zoom", fontsize=6, pad=1)
            ax.bar(i, 0, color="none", edgecolor="none")
            ax.text(i, ymax * 0.05, r"$\mathcal{S}$", ha="center", fontsize=6.5)
    ax.axhline(0, color="#000", lw=0.6)
    ax.set_xticks(xs)
    ax.set_xticklabels(labs, fontsize=6.5)
    ax.set_ylim(-ymax * 0.05, ymax)
    ax.set_title(dop, fontsize=8, fontweight="bold", color=get_color(dop))


def figure2_synergy_combined(audit: dict, sdc: dict, out_dir: Path) -> Path:
    """Fig. 2: design-space triangle + S bars + scaling."""
    apply_nature_style()
    by_dop = _synergy_by_dopant(audit)
    fits = audit.get("size_scaling_fits", {})

    fig = plt.figure(figsize=(NATURE_DOUBLE_COL, NATURE_DOUBLE_COL * 0.82))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.15, 1.0], hspace=0.42, wspace=0.35)

    ax_tri = fig.add_subplot(gs[0, :])
    plot_synergy_design_triangle(ax_tri, sdc, highlight_n=TETRAMER_N)
    finalize_axes(ax_tri, panel_label="a")

    ax_bar = fig.add_subplot(gs[1, 0])
    rows = [r for r in audit["synergy_table"] if r["n_molecules"] == TETRAMER_N]
    rows.sort(key=lambda r: r["dopant"])
    labels = [r["dopant"] for r in rows]
    ss = [r["synergy_S_meV_per_atom"] for r in rows]
    x = np.arange(len(labels))
    ylo, yhi = min(ss) * 1.15, max(max(ss) * 1.35, 7.0)
    shade_synergy_physics(ax_bar, ylo, yhi)
    ax_bar.bar(x, ss, color=[get_color(d) for d in labels], edgecolor="#000", lw=0.9, width=0.58, zorder=3)
    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(labels)
    ax_bar.set_xlabel(r"Dopant at $n=4$")
    ax_bar.set_ylabel(r"$\mathcal{S}$ (meV/atom)")
    ax_bar.set_ylim(ylo, yhi)
    annotate_bar_values(ax_bar, x, ss, fontsize=8)
    finalize_axes(ax_bar, panel_label="b")

    ax_scale = fig.add_subplot(gs[1, 1:])
    ylo_b = min(r["synergy_S_meV_per_atom"] for r in audit["synergy_table"]) * 1.08
    yhi_b = max(r["synergy_S_meV_per_atom"] for r in audit["synergy_table"]) * 1.12
    shade_synergy_physics(ax_scale, ylo_b, max(yhi_b, 8.0))
    n_grid = np.linspace(1, 8, 80)
    for dop in ("B", "N", "P"):
        pts = by_dop[dop]
        ns = np.array([p["n_molecules"] for p in pts])
        sv = np.array([p["synergy_S_meV_per_atom"] for p in pts])
        style_line(ax_scale, ns, sv, dop, dop, linewidth=1.8, markersize=8, highlight_n=TETRAMER_N, x_arr=ns)
        fit = fits.get(dop)
        if fit:
            ax_scale.plot(n_grid, fit_curve_n(fit["S_infinity"], fit["A"], n_grid), color=get_color(dop), ls=(0, (3, 2)), lw=1.0, alpha=0.7)
    ax_scale.set_xlabel(r"Supercell size $n$")
    ax_scale.set_ylabel(r"$\mathcal{S}$ (meV/atom)")
    ax_scale.set_xticks([1, 2, 4, 6, 8])
    ax_scale.set_xlim(0.4, 8.6)
    ax_scale.set_ylim(ylo_b, max(yhi_b, 8.0))
    ax_scale.axvline(TETRAMER_N, color="#444", ls=(0, (2, 2)), lw=0.9)
    finalize_axes(ax_scale, panel_label="c")
    origin_legend(ax_scale, ncol=3, loc="lower right")

    fig.subplots_adjust(left=0.08, right=0.98, top=0.94, bottom=0.12)
    return save_figure(fig, out_dir / "figure2_synergy_combined.pdf")


def figure3_electronic_morphology(exp4: dict, out_dir: Path) -> Path:
    """Fig. 3: gap map, band edges, PDOS, dopant MOs, IPR."""
    apply_nature_style()
    pdos = load_exp7_pdos(PDOS_DIR)
    strains = [-5.0, 0.0, 5.0]
    strain_labs = [r"$-5$", r"$0$", r"$+5$"]
    dopants = ("pristine", "B", "N", "P")
    dop_labs = ["Pristine", "B", "N", "P"]

    fig = plt.figure(figsize=(NATURE_DOUBLE_COL, NATURE_DOUBLE_COL * 0.82))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.05], hspace=0.48, wspace=0.38)

    ax = fig.add_subplot(gs[0, 0])
    for dop in dopants:
        gaps = []
        for s in strains:
            r = records_for(pdos, dopant=dop, strain_pct=s, kind="C")
            gaps.append(r.gap_ev if r else np.nan)
        style_line(ax, np.array(strains), np.array(gaps), dop, dop if dop != "pristine" else "Pristine", linewidth=1.8, markersize=8)
    ax.set_xlabel(r"Biaxial strain $\varepsilon$ (\%)")
    ax.set_ylabel(r"HOMO–LUMO gap (eV)")
    ax.set_ylim(-0.05, 1.75)
    finalize_axes(ax, panel_label="a")
    origin_legend(ax, ncol=2, loc="upper center", bbox=(0.5, 1.22))

    ax = fig.add_subplot(gs[0, 1])
    gmat = gap_matrix(pdos, dopants, strains, kind="C")
    plot_gap_heatmap(ax, gmat, dop_labs, strain_labs, vmax=1.6)
    finalize_axes(ax, panel_label="b")

    ax = fig.add_subplot(gs[0, 2])
    inner = ax.inset_axes([0.0, 0.0, 1.0, 1.0])
    inner.axis("off")
    ax.axis("off")
    sub = inner.inset_axes([0.02, 0.08, 0.30, 0.84])
    r_n = records_for(pdos, dopant="N", strain_pct=0.0, kind="C")
    if r_n:
        plot_band_edge_morph(sub, r_n, color=get_color("N"), title=r"N, $\varepsilon=0$")
    sub2 = inner.inset_axes([0.36, 0.08, 0.30, 0.84])
    r_b = records_for(pdos, dopant="B", strain_pct=0.0, kind="C")
    if r_b:
        plot_band_edge_morph(sub2, r_b, color=get_color("B"), title=r"B, $\varepsilon=0$")
    sub3 = inner.inset_axes([0.70, 0.08, 0.28, 0.84])
    r_p = records_for(pdos, dopant="P", strain_pct=0.0, kind="C")
    if r_p:
        plot_band_edge_morph(sub3, r_p, color=get_color("P"), title=r"P, $\varepsilon=0$")
    ax.text(0.5, 1.02, r"Band-edge morph ($E_F=0$)", transform=ax.transAxes, ha="center", fontsize=8, fontweight="bold")
    finalize_axes(ax, panel_label="c")

    ax = fig.add_subplot(gs[1, 0])
    plot_pdos_deconvolution_xps(ax, pdos, dopant="N", strain_pct=5.0, e_min=-4.5, e_max=1.2)
    finalize_axes(ax, panel_label="d")

    ax = fig.add_subplot(gs[1, 1])
    plot_pdos_deconvolution_xps(ax, pdos, dopant="B", strain_pct=5.0, e_min=-4.5, e_max=1.2)
    finalize_axes(ax, panel_label="e")

    ax = fig.add_subplot(gs[1, 2])
    ipr0 = exp4["systems"]["pristine_0pct"]["IPR"]
    ipr1 = exp4["systems"]["coupled_B_3pct"]["IPR"]
    plot_ipr_localization_morph(ax, ipr0, ipr1)
    finalize_axes(ax, panel_label="f")

    fig.subplots_adjust(left=0.07, right=0.98, top=0.90, bottom=0.10)
    return save_figure(fig, out_dir / "figure3_electronic_morphology.pdf")


def main() -> int:
    out_dir = ROOT / "paper" / "figures" / "final_figures"
    exp5 = load_json(ROOT / "dft_results/exp_5_synergy/results/real_dft_results.json")
    table1 = load_json(ROOT / "experiments/analysis/table1_verification.json")
    audit = load_json(ROOT / "experiments/analysis/sdc/sdc_exp10_synergy_audit.json")
    sdc = load_json(ROOT / "experiments/analysis/sdc/sdc_exp10_results.json")
    exp4 = load_json(ROOT / "experiments/analysis/exp4_polaron_verification.json")

    p1 = figure1_strain_coupling(exp5, table1, out_dir)
    p2 = figure2_synergy_combined(audit, sdc, out_dir)
    p3 = figure3_electronic_morphology(exp4, out_dir)
    print(f"Wrote {p1}")
    print(f"Wrote {p2}")
    print(f"Wrote {p3}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
