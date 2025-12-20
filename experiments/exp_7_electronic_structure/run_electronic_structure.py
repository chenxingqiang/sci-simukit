#!/usr/bin/env python3
"""
Experiment 7: Electronic Structure Analysis
============================================
Goal: Extract HOMO-LUMO gap, MO energy levels, and electron density
      for B/N/P-doped C60 systems under strain

Key CP2K additions:
- MO eigenvalue output
- Electron density cube files
- PDOS (Projected Density of States)
"""

import os
import sys
import numpy as np
from pathlib import Path

# Import qHP C60 structure module
sys.path.insert(0, str(Path(__file__).parent.parent))
from qhp_c60_structures import (
    get_single_c60_coordinates,
    create_substitutional_doped_structure,
    format_coords_for_cp2k
)

def get_c60_coords_with_strain_and_doping(strain_percent, dopant, n_dopants=4):
    """Get C60 coordinates with strain and doping applied"""
    coords = get_single_c60_coordinates()
    scale = 1.0 + strain_percent / 100.0
    
    # Apply doping
    if dopant != 'pristine':
        concentration = n_dopants / 60.0
        atoms, _ = create_substitutional_doped_structure(coords, dopant, concentration, seed=42)
    else:
        atoms = [('C', x, y, z) for x, y, z in coords]
    
    # Apply biaxial strain and format
    formatted_lines = []
    for elem, x, y, z in atoms:
        x_scaled = x * scale
        y_scaled = y * scale
        z_scaled = z  # No strain in z for 2D
        formatted_lines.append(f"      {elem}  {x_scaled:.6f}  {y_scaled:.6f}  {z_scaled:.6f}")
    
    return '\n'.join(formatted_lines)

def generate_cp2k_input(strain, dopant, output_dir):
    """Generate CP2K input with electronic structure output"""
    
    coords = get_c60_coords_with_strain_and_doping(strain, dopant)
    
    strain_str = f"{strain:+.1f}".replace('.', 'p').replace('+', 'pos').replace('-', 'neg')
    project_name = f"elec_{strain_str}_{dopant}"
    
    # Box size with strain
    box_size = 20.0 * (1.0 + strain / 100.0)
    
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
      MAX_SCF 300
      
      &OT
        MINIMIZER DIIS
        PRECONDITIONER FULL_ALL
      &END OT
      
      &OUTER_SCF
        MAX_SCF 20
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
      ! MO Eigenvalues - Key for HOMO-LUMO gap
      &MO
        EIGENVALUES .TRUE.
        OCCUPATION_NUMBERS .TRUE.
        NDIGITS 8
        &EACH
          QS_SCF 0
        &END EACH
      &END MO
      
      ! MO Cube files for orbital visualization
      &MO_CUBES
        NHOMO 3
        NLUMO 3
        WRITE_CUBE .TRUE.
      &END MO_CUBES
      
      ! Total electron density
      &E_DENSITY_CUBE
        STRIDE 2 2 2
      &END E_DENSITY_CUBE
      
      ! Projected DOS
      &PDOS
        NLUMO 10
        COMPONENTS .TRUE.
      &END PDOS
      
      ! Mulliken population analysis
      &MULLIKEN
      &END MULLIKEN
      
      ! Hirshfeld charges
      &HIRSHFELD
      &END HIRSHFELD
    &END PRINT
  &END DFT
  
  &SUBSYS
    &CELL
      ABC {box_size:.4f} {box_size:.4f} 20.0000
      PERIODIC XYZ
    &END CELL
    
    &COORD
{coords}
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
    """Generate inputs for electronic structure analysis"""
    
    output_dir = Path(__file__).parent / "inputs"
    output_dir.mkdir(exist_ok=True)
    
    # Parameters: representative strain values and all dopants
    strains = [-5.0, 0.0, +5.0]  # Key strain points
    dopants = ['pristine', 'B', 'N', 'P']
    
    print("=" * 60)
    print("Experiment 7: Electronic Structure Analysis")
    print("=" * 60)
    print(f"Strains: {strains}")
    print(f"Dopants: {dopants}")
    print(f"Total calculations: {len(strains) * len(dopants)}")
    print()
    
    input_files = []
    
    for strain in strains:
        for dopant in dopants:
            input_file, project = generate_cp2k_input(strain, dopant, output_dir)
            input_files.append((input_file, project))
            print(f"Generated: {project}.inp")
    
    # Generate run script
    run_script = output_dir.parent / "run_all.sh"
    with open(run_script, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# Run all electronic structure calculations\n\n")
        f.write("cd inputs\n\n")
        for input_file, project in input_files:
            f.write(f"echo 'Running {project}...'\n")
            f.write(f"mpirun -np 8 cp2k.popt -i {project}.inp -o {project}.out\n")
            f.write("echo 'Done.'\n\n")
    
    os.chmod(run_script, 0o755)
    
    print()
    print(f"Generated {len(input_files)} input files in: {output_dir}")
    print(f"Run script: {run_script}")
    print()
    print("Output files will include:")
    print("  - *.out: Total energies and MO eigenvalues")
    print("  - *-WFN_*.cube: HOMO/LUMO orbital cube files")
    print("  - *-ELECTRON_DENSITY-*.cube: Electron density")
    print("  - *.pdos: Projected density of states")

if __name__ == "__main__":
    main()

