"""Polaron reorganization-energy configuration diagram (Capobianco Fig. style)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Arc, FancyBboxPatch
import numpy as np

# Literature polaron binding energies (eV), Capobianco et al. Nano Lett. 2024 Table 2
LAMBDA = {
    "vdW": {"crys": 0.13, "loc": 0.05, "env": 0.08},
    "qHP": {"crys": 0.10, "loc": 0.04, "env": 0.06},
}

VBM_PURPLE = "#7B3294"
CBM_TEAL = "#008585"
RED = "#CC0033"
BLUE = "#0055AA"
GREY = "#666666"


def _parabola(x, x0, y0, k=0.35):
    return y0 + k * (x - x0) ** 2


def _draw_cluster_inset(ax, center_color=None, env_color=None, title=""):
    """Schematic 7-molecule cluster (top view)."""
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)
    ax.set_aspect("equal")
    ax.axis("off")
    angles = np.linspace(0, 2 * np.pi, 7, endpoint=False)
    for i, th in enumerate(angles):
        x, y = 0.85 * np.cos(th), 0.85 * np.sin(th)
        if i == 0 and center_color:
            fc, ec = center_color, "#222"
        elif env_color and i > 0:
            fc, ec = env_color, "#222"
        else:
            fc, ec = "#E8E8E8", "#888"
        ax.add_patch(plt.Circle((x, y), 0.28, fc=fc, ec=ec, lw=0.6, zorder=2))
        # wireframe hint
        ax.add_patch(plt.Circle((x, y), 0.18, fill=False, ec="#AAA", lw=0.4, zorder=3))
    if title:
        ax.text(0, -1.22, title, ha="center", fontsize=5.5, fontweight="bold")


def plot_config_coordinate(ax, *, material: str = "vdW", panel_label: str = "a") -> None:
    lam = LAMBDA["vdW" if material == "vdW" else "qHP"]
    lam_c, lam_loc, lam_env = lam["crys"], lam["loc"], lam["env"]

    ax.set_facecolor("#FAFAFA")
    x = np.linspace(-0.2, 2.8, 400)
    e_bulk = 0.0
    x_neu, x_chg = 0.0, 1.35
    y_neu = _parabola(x, x_neu, e_bulk, k=0.55)
    y_chg = _parabola(x, x_chg, e_bulk - lam_c - 0.15, k=0.42)

    ax.plot(x, y_neu, color="#333", lw=1.6, zorder=2)
    ax.plot(x, y_chg, color="#333", lw=1.6, zorder=2)
    ax.text(-0.05, e_bulk + 0.55, "Neutral bulk", fontsize=7, fontweight="bold")
    ax.text(1.05, e_bulk - lam_c - 0.15 + 0.55, "Negatively charged system", fontsize=7, fontweight="bold")

    e_vert = _parabola(x_neu, x_chg, e_bulk - lam_c - 0.15, k=0.42)
    e_loc = e_vert + lam_env
    e_opt = e_bulk - lam_c - 0.15

    ax.scatter([x_neu], [e_bulk], s=28, c="white", edgecolors="#000", lw=0.8, zorder=5)
    ax.text(x_neu - 0.08, e_bulk + 0.08, r"$E_{\mathrm{bulk}}$", fontsize=7)

    ax.annotate(
        "",
        xy=(x_neu, e_vert),
        xytext=(x_neu, e_bulk),
        arrowprops=dict(arrowstyle="-|>", color="#333", lw=1.2),
    )
    ax.text(x_neu + 0.12, (e_bulk + e_vert) / 2, "Electron\ninjection", fontsize=6, va="center")

    ax.scatter([x_neu], [e_vert], s=32, c=GREY, edgecolors="#000", lw=0.7, zorder=5)
    ax.scatter([0.55], [e_loc], s=32, c=RED, edgecolors="#000", lw=0.7, zorder=5)
    ax.scatter([x_chg], [e_opt], s=32, c=BLUE, edgecolors="#000", lw=0.7, zorder=5)
    ax.text(x_neu - 0.05, e_vert - 0.12, r"$E_{\mathrm{vert}}^-$", fontsize=6.5, ha="right")
    ax.text(0.62, e_loc + 0.06, r"$E_{\mathrm{loc}}^-$", fontsize=6.5, color=RED)
    ax.text(x_chg + 0.05, e_opt - 0.12, r"$E_{\mathrm{opt}}^-$", fontsize=6.5, color=BLUE)

    # Trajectory highlights on charged PES
    xs = np.linspace(x_neu, x_chg, 80)
    ys = _parabola(xs, x_chg, e_opt, k=0.42)
    i_loc = int(0.45 * len(xs))
    ax.plot(xs[:i_loc], ys[:i_loc], color=RED, lw=2.2, zorder=3, solid_capstyle="round")
    ax.plot(xs[i_loc:], ys[i_loc:], color=BLUE, lw=2.2, zorder=3, solid_capstyle="round")

    # Lambda brackets
    def bracket(xb, y1, y2, label, color, side="left"):
        xm = xb - 0.18 if side == "left" else xb + 0.18
        ax.plot([xm, xm], [y1, y2], color=color, lw=1.0)
        ax.plot([xm - 0.04, xm + 0.04], [y1, y1], color=color, lw=1.0)
        ax.plot([xm - 0.04, xm + 0.04], [y2, y2], color=color, lw=1.0)
        ax.text(xm - 0.22 if side == "left" else xm + 0.22, (y1 + y2) / 2, label, fontsize=6.5, color=color, va="center", ha="right" if side == "left" else "left")

    bracket(x_neu - 0.05, e_vert, e_loc, r"$\lambda^-(\mathrm{loc})$", RED, "left")
    bracket(x_chg + 0.05, e_loc, e_opt, r"$\lambda^-(\mathrm{env})$", BLUE, "right")
    bracket(x_neu - 0.32, e_vert, e_opt, r"$\lambda^-(\mathrm{crys})$", "#222", "left")
    ax.text(0.02, 0.02, f"{material} $C_{{60}}$: $\\lambda^-={lam_c:.2f}$ eV", transform=ax.transAxes, fontsize=6.5)

    ax.set_xlabel("Nuclear coordinates", fontsize=8)
    ax.set_ylabel("Energy", fontsize=8)
    ax.set_xlim(-0.35, 2.5)
    ax.set_ylim(e_bulk - lam_c - 0.55, e_bulk + 0.75)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.text(-0.12, 1.04, f"({panel_label})", transform=ax.transAxes, fontsize=10, fontweight="bold")

    # Insets
    inset_specs = [
        (0.06, 0.78, 0.20, 0.20, None, None, r"$E_{\mathrm{vert}}^-$"),
        (0.40, 0.78, 0.20, 0.20, RED, None, r"$E_{\mathrm{loc}}^-$"),
        (0.74, 0.78, 0.20, 0.20, RED, BLUE, r"$E_{\mathrm{opt}}^-$"),
    ]
    for x0, y0, w, h, cc, ec, ttl in inset_specs:
        iax = ax.inset_axes([x0, y0, w, h])
        _draw_cluster_inset(iax, center_color=cc, env_color=ec, title=ttl)


def _read_xyz_centers(xyz_path: Path, n_mol: int = 2) -> list[np.ndarray]:
    lines = xyz_path.read_text().strip().splitlines()
    n = int(lines[0])
    coords = np.array([[float(p) for p in ln.split()[1:4]] for ln in lines[2 : 2 + n]])
    # split by z-gap heuristic for dimer
    z = coords[:, 2]
    mid = np.median(z)
    low, high = coords[z <= mid], coords[z > mid]
    return [low.mean(axis=0), high.mean(axis=0)]


def _draw_c60_wireframe(ax, center, radius=4.2, color="#888", alpha=0.9):
    u = np.linspace(0, 2 * np.pi, 24)
    v = np.linspace(0, np.pi, 12)
    x = center[0] + radius * np.outer(np.cos(u), np.sin(v))
    y = center[1] + radius * np.outer(np.sin(u), np.sin(v))
    z = center[2] + radius * np.outer(np.ones_like(u), np.cos(v))
    ax.plot_wireframe(x, y, z, color=color, linewidth=0.35, alpha=alpha)


def plot_vdw_qhp_comparison(fig, gs_row, *, panel_label: str = "b") -> None:
    xyz = Path(__file__).resolve().parents[2] / "dft_results/exp_4_polaron/xyz_structures/polaron_+0.0_pristine_q0.xyz"
    centers = _read_xyz_centers(xyz) if xyz.exists() else [np.array([0, 0, 0]), np.array([0, 0, 12])]

    titles = ["vdW $C_{60}$", "qHP $C_{60}$"]
    offsets = [(-14, 0), (6, 0)]
    for j, (title, (dx, dy)) in enumerate(zip(titles, offsets)):
        ax = fig.add_subplot(gs_row[j], projection="3d")
        ax.set_facecolor("#FAFAFA")
        c0 = centers[0] + np.array([dx, dy, 0])
        c1 = centers[1] + np.array([dx, dy, 0])
        if j == 0:
            c1 = c1 + np.array([4.5, 0, 0])  # vdW: larger separation
        _draw_c60_wireframe(ax, c0)
        _draw_c60_wireframe(ax, c1)
        # isosurface blobs (schematic)
        for c, col in [(c0, VBM_PURPLE), (c1, CBM_TEAL if j else VBM_PURPLE)]:
            ax.scatter([c[0]], [c[1]], [c[2]], s=1200, c=col, alpha=0.22, edgecolors="none")
        ax.set_title(title, fontsize=8, fontweight="bold", pad=2)
        lam = LAMBDA["vdW" if j == 0 else "qHP"]["crys"]
        ax.text2D(0.05, 0.92, rf"$\lambda^-={lam:.2f}$ eV", transform=ax.transAxes, fontsize=7)
        ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
        ax.view_init(elev=12, azim=-58)
        ax.dist = 7
    fig.text(0.02, 0.48, f"({panel_label})", fontsize=10, fontweight="bold")


def compose_polaron_lambda_figure(out_pdf: Path) -> None:
    fig = plt.figure(figsize=(7.6, 4.5), dpi=300)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 0.85], hspace=0.38, wspace=0.28)
    ax_a = fig.add_subplot(gs[0, :])
    plot_config_coordinate(ax_a, material="qHP", panel_label="a")
    sub = gs[1, :].subgridspec(1, 2, wspace=0.15)
    plot_vdw_qhp_comparison(fig, sub, panel_label="b")
    out_pdf = Path(out_pdf)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf, bbox_inches="tight", facecolor="white")
    fig.savefig(out_pdf.with_suffix(".png"), bbox_inches="tight", facecolor="white", dpi=300)
    plt.close(fig)
    print(f"Wrote {out_pdf}")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    compose_polaron_lambda_figure(root / "paper/figures/final_figures/figure5_polaron_reorganization.pdf")
