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
    python src/sdc_coupling_analysis.py --dir experiments/exp_5_synergy
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

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
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = {"B": "#c0392b", "N": "#2980b9", "P": "#27ae60"}
        by_dop: Dict[str, List[SynergyRecord]] = {}
        for rec in synergy_records:
            by_dop.setdefault(rec.dopant, []).append(rec)

        for dop, recs in sorted(by_dop.items()):
            recs.sort(key=lambda r: r.n_molecules)
            ns = [r.n_molecules for r in recs]
            ss = [r.synergy_S * HA_TO_EV if "Ha" in r.property_name else r.synergy_S for r in recs]
            ax.plot(ns, ss, "o-", color=colors.get(dop, "gray"), label=f"{dop}-doped", linewidth=2)

            fit = fits.get(dop)
            if fit:
                n_fine = np.linspace(min(ns), max(ns) * 1.2, 50)
                s_inf = fit["S_infinity"]
                if "Ha" in recs[0].property_name:
                    s_inf *= HA_TO_EV
                    a = fit["A"] * HA_TO_EV
                else:
                    a = fit["A"]
                s_pred = s_inf + a * np.power(n_fine, -fit["alpha"])
                ax.plot(n_fine, s_pred, "--", color=colors.get(dop, "gray"), alpha=0.7)

        ax.axhline(0, color="gray", linestyle=":", linewidth=0.8)
        ax.set_xlabel("System size (n × C$_{60}$)")
        ax.set_ylabel("Synergy order parameter $S$")
        ax.set_title(f"SDC synergy vs size ({tag})")
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        out = self.output_dir / "figures" / f"sdc_synergy_vs_size_{tag}.pdf"
        fig.savefig(out, dpi=300, bbox_inches="tight")
        fig.savefig(out.with_suffix(".png"), dpi=300, bbox_inches="tight")
        plt.close(fig)
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

        fig, ax = plt.subplots(figsize=(7, 5))
        colors = {"pristine": "black", "B": "#c0392b", "N": "#2980b9", "P": "#27ae60"}
        sensitivities: Dict[str, float] = {}

        for dop, pts in sorted(rows.items()):
            by_strain: Dict[float, List[float]] = {}
            for eps, e in pts:
                by_strain.setdefault(eps, []).append(e)
            strains = sorted(by_strain.keys())
            if len(strains) < 2:
                continue
            means = [float(np.mean(by_strain[s])) for s in strains]
            ax.plot(strains, means, "o-", label=dop, color=colors.get(dop, "gray"))
            coeffs = np.polyfit(strains, means, 1)
            sensitivities[dop] = float(coeffs[0] * 1000)  # eV/% -> meV/%

        ax.set_xlabel("Biaxial strain (%)")
        ax.set_ylabel("Energy per atom (eV)")
        ax.set_title("Strain response by dopant (Exp10 converged points)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        out = self.output_dir / "figures" / "sdc_strain_sensitivity_exp10.pdf"
        fig.savefig(out, dpi=300, bbox_inches="tight")
        plt.close(fig)

        with open(self.output_dir / "strain_sensitivity_meV_per_pct.json", "w") as f:
            json.dump(sensitivities, f, indent=2)
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

        json_path = self.output_dir / "sdc_exp10_results.json"
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

        logger.info("Wrote %s and %s", json_path, csv_path)
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
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    exp10_dir = args.exp10 if args.exp10.is_absolute() else repo_root / args.exp10
    out_dir = args.out_dir if args.out_dir.is_absolute() else repo_root / args.out_dir

    analyzer = SDCAnalyzer(out_dir)
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
