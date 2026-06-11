#!/usr/bin/env python3
"""
Experiment 2: Doping Effects Analysis
Analyzes DFT results for different dopant types (B, N, P) and concentrations (3%, 5%, 7%)
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
        # Find last SCF step
        matches = re.findall(r'^\s*(\d+)\s+OT', content, re.MULTILINE)
        if matches:
            scf_steps = int(matches[-1])
    return converged, scf_steps

def parse_filename(filename: str) -> Dict:
    """Parses filename to extract dopant and concentration."""
    # Example: C60_B_0.03_doped.out
    dopant = 'pristine'
    concentration = 0.0
    
    match = re.match(r'C60_(\w+)_(\d+\.\d+)_doped\.out', filename)
    if match:
        dopant = match.group(1)
        concentration = float(match.group(2))
    
    return {'dopant': dopant, 'concentration': concentration}

def analyze_dft_results(outputs_dir: Path) -> Dict:
    """Analyzes DFT output files for Experiment 2."""
    results = {}
    output_files = list(outputs_dir.glob("*.out"))
    
    if not output_files:
        logger.error(f"No output files found in {outputs_dir}")
        return None

    logger.info(f"Found {len(output_files)} output files")

    for output_file in output_files:
        file_info = parse_filename(output_file.name)
        dopant = file_info['dopant']
        concentration = file_info['concentration']
        
        total_energy_Ha = extract_energy_from_cp2k_output(output_file)
        n_atoms = extract_n_atoms_from_cp2k_output(output_file)
        converged, scf_steps = extract_convergence_info(output_file)

        key = f"{dopant}_{concentration:.2f}"
        
        if total_energy_Ha is not None:
            results[key] = {
                "dopant": dopant,
                "concentration": concentration,
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
            logger.info(f"  {status} {dopant}_{concentration:.0%}: E = {total_energy_Ha:.6f} Ha ({n_atoms} atoms)")
        else:
            logger.warning(f"  ✗ Cannot extract energy from {output_file.name}")
            results[key] = {
                "dopant": dopant,
                "concentration": concentration,
                "status": "failed",
                "output_file": output_file.name
            }
    
    return results

def calculate_formation_energy(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates formation energy relative to pristine at each concentration."""
    df['formation_energy_eV'] = np.nan
    
    for conc in df['concentration'].unique():
        pristine_energy = df[(df['dopant'] == 'pristine') & (df['concentration'] == conc)]['total_energy_eV']
        if len(pristine_energy) > 0:
            pristine_e = pristine_energy.iloc[0]
            mask = df['concentration'] == conc
            df.loc[mask, 'formation_energy_eV'] = df.loc[mask, 'total_energy_eV'] - pristine_e
    
    return df

def calculate_doping_effects(df: pd.DataFrame) -> Dict:
    """Calculates doping effects for each dopant type."""
    effects = {}
    
    for dopant in df['dopant'].unique():
        if dopant == 'pristine':
            continue
        
        subset = df[df['dopant'] == dopant].sort_values('concentration')
        if len(subset) >= 2:
            # Linear fit: E = a * concentration + b
            coeffs = np.polyfit(subset['concentration'], subset['total_energy_Ha'], 1)
            slope_Ha = coeffs[0]  # dE/d(concentration)
            effects[dopant] = {
                'slope_Ha_per_concentration': slope_Ha,
                'slope_eV_per_percent': slope_Ha * HA_TO_EV * 100,  # per 1% concentration
                'energies': subset['total_energy_Ha'].tolist(),
                'concentrations': subset['concentration'].tolist()
            }
    
    return effects

def generate_plots(df: pd.DataFrame, output_dir: Path) -> Dict:
    """Generates plots for Experiment 2 analysis."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    colors = {'pristine': 'black', 'B': 'red', 'N': 'blue', 'P': 'green'}
    markers = {'pristine': 'o', 'B': 's', 'N': '^', 'P': 'D'}
    
    # Plot 1: Total Energy vs Concentration
    ax1 = axes[0, 0]
    for dopant in df['dopant'].unique():
        subset = df[df['dopant'] == dopant].sort_values('concentration')
        ax1.plot(subset['concentration'] * 100, subset['total_energy_Ha'], 
                marker=markers.get(dopant, 'o'), linestyle='-', 
                color=colors.get(dopant, 'gray'), label=f'{dopant}', linewidth=2, markersize=8)
    ax1.set_xlabel('Doping Concentration (%)', fontsize=11)
    ax1.set_ylabel('Total Energy (Ha)', fontsize=11)
    ax1.set_title('Total Energy vs Doping Concentration', fontsize=12, fontweight='bold')
    ax1.legend(title='Dopant', fontsize=9)
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    # Plot 2: Formation Energy (relative to pristine)
    ax2 = axes[0, 1]
    for dopant in df['dopant'].unique():
        if dopant == 'pristine':
            continue
        subset = df[df['dopant'] == dopant].sort_values('concentration')
        ax2.plot(subset['concentration'] * 100, subset['formation_energy_eV'], 
                marker=markers.get(dopant, 'o'), linestyle='-', 
                color=colors.get(dopant, 'gray'), label=f'{dopant} doping', linewidth=2, markersize=8)
    ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5, label='Pristine reference')
    ax2.set_xlabel('Doping Concentration (%)', fontsize=11)
    ax2.set_ylabel('Formation Energy (eV)', fontsize=11)
    ax2.set_title('Formation Energy vs Doping Concentration', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, linestyle='--', alpha=0.7)
    
    # Plot 3: Energy per atom
    ax3 = axes[1, 0]
    for dopant in df['dopant'].unique():
        subset = df[df['dopant'] == dopant].sort_values('concentration')
        ax3.plot(subset['concentration'] * 100, subset['energy_per_atom_eV'], 
                marker=markers.get(dopant, 'o'), linestyle='-', 
                color=colors.get(dopant, 'gray'), label=f'{dopant}', linewidth=2, markersize=8)
    ax3.set_xlabel('Doping Concentration (%)', fontsize=11)
    ax3.set_ylabel('Energy per Atom (eV)', fontsize=11)
    ax3.set_title('Energy per Atom vs Doping Concentration', fontsize=12, fontweight='bold')
    ax3.legend(title='Dopant', fontsize=9)
    ax3.grid(True, linestyle='--', alpha=0.7)
    
    # Plot 4: Summary statistics
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    # Create summary text
    summary_text = "DFT Calculation Summary (Exp2: Doping)\n"
    summary_text += "=" * 45 + "\n\n"
    
    completed = len(df[df['status'] == 'success'])
    total = len(df)
    summary_text += f"Total Calculations: {total}\n"
    summary_text += f"Completed: {completed}\n"
    summary_text += f"Running: {total - completed}\n\n"
    
    summary_text += "Formation Energies at 5% doping:\n"
    for dopant in ['B', 'N', 'P']:
        row = df[(df['dopant'] == dopant) & (df['concentration'] == 0.05)]
        if len(row) > 0:
            fe = row['formation_energy_eV'].iloc[0]
            summary_text += f"  {dopant}: {fe:+.2f} eV\n"
    
    summary_text += "\nStability Order:\n"
    avg_fe = {}
    for dopant in ['B', 'N', 'P']:
        subset = df[df['dopant'] == dopant]
        if len(subset) > 0:
            avg_fe[dopant] = subset['formation_energy_eV'].mean()
    sorted_dopants = sorted(avg_fe.items(), key=lambda x: x[1])
    for i, (dopant, fe) in enumerate(sorted_dopants, 1):
        stability = "Most Stable" if i == 1 else ("Least Stable" if i == len(sorted_dopants) else "")
        summary_text += f"  {i}. {dopant}: {fe:+.2f} eV avg {stability}\n"
    
    ax4.text(0.1, 0.9, summary_text, transform=ax4.transAxes, fontsize=10,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plot_file = output_dir / "real_dft_analysis.png"
    plt.savefig(plot_file, dpi=300)
    plt.close()
    logger.info(f"  Plot saved: {plot_file}")
    
    return {'main_plot': str(plot_file)}

def generate_summary(df: pd.DataFrame, doping_effects: Dict) -> Dict:
    """Generates a summary of the analysis."""
    summary = {
        "total_calculations": len(df),
        "successful_calculations": len(df[df['status'] == 'success']),
        "dopant_types": df['dopant'].unique().tolist(),
        "concentrations": sorted(df['concentration'].unique().tolist()),
    }
    
    # Most stable configuration
    completed = df[df['status'] == 'success']
    if len(completed) > 0:
        most_stable = completed.loc[completed['total_energy_Ha'].idxmin()]
        summary['most_stable'] = {
            'dopant': most_stable['dopant'],
            'concentration': most_stable['concentration'],
            'energy_Ha': most_stable['total_energy_Ha']
        }
    
    # Doping stability ranking at 5% concentration
    stability_at_5pct = {}
    for dopant in ['B', 'N', 'P']:
        row = df[(df['dopant'] == dopant) & (df['concentration'] == 0.05)]
        if len(row) > 0 and row['status'].iloc[0] == 'success':
            stability_at_5pct[dopant] = row['formation_energy_eV'].iloc[0]
    summary['formation_energies_5pct'] = stability_at_5pct
    
    # Doping effects (concentration sensitivity)
    summary['doping_effects'] = {k: v['slope_eV_per_percent'] for k, v in doping_effects.items()}
    
    return summary

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Analyze DFT results for Experiment 2.")
    parser.add_argument('--dir', type=str, default='.', help="Base directory containing 'outputs' folder.")
    args = parser.parse_args()

    base_dir = Path(args.dir)
    outputs_dir = base_dir / "outputs"
    results_dir = base_dir / "results"
    figures_dir = base_dir / "figures"

    results_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("Experiment 2: Doping Effects DFT Analysis")
    logger.info("=" * 60)
    
    # Analyze DFT results
    dft_raw_results = analyze_dft_results(outputs_dir)
    if dft_raw_results is None:
        logger.error("No valid data found!")
        return

    # Convert to DataFrame
    df = pd.DataFrame(list(dft_raw_results.values()))
    
    # Calculate derived properties
    logger.info("\nCalculating formation energies...")
    df = calculate_formation_energy(df)
    
    logger.info("\nCalculating doping effects...")
    doping_effects = calculate_doping_effects(df)
    for dopant, effect in doping_effects.items():
        logger.info(f"  {dopant}: dE/d(conc) = {effect['slope_eV_per_percent']:.2f} eV/%")
    
    # Generate summary
    analysis_summary = generate_summary(df, doping_effects)
    
    # Generate plots
    logger.info("\nGenerating plots...")
    generated_plots = generate_plots(df, figures_dir)

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
    
    if 'most_stable' in analysis_summary:
        ms = analysis_summary['most_stable']
        logger.info(f"  Most stable: {ms['dopant']} at {ms['concentration']:.0%}")
    
    logger.info("\n  Formation Energies at 5%:")
    for dopant, fe in analysis_summary.get('formation_energies_5pct', {}).items():
        logger.info(f"    {dopant}: {fe:+.2f} eV")

if __name__ == "__main__":
    main()

