#!/usr/bin/env python3
"""Generate SI four-corner energy table + CSV from sdc_exp10_results.json."""

from __future__ import annotations

import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SDC = REPO / "experiments" / "analysis" / "sdc" / "sdc_exp10_results.json"
OUT_TEX = REPO / "paper" / "tables" / "tab_S_corner_energies.tex"
OUT_CSV = REPO / "paper" / "figures" / "data" / "sdc_corner_energies.csv"
HA_TO_MEV = 27.211386245988 * 1000.0


def _corner_row(row: dict) -> dict[str, float | int | str]:
    e00 = float(row["reference"])
    d_str = float(row["strain_only_delta"])
    d_dop = float(row["doping_only_delta"])
    e_eps0 = e00 + d_str
    e_0d = e00 + d_dop
    e_epsd = float(row["combined"])
    s_mev = float(row["synergy_S"]) * HA_TO_MEV
    return {
        "n_molecules": int(row["n_molecules"]),
        "dopant": str(row["dopant"]),
        "strain_pct": float(row["strain_pct"]),
        "E_00_Ha_per_atom": e00,
        "E_eps0_Ha_per_atom": e_eps0,
        "E_0d_Ha_per_atom": e_0d,
        "E_epsd_Ha_per_atom": e_epsd,
        "S_meV_per_atom": s_mev,
    }


def main() -> None:
    data = json.loads(SDC.read_text())
    rows = sorted(
        (_corner_row(r) for r in data["synergy_energy_per_atom"]),
        key=lambda r: (r["n_molecules"], r["dopant"]),
    )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    body_lines = []
    for r in rows:
        body_lines.append(
            f"{r['n_molecules']} & {r['dopant']} & $+{r['strain_pct']:.0f}$ & "
            f"{r['E_00_Ha_per_atom']:.10f} & {r['E_eps0_Ha_per_atom']:.10f} & "
            f"{r['E_0d_Ha_per_atom']:.10f} & {r['E_epsd_Ha_per_atom']:.10f} & "
            f"${r['S_meV_per_atom']:+.2f}$ \\\\"
        )
    body = "\n".join(body_lines)

    tex = f"""\\begin{{table*}}[t]
\\caption{{\\label{{tab:S_corners}}Machine-readable four-corner total energies per atom (Ha/atom) underlying $\\mathcal{{S}}$ at $+3$\\% biaxial strain (PBE+D3, rigid protocol, reference placement seed~42).
Corners follow Eq.~\\eqref{{eq:four_corner}}: $E_{{00}}=E(0,0)$, $E_{{\\epsilon 0}}=E(\\Delta\\epsilon,0)$, $E_{{0\\delta}}=E(0,\\Delta\\delta)$, $E_{{\\epsilon\\delta}}=E(\\Delta\\epsilon,\\Delta\\delta)$, all per atom relative to the same supercell size $n\\times\\mathrm{{C}}_{{60}}$.
$\\mathcal{{S}}$ (meV/atom) matches Eq.~\\eqref{{eq:synergy_order}} and the open audit chain (CSV mirror in the public data release).}}
\\begin{{ruledtabular}}
\\footnotesize
\\begin{{tabular}}{{cccccccr}}
$n$ & $\\delta$ & $\\epsilon$ (\\%) & $E_{{00}}$ & $E_{{\\epsilon 0}}$ & $E_{{0\\delta}}$ & $E_{{\\epsilon\\delta}}$ & $\\mathcal{{S}}$ \\\\
\\hline
{body}
\\end{{tabular}}
\\end{{ruledtabular}}
\\end{{table*}}
"""
    OUT_TEX.write_text(tex, encoding="utf-8")
    print(f"wrote {OUT_TEX.relative_to(REPO)}")
    print(f"wrote {OUT_CSV.relative_to(REPO)} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
