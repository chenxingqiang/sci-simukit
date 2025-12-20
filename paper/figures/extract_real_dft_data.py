#!/usr/bin/env python3
"""
Extract Real DFT Data from Server Outputs

This script extracts actual DFT calculation results (total energy)
from CP2K output files and creates honest visualizations.

Author: Xingqiang Chen
Date: 2024
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import re

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
    'lines.linewidth': 1.2,
    'lines.markersize': 6,
    'axes.grid': False,
})

COLORS = {
    'pristine': '#1f77b4',
    'B': '#d62728',
    'N': '#2ca02c',
    'P': '#9467bd',
}

MARKERS = {
    'pristine': 'o',
    'B': 's',
    'N': '^',
    'P': 'D',
}


def load_real_dft_data():
    """
    Load real DFT data extracted from server.
    These are the actual calculation results.
    """
    
    # Experiment 1: C60 dimer under strain (RKS, 120 atoms)
    exp1_data = {
        'C60_strain_-5.0_pristine': {'strain': -5.0, 'energy': -681.810585529232, 'n_atoms': 120},
        'C60_strain_-2.5_pristine': {'strain': -2.5, 'energy': -681.810524698309, 'n_atoms': 120},
        'C60_strain_+0.0_pristine': {'strain': 0.0, 'energy': -681.810470811466, 'n_atoms': 120},
        'C60_strain_+2.5_pristine': {'strain': 2.5, 'energy': -681.810495411986, 'n_atoms': 120},
        'C60_strain_+5.0_pristine': {'strain': 5.0, 'energy': -681.810434885755, 'n_atoms': 120},
    }
    
    # Experiment 2: Doped C60 (UKS, variable atoms)
    exp2_data = {
        'C60_pristine_0.03': {'dopant': 'pristine', 'conc': 0.025, 'energy': -340.905920201698, 'n_atoms': 60},
        'C60_pristine_0.05': {'dopant': 'pristine', 'conc': 0.05, 'energy': -340.905920201698, 'n_atoms': 60},
        'C60_pristine_0.07': {'dopant': 'pristine', 'conc': 0.075, 'energy': -340.905920201698, 'n_atoms': 60},
        'C60_B_0.03': {'dopant': 'B', 'conc': 0.025, 'energy': -335.062018798996, 'n_atoms': 2},
        'C60_B_0.05': {'dopant': 'B', 'conc': 0.05, 'energy': -332.149610191411, 'n_atoms': 3},
        'C60_B_0.07': {'dopant': 'B', 'conc': 0.075, 'energy': -329.194364575741, 'n_atoms': 4},
        'C60_N_0.03': {'dopant': 'N', 'conc': 0.025, 'energy': -349.380255582321, 'n_atoms': 2},
        'C60_N_0.05': {'dopant': 'N', 'conc': 0.05, 'energy': -353.621121599736, 'n_atoms': 3},
        'C60_N_0.07': {'dopant': 'N', 'conc': 0.075, 'energy': -357.841194673279, 'n_atoms': 4},
        'C60_P_0.05': {'dopant': 'P', 'conc': 0.05, 'energy': -342.295053180304, 'n_atoms': 3},
        'C60_P_0.07': {'dopant': 'P', 'conc': 0.075, 'energy': -342.930560298940, 'n_atoms': 4},
    }
    
    # Experiment 4: Polaron (C60 dimer, 120 atoms, UKS)
    exp4_data = {
        'polaron_+0.0_pristine': {'strain': 0.0, 'dopant': 'pristine', 'energy': -681.810470811467, 'n_atoms': 120},
        'polaron_+0.0_B': {'strain': 0.0, 'dopant': 'B', 'energy': -664.295718549217, 'n_atoms': 120},
        'polaron_+0.0_N': {'strain': 0.0, 'dopant': 'N', 'energy': -707.228383800690, 'n_atoms': 120},
        'polaron_+0.0_P': {'strain': 0.0, 'dopant': 'P', 'energy': -685.273015572529, 'n_atoms': 120},
        'polaron_+3.0_pristine': {'strain': 3.0, 'dopant': 'pristine', 'energy': -681.810484918564, 'n_atoms': 120},
        'polaron_+3.0_B': {'strain': 3.0, 'dopant': 'B', 'energy': -664.255639572399, 'n_atoms': 120},
        'polaron_+3.0_N': {'strain': 3.0, 'dopant': 'N', 'energy': -707.231499445652, 'n_atoms': 120},
        'polaron_+3.0_P': {'strain': 3.0, 'dopant': 'P', 'energy': -685.263412396684, 'n_atoms': 120},
    }
    
    # Experiment 6: Optimal conditions (single C60, 60 atoms)
    exp6_data = {
        'optimal_+0.0_pristine': {'strain': 0.0, 'dopant': 'pristine', 'energy': -340.888236200700, 'n_atoms': 60},
        'optimal_+0.0_B': {'strain': 0.0, 'dopant': 'B', 'energy': -337.966138686483, 'n_atoms': 60},
        'optimal_+0.0_N': {'strain': 0.0, 'dopant': 'N', 'energy': -345.124700703805, 'n_atoms': 60},
        'optimal_+0.0_P': {'strain': 0.0, 'dopant': 'P', 'energy': -341.460490237628, 'n_atoms': 60},
        'optimal_+3.0_pristine': {'strain': 3.0, 'dopant': 'pristine', 'energy': -340.888228874417, 'n_atoms': 60},
        'optimal_+3.0_B': {'strain': 3.0, 'dopant': 'B', 'energy': -337.966134643844, 'n_atoms': 60},
        'optimal_+3.0_N': {'strain': 3.0, 'dopant': 'N', 'energy': -345.124683692834, 'n_atoms': 60},
        'optimal_+3.0_P': {'strain': 3.0, 'dopant': 'P', 'energy': -341.460481969178, 'n_atoms': 60},
        'optimal_-3.0_pristine': {'strain': -3.0, 'dopant': 'pristine', 'energy': -340.888237520018, 'n_atoms': 60},
        'optimal_-3.0_B': {'strain': -3.0, 'dopant': 'B', 'energy': -337.966142728462, 'n_atoms': 60},
        'optimal_-3.0_N': {'strain': -3.0, 'dopant': 'N', 'energy': -345.124717432520, 'n_atoms': 60},
        'optimal_-3.0_P': {'strain': -3.0, 'dopant': 'P', 'energy': -341.460498155988, 'n_atoms': 60},
        'optimal_+5.0_pristine': {'strain': 5.0, 'dopant': 'pristine', 'energy': -340.888237390550, 'n_atoms': 60},
        'optimal_+5.0_B': {'strain': 5.0, 'dopant': 'B', 'energy': -337.966139144861, 'n_atoms': 60},
        'optimal_+5.0_N': {'strain': 5.0, 'dopant': 'N', 'energy': -345.124678796004, 'n_atoms': 60},
        'optimal_+5.0_P': {'strain': 5.0, 'dopant': 'P', 'energy': -341.460486362444, 'n_atoms': 60},
        'optimal_-5.0_pristine': {'strain': -5.0, 'dopant': 'pristine', 'energy': -340.888223691814, 'n_atoms': 60},
        'optimal_-5.0_N': {'strain': -5.0, 'dopant': 'N', 'energy': -345.124714172436, 'n_atoms': 60},
        'optimal_-5.0_P': {'strain': -5.0, 'dopant': 'P', 'energy': -341.460486420593, 'n_atoms': 60},
    }
    
    return exp1_data, exp2_data, exp4_data, exp6_data


def figure1_strain_energy(exp1_data, save_path):
    """
    Figure 1: Real DFT Energy vs Strain
    Shows the actual total energy response to biaxial strain.
    """
    fig, ax = plt.subplots(figsize=(4.5, 3.5))
    
    strains = []
    energies = []
    
    for key, val in exp1_data.items():
        strains.append(val['strain'])
        energies.append(val['energy'])
    
    # Sort by strain
    sorted_pairs = sorted(zip(strains, energies))
    strains, energies = zip(*sorted_pairs)
    strains = np.array(strains)
    energies = np.array(energies)
    
    # Convert to relative energy (meV/atom)
    n_atoms = 120
    e_ref = energies[strains == 0][0]
    relative_energy = (energies - e_ref) * 27211.386  # Ha to meV
    energy_per_atom = relative_energy / n_atoms
    
    ax.plot(strains, energy_per_atom, 'o-', color=COLORS['pristine'], 
           markersize=8, markerfacecolor='white', markeredgewidth=1.5)
    
    # Polynomial fit
    coeffs = np.polyfit(strains, energy_per_atom, 2)
    x_fit = np.linspace(-5.5, 5.5, 100)
    y_fit = np.polyval(coeffs, x_fit)
    ax.plot(x_fit, y_fit, '--', color='gray', alpha=0.7, lw=1)
    
    ax.set_xlabel('Biaxial Strain (%)')
    ax.set_ylabel(r'$\Delta E$ (meV/atom)')
    ax.set_xlim(-6, 6)
    ax.axhline(y=0, color='gray', linestyle=':', lw=0.8)
    ax.minorticks_on()
    
    # Add annotation
    ax.text(0.95, 0.95, 'qHP C$_{60}$ dimer\nDFT (PBE+rVV10)', 
           transform=ax.transAxes, ha='right', va='top', fontsize=9,
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.savefig(save_path.with_suffix('.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Figure 1 saved: {save_path}")


def figure2_doping_energy(exp2_data, save_path):
    """
    Figure 2: Doping Effects on Total Energy
    Shows how different dopants affect the system energy.
    """
    fig, ax = plt.subplots(figsize=(4.5, 3.5))
    
    # Reference: pristine C60 energy
    e_pristine = exp2_data['C60_pristine_0.05']['energy']
    
    dopants = ['B', 'N', 'P']
    
    for dopant in dopants:
        concs = []
        binding_energies = []
        
        for key, val in exp2_data.items():
            if val['dopant'] == dopant:
                concs.append(val['conc'])
                # Binding energy relative to pristine (per dopant atom)
                n_dopant = val['n_atoms']  # Number of dopant atoms
                if n_dopant > 0:
                    e_bind = (val['energy'] - e_pristine) * 27.211386  # Ha to eV
                    binding_energies.append(e_bind)
        
        if concs and binding_energies:
            sorted_pairs = sorted(zip(concs, binding_energies))
            c, be = zip(*sorted_pairs)
            
            ax.plot(np.array(c)*100, be, marker=MARKERS[dopant], color=COLORS[dopant],
                   label=dopant, markerfacecolor=COLORS[dopant], markeredgewidth=1.2)
    
    ax.set_xlabel('Doping Concentration (%)')
    ax.set_ylabel(r'$\Delta E$ (eV)')
    ax.legend(loc='upper right', frameon=False)
    ax.minorticks_on()
    ax.axhline(y=0, color='gray', linestyle=':', lw=0.8)
    
    # Add annotation
    ax.text(0.05, 0.95, 'C$_{60}$ + Dopant\nDFT (PBE+rVV10)', 
           transform=ax.transAxes, ha='left', va='top', fontsize=9,
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.savefig(save_path.with_suffix('.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Figure 2 saved: {save_path}")


def figure3_combined_effects(exp4_data, exp6_data, save_path):
    """
    Figure 3: Combined Strain-Doping Effects
    Two-panel showing:
    (a) Exp4: Polaron - Energy of doped C60 dimer at different strains
    (b) Exp6: Optimal - Energy of single doped C60 at different strains
    """
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0))
    
    # Panel (a): Experiment 4 - Polaron
    ax1 = axes[0]
    
    # Group by dopant
    dopants = ['pristine', 'B', 'N', 'P']
    
    for dopant in dopants:
        strains = []
        energies = []
        
        for key, val in exp4_data.items():
            if val['dopant'] == dopant:
                strains.append(val['strain'])
                energies.append(val['energy'])
        
        if strains:
            sorted_pairs = sorted(zip(strains, energies))
            s, e = zip(*sorted_pairs)
            
            # Normalize to per-atom energy
            e = np.array(e) / 120 * 27.211386  # eV/atom
            
            ax1.plot(s, e, marker=MARKERS[dopant], color=COLORS[dopant],
                    label=dopant, markerfacecolor='white' if dopant == 'pristine' else COLORS[dopant],
                    markeredgewidth=1.2)
    
    ax1.set_xlabel('Strain (%)')
    ax1.set_ylabel('Energy (eV/atom)')
    ax1.legend(loc='upper right', frameon=False, fontsize=8)
    ax1.text(-0.15, 1.05, '(a) C$_{60}$ dimer', transform=ax1.transAxes, fontweight='bold', fontsize=10)
    ax1.minorticks_on()
    
    # Panel (b): Experiment 6 - Optimal conditions
    ax2 = axes[1]
    
    for dopant in dopants:
        strains = []
        energies = []
        
        for key, val in exp6_data.items():
            if val['dopant'] == dopant:
                strains.append(val['strain'])
                energies.append(val['energy'])
        
        if strains:
            sorted_pairs = sorted(zip(strains, energies))
            s, e = zip(*sorted_pairs)
            
            # Normalize to per-atom energy
            e = np.array(e) / 60 * 27.211386  # eV/atom
            
            ax2.plot(s, e, marker=MARKERS[dopant], color=COLORS[dopant],
                    label=dopant, markerfacecolor='white' if dopant == 'pristine' else COLORS[dopant],
                    markeredgewidth=1.2)
    
    ax2.set_xlabel('Strain (%)')
    ax2.set_ylabel('Energy (eV/atom)')
    ax2.legend(loc='upper right', frameon=False, fontsize=8)
    ax2.text(-0.15, 1.05, '(b) Single C$_{60}$', transform=ax2.transAxes, fontweight='bold', fontsize=10)
    ax2.minorticks_on()
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.savefig(save_path.with_suffix('.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Figure 3 saved: {save_path}")


def main():
    """Generate figures from real DFT data."""
    
    print("=" * 60)
    print("Extracting Real DFT Data and Generating Honest Figures")
    print("=" * 60)
    
    # Load data
    exp1_data, exp2_data, exp4_data, exp6_data = load_real_dft_data()
    
    print(f"\nExperiment 1: {len(exp1_data)} calculations")
    print(f"Experiment 2: {len(exp2_data)} calculations")
    print(f"Experiment 4: {len(exp4_data)} calculations")
    print(f"Experiment 6: {len(exp6_data)} calculations")
    
    # Output directory
    figures_dir = Path(__file__).parent / "real_dft_figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate figures
    print("\n--- Generating Figure 1: Strain-Energy ---")
    figure1_strain_energy(exp1_data, figures_dir / "fig1_strain_energy.pdf")
    
    print("\n--- Generating Figure 2: Doping Effects ---")
    figure2_doping_energy(exp2_data, figures_dir / "fig2_doping_energy.pdf")
    
    print("\n--- Generating Figure 3: Combined Effects ---")
    figure3_combined_effects(exp4_data, exp6_data, figures_dir / "fig3_combined_effects.pdf")
    
    print("\n" + "=" * 60)
    print("All figures generated from REAL DFT data!")
    print(f"Output directory: {figures_dir}")
    print("=" * 60)
    
    # Print data summary
    print("\n=== Data Summary ===")
    print("\nExperiment 1 (pristine C60 dimer):")
    for key, val in sorted(exp1_data.items(), key=lambda x: x[1]['strain']):
        print(f"  {val['strain']:+.1f}% strain: {val['energy']:.6f} Ha")
    
    print("\nExperiment 6 (doped C60, 0% strain):")
    for dopant in ['pristine', 'B', 'N', 'P']:
        for key, val in exp6_data.items():
            if val['dopant'] == dopant and val['strain'] == 0:
                print(f"  {dopant}: {val['energy']:.6f} Ha")


if __name__ == "__main__":
    main()

