#!/usr/bin/env python3
"""
Experiment 9: Charged System Polaron Dynamics
==============================================
Goal: Study polaron formation and dynamics in charged (q=±1) systems
      Compare neutral vs charged states to understand charge carrier behavior

Key calculations:
- Neutral (q=0): Reference state
- Cation (q=+1): Hole polaron
- Anion (q=-1): Electron polaron

Derived properties:
- Ionization potential (IP) = E(q=+1) - E(q=0)
- Electron affinity (EA) = E(q=0) - E(q=-1)
- Polaron formation energy
- Charge localization (from spin density)
"""

import os
import sys
from pathlib import Path

# Import qHP C60 structure module
sys.path.insert(0, str(Path(__file__).parent.parent))
from qhp_c60_structures import (
    get_c60_dimer_coordinates,
    create_substitutional_doped_structure,
    format_coords_for_cp2k
)

def get_dimer_coords_with_doping(dopant, n_dopants_per_c60=2):
    """Get C60 dimer coordinates with optional doping"""
    coords, cell_info = get_c60_dimer_coordinates(separation=10.0)
    
    # Apply doping
    if dopant != 'pristine':
        concentration = (n_dopants_per_c60 * 2) / 120.0  # 2 C60s
        atoms, _ = create_substitutional_doped_structure(coords, dopant, concentration, seed=42)
    else:
        atoms = [('C', x, y, z) for x, y, z in coords]
    
    return atoms, cell_info

def generate_charged_input(dopant, charge, output_dir):
    """Generate CP2K input for charged system"""
    
    atoms, cell_info = get_dimer_coords_with_doping(dopant)
    
    charge_str = f"q{charge:+d}".replace('+', 'pos').replace('-', 'neg')
    project_name = f"polaron_{dopant}_{charge_str}"
    
    # Determine multiplicity (spin)
    if charge == 0:
        multiplicity = 1
        uks = ".FALSE."
    else:
        multiplicity = 2
        uks = ".TRUE."
    
    # Format coordinates
    coords_str = format_coords_for_cp2k(atoms)
    
    input_content = f"""&GLOBAL
  PROJECT {project_name}
  RUN_TYPE ENERGY
  PRINT_LEVEL MEDIUM
&END GLOBAL

&FORCE_EVAL
  METHOD Quickstep
  
  &DFT
    BASIS_SET_FILE_NAME BASIS_MOLOPT
    POTENTIAL_FILE_NAME GTH_POTENTIALS
    
    CHARGE {charge}
    MULTIPLICITY {multiplicity}
    UKS {uks}
    
    &MGRID
      CUTOFF 400
      REL_CUTOFF 50
    &END MGRID
    
    &QS
      METHOD GPW
      EPS_DEFAULT 1.0E-10
    &END QS
    
    &SCF
      SCF_GUESS ATOMIC
      EPS_SCF 1.0E-6
      MAX_SCF 500
      
      &OT
        MINIMIZER DIIS
        PRECONDITIONER FULL_ALL
      &END OT
      
      &OUTER_SCF
        MAX_SCF 30
        EPS_SCF 1.0E-6
      &END OUTER_SCF
    &END SCF
    
    &XC
      &XC_FUNCTIONAL PBE
      &END XC_FUNCTIONAL
      
      &VDW_POTENTIAL
        POTENTIAL_TYPE PAIR_POTENTIAL
        &PAIR_POTENTIAL
          TYPE DFTD3
          PARAMETER_FILE_NAME dftd3.dat
          REFERENCE_FUNCTIONAL PBE
        &END PAIR_POTENTIAL
      &END VDW_POTENTIAL
    &END XC
    
    &PRINT
      &MO
        EIGENVALUES .TRUE.
        OCCUPATION_NUMBERS .TRUE.
        NDIGITS 8
      &END MO
      
      &V_HARTREE_CUBE
        STRIDE 2 2 2
      &END V_HARTREE_CUBE
      
      &MULLIKEN
      &END MULLIKEN
      
      &HIRSHFELD
      &END HIRSHFELD
    &END PRINT
  &END DFT
  
  &SUBSYS
    &CELL
      ABC {cell_info['a']:.4f} {cell_info['b']:.4f} {cell_info['c']:.4f}
      PERIODIC XYZ
    &END CELL
    
    &COORD
{coords_str}
    &END COORD
    
    &KIND C
      BASIS_SET DZVP-MOLOPT-SR-GTH
      POTENTIAL GTH-PBE-q4
    &END KIND
    
    &KIND B
      BASIS_SET DZVP-MOLOPT-SR-GTH
      POTENTIAL GTH-PBE-q3
    &END KIND
    
    &KIND N
      BASIS_SET DZVP-MOLOPT-SR-GTH
      POTENTIAL GTH-PBE-q5
    &END KIND
    
    &KIND P
      BASIS_SET DZVP-MOLOPT-SR-GTH
      POTENTIAL GTH-PBE-q5
    &END KIND
  &END SUBSYS
&END FORCE_EVAL
"""
    
    input_file = os.path.join(output_dir, f"{project_name}.inp")
    with open(input_file, 'w') as f:
        f.write(input_content)
    
    return input_file, project_name

def main():
    """Generate charged system inputs for polaron study"""
    
    output_dir = Path(__file__).parent / "inputs"
    output_dir.mkdir(exist_ok=True)
    
    dopants = ['pristine', 'N', 'B', 'P']
    charges = [0, +1, -1]
    
    print("=" * 60)
    print("Experiment 9: Charged System Polaron Dynamics")
    print("=" * 60)
    print(f"Dopants: {dopants}")
    print(f"Charges: {charges}")
    print(f"Total calculations: {len(dopants) * len(charges)}")
    print()
    print("Physics to extract:")
    print("  - Ionization Potential (IP) = E(+1) - E(0)")
    print("  - Electron Affinity (EA) = E(0) - E(-1)")
    print("  - Fundamental Gap = IP - EA")
    print()
    
    input_files = []
    
    for dopant in dopants:
        for charge in charges:
            input_file, project = generate_charged_input(dopant, charge, output_dir)
            input_files.append((input_file, project, dopant, charge))
            charge_name = {0: 'neutral', 1: 'cation', -1: 'anion'}[charge]
            print(f"Generated: {project}.inp ({charge_name})")
    
    # Generate run script
    run_script = output_dir.parent / "run_all.sh"
    with open(run_script, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# Run all charged polaron calculations\n\n")
        f.write("cd inputs\n\n")
        
        for input_file, project, dopant, charge in input_files:
            charge_name = {0: 'neutral', 1: 'cation (+1)', -1: 'anion (-1)'}[charge]
            f.write(f"echo 'Running {dopant} {charge_name}...'\n")
            f.write(f"mpirun -np 8 cp2k.popt -i {project}.inp -o {project}.out\n")
            f.write(f"echo 'Done.'\n\n")
    
    os.chmod(run_script, 0o755)
    
    # Generate analysis script
    analysis_script = output_dir.parent / "analyze_results.py"
    with open(analysis_script, 'w') as f:
        f.write('''#!/usr/bin/env python3
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
                match = re.search(r'(-\\d+\\.\\d+)', line)
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
            
            print(f"\\n{dopant}:")
            print(f"  Ionization Potential (IP): {IP:.3f} eV")
            print(f"  Electron Affinity (EA): {EA:.3f} eV")
            print(f"  Fundamental Gap: {IP - EA:.3f} eV")
    
    # Save results
    with open(Path(__file__).parent / "polaron_results.json", 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
''')
    
    os.chmod(analysis_script, 0o755)
    
    print()
    print(f"Generated {len(input_files)} input files")
    print(f"Run script: {run_script}")
    print(f"Analysis: {analysis_script}")

if __name__ == "__main__":
    main()
