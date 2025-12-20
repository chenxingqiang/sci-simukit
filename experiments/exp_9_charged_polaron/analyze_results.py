#!/usr/bin/env python3
"""Analyze charged polaron calculation results"""

import os
import re
import json
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
    
    dopants = ['pristine', 'N', 'B', 'P']
    charges = [0, +1, -1]
    
    results = {}
    
    for dopant in dopants:
        results[dopant] = {}
        
        for charge in charges:
            charge_str = f"q{charge:+d}".replace('+', 'pos').replace('-', 'neg')
            project = f"polaron_{dopant}_{charge_str}"
            out_file = inputs_dir / f"{project}.out"
            
            if out_file.exists():
                energy = extract_energy(out_file)
                results[dopant][charge] = energy
                print(f"{dopant} (q={charge:+d}): {energy:.6f} Ha")
    
    print()
    print("=" * 50)
    print("Derived Properties:")
    print("=" * 50)
    
    Ha_to_eV = 27.2114
    
    for dopant in dopants:
        if all(q in results[dopant] for q in [0, +1, -1]):
            E0 = results[dopant][0]
            Ep = results[dopant][+1]
            Em = results[dopant][-1]
            
            IP = (Ep - E0) * Ha_to_eV
            EA = (E0 - Em) * Ha_to_eV
            
            print(f"\n{dopant}:")
            print(f"  Ionization Potential (IP): {IP:.3f} eV")
            print(f"  Electron Affinity (EA): {EA:.3f} eV")
            print(f"  Fundamental Gap: {IP - EA:.3f} eV")
    
    # Save results
    with open(Path(__file__).parent / "polaron_results.json", 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
