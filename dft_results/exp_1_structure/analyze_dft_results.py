#!/usr/bin/env python3
"""
Experiment 1: Structural Properties Analysis
Analyzes DFT results for pristine C60 dimer under different biaxial strains
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import re
import logging
import json
from typing import Dict, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
HA_TO_EV = 27.2114

def extract_energy_from_cp2k_output(output_file: Path) -> Optional[float]:
    """Extracts the final total energy from a CP2K output file."""
    if not output_file.exists():
        return None
    with open(output_file, 'r') as f:
        content = f.read()
        match = re.search(r'ENERGY\| Total FORCE_EVAL \( QS \) energy \[a.u.\]:\s*([-+]?\d+\.\d+)', content)
        if match:
            return float(match.group(1))
    return None

def extract_n_atoms_from_cp2k_output(output_file: Path) -> Optional[int]:
    """Extracts the number of atoms from a CP2K output file."""
    if not output_file.exists():
        return None
    with open(output_file, 'r') as f:
        content = f.read()
        match = re.search(r'Number of atoms\s*=\s*(\d+)', content)
        if match:
            return int(match.group(1))
    return None

def extract_convergence_info(output_file: Path) -> Tuple[bool, Optional[int]]:
    """Extracts convergence status and SCF steps from a CP2K output file."""
    converged = False
    scf_steps = None
    if not output_file.exists():
        return converged, scf_steps
    with open(output_file, 'r') as f:
        content = f.read()
        if 'SCF run converged' in content:
            converged = True
        matches = re.findall(r'^\s*(\d+)\s+OT', content, re.MULTILINE)
        if matches:
            scf_steps = int(matches[-1])
    return converged, scf_steps

def parse_filename(filename: str) -> Dict:
    """Parses filename to extract strain."""
    # Example: C60_strain_+2.5_pristine.out
    strain = 0.0
    
    match = re.search(r'strain_([-+]?\d+\.?\d*)_pristine', filename)
    if match:
        strain = float(match.group(1).replace('+', ''))
    
    return {'strain': strain}

def analyze_dft_results(outputs_dir: Path) -> Dict:
    """Analyzes DFT output files for Experiment 1."""
    results = {}
    output_files = list(outputs_dir.glob("C60_strain_*.out"))
    
    if not output_files:
        logger.error(f"No output files found in {outputs_dir}")
        return None

    logger.info(f"Found {len(output_files)} output files")

    for output_file in output_files:
        file_info = parse_filename(output_file.name)
        strain = file_info['strain']
        
        total_energy_Ha = extract_energy_from_cp2k_output(output_file)
        n_atoms = extract_n_atoms_from_cp2k_output(output_file)
        converged, scf_steps = extract_convergence_info(output_file)

        key = f"strain_{strain:+.1f}"
        
        if total_energy_Ha is not None:
            results[key] = {
                "strain": strain,
                "total_energy_Ha": total_energy_Ha,
                "total_energy_eV": total_energy_Ha * HA_TO_EV,
                "n_atoms": n_atoms,
                "energy_per_atom_Ha": total_energy_Ha / n_atoms if n_atoms else None,
                "energy_per_atom_eV": (total_energy_Ha / n_atoms * HA_TO_EV) if n_atoms else None,
                "converged": converged,
                "scf_steps": scf_steps,
                "output_file": output_file.name,
                "status": "success" if converged else "running"
            }
            status = "✓" if converged else "◐"
            logger.info(f"  {status} strain {strain:+.1f}%: E = {total_energy_Ha:.6f} Ha ({n_atoms} atoms)")
        else:
            logger.warning(f"  ✗ Cannot extract energy from {output_file.name}")
            results[key] = {
                "strain": strain,
                "status": "failed",
                "output_file": output_file.name
            }
    
    return results

def calculate_strain_response(df: pd.DataFrame) -> Dict:
    """Calculates strain response properties."""
    df_sorted = df.sort_values('strain')
    
    # Relative energy to 0% strain
    e0 = df[df['strain'] == 0.0]['total_energy_Ha'].iloc[0]
    df['relative_energy_Ha'] = df['total_energy_Ha'] - e0
    df['relative_energy_meV'] = df['relative_energy_Ha'] * HA_TO_EV * 1000
    
    # Fit quadratic: E = E0 + a*ε + b*ε²
    strains = df_sorted['strain'].values
    energies = df_sorted['total_energy_Ha'].values
    
    # Quadratic fit
    coeffs = np.polyfit(strains, energies, 2)
    a, b, c = coeffs  # E = a*ε² + b*ε + c
    
    # Strain sensitivity: dE/dε at ε=0 is b
    # Elastic constant proxy: d²E/dε² is 2a
    
    response = {
        'equilibrium_energy_Ha': c,
        'linear_coefficient_Ha_per_percent': b,
        'quadratic_coefficient_Ha_per_percent2': a,
        'strain_sensitivity_meV_per_percent': b * HA_TO_EV * 1000,
        'elastic_modulus_proxy_meV_per_percent2': 2 * a * HA_TO_EV * 1000
    }
    
    return response, df

def generate_plots(df: pd.DataFrame, strain_response: Dict, output_dir: Path) -> Dict:
    """Generates plots for Experiment 1 analysis."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    df_sorted = df.sort_values('strain')
    strains = df_sorted['strain'].values
    
    # Plot 1: Total Energy vs Strain
    ax1 = axes[0, 0]
    ax1.plot(strains, df_sorted['total_energy_Ha'], 'ko-', linewidth=2, markersize=10, label='DFT')
    
    # Fit curve
    fit_strains = np.linspace(strains.min(), strains.max(), 100)
    a = strain_response['quadratic_coefficient_Ha_per_percent2']
    b = strain_response['linear_coefficient_Ha_per_percent']
    c = strain_response['equilibrium_energy_Ha']
    fit_energies = a * fit_strains**2 + b * fit_strains + c
    ax1.plot(fit_strains, fit_energies, 'r--', linewidth=1.5, alpha=0.7, label='Quadratic fit')
    
    ax1.set_xlabel('Biaxial Strain (%)', fontsize=11)
    ax1.set_ylabel('Total Energy (Ha)', fontsize=11)
    ax1.set_title('Total Energy vs Biaxial Strain (C60 Dimer)', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    # Plot 2: Relative Energy in meV
    ax2 = axes[0, 1]
    ax2.bar(strains, df_sorted['relative_energy_meV'], color='steelblue', alpha=0.8, width=1.5)
    ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Biaxial Strain (%)', fontsize=11)
    ax2.set_ylabel('Relative Energy (meV)', fontsize=11)
    ax2.set_title('Energy Change Relative to 0% Strain', fontsize=12, fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.7, axis='y')
    
    # Plot 3: Energy per atom
    ax3 = axes[1, 0]
    if df_sorted['energy_per_atom_eV'].notna().any():
        ax3.plot(strains, df_sorted['energy_per_atom_eV'], 'go-', linewidth=2, markersize=10)
        ax3.set_ylabel('Energy per Atom (eV)', fontsize=11)
    else:
        ax3.plot(strains, df_sorted['total_energy_Ha'] / 120, 'go-', linewidth=2, markersize=10)
        ax3.set_ylabel('Energy per Atom (Ha)', fontsize=11)
    ax3.set_xlabel('Biaxial Strain (%)', fontsize=11)
    ax3.set_title('Energy per Atom vs Strain', fontsize=12, fontweight='bold')
    ax3.grid(True, linestyle='--', alpha=0.7)
    
    # Plot 4: Summary
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    summary_text = "DFT Calculation Summary (Exp1: Structure)\n"
    summary_text += "=" * 45 + "\n\n"
    summary_text += f"System: C60 Dimer (120 atoms)\n"
    summary_text += f"Calculations: {len(df)}\n\n"
    
    summary_text += "Strain Response:\n"
    summary_text += f"  Linear: {strain_response['strain_sensitivity_meV_per_percent']:.3f} meV/%\n"
    summary_text += f"  Quadratic: {strain_response['elastic_modulus_proxy_meV_per_percent2']:.3f} meV/%²\n\n"
    
    # Find minimum
    min_idx = df_sorted['total_energy_Ha'].idxmin()
    min_strain = df.loc[min_idx, 'strain']
    min_energy = df.loc[min_idx, 'total_energy_Ha']
    
    summary_text += f"Minimum Energy:\n"
    summary_text += f"  Strain: {min_strain:+.1f}%\n"
    summary_text += f"  Energy: {min_energy:.6f} Ha\n\n"
    
    summary_text += "Energy at Each Strain:\n"
    for _, row in df_sorted.iterrows():
        summary_text += f"  {row['strain']:+5.1f}%: {row['relative_energy_meV']:+.3f} meV\n"
    
    ax4.text(0.1, 0.9, summary_text, transform=ax4.transAxes, fontsize=10,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plot_file = output_dir / "real_dft_analysis.png"
    plt.savefig(plot_file, dpi=300)
    plt.close()
    logger.info(f"  Plot saved: {plot_file}")
    
    return {'main_plot': str(plot_file)}

def generate_summary(df: pd.DataFrame, strain_response: Dict) -> Dict:
    """Generates a summary of the analysis."""
    summary = {
        "total_calculations": len(df),
        "successful_calculations": len(df[df['status'] == 'success']),
        "system": "C60 Dimer (pristine)",
        "n_atoms": 120,
        "strain_values": sorted(df['strain'].unique().tolist()),
    }
    
    # Strain response
    summary['strain_response'] = {
        'linear_meV_per_percent': strain_response['strain_sensitivity_meV_per_percent'],
        'quadratic_meV_per_percent2': strain_response['elastic_modulus_proxy_meV_per_percent2']
    }
    
    # Most stable strain
    min_idx = df['total_energy_Ha'].idxmin()
    summary['most_stable_strain'] = {
        'strain': df.loc[min_idx, 'strain'],
        'energy_Ha': df.loc[min_idx, 'total_energy_Ha']
    }
    
    # Energy range
    summary['energy_range_meV'] = df['relative_energy_meV'].max() - df['relative_energy_meV'].min()
    
    return summary

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Analyze DFT results for Experiment 1.")
    parser.add_argument('--dir', type=str, default='.', help="Base directory containing 'outputs' folder.")
    args = parser.parse_args()

    base_dir = Path(args.dir)
    outputs_dir = base_dir / "outputs"
    results_dir = base_dir / "results"
    figures_dir = base_dir / "figures"

    results_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("Experiment 1: Structural Properties DFT Analysis")
    logger.info("=" * 60)
    
    # Analyze DFT results
    dft_raw_results = analyze_dft_results(outputs_dir)
    if dft_raw_results is None:
        logger.error("No valid data found!")
        return

    # Convert to DataFrame
    df = pd.DataFrame(list(dft_raw_results.values()))
    
    # Calculate strain response
    logger.info("\nCalculating strain response...")
    strain_response, df = calculate_strain_response(df)
    logger.info(f"  Linear coefficient: {strain_response['strain_sensitivity_meV_per_percent']:.3f} meV/%")
    logger.info(f"  Elastic modulus proxy: {strain_response['elastic_modulus_proxy_meV_per_percent2']:.3f} meV/%²")
    
    # Generate summary
    analysis_summary = generate_summary(df, strain_response)
    
    # Generate plots
    logger.info("\nGenerating plots...")
    generated_plots = generate_plots(df, strain_response, figures_dir)

    # Save results
    logger.info("\nSaving results...")
    
    # Save detailed results
    detailed_results_file = results_dir / "real_dft_results.json"
    with open(detailed_results_file, 'w') as f:
        json.dump(df.to_dict(orient='records'), f, indent=2)
    logger.info(f"  Detailed results: {detailed_results_file}")

    # Save analysis summary
    summary_file = results_dir / "analysis_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(analysis_summary, f, indent=2)
    logger.info(f"  Analysis summary: {summary_file}")

    logger.info("\n" + "=" * 60)
    logger.info("Analysis Complete!")
    logger.info("=" * 60)
    logger.info(f"  Successful: {analysis_summary['successful_calculations']}/{analysis_summary['total_calculations']}")
    logger.info(f"  Most stable strain: {analysis_summary['most_stable_strain']['strain']:+.1f}%")
    logger.info(f"  Energy range: {analysis_summary['energy_range_meV']:.3f} meV")

if __name__ == "__main__":
    main()

