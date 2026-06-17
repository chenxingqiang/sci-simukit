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

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from nature_style import (  # noqa: E402
    NATURE_ONE_HALF_COL,
    apply_nature_style,
    finalize_axes,
    get_color,
    get_marker,
    nature_legend,
    save_figure,
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
    n_atoms = records[0]["n_atoms"]
    strains, deltas = [], []
    for r in records:
        if r["dopant"] != dopant:
            continue
        d_meV = (r["total_energy_Ha"] - e0) * HA_TO_MEV / n_atoms
        strains.append(r["strain"])
        deltas.append(d_meV)
    return np.array(strains), np.array(deltas)


def formation_energy_ev_per_dopant(
    grouped: Dict[str, List[dict]], dopant: str, strain: float
) -> float:
    ed = next(r for r in grouped[dopant] if r["strain"] == strain)
    ep = next(r for r in grouped["pristine"] if r["strain"] == strain)
    return (ed["total_energy_Ha"] - ep["total_energy_Ha"]) * HA_TO_EV / N_DOPANTS_TETRAMER


def figure1_strain_doping(
    exp1: list,
    exp5: dict,
    out_dir: Path,
) -> Path:
    """Left panel of Fig. electronic_props: pristine size check + formation energy vs strain."""
    apply_nature_style()
    grouped = group_exp5(exp5)
    fig, axes = plt.subplots(1, 2, figsize=(NATURE_ONE_HALF_COL * 1.55, NATURE_ONE_HALF_COL * 0.72))

    ax = axes[0]
    exp1_sorted = sorted(exp1, key=lambda r: r["strain"])
    s_dimer = np.array([r["strain"] for r in exp1_sorted])
    y_dimer = np.array([r["relative_energy_meV"] for r in exp1_sorted]) / 120.0
    ax.plot(
        s_dimer,
        y_dimer,
        color="#7A7A7A",
        marker="o",
        linestyle="-",
        linewidth=0.8,
        markersize=4.5,
        markeredgecolor="#333333",
        markeredgewidth=0.4,
        label=r"Dimer ($120$ atoms)",
    )
    s_tet, y_tet = delta_e_per_atom_meV(grouped["pristine"], "pristine")
    ax.plot(
        s_tet,
        y_tet,
        color="#5B2C83",
        marker="s",
        linestyle="-",
        linewidth=0.8,
        markersize=4.5,
        markeredgecolor="#333333",
        markeredgewidth=0.4,
        label=r"Tetramer ($240$ atoms)",
    )
    ax.set_xlabel(r"Biaxial strain $\varepsilon$ (\%)")
    ax.set_ylabel(r"$\Delta E/N_{\mathrm{atom}}$ (meV/atom)")
    ax.set_xlim(-5.5, 5.5)
    finalize_axes(ax, panel_label="a")
    nature_legend(ax, ncol=1, loc="upper right")

    ax = axes[1]
    for dop in EXP5_DOPANTS:
        strains = []
        efs = []
        for r in grouped[dop]:
            ef = formation_energy_ev_per_dopant(grouped, dop, r["strain"])
            strains.append(r["strain"])
            efs.append(ef)
        ax.plot(
            strains,
            efs,
            color=get_color(dop),
            marker=get_marker(dop),
            linestyle="-",
            linewidth=0.8,
            markersize=4.5,
            markeredgecolor="#333333",
            markeredgewidth=0.4,
            label=f"{dop}-doped",
        )
    ax.set_xlabel(r"Biaxial strain $\varepsilon$ (\%)")
    ax.set_ylabel(r"$E_f$ (eV/dopant)")
    ax.set_xlim(-5.5, 5.5)
    finalize_axes(ax, panel_label="b")
    nature_legend(ax, ncol=1, loc="best")

    fig.subplots_adjust(wspace=0.38, top=0.92, bottom=0.18, left=0.11, right=0.98)
    return save_figure(fig, out_dir / "figure1_strain_doping.pdf")


def figure2_coupling_summary(exp5: dict, table1: dict, out_dir: Path) -> Path:
    """Right panel of Fig. electronic_props: ΔE from 0% + α bar chart."""
    apply_nature_style()
    grouped = group_exp5(exp5)
    fig, axes = plt.subplots(1, 2, figsize=(NATURE_ONE_HALF_COL * 1.55, NATURE_ONE_HALF_COL * 0.72))

    ax = axes[0]
    systems = ["pristine", *EXP5_DOPANTS]
    for dop in systems:
        recs = grouped[dop]
        e0 = next(r["total_energy_Ha"] for r in recs if r["strain"] == 0.0)
        strains, deltas = [], []
        for r in recs:
            if dop == "P" and abs(r["strain"] - P_EXCLUDE_STRAIN) < 0.01:
                continue
            d = (r["total_energy_Ha"] - e0) * HA_TO_MEV
            strains.append(r["strain"])
            deltas.append(d)
        ax.plot(
            strains,
            deltas,
            color=get_color(dop),
            marker=get_marker(dop),
            linestyle="-",
            linewidth=0.8,
            markersize=4.5,
            markeredgecolor="#333333",
            markeredgewidth=0.4,
            label="Pristine" if dop == "pristine" else f"{dop}",
        )
    ax.set_xlabel(r"Biaxial strain $\varepsilon$ (\%)")
    ax.set_ylabel(r"$\Delta E$ from $\varepsilon=0$ (meV)")
    ax.set_xlim(-5.5, 5.5)
    finalize_axes(ax, panel_label="a")
    nature_legend(ax, ncol=2, loc="upper left")

    ax = axes[1]
    labels = []
    alphas = []
    colors = []
    for key in ("pristine", "B", "N", "P"):
        sysd = table1["systems"][key]
        labels.append("Pristine" if key == "pristine" else key)
        alphas.append(sysd["alpha_meV_per_pct"])
        colors.append(get_color(key))
    x = np.arange(len(labels))
    ax.bar(x, alphas, color=colors, edgecolor="#333333", linewidth=0.4, width=0.65, zorder=3)
    ax.axhline(0, color="#333333", linewidth=0.6, zorder=2)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel(r"$\alpha = \mathrm{d}E/\mathrm{d}\varepsilon$ (meV/\%)")
    finalize_axes(ax, panel_label="b")

    fig.subplots_adjust(wspace=0.38, top=0.92, bottom=0.18, left=0.11, right=0.98)
    return save_figure(fig, out_dir / "figure2_synergy.pdf")



def figure4_exp4_polaron(audit: dict, out_dir: Path) -> Path:
    """Two-point Exp4 IPR and J (verified audit JSON only)."""
    apply_nature_style()
    fig, axes = plt.subplots(1, 2, figsize=(NATURE_ONE_HALF_COL * 1.05, NATURE_ONE_HALF_COL * 0.62))
    labels = ["Pristine\n(0%)", "B +3%"]
    keys = ("pristine_0pct", "coupled_B_3pct")
    iprs = [audit["systems"][k]["IPR"] for k in keys]
    js = [audit["systems"][k]["J_meV"] for k in keys]
    colors = [get_color("pristine"), get_color("B")]

    ax = axes[0]
    x = np.arange(2)
    ax.bar(x, iprs, color=colors, edgecolor="#333333", linewidth=0.4, width=0.55, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("IPR")
    finalize_axes(ax, panel_label="a")

    ax = axes[1]
    ax.bar(x, js, color=colors, edgecolor="#333333", linewidth=0.4, width=0.55, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel(r"$J$ (meV)")
    finalize_axes(ax, panel_label="b")

    fig.subplots_adjust(wspace=0.42, top=0.92, bottom=0.22, left=0.14, right=0.96)
    return save_figure(fig, out_dir / "figure4_exp4_polaron.pdf")


def copy_sdc_pending(sdc_fig: Path, pending_dir: Path) -> None:
    if not sdc_fig.exists():
        return
    pending_dir.mkdir(parents=True, exist_ok=True)
    for ext in (".pdf", ".png"):
        src = sdc_fig.with_suffix(ext)
        if src.exists():
            dst = pending_dir / src.name
            dst.write_bytes(src.read_bytes())


def main() -> int:
    out_dir = ROOT / "paper" / "figures" / "final_figures"
    exp1 = load_json(ROOT / "dft_results/exp_1_structure/results/real_dft_results.json")
    exp5 = load_json(ROOT / "dft_results/exp_5_synergy/results/real_dft_results.json")
    table1 = load_json(ROOT / "experiments/analysis/table1_verification.json")
    exp4 = load_json(ROOT / "experiments/analysis/exp4_polaron_verification.json")

    p1 = figure1_strain_doping(exp1, exp5, out_dir)
    p2 = figure2_coupling_summary(exp5, table1, out_dir)
    p4 = figure4_exp4_polaron(exp4, out_dir)
    print(f"Wrote {p1}")
    print(f"Wrote {p2}")
    print(f"Wrote {p4}")

    sdc_fig = ROOT / "experiments/analysis/sdc/figures/sdc_synergy_vs_size_eps3pct_epa.pdf"
    copy_sdc_pending(sdc_fig, ROOT / "paper/figures/pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
