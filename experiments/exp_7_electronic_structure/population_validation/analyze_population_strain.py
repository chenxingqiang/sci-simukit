#!/usr/bin/env python3
"""Parse Hirshfeld charges on P dopant site vs strain (n=1 periodic)."""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
INP_DIR = Path(__file__).resolve().parent / "inputs"
OUT_JSON = REPO / "experiments" / "analysis" / "population_P_n1_strain.json"
META = INP_DIR / "dopant_site_index.json"
STRAINS = (-5.0, -2.5, 0.0, 2.5, 3.0, 5.0)


def strain_tag(eps: float) -> str:
    s = f"{eps:+.1f}".replace("+", "p").replace("-", "m")
    return f"strain{s}pct"


def parse_hirshfeld_p(out: Path, dopant_idx: int) -> float | None:
    if not out.exists() or "SCF run converged" not in out.read_text(errors="replace"):
        return None
    text = out.read_text(errors="replace")
    # CP2K Hirshfeld: atom index in output blocks
    blocks = re.split(r"# Atom\s+Element\s+Kind\s+Atomic charge", text)
    if len(blocks) < 2:
        # fallback Mulliken on P line
        for line in text.splitlines():
            if re.match(r"^\s+\d+\s+P\s", line):
                parts = line.split()
                if len(parts) >= 5:
                    return float(parts[-1])
        return None
    tail = blocks[-1]
    lines = [ln for ln in tail.splitlines() if re.match(r"^\s+\d+\s+\w", ln)]
    for ln in lines:
        parts = ln.split()
        if len(parts) >= 5 and parts[0] == str(dopant_idx + 1):
            return float(parts[-1])
    for ln in lines:
        parts = ln.split()
        if len(parts) >= 5 and parts[1] == "P":
            return float(parts[-1])
    return None


def main() -> None:
    meta = json.loads(META.read_text()) if META.exists() else {"dopant_index": 0}
    dop_idx = int(meta.get("dopant_index", 0))

    points = []
    for strain in STRAINS:
        base = f"pop_n1_P_{strain_tag(strain)}"
        out = INP_DIR / f"{base}.out"
        q = parse_hirshfeld_p(out, dop_idx)
        points.append(
            {
                "strain_pct": strain,
                "task": base,
                "converged": out.exists() and "SCF run converged" in out.read_text(errors="replace"),
                "hirshfeld_charge_P": q,
            }
        )

    converged = sum(1 for p in points if p["converged"])
    report = {
        "system": "1xC60 P substitutional",
        "seed": meta.get("seed", 42),
        "dopant_index": dop_idx,
        "status": "complete" if converged == len(STRAINS) else ("partial" if converged else "pending"),
        "mayer_note": "Mayer bond orders: post-process CP2K WFN with Lobster/Multiwfn (see docs/prb_review_cn_mapping.md)",
        "strain_path": points,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
