"""Synergy size-scaling facet regressions (Exp. 10 SDC audit)."""

from __future__ import annotations

import numpy as np

from nature_style import get_color

COLOR_DATA = "#0055AA"
COLOR_FIT = "#CC0033"

FACET_ORDER = (
    ("B", "B-doped"),
    ("N", "N-doped"),
    ("P", "P-doped"),
    ("all", r"Additive $\mathcal{S}=0$"),
)


def _style_facet(ax, title: str) -> None:
    ax.set_title(title, fontsize=7.5, fontweight="bold", loc="left", pad=5)
    ax.patch.set_facecolor("#FAFAFA")


def _series(audit: dict, dop: str) -> tuple[np.ndarray, np.ndarray]:
    rows = [r for r in audit["synergy_table"] if r["dopant"] == dop]
    rows.sort(key=lambda r: r["n_molecules"])
    ns = np.array([r["n_molecules"] for r in rows], dtype=float)
    sv = np.array([r["synergy_S_meV_per_atom"] for r in rows], dtype=float)
    return ns, sv


def _fit_s_vs_inv_n(ns: np.ndarray, sv: np.ndarray) -> tuple[np.ndarray, np.ndarray, str]:
    """Linear fit S = S_inf + A/n in meV/atom."""
    if len(ns) < 2:
        return ns, sv, "n/a"
    inv = 1.0 / ns
    a_coef, s_inf = np.polyfit(inv, sv, 1)
    xg = np.linspace(float(ns.min()), float(ns.max()), 50)
    yg = s_inf + a_coef / xg
    return xg, yg, rf"$\mathcal{{S}}={s_inf:.1f}+{a_coef:.1f}/n$"


def plot_synergy_size_facet_regression(
    fig,
    subplot_spec,
    audit: dict,
    *,
    panel_label: str | None = "d",
    highlight_n: int = 4,
) -> None:
    """2x2 facets: S vs n with blue DFT points and red 1/n linear fit."""
    from matplotlib.gridspec import GridSpecFromSubplotSpec

    inner = GridSpecFromSubplotSpec(2, 2, subplot_spec=subplot_spec, wspace=0.32, hspace=0.42)

    for idx, (key, title) in enumerate(FACET_ORDER):
        ax = fig.add_subplot(inner[idx // 2, idx % 2])
        _style_facet(ax, title)

        if key == "all":
            for dop in ("B", "N", "P"):
                ns, sv = _series(audit, dop)
                ax.scatter(ns, sv, s=22, c=get_color(dop), edgecolors="#111", linewidths=0.4, zorder=4, label=dop)
                xg, yg, _ = _fit_s_vs_inv_n(ns, sv)
                ax.plot(xg, yg, color=get_color(dop), lw=1.1, ls=(0, (3, 2)), zorder=2)
            ax.axhline(0, color=COLOR_FIT, lw=1.2, zorder=1)
            ax.text(0.04, 0.96, r"$\mathcal{S}=0$", transform=ax.transAxes, fontsize=6, color=COLOR_FIT, va="top", fontweight="bold")
            ax.legend(loc="lower right", fontsize=5.5, frameon=True, edgecolor="#333")
        else:
            ns, sv = _series(audit, key)
            ax.scatter(ns, sv, s=28, c=COLOR_DATA, edgecolors="#111", linewidths=0.5, zorder=4)
            xg, yg, eq = _fit_s_vs_inv_n(ns, sv)
            ax.plot(xg, yg, color=COLOR_FIT, lw=1.6, zorder=3)
            ax.text(0.04, 0.96, eq, transform=ax.transAxes, fontsize=5.5, color=COLOR_FIT, va="top", fontweight="bold")
            if highlight_n in ns:
                j = int(np.where(ns == highlight_n)[0][0])
                ax.scatter([ns[j]], [sv[j]], s=55, facecolors="none", edgecolors="#111", linewidths=1.2, zorder=5)

        if idx == 0 and panel_label:
            ax.text(-0.20, 1.14, f"({panel_label})", transform=ax.transAxes, fontweight="bold", fontsize=9)
        ax.axhline(0, color="#CCCCCC", lw=0.5, zorder=0)
        ax.grid(True, color="#E8E8E8", lw=0.5, zorder=0)
        ax.set_xticks([1, 2, 4, 6, 8])
        if idx >= 2:
            ax.set_xlabel(r"Supercell size $n$", fontsize=6.5)
        else:
            ax.tick_params(labelbottom=False)
        if idx % 2 == 0:
            ax.set_ylabel(r"$\mathcal{S}$ (meV/atom)", fontsize=6.5)
        ax.tick_params(labelsize=6)
