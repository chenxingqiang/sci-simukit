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
OT_LINE_RE = re.compile(r"^\s+(\d+) OT \S+\s+\S+\s+([\d.]+)\s+(\S+)", re.M)

# Keep in sync with c/src/main_run.c default_pending[].
BATCH_ORDER = [
    "size_2x60_pristine_pos0pct",
    "size_2x60_pristine_pos3pct",
    "size_4x60_P_pos3pct",
    "size_6x60_B_pos3pct",
    "size_6x60_N_pos3pct",
    "size_8x60_B_pos0pct",
    "size_8x60_B_pos3pct",
    "size_8x60_N_pos3pct",
    "size_8x60_P_pos0pct",
    "size_8x60_P_pos3pct",
    "size_8x60_pristine_pos0pct",
    "size_8x60_pristine_pos3pct",
]


def reference_ot_task(task: str) -> str | None:
    """Map size_Nx60_D_posXpct -> size_Nx60_D_pos0pct (skip already-at-pos0)."""
    if "_pos" not in task or task.endswith("_pos0pct"):
        return None
    return task.rsplit("_pos", 1)[0] + "_pos0pct"


def read_eps_scf(task: str) -> float:
    inp = INPUTS / f"{task}.inp"
    if not inp.is_file():
        return 1e-6
    m = re.search(r"EPS_SCF\s+([\d.E+-]+)", inp.read_text(errors="replace"))
    return float(m.group(1)) if m else 1e-6


def avg_ot_step_seconds(out_path: Path, last_n: int = 10) -> float | None:
    if not out_path.is_file():
        return None
    text = out_path.read_text(errors="replace")
    start = text.rfind("PROGRAM STARTED AT")
    ot_text = text[start:] if start >= 0 else text
    times = [float(m.group(2)) for m in OT_LINE_RE.finditer(ot_text)]
    if not times:
        return None
    chunk = times[-last_n:]
    return sum(chunk) / len(chunk)


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
        rt = next(r for r in rows if r["task"] == running_task)
        snapshot = {
            "last_ot_step": rt.get("last_ot_step"),
            "last_grad": rt.get("last_grad"),
        }
        ref_task = reference_ot_task(running_task)
        if ref_task:
            ref_row = next((r for r in rows if r["task"] == ref_task), None)
            if ref_row and ref_row.get("converged") and ref_row.get("last_ot_step"):
                ref_ot = ref_row["last_ot_step"]
                snapshot["reference_task"] = ref_task
                snapshot["reference_ot_steps"] = ref_ot
                if rt.get("last_ot_step"):
                    snapshot["ot_progress_pct"] = round(
                        100.0 * rt["last_ot_step"] / ref_ot, 1
                    )
        eps = read_eps_scf(running_task)
        snapshot["eps_scf"] = eps
        if rt.get("last_grad") is not None and eps > 0:
            snapshot["grad_ratio_to_eps"] = round(rt["last_grad"] / eps, 1)
        ot_step = rt.get("last_ot_step") or 0
        ratio = snapshot.get("grad_ratio_to_eps") or 0
        if ot_step >= 200 and ratio > 10:
            snapshot["escalation_hint"] = (
                "OT>=200 and grad>10x EPS; if no SCF converged by OT~300, "
                "consider EPS 1e-5 rerun (see AGENTS pristine 2x60 protocol)"
            )
        avg_s = avg_ot_step_seconds(INPUTS / f"{running_task}.out")
        ref_ot = snapshot.get("reference_ot_steps")
        if avg_s and ref_ot and ot_step:
            remaining = max(0, int(ref_ot) - ot_step)
            snapshot["time_per_ot_step_s"] = round(avg_s, 1)
            snapshot["eta_minutes_to_ref_ot"] = round(remaining * avg_s / 60.0, 0)
        payload["running_snapshot"] = snapshot

    by_task = {r["task"]: r for r in rows}
    pending_refs = {}
    for task in payload["pending"]:
        ref_task = reference_ot_task(task)
        if not ref_task:
            continue
        ref_row = by_task.get(ref_task)
        if ref_row and ref_row.get("converged") and ref_row.get("last_ot_step"):
            pending_refs[task] = {
                "reference_task": ref_task,
                "reference_ot_steps": ref_row["last_ot_step"],
                "eps_scf": read_eps_scf(task),
            }
    if pending_refs:
        payload["pending_reference_ot"] = pending_refs

    pending_set = set(payload["pending"])
    batch_queue = [t for t in BATCH_ORDER if t in pending_set]
    for task in payload["pending"]:
        if task not in batch_queue:
            batch_queue.append(task)
    if batch_queue:
        payload["batch_queue"] = batch_queue
        if running_task and running_task in batch_queue:
            idx = batch_queue.index(running_task)
            if idx + 1 < len(batch_queue):
                payload["next_after_running"] = batch_queue[idx + 1]
        elif not running_task:
            payload["next_after_running"] = batch_queue[0]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"{OUT}: {conv}/{len(rows)} converged")


if __name__ == "__main__":
    main()
