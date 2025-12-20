#!/usr/bin/env python3
"""
Analyze size scaling results - Check finite size effects
Verifies that small system results are reliable
"""

import os
import re
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def extract_energy(out_file):
    """Extract total energy from CP2K output"""
    energy = None
    with open(out_file, 'r') as f:
        for line in f:
            if 'ENERGY| Total FORCE_EVAL' in line:
                match = re.search(r'(-\d+\.\d+)', line)
                if match:
                    energy = float(match.group(1))
    return energy

def main():
    inputs_dir = Path(__file__).parent / "inputs"
    
    n_molecules_list = [1, 2, 4, 6, 8]
    dopants = ['pristine', 'N', 'B', 'P']
    strains = [0.0, 3.0]
    
    # Collect all results
    results = {}
    
    print("=" * 70)
    print("Size Scaling Analysis - Finite Size Effect Validation")
    print("=" * 70)
    
    for dopant in dopants:
        results[dopant] = {}
        for strain in strains:
            strain_key = f"{strain:+.0f}%"
            results[dopant][strain_key] = {
                'n_atoms': [], 
                'E_total': [], 
                'E_per_atom': [], 
                'E_per_c60': []
            }
            
            for n_mol in n_molecules_list:
                n_atoms = n_mol * 60
                strain_str = f"{strain:+.0f}pct".replace('+', 'pos').replace('-', 'neg')
                project = f"size_{n_mol}x60_{dopant}_{strain_str}"
                out_file = inputs_dir / f"{project}.out"
                
                if out_file.exists():
                    energy = extract_energy(out_file)
                    if energy:
                        results[dopant][strain_key]['n_atoms'].append(n_atoms)
                        results[dopant][strain_key]['E_total'].append(energy)
                        results[dopant][strain_key]['E_per_atom'].append(energy / n_atoms)
                        results[dopant][strain_key]['E_per_c60'].append(energy / n_mol)
    
    # Print convergence analysis
    Ha_to_meV = 27211.4
    
    print("\n" + "=" * 70)
    print("Energy per atom convergence (relative to largest system)")
    print("=" * 70)
    
    for dopant in dopants:
        print(f"\n{dopant}:")
        for strain_key in results[dopant]:
            data = results[dopant][strain_key]
            if len(data['E_per_atom']) > 1:
                e_per_atom = data['E_per_atom']
                n_atoms = data['n_atoms']
                e_ref = e_per_atom[-1]  # Largest system as reference
                
                print(f"  Strain {strain_key}:")
                for n, e in zip(n_atoms, e_per_atom):
                    diff_meV = (e - e_ref) * Ha_to_meV
                    print(f"    {n:3d} atoms: ΔE = {diff_meV:+8.2f} meV/atom")
    
    # Strain sensitivity vs size
    print("\n" + "=" * 70)
    print("Strain sensitivity vs system size")
    print("=" * 70)
    
    for dopant in dopants:
        if '+0%' in results[dopant] and '+3%' in results[dopant]:
            data_0 = results[dopant]['+0%']
            data_3 = results[dopant]['+3%']
            
            if len(data_0['E_per_c60']) == len(data_3['E_per_c60']) and len(data_0['E_per_c60']) > 0:
                print(f"\n{dopant}:")
                for i, n in enumerate(data_0['n_atoms']):
                    dE = (data_3['E_per_c60'][i] - data_0['E_per_c60'][i]) * 27.2114 * 1000 / 3.0  # meV/%
                    print(f"  {n:3d} atoms: dE/dε = {dE:+.2f} meV/%")
    
    # Generate plots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    colors = {'pristine': 'black', 'N': 'blue', 'B': 'red', 'P': 'green'}
    markers = {'+0%': 'o', '+3%': 's'}
    
    # Panel 1: E/atom convergence at 0% strain
    ax = axes[0, 0]
    for dopant in dopants:
        if '+0%' in results[dopant] and len(results[dopant]['+0%']['n_atoms']) > 0:
            data = results[dopant]['+0%']
            e_rel = [(e - data['E_per_atom'][-1]) * Ha_to_meV for e in data['E_per_atom']]
            ax.plot(data['n_atoms'], e_rel, 'o-', 
                   color=colors[dopant], label=dopant, markersize=8)
    ax.set_xlabel('Number of atoms')
    ax.set_ylabel('ΔE/atom (meV) vs largest')
    ax.set_title('Energy Convergence (0% strain)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    
    # Panel 2: E/atom convergence at 3% strain
    ax = axes[0, 1]
    for dopant in dopants:
        if '+3%' in results[dopant] and len(results[dopant]['+3%']['n_atoms']) > 0:
            data = results[dopant]['+3%']
            e_rel = [(e - data['E_per_atom'][-1]) * Ha_to_meV for e in data['E_per_atom']]
            ax.plot(data['n_atoms'], e_rel, 's-', 
                   color=colors[dopant], label=dopant, markersize=8)
    ax.set_xlabel('Number of atoms')
    ax.set_ylabel('ΔE/atom (meV) vs largest')
    ax.set_title('Energy Convergence (3% strain)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    
    # Panel 3: Strain sensitivity vs size
    ax = axes[1, 0]
    for dopant in dopants:
        if '+0%' in results[dopant] and '+3%' in results[dopant]:
            data_0 = results[dopant]['+0%']
            data_3 = results[dopant]['+3%']
            if len(data_0['E_per_c60']) == len(data_3['E_per_c60']) and len(data_0['E_per_c60']) > 0:
                sensitivities = []
                for i in range(len(data_0['E_per_c60'])):
                    dE = (data_3['E_per_c60'][i] - data_0['E_per_c60'][i]) * 27.2114 * 1000 / 3.0
                    sensitivities.append(dE)
                ax.plot(data_0['n_atoms'], sensitivities, 'o-',
                       color=colors[dopant], label=dopant, markersize=8)
    ax.set_xlabel('Number of atoms')
    ax.set_ylabel('Strain sensitivity (meV/%)')
    ax.set_title('Strain Sensitivity vs System Size')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Panel 4: Formation energy convergence
    ax = axes[1, 1]
    for dopant in dopants:
        if dopant != 'pristine' and '+0%' in results[dopant] and '+0%' in results['pristine']:
            data_d = results[dopant]['+0%']
            data_p = results['pristine']['+0%']
            if len(data_d['E_per_c60']) == len(data_p['E_per_c60']) and len(data_d['E_per_c60']) > 0:
                form_e = [(ed - ep) * 27.2114 
                         for ed, ep in zip(data_d['E_per_c60'], data_p['E_per_c60'])]
                ax.plot(data_d['n_atoms'], form_e, 'o-',
                       color=colors[dopant], label=f'{dopant} doping', markersize=8)
    ax.set_xlabel('Number of atoms')
    ax.set_ylabel('Formation energy per C60 (eV)')
    ax.set_title('Formation Energy Convergence')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'size_scaling_analysis.png', dpi=150)
    print(f"\nSaved: size_scaling_analysis.png")
    
    # Save JSON
    with open(Path(__file__).parent / "size_scaling_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    print("Saved: size_scaling_results.json")
    
    # Conclusion
    print("\n" + "=" * 70)
    print("CONCLUSION: Finite Size Effects")
    print("=" * 70)
    print("If E/atom converges to < 1 meV for systems >= 120 atoms,")
    print("the dimer (120 atoms) used in Exp1-6 is reliable.")

if __name__ == "__main__":
    main()
