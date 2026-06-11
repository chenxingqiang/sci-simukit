#!/usr/bin/env python3
"""Write experiments/analysis/exp10_status.json from converged gates on size_*.out."""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "experiments/exp_10_size_scaling/inputs"
OUT = ROOT / "experiments/analysis/exp10_status.json"
OT_RE = re.compile(r"^\s+(\d+) OT \S+\s+\S+\s+\S+\s+(\S+)", re.M)


def main() -> None:
    rows = []
    for inp in sorted(INPUTS.glob("size_*.inp")):
        task = inp.stem
        out = INPUTS / f"{task}.out"
        converged = False
        last_ot = None
        last_grad = None
        if out.is_file():
            text = out.read_text(errors="replace")
            converged = "SCF run converged" in text
            # Use only the latest run segment when .out files are appended across restarts.
            start = text.rfind("PROGRAM STARTED AT")
            ot_text = text[start:] if start >= 0 else text
            matches = list(OT_RE.finditer(ot_text))
            if matches:
                last_ot = int(matches[-1].group(1))
                last_grad = float(matches[-1].group(2))
        rows.append(
            {
                "task": task,
                "converged": converged,
                "last_ot_step": last_ot,
                "last_grad": last_grad,
            }
        )
    conv = sum(r["converged"] for r in rows)
    pending_rows = [r for r in rows if not r["converged"] and r.get("last_ot_step")]
    running_task = None
    if pending_rows:
        running_task = max(pending_rows, key=lambda r: r["last_ot_step"] or 0)["task"]
    payload = {
        "updated": date.today().isoformat(),
        "converged": conv,
        "total": len(rows),
        "pending": [r["task"] for r in rows if not r["converged"]],
        "tasks": rows,
    }
    if running_task:
        payload["running_task"] = running_task
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"{OUT}: {conv}/{len(rows)} converged")


if __name__ == "__main__":
    main()
