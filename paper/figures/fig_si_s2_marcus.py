#!/usr/bin/env python3
"""Fig.~3 / S2 — Marcus configuration coordinate (cross-dopant comparison)."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

FIG_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(FIG_DIR))

from _load_audit import load_json
from _style import COLOR_CBM, COLOR_VBM, PRB_WIDTH_IN, apply_si_style, style_axes

COLOR_ADIAB = "#333333"


def _parabola(q, q0, e0, k):
    return e0 + 0.5 * k * (q - q0) ** 2


def _arrow_key_handles() -> list[Line2D]:
    return [
        Line2D([0], [0], color=COLOR_ADIAB, lw=0.9, marker="<", markersize=4, label="adiabatic IP"),
        Line2D([0], [0], color=COLOR_CBM, lw=0, marker="s", markersize=4, label="adiab. EA (B, P)"),
        Line2D([0], [0], color="#BBBBBB", lw=0, marker="s", markersize=5, markerfacecolor="#EEEEEE", markeredgecolor="#BBBBBB", label=r"neutral $Q$ (vertical SP)"),
    ]


def build(out_dir: Path) -> tuple[Path, Path]:
    apply_si_style()
    exp9 = load_json("experiments/analysis/exp9_polaron_verification.json")
    ad = exp9["derived"]["adiabatic_eV"]

    fig, axes = plt.subplots(1, 4, figsize=(PRB_WIDTH_IN, 2.35), sharey=True)
    q = np.linspace(-1.2, 1.2, 200)

    panels = [
        ("pristine", ad["pristine"]["IP"], None),
        ("N", ad["N"]["IP"], None),
        ("B", ad["B"]["IP"], ad["B"]["EA"]),
        ("P", ad["P"]["IP"], ad["P"]["EA"]),
    ]

    q0_charged = 0.35
    k = 1.1
    e0, e1 = 0.0, 0.35

    for i, (ax, (name, ip, ea)) in enumerate(zip(axes, panels)):
        neutral = _parabola(q, 0.0, e0, k)
        charged = _parabola(q, q0_charged, e1, k)
        leg_neutral = "neutral ($q{=}0$)" if i == 0 else "_nolegend_"
        leg_charged = "charged ($q{\\pm}1$)" if i == 0 else "_nolegend_"
        ax.plot(q, neutral, color=COLOR_VBM, lw=0.9, label=leg_neutral)
        ax.plot(q, charged, color=COLOR_CBM, lw=0.9, label=leg_charged)
        ax.axvspan(-0.15, 0.15, color="#EEEEEE", zorder=0, alpha=0.65)

        # Adiabatic hole channel: neutral minimum -> charged minimum (same geometry for all panels).
        ax.annotate(
            "",
            xy=(0.0, e0),
            xytext=(q0_charged, e1),
            arrowprops=dict(arrowstyle="<->", color=COLOR_ADIAB, lw=0.6),
        )
        ax.text(
            0.40,
            (e0 + e1) / 2 + 0.02,
            rf"IP$={ip:.2f}$ eV",
            fontsize=5.5,
            va="center",
            color=COLOR_ADIAB,
        )

        if ea is not None:
            ax.text(
                q0_charged + 0.02,
                e1 + 0.025,
                rf"EA$={ea:.2f}$ eV",
                fontsize=5.5,
                va="bottom",
                ha="left",
                color=COLOR_CBM,
            )

        lam_block = exp9["derived"]["lambda_eV"].get(name, {})
        lam_ip = lam_block.get("lambda_IP_eV")
        lam_ea = lam_block.get("lambda_EA_eV")
        parts = []
        if lam_ip is not None:
            parts.append(rf"$\lambda^{{+}}={lam_ip:.2f}$")
        if lam_ea is not None and not (name == "B" and lam_ea < 0):
            parts.append(rf"$\lambda^{{-}}={lam_ea:.2f}$")
        lam_txt = "; ".join(parts) + " eV" if parts else r"$\lambda$ pending"
        if name == "B":
            lam_txt += r" ($\lambda^{-}$ excluded)"
        lam_color = "#333333" if parts else "#888888"
        ax.text(
            0.5,
            0.08,
            lam_txt,
            transform=ax.transAxes,
            fontsize=5.0,
            color=lam_color,
            ha="center",
            va="bottom",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#CCCCCC", alpha=0.96, lw=0.45),
        )
        if i == 0:
            ax.text(
                0.5,
                0.97,
                rf"$\lambda^{{\pm}}=E_{{\mathrm{{vert}}}}^{{\pm}}-E_{{\mathrm{{opt}}}}^{{\pm}}$",
                transform=ax.transAxes,
                fontsize=4.8,
                ha="center",
                va="top",
                color="#666666",
            )

        ax.set_xlabel("")
        ax.set_title(name.capitalize(), fontsize=6.5, pad=4)
        ax.set_xlim(-1.1, 1.1)
        ax.set_ylim(-0.05, 0.58)
        style_axes(ax)

    axes[0].set_ylabel("energy (eV, schematic)")

    curve_handles, curve_labels = axes[0].get_legend_handles_labels()
    key_handles = _arrow_key_handles()
    fig.legend(
        curve_handles + key_handles,
        curve_labels + [h.get_label() for h in key_handles],
        frameon=True,
        fancybox=False,
        edgecolor="#CCCCCC",
        facecolor="white",
        framealpha=0.96,
        loc="upper left",
        ncol=3,
        fontsize=4.8,
        handlelength=1.4,
        columnspacing=0.8,
        borderpad=0.35,
        bbox_to_anchor=(0.07, 1.03),
    )
    fig.text(
        0.5,
        0.99,
        "Columns: same Marcus workflow (charged GEO\\_OPT + vertical SP at neutral geometry); "
        "compare dopant-dependent IP/EA and $\\lambda^{\\pm}$.",
        fontsize=5,
        ha="center",
        va="top",
        color="#444444",
    )
    fig.supxlabel("configuration coordinate $Q$", fontsize=6, y=0.10)
    fig.subplots_adjust(wspace=0.42, bottom=0.22, top=0.78, left=0.07, right=0.99)

    out_dir.mkdir(parents=True, exist_ok=True)
    pdf = out_dir / "figure_s2_marcus.pdf"
    png = out_dir / "figure_s2_marcus.png"
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.05)
    fig.savefig(png, bbox_inches="tight", pad_inches=0.05, dpi=300)
    plt.close(fig)
    return pdf, png


if __name__ == "__main__":
    pdf, png = build(FIG_DIR / "out")
    print(f"Wrote {pdf}\nWrote {png}")
