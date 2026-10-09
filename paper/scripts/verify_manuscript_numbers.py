#!/usr/bin/env python3
"""Check every quantitative claim in the PRB main text against canonical audit data.

Each check names the manuscript location it guards and the JSON or archived DFT
output it reads, so a failure points at both sides of the discrepancy. Run it
before any submission or referee reply; it exits non-zero on the first mismatch
class so it can gate a build.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PAPER = REPO / "paper"
HARTREE_MEV = 27211.386245988
FLOOR_MEV = 2.0

sys.path.insert(0, str(PAPER / "figures"))


def audit(rel: str) -> dict:
    return json.loads((REPO / "experiments" / "analysis" / rel).read_text())


class Report:
    def __init__(self) -> None:
        self.passed: list[str] = []
        self.failed: list[str] = []

    def check(self, name: str, ok: bool, detail: str) -> None:
        (self.passed if ok else self.failed).append(f"{name}: {detail}")

    def emit(self) -> int:
        for line in self.passed:
            print(f"[PASS] {line}")
        for line in self.failed:
            print(f"[FAIL] {line}")
        print(f"\nPASS={len(self.passed)}  FAIL={len(self.failed)}")
        return 1 if self.failed else 0


def corner_rows() -> dict[tuple[int, str], tuple[float, float, float, float, float]]:
    """Four-corner totals and the printed S from the machine-readable SI table."""
    pat = re.compile(
        r"^\s*(\d+) & ([BNP]) & \$\+3\$ & (\S+) & (\S+) & (\S+) & (\S+) & \$([-+][\d.]+)\$"
    )
    rows: dict[tuple[int, str], tuple[float, float, float, float, float]] = {}
    for line in (PAPER / "tables" / "tab_S_corner_energies.tex").read_text().splitlines():
        m = pat.match(line)
        if m:
            rows[(int(m.group(1)), m.group(2))] = (
                float(m.group(3)),
                float(m.group(4)),
                float(m.group(5)),
                float(m.group(6)),
                float(m.group(7)),
            )
    return rows


def main() -> int:
    r = Report()
    tex = (PAPER / "strain_doped_graphullerene.tex").read_text()
    sdc = audit("sdc/sdc_exp10_synergy_audit.json")
    S = {(x["n_molecules"], x["dopant"]): x["synergy_S_meV_per_atom"] for x in sdc["synergy_table"]}

    # Table IV rows must equal the canonical synergy audit.
    grid = (PAPER / "tables" / "tab_S_synergy_grid.tex").read_text()
    for n in (1, 2, 4):
        for d in "BNP":
            m = re.search(rf"^{n} & {d} & \$\+3\$ & 1\.67 & \$([-+][\d.]+)\$", grid, re.M)
            got = float(m.group(1)) if m else None
            r.check(
                f"Table IV n={n} {d}",
                got is not None and abs(got - S[(n, d)]) < 0.011,
                f"table={got} audit={S[(n, d)]:.2f}",
            )

    # S printed in the SI corner table must be reproducible from its own corners.
    rows = corner_rows()
    for (n, d), (e00, ee0, e0d, eed, printed) in sorted(rows.items()):
        recomputed = (eed - ee0 - e0d + e00) * HARTREE_MEV
        r.check(
            f"corner self-consistency n={n} {d}",
            abs(recomputed - printed) < 0.011,
            f"recomputed={recomputed:+.2f} printed={printed:+.2f}",
        )

    # Additive-failure fraction eta quoted in Results.
    eta = {
        k: abs((v[3] - v[1] - v[2] + v[0]) * HARTREE_MEV) / abs((v[3] - v[0]) * HARTREE_MEV) * 100
        for k, v in rows.items()
    }
    r.check(
        "eta(P) = 8-12% in Results",
        all(8.0 <= eta[(n, "P")] <= 12.0 for n in (1, 2, 4, 6, 8)),
        ", ".join(f"{eta[(n, 'P')]:.1f}" for n in (1, 2, 4, 6, 8)),
    )
    r.check(
        "eta(B) below 1% in Results",
        all(eta[(n, "B")] < 1.0 for n in (1, 2, 4, 6, 8)),
        ", ".join(f"{eta[(n, 'B')]:.2f}" for n in (1, 2, 4, 6, 8)),
    )
    r.check(
        "eta(N) below 1% in Results",
        all(eta[(n, "N")] < 1.0 for n in (1, 2, 4, 6, 8)),
        ", ".join(f"{eta[(n, 'N')]:.2f}" for n in (1, 2, 4, 6, 8)),
    )

    # Significance stratification quoted in the Abstract and Results.
    r.check(
        "P |S| = 12-16x floor",
        all(11.5 <= abs(S[(n, "P")]) / FLOOR_MEV <= 16.1 for n in (1, 2, 4, 6, 8)),
        ", ".join(f"{abs(S[(n, 'P')]) / FLOOR_MEV:.1f}" for n in (1, 2, 4, 6, 8)),
    )
    r.check(
        "B |S| = 1-6x floor",
        all(1.0 <= abs(S[(n, "B")]) / FLOOR_MEV <= 6.0 for n in (1, 2, 4, 6, 8)),
        ", ".join(f"{abs(S[(n, 'B')]) / FLOOR_MEV:.1f}" for n in (1, 2, 4, 6, 8)),
    )

    # Pristine-reference consistency: the quantity is n-independent by construction.
    ref = audit("reference_consistency_audit.json")
    plateau = [ref["per_n"][k]["strain_cost_meV_per_atom"] for k in ("1", "4", "6")]
    r.check(
        "reference plateau reproducible to 0.06 meV/atom",
        max(plateau) - min(plateau) <= 0.12,
        f"n=1,4,6 -> {plateau}",
    )
    for n, expected in (("2", 4.2), ("8", 5.4)):
        got = ref["per_n"][n]["systematic_uncertainty_meV_per_atom"]
        r.check(
            f"reference offset n={n} quoted in Table I",
            abs(got - expected) < 0.06 and f"${expected}$" in tex,
            f"audit={got:.2f} expected={expected}",
        )
    r.check(
        "N sign-change claim withdrawn",
        "N changes sign at" not in tex,
        "no stale sign-change sentence in main text",
    )

    # Alternate placement must track the closed seed-137 grid, not a partial one.
    from _load_audit import load_seed137_alpha_S, parse_exp7_gaps  # noqa: PLC0415

    alpha137, s137 = load_seed137_alpha_S()
    placement = (PAPER / "tables" / "tab_IV.tex").read_text()
    for d, a_exp, s_exp in (("B", -45, 1.9), ("N", -60, 0.3), ("P", 1028, -32.3)):
        r.check(
            f"alternate placement {d}",
            abs(a_exp - alpha137[d]) < 0.6
            and abs(s_exp - s137[d]) < 0.06
            and f"${a_exp:+d}$" in placement,
            f"table={a_exp:+d}/{s_exp:+} audit={alpha137[d]:+.1f}/{s137[d]:+.2f}",
        )

    # alpha must be quoted with its fit standard error.
    from _load_audit import load_reference_pbed3_alpha_S  # noqa: PLC0415

    alpha, _, _, alpha_err = load_reference_pbed3_alpha_S()
    for d, a_exp, e_exp in (("B", 59, 116), ("N", -297, 110), ("P", 456, 870)):
        r.check(
            f"alpha({d}) with standard error",
            abs(a_exp - alpha[d]) < 1.0 and abs(e_exp - alpha_err[d]) < 2.0,
            f"tex={a_exp:+}+-{e_exp} audit={alpha[d]:+.1f}+-{alpha_err[d]:.0f}",
        )
    r.check(
        "only N resolved beyond 2 sigma",
        abs(alpha["N"]) / alpha_err["N"] > 2
        and abs(alpha["B"]) / alpha_err["B"] < 2
        and abs(alpha["P"]) / alpha_err["P"] < 2,
        f"B={abs(alpha['B']) / alpha_err['B']:.2f} N={abs(alpha['N']) / alpha_err['N']:.2f} "
        f"P={abs(alpha['P']) / alpha_err['P']:.2f} sigma",
    )

    # Relaxation controls.
    matched = audit("relax_validation_matched_functional.json")
    tetramer = audit("relax_validation_tetramer.json")
    periodic = audit("periodic_relax_validation_n1_P.json")
    r.check(
        "Table II matched rigid S = +1.19",
        abs(matched["S_rigid_pbed3"]["S_meV_per_atom"] - 1.19) < 0.01,
        f"{matched['S_rigid_pbed3']['S_meV_per_atom']:.4f}",
    )
    r.check(
        "Table II relaxed S = -2.28",
        abs(tetramer["S_relaxed"]["S_meV_per_atom"] + 2.28) < 0.01,
        f"{tetramer['S_relaxed']['S_meV_per_atom']:.4f}",
    )
    r.check(
        "periodic n=1 P relaxation extinguishes S",
        abs(periodic["S_rigid"]["S_meV_per_atom"] + 31.9) < 0.05
        and abs(periodic["S_relaxed"]["S_meV_per_atom"]) < 0.01,
        f"rigid={periodic['S_rigid']['S_meV_per_atom']:.2f} "
        f"relaxed={periodic['S_relaxed']['S_meV_per_atom']:.5f}",
    )

    # Frontier separations must come from committed spectra, not absent .out files.
    gaps = {(p.dopant, p.strain_pct): p.gap_ev for p in parse_exp7_gaps()}
    r.check("Fig. 1(c) traceable to archived PDOS", len(gaps) == 12, f"{len(gaps)} points")
    for d, quoted in (("B", 0.03), ("N", -0.14), ("P", 0.05)):
        r.check(
            f"E_H-L({d}, eps=0)",
            abs(gaps[(d, 0.0)] - quoted) < 0.006,
            f"tex={quoted:+.2f} pdos={gaps[(d, 0.0)]:+.4f}",
        )
    r.check(
        "substituted cages within 0.2 eV of gap closure",
        all(abs(gaps[(d, e)]) <= 0.2 for d in "BNP" for e in (-5.0, 0.0, 5.0)),
        f"max |E_H-L| = {max(abs(gaps[(d, e)]) for d in 'BNP' for e in (-5.0, 0.0, 5.0)):.3f} eV",
    )

    # Dispersion cross term.
    vdw = audit("s_vdw_decomposition.json")["analyses"][0]
    r.check(
        "S_vdW = +0.33 meV/atom",
        abs(vdw["S_vdW_meV_per_atom"] - 0.33) < 0.01,
        f"{vdw['S_vdW_meV_per_atom']:.4f}",
    )

    # Main-text boundary rules (no repository paths, scripts or revision status).
    forbidden = re.findall(
        r"experiments/|dft_results/|SCF run converged|PROGRAM ENDED|simukit|at revision|7/8",
        tex,
    )
    r.check("main text free of repository internals", not forbidden, f"hits={forbidden}")

    return r.emit()


if __name__ == "__main__":
    raise SystemExit(main())
