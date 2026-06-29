#!/usr/bin/env python3
"""Generate paper/tables/tab_S_synergy_grid.tex from sdc_exp10_synergy_audit.json."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SDC = REPO / "experiments" / "analysis" / "sdc" / "sdc_exp10_synergy_audit.json"
OUT = REPO / "paper" / "tables" / "tab_S_synergy_grid.tex"


def main() -> None:
    data = json.loads(SDC.read_text())
    rows = []
    for row in sorted(
        data["synergy_table"],
        key=lambda r: (r["n_molecules"], r["dopant"]),
    ):
        n, d, s = row["n_molecules"], row["dopant"], row["synergy_S_meV_per_atom"]
        rows.append(f"{n} & {d} & $+3$ & ${s:+.2f}$ \\\\")

    body = "\n".join(rows)
    tex = f"""\\begin{{table*}}[t]
\\caption{{\\label{{tab:Sgrid}}Fifteen-point periodic synergy audit at $+3$\\% biaxial strain (PBE+D3 rigid protocol, reference placement seed~42).
$\\mathcal{{S}}$ in meV/atom from Eq.~\\eqref{{eq:synergy_order}}; source: \\texttt{{sdc\\_exp10\\_synergy\\_audit.json}}.}}
\\begin{{ruledtabular}}
\\begin{{tabular}}{{cccc}}
$n$ (C$_{{60}}$ units) & Dopant & $\\epsilon$ (\\%) & $\\mathcal{{S}}$ (meV/atom) \\\\
\\hline
{body}
\\end{{tabular}}
\\end{{ruledtabular}}
\\end{{table*}}
"""
    OUT.write_text(tex, encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
