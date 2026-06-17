"""2D structure / strain / localization morphologies."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

ELEM_COLOR = {"C": "#505050", "B": "#0055AA", "N": "#CC0033", "P": "#FF8800"}
BOND_CUTOFF = 1.75
DOPANT_ELEMENTS = frozenset({"B", "N", "P"})


def read_inp_dopant_indices(inp_path: Path) -> List[int]:
    """Return 0-based indices of B/N/P atoms in &COORD block."""
    lines = Path(inp_path).read_text().splitlines()
    in_coord = False
    syms: List[str] = []
    for line in lines:
        s = line.strip()
        if s.startswith("&COORD"):
            in_coord = True
            continue
        if in_coord and s.startswith("&END"):
            break
        if in_coord and s and not s.startswith("#"):
            syms.append(s.split()[0])
    return [i for i, sym in enumerate(syms) if sym in DOPANT_ELEMENTS]


def read_xyz(path: Path) -> Tuple[List[str], np.ndarray]:
    lines = Path(path).read_text().strip().splitlines()
    n = int(lines[0].strip())
    syms, pos = [], []
    for line in lines[2 : 2 + n]:
        p = line.split()
        syms.append(p[0])
        pos.append([float(p[1]), float(p[2]), float(p[3])])
    return syms, np.array(pos)


def infer_bonds(symbols: List[str], pos: np.ndarray) -> List[Tuple[int, int]]:
    bonds = []
    n = len(symbols)
    for i in range(n):
        for j in range(i + 1, n):
            if np.linalg.norm(pos[i] - pos[j]) < BOND_CUTOFF:
                bonds.append((i, j))
    return bonds


def cage_centroids(pos: np.ndarray, n_cages: int = 4) -> np.ndarray:
    per = len(pos) // n_cages
    return np.array([pos[i * per : (i + 1) * per].mean(axis=0) for i in range(n_cages)])


def plot_tetramer_topview(ax, xyz_path: Path, *, inp_path: Path | None = None, title: str = "") -> None:
    syms, pos = read_xyz(xyz_path)
    dop_idx_inp = set(read_inp_dopant_indices(inp_path)) if inp_path and inp_path.exists() else set()
    bonds = infer_bonds(syms, pos)
    xy = pos[:, :2]
    ctrs = cage_centroids(pos)[:, :2]
    for i, j in bonds:
        ax.plot([xy[i, 0], xy[j, 0]], [xy[i, 1], xy[j, 1]], color="#888888", lw=0.35, alpha=0.55, zorder=1)
    for k, (s, (x, y)) in enumerate(zip(syms, xy)):
        is_dop = s in DOPANT_ELEMENTS or k in dop_idx_inp
        r = 0.55 if is_dop else 0.22
        col = ELEM_COLOR.get(s if is_dop else "C", "#505050")
        ax.add_patch(
            Circle((x, y), r, facecolor=col, edgecolor="#111", lw=0.5 if is_dop else 0.35, zorder=4 if is_dop else 3)
        )
    for k, c in enumerate(ctrs):
        ax.add_patch(Circle(c, 2.8, fill=False, edgecolor="#AAAAAA", lw=0.6, linestyle=(0, (4, 3)), zorder=0))
        ax.text(c[0], c[1], f"{k + 1}", ha="center", va="center", fontsize=6, color="#666666")
    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=8, fontweight="bold", pad=2, color=ELEM_COLOR.get(title, "#333333"))


def plot_dopant_triptych(ax, xyz_dir: Path, *, strain_tag: str = "+0.0") -> None:
    """B / N / P tetramer top views side-by-side (VMD-free ball-and-stick)."""
    ax.axis("off")
    for i, dop in enumerate(("B", "N", "P")):
        sub = ax.inset_axes([0.01 + i * 0.33, 0.02, 0.31, 0.96])
        xyz = xyz_dir / f"C60_strain_{strain_tag}_{dop}_doped_synergy.xyz"
        plot_tetramer_topview(sub, xyz, title=dop)
    ax.text(0.5, 1.02, r"$4\times\mathrm{C}_{60}$ tetramers ($\varepsilon=0$)", transform=ax.transAxes, ha="center", fontsize=8)


def plot_strain_cell_morph(ax, xyz0: Path, xyz_strained: Path) -> None:
    _, p0 = read_xyz(xyz0)
    _, p1 = read_xyz(xyz_strained)
    for pos, label, color, ls in ((p0, r"$\varepsilon=0$", "#333333", "-"), (p1, r"$\varepsilon=+5$%", "#CC0033", "--")):
        lo, hi = pos.min(axis=0), pos.max(axis=0)
        ax.add_patch(Rectangle((lo[0], lo[1]), hi[0]-lo[0], hi[1]-lo[1], fill=False, edgecolor=color, lw=1.4, linestyle=ls))
        ax.text(lo[0], hi[1] + 0.3, label, color=color, fontsize=7, ha="left")
    ax.add_patch(FancyArrowPatch(p0.mean(axis=0)[:2], p1.mean(axis=0)[:2], arrowstyle="-|>", mutation_scale=10, lw=1.0, color="#0055AA"))
    allp = np.vstack([p0[:, :2], p1[:, :2]])
    lo, hi = allp.min(0) - 1.5, allp.max(0) + 1.5
    ax.set_xlim(lo[0], hi[0]); ax.set_ylim(lo[1], hi[1]); ax.set_aspect("equal"); ax.axis("off")


def plot_ipr_localization_morph(
    ax,
    ipr_pristine: float,
    ipr_coupled: float,
    *,
    j_pristine: float | None = None,
    j_coupled: float | None = None,
) -> None:
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")
    ax.text(5, 4.6, "Carrier localization (Exp.~4)", ha="center", fontsize=8, fontweight="bold")

    def panel(x0, ipr, cap, j_meV=None):
        ax.add_patch(Rectangle((x0, 0.4), 4.2, 3.6, fill=False, edgecolor="#666666", lw=0.8))
        for cx, cy in [(x0 + 1.2, 2.2), (x0 + 2.2, 2.2), (x0 + 3.2, 2.2), (x0 + 2.2, 1.2)]:
            ax.add_patch(Circle((cx, cy), 0.35, facecolor="#DDDDDD", edgecolor="#888888", lw=0.5))
        r = np.sqrt(60.0 / max(ipr, 1)) * 0.12
        ax.add_patch(Circle((x0 + 2.2, 2.2), r, facecolor="#CC0033", edgecolor="#000", alpha=0.35, lw=0.8))
        ax.text(x0 + 2.2, 0.15, cap, ha="center", fontsize=7)
        ax.text(x0 + 2.2, 3.85, f"IPR={ipr:.0f}", ha="center", fontsize=8, fontweight="bold")
        if j_meV is not None:
            ax.text(x0 + 2.2, 3.45, f"$J={j_meV:.0f}$ meV", ha="center", fontsize=6.5, color="#0055AA")

    panel(0.3, ipr_pristine, "pristine", j_pristine)
    panel(5.5, ipr_coupled, "B + 3% strain", j_coupled)
    if j_pristine is not None and j_coupled is not None and j_pristine > 0:
        pct = 100.0 * (j_coupled - j_pristine) / j_pristine
        ax.annotate(
            "",
            xy=(7.6, 2.2),
            xytext=(2.4, 2.2),
            arrowprops=dict(arrowstyle="-|>", color="#0055AA", lw=1.1),
        )
        ax.text(5, 2.55, f"$\\Delta J=+{pct:.0f}$\\%", ha="center", fontsize=7, color="#0055AA", fontweight="bold")
