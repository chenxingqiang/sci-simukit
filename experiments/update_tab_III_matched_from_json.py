#!/usr/bin/env python3
"""Update tab_III.tex when matched-functional rigid PBE+D3 grid is complete."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MATCHED = REPO / "experiments" / "analysis" / "relax_validation_matched_functional.json"
TAB = REPO / "paper" / "tables" / "tab_III.tex"


def main() -> None:
    if not MATCHED.exists():
        print("skip: no matched JSON")
        return
    d = json.loads(MATCHED.read_text())
    if not d.get("quantitative_ratio_valid"):
        print("skip: quantitative_ratio_valid false")
        return
    sr = d["S_rigid_pbed3"]["S_meV_per_atom"]
    rr = d.get("retention_ratio_abs")
    text = TAB.read_text(encoding="utf-8")
    note = (
        "Matched-functional rigid reference (PBE+D3, same four corners): "
        f"$\\mathcal{{S}}_{{\\mathrm{{rigid}}}}^{{\\mathrm{{PBE+D3}}}}={sr:+.2f}$~meV/atom; "
        f"$|\\mathcal{{S}}_{{\\mathrm{{relaxed}}}}|/|\\mathcal{{S}}_{{\\mathrm{{rigid}}}}^{{\\mathrm{{PBE+D3}}}}|\\approx {rr:.1f}$ "
        "(sign \\emph{not} preserved on the matched-functional grid)."
    )
    old = "until a matched-functional rigid grid is recomputed."
    new = f"until a matched-functional rigid grid is recomputed. {note}"
    if old in text and note not in text:
        text = text.replace(old, new, 1)
        TAB.write_text(text, encoding="utf-8")
        print(f"updated {TAB.relative_to(REPO)}")
    else:
        print("caption already updated or pattern missing")


if __name__ == "__main__":
    main()
