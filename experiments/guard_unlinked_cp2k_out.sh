#!/usr/bin/env bash
# Mirror CP2K .out files unlinked (link count 0) but still open — avoids total loss on rm during run.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

python3 << PY
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

def lsof_unlinked() -> list[tuple[int, int, str]]:
    try:
        raw = subprocess.check_output(["lsof", "+L1"], text=True, errors="replace")
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []
    rows: list[tuple[int, int, str]] = []
    for line in raw.splitlines():
        if "cp2k" not in line.lower() or ".out" not in line:
            continue
        m = re.match(
            r"^\S+\s+(\d+)\s+\S+\s+(\d+)w\s+\S+\s+\S+\s+\S+\s+0\s+\d+\s+(.+\.out)\s*$",
            line,
        )
        if m:
            rows.append((int(m.group(1)), int(m.group(2)), m.group(3).strip()))
    return rows

def mirror_linux(pid: int, fd: int, dest: Path) -> bool:
    src = Path(f"/proc/{pid}/fd/{fd}")
    if not src.exists():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    return True

hits = lsof_unlinked()
if not hits:
    print("guard_unlinked: no unlinked cp2k .out (OK)")
    raise SystemExit(0)

rc = 0
for pid, fd, path in hits:
    dest = Path(path)
    mirror = dest.with_suffix(dest.suffix + ".mirror")
    if mirror_linux(pid, fd, mirror):
        print(f"guard_unlinked: mirrored {path} -> {mirror} ({mirror.stat().st_size} B)")
    else:
        print(
            f"WARN unlinked cp2k .out pid={pid} fd={fd} path={path}\n"
            "  Do NOT rm/kill until job ends; avoid deleting .out while cp2k holds it.",
            flush=True,
        )
        rc = 1
raise SystemExit(rc)
PY
