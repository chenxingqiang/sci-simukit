#!/usr/bin/env python3
"""Fill paper/tables/tab_IV.tex alternate column when seed137 grid is complete."""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
JSON = REPO / "experiments" / "analysis" / "seed_validation_tetramer.json"
TAB = REPO / "paper" / "tables" / "tab_IV.tex"


def fmt_alpha(v: float | None) -> str:
    if v is None:
        return "pending"
    return f"${v:+.1f}$"


def fmt_s(v: float | None) -> str:
    if v is None:
        return "pending"
    return f"${v:+.1f}$"


def main() -> None:
    d = json.loads(JSON.read_text())
    if d.get("status") != "complete":
        print(f"skip: status={d.get('status')} (need complete 18/18)")
        return
    if any(d.get("alpha_provisional", {}).values()):
        print("skip: alpha_provisional still true")
        return

    a137 = d["tetramer_alpha_meV_per_pct"]["seed137"]
    s137 = d["tetramer_S_meV_per_atom_at_eps3"]["seed137"]
    text = TAB.read_text(encoding="utf-8")

    for dop in ("B", "N", "P"):
        old = f"{dop} & alternate & pending & pending & pending"
        new = f"{dop} & alternate & {fmt_alpha(a137.get(dop))} & {fmt_s(s137.get(dop))} & verified (seed~137)"
        if old not in text:
            old2 = f"{dop} & alternate & pending & pending & pending \\\\"
            new2 = f"{dop} & alternate & {fmt_alpha(a137.get(dop))} & {fmt_s(s137.get(dop))} & verified (seed~137) \\\\"
            if old2 in text:
                text = text.replace(old2, new2)
            else:
                print(f"warn: row not found for {dop}")
        else:
            text = text.replace(old, new)

    TAB.write_text(text, encoding="utf-8")
    print(f"updated {TAB.relative_to(REPO)}")


if __name__ == "__main__":
    main()
