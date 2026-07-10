#!/usr/bin/env python3
"""Fill paper/tables/tab_I.tex when reference-placement PBE+D3 grid is complete (24/24)."""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
JSON = REPO / "experiments/analysis/reference_placement_pbed3.json"
TAB = REPO / "paper/tables/tab_I.tex"

N_DOP = {"B": 13, "N": 12, "P": 12}
LABEL = {"B": "B-doped", "N": "N-doped", "P": "P-doped"}


def fmt_e(ha: float) -> str:
    return f"{ha:.4f}"


def fmt_alpha(v: float | None) -> str:
    if v is None:
        raise ValueError("alpha missing")
    return f"{v:+.1f}"


def fmt_esub(v: float | None) -> str:
    if v is None:
        raise ValueError("E_sub missing")
    return f"{v:+.1f}"


def row_line(name: str, n_dop: str, e0: str, e5: str, alpha: str, esub: str) -> str:
    esub_col = esub if esub != "---" else "---"
    return f"{name} & {n_dop} & ${e0}$ & ${e5}$ & ${alpha}$ & {esub_col} \\\\"


def main() -> None:
    d = json.loads(JSON.read_text(encoding="utf-8"))
    if d.get("status") != "complete":
        print(f"skip: status={d.get('status')} (need complete 24/24)")
        return
    if d.get("alpha_provisional"):
        print("skip: alpha_provisional still true")
        return

    pri = d["pristine"]
    pri_e = {float(k): v for k, v in pri["strain_energies_ha"].items()}
    if 0.0 not in pri_e or 5.0 not in pri_e:
        print("skip: pristine missing eps=0 or +5%")
        return

    lines = [
        row_line(
            "Pristine",
            "---",
            fmt_e(pri_e[0.0]),
            fmt_e(pri_e[5.0]),
            fmt_alpha(pri["alpha_meV_per_pct"]),
            "---",
        )
    ]
    for dop in ("B", "N", "P"):
        sys = d["systems"][dop]
        e_ha = {float(k): v for k, v in sys["strain_energies_ha"].items()}
        lines.append(
            row_line(
                LABEL[dop],
                str(N_DOP[dop]),
                fmt_e(e_ha[0.0]),
                fmt_e(e_ha[5.0]),
                fmt_alpha(sys["alpha_meV_per_pct"]),
                fmt_esub(sys["E_sub_eV_per_dopant"]),
            )
        )
    body = "\n".join(lines)

    text = TAB.read_text(encoding="utf-8")
    text = text.replace(
        "Linear strain sensitivities and raw substitution energy differences for tetramer models "
        "(archived rigid-strain grid, legacy PBE without D3).",
        "Linear strain sensitivities and raw substitution energy differences for tetramer models "
        "(rigid-strain grid, PBE+D3; reference placement, seed~42).",
    )
    text = text.replace(
        "reference-placement PBE+D3 modernization is in progress.",
        "reference-placement PBE+D3 modernization is complete.",
    )
    text = re.sub(
        r"(?m)^Pristine & ---.*?^P-doped & 12 & \$[^$]+\$ & \$[^$]+\$ & \$[^$]+\$ & \$[^$]+\$ \\\\$",
        body,
        text,
        count=1,
    )

    TAB.write_text(text, encoding="utf-8")
    print(f"updated {TAB.relative_to(REPO)}")


if __name__ == "__main__":
    main()
