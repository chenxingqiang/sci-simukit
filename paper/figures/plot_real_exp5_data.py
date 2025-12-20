#!/usr/bin/env python3
"""
Plot Real DFT Data from Experiment 5 (Synergy)

This script uses actual CP2K calculation results to create 
publication-quality figures for the graphullerene paper.

Author: Xingqiang Chen
Date: 2024
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

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
    'lines.linewidth': 1.5,
    'lines.markersize': 7,
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

# Real DFT data from Experiment 5 (C60 tetramer, ~240 atoms)
EXP5_DATA = {
    'pristine': {
        -5.0: -1363.550972656326,
        -2.5: -1363.551049243674,
        0.0: -1363.551156170134,
        2.5: -1363.551119516428,
        3.0: -1363.552164663920,
        5.0: -1363.550870979375,
    },
    'B': {
        -5.0: -1328.450219249360,
        -2.5: -1328.473705542199,
        0.0: -1328.489979706896,
        2.5: -1328.506491756213,
        3.0: -1328.457059357138,
        5.0: -1328.408958995534,
    },
    'N': {
        -5.0: -1414.278832222583,
        -2.5: -1414.322113403947,
        0.0: -1414.381232387249,
        2.5: -1414.408053530233,
        3.0: -1414.332245698258,
        5.0: -1414.405260357801,
    },
    'P': {
        -5.0: -1370.485720075769,
        -2.5: -1370.477261059190,
        0.0: -1370.496465821598,
        2.5: -1369.909277509703,  # Note: outlier
        3.0: -1370.489003155048,
        5.0: -1370.488848617021,
    },
}

# Real DFT data from Experiment 1 (C60 dimer, 120 atoms)
EXP1_DATA = {
    'pristine': {
        -5.0: -681.810585529232,
        -2.5: -681.810524698309,
        0.0: -681.810470811466,
        2.5: -681.810495411986,
        5.0: -681.810434885755,
    }
}


def figure1_strain_response(save_path: Path):
    """
    Figure 1: Strain-Energy Response
    
    Shows how total energy changes with biaxial strain for different systems.
    """
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0))
    
    # Panel (a): Exp1 - pristine C60 dimer
    ax1 = axes[0]
    
    strains = sorted(EXP1_DATA['pristine'].keys())
    energies = [EXP1_DATA['pristine'][s] for s in strains]
    
    # Relative energy (meV/atom)
    e_ref = EXP1_DATA['pristine'][0.0]
    n_atoms = 120
    relative_e = [(e - e_ref) * 27211.386 / n_atoms for e in energies]
    
    ax1.plot(strains, relative_e, 'o-', color=COLORS['pristine'], 
            markerfacecolor='white', markeredgewidth=1.5, markersize=8)
    
    ax1.set_xlabel('Biaxial Strain (%)')
    ax1.set_ylabel(r'$\Delta E$ (meV/atom)')
    ax1.axhline(y=0, color='gray', linestyle=':', lw=0.8)
    ax1.set_xlim(-6, 6)
    ax1.text(-0.15, 1.05, '(a)', transform=ax1.transAxes, fontweight='bold', fontsize=11)
    ax1.text(0.95, 0.95, 'C$_{60}$ dimer\n(120 atoms)', transform=ax1.transAxes, 
            ha='right', va='top', fontsize=9, 
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax1.minorticks_on()
    
    # Panel (b): Exp5 - all dopant types
    ax2 = axes[1]
    
    for dopant in ['pristine', 'B', 'N', 'P']:
        data = EXP5_DATA[dopant]
        strains = sorted(data.keys())
        energies = [data[s] for s in strains]
        
        # Relative energy per atom (meV/atom)
        n_atoms = 240
        e_ref = EXP5_DATA['pristine'][0.0]
        relative_e = [(e - e_ref) * 27211.386 / n_atoms for e in energies]
        
        ax2.plot(strains, relative_e, marker=MARKERS[dopant], color=COLORS[dopant],
                label=dopant, markerfacecolor='white' if dopant == 'pristine' else COLORS[dopant],
                markeredgewidth=1.2)
    
    ax2.set_xlabel('Biaxial Strain (%)')
    ax2.set_ylabel(r'$\Delta E$ (meV/atom)')
    ax2.legend(loc='upper right', frameon=False, ncol=2)
    ax2.axhline(y=0, color='gray', linestyle=':', lw=0.8)
    ax2.set_xlim(-6, 6)
    ax2.text(-0.15, 1.05, '(b)', transform=ax2.transAxes, fontweight='bold', fontsize=11)
    ax2.text(0.95, 0.05, 'C$_{60}$ tetramer\n(240 atoms)', transform=ax2.transAxes, 
            ha='right', va='bottom', fontsize=9,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax2.minorticks_on()
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.savefig(save_path.with_suffix('.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Figure 1 saved: {save_path}")


def figure2_doping_effects(save_path: Path):
    """
    Figure 2: Doping Effects at Different Strains
    
    Shows the energy difference between doped and pristine systems.
    """
    fig, ax = plt.subplots(figsize=(5.0, 4.0))
    
    for dopant in ['B', 'N', 'P']:
        strains = []
        binding_energies = []
        
        for strain in sorted(EXP5_DATA[dopant].keys()):
            e_doped = EXP5_DATA[dopant][strain]
            e_pristine = EXP5_DATA['pristine'][strain]
            
            # Binding energy in eV (per dopant atom, assuming 6 dopants)
            n_dopants = 6
            e_bind = (e_doped - e_pristine) * 27.211386 / n_dopants
            
            strains.append(strain)
            binding_energies.append(e_bind)
        
        ax.plot(strains, binding_energies, marker=MARKERS[dopant], color=COLORS[dopant],
               label=dopant, markerfacecolor=COLORS[dopant], markeredgewidth=1.2)
    
    ax.set_xlabel('Biaxial Strain (%)')
    ax.set_ylabel(r'Formation Energy (eV/dopant)')
    ax.legend(loc='best', frameon=False)
    ax.axhline(y=0, color='gray', linestyle=':', lw=0.8)
    ax.set_xlim(-6, 6)
    ax.minorticks_on()
    
    # Add annotation
    ax.text(0.95, 0.95, 'C$_{60}$ tetramer\nDFT (PBE+rVV10)', 
           transform=ax.transAxes, ha='right', va='top', fontsize=9,
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.savefig(save_path.with_suffix('.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Figure 2 saved: {save_path}")


def figure3_synergy_analysis(save_path: Path):
    """
    Figure 3: Synergistic Strain-Doping Coupling Analysis
    
    Three-panel figure showing:
    (a) Absolute energies vs strain
    (b) Strain response for each dopant (normalized)
    (c) Optimal conditions identification
    """
    fig, axes = plt.subplots(1, 3, figsize=(8.5, 3.0))
    
    # Panel (a): Absolute energies
    ax1 = axes[0]
    
    for dopant in ['pristine', 'B', 'N', 'P']:
        data = EXP5_DATA[dopant]
        strains = sorted(data.keys())
        energies = [data[s] for s in strains]
        
        ax1.plot(strains, energies, marker=MARKERS[dopant], color=COLORS[dopant],
                label=dopant, markerfacecolor='white' if dopant == 'pristine' else COLORS[dopant],
                markeredgewidth=1.2)
    
    ax1.set_xlabel('Strain (%)')
    ax1.set_ylabel('Total Energy (Ha)')
    ax1.legend(loc='upper right', frameon=False, fontsize=8)
    ax1.text(-0.15, 1.05, '(a)', transform=ax1.transAxes, fontweight='bold', fontsize=11)
    ax1.minorticks_on()
    
    # Panel (b): Strain response (normalized to 0% strain)
    ax2 = axes[1]
    
    for dopant in ['pristine', 'B', 'N', 'P']:
        data = EXP5_DATA[dopant]
        e_ref = data[0.0]
        
        strains = sorted(data.keys())
        # Energy change in meV
        delta_e = [(data[s] - e_ref) * 27211.386 for s in strains]
        
        ax2.plot(strains, delta_e, marker=MARKERS[dopant], color=COLORS[dopant],
                label=dopant, markerfacecolor='white' if dopant == 'pristine' else COLORS[dopant],
                markeredgewidth=1.2)
    
    ax2.set_xlabel('Strain (%)')
    ax2.set_ylabel(r'$\Delta E$ (meV)')
    ax2.axhline(y=0, color='gray', linestyle=':', lw=0.8)
    ax2.text(-0.15, 1.05, '(b)', transform=ax2.transAxes, fontweight='bold', fontsize=11)
    ax2.minorticks_on()
    
    # Panel (c): Synergy factor
    ax3 = axes[2]
    
    # Calculate synergy: how much does doping enhance strain response?
    for dopant in ['B', 'N', 'P']:
        data_doped = EXP5_DATA[dopant]
        data_pristine = EXP5_DATA['pristine']
        
        strains = sorted(data_doped.keys())
        synergy = []
        
        for s in strains:
            # Synergy = (E_doped(s) - E_doped(0)) / (E_pristine(s) - E_pristine(0))
            de_doped = data_doped[s] - data_doped[0.0]
            de_pristine = data_pristine[s] - data_pristine[0.0]
            
            if abs(de_pristine) > 1e-6:
                syn = de_doped / de_pristine
            else:
                syn = 1.0
            synergy.append(syn)
        
        ax3.plot(strains, synergy, marker=MARKERS[dopant], color=COLORS[dopant],
                label=dopant, markerfacecolor=COLORS[dopant], markeredgewidth=1.2)
    
    ax3.set_xlabel('Strain (%)')
    ax3.set_ylabel('Synergy Factor')
    ax3.axhline(y=1.0, color='gray', linestyle='--', lw=0.8)
    ax3.legend(loc='best', frameon=False, fontsize=8)
    ax3.text(-0.15, 1.05, '(c)', transform=ax3.transAxes, fontweight='bold', fontsize=11)
    ax3.minorticks_on()
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.savefig(save_path.with_suffix('.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Figure 3 saved: {save_path}")


def main():
    """Generate all figures from real DFT data."""
    
    print("=" * 60)
    print("Generating Figures from REAL Experiment 5 DFT Data")
    print("=" * 60)
    
    # Create output directory
    figures_dir = Path(__file__).parent / "real_exp5_figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nData Summary:")
    print(f"  Experiment 1: {len(EXP1_DATA['pristine'])} calculations (C60 dimer)")
    print(f"  Experiment 5: {sum(len(v) for v in EXP5_DATA.values())} calculations (C60 tetramer)")
    
    # Generate figures
    print("\n--- Generating Figure 1: Strain Response ---")
    figure1_strain_response(figures_dir / "fig1_strain_response.pdf")
    
    print("\n--- Generating Figure 2: Doping Effects ---")
    figure2_doping_effects(figures_dir / "fig2_doping_effects.pdf")
    
    print("\n--- Generating Figure 3: Synergy Analysis ---")
    figure3_synergy_analysis(figures_dir / "fig3_synergy_analysis.pdf")
    
    print("\n" + "=" * 60)
    print("All figures generated from REAL DFT data!")
    print(f"Output directory: {figures_dir}")
    print("=" * 60)
    
    # Print key findings
    print("\n=== Key Findings from Real DFT Data ===")
    
    print("\n1. Strain Response (Exp1 - C60 dimer):")
    e_ref = EXP1_DATA['pristine'][0.0]
    for s in sorted(EXP1_DATA['pristine'].keys()):
        de = (EXP1_DATA['pristine'][s] - e_ref) * 27211.386 / 120
        print(f"   {s:+.1f}% strain: {de:+.4f} meV/atom")
    
    print("\n2. Doping Effects (Exp5 - at 0% strain):")
    e_pristine = EXP5_DATA['pristine'][0.0]
    for dopant in ['B', 'N', 'P']:
        e_doped = EXP5_DATA[dopant][0.0]
        de = (e_doped - e_pristine) * 27.211386
        print(f"   {dopant}-doped: {de:+.3f} eV (total)")
    
    print("\n3. Most Stable Configuration:")
    min_e = float('inf')
    best_config = None
    for dopant, data in EXP5_DATA.items():
        for strain, energy in data.items():
            if energy < min_e:
                min_e = energy
                best_config = (dopant, strain)
    print(f"   {best_config[0]} at {best_config[1]:+.1f}% strain: {min_e:.6f} Ha")


if __name__ == "__main__":
    main()

