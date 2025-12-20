#!/usr/bin/env python3
"""
Experiment 8: Geometry Optimization + Single Point Energy
==========================================================
Goal: First optimize the structure, then calculate accurate energies
      This ensures reliable equilibrium geometries before property calculation

Two-step workflow:
1. GEO_OPT: Find equilibrium structure
2. ENERGY: Calculate properties at optimized geometry
"""

import os
import sys
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
        z_scaled = z
        formatted_lines.append(f"      {elem}  {x_scaled:.6f}  {y_scaled:.6f}  {z_scaled:.6f}")
    
    return '\n'.join(formatted_lines)

def generate_geo_opt_input(strain, dopant, output_dir):
    """Generate CP2K input for geometry optimization"""
    
    coords = get_c60_coords_with_strain_and_doping(strain, dopant)
    
    strain_str = f"{strain:+.1f}".replace('.', 'p').replace('+', 'pos').replace('-', 'neg')
    project_name = f"geoopt_{strain_str}_{dopant}"
    
    box_size = 15.0 * (1.0 + strain / 100.0)
    
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
      &FORCES
      &END FORCES
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

def generate_single_point_template():
    """Generate template for single-point calculation on optimized geometry"""
    
    template = """&GLOBAL
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
      CUTOFF 500
      REL_CUTOFF 60
    &END MGRID
    
    &QS
      METHOD GPW
      EPS_DEFAULT 1.0E-12
    &END QS
    
    &SCF
      SCF_GUESS RESTART
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
      
      &MULLIKEN
      &END MULLIKEN
    &END PRINT
  &END DFT
  
  &SUBSYS
    &CELL
      ABC {box_a} {box_b} {box_c}
      PERIODIC XYZ
    &END CELL
    
    &TOPOLOGY
      COORD_FILE_NAME {optimized_xyz}
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
    
    # Representative configurations
    strains = [0.0, +3.0]
    dopants = ['pristine', 'N', 'B', 'P']
    
    print("=" * 60)
    print("Experiment 8: Geometry Optimization + Single Point")
    print("=" * 60)
    print(f"Strains: {strains}")
    print(f"Dopants: {dopants}")
    print(f"Total GEO_OPT calculations: {len(strains) * len(dopants)}")
    print()
    
    input_files = []
    
    for strain in strains:
        for dopant in dopants:
            input_file, project = generate_geo_opt_input(strain, dopant, output_dir)
            input_files.append((input_file, project))
            print(f"Generated: {project}.inp")
    
    # Save single-point template
    template_file = output_dir / "single_point_template.inp"
    with open(template_file, 'w') as f:
        f.write(generate_single_point_template())
    print(f"\nSingle-point template: {template_file}")
    
    # Generate workflow script
    workflow_script = output_dir.parent / "run_workflow.sh"
    with open(workflow_script, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# Two-step workflow: GEO_OPT -> ENERGY\n\n")
        f.write("cd inputs\n\n")
        
        for input_file, project in input_files:
            f.write(f"echo '=== Step 1: Geometry Optimization - {project} ==='\n")
            f.write(f"mpirun -np 8 cp2k.popt -i {project}.inp -o {project}.out\n")
            f.write(f"\n")
            f.write(f"# Extract final geometry from trajectory\n")
            f.write(f"tail -n 61 {project}-pos-1.xyz > {project}_optimized.xyz\n")
            f.write(f"\n")
            f.write(f"echo '=== Step 2: Single Point Energy - {project} ==='\n")
            f.write(f"sed -e 's/{{project_name}}/{project}_sp/' \\\n")
            f.write(f"    -e 's/{{optimized_xyz}}/{project}_optimized.xyz/' \\\n")
            f.write(f"    -e 's/{{box_a}}/15.0/' \\\n")
            f.write(f"    -e 's/{{box_b}}/15.0/' \\\n")
            f.write(f"    -e 's/{{box_c}}/20.0/' \\\n")
            f.write(f"    single_point_template.inp > {project}_sp.inp\n")
            f.write(f"\n")
            f.write(f"mpirun -np 8 cp2k.popt -i {project}_sp.inp -o {project}_sp.out\n")
            f.write(f"echo 'Done: {project}'\n\n")
    
    os.chmod(workflow_script, 0o755)
    
    print()
    print(f"Workflow: {workflow_script}")
    print("  1. Geometry optimization")
    print("  2. Extract optimized coordinates")
    print("  3. Single-point with tighter convergence")

if __name__ == "__main__":
    main()
