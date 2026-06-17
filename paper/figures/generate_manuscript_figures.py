#!/usr/bin/env python3
"""Main-text figures: two panels only, verified JSON sources."""

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
    apply_nature_style,
    finalize_axes,
    get_color,
    nature_legend,
    save_figure,
    style_line,
)

HA_TO_MEV = 27.211386245988 * 1000.0
EXP5_DOPANTS = ("B", "N", "P")
P_EXCLUDE_STRAIN = 2.5


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


def figure3_synergy_tetramer(audit: dict, out_dir: Path) -> Path:
    """Fig. 3: S at n=4 (+3%) — direct proof additive strain+doping sum fails."""
    apply_nature_style()
    rows = [r for r in audit["synergy_table"] if r["n_molecules"] == 4]
    rows.sort(key=lambda r: r["dopant"])
    labels = [r["dopant"] for r in rows]
    ss = [r["synergy_S_meV_per_atom"] for r in rows]
    colors = [get_color(d) for d in labels]

    fig, ax = plt.subplots(figsize=(NATURE_DOUBLE_COL * 0.38, NATURE_DOUBLE_COL * 0.36))
    x = np.arange(len(labels))
    ax.bar(x, ss, color=colors, edgecolor="#333333", linewidth=0.45, width=0.6, zorder=3)
    ax.axhline(0, color="#333333", linestyle="--", linewidth=0.7, zorder=1)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel(r"$\mathcal{S}$ (meV/atom) at $+3$\% strain")
    ax.set_xlabel(r"Dopant ($n=4 \times \mathrm{C}_{60}$, tetramer scale)")
    for xi, s in zip(x, ss):
        va = "bottom" if s >= 0 else "top"
        dy = 1.2 if s >= 0 else -1.2
        ax.text(xi, s + dy, f"{s:+.1f}", ha="center", va=va, fontsize=6.5)
    finalize_axes(ax)
    fig.subplots_adjust(left=0.18, right=0.96, top=0.92, bottom=0.22)
    return save_figure(fig, out_dir / "figure3_synergy_tetramer.pdf")


def figure1_strain_coupling(exp5: dict, table1: dict, out_dir: Path) -> Path:
    """Fig. 1: (a) strain response ΔE/N; (b) strain sensitivity α."""
    apply_nature_style()
    grouped = group_exp5(exp5)
    fig, axes = plt.subplots(
        1, 2, figsize=(NATURE_DOUBLE_COL, NATURE_DOUBLE_COL * 0.36)
    )

    ax = axes[0]
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
        style_line(ax, np.array(strains), np.array(ys), dop, label)
    ax.axhline(0, color="#CCCCCC", linewidth=0.5, zorder=0)
    ax.set_xlabel(r"Biaxial strain $\varepsilon$ (\%)")
    ax.set_ylabel(r"$\Delta E/N_{\mathrm{atom}}$ (meV/atom, rel.\ $\varepsilon=0$)")
    ax.set_xlim(-5.5, 5.5)
    finalize_axes(ax, panel_label="a")
    nature_legend(ax, ncol=2, loc="upper left")
    ax.text(
        0.03,
        0.97,
        r"Opposite $\alpha$: N stabilizes, B destabilizes under tension",
        transform=ax.transAxes,
        fontsize=5.5,
        va="top",
        ha="left",
        color="#333333",
    )

    ax = axes[1]
    keys = ("pristine", "B", "N", "P")
    labels = ["Pristine", "B", "N", "P"]
    alphas = [table1["systems"][k]["alpha_meV_per_pct"] for k in keys]
    y_pos = np.arange(len(labels))
    colors = [get_color(k) for k in keys]
    ax.barh(y_pos, alphas, color=colors, edgecolor="#333333", linewidth=0.4, height=0.55)
    ax.axvline(0, color="#333333", linewidth=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.set_xlabel(r"$\alpha = \mathrm{d}E/\mathrm{d}\varepsilon$ (meV/\%)")
    for i, a in enumerate(alphas):
        ha = "left" if a >= 0 else "right"
        dx = 8 if a >= 0 else -8
        ax.text(a + dx, i, f"{a:.1f}", va="center", ha=ha, fontsize=6)
    finalize_axes(ax, panel_label="b")

    fig.subplots_adjust(wspace=0.45, left=0.09, right=0.98, top=0.88, bottom=0.20)
    return save_figure(fig, out_dir / "figure1_strain_coupling.pdf")


def figure2_sdc_scaling(audit: dict, out_dir: Path) -> Path:
    """Fig. 2: synergy S(n) at +3% — data points and additive reference only."""
    apply_nature_style()
    rows = audit["synergy_table"]
    by_dop: Dict[str, List[dict]] = defaultdict(list)
    for row in rows:
        by_dop[row["dopant"]].append(row)

    fig, ax = plt.subplots(figsize=(NATURE_DOUBLE_COL * 0.48, NATURE_DOUBLE_COL * 0.38))
    for dop in ("B", "N", "P"):
        pts = sorted(by_dop[dop], key=lambda r: r["n_molecules"])
        ns = [p["n_molecules"] for p in pts]
        ss = [p["synergy_S_meV_per_atom"] for p in pts]
        style_line(ax, np.array(ns), np.array(ss), dop, dop)

    ax.axhline(0, color="#333333", linestyle="--", linewidth=0.7, label=r"$\mathcal{S}=0$ (additive)")
    ax.set_xlabel(r"Supercell size $n$ ($n \times \mathrm{C}_{60}$)")
    ax.set_ylabel(r"$\mathcal{S}$ (meV/atom) at $+3$\% strain")
    ax.set_xticks(sorted({r["n_molecules"] for r in rows}))
    finalize_axes(ax)
    nature_legend(ax, ncol=2, loc="best")
    fig.subplots_adjust(left=0.16, right=0.97, top=0.90, bottom=0.18)
    return save_figure(fig, out_dir / "figure2_sdc_scaling.pdf")


def main() -> int:
    out_dir = ROOT / "paper" / "figures" / "final_figures"
    exp5 = load_json(ROOT / "dft_results/exp_5_synergy/results/real_dft_results.json")
    table1 = load_json(ROOT / "experiments/analysis/table1_verification.json")
    audit = load_json(ROOT / "experiments/analysis/sdc/sdc_exp10_synergy_audit.json")

    p1 = figure1_strain_coupling(exp5, table1, out_dir)
    p2 = figure2_sdc_scaling(audit, out_dir)
    p3 = figure3_synergy_tetramer(audit, out_dir)
    print(f"Wrote {p1}")
    print(f"Wrote {p2}")
    print(f"Wrote {p3}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
