#!/usr/bin/env python3
"""
Experiment 9: Charged System Polaron Dynamics
==============================================
Goal: Study polaron formation and dynamics in charged (q=±1) systems
      Compare neutral vs charged states to understand charge carrier behavior

CORRECTED: 
- Two-step workflow: GEO_OPT first, then ENERGY
- Charged systems need geometry relaxation to capture polaron distortion

Key calculations:
- Neutral (q=0): Reference state
- Cation (q=+1): Hole polaron - geometry relaxation captures hole localization
- Anion (q=-1): Electron polaron - geometry relaxation captures electron localization

Derived properties:
- Adiabatic Ionization Potential (IP) = E_opt(q=+1) - E_opt(q=0)
- Adiabatic Electron Affinity (EA) = E_opt(q=0) - E_opt(q=-1)
- Polaron binding energy = E_vertical - E_adiabatic
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
        concentration = (n_dopants_per_c60 * 2) / 120.0
        atoms, _ = create_substitutional_doped_structure(coords, dopant, concentration, seed=42)
    else:
        atoms = [('C', x, y, z) for x, y, z in coords]
    
    return atoms, cell_info

def generate_geo_opt_input(dopant, charge, output_dir):
    """Generate CP2K input for charged system geometry optimization
    
    This captures the polaron distortion - critical for accurate IP/EA
    """
    atoms, cell_info = get_dimer_coords_with_doping(dopant)
    
    charge_str = f"q{charge:+d}".replace('+', 'pos').replace('-', 'neg')
    project_name = f"polaron_{dopant}_{charge_str}_opt"
    
    # Spin settings
    if charge == 0:
        multiplicity = 1
        uks = ".FALSE."
    else:
        multiplicity = 2
        uks = ".TRUE."
    
    coords_str = format_coords_for_cp2k(atoms)
    
    input_content = f"""&GLOBAL
  PROJECT {project_name}
  RUN_TYPE GEO_OPT
  PRINT_LEVEL MEDIUM
&END GLOBAL

&MOTION
  &GEO_OPT
    TYPE MINIMIZATION
    OPTIMIZER BFGS
    MAX_ITER 300
    MAX_DR 1.0E-3
    MAX_FORCE 1.0E-4
    RMS_DR 5.0E-4
    RMS_FORCE 5.0E-5
  &END GEO_OPT
  
  &PRINT
    &TRAJECTORY
      FORMAT XYZ
      &EACH
        GEO_OPT 1
      &END EACH
    &END TRAJECTORY
    
    &RESTART
      &EACH
        GEO_OPT 10
      &END EACH
    &END RESTART
  &END PRINT
&END MOTION

&FORCE_EVAL
  METHOD Quickstep
  
  &DFT
    BASIS_SET_FILE_NAME BASIS_MOLOPT
    POTENTIAL_FILE_NAME GTH_POTENTIALS
    
    CHARGE {charge}
    MULTIPLICITY {multiplicity}
    UKS {uks}
    
    &MGRID
      CUTOFF 300
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
    
    return input_file, project_name, cell_info

def generate_single_point_template(cell_info):
    """Template for final energy calculation on optimized geometry"""
    
    template = f"""&GLOBAL
  PROJECT {{project_name}}
  RUN_TYPE ENERGY
  PRINT_LEVEL MEDIUM
&END GLOBAL

&FORCE_EVAL
  METHOD Quickstep
  
  &DFT
    BASIS_SET_FILE_NAME BASIS_MOLOPT
    POTENTIAL_FILE_NAME GTH_POTENTIALS
    
    CHARGE {{charge}}
    MULTIPLICITY {{multiplicity}}
    UKS {{uks}}
    
    &MGRID
      CUTOFF 450
      REL_CUTOFF 55
    &END MGRID
    
    &QS
      METHOD GPW
      EPS_DEFAULT 1.0E-11
    &END QS
    
    &SCF
      SCF_GUESS ATOMIC
      EPS_SCF 1.0E-7
      MAX_SCF 500
      
      &OT
        MINIMIZER DIIS
        PRECONDITIONER FULL_ALL
      &END OT
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
    
    &TOPOLOGY
      COORD_FILE_NAME {{optimized_xyz}}
      COORD_FILE_FORMAT XYZ
    &END TOPOLOGY
    
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
    return template

def main():
    """Generate charged polaron inputs with geometry optimization"""
    
    output_dir = Path(__file__).parent / "inputs"
    output_dir.mkdir(exist_ok=True)
    
    dopants = ['pristine', 'N', 'B', 'P']
    charges = [0, +1, -1]
    
    print("=" * 60)
    print("Experiment 9: Charged System Polaron Dynamics")
    print("=" * 60)
    print("System: C60 dimer (120 atoms)")
    print("Workflow: GEO_OPT -> ENERGY (captures polaron distortion)")
    print(f"Dopants: {dopants}")
    print(f"Charges: {charges}")
    print(f"Total GEO_OPT calculations: {len(dopants) * len(charges)}")
    print()
    print("Physics to extract:")
    print("  - Adiabatic IP = E_opt(+1) - E_opt(0)")
    print("  - Adiabatic EA = E_opt(0) - E_opt(-1)")
    print("  - Polaron distortion from geometry comparison")
    print()
    
    input_files = []
    cell_info = None
    
    for dopant in dopants:
        for charge in charges:
            input_file, project, cell_info = generate_geo_opt_input(dopant, charge, output_dir)
            input_files.append((input_file, project, dopant, charge))
            charge_name = {0: 'neutral', 1: 'cation', -1: 'anion'}[charge]
            print(f"Generated: {project}.inp ({charge_name})")
    
    # Save single-point template
    template_file = output_dir / "single_point_template.inp"
    with open(template_file, 'w') as f:
        f.write(generate_single_point_template(cell_info))
    
    # Generate workflow script
    run_script = output_dir.parent / "run_workflow.sh"
    with open(run_script, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# Polaron workflow: GEO_OPT -> ENERGY\n")
        f.write("# Captures polaron lattice distortion\n\n")
        f.write("cd inputs\n\n")
        
        for input_file, project, dopant, charge in input_files:
            charge_name = {0: 'neutral', 1: 'cation (+1)', -1: 'anion (-1)'}[charge]
            mult = 1 if charge == 0 else 2
            uks = ".FALSE." if charge == 0 else ".TRUE."
            
            f.write(f"echo '=== {dopant} {charge_name}: Step 1 - GEO_OPT ==='\n")
            f.write(f"mpirun -np 8 cp2k.popt -i {project}.inp -o {project}.out\n")
            f.write(f"\n")
            f.write(f"# Extract optimized geometry (last frame: 122 lines = 1 atom count + 1 comment + 120 coords)\n")
            f.write(f"tail -n 122 {project}-pos-1.xyz > {project}_final.xyz\n")
            f.write(f"\n")
            f.write(f"echo '=== {dopant} {charge_name}: Step 2 - ENERGY ==='\n")
            sp_project = project.replace('_opt', '_sp')
            f.write(f"sed -e 's/{{project_name}}/{sp_project}/' \\\n")
            f.write(f"    -e 's/{{optimized_xyz}}/{project}_final.xyz/' \\\n")
            f.write(f"    -e 's/{{charge}}/{charge}/' \\\n")
            f.write(f"    -e 's/{{multiplicity}}/{mult}/' \\\n")
            f.write(f"    -e 's/{{uks}}/{uks}/' \\\n")
            f.write(f"    single_point_template.inp > {sp_project}.inp\n")
            f.write(f"\n")
            f.write(f"mpirun -np 8 cp2k.popt -i {sp_project}.inp -o {sp_project}.out\n")
            f.write(f"echo 'Done: {dopant} {charge_name}'\n\n")
    
    os.chmod(run_script, 0o755)
    
    # Generate analysis script
    analysis_script = output_dir.parent / "analyze_results.py"
    with open(analysis_script, 'w') as f:
        f.write('''#!/usr/bin/env python3
"""Analyze charged polaron calculation results - Adiabatic IP/EA"""

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
                match = re.search(r'(-\\d+\\.\\d+)', line)
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
            
            print(f"\\n{dopant}:")
            print(f"  Adiabatic IP: {IP:.3f} eV")
            print(f"  Adiabatic EA: {EA:.3f} eV")
            print(f"  Fundamental Gap: {gap:.3f} eV")
    
    # Save results
    with open(Path(__file__).parent / "polaron_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\\nResults saved to polaron_results.json")

if __name__ == "__main__":
    main()
''')
    
    os.chmod(analysis_script, 0o755)
    
    print()
    print(f"Generated {len(input_files)} GEO_OPT input files")
    print(f"Workflow script: {run_script}")
    print(f"Analysis script: {analysis_script}")

if __name__ == "__main__":
    main()
