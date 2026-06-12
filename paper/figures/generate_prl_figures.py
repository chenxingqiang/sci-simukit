#!/usr/bin/env python3
"""
Generate PRL-Style Publication Figures for Graphullerene Paper

Creates professional figures following Physical Review Letters style:
- Clean, minimalist design
- High contrast with limited colors
- Clear axis labels and legends
- Publication-ready resolution (300+ dpi)

Author: Xingqiang Chen
Date: 2024
"""

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prl_style import (  # noqa: E402
    COLORS,
    MARKERS,
    PRL_DOUBLE_COL,
    apply_prl_style,
    finalize_axes,
    save_figure,
)

apply_prl_style()


def load_experiment_data(exp_dir: Path) -> dict:
    """Load experiment results from JSON file."""
    results_file = exp_dir / "results" / "dft_results.json"
    if results_file.exists():
        with open(results_file) as f:
            return json.load(f)
    return {}


def figure1_synergistic_coupling(data_exp6: dict, save_path: Path):
    """
    Figure 1: Non-Additive Coupling Between Strain and Doping
    
    Two-panel figure showing:
    (a) Mobility vs strain for different dopants
    (b) Synergistic enhancement factor
    """
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0))
    
    # Organize data
    dopants = ['pristine', 'B', 'N', 'B+N']
    strains = sorted(set(v['strain'] for v in data_exp6.values()))
    
    # Panel (a): Mobility vs Strain
    ax1 = axes[0]
    
    for dopant in dopants:
        strain_vals = []
        mobility_vals = []
        
        for key, val in data_exp6.items():
            if val.get('dopant') == dopant and val.get('status') == 'success':
                strain_vals.append(val['strain'])
                mobility_vals.append(val['mobility'])
        
        if strain_vals:
            # Sort by strain
            sorted_pairs = sorted(zip(strain_vals, mobility_vals))
            s, m = zip(*sorted_pairs)
            
            ax1.plot(s, m, marker=MARKERS[dopant], color=COLORS[dopant], 
                    label=dopant if dopant != 'B+N' else 'B/N', 
                    markerfacecolor='white' if dopant == 'pristine' else COLORS[dopant],
                    markeredgewidth=1.2)
    
    ax1.set_xlabel('Biaxial Strain (%)')
    ax1.set_ylabel(r'Electron Mobility (cm$^2$V$^{-1}$s$^{-1}$)')
    ax1.legend(loc='upper left', frameon=False, ncol=2)
    ax1.set_xlim(-6, 6)
    ax1.text(-0.15, 1.05, '(a)', transform=ax1.transAxes, fontweight='bold', fontsize=11)
    
    # Add minor ticks
    ax1.minorticks_on()
    ax1.tick_params(which='minor', length=2)
    
    # Panel (b): Synergistic Enhancement
    ax2 = axes[1]
    
    # Calculate enhancement factor: (doped+strained) / (pristine at same strain)
    enhancement_data = {}
    
    for dopant in ['B', 'N', 'B+N']:
        enhancement_data[dopant] = {'strain': [], 'factor': []}
        
        for key, val in data_exp6.items():
            if val.get('dopant') == dopant and val.get('status') == 'success':
                strain = val['strain']
                mobility_doped = val['mobility']
                
                # Find pristine at same strain
                pristine_key = f"strain_{strain}_pristine"
                if pristine_key in data_exp6:
                    mobility_pristine = data_exp6[pristine_key]['mobility']
                    if mobility_pristine > 0:
                        factor = mobility_doped / mobility_pristine
                        enhancement_data[dopant]['strain'].append(strain)
                        enhancement_data[dopant]['factor'].append(factor)
    
    for dopant in ['B', 'N', 'B+N']:
        if enhancement_data[dopant]['strain']:
            sorted_pairs = sorted(zip(enhancement_data[dopant]['strain'], 
                                     enhancement_data[dopant]['factor']))
            s, f = zip(*sorted_pairs)
            
            label = dopant if dopant != 'B+N' else 'B/N'
            ax2.plot(s, f, marker=MARKERS[dopant], color=COLORS[dopant], 
                    label=label, markerfacecolor=COLORS[dopant], markeredgewidth=1.2)
    
    # Reference line at 1.0
    ax2.axhline(y=1.0, color='gray', linestyle='--', linewidth=0.8, alpha=0.7)
    
    ax2.set_xlabel('Biaxial Strain (%)')
    ax2.set_ylabel('Enhancement Factor')
    ax2.legend(loc='upper left', frameon=False)
    ax2.set_xlim(-6, 6)
    ax2.set_ylim(0.9, 1.6)
    ax2.text(-0.15, 1.05, '(b)', transform=ax2.transAxes, fontweight='bold', fontsize=11)
    ax2.minorticks_on()
    ax2.tick_params(which='minor', length=2)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', format='pdf')
    plt.savefig(save_path.with_suffix('.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Figure 1 saved: {save_path}")


def figure2_polaron_mechanism(data_exp4: dict, data_exp6: dict, save_path: Path):
    """
    Figure 2: Polaron Transition Mechanism
    
    Three-panel figure showing:
    (a) IPR vs strain (charge delocalization)
    (b) Electronic coupling J vs strain
    (c) Activation energy vs strain
    """
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.5))
    
    # Organize exp4 data (IPR and J)
    dopants_exp4 = ['pristine', 'Li', 'Na', 'K']
    
    # Panel (a): IPR vs Strain
    ax1 = axes[0]
    
    for dopant in dopants_exp4:
        strain_vals = []
        ipr_vals = []
        
        for key, val in data_exp4.items():
            if val.get('dopant') == dopant and val.get('status') == 'success':
                strain_vals.append(val['strain'])
                ipr_vals.append(val['ipr'])
        
        if strain_vals:
            sorted_pairs = sorted(zip(strain_vals, ipr_vals))
            s, ipr = zip(*sorted_pairs)
            
            ax1.plot(s, ipr, marker=MARKERS.get(dopant, 'o'), color=COLORS.get(dopant, 'gray'),
                    label=dopant, markerfacecolor='white' if dopant == 'pristine' else COLORS.get(dopant, 'gray'),
                    markeredgewidth=1.2)
    
    ax1.set_xlabel('Strain (%)')
    ax1.set_ylabel('IPR')
    ax1.legend(loc='upper right', frameon=False, fontsize=8)
    ax1.set_xlim(-6, 6)
    ax1.text(-0.18, 1.05, '(a)', transform=ax1.transAxes, fontweight='bold', fontsize=11)
    ax1.minorticks_on()
    
    # Add arrow showing delocalization direction
    ax1.annotate('', xy=(-4, 35), xytext=(-4, 48),
                arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))
    ax1.text(-3.5, 41, 'Delocalized', fontsize=8, rotation=90, va='center')
    
    # Panel (b): Electronic Coupling J vs Strain
    ax2 = axes[1]
    
    for dopant in dopants_exp4:
        strain_vals = []
        j_vals = []
        
        for key, val in data_exp4.items():
            if val.get('dopant') == dopant and val.get('status') == 'success':
                strain_vals.append(val['strain'])
                j_vals.append(val['electronic_coupling'])
        
        if strain_vals:
            sorted_pairs = sorted(zip(strain_vals, j_vals))
            s, j = zip(*sorted_pairs)
            
            ax2.plot(s, j, marker=MARKERS.get(dopant, 'o'), color=COLORS.get(dopant, 'gray'),
                    label=dopant, markerfacecolor='white' if dopant == 'pristine' else COLORS.get(dopant, 'gray'),
                    markeredgewidth=1.2)
    
    ax2.set_xlabel('Strain (%)')
    ax2.set_ylabel('J (meV)')
    ax2.set_xlim(-6, 6)
    ax2.text(-0.18, 1.05, '(b)', transform=ax2.transAxes, fontweight='bold', fontsize=11)
    ax2.minorticks_on()
    
    # Panel (c): Activation Energy vs Strain (from exp6)
    ax3 = axes[2]
    
    dopants_exp6 = ['pristine', 'B', 'N', 'B+N']
    
    for dopant in dopants_exp6:
        strain_vals = []
        ea_vals = []
        
        for key, val in data_exp6.items():
            if val.get('dopant') == dopant and val.get('status') == 'success':
                strain_vals.append(val['strain'])
                ea_vals.append(val['activation_energy'])
        
        if strain_vals:
            sorted_pairs = sorted(zip(strain_vals, ea_vals))
            s, ea = zip(*sorted_pairs)
            
            label = dopant if dopant != 'B+N' else 'B/N'
            ax3.plot(s, ea, marker=MARKERS[dopant], color=COLORS[dopant],
                    label=label, markerfacecolor='white' if dopant == 'pristine' else COLORS[dopant],
                    markeredgewidth=1.2)
    
    ax3.set_xlabel('Strain (%)')
    ax3.set_ylabel(r'$E_a$ (eV)')
    ax3.legend(loc='upper right', frameon=False, fontsize=8, ncol=2)
    ax3.set_xlim(-6, 6)
    ax3.text(-0.18, 1.05, '(c)', transform=ax3.transAxes, fontweight='bold', fontsize=11)
    ax3.minorticks_on()
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', format='pdf')
    plt.savefig(save_path.with_suffix('.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Figure 2 saved: {save_path}")


def figure3_comprehensive_summary(data_exp6: dict, ml_results: dict, save_path: Path):
    """
    Figure 3: Comprehensive Summary - ML Validation for All Three Properties
    
    Three-panel figure showing predicted vs actual for:
    (a) Band gap
    (b) Mobility  
    (c) Activation energy
    """
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.5))
    
    # Collect all data
    all_data = []
    for key, val in data_exp6.items():
        if val.get('status') == 'success':
            all_data.append({
                'strain': val['strain'],
                'dopant': val['dopant'],
                'bandgap': val['bandgap'],
                'mobility': val['mobility'],
                'activation_energy': val['activation_energy']
            })
    
    # Prepare features for prediction
    strains = np.array([d['strain'] for d in all_data])
    dopant_is_B = np.array([1 if 'B' in d['dopant'] else 0 for d in all_data])
    dopant_is_N = np.array([1 if 'N' in d['dopant'] else 0 for d in all_data])
    
    # Create feature matrix
    X = np.column_stack([strains, strains**2, dopant_is_B, dopant_is_N])
    
    properties = ['bandgap', 'mobility', 'activation_energy']
    labels = ['Band Gap (eV)', r'Mobility (cm$^2$V$^{-1}$s$^{-1}$)', r'$E_a$ (eV)']
    colors = ['#2E86AB', '#A23B72', '#F18F01']
    
    for idx, (prop, label, color) in enumerate(zip(properties, labels, colors)):
        ax = axes[idx]
        
        y_actual = np.array([d[prop] for d in all_data])
        
        # Fit multivariate linear model
        from numpy.linalg import lstsq
        coeffs, _, _, _ = lstsq(np.column_stack([np.ones(len(X)), X]), y_actual, rcond=None)
        y_pred = coeffs[0] + X @ coeffs[1:]
        
        # Calculate R²
        ss_res = np.sum((y_actual - y_pred)**2)
        ss_tot = np.sum((y_actual - np.mean(y_actual))**2)
        r2 = 1 - ss_res/ss_tot
        
        # Calculate MAE
        mae = np.mean(np.abs(y_actual - y_pred))
        
        # Plot
        ax.scatter(y_actual, y_pred, c=color, s=40, alpha=0.7, edgecolors='white', linewidths=0.5)
        
        # Perfect prediction line
        min_val = min(y_actual.min(), y_pred.min())
        max_val = max(y_actual.max(), y_pred.max())
        margin = (max_val - min_val) * 0.1
        ax.plot([min_val-margin, max_val+margin], [min_val-margin, max_val+margin], 
               'k--', lw=1, alpha=0.7)
        
        ax.set_xlabel(f'Actual {label}')
        ax.set_ylabel(f'Predicted')
        ax.text(0.05, 0.95, f'$R^2$ = {r2:.3f}', transform=ax.transAxes, 
               fontsize=9, va='top', fontweight='bold')
        ax.set_xlim(min_val-margin, max_val+margin)
        ax.set_ylim(min_val-margin, max_val+margin)
        ax.set_aspect('equal')
        
        panel_labels = ['(a)', '(b)', '(c)']
        ax.text(-0.2, 1.05, panel_labels[idx], transform=ax.transAxes, fontweight='bold', fontsize=11)
        ax.minorticks_on()
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', format='pdf')
    plt.savefig(save_path.with_suffix('.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Figure 3 saved: {save_path}")


def main():
    """Generate all PRL-style figures."""
    
    # Setup paths
    project_root = Path(__file__).parent.parent.parent
    exp_dir = project_root / "experiments"
    figures_dir = Path(__file__).parent / "publication_quality"
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Generating PRL-Style Publication Figures")
    print("=" * 60)
    
    # Load experiment data
    data_exp4 = load_experiment_data(exp_dir / "exp_4_polaron")
    data_exp6 = load_experiment_data(exp_dir / "exp_6_optimal")
    
    # Load ML results
    ml_results_file = project_root / "results" / "ml_models" / "ml_training_results.json"
    ml_results = {}
    if ml_results_file.exists():
        with open(ml_results_file) as f:
            ml_results = json.load(f)
    
    print(f"\nExp4 data points: {len(data_exp4)}")
    print(f"Exp6 data points: {len(data_exp6)}")
    
    # Generate figures
    print("\n--- Generating Figure 1: Synergistic Coupling ---")
    figure1_synergistic_coupling(data_exp6, figures_dir / "figure1_synergistic_coupling.pdf")
    
    print("\n--- Generating Figure 2: Polaron Mechanism ---")
    figure2_polaron_mechanism(data_exp4, data_exp6, figures_dir / "figure2_polaron_mechanism.pdf")
    
    print("\n--- Generating Figure 3: Comprehensive Summary ---")
    figure3_comprehensive_summary(data_exp6, ml_results, figures_dir / "figure3_comprehensive_summary.pdf")
    
    print("\n" + "=" * 60)
    print("All figures generated successfully!")
    print(f"Output directory: {figures_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()

