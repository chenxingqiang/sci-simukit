#!/usr/bin/env python3
"""Fig. S4 — Exp.7 pi-DOS tetramer panel @ epsilon=0 (Electron purple/teal)."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

FIG_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(FIG_DIR))

from _pdos import gaussian_dos, parse_pdos
from _style import COLOR_CBM, COLOR_TOTAL, COLOR_VBM, apply_si_style, panel_label, style_axes


def _plot_dos(ax, pdos_path: Path, title: str, *, dos=None, ymax: float | None = None) -> None:
    series = parse_pdos(pdos_path)
    grid = np.linspace(-2.5, 2.5, 400)
    if dos is None:
        dos = gaussian_dos(series.energy_ev, series.pi_weight, grid, sigma_ev=0.07)
    valence = grid <= 0
    conduction = grid >= 0
    ax.fill_between(grid, 0, dos, where=valence, color=COLOR_VBM, alpha=0.85, lw=0)
    ax.fill_between(grid, 0, dos, where=conduction, color=COLOR_CBM, alpha=0.85, lw=0)
    ax.plot(grid, dos, color=COLOR_TOTAL, lw=0.55, alpha=0.55)
    ax.axvline(0, color="#333333", lw=0.55)
    ymax = ymax if ymax is not None else dos.max() * 1.15
    ax.text(
        0.97,
        0.94,
        title,
        transform=ax.transAxes,
        fontsize=6.5,
        va="top",
        ha="right",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.9),
    )
    ax.text(-1.95, ymax * 0.82, "VBM", fontsize=6, color=COLOR_VBM, ha="left", va="top")
    ax.text(0.22, ymax * 0.82, "CBM", fontsize=6, color=COLOR_CBM, ha="left", va="top")
    ax.set_xlim(-2.0, 2.0)
    ax.set_ylim(0, ymax)
    ax.set_xlabel("energy (eV)")
    style_axes(ax)


def build(out_dir: Path) -> tuple[Path, Path]:
    apply_si_style()
    root = FIG_DIR.parents[1]
    base = root / "dft_results/exp_7_electronic_structure/outputs"
    panels = [
        ("pristine", base / "elec_pos0p0_pristine-k1-1.pdos"),
        ("B", base / "elec_pos0p0_B-k1-1.pdos"),
        ("N", base / "elec_pos0p0_N-k1-1.pdos"),
        ("P", base / "elec_pos0p0_P-k1-1.pdos"),
    ]
    for _, path in panels:
        if not path.is_file():
            raise FileNotFoundError(path)

    # Shared y-scale for cross-panel comparison
    ymax = 0.0
    dos_cache: list[tuple] = []
    grid = np.linspace(-2.5, 2.5, 400)
    for name, path in panels:
        series = parse_pdos(path)
        dos = gaussian_dos(series.energy_ev, series.pi_weight, grid, sigma_ev=0.07)
        ymax = max(ymax, float(dos.max()))
        dos_cache.append((name, path, dos))
    ymax *= 1.12

    fig, axes = plt.subplots(2, 2, figsize=(6.75, 3.35), sharex=True, sharey=True)
    labels = "abcd"
    for ax, (name, path, dos), plab in zip(axes.ravel(), dos_cache, labels):
        _plot_dos(ax, path, f"{name}, $\\epsilon{{=}}0$", dos=dos, ymax=ymax)
        panel_label(ax, plab, fontsize=9)
    axes[0, 0].set_ylabel(r"$\pi$-DOS (a.u.)")
    axes[1, 0].set_ylabel(r"$\pi$-DOS (a.u.)")
    fig.subplots_adjust(wspace=0.32, hspace=0.38, left=0.10, right=0.98, top=0.94, bottom=0.14)

    out_dir.mkdir(parents=True, exist_ok=True)
    pdf = out_dir / "figure_s4_pdos_exp7.pdf"
    png = out_dir / "figure_s4_pdos_exp7.png"
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.04)
    fig.savefig(png, bbox_inches="tight", pad_inches=0.04, dpi=300)
    plt.close(fig)
    return pdf, png


if __name__ == "__main__":
    pdf, png = build(FIG_DIR / "out")
    print(f"Wrote {pdf}\nWrote {png}")
