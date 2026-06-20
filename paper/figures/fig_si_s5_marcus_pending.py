#!/usr/bin/env python3
"""Fig. S5 — Marcus configuration coordinate (adiabatic IP/EA verified; lambda pending)."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

FIG_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(FIG_DIR))

from _load_audit import load_json
from _style import COLOR_CBM, COLOR_VBM, apply_si_style, panel_label, style_axes


def _parabola(q, q0, e0, k):
    return e0 + 0.5 * k * (q - q0) ** 2


def build(out_dir: Path) -> tuple[Path, Path]:
    apply_si_style()
    exp9 = load_json("experiments/analysis/exp9_polaron_verification.json")
    ad = exp9["derived"]["adiabatic_eV"]

    fig, axes = plt.subplots(1, 4, figsize=(9.0, 2.05), sharey=True)
    q = np.linspace(-1.2, 1.2, 200)

    panels = [
        ("pristine", ad["pristine"]["IP"], None, "IP"),
        ("N", ad["N"]["IP"], None, "IP"),
        ("B", ad["B"]["IP"], ad["B"]["EA"], "EA"),
        ("P", ad["P"]["IP"], ad["P"]["EA"], "IP"),
    ]

    for ax, (name, ip, ea, focus) in zip(axes, panels):
        e0, e1 = 0.0, 0.35
        neutral = _parabola(q, 0.0, e0, 1.1)
        charged = _parabola(q, 0.35, e1, 1.1)
        ax.plot(q, neutral, color=COLOR_VBM, lw=0.9, label="neutral")
        ax.plot(q, charged, color=COLOR_CBM, lw=0.9, label="$q=\\pm1$")
        ax.axvspan(-0.15, 0.15, color="#EEEEEE", zorder=0, alpha=0.6)
        if ip is not None:
            ax.annotate(
                "",
                xy=(0.0, e0),
                xytext=(0.35, e1),
                arrowprops=dict(arrowstyle="<->", color="#333333", lw=0.55),
            )
            ax.text(0.42, (e0 + e1) / 2, f"IP={ip:.2f} eV", fontsize=5.5, va="center")
        if ea is not None and (focus == "EA" or name == "P"):
            ax.annotate(
                "",
                xy=(0.0, e0),
                xytext=(-0.35, e1 - 0.05),
                arrowprops=dict(arrowstyle="<->", color="#333333", lw=0.55),
            )
            ax.text(-0.72, (e0 + e1) / 2 - 0.05, f"EA={ea:.2f} eV", fontsize=5.5, va="center")
        lam_block = exp9["derived"]["lambda_eV"].get(name, {})
        lam_ip = lam_block.get("lambda_IP_eV")
        lam_ea = lam_block.get("lambda_EA_eV")
        parts = []
        if lam_ip is not None:
            parts.append(rf"$\lambda^{{+}}={lam_ip:.2f}$")
        if lam_ea is not None:
            parts.append(rf"$\lambda^{{-}}={lam_ea:.2f}$")
        if parts:
            lam_txt = "; ".join(parts) + " eV"
            lam_color = "#333333"
        else:
            lam_txt = r"$\lambda$ [pending Exp.~9 SP]"
            lam_color = "#888888"
        ax.text(
            0.02,
            0.06,
            lam_txt,
            transform=ax.transAxes,
            fontsize=5,
            color=lam_color,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#CCCCCC", alpha=0.9),
        )
        ax.set_xlabel("configuration coordinate $Q$")
        ax.set_title(name.capitalize(), fontsize=6.5, pad=2)
        ax.set_xlim(-1.1, 1.1)
        ax.set_ylim(-0.05, 0.55)
        style_axes(ax)

    axes[0].set_ylabel("energy (eV, schematic)")
    panel_label(axes[0], "S5")
    fig.legend(frameon=False, loc="upper center", ncol=2, fontsize=5, bbox_to_anchor=(0.5, 1.04))
    fig.subplots_adjust(wspace=0.22)

    out_dir.mkdir(parents=True, exist_ok=True)
    pdf = out_dir / "figure_s5_marcus_pending.pdf"
    png = out_dir / "figure_s5_marcus_pending.png"
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.05)
    fig.savefig(png, bbox_inches="tight", pad_inches=0.05, dpi=300)
    plt.close(fig)
    return pdf, png


if __name__ == "__main__":
    pdf, png = build(FIG_DIR / "out")
    print(f"Wrote {pdf}\nWrote {png}")
