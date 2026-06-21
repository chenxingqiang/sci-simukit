#!/usr/bin/env python3
"""Fig. S3 — tetramer dimer nearest-neighbor coupling J (PBE+D3)."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

FIG_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(FIG_DIR))

from _load_audit import load_json
from _style import COLOR_CBM, DOPANT_COLORS, apply_si_style, panel_label, style_axes


def build(out_dir: Path) -> tuple[Path, Path]:
    apply_si_style()
    exp4 = load_json("experiments/analysis/exp4_polaron_verification.json")
    sys_map = exp4["systems"]

    fig, ax_j = plt.subplots(figsize=(3.6, 2.2))

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

    panel_label(ax_j, "S3")
    fig.subplots_adjust(left=0.14, right=0.98, top=0.92, bottom=0.28)

    out_dir.mkdir(parents=True, exist_ok=True)
    pdf = out_dir / "figure_s3_j_exp4.pdf"
    png = out_dir / "figure_s3_j_exp4.png"
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.04)
    fig.savefig(png, bbox_inches="tight", pad_inches=0.04, dpi=300)
    plt.close(fig)
    return pdf, png


if __name__ == "__main__":
    pdf, png = build(FIG_DIR / "out")
    print(f"Wrote {pdf}\nWrote {png}")
