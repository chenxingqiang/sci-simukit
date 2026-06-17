#!/usr/bin/env python3
"""Generate main-text figures for strain_doped_graphullerene.tex from verified JSON."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from nature_style import (  # noqa: E402
    NATURE_DOUBLE_COL,
    NATURE_ONE_HALF_COL,
    add_reference_line,
    annotate_bar_values,
    apply_nature_style,
    finalize_axes,
    get_color,
    get_marker,
    nature_legend,
    save_figure,
    style_line,
)

HA_TO_EV = 27.211386245988
HA_TO_MEV = HA_TO_EV * 1000.0
N_DOPANTS_TETRAMER = 4
EXP5_DOPANTS = ("B", "N", "P")
P_EXCLUDE_STRAIN = 2.5  # metastable point; excluded from alpha fit only


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


def delta_e_per_atom_meV(records: List[dict], dopant: str) -> Tuple[np.ndarray, np.ndarray]:
    e0 = next(r["total_energy_Ha"] for r in records if r["dopant"] == dopant and r["strain"] == 0.0)
    strains, deltas = [], []
    for r in records:
        if r["dopant"] != dopant:
            continue
        d_meV = (r["total_energy_Ha"] - e0) * HA_TO_MEV / r["n_atoms"]
        strains.append(r["strain"])
        deltas.append(d_meV)
    return np.array(strains), np.array(deltas)


def formation_energy_ev_per_dopant(
    grouped: Dict[str, List[dict]], dopant: str, strain: float
) -> float:
    ed = next(r for r in grouped[dopant] if r["strain"] == strain)
    ep = next(r for r in grouped["pristine"] if r["strain"] == strain)
    return (ed["total_energy_Ha"] - ep["total_energy_Ha"]) * HA_TO_EV / N_DOPANTS_TETRAMER


def _panel_pristine_size(ax, exp1: list, grouped: Dict[str, List[dict]]) -> None:
    exp1_sorted = sorted(exp1, key=lambda r: r["strain"])
    s_dimer = np.array([r["strain"] for r in exp1_sorted])
    y_dimer = np.array([r["relative_energy_meV"] for r in exp1_sorted]) / 120.0
    style_line(ax, s_dimer, y_dimer, "pristine", r"Dimer ($120$ atoms)")
    s_tet, y_tet = delta_e_per_atom_meV(grouped["pristine"], "pristine")
    style_line(ax, s_tet, y_tet, "N", r"Tetramer ($240$ atoms)")
    add_reference_line(ax, 0.0, r"$\Delta E/N=0$", color="#888888", linestyle=":")
    ax.set_xlabel(r"Biaxial strain $\varepsilon$ (\%)")
    ax.set_ylabel(r"$\Delta E/N_{\mathrm{atom}}$ (meV/atom)")
    ax.set_xlim(-5.5, 5.5)
    finalize_axes(ax, panel_label="a")
    nature_legend(ax, ncol=1, loc="upper right")


def _panel_substitution_energy(ax, grouped: Dict[str, List[dict]]) -> None:
    for dop in EXP5_DOPANTS:
        strains, efs = [], []
        for r in grouped[dop]:
            strains.append(r["strain"])
            efs.append(formation_energy_ev_per_dopant(grouped, dop, r["strain"]))
        style_line(ax, np.array(strains), np.array(efs), dop, f"{dop}-doped")
    add_reference_line(ax, 0.0, r"$E_f=0$", color="#888888", linestyle=":")
    ax.set_xlabel(r"Biaxial strain $\varepsilon$ (\%)")
    ax.set_ylabel(r"$E_f$ (eV/dopant)")
    ax.set_xlim(-5.5, 5.5)
    finalize_axes(ax, panel_label="b")
    nature_legend(ax, ncol=1, loc="best")


def _panel_delta_e(ax, grouped: Dict[str, List[dict]]) -> None:
    for dop in ["pristine", *EXP5_DOPANTS]:
        recs = grouped[dop]
        e0 = next(r["total_energy_Ha"] for r in recs if r["strain"] == 0.0)
        strains, deltas = [], []
        for r in recs:
            if dop == "P" and abs(r["strain"] - P_EXCLUDE_STRAIN) < 0.01:
                continue
            strains.append(r["strain"])
            deltas.append((r["total_energy_Ha"] - e0) * HA_TO_MEV)
        label = "Pristine" if dop == "pristine" else dop
        style_line(ax, np.array(strains), np.array(deltas), dop, label)
    add_reference_line(ax, 0.0, r"$\Delta E=0$", color="#888888", linestyle=":")
    ax.set_xlabel(r"Biaxial strain $\varepsilon$ (\%)")
    ax.set_ylabel(r"$\Delta E$ from $\varepsilon=0$ (meV)")
    ax.set_xlim(-5.5, 5.5)
    finalize_axes(ax, panel_label="c")
    nature_legend(ax, ncol=2, loc="upper left")


def _panel_alpha(ax, table1: dict) -> None:
    keys = ("pristine", "B", "N", "P")
    labels = ["Pristine", "B", "N", "P"]
    alphas = [table1["systems"][k]["alpha_meV_per_pct"] for k in keys]
    colors = [get_color(k) for k in keys]
    x = np.arange(len(labels))
    bars = ax.bar(x, alphas, color=colors, edgecolor="#333333", linewidth=0.45, width=0.62, zorder=3)
    ax.axhline(0, color="#333333", linewidth=0.6, zorder=2)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel(r"$\alpha = \mathrm{d}E/\mathrm{d}\varepsilon$ (meV/\%)")
    annotate_bar_values(ax, x, alphas, fmt="{:.1f}")
    # Inset: pristine |α| on magnified scale
    inset = ax.inset_axes([0.06, 0.52, 0.28, 0.42])
    inset.bar([0], [abs(alphas[0])], color=colors[0], edgecolor="#333333", linewidth=0.4, width=0.5)
    inset.set_xticks([0])
    inset.set_xticklabels(["Pristine"], fontsize=5)
    inset.set_ylabel(r"$|\alpha|$", fontsize=5)
    inset.tick_params(labelsize=5)
    inset.set_title(r"$|\alpha_{\mathrm{pr}}| \approx 1$ meV/\%", fontsize=5, pad=2)
    for spine in inset.spines.values():
        spine.set_linewidth(0.5)
    finalize_axes(ax, panel_label="d")


def figure_main_exp5(exp1: list, exp5: dict, table1: dict, out_dir: Path) -> Path:
    """2×2 composite Exp.5 figure (Nature double-column width)."""
    apply_nature_style()
    grouped = group_exp5(exp5)
    fig = plt.figure(figsize=(NATURE_DOUBLE_COL, NATURE_DOUBLE_COL * 0.62))
    gs = GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.38, left=0.09, right=0.98, top=0.97, bottom=0.11)
    _panel_pristine_size(fig.add_subplot(gs[0, 0]), exp1, grouped)
    _panel_substitution_energy(fig.add_subplot(gs[0, 1]), grouped)
    _panel_delta_e(fig.add_subplot(gs[1, 0]), grouped)
    _panel_alpha(fig.add_subplot(gs[1, 1]), table1)
    return save_figure(fig, out_dir / "figure_main_exp5.pdf")


def figure1_strain_doping(exp1: list, exp5: dict, out_dir: Path) -> Path:
    apply_nature_style()
    grouped = group_exp5(exp5)
    fig, axes = plt.subplots(1, 2, figsize=(NATURE_ONE_HALF_COL * 1.55, NATURE_ONE_HALF_COL * 0.76))
    _panel_pristine_size(axes[0], exp1, grouped)
    _panel_substitution_energy(axes[1], grouped)
    fig.subplots_adjust(wspace=0.38, top=0.92, bottom=0.18, left=0.11, right=0.98)
    return save_figure(fig, out_dir / "figure1_strain_doping.pdf")


def figure2_coupling_summary(exp5: dict, table1: dict, out_dir: Path) -> Path:
    apply_nature_style()
    grouped = group_exp5(exp5)
    fig, axes = plt.subplots(1, 2, figsize=(NATURE_ONE_HALF_COL * 1.55, NATURE_ONE_HALF_COL * 0.76))
    _panel_delta_e(axes[0], grouped)
    _panel_alpha(axes[1], table1)
    fig.subplots_adjust(wspace=0.38, top=0.92, bottom=0.18, left=0.11, right=0.98)
    return save_figure(fig, out_dir / "figure2_synergy.pdf")


def figure3_sdc_scaling(audit: dict, out_dir: Path) -> Path:
    """Synergy S(n) at +3% strain with 1/n extrapolation and N sign-flip marker."""
    apply_nature_style()
    rows = audit["synergy_table"]
    by_dop: Dict[str, List[dict]] = defaultdict(list)
    for row in rows:
        by_dop[row["dopant"]].append(row)

    fig, ax = plt.subplots(figsize=(NATURE_DOUBLE_COL * 0.52, NATURE_DOUBLE_COL * 0.44))
    ax.axhspan(-2.5, 2.5, color="#F0F0F0", alpha=0.55, zorder=0)

    for dop in sorted(by_dop):
        pts = sorted(by_dop[dop], key=lambda r: r["n_molecules"])
        ns = np.array([p["n_molecules"] for p in pts], dtype=float)
        ss = np.array([p["synergy_S_meV_per_atom"] for p in pts])
        color = get_color(dop)
        marker = get_marker(dop)

        ax.plot(
            ns,
            ss,
            linestyle="none",
            marker=marker,
            markersize=6.0,
            color=color,
            markerfacecolor=color,
            markeredgecolor="#333333",
            markeredgewidth=0.45,
            zorder=4,
        )

        s_inf = None
        if len(ns) >= 3:
            inv_n = 1.0 / ns
            slope, intercept = np.polyfit(inv_n, ss, 1)
            s_inf = intercept
            n_line = np.linspace(ns.min(), ns.max() + 0.8, 80)
            s_line = slope / n_line + intercept
            ax.plot(n_line, s_line, "--", color=color, linewidth=0.85, alpha=0.9, zorder=2)
            leg = rf"{dop} ($\mathcal{{S}}_\infty \approx {s_inf:.2f}$ meV/atom)"
        else:
            leg = dop
        ax.plot([], [], linestyle="none", marker=marker, color=color, label=leg)

        if dop == "N" and any(p["n_molecules"] == 8 for p in pts):
            n8 = next(p for p in pts if p["n_molecules"] == 8)
            ax.annotate(
                "sign flip",
                xy=(8, n8["synergy_S_meV_per_atom"]),
                xytext=(6.2, -9.5),
                fontsize=5.5,
                arrowprops=dict(arrowstyle="->", color="#333333", lw=0.6),
                color="#333333",
            )

    add_reference_line(ax, 0.0, r"Additive ($\mathcal{S}=0$)", color="#333333", linestyle="--")
    ax.set_xlabel(r"Supercell size $n$ ($n \times \mathrm{C}_{60}$)")
    ax.set_ylabel(r"Synergy $\mathcal{S}$ (meV/atom)")
    ax.set_xticks(sorted({r["n_molecules"] for r in rows}))
    finalize_axes(ax, panel_label="")
    nature_legend(ax, ncol=1, loc="upper right")
    fig.subplots_adjust(top=0.90, bottom=0.16, left=0.14, right=0.96)
    return save_figure(fig, out_dir / "figure3_sdc_scaling.pdf")


def figure4_exp4_polaron(audit: dict, out_dir: Path) -> Path:
    """Exp4 IPR/J with value labels and relative change annotation."""
    apply_nature_style()
    keys = ("pristine_0pct", "coupled_B_3pct")
    labels = ["Pristine\n(0%)", "B +3%"]
    iprs = [audit["systems"][k]["IPR"] for k in keys]
    js = [audit["systems"][k]["J_meV"] for k in keys]
    colors = [get_color("pristine"), get_color("B")]

    fig, axes = plt.subplots(1, 2, figsize=(NATURE_DOUBLE_COL * 0.55, NATURE_DOUBLE_COL * 0.28))
    x = np.arange(2)

    ax = axes[0]
    ax.bar(x, iprs, color=colors, edgecolor="#333333", linewidth=0.45, width=0.55, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("IPR")
    annotate_bar_values(ax, x, iprs, fmt="{:.0f}")
    pct_ipr = 100.0 * (iprs[1] - iprs[0]) / iprs[0]
    ax.annotate(f"{pct_ipr:.0f}%", xy=(0.5, max(iprs) * 0.55), ha="center", fontsize=6, color="#555555")
    finalize_axes(ax, panel_label="a")

    ax = axes[1]
    ax.bar(x, js, color=colors, edgecolor="#333333", linewidth=0.45, width=0.55, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel(r"$J$ (meV)")
    annotate_bar_values(ax, x, js, fmt="{:.1f}")
    pct_j = 100.0 * (js[1] - js[0]) / js[0]
    ax.annotate(f"+{pct_j:.0f}%", xy=(0.5, max(js) * 0.55), ha="center", fontsize=6, color="#555555")
    finalize_axes(ax, panel_label="b")

    fig.subplots_adjust(wspace=0.35, top=0.92, bottom=0.22, left=0.10, right=0.98)
    return save_figure(fig, out_dir / "figure4_exp4_polaron.pdf")


def main() -> int:
    out_dir = ROOT / "paper" / "figures" / "final_figures"
    exp1 = load_json(ROOT / "dft_results/exp_1_structure/results/real_dft_results.json")
    exp5 = load_json(ROOT / "dft_results/exp_5_synergy/results/real_dft_results.json")
    table1 = load_json(ROOT / "experiments/analysis/table1_verification.json")
    exp4 = load_json(ROOT / "experiments/analysis/exp4_polaron_verification.json")
    audit = load_json(ROOT / "experiments/analysis/sdc/sdc_exp10_synergy_audit.json")

    outputs = [
        figure_main_exp5(exp1, exp5, table1, out_dir),
        figure1_strain_doping(exp1, exp5, out_dir),
        figure2_coupling_summary(exp5, table1, out_dir),
        figure3_sdc_scaling(audit, out_dir),
        figure4_exp4_polaron(exp4, out_dir),
    ]
    for p in outputs:
        print(f"Wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
