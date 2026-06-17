"""Electronic-structure facet regressions (Exp. 7 PDOS, ggplot small-multiples style)."""

from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np

from pdos_parser import homo_lumo_ev, records_for

COLOR_A = "#0055AA"
COLOR_B = "#CC0033"

FACET_ORDER = (
    ("B", "B-doped"),
    ("N", "N-doped"),
    ("P", "P-doped"),
    ("pristine", "Pristine"),
)


def _fit_line(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, str]:
    if len(x) < 2:
        return x, y, "n/a"
    slope, intercept = np.polyfit(x, y, 1)
    xg = np.linspace(float(x.min()), float(x.max()), 50)
    return xg, intercept + slope * xg, f"$y={intercept:.2f}+{slope:.3f}x$"


def _style_facet(ax, title: str) -> None:
    ax.set_title(title, fontsize=7.5, fontweight="bold", loc="left", pad=5)
    ax.patch.set_facecolor("#FAFAFA")


def _gap_series(records: Iterable, dop: str, strains: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    xs, ys = [], []
    for s in strains:
        r = records_for(records, dopant=dop, strain_pct=float(s), kind="C")
        if r:
            xs.append(float(s))
            ys.append(r.gap_ev)
    return np.array(xs), np.array(ys)


def _homo_lumo_series(records: Iterable, dop: str, strains: Sequence[float]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    xs, homo, lumo = [], [], []
    for s in strains:
        r = records_for(records, dopant=dop, strain_pct=float(s), kind="C")
        if r:
            h, l = homo_lumo_ev(r)
            xs.append(float(s))
            homo.append(h)
            lumo.append(l)
    return np.array(xs), np.array(homo), np.array(lumo)


def _draw_dual_regression(ax, x: np.ndarray, y_blue: np.ndarray, y_red: np.ndarray) -> None:
    ax.scatter(x, y_blue, s=26, c=COLOR_A, edgecolors="#111", linewidths=0.4, zorder=4)
    ax.scatter(x, y_red, s=26, c=COLOR_B, edgecolors="#111", linewidths=0.4, zorder=4)
    xg0, yg0, eq0 = _fit_line(x, y_blue)
    xg1, yg1, eq1 = _fit_line(x, y_red)
    ax.plot(xg0, yg0, color=COLOR_A, lw=1.4, zorder=2)
    ax.plot(xg1, yg1, color=COLOR_B, lw=1.6, zorder=3)
    ax.text(0.04, 0.96, eq0, transform=ax.transAxes, fontsize=5.5, color=COLOR_A, va="top")
    ax.text(0.04, 0.80, eq1, transform=ax.transAxes, fontsize=5.5, color=COLOR_B, va="top", fontweight="bold")


def plot_gap_strain_facet_regression(
    fig,
    subplot_spec,
    records: Iterable,
    *,
    strains: Sequence[float] = (-5.0, 0.0, 5.0),
    panel_label: str | None = "a",
) -> None:
    """Gap (eV) vs strain; blue=pristine reference, red=facet dopant."""
    from matplotlib.gridspec import GridSpecFromSubplotSpec

    inner = GridSpecFromSubplotSpec(2, 2, subplot_spec=subplot_spec, wspace=0.30, hspace=0.40)
    ref_x, ref_y = _gap_series(records, "pristine", strains)

    for idx, (dop, title) in enumerate(FACET_ORDER):
        ax = fig.add_subplot(inner[idx // 2, idx % 2])
        _style_facet(ax, title)

        if dop == "pristine":
            ax.scatter(ref_x, ref_y, s=28, c=COLOR_A, edgecolors="#111", linewidths=0.5, zorder=4)
            xg, yg, eq = _fit_line(ref_x, ref_y)
            ax.plot(xg, yg, color=COLOR_B, lw=1.6, zorder=3)
            ax.text(0.04, 0.96, eq, transform=ax.transAxes, fontsize=5.5, color=COLOR_B, va="top", fontweight="bold")
        else:
            x, y = _gap_series(records, dop, strains)
            ax.scatter(ref_x, ref_y, s=22, c=COLOR_A, edgecolors="#111", linewidths=0.4, alpha=0.9, zorder=3)
            ax.scatter(x, y, s=26, c=COLOR_B, edgecolors="#111", linewidths=0.5, zorder=4)
            xg0, yg0, eq0 = _fit_line(ref_x, ref_y)
            xg1, yg1, eq1 = _fit_line(x, y)
            ax.plot(xg0, yg0, color=COLOR_A, lw=1.3, zorder=2)
            ax.plot(xg1, yg1, color=COLOR_B, lw=1.5, zorder=3)
            ax.text(0.04, 0.96, eq0, transform=ax.transAxes, fontsize=5.2, color=COLOR_A, va="top")
            ax.text(0.04, 0.80, eq1, transform=ax.transAxes, fontsize=5.2, color=COLOR_B, va="top", fontweight="bold")

        if idx == 0 and panel_label:
            ax.text(-0.20, 1.14, f"({panel_label})", transform=ax.transAxes, fontweight="bold", fontsize=9)
        ax.axhline(0.08, color="#888888", lw=0.6, ls=(0, (4, 3)), zorder=0)
        ax.grid(True, color="#E8E8E8", lw=0.5, zorder=0)
        ax.set_xlim(-5.8, 5.8)
        if idx >= 2:
            ax.set_xlabel(r"$\varepsilon$ (\%)", fontsize=6.5)
        else:
            ax.tick_params(labelbottom=False)
        if idx % 2 == 0:
            ax.set_ylabel(r"Gap (eV)", fontsize=6.5)
        ax.tick_params(labelsize=6)


def plot_bandedge_strain_facet_regression(
    fig,
    subplot_spec,
    records: Iterable,
    *,
    strains: Sequence[float] = (-5.0, 0.0, 5.0),
    panel_label: str | None = "c",
) -> None:
    """HOMO (blue) and LUMO (red) vs strain per facet."""
    from matplotlib.gridspec import GridSpecFromSubplotSpec

    inner = GridSpecFromSubplotSpec(2, 2, subplot_spec=subplot_spec, wspace=0.30, hspace=0.40)

    for idx, (dop, title) in enumerate(FACET_ORDER):
        ax = fig.add_subplot(inner[idx // 2, idx % 2])
        _style_facet(ax, title)
        x, homo, lumo = _homo_lumo_series(records, dop, strains)
        if len(x) >= 2:
            _draw_dual_regression(ax, x, homo, lumo)
        ax.axhline(0, color="#AAAAAA", lw=0.5, zorder=0)
        if idx == 0 and panel_label:
            ax.text(-0.20, 1.14, f"({panel_label})", transform=ax.transAxes, fontweight="bold", fontsize=9)
        ax.grid(True, color="#E8E8E8", lw=0.5, zorder=0)
        ax.set_xlim(-5.8, 5.8)
        if idx >= 2:
            ax.set_xlabel(r"$\varepsilon$ (\%)", fontsize=6.5)
        else:
            ax.tick_params(labelbottom=False)
        if idx % 2 == 0:
            ax.set_ylabel(r"$E-E_F$ (eV)", fontsize=6.5)
        ax.tick_params(labelsize=6)
