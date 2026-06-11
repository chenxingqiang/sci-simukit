#!/usr/bin/env python3
"""
Experiment 3: Electronic Properties Analysis
Analyzes DFT results for C60 dimer under different strains and doping types
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

# PRL Style Configuration
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'axes.linewidth': 0.8,
    'xtick.major.width': 0.6,
    'ytick.major.width': 0.6,
    'xtick.minor.width': 0.4,
    'ytick.minor.width': 0.4,
    'lines.linewidth': 1.2,
    'lines.markersize': 6,
    'axes.grid': False,
    'axes.spines.top': True,
    'axes.spines.right': True,
})

# Professional color palette
COLORS = {'pristine': '#1f77b4', 'B': '#d62728', 'N': '#2ca02c', 'P': '#9467bd'}
MARKERS = {'pristine': 'o', 'B': 's', 'N': '^', 'P': 'D'}

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
    """Extracts convergence status and SCF steps."""
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
    """Parses filename to extract strain and dopant."""
    # Example: C60_strain_+2.5_B_doped.out or C60_strain_+2.5_pristine.out
    strain = 0.0
    dopant = 'pristine'
    
    # Extract strain
    match_strain = re.search(r'strain_([-+]?\d+\.?\d*)', filename)
    if match_strain:
        strain = float(match_strain.group(1).replace('+', ''))
    
    # Extract dopant
    if '_pristine' in filename:
        dopant = 'pristine'
    else:
        match_dopant = re.search(r'_([A-Z])_doped', filename)
        if match_dopant:
            dopant = match_dopant.group(1)
    
    return {'strain': strain, 'dopant': dopant}

def analyze_dft_results(outputs_dir: Path) -> Dict:
    """Analyzes DFT output files for Experiment 3."""
    results = {}
    output_files = list(outputs_dir.glob("C60_strain_*.out"))
    
    if not output_files:
        logger.error(f"No output files found in {outputs_dir}")
        return None

    logger.info(f"Found {len(output_files)} output files")

    for output_file in output_files:
        file_info = parse_filename(output_file.name)
        strain = file_info['strain']
        dopant = file_info['dopant']
        
        total_energy_Ha = extract_energy_from_cp2k_output(output_file)
        n_atoms = extract_n_atoms_from_cp2k_output(output_file)
        converged, scf_steps = extract_convergence_info(output_file)

        key = f"strain_{strain:+.1f}_{dopant}"
        
        if total_energy_Ha is not None:
            results[key] = {
                "strain": strain,
                "dopant": dopant,
                "total_energy_Ha": total_energy_Ha,
                "total_energy_eV": total_energy_Ha * HA_TO_EV,
                "n_atoms": n_atoms,
                "converged": converged,
                "scf_steps": scf_steps,
                "output_file": output_file.name,
                "status": "success" if converged else "running"
            }
            status = "✓" if converged else "◐"
            logger.info(f"  {status} {dopant} @ {strain:+.1f}%: E = {total_energy_Ha:.6f} Ha")
        else:
            logger.warning(f"  ✗ Cannot extract energy from {output_file.name}")
            results[key] = {
                "strain": strain,
                "dopant": dopant,
                "status": "failed",
                "output_file": output_file.name
            }
    
    return results

def calculate_strain_effects(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates strain effects for each dopant type."""
    # Calculate relative energy to pristine at each strain
    df['doping_effect_eV'] = np.nan
    
    for strain in df['strain'].unique():
        pristine_energy = df[(df['dopant'] == 'pristine') & (df['strain'] == strain)]['total_energy_Ha']
        if len(pristine_energy) > 0:
            pristine_e = pristine_energy.iloc[0]
            mask = df['strain'] == strain
            df.loc[mask, 'doping_effect_eV'] = (df.loc[mask, 'total_energy_Ha'] - pristine_e) * HA_TO_EV
    
    return df

def calculate_strain_sensitivity(df: pd.DataFrame) -> Dict:
    """Calculates strain sensitivity for each dopant type."""
    sensitivities = {}
    
    for dopant in df['dopant'].unique():
        subset = df[df['dopant'] == dopant].sort_values('strain')
        if len(subset) >= 2:
            # Linear fit: E = a * strain + b
            coeffs = np.polyfit(subset['strain'], subset['total_energy_Ha'], 1)
            slope_Ha = coeffs[0]  # dE/dstrain
            sensitivities[dopant] = {
                'slope_Ha_per_percent': slope_Ha,
                'slope_meV_per_percent': slope_Ha * HA_TO_EV * 1000
            }
    
    return sensitivities

def generate_plots(df: pd.DataFrame, sensitivities: Dict, output_dir: Path) -> Dict:
    """Generates plots for Experiment 3 analysis (PRL Style)."""
    fig, axes = plt.subplots(2, 2, figsize=(7.0, 5.5))
    
    # Plot 1: RELATIVE Energy vs Strain for each dopant (relative to 0% strain)
    ax1 = axes[0, 0]
    for dopant in ['pristine', 'B', 'N', 'P']:
        subset = df[df['dopant'] == dopant].sort_values('strain')
        if len(subset) > 0:
            # Calculate relative energy to 0% strain
            e0 = subset[subset['strain'] == 0.0]['total_energy_Ha']
            if len(e0) > 0:
                e0_val = e0.iloc[0]
                rel_energy_meV = (subset['total_energy_Ha'] - e0_val) * HA_TO_EV * 1000
                ax1.plot(subset['strain'], rel_energy_meV, 
                        marker=MARKERS.get(dopant, 'o'), linestyle='-', 
                        color=COLORS.get(dopant, 'gray'), label=dopant,
                        markerfacecolor='white' if dopant == 'pristine' else COLORS.get(dopant),
                        markeredgewidth=1.2)
    ax1.axhline(y=0, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
    ax1.set_xlabel('Biaxial Strain (%)')
    ax1.set_ylabel('Relative Energy (meV)')
    ax1.legend(loc='best', frameon=False)
    ax1.minorticks_on()
    ax1.text(-0.15, 1.05, '(a)', transform=ax1.transAxes, fontweight='bold', fontsize=11)
    
    # Plot 2: Energy Heatmap (strain vs dopant)
    ax2 = axes[0, 1]
    dopants = ['pristine', 'B', 'N', 'P']
    strains = sorted(df['strain'].unique())
    
    # Build matrix of relative energies (meV, relative to pristine at 0%)
    e_ref = df[(df['dopant'] == 'pristine') & (df['strain'] == 0.0)]['total_energy_Ha'].iloc[0]
    matrix = np.zeros((len(dopants), len(strains)))
    
    for i, dopant in enumerate(dopants):
        for j, strain in enumerate(strains):
            row = df[(df['dopant'] == dopant) & (df['strain'] == strain)]
            if len(row) > 0:
                matrix[i, j] = (row['total_energy_Ha'].iloc[0] - e_ref) * HA_TO_EV * 1000  # meV
    
    im = ax2.imshow(matrix, cmap='RdBu_r', aspect='auto')
    ax2.set_xticks(range(len(strains)))
    ax2.set_xticklabels([f'{s:+.0f}' for s in strains], fontsize=8)
    ax2.set_yticks(range(len(dopants)))
    ax2.set_yticklabels(dopants)
    ax2.set_xlabel('Strain (%)')
    ax2.set_ylabel('Dopant')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax2, shrink=0.8, pad=0.02)
    cbar.set_label('Energy (meV)', fontsize=9)
    cbar.ax.tick_params(labelsize=8)
    
    ax2.text(-0.15, 1.05, '(b)', transform=ax2.transAxes, fontweight='bold', fontsize=11)
    
    # Plot 3: Strain Sensitivity Comparison
    ax3 = axes[1, 0]
    dopants = ['pristine', 'B', 'N', 'P']
    sensitivity_values = [sensitivities.get(d, {}).get('slope_meV_per_percent', 0) for d in dopants]
    bar_colors = [COLORS.get(d, 'gray') for d in dopants]
    bars = ax3.bar(dopants, sensitivity_values, color=bar_colors, alpha=0.85, edgecolor='black', linewidth=0.5)
    ax3.axhline(y=0, color='gray', linestyle='--', linewidth=0.8, alpha=0.7)
    ax3.set_xlabel('Dopant Type')
    ax3.set_ylabel('Strain Sensitivity (meV/%)')
    ax3.minorticks_on()
    ax3.text(-0.15, 1.05, '(c)', transform=ax3.transAxes, fontweight='bold', fontsize=11)
    
    # Add value labels
    for bar, val in zip(bars, sensitivity_values):
        y_pos = bar.get_height() if val >= 0 else bar.get_height() - 5
        va = 'bottom' if val >= 0 else 'top'
        ax3.text(bar.get_x() + bar.get_width()/2, y_pos, 
                f'{val:.1f}', ha='center', va=va, fontsize=8)
    
    # Plot 4: Summary text box
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    summary_text = "Experiment 3: Electronic Properties\n"
    summary_text += "─" * 35 + "\n\n"
    
    completed = len(df[df['status'] == 'success'])
    total = len(df)
    summary_text += f"Calculations: {completed}/{total}\n\n"
    
    summary_text += "Strain Sensitivity (meV/%):\n"
    for dopant in ['pristine', 'B', 'N', 'P']:
        sens = sensitivities.get(dopant, {}).get('slope_meV_per_percent', np.nan)
        summary_text += f"  {dopant}: {sens:+.2f}\n"
    
    summary_text += "\nDoping Effects at 0%:\n"
    zero_strain = df[df['strain'] == 0.0]
    for dopant in ['B', 'N', 'P']:
        row = zero_strain[zero_strain['dopant'] == dopant]
        if len(row) > 0:
            effect = row['doping_effect_eV'].iloc[0]
            summary_text += f"  {dopant}: {effect:+.0f} eV\n"
    
    # Enhancement factors
    pristine_sens = abs(sensitivities.get('pristine', {}).get('slope_meV_per_percent', 1))
    if pristine_sens > 0:
        summary_text += "\nEnhancement Factor:\n"
        for dopant in ['B', 'N', 'P']:
            sens = abs(sensitivities.get(dopant, {}).get('slope_meV_per_percent', 0))
            enhancement = sens / pristine_sens if pristine_sens > 0 else 0
            summary_text += f"  {dopant}: {enhancement:.0f}×\n"
    
    ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, fontsize=9,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='#f8f8f8', edgecolor='gray', alpha=0.9))
    
    plt.tight_layout()
    
    # Save in multiple formats
    plot_file = output_dir / "real_dft_analysis.png"
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / "real_dft_analysis.pdf", dpi=300, bbox_inches='tight', format='pdf')
    plt.close()
    logger.info(f"  Plot saved: {plot_file}")
    
    return {'main_plot': str(plot_file)}

def generate_summary(df: pd.DataFrame, sensitivities: Dict) -> Dict:
    """Generates a summary of the analysis."""
    summary = {
        "total_calculations": len(df),
        "successful_calculations": len(df[df['status'] == 'success']),
        "dopant_types": sorted(df['dopant'].unique().tolist()),
        "strain_values": sorted(df['strain'].unique().tolist()),
    }
    
    # Strain sensitivities
    summary['strain_sensitivities_meV_per_percent'] = {
        k: v['slope_meV_per_percent'] for k, v in sensitivities.items()
    }
    
    # Most stable configuration
    completed = df[df['status'] == 'success']
    if len(completed) > 0:
        most_stable = completed.loc[completed['total_energy_Ha'].idxmin()]
        summary['most_stable'] = {
            'dopant': most_stable['dopant'],
            'strain': most_stable['strain'],
            'energy_Ha': most_stable['total_energy_Ha']
        }
    
    # Doping effects at 0% strain
    zero_strain = df[df['strain'] == 0.0]
    summary['doping_effects_0_strain_eV'] = {}
    for dopant in ['B', 'N', 'P']:
        row = zero_strain[zero_strain['dopant'] == dopant]
        if len(row) > 0 and 'doping_effect_eV' in row.columns:
            summary['doping_effects_0_strain_eV'][dopant] = row['doping_effect_eV'].iloc[0]
    
    return summary

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Analyze DFT results for Experiment 3.")
    parser.add_argument('--dir', type=str, default='.', help="Base directory containing 'outputs' folder.")
    args = parser.parse_args()

    base_dir = Path(args.dir)
    outputs_dir = base_dir / "outputs"
    results_dir = base_dir / "results"
    figures_dir = base_dir / "figures"

    results_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("Experiment 3: Electronic Properties DFT Analysis")
    logger.info("=" * 60)
    
    # Analyze DFT results
    dft_raw_results = analyze_dft_results(outputs_dir)
    if dft_raw_results is None:
        logger.error("No valid data found!")
        return

    # Convert to DataFrame
    df = pd.DataFrame(list(dft_raw_results.values()))
    
    # Calculate strain effects
    logger.info("\nCalculating strain effects...")
    df = calculate_strain_effects(df)
    
    # Calculate strain sensitivity
    logger.info("\nCalculating strain sensitivities...")
    sensitivities = calculate_strain_sensitivity(df)
    for dopant, sens in sensitivities.items():
        logger.info(f"  {dopant}: {sens['slope_meV_per_percent']:+.2f} meV/%")
    
    # Generate summary
    analysis_summary = generate_summary(df, sensitivities)
    
    # Generate plots
    logger.info("\nGenerating plots...")
    generated_plots = generate_plots(df, sensitivities, figures_dir)

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
        logger.info(f"  Most stable: {ms['dopant']} @ {ms['strain']:+.1f}%")

if __name__ == "__main__":
    main()

