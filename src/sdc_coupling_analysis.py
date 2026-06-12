#!/usr/bin/env python3
"""
Strain-Doping Coupling (SDC) analysis tool for graphullerene DFT results.

NOTE: Production path is the C implementation (canonical, DFT-coupled):
  cd c && make && ./simukit-sdc ../experiments/exp_10_size_scaling/inputs
See c/include/simukit/ and AGENTS.md § C 核心工程.

This Python script remains for plotting (matplotlib) and parity checks.

Computes the synergy order parameter S for observable P:

    S(P; epsilon, delta) = Delta P(epsilon, delta)
                           - [Delta P(epsilon, 0) + Delta P(0, delta)]

where Delta P is the change from the pristine, zero-strain reference at the
same system size. Maps to H_eff = H0 + V_dop + V_str + V_coup in paper/AGENTS.

Usage:
    python src/sdc_coupling_analysis.py --exp10 experiments/exp_10_size_scaling/inputs
    python src/sdc_coupling_analysis.py --plots-from-json experiments/analysis/sdc/sdc_exp10_results.json
    python src/sdc_coupling_analysis.py --dir experiments/exp_5_synergy
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

_REPO_ROOT = Path(__file__).resolve().parents[1]
_PRL_STYLE_DIR = _REPO_ROOT / "paper" / "figures"
if str(_PRL_STYLE_DIR) not in sys.path:
    sys.path.insert(0, str(_PRL_STYLE_DIR))
from prl_style import (  # noqa: E402
    PRL_SINGLE_COL,
    apply_prl_style,
    finalize_axes,
    get_color,
    get_marker,
    save_figure,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

HA_TO_EV = 27.211386245988


@dataclass
class ParsedOutput:
    path: str
    converged: bool
    n_atoms: int = 0
    total_energy_ha: Optional[float] = None
    energy_per_atom_ha: Optional[float] = None
    homo_ev: Optional[float] = None
    lumo_ev: Optional[float] = None
    bandgap_ev: Optional[float] = None
    j_coupling_meV: Optional[float] = None
    # size-scaling metadata (optional)
    n_molecules: Optional[int] = None
    dopant: Optional[str] = None
    strain_pct: Optional[float] = None


@dataclass
class SynergyRecord:
    property_name: str
    n_molecules: int
    dopant: str
    strain_pct: float
    reference: float
    combined: float
    strain_only_delta: float
    doping_only_delta: float
    synergy_S: float
    source_files: Dict[str, str] = field(default_factory=dict)


class CP2KOutputParser:
    """Minimal CP2K .out parser for SDC workflow."""

    ENERGY_RE = re.compile(
        r"ENERGY\| Total FORCE_EVAL \( QS \) energy \[a.u.\]:\s*([-+]?\d+\.\d+)"
    )
    ATOMS_RE = re.compile(r"- Atoms:\s+(\d+)")

    @classmethod
    def parse(cls, path: Path) -> ParsedOutput:
        text = path.read_text(errors="replace")
        converged = "SCF run converged" in text and "PROGRAM ENDED" in text
        n_atoms = 0
        m = cls.ATOMS_RE.search(text)
        if m:
            n_atoms = int(m.group(1))

        total_ha = None
        em = cls.ENERGY_RE.search(text)
        if em:
            total_ha = float(em.group(1))

        epa = total_ha / n_atoms if total_ha is not None and n_atoms > 0 else None

        homo, lumo, bg, j_meV = cls._parse_mo_eigenvalues(text, n_atoms)

        return ParsedOutput(
            path=str(path),
            converged=converged,
            n_atoms=n_atoms,
            total_energy_ha=total_ha,
            energy_per_atom_ha=epa,
            homo_ev=homo,
            lumo_ev=lumo,
            bandgap_ev=bg,
            j_coupling_meV=j_meV,
        )

    @staticmethod
    def _parse_mo_eigenvalues(
        text: str, n_atoms: int
    ) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
        """Extract HOMO/LUMO from MO eigenvalue block (Hartree -> eV)."""
        eigenvalues: List[float] = []
        in_block = False
        for line in text.splitlines():
            if "MO EIGENVALUES" in line or "Occupation" in line and "Eigenvalues" in line:
                in_block = True
                continue
            if in_block:
                if not line.strip() or "Fermi" in line or line.startswith(" ---"):
                    if eigenvalues:
                        break
                    continue
                for part in line.split():
                    try:
                        eigenvalues.append(float(part))
                    except ValueError:
                        pass

        if not eigenvalues or n_atoms <= 0:
            return None, None, None, None

        n_electrons = n_atoms * 4
        homo_idx = n_electrons // 2 - 1
        if homo_idx < 0 or homo_idx >= len(eigenvalues):
            return None, None, None, None

        homo = eigenvalues[homo_idx] * HA_TO_EV
        lumo = eigenvalues[homo_idx + 1] * HA_TO_EV if homo_idx + 1 < len(eigenvalues) else None
        homo_1 = eigenvalues[homo_idx - 1] * HA_TO_EV if homo_idx - 1 >= 0 else None
        bg = (lumo - homo) if lumo is not None else None
        j_meV = abs(homo - homo_1) / 2 * 1000 if homo_1 is not None else None
        return homo, lumo, bg, j_meV


class SDCAnalyzer:
    """Strain-doping coupling analyzer."""

    SIZE_NAME_RE = re.compile(
        r"size_(?P<n>\d+)x60_(?P<dopant>pristine|[BNP])_(?P<strain>pos|neg)(?P<val>\d+)pct",
        re.IGNORECASE,
    )
    EXP5_NAME_RE = re.compile(
        r".*_(?P<strain>[-+]?\d+\.?\d*)_(?P<dopant>pristine|[BNP])\.out$",
        re.IGNORECASE,
    )

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "figures").mkdir(exist_ok=True)

    def scan_exp10_directory(self, inputs_dir: Path) -> Dict[str, ParsedOutput]:
        records: Dict[str, ParsedOutput] = {}
        for out_path in sorted(inputs_dir.glob("size_*.out")):
            meta = self.parse_size_scaling_filename(out_path.name)
            if meta is None:
                continue
            parsed = CP2KOutputParser.parse(out_path)
            parsed.n_molecules = meta["n_molecules"]
            parsed.dopant = meta["dopant"]
            parsed.strain_pct = meta["strain_pct"]
            key = self._size_key(meta["n_molecules"], meta["dopant"], meta["strain_pct"])
            records[key] = parsed
        return records

    @staticmethod
    def parse_size_scaling_filename(name: str) -> Optional[Dict]:
        m = SDCAnalyzer.SIZE_NAME_RE.match(name.replace(".out", "").replace(".inp", ""))
        if not m:
            return None
        sign = -1 if m.group("strain").lower() == "neg" else 1
        return {
            "n_molecules": int(m.group("n")),
            "dopant": m.group("dopant").capitalize() if m.group("dopant") != "pristine" else "pristine",
            "strain_pct": sign * float(m.group("val")),
        }

    @staticmethod
    def _size_key(n: int, dopant: str, strain: float) -> str:
        return f"n{n}_{dopant}_eps{strain:+.0f}"

    def compute_synergy(
        self,
        records: Dict[str, ParsedOutput],
        property_name: str,
        strain_pct: float = 3.0,
    ) -> List[SynergyRecord]:
        """Compute S for each (n, dopant) at fixed strain."""
        getter = self._property_getter(property_name)
        unit = self._property_unit(property_name)
        results: List[SynergyRecord] = []

        sizes = sorted({r.n_molecules for r in records.values() if r.n_molecules})
        dopants = sorted({r.dopant for r in records.values() if r.dopant and r.dopant != "pristine"})

        for n in sizes:
            ref = records.get(self._size_key(n, "pristine", 0.0))
            strain_pristine = records.get(self._size_key(n, "pristine", strain_pct))
            if not ref or not ref.converged or getter(ref) is None:
                continue
            p_ref = getter(ref)

            delta_str = (
                getter(strain_pristine) - p_ref
                if strain_pristine and strain_pristine.converged and getter(strain_pristine) is not None
                else None
            )

            for dop in dopants:
                d0 = records.get(self._size_key(n, dop, 0.0))
                combined = records.get(self._size_key(n, dop, strain_pct))
                if not all([d0, combined]) or not combined.converged or not d0.converged:
                    continue
                p_d0 = getter(d0)
                p_comb = getter(combined)
                if p_d0 is None or p_comb is None:
                    continue

                delta_comb = p_comb - p_ref
                delta_dop = p_d0 - p_ref
                if delta_str is None:
                    continue

                synergy = delta_comb - (delta_str + delta_dop)
                results.append(
                    SynergyRecord(
                        property_name=f"{property_name} ({unit})",
                        n_molecules=n,
                        dopant=dop,
                        strain_pct=strain_pct,
                        reference=p_ref,
                        combined=p_comb,
                        strain_only_delta=delta_str,
                        doping_only_delta=delta_dop,
                        synergy_S=synergy,
                        source_files={
                            "ref": ref.path,
                            "combined": combined.path,
                            "doping_only": d0.path,
                            "strain_only": strain_pristine.path if strain_pristine else "",
                        },
                    )
                )
        return results

    @staticmethod
    def _property_getter(name: str):
        mapping = {
            "energy_per_atom_ha": lambda r: r.energy_per_atom_ha,
            "total_energy_ha": lambda r: r.total_energy_ha,
            "bandgap_ev": lambda r: r.bandgap_ev,
            "j_coupling_meV": lambda r: r.j_coupling_meV,
        }
        if name not in mapping:
            raise ValueError(f"Unknown property: {name}")
        return mapping[name]

    @staticmethod
    def _property_unit(name: str) -> str:
        return {
            "energy_per_atom_ha": "Ha/atom",
            "total_energy_ha": "Ha",
            "bandgap_ev": "eV",
            "j_coupling_meV": "meV",
        }.get(name, "")

    def fit_size_scaling(
        self, synergy_records: List[SynergyRecord]
    ) -> Dict[str, Dict]:
        """Fit S(n) ~ S_inf + A * n^(-alpha) per dopant."""
        fits: Dict[str, Dict] = {}
        by_dopant: Dict[str, List[Tuple[int, float]]] = {}
        for rec in synergy_records:
            by_dopant.setdefault(rec.dopant, []).append((rec.n_molecules, rec.synergy_S))

        for dop, points in by_dopant.items():
            if len(points) < 2:
                continue
            ns = np.array([p[0] for p in points], dtype=float)
            ss = np.array([p[1] for p in points], dtype=float)

            def model(n, s_inf, a, alpha):
                return s_inf + a * np.power(n, -alpha)

            try:
                popt, _ = _curve_fit_safe(model, ns, ss, p0=[ss[-1], ss[0] - ss[-1], 1.0])
                fits[dop] = {
                    "S_infinity": float(popt[0]),
                    "A": float(popt[1]),
                    "alpha": float(popt[2]),
                    "n_points": len(points),
                }
            except Exception as exc:
                logger.warning("Size scaling fit failed for %s: %s", dop, exc)
        return fits

    def plot_synergy_vs_size(
        self, synergy_records: List[SynergyRecord], fits: Dict[str, Dict], tag: str
    ) -> Path:
        apply_prl_style()
        fig, ax = plt.subplots(figsize=(PRL_SINGLE_COL, PRL_SINGLE_COL * 0.78))

        by_dop: Dict[str, List[SynergyRecord]] = {}
        for rec in synergy_records:
            by_dop.setdefault(rec.dopant, []).append(rec)

        ha_to_meV = HA_TO_EV * 1000.0

        for dop, recs in sorted(by_dop.items()):
            recs.sort(key=lambda r: r.n_molecules)
            ns = np.array([r.n_molecules for r in recs], dtype=float)
            if "Ha" in recs[0].property_name:
                ss = np.array([r.synergy_S * ha_to_meV for r in recs])
            else:
                ss = np.array([r.synergy_S for r in recs])

            color = get_color(dop)
            marker = get_marker(dop)
            ax.plot(
                ns,
                ss,
                linestyle="-",
                linewidth=0.9,
                color=color,
                marker=marker,
                markersize=5,
                markerfacecolor="white",
                markeredgecolor=color,
                markeredgewidth=0.9,
                label=f"{dop}",
                zorder=3,
            )

            fit = fits.get(dop)
            if fit and len(ns) >= 2:
                n_fine = np.linspace(max(1.0, ns.min()), ns.max() * 1.15, 80)
                s_inf = fit["S_infinity"]
                a_coef = fit["A"]
                if "Ha" in recs[0].property_name:
                    s_inf *= ha_to_meV
                    a_coef *= ha_to_meV
                s_pred = s_inf + a_coef * np.power(n_fine, -fit["alpha"])
                ax.plot(
                    n_fine,
                    s_pred,
                    linestyle="--",
                    linewidth=0.75,
                    color=color,
                    alpha=0.85,
                    zorder=2,
                )

        ax.axhline(0, color="#666666", linestyle="-", linewidth=0.5, zorder=1)
        ax.set_xlabel(r"Supercell size $n$ ($n \times \mathrm{C}_{60}$)")
        ax.set_ylabel(r"Synergy $\mathcal{S}$ (meV/atom)")
        ax.set_xticks(sorted({r.n_molecules for r in synergy_records}))
        ax.legend(loc="best", handlelength=1.8, borderpad=0.4)
        finalize_axes(ax)

        fig.tight_layout(pad=0.35)
        out = self.output_dir / "figures" / f"sdc_synergy_vs_size_{tag}.pdf"
        save_figure(fig, out)
        return out

    def plot_strain_sensitivity(self, records: Dict[str, ParsedOutput]) -> Optional[Path]:
        """dE/dε per dopant from pristine 0% and +3% (meV/% per atom scale)."""
        rows: Dict[str, List[Tuple[float, float]]] = {}
        for key, rec in records.items():
            if not rec.converged or rec.strain_pct is None or rec.n_molecules is None:
                continue
            if rec.dopant is None or rec.energy_per_atom_ha is None:
                continue
            rows.setdefault(rec.dopant, []).append((rec.strain_pct, rec.energy_per_atom_ha * HA_TO_EV))

        if not rows:
            return None

        apply_prl_style()
        fig, ax = plt.subplots(figsize=(PRL_SINGLE_COL, PRL_SINGLE_COL * 0.78))
        sensitivities: Dict[str, float] = {}

        for dop, pts in sorted(rows.items()):
            by_strain: Dict[float, List[float]] = {}
            for eps, e in pts:
                by_strain.setdefault(eps, []).append(e)
            strains = sorted(by_strain.keys())
            if len(strains) < 2:
                continue
            means = [float(np.mean(by_strain[s])) for s in strains]
            color = get_color(dop)
            marker = get_marker(dop)
            ax.plot(
                strains,
                means,
                linestyle="-",
                linewidth=0.9,
                color=color,
                marker=marker,
                markersize=5,
                markerfacecolor="white" if dop == "pristine" else color,
                markeredgecolor=color,
                markeredgewidth=0.9,
                label=dop if dop != "pristine" else "pristine",
            )
            coeffs = np.polyfit(strains, means, 1)
            sensitivities[dop] = float(coeffs[0] * 1000)

        ax.set_xlabel(r"Biaxial strain $\varepsilon$ (\%)")
        ax.set_ylabel(r"Energy per atom (eV)")
        ax.legend(loc="best", handlelength=1.8, borderpad=0.4)
        finalize_axes(ax)
        fig.tight_layout(pad=0.35)
        out = self.output_dir / "figures" / "sdc_strain_sensitivity_exp10.pdf"
        save_figure(fig, out)

        with open(self.output_dir / "strain_sensitivity_meV_per_pct.json", "w") as f:
            json.dump(sensitivities, f, indent=2)
        return out

    @staticmethod
    def synergy_records_from_json(data: dict) -> List[SynergyRecord]:
        strain_pct = float(data.get("strain_pct", 3.0))
        records: List[SynergyRecord] = []
        for row in data.get("synergy_energy_per_atom", []):
            records.append(
                SynergyRecord(
                    property_name="energy_per_atom_ha",
                    n_molecules=int(row["n_molecules"]),
                    dopant=str(row["dopant"]),
                    strain_pct=float(row.get("strain_pct", strain_pct)),
                    reference=float(row["reference"]),
                    combined=float(row["combined"]),
                    strain_only_delta=float(row["strain_only_delta"]),
                    doping_only_delta=float(row["doping_only_delta"]),
                    synergy_S=float(row["synergy_S"]),
                )
            )
        return records

    def write_synergy_audit_json(
        self,
        synergy_epa: List[SynergyRecord],
        fits: Dict[str, Dict],
        strain_pct: float,
    ) -> Path:
        """Machine-readable synergy table (meV/atom) + provisional size-scaling fits."""
        rows = []
        for rec in sorted(synergy_epa, key=lambda r: (r.n_molecules, r.dopant)):
            rows.append(
                {
                    "n_molecules": rec.n_molecules,
                    "dopant": rec.dopant,
                    "strain_pct": rec.strain_pct,
                    "synergy_S_ha_per_atom": rec.synergy_S,
                    "synergy_S_meV_per_atom": rec.synergy_S * HA_TO_EV * 1000.0,
                }
            )
        audit = {
            "strain_pct": strain_pct,
            "n_synergy_points": len(rows),
            "synergy_table": rows,
            "size_scaling_fits": fits,
            "S_infinity_status": "provisional_pending_40_of_40",
            "note": "Canonical synergy from simukit-sdc; do not cite S_infinity until Exp10 complete.",
        }
        out = self.output_dir / "sdc_exp10_synergy_audit.json"
        with open(out, "w") as f:
            json.dump(audit, f, indent=2)
        logger.info("Wrote synergy audit -> %s", out)
        return out

    def plots_from_canonical_json(self, json_path: Path) -> Path:
        """Regenerate synergy-vs-size figures from simukit-sdc JSON only."""
        data = json.loads(json_path.read_text())
        strain_pct = float(data.get("strain_pct", 3.0))
        synergy_epa = self.synergy_records_from_json(data)
        if not synergy_epa:
            raise ValueError(f"No synergy_energy_per_atom in {json_path}")
        fits = self.fit_size_scaling(synergy_epa)
        tag = f"eps{int(strain_pct)}pct_epa"
        out = self.plot_synergy_vs_size(synergy_epa, fits, tag)
        self.write_synergy_audit_json(synergy_epa, fits, strain_pct)
        logger.info(
            "Plotted %d synergy points from %s -> %s",
            len(synergy_epa),
            json_path,
            out,
        )
        return out

    def run_exp10(self, inputs_dir: Path, strain_pct: float = 3.0) -> Dict:
        records = self.scan_exp10_directory(inputs_dir)
        converged = sum(1 for r in records.values() if r.converged)
        logger.info("Exp10: %d parsed, %d converged", len(records), converged)

        synergy_epa = self.compute_synergy(records, "energy_per_atom_ha", strain_pct)
        synergy_bg = self.compute_synergy(records, "bandgap_ev", strain_pct)

        fits = self.fit_size_scaling(synergy_epa)
        tag = f"eps{int(strain_pct)}pct_epa"
        if synergy_epa:
            self.plot_synergy_vs_size(synergy_epa, fits, tag)
        self.plot_strain_sensitivity(records)

        payload = {
            "inputs_dir": str(inputs_dir),
            "strain_pct": strain_pct,
            "n_parsed": len(records),
            "n_converged": converged,
            "synergy_energy_per_atom": [asdict(r) for r in synergy_epa],
            "synergy_bandgap": [asdict(r) for r in synergy_bg],
            "size_scaling_fits": fits,
            "records_summary": {
                k: {
                    "converged": v.converged,
                    "n_molecules": v.n_molecules,
                    "dopant": v.dopant,
                    "strain_pct": v.strain_pct,
                    "energy_per_atom_ha": v.energy_per_atom_ha,
                    "bandgap_ev": v.bandgap_ev,
                    "path": v.path,
                }
                for k, v in records.items()
            },
        }

        json_path = self.output_dir / "sdc_exp10_results_python.json"
        canonical = self.output_dir / "sdc_exp10_results.json"
        with open(json_path, "w") as f:
            json.dump(payload, f, indent=2)

        csv_path = self.output_dir / "sdc_synergy_table.csv"
        with open(csv_path, "w") as f:
            f.write("property,n_molecules,dopant,strain_pct,synergy_S,ref,combined\n")
            for rec in synergy_epa + synergy_bg:
                f.write(
                    f"{rec.property_name},{rec.n_molecules},{rec.dopant},{rec.strain_pct},"
                    f"{rec.synergy_S},{rec.reference},{rec.combined}\n"
                )

        logger.info(
            "Wrote %s, %s (canonical synergy JSON: ./c/simukit-sdc → %s)",
            json_path,
            csv_path,
            canonical.name,
        )
        return payload


def _curve_fit_safe(model, x, y, p0):
    from scipy.optimize import curve_fit

    return curve_fit(model, x, y, p0=p0, maxfev=10000)


def main():
    parser = argparse.ArgumentParser(description="SDC strain-doping coupling analysis")
    parser.add_argument(
        "--exp10",
        type=Path,
        default=Path("experiments/exp_10_size_scaling/inputs"),
        help="Exp10 inputs directory with size_*.out",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/analysis/sdc"),
        help="Output directory for JSON/figures",
    )
    parser.add_argument("--strain", type=float, default=3.0, help="Strain %% for synergy (default +3)")
    parser.add_argument(
        "--plots-from-json",
        type=Path,
        default=None,
        help="Regenerate synergy figures from simukit-sdc JSON (read-only; no canonical overwrite)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    exp10_dir = args.exp10 if args.exp10.is_absolute() else repo_root / args.exp10
    out_dir = args.out_dir if args.out_dir.is_absolute() else repo_root / args.out_dir

    analyzer = SDCAnalyzer(out_dir)

    if args.plots_from_json is not None:
        json_path = (
            args.plots_from_json
            if args.plots_from_json.is_absolute()
            else repo_root / args.plots_from_json
        )
        analyzer.plots_from_canonical_json(json_path)
        return

    payload = analyzer.run_exp10(exp10_dir, strain_pct=args.strain)

    n_syn = len(payload["synergy_energy_per_atom"])
    logger.info("Synergy records (energy/atom): %d", n_syn)
    for rec in payload["synergy_energy_per_atom"][:5]:
        logger.info(
            "  n=%s %s S=%.2e Ha/atom",
            rec["n_molecules"],
            rec["dopant"],
            rec["synergy_S"],
        )


if __name__ == "__main__":
    main()
