#!/usr/bin/env python3
"""Parse Hirshfeld charges on dopant site vs strain (n=1 periodic B/N/P)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
INP_DIR = Path(__file__).resolve().parent / "inputs"
STRAINS = (-5.0, -2.5, 0.0, 2.5, 3.0, 5.0)
DOPANTS = ("B", "N", "P")


def strain_tag(eps: float) -> str:
    s = f"{eps:+.1f}".replace("+", "p").replace("-", "m")
    return f"strain{s}pct"


def parse_hirshfeld(out: Path, dopant_idx: int, element: str) -> float | None:
    if not out.exists() or "SCF run converged" not in out.read_text(errors="replace"):
        return None
    text = out.read_text(errors="replace")
    blocks = re.split(r"# Atom\s+Element\s+Kind\s+Atomic charge", text)
    if len(blocks) < 2:
        for line in text.splitlines():
            if re.match(rf"^\s+\d+\s+{element}\s", line):
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
        if len(parts) >= 5 and parts[1] == element:
            return float(parts[-1])
    return None


def analyze_dopant(dopant: str) -> dict:
    meta_path = INP_DIR / f"dopant_site_index_{dopant}.json"
    if not meta_path.exists() and dopant == "P":
        meta_path = INP_DIR / "dopant_site_index.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {"dopant_index": 0}
    dop_idx = int(meta.get("dopant_index", 0))
    points = []
    for strain in STRAINS:
        base = f"pop_n1_{dopant}_{strain_tag(strain)}"
        out = INP_DIR / f"{base}.out"
        q = parse_hirshfeld(out, dop_idx, dopant)
        points.append(
            {
                "strain_pct": strain,
                "task": base,
                "converged": out.exists() and "SCF run converged" in out.read_text(errors="replace"),
                f"hirshfeld_charge_{dopant}": q,
            }
        )
    converged = sum(1 for p in points if p["converged"])
    return {
        "system": f"1xC60 {dopant} substitutional",
        "seed": meta.get("seed", 42),
        "dopant_index": dop_idx,
        "status": "complete" if converged == len(STRAINS) else ("partial" if converged else "pending"),
        "mayer_note": "Mayer bond orders: post-process CP2K WFN with Lobster/Multiwfn",
        "strain_path": points,
    }


def main() -> None:
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(DOPANTS)
    for dop in targets:
        report = analyze_dopant(dop)
        out_json = REPO / "experiments/analysis" / f"population_{dop}_n1_strain.json"
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {out_json.relative_to(REPO)} status={report['status']}")


if __name__ == "__main__":
    main()
