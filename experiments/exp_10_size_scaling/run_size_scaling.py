#!/usr/bin/env python3
"""
Experiment 10: Finite Size Effect Validation
=============================================
Goal: Study how properties scale with system size to validate
      that observed effects are not artifacts of small system size

System sizes:
- C60 monomer (60 atoms)
- C60 dimer (120 atoms)  
- C60 tetramer (240 atoms)
- C60 hexamer (360 atoms)
- C60 octamer (480 atoms)

Key metrics to track:
- Energy per atom convergence
- Strain sensitivity per C60 unit
- Formation energy per dopant
"""

import os
import sys
from pathlib import Path

# Import qHP C60 structure module
sys.path.insert(0, str(Path(__file__).parent.parent))
from qhp_c60_structures import (
    get_multi_c60_coordinates,
    get_supercell_dimensions,
    create_substitutional_doped_structure,
    format_coords_for_cp2k
)

def generate_size_scaling_input(n_molecules, dopant, output_dir):
    """Generate CP2K input for size scaling study"""
    
    # Get multi-C60 coordinates
    coords, cell_info = get_multi_c60_coordinates(n_molecules)
    
    # Apply doping if needed
    if dopant != 'pristine':
        # 1 dopant per C60
        concentration = n_molecules / len(coords)
        atoms, _ = create_substitutional_doped_structure(coords, dopant, concentration, seed=42)
    else:
        atoms = [('C', x, y, z) for x, y, z in coords]
    
    n_atoms = len(atoms)
    project_name = f"size_{n_molecules}x60_{dopant}"
    
    # Format coordinates
    coords_str = format_coords_for_cp2k(atoms)
    
    # Adjust SCF settings for larger systems
    if n_molecules >= 6:
        max_scf = 500
        cutoff = 350
    else:
        max_scf = 300
        cutoff = 400
    
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
      CUTOFF {cutoff}
      REL_CUTOFF 50
    &END MGRID
    
    &QS
      METHOD GPW
      EPS_DEFAULT 1.0E-10
    &END QS
    
    &SCF
      SCF_GUESS ATOMIC
      EPS_SCF 1.0E-6
      MAX_SCF {max_scf}
      
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
      &MULLIKEN
      &END MULLIKEN
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
    
    return input_file, project_name, n_atoms

def main():
    """Generate size scaling inputs"""
    
    output_dir = Path(__file__).parent / "inputs"
    output_dir.mkdir(exist_ok=True)
    
    # System sizes to test
    n_molecules_list = [1, 2, 4, 6, 8]
    dopants = ['pristine', 'N']
    
    print("=" * 60)
    print("Experiment 10: Finite Size Effect Validation")
    print("=" * 60)
    print(f"System sizes: {[n*60 for n in n_molecules_list]} atoms")
    print(f"Dopants: {dopants}")
    print(f"Total calculations: {len(n_molecules_list) * len(dopants)}")
    print()
    
    input_files = []
    
    for n_mol in n_molecules_list:
        for dopant in dopants:
            input_file, project, n_atoms = generate_size_scaling_input(
                n_mol, dopant, output_dir
            )
            input_files.append((input_file, project, n_atoms))
            print(f"Generated: {project}.inp ({n_atoms} atoms)")
    
    # Generate run script
    run_script = output_dir.parent / "run_all.sh"
    with open(run_script, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# Run size scaling calculations\n")
        f.write("# Note: Larger systems require more memory and time\n\n")
        f.write("cd inputs\n\n")
        
        for input_file, project, n_atoms in input_files:
            mem_estimate = n_atoms // 60 * 0.5
            n_cores = min(16, max(4, n_atoms // 30))
            
            f.write(f"echo '=== {project} ({n_atoms} atoms, ~{mem_estimate:.1f} GB) ==='\n")
            f.write(f"mpirun -np {n_cores} cp2k.popt -i {project}.inp -o {project}.out\n")
            f.write(f"echo 'Done.'\n\n")
    
    os.chmod(run_script, 0o755)
    
    # Generate analysis script
    analysis_script = output_dir.parent / "analyze_size_scaling.py"
    with open(analysis_script, 'w') as f:
        f.write('''#!/usr/bin/env python3
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
                match = re.search(r'(-\\d+\\.\\d+)', line)
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
            print(f"\\n{dopant}:")
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
    print(f"\\nSaved: size_scaling_analysis.png")
    
    with open(Path(__file__).parent / "size_scaling_results.json", 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
''')
    
    os.chmod(analysis_script, 0o755)
    
    print()
    print("Expected computational resources:")
    print("  60 atoms:  ~4 GB, ~10 min")
    print(" 120 atoms:  ~8 GB, ~30 min")
    print(" 240 atoms: ~16 GB, ~2 hours")
    print(" 360 atoms: ~24 GB, ~4 hours")
    print(" 480 atoms: ~32 GB, ~8 hours")
    print()
    print(f"Run script: {run_script}")
    print(f"Analysis: {analysis_script}")

if __name__ == "__main__":
    main()
