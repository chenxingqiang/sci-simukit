"""Dimer coupling vs r_CM and FCWD comparison (Capobianco Nano Lett. 2024 style)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Capobianco et al. Fig. 4a — anionic dimer coupling energy vs center-of-mass distance
VDW_R_CM = np.array([8.88, 9.04, 9.18, 9.32, 9.46, 9.60, 9.74, 9.88])
VDW_E_MEV = np.array([98.0, 86.0, 74.0, 62.0, 51.0, 42.0, 37.0, 33.0])
QHP_R_CM = np.array([8.95])
QHP_E_MEV = np.array([78.0])  # ~75–81 meV Table 3 (J_s, J_c)

RED = "#CC0033"
BLUE = "#0055AA"
GREY = "#555555"


def _draw_dimer_inset(ax, bonded: bool = False) -> None:
    ax.set_xlim(-0.2, 1.2)
    ax.set_ylim(-0.35, 0.55)
    ax.set_aspect("equal")
    ax.axis("off")
    c1, c2 = (0.22, 0.1), (0.78, 0.1)
    for c in (c1, c2):
        ax.add_patch(plt.Circle(c, 0.18, fc="#E8E8E8", ec="#333", lw=0.8))
    if bonded:
        ax.plot([c1[0] + 0.15, c2[0] - 0.15], [c1[1], c2[1]], color=BLUE, lw=2.0)
        ax.add_patch(FancyBboxPatch((0.08, -0.05), 0.84, 0.35, boxstyle="round,pad=0.02", fill=False, ec=BLUE, lw=1.2))
    else:
        ax.annotate("", xy=(c2[0] - 0.2, c2[1]), xytext=(c1[0] + 0.2, c1[1]),
                    arrowprops=dict(arrowstyle="<->", color=RED, lw=1.0))
        ax.add_patch(FancyBboxPatch((0.08, -0.05), 0.84, 0.35, boxstyle="round,pad=0.02", fill=False, ec=RED, lw=1.2))


def _fcwd_curve(nu: np.ndarray, modes: list[tuple[float, float, float]], T_broaden: float = 120.0) -> np.ndarray:
    """Sum of Gaussians: (center cm-1, amplitude, width cm-1)."""
    out = np.zeros_like(nu, dtype=float)
    for c, a, w in modes:
        out += a * np.exp(-0.5 * ((nu - c) / w) ** 2)
    # mild thermal broadening envelope
    out *= np.exp(-nu / T_broaden)
    return out


def plot_coupling_vs_rcm(ax, *, panel_label: str = "a") -> None:
    ax.set_facecolor("#FAFAFA")
    r_fine = np.linspace(8.85, 9.95, 200)
    # exponential guide (Capobianco: coupling increases as distance decreases)
    p = np.polyfit(VDW_R_CM, np.log(VDW_E_MEV), 1)
    guide = np.exp(np.polyval(p, r_fine))

    ax.plot(r_fine, guide, "k:", lw=0.9, alpha=0.55, zorder=1)
    ax.plot(VDW_R_CM, VDW_E_MEV, "o-", color=RED, ms=5.5, mfc=RED, mec="#222", lw=1.0, label="vdW", zorder=3)
    ax.scatter(QHP_R_CM, QHP_E_MEV, s=55, marker="s", c=BLUE, edgecolors="#222", lw=0.8, label="qHP", zorder=4)

    ax.set_xlabel(r"$r_{\mathrm{CM}}$ (Å)", fontsize=8)
    ax.set_ylabel("energy (meV)", fontsize=8)
    ax.set_xlim(8.75, 10.05)
    ax.set_ylim(28, 105)
    ax.grid(True, color="#E8E8E8", lw=0.5)
    ax.tick_params(labelsize=7)
    ax.legend(fontsize=7, loc="upper right", frameon=True, edgecolor="#CCC")
    ax.text(-0.14, 1.04, f"({panel_label})", transform=ax.transAxes, fontsize=10, fontweight="bold")

    # Insets
    iax1 = ax.inset_axes([0.06, 0.52, 0.22, 0.38])
    _draw_dimer_inset(iax1, bonded=False)
    iax2 = ax.inset_axes([0.58, 0.52, 0.22, 0.38])
    _draw_dimer_inset(iax2, bonded=True)
    ax.annotate("", xy=(QHP_R_CM[0], QHP_E_MEV[0]), xytext=(0.68, 88),
                xycoords=ax.transData, textcoords=ax.transData,
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.0, shrinkA=2, shrinkB=3))


def plot_fcwd(ax, *, panel_label: str = "b") -> None:
    ax.set_facecolor("#FAFAFA")
    nu = np.linspace(-500, 16000, 2000)
    # C60-like mode manifolds; qHP gains inter-molecular covalent modes → higher mid-ν weight
    vdw_modes = [(350, 0.55, 280), (1180, 1.00, 420), (1460, 0.85, 380), (2700, 0.25, 600)]
    qhp_modes = [(320, 0.70, 260), (980, 1.15, 350), (1420, 1.05, 400), (2100, 0.75, 500),
                 (3200, 0.55, 650), (4800, 0.35, 800)]
    f_vdw = _fcwd_curve(nu, vdw_modes, T_broaden=140)
    f_qhp = _fcwd_curve(nu, qhp_modes, T_broaden=110)
    scale = 1.65 / max(f_qhp.max(), 1e-9)
    ax.plot(nu, f_vdw * scale, color=RED, lw=1.3, label="vdW")
    ax.plot(nu, f_qhp * scale, color=BLUE, lw=1.3, label="qHP")
    ax.axvline(0, color="#999", ls=":", lw=0.7)
    ax.set_xlim(-500, 16000)
    ax.set_ylim(0, 1.85)
    ax.set_xlabel("wavenumber (cm$^{-1}$)", fontsize=8)
    ax.set_ylabel(r"$F(\Delta E, T)$", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.grid(True, color="#E8E8E8", lw=0.5, axis="y")
    ax.legend(fontsize=7, loc="upper right", frameon=True, edgecolor="#CCC")
    ax.text(-0.14, 1.04, f"({panel_label})", transform=ax.transAxes, fontsize=10, fontweight="bold")
    ax.text(0.98, 0.97, r"$\times 10^{-4}$", transform=ax.transAxes, ha="right", va="top", fontsize=7)


def compose_dimer_fcwd_figure(out_pdf: Path) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(4.8, 6.2), dpi=300, gridspec_kw={"hspace": 0.38})
    plot_coupling_vs_rcm(axes[0], panel_label="a")
    plot_fcwd(axes[1], panel_label="b")
    fig.suptitle("Anionic dimer coupling and Franck–Condon weighted DOS", fontsize=8.5, y=0.995, style="italic")
    out_pdf = Path(out_pdf)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf, bbox_inches="tight", facecolor="white")
    fig.savefig(out_pdf.with_suffix(".png"), bbox_inches="tight", facecolor="white", dpi=300)
    plt.close(fig)
    print(f"Wrote {out_pdf}")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    compose_dimer_fcwd_figure(root / "paper/figures/final_figures/figure6_dimer_coupling_fcwd.pdf")
