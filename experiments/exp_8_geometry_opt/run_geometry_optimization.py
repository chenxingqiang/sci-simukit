#!/usr/bin/env python3
"""
Experiment 8: Geometry Optimization
====================================
Goal: Optimize equilibrium structures for pristine and doped C60 dimers
      WITHOUT strain - strain would be released during optimization

CORRECTED:
- Uses C60 dimer (120 atoms) for consistency with Exp1-6
- Only 0% strain (optimization would release any applied strain)
- Fixed cell parameters (only optimize atomic positions)

Two-step workflow:
1. GEO_OPT: Find equilibrium atomic positions (fixed cell)
2. ENERGY: Calculate properties at optimized geometry
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
    """Get C60 dimer coordinates with optional doping (no strain)"""
    coords, cell_info = get_c60_dimer_coordinates(separation=10.0)
    
    # Apply doping
    if dopant != 'pristine':
        concentration = (n_dopants_per_c60 * 2) / 120.0
        atoms, _ = create_substitutional_doped_structure(coords, dopant, concentration, seed=42)
    else:
        atoms = [('C', x, y, z) for x, y, z in coords]
    
    return atoms, cell_info

def generate_geo_opt_input(dopant, output_dir):
    """Generate CP2K input for geometry optimization (no strain)"""
    
    atoms, cell_info = get_dimer_coords_with_doping(dopant)
    coords_str = format_coords_for_cp2k(atoms)
    
    project_name = f"geoopt_{dopant}"
    
    input_content = f"""&GLOBAL
  PROJECT {project_name}
  RUN_TYPE GEO_OPT
  PRINT_LEVEL MEDIUM
&END GLOBAL

&MOTION
  &GEO_OPT
    TYPE MINIMIZATION
    OPTIMIZER BFGS
    MAX_ITER 500
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
    """Generate template for single-point calculation on optimized geometry"""
    
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
    
    &MGRID
      CUTOFF 500
      REL_CUTOFF 60
    &END MGRID
    
    &QS
      METHOD GPW
      EPS_DEFAULT 1.0E-12
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
        NDIGITS 10
      &END MO
      
      &MO_CUBES
        NHOMO 3
        NLUMO 3
        WRITE_CUBE .TRUE.
      &END MO_CUBES
      
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
    """Generate geometry optimization inputs"""
    
    output_dir = Path(__file__).parent / "inputs"
    output_dir.mkdir(exist_ok=True)
    
    # Only optimize 0% strain structures - strain would be released during optimization
    dopants = ['pristine', 'N', 'B', 'P']
    
    print("=" * 60)
    print("Experiment 8: Geometry Optimization (Fixed Cell)")
    print("=" * 60)
    print("System: C60 dimer (120 atoms)")
    print("Strain: 0% only (optimization would release applied strain)")
    print(f"Dopants: {dopants}")
    print(f"Total GEO_OPT calculations: {len(dopants)}")
    print()
    
    input_files = []
    cell_info = None
    
    for dopant in dopants:
        input_file, project, cell_info = generate_geo_opt_input(dopant, output_dir)
        input_files.append((input_file, project))
        print(f"Generated: {project}.inp")
    
    # Save single-point template
    template_file = output_dir / "single_point_template.inp"
    with open(template_file, 'w') as f:
        f.write(generate_single_point_template(cell_info))
    print(f"\nSingle-point template: {template_file}")
    
    # Generate workflow script
    workflow_script = output_dir.parent / "run_workflow.sh"
    with open(workflow_script, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# Two-step workflow: GEO_OPT -> ENERGY\n")
        f.write("# System: C60 dimer (120 atoms), no strain\n\n")
        f.write("cd inputs\n\n")
        
        for input_file, project in input_files:
            f.write(f"echo '=== Step 1: Geometry Optimization - {project} ==='\n")
            f.write(f"mpirun -np 8 cp2k.popt -i {project}.inp -o {project}.out\n")
            f.write(f"\n")
            f.write(f"# Extract final geometry from trajectory\n")
            f.write(f"tail -n 121 {project}-pos-1.xyz > {project}_optimized.xyz\n")
            f.write(f"\n")
            f.write(f"echo '=== Step 2: Single Point Energy - {project} ==='\n")
            f.write(f"sed -e 's/{{project_name}}/{project}_sp/' \\\n")
            f.write(f"    -e 's/{{optimized_xyz}}/{project}_optimized.xyz/' \\\n")
            f.write(f"    single_point_template.inp > {project}_sp.inp\n")
            f.write(f"\n")
            f.write(f"mpirun -np 8 cp2k.popt -i {project}_sp.inp -o {project}_sp.out\n")
            f.write(f"echo 'Done: {project}'\n\n")
    
    os.chmod(workflow_script, 0o755)
    
    print()
    print(f"Workflow: {workflow_script}")
    print("  1. Geometry optimization (fixed cell, optimize atoms)")
    print("  2. Extract optimized coordinates")
    print("  3. Single-point with tighter convergence + MO output")
    print()
    print("Purpose: Obtain equilibrium structures and verify doping effects")

if __name__ == "__main__":
    main()
