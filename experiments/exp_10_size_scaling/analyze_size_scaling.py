#!/usr/bin/env python3
"""Analyze size scaling results to check finite size effects"""

import os
import re
import json
import matplotlib.pyplot as plt
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
    dopants = ['pristine', 'N']
    
    results = {}
    
    for dopant in dopants:
        results[dopant] = {'n_atoms': [], 'E_total': [], 'E_per_atom': [], 'E_per_c60': []}
        
        for n_mol in n_molecules_list:
            n_atoms = n_mol * 60
            project = f"size_{n_mol}x60_{dopant}"
            out_file = inputs_dir / f"{project}.out"
            
            if out_file.exists():
                energy = extract_energy(out_file)
                if energy:
                    results[dopant]['n_atoms'].append(n_atoms)
                    results[dopant]['E_total'].append(energy)
                    results[dopant]['E_per_atom'].append(energy / n_atoms)
                    results[dopant]['E_per_c60'].append(energy / n_mol)
                    
                    print(f"{dopant} ({n_atoms} atoms): E = {energy:.6f} Ha, "
                          f"E/atom = {energy/n_atoms:.6f} Ha")
    
    print()
    print("=" * 50)
    print("Size Convergence Analysis:")
    print("=" * 50)
    
    Ha_to_meV = 27211.4
    
    for dopant in dopants:
        if len(results[dopant]['E_per_atom']) > 1:
            e_per_atom = results[dopant]['E_per_atom']
            n_atoms = results[dopant]['n_atoms']
            
            e_ref = e_per_atom[-1]
            print(f"\n{dopant}:")
            for i, (n, e) in enumerate(zip(n_atoms, e_per_atom)):
                diff_meV = (e - e_ref) * Ha_to_meV
                print(f"  {n} atoms: E/atom - E_ref = {diff_meV:+.2f} meV/atom")
    
    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    for dopant in dopants:
        if len(results[dopant]['n_atoms']) > 0:
            axes[0].plot(results[dopant]['n_atoms'], 
                        [e * Ha_to_meV for e in results[dopant]['E_per_atom']],
                        'o-', label=dopant, markersize=8)
            
            if dopant != 'pristine' and 'pristine' in results:
                if len(results[dopant]['E_per_c60']) == len(results['pristine']['E_per_c60']):
                    form_e = [(e_d - e_p) * 27.2114 
                             for e_d, e_p in zip(results[dopant]['E_per_c60'], 
                                                 results['pristine']['E_per_c60'])]
                    axes[1].plot(results[dopant]['n_atoms'], form_e, 
                                'o-', label=f'{dopant} formation E', markersize=8)
    
    axes[0].set_xlabel('Number of atoms')
    axes[0].set_ylabel('Energy per atom (meV)')
    axes[0].set_title('Size Convergence')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    axes[1].set_xlabel('Number of atoms')
    axes[1].set_ylabel('Formation energy per C60 (eV)')
    axes[1].set_title('Formation Energy Convergence')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'size_scaling_analysis.png', dpi=150)
    print(f"\nSaved: size_scaling_analysis.png")
    
    with open(Path(__file__).parent / "size_scaling_results.json", 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
