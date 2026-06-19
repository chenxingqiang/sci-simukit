#!/usr/bin/env python3
"""Legacy Exp9 energy extractor (inputs/*.out).

Prefer: python3 experiments/analysis/analyze_exp9_polaron.py
Outputs: dft_results/exp_9_charged_polaron/outputs/
JSON:    experiments/analysis/exp9_polaron_verification.json
"""

import os
import re
import json
from pathlib import Path

def extract_energy(out_file):
    """Extract final energy from CP2K output"""
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
    
    dopants = ['pristine', 'N', 'B', 'P']
    charges = [0, +1, -1]
    
    results = {}
    
    print("=" * 60)
    print("Extracting adiabatic energies from optimized structures")
    print("=" * 60)
    
    for dopant in dopants:
        results[dopant] = {}
        
        for charge in charges:
            charge_str = f"q{charge:+d}".replace('+', 'pos').replace('-', 'neg')
            # Look for single-point output (more accurate)
            sp_project = f"polaron_{dopant}_{charge_str}_sp"
            sp_file = inputs_dir / f"{sp_project}.out"
            
            # Fall back to GEO_OPT output
            if not sp_file.exists():
                sp_file = inputs_dir / f"polaron_{dopant}_{charge_str}_opt.out"
            
            if sp_file.exists():
                energy = extract_energy(sp_file)
                results[dopant][charge] = energy
                print(f"{dopant} (q={charge:+d}): {energy:.6f} Ha")
    
    print()
    print("=" * 60)
    print("Adiabatic Ionization Potentials and Electron Affinities")
    print("=" * 60)
    
    Ha_to_eV = 27.2114
    
    for dopant in dopants:
        if all(q in results[dopant] for q in [0, +1, -1]):
            E0 = results[dopant][0]
            Ep = results[dopant][+1]
            Em = results[dopant][-1]
            
            IP = (Ep - E0) * Ha_to_eV
            EA = (E0 - Em) * Ha_to_eV
            gap = IP - EA
            
            print(f"\n{dopant}:")
            print(f"  Adiabatic IP: {IP:.3f} eV")
            print(f"  Adiabatic EA: {EA:.3f} eV")
            print(f"  Fundamental Gap: {gap:.3f} eV")
    
    # Save results
    with open(Path(__file__).parent / "polaron_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to polaron_results.json")

if __name__ == "__main__":
    main()
