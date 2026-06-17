"""Figure S4-style VBM/CBM isosurfaces + band-edge DOS (Exp. 7 pristine)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from pdos_parser import HA_TO_EV, gaussian_dos, parse_pdos

VBM_COLOR = "#7B3294"
CBM_COLOR = "#008585"
S_COLOR = "#555555"
P_COLOR = "#888888"


def _orbital_weights(record) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    s_w, p_w, total = [], [], []
    with open(record.path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split()
            s_w.append(float(parts[3]))
            if len(parts) >= 7:
                p_w.append(float(parts[4]) + float(parts[5]) + float(parts[6]))
            else:
                p_w.append(0.0)
            total.append(sum(float(x) for x in parts[3:]))
    return np.array(s_w), np.array(p_w), np.array(total)


def plot_band_edge_dos(ax, pdos_path: Path, *, e_window: tuple[float, float] | None = None) -> None:
    rec = parse_pdos(pdos_path)
    ef = rec.e_fermi_au
    evals_ev = (rec.eigenvalues_au - ef) * HA_TO_EV
    s_w, p_w, tot_w = _orbital_weights(rec)
    homo_ev = (rec.homo_au - ef) * HA_TO_EV
    lumo_ev = (rec.lumo_au - ef) * HA_TO_EV
    if e_window is None:
        e_window = (homo_ev - 2.4, lumo_ev + 0.9)
    grid = np.linspace(e_window[0], e_window[1], 700)
    sigma = 0.055

    occ = rec.occupations > 0.5
    v_mask = occ & (evals_ev >= e_window[0]) & (evals_ev <= homo_ev + 0.02)
    c_mask = (~occ) & (evals_ev >= lumo_ev - 0.02) & (evals_ev <= e_window[1])

    def _plot_band(mask, color, label_prefix, mode):
        e_sub = evals_ev[mask]
        occ_sub = rec.occupations[mask]
        s_sub, p_sub, t_sub = s_w[mask], p_w[mask], tot_w[mask]
        dos_t = gaussian_dos(e_sub, t_sub, occ_sub, grid, sigma, mode=mode)
        dos_p = gaussian_dos(e_sub, p_sub, occ_sub, grid, sigma, mode=mode)
        dos_s = gaussian_dos(e_sub, s_sub, occ_sub, grid, sigma, mode=mode)
        peak = max(dos_t.max(), 1e-9)
        ax.fill_between(grid, 0, dos_t / peak, color=color, alpha=0.12, zorder=1)
        ax.plot(grid, dos_t / peak, color=color, lw=1.5, label=f"{label_prefix} Total")
        ax.plot(grid, dos_p / peak, color=P_COLOR, ls="--", lw=0.9, label=f"{label_prefix} $p$")
        ax.plot(grid, dos_s / peak, color=S_COLOR, ls=":", lw=0.9, label=f"{label_prefix} $s$")

    _plot_band(v_mask, VBM_COLOR, "VBM", "occupied")
    _plot_band(c_mask, CBM_COLOR, "CBM", "unoccupied")
    ax.axvspan(homo_ev, lumo_ev, color="#EEEEEE", alpha=0.55, zorder=0)
    ax.axvline(homo_ev, color=VBM_COLOR, lw=0.7, alpha=0.6)
    ax.axvline(lumo_ev, color=CBM_COLOR, lw=0.7, alpha=0.6)
    ax.set_xlim(e_window)
    ax.set_ylim(0, 1.08)
    ax.set_yticks([])
    ax.set_xlabel("energy (eV)", fontsize=8)
    ax.set_ylabel("DOS (a.u.)", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.text(0.03, 0.97, f"gap = {rec.gap_ev:.2f} eV", transform=ax.transAxes, fontsize=6.5, va="top")
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), fontsize=5.5, loc="upper right", frameon=True, edgecolor="#CCC")


def compose_vbm_cbm_figure(vbm_png: Path, cbm_png: Path, pdos_path: Path, out_pdf: Path, *, title: str = "qHP $C_{60}$ graphullerene ($\\varepsilon=0$%, pristine)") -> None:
    from PIL import Image
    import numpy as np
    fig = plt.figure(figsize=(7.2, 2.6), dpi=300)
    gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.05, 1.0], wspace=0.08)
    for i, (png, label, color) in enumerate([(vbm_png, "VBM", VBM_COLOR), (cbm_png, "CBM", CBM_COLOR)]):
        ax = fig.add_subplot(gs[0, i])
        ax.imshow(np.array(Image.open(png)))
        ax.axis("off")
        ax.set_title(label, fontsize=9, fontweight="bold", color=color, pad=4)
    ax_d = fig.add_subplot(gs[0, 2])
    plot_band_edge_dos(ax_d, pdos_path)
    fig.suptitle(title, fontsize=8, y=1.02, style="italic")
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf, bbox_inches="tight", facecolor="white")
    fig.savefig(out_pdf.with_suffix(".png"), bbox_inches="tight", facecolor="white", dpi=300)
    plt.close(fig)
    print(f"Wrote {out_pdf}")
