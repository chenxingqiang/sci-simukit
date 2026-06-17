"""Facet scatter + dual linear regression (ggplot / Origin small-multiples style)."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

COLOR_REF = "#0055AA"
COLOR_DOP = "#CC0033"
HA_TO_MEV = 27.211386245988 * 1000.0

FACET_ORDER = (
    ("B", "B-doped"),
    ("N", "N-doped"),
    ("P", "P-doped"),
    ("pristine", "Pristine"),
)


def _strain_series(grouped: dict, dop: str, *, exclude_strain: float | None = None) -> tuple[np.ndarray, np.ndarray]:
    recs = grouped[dop]
    e0 = next(r["total_energy_Ha"] for r in recs if r["strain"] == 0.0)
    n_atoms = recs[0]["n_atoms"]
    xs, ys = [], []
    for r in recs:
        if exclude_strain is not None and abs(r["strain"] - exclude_strain) < 0.01:
            continue
        xs.append(r["strain"])
        ys.append((r["total_energy_Ha"] - e0) * HA_TO_MEV / n_atoms)
    return np.array(xs), np.array(ys)


def _fit_line(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, str]:
    if len(x) < 2:
        return x, y, "y = n/a"
    slope, intercept = np.polyfit(x, y, 1)
    xg = np.linspace(float(x.min()), float(x.max()), 50)
    return xg, intercept + slope * xg, f"$y={intercept:.1f}+{slope:.2f}x$"


def _style_facet_header(ax, title: str) -> None:
    ax.set_title(title, fontsize=8, fontweight="bold", loc="left", pad=6)
    ax.patch.set_facecolor("#FAFAFA")


def plot_strain_facet_regression(
    fig,
    subplot_spec,
    grouped: dict,
    *,
    exclude_p_strain: float = 2.5,
) -> None:
    """2x2 facets: Delta E/N vs strain; blue=pristine reference, red=facet dopant."""
    from matplotlib.gridspec import GridSpecFromSubplotSpec

    inner = GridSpecFromSubplotSpec(2, 2, subplot_spec=subplot_spec, wspace=0.32, hspace=0.42)
    ref_x, ref_y = _strain_series(grouped, "pristine")

    for idx, (dop, title) in enumerate(FACET_ORDER):
        ax = fig.add_subplot(inner[idx // 2, idx % 2])
        _style_facet_header(ax, title)

        if dop == "pristine":
            x, y = ref_x, ref_y
            ax.scatter(x, y, s=28, c=COLOR_REF, edgecolors="#111", linewidths=0.5, zorder=4)
            xg, yg, eq = _fit_line(x, y)
            ax.plot(xg, yg, color=COLOR_DOP, lw=1.6, zorder=3)
            ax.text(0.04, 0.96, eq, transform=ax.transAxes, fontsize=6, color=COLOR_DOP, va="top", fontweight="bold")
        else:
            x, y = _strain_series(grouped, dop, exclude_strain=exclude_p_strain if dop == "P" else None)
            ax.scatter(ref_x, ref_y, s=24, c=COLOR_REF, edgecolors="#111", linewidths=0.4, alpha=0.9, zorder=3)
            ax.scatter(x, y, s=28, c=COLOR_DOP, edgecolors="#111", linewidths=0.5, zorder=4)
            xg0, yg0, eq0 = _fit_line(ref_x, ref_y)
            xg1, yg1, eq1 = _fit_line(x, y)
            ax.plot(xg0, yg0, color=COLOR_REF, lw=1.4, zorder=2)
            ax.plot(xg1, yg1, color=COLOR_DOP, lw=1.6, zorder=3)
            ax.text(0.04, 0.96, eq0, transform=ax.transAxes, fontsize=5.8, color=COLOR_REF, va="top")
            ax.text(0.04, 0.82, eq1, transform=ax.transAxes, fontsize=5.8, color=COLOR_DOP, va="top", fontweight="bold")

        if idx == 0:
            ax.text(-0.18, 1.12, "(c)", transform=ax.transAxes, fontweight="bold", fontsize=9)
        ax.axhline(0, color="#CCCCCC", lw=0.5, zorder=0)
        ax.grid(True, color="#E8E8E8", lw=0.6, zorder=0)
        ax.set_xlim(-5.8, 5.8)
        if idx >= 2:
            ax.set_xlabel(r"Strain $\varepsilon$ (\%)", fontsize=7)
        else:
            ax.tick_params(labelbottom=False)
        if idx % 2 == 0:
            ax.set_ylabel(r"$\Delta E/N_{\mathrm{atom}}$ (meV/atom)", fontsize=7)
        ax.tick_params(labelsize=6.5)
