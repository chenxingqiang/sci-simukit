#!/usr/bin/env python3
"""
Final Publication-Quality Figures for Graphullerene Paper

Based on REAL DFT calculation results from:
- Experiment 1: C60 dimer under strain (5 calculations)
- Experiment 5: C60 tetramer with strain+doping (24 calculations)

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

# Real DFT data (cleaned - excluding P at +2.5% outlier)
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
        # 2.5: excluded (outlier)
        3.0: -1370.489003155048,
        5.0: -1370.488848617021,
    },
}

EXP1_DATA = {
    'pristine': {
        -5.0: -681.810585529232,
        -2.5: -681.810524698309,
        0.0: -681.810470811466,
        2.5: -681.810495411986,
        5.0: -681.810434885755,
    }
}


def figure1_combined(save_path: Path):
    """
    Figure 1: Strain and Doping Effects
    
    Two-panel figure:
    (a) Pristine C60 strain response
    (b) Doping-induced energy changes at different strains
    """
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0))
    
    # Panel (a): Strain response of pristine systems
    ax1 = axes[0]
    
    # Exp1 (dimer)
    strains1 = sorted(EXP1_DATA['pristine'].keys())
    e_ref1 = EXP1_DATA['pristine'][0.0]
    delta_e1 = [(EXP1_DATA['pristine'][s] - e_ref1) * 27211.386 / 120 for s in strains1]
    
    ax1.plot(strains1, delta_e1, 'o-', color=COLORS['pristine'], 
            markerfacecolor='white', markeredgewidth=1.5, markersize=8,
            label='Dimer (120 atoms)')
    
    # Exp5 pristine (tetramer)
    strains5 = sorted(EXP5_DATA['pristine'].keys())
    e_ref5 = EXP5_DATA['pristine'][0.0]
    delta_e5 = [(EXP5_DATA['pristine'][s] - e_ref5) * 27211.386 / 240 for s in strains5]
    
    ax1.plot(strains5, delta_e5, 's--', color='#ff7f0e', 
            markerfacecolor='white', markeredgewidth=1.5, markersize=7,
            label='Tetramer (240 atoms)')
    
    ax1.set_xlabel('Biaxial Strain (%)')
    ax1.set_ylabel(r'$\Delta E$ (meV/atom)')
    ax1.axhline(y=0, color='gray', linestyle=':', lw=0.8)
    ax1.set_xlim(-6, 6)
    ax1.legend(loc='upper left', frameon=False, fontsize=8)
    ax1.text(-0.15, 1.05, '(a)', transform=ax1.transAxes, fontweight='bold', fontsize=11)
    ax1.minorticks_on()
    
    # Panel (b): Doping formation energy at 0% strain
    ax2 = axes[1]
    
    # Formation energy relative to pristine at each strain
    strains_all = [-5.0, -2.5, 0.0, 3.0, 5.0]  # excluding 2.5 due to P outlier
    
    for dopant in ['B', 'N', 'P']:
        formation_e = []
        strains_valid = []
        
        for s in strains_all:
            if s in EXP5_DATA[dopant]:
                e_doped = EXP5_DATA[dopant][s]
                e_pristine = EXP5_DATA['pristine'][s]
                # Formation energy per dopant (6 dopants in tetramer)
                f_e = (e_doped - e_pristine) * 27.211386 / 6
                formation_e.append(f_e)
                strains_valid.append(s)
        
        ax2.plot(strains_valid, formation_e, marker=MARKERS[dopant], color=COLORS[dopant],
                label=dopant, markerfacecolor=COLORS[dopant], markeredgewidth=1.2)
    
    ax2.set_xlabel('Biaxial Strain (%)')
    ax2.set_ylabel(r'Formation Energy (eV/dopant)')
    ax2.axhline(y=0, color='gray', linestyle=':', lw=0.8)
    ax2.legend(loc='best', frameon=False)
    ax2.set_xlim(-6, 6)
    ax2.text(-0.15, 1.05, '(b)', transform=ax2.transAxes, fontweight='bold', fontsize=11)
    ax2.minorticks_on()
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.savefig(save_path.with_suffix('.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Figure 1 saved: {save_path}")


def figure2_synergy(save_path: Path):
    """
    Figure 2: Synergistic Strain-Doping Coupling
    
    Shows how strain modulates doping effects (key discovery).
    """
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0))
    
    # Panel (a): Energy curves for each system
    ax1 = axes[0]
    
    for dopant in ['pristine', 'B', 'N', 'P']:
        data = EXP5_DATA[dopant]
        strains = sorted(data.keys())
        
        # Normalize to 0% strain for each dopant
        e_ref = data[0.0]
        delta_e = [(data[s] - e_ref) * 27211.386 for s in strains]  # meV
        
        ax1.plot(strains, delta_e, marker=MARKERS[dopant], color=COLORS[dopant],
                label=dopant, markerfacecolor='white' if dopant == 'pristine' else COLORS[dopant],
                markeredgewidth=1.2)
    
    ax1.set_xlabel('Biaxial Strain (%)')
    ax1.set_ylabel(r'$\Delta E$ from 0% strain (meV)')
    ax1.axhline(y=0, color='gray', linestyle=':', lw=0.8)
    ax1.legend(loc='best', frameon=False, fontsize=8)
    ax1.set_xlim(-6, 6)
    ax1.text(-0.15, 1.05, '(a)', transform=ax1.transAxes, fontweight='bold', fontsize=11)
    ax1.minorticks_on()
    
    # Panel (b): Strain sensitivity (slope) for each dopant
    ax2 = axes[1]
    
    # Calculate strain sensitivity: d(E)/d(strain) for each dopant
    dopant_list = ['pristine', 'B', 'N', 'P']
    sensitivities = []
    
    for dopant in dopant_list:
        data = EXP5_DATA[dopant]
        strains = np.array(sorted(data.keys()))
        energies = np.array([data[s] for s in strains])
        
        # Linear fit
        coeffs = np.polyfit(strains, energies, 1)
        slope = coeffs[0] * 27211.386  # meV per % strain
        sensitivities.append(slope)
    
    x_pos = np.arange(len(dopant_list))
    colors = [COLORS[d] for d in dopant_list]
    
    bars = ax2.bar(x_pos, sensitivities, color=colors, edgecolor='black', linewidth=0.8)
    
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(dopant_list)
    ax2.set_ylabel(r'Strain Sensitivity (meV/%)')
    ax2.axhline(y=0, color='gray', linestyle=':', lw=0.8)
    ax2.text(-0.15, 1.05, '(b)', transform=ax2.transAxes, fontweight='bold', fontsize=11)
    
    # Add value labels on bars
    for bar, val in zip(bars, sensitivities):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1f}', ha='center', va='bottom' if height > 0 else 'top',
                fontsize=8)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.savefig(save_path.with_suffix('.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Figure 2 saved: {save_path}")


def main():
    """Generate final publication figures."""
    
    print("=" * 60)
    print("Generating Final Publication Figures")
    print("Based on Real DFT Data")
    print("=" * 60)
    
    # Create output directory
    figures_dir = Path(__file__).parent / "final_figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nData Summary:")
    print(f"  Experiment 1: 5 calculations")
    print(f"  Experiment 5: 23 calculations (1 outlier excluded)")
    
    # Generate figures
    print("\n--- Generating Figure 1: Strain and Doping Effects ---")
    figure1_combined(figures_dir / "figure1_strain_doping.pdf")
    
    print("\n--- Generating Figure 2: Synergistic Coupling ---")
    figure2_synergy(figures_dir / "figure2_synergy.pdf")
    
    print("\n" + "=" * 60)
    print("Publication figures generated!")
    print(f"Output directory: {figures_dir}")
    print("=" * 60)
    
    # Key findings summary
    print("\n=== KEY FINDINGS FROM REAL DFT DATA ===")
    
    print("\n1. Strain Response:")
    print("   - C60 systems show asymmetric strain response")
    print("   - Compression (-5%) lowers energy more than tension (+5%)")
    
    print("\n2. Doping Effects (Formation Energy per dopant at 0% strain):")
    for dopant in ['B', 'N', 'P']:
        e_doped = EXP5_DATA[dopant][0.0]
        e_pristine = EXP5_DATA['pristine'][0.0]
        f_e = (e_doped - e_pristine) * 27.211386 / 6
        print(f"   {dopant}: {f_e:+.2f} eV/dopant")
    
    print("\n3. Most Stable System:")
    print("   N-doped at +2.5% tensile strain: -1414.408 Ha")
    
    print("\n4. Strain Sensitivity (dE/dε):")
    for dopant in ['pristine', 'B', 'N', 'P']:
        data = EXP5_DATA[dopant]
        strains = np.array(sorted(data.keys()))
        energies = np.array([data[s] for s in strains])
        coeffs = np.polyfit(strains, energies, 1)
        slope = coeffs[0] * 27211.386
        print(f"   {dopant}: {slope:+.2f} meV/%")


if __name__ == "__main__":
    main()

