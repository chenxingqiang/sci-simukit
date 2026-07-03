#!/usr/bin/env python3
"""Generate paper/tables/tab_S_synergy_grid.tex from sdc_exp10_synergy_audit.json."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SDC = REPO / "experiments" / "analysis" / "sdc" / "sdc_exp10_synergy_audit.json"
OUT = REPO / "paper" / "tables" / "tab_S_synergy_grid.tex"


def _rows(data: dict, *, n_max: int | None) -> list[str]:
    rows = []
    for row in sorted(
        data["synergy_table"],
        key=lambda r: (r["n_molecules"], r["dopant"]),
    ):
        n = row["n_molecules"]
        if n_max is not None and n > n_max:
            continue
        d, s = row["dopant"], row["synergy_S_meV_per_atom"]
        rows.append(f"{n} & {d} & $+3$ & ${s:+.2f}$ \\\\")
    return rows


def main() -> None:
    data = json.loads(SDC.read_text())
    main_body = "\n".join(_rows(data, n_max=4))
    si_only = []
    for row in sorted(data["synergy_table"], key=lambda r: (r["n_molecules"], r["dopant"])):
        if row["n_molecules"] >= 6:
            n, d, s = row["n_molecules"], row["dopant"], row["synergy_S_meV_per_atom"]
            si_only.append(f"{n} & {d} & $+3$ & ${s:+.2f}$ \\\\")
    si_body = "\n".join(si_only)

    main_tex = f"""\\begin{{table*}}[t]
\\caption{{\\label{{tab:Sgrid}}Periodic synergy audit at $+3$\\% biaxial strain (PBE+D3 rigid protocol, reference placement seed~42; core $n\\leq 4$ at 400~Ry).
$\\mathcal{{S}}$ in meV/atom from Eq.~\\eqref{{eq:synergy_order}}. $n\\geq 6$ rows (350~Ry production settings) are in Supplemental Material Table~S1.}}
\\begin{{ruledtabular}}
\\begin{{tabular}}{{cccc}}
$n$ (C$_{{60}}$ units) & Dopant & $\\epsilon$ (\\%) & $\\mathcal{{S}}$ (meV/atom) \\\\
\\hline
{main_body}
\\end{{tabular}}
\\end{{ruledtabular}}
\\end{{table*}}
"""
    OUT.write_text(main_tex, encoding="utf-8")
    si_out = REPO / "paper" / "tables" / "tab_S_synergy_grid_si.tex"
    si_tex = f"""\\begin{{table}}[t]
\\caption{{\\label{{tab:Sgrid_si}}Supplemental periodic synergy rows at $+3$\\% ($n\\geq 6$; 350~Ry production cutoff; completeness only).}}
\\begin{{ruledtabular}}
\\begin{{tabular}}{{cccc}}
$n$ & Dopant & $\\epsilon$ (\\%) & $\\mathcal{{S}}$ (meV/atom) \\\\
\\hline
{si_body}
\\end{{tabular}}
\\end{{ruledtabular}}
\\end{{table}}
"""
    si_out.write_text(si_tex, encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)}")
    print(f"wrote {si_out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
