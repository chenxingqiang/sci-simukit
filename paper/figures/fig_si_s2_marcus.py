#!/usr/bin/env python3
"""Fig.~3 / S2 — Marcus protocol schematic + tabulated IP/EA and lambda.

Main manuscript (Fig.~\\ref{fig:marcus}) uses native TikZ + ruledtabular:
  paper/figures/tikz/marcus_schematic.tex
  paper/figures/tikz/marcus_table.tex
This script remains for SI PNG/PDF export if needed.
"""

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
EM_DASH = "\u2014"


def _parabola(q, q0, e0, k):
    return e0 + 0.5 * k * (q - q0) ** 2


def _arrow_key_handles() -> list[Line2D]:
    return [
        Line2D([0], [0], color=COLOR_ADIAB, lw=0.9, marker="<", markersize=4, label="adiabatic IP"),
        Line2D([0], [0], color=COLOR_CBM, lw=0, marker="s", markersize=4, label="adiab. EA (B, P)"),
        Line2D(
            [0],
            [0],
            color="#BBBBBB",
            lw=0,
            marker="s",
            markersize=5,
            markerfacecolor="#EEEEEE",
            markeredgecolor="#BBBBBB",
            label=r"neutral $Q$ (vertical SP)",
        ),
    ]


def _lambda_cells(name: str, lam_block: dict) -> tuple[str, str]:
    """Return ($\lambda^+$, $\lambda^-$) display strings for the table."""
    lam_ip = lam_block.get("lambda_IP_eV")
    lam_ea = lam_block.get("lambda_EA_eV")
    lam_p = f"{lam_ip:.3f}" if lam_ip is not None else EM_DASH
    if name == "B":
        lam_m = f"{EM_DASH}$^{{\\dagger}}$"
    elif lam_ea is not None:
        lam_m = f"{lam_ea:.3f}"
    else:
        lam_m = EM_DASH
    return lam_p, lam_m


def _style_ruled_table(table, n_data_rows: int) -> None:
    """APS/PRB-style ruledtabular: horizontal rules only, no vertical grid."""
    nrows = n_data_rows + 1
    rule_lw = 0.55
    for (row, col), cell in table.get_celld().items():
        cell.set_facecolor("white")
        cell.set_edgecolor("#000000")
        cell.set_linewidth(0.0)
        if row == 0:
            cell.visible_edges = "TB"
            cell.set_linewidth(rule_lw)
            cell.set_text_props(weight="bold", fontsize=6.2)
            cell.get_text().set_ha("center")
            cell.set_height(0.14)
        elif row == nrows:
            cell.visible_edges = "B"
            cell.set_linewidth(rule_lw)
            cell.set_text_props(fontsize=6.0)
            cell.set_height(0.12)
        else:
            cell.visible_edges = ""
            cell.set_text_props(fontsize=6.0)
            cell.set_height(0.12)
        if row > 0:
            txt = cell.get_text()
            if col == 0:
                txt.set_ha("left")
            else:
                txt.set_ha("right")
                txt.set_family("monospace")


def build(out_dir: Path) -> tuple[Path, Path]:
    apply_si_style()
    exp9 = load_json("experiments/analysis/exp9_polaron_verification.json")
    ad = exp9["derived"]["adiabatic_eV"]
    lam_all = exp9["derived"]["lambda_eV"]

    fig = plt.figure(figsize=(PRB_WIDTH_IN, 2.55))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.05], wspace=0.32)
    ax = fig.add_subplot(gs[0, 0])
    ax_tbl = fig.add_subplot(gs[0, 1])
    ax_tbl.axis("off")

    q = np.linspace(-1.2, 1.2, 200)
    q0_charged = 0.35
    k = 1.1
    e0, e1 = 0.0, 0.35

    neutral = _parabola(q, 0.0, e0, k)
    charged = _parabola(q, q0_charged, e1, k)
    ax.plot(q, neutral, color=COLOR_VBM, lw=0.95, label="neutral ($q{=}0$)")
    ax.plot(q, charged, color=COLOR_CBM, lw=0.95, label="charged ($q{\\pm}1$)")
    ax.axvspan(-0.15, 0.15, color="#EEEEEE", zorder=0, alpha=0.65)

    ax.annotate(
        "",
        xy=(0.0, e0),
        xytext=(q0_charged, e1),
        arrowprops=dict(arrowstyle="<->", color=COLOR_ADIAB, lw=0.65),
    )
    ax.text(
        0.42,
        (e0 + e1) / 2 + 0.02,
        "adiabatic IP",
        fontsize=5.5,
        va="center",
        color=COLOR_ADIAB,
    )
    ax.text(
        q0_charged + 0.02,
        e1 + 0.03,
        "adiab. EA (B, P)",
        fontsize=5.0,
        va="bottom",
        ha="left",
        color=COLOR_CBM,
    )
    ax.text(
        0.5,
        0.97,
        r"$\lambda^{\pm}=E_{\mathrm{vert}}^{\pm}-E_{\mathrm{opt}}^{\pm}$",
        transform=ax.transAxes,
        fontsize=5.0,
        ha="center",
        va="top",
        color="#666666",
    )
    ax.set_xlabel("configuration coordinate $Q$")
    ax.set_ylabel("energy (eV, schematic)")
    ax.set_title("(a) Marcus protocol", fontsize=7.0, pad=4, loc="left", fontweight="normal")
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-0.05, 0.58)
    style_axes(ax)

    rows = []
    for name in ("pristine", "N", "B", "P"):
        ip = ad[name]["IP"]
        ea = ad[name].get("EA")
        ea_txt = f"{ea:.2f}" if ea is not None else EM_DASH
        lam_p, lam_m = _lambda_cells(name, lam_all.get(name, {}))
        rows.append([name.capitalize(), f"{ip:.2f}", ea_txt, lam_p, lam_m])

    col_labels = ["Dopant", "IP (eV)", "EA (eV)", r"$\lambda^{+}$ (eV)", r"$\lambda^{-}$ (eV)"]
    col_widths = [0.20, 0.18, 0.18, 0.20, 0.20]
    table = ax_tbl.table(
        cellText=rows,
        colLabels=col_labels,
        loc="upper center",
        cellLoc="center",
        colLoc="center",
        colWidths=col_widths,
        bbox=[0.0, 0.22, 1.0, 0.62],
    )
    table.auto_set_font_size(False)
    _style_ruled_table(table, n_data_rows=len(rows))

    ax_tbl.set_title(
        r"(b) Adiabatic IP/EA and $\lambda^{\pm}$",
        fontsize=7.0,
        pad=6,
        loc="left",
        fontweight="normal",
    )
    ax_tbl.text(
        0.0,
        0.06,
        r"$^{\dagger}$B channel: $\lambda^{-}<0$ under fixed neutral-geometry vertical SP; not reported.",
        transform=ax_tbl.transAxes,
        fontsize=5.2,
        ha="left",
        va="bottom",
        color="#444444",
    )

    curve_handles, curve_labels = ax.get_legend_handles_labels()
    key_handles = _arrow_key_handles()
    fig.legend(
        curve_handles + key_handles,
        curve_labels + [h.get_label() for h in key_handles],
        frameon=True,
        fancybox=False,
        edgecolor="#CCCCCC",
        facecolor="white",
        framealpha=0.96,
        loc="upper center",
        ncol=3,
        fontsize=5.0,
        handlelength=1.4,
        columnspacing=0.8,
        borderpad=0.35,
        bbox_to_anchor=(0.48, 1.02),
    )
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.18, top=0.80)

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
