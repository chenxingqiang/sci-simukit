#!/usr/bin/env python3
"""Fig. S6 — Exp.4 verified J audit (two-point; FCWD pending MolFC)."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

FIG_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(FIG_DIR))

from _load_audit import load_json
from _style import COLOR_CBM, DOPANT_COLORS, apply_prl_style, panel_label, style_axes


def build(out_dir: Path) -> tuple[Path, Path]:
    apply_prl_style()
    exp4 = load_json("experiments/analysis/exp4_polaron_verification.json")
    p = exp4["systems"]["pristine_0pct"]
    b = exp4["systems"]["coupled_B_3pct"]

    labels = ["pristine\n$\\epsilon{=}0$", "B @\n$\\epsilon{=}+3$\\%"]
    j_vals = [p["J_meV"], b["J_meV"]]
    colors = [DOPANT_COLORS["pristine"], COLOR_CBM]

    fig, ax = plt.subplots(figsize=(2.2, 1.6))
    x = np.arange(len(labels))
    ax.bar(x, j_vals, color=colors, width=0.55, edgecolor="none")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=6)
    ax.set_ylabel(r"$J$ (meV)")
    ax.set_ylim(0, max(j_vals) * 1.25)
    style_axes(ax, grid=True)
    for i, v in enumerate(j_vals):
        ax.text(i, v + 1.2, f"{v:.1f}", ha="center", va="bottom", fontsize=5.5)
    ax.text(0.98, 0.95, "Exp.4 audit", transform=ax.transAxes, ha="right", va="top", fontsize=5, color="#666666")
    panel_label(ax, "S6")
    fig.text(0.5, 0.02, "[FCWD panel pending MolFC]", ha="center", fontsize=5, color="#888888")

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
