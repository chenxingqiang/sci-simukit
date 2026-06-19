#!/usr/bin/env python3
"""Fig. S6 — Exp.4 J audit + synthetic FCWD envelope (MolFC pending)."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

FIG_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(FIG_DIR))

from _load_audit import load_json
from _style import COLOR_CBM, COLOR_VBM, DOPANT_COLORS, apply_si_style, panel_label, style_axes


def build(out_dir: Path) -> tuple[Path, Path]:
    apply_si_style()
    exp4 = load_json("experiments/analysis/exp4_polaron_verification.json")
    sys_map = exp4["systems"]

    fig = plt.figure(figsize=(6.5, 2.05))
    gs = GridSpec(1, 2, figure=fig, width_ratios=[1.15, 1.05], wspace=0.42)
    ax_j = fig.add_subplot(gs[0, 0])
    ax_f = fig.add_subplot(gs[0, 1])

    keys = [
        ("pristine_0pct", "pristine\n$\\epsilon{=}0$"),
        ("pristine_3pct", "pristine\n$\\epsilon{=}+3$\\%"),
        ("B_0pct", "B\n$\\epsilon{=}0$"),
        ("coupled_B_3pct", "B\n$\\epsilon{=}+3$\\%"),
    ]
    j_vals = [sys_map[k]["J_meV"] for k, _ in keys]
    colors = [
        DOPANT_COLORS["pristine"],
        DOPANT_COLORS["pristine"],
        COLOR_CBM,
        COLOR_CBM,
    ]
    x = np.arange(len(keys))
    ax_j.bar(x, j_vals, color=colors, width=0.55, edgecolor="none")
    ax_j.set_xticks(x)
    ax_j.set_xticklabels([lab for _, lab in keys], fontsize=5.5)
    ax_j.set_ylabel(r"$J$ (meV)")
    ax_j.set_ylim(0, max(j_vals) * 1.28)
    style_axes(ax_j, grid=True)
    for i, v in enumerate(j_vals):
        ax_j.text(i, v + 1.0, f"{v:.1f}", ha="center", va="bottom", fontsize=5.5)
    ax_j.text(0.98, 0.95, "Exp.4", transform=ax_j.transAxes, ha="right", va="top", fontsize=5, color="#666666")

    # Illustrative FCWD envelope (Capobianco2024 vocabulary; not DFT modes)
    q = np.linspace(-2.5, 2.5, 300)
    vdw = np.exp(-0.5 * (q / 0.85) ** 2)
    qhp = np.exp(-0.5 * ((q - 0.15) / 0.55) ** 2)
    ax_f.fill_between(q, 0, vdw, color="#AAAAAA", alpha=0.35, lw=0)
    ax_f.plot(q, vdw, color="#666666", lw=0.75, label="vdW C$_{60}$ [lit.]")
    ax_f.fill_between(q, 0, qhp, color=COLOR_CBM, alpha=0.25, lw=0)
    ax_f.plot(q, qhp, color=COLOR_CBM, lw=0.85, label="qHP C$_{60}$ [lit.]")
    ax_f.set_xlabel(r"mode coordinate $Q$ (a.u.)")
    ax_f.set_ylabel("FCWD (a.u.)")
    ax_f.set_xlim(-2.5, 2.5)
    ax_f.set_ylim(0, 1.15)
    style_axes(ax_f)
    ax_f.legend(frameon=False, fontsize=5, loc="upper right")
    ax_f.text(
        0.02,
        0.06,
        "[synthetic; MolFC pending]",
        transform=ax_f.transAxes,
        fontsize=5,
        color="#888888",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#CCCCCC", alpha=0.9),
    )

    panel_label(ax_j, "S6")
    ax_j.text(0.03, 0.78, "(a)", transform=ax_j.transAxes, fontsize=6, fontweight="bold")
    ax_f.text(0.03, 0.78, "(b)", transform=ax_f.transAxes, fontsize=6, fontweight="bold")

    fig.subplots_adjust(left=0.10, right=0.98, top=0.92, bottom=0.22)

    out_dir.mkdir(parents=True, exist_ok=True)
    pdf = out_dir / "figure_s6_j_exp4.pdf"
    png = out_dir / "figure_s6_j_exp4.png"
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.04)
    fig.savefig(png, bbox_inches="tight", pad_inches=0.04, dpi=300)
    plt.close(fig)
    return pdf, png


if __name__ == "__main__":
    pdf, png = build(FIG_DIR / "out")
    print(f"Wrote {pdf}\nWrote {png}")
