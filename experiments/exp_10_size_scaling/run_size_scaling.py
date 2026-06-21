#!/usr/bin/env python3
"""
Experiment 10: Finite Size Effect Validation
=============================================
Goal: Study how properties scale with system size to validate
      that observed effects are not artifacts of small system size

CORRECTED:
- Include all dopant types (pristine, N, B, P) for completeness
- Test both 0% and +3% strain to verify strain-size coupling
- Focus on energy per atom convergence

System sizes:
- C60 monomer (60 atoms): Quick test
- C60 dimer (120 atoms): Standard for Exp1-6
- C60 tetramer (240 atoms): Network properties
- C60 hexamer (360 atoms): Larger network
- C60 octamer (480 atoms): Convergence check

Key metrics:
- Energy per atom convergence
- Strain sensitivity vs system size
- Formation energy per dopant vs system size
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

def generate_size_scaling_input(n_molecules, dopant, strain, output_dir):
    """Generate CP2K input for size scaling study with optional strain"""
    
    # Get multi-C60 coordinates
    coords, cell_info = get_multi_c60_coordinates(n_molecules)
    
    # Apply doping (1 dopant per C60 molecule)
    if dopant != 'pristine':
        concentration = n_molecules / len(coords)
        atoms, _ = create_substitutional_doped_structure(coords, dopant, concentration, seed=42)
    else:
        atoms = [('C', x, y, z) for x, y, z in coords]
    
    # Apply strain
    scale = 1.0 + strain / 100.0
    scaled_atoms = []
    for elem, x, y, z in atoms:
        scaled_atoms.append((elem, x * scale, y * scale, z))
    
    n_atoms = len(scaled_atoms)
    
    strain_str = f"{strain:+.0f}pct".replace('+', 'pos').replace('-', 'neg')
    project_name = f"size_{n_molecules}x60_{dopant}_{strain_str}"
    
    # Format coordinates
    coords_str = format_coords_for_cp2k(scaled_atoms)
    
    # Scale cell
    scaled_cell = {
        'a': cell_info['a'] * scale,
        'b': cell_info['b'] * scale,
        'c': cell_info['c']
    }
    
    # Adjust SCF settings for larger systems
    if n_molecules >= 6:
        max_scf = 500
        cutoff = 350  # production Exp10 n>=6 (400 Ry control: cutoff400.inp)
    else:
        max_scf = 300
        cutoff = 400  # production Exp10 n<=4
    
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
      ABC {scaled_cell['a']:.4f} {scaled_cell['b']:.4f} {scaled_cell['c']:.4f}
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
    """Generate size scaling inputs with all dopants and strain"""
    
    output_dir = Path(__file__).parent / "inputs"
    output_dir.mkdir(exist_ok=True)
    
    # System sizes
    n_molecules_list = [1, 2, 4, 6, 8]
    
    # All dopants (CORRECTED: include B and P)
    dopants = ['pristine', 'N', 'B', 'P']
    
    # Strain values (CORRECTED: test strain-size coupling)
    strains = [0.0, +3.0]
    
    total_calcs = len(n_molecules_list) * len(dopants) * len(strains)
    
    print("=" * 60)
    print("Experiment 10: Finite Size Effect Validation")
    print("=" * 60)
    print(f"System sizes: {[n*60 for n in n_molecules_list]} atoms")
    print(f"Dopants: {dopants}")
    print(f"Strains: {strains}%")
    print(f"Total calculations: {total_calcs}")
    print()
    
    input_files = []
    
    for n_mol in n_molecules_list:
        for dopant in dopants:
            for strain in strains:
                input_file, project, n_atoms = generate_size_scaling_input(
                    n_mol, dopant, strain, output_dir
                )
                input_files.append((input_file, project, n_atoms, dopant, strain))
                print(f"Generated: {project}.inp ({n_atoms} atoms)")
    
    # Generate run script with priority ordering (small systems first)
    run_script = output_dir.parent / "run_all.sh"
    with open(run_script, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# Size scaling calculations\n")
        f.write("# Ordered by size (small systems first for quick validation)\n\n")
        f.write("cd inputs\n\n")
        
        # Sort by number of atoms
        sorted_files = sorted(input_files, key=lambda x: x[2])
        
        for input_file, project, n_atoms, dopant, strain in sorted_files:
            mem_estimate = n_atoms // 60 * 0.5
            n_cores = min(16, max(4, n_atoms // 30))
            
            f.write(f"echo '=== {project} ({n_atoms} atoms, ~{mem_estimate:.1f} GB) ==='\n")
            f.write(f"mpirun -np {n_cores} cp2k.popt -i {project}.inp -o {project}.out\n")
            f.write(f"echo 'Done.'\n\n")
    
    os.chmod(run_script, 0o755)
    
    # Generate comprehensive analysis script
    analysis_script = output_dir.parent / "analyze_size_scaling.py"
    with open(analysis_script, 'w') as f:
        f.write('''#!/usr/bin/env python3
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
                match = re.search(r'(-\\d+\\.\\d+)', line)
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
    
    print("\\n" + "=" * 70)
    print("Energy per atom convergence (relative to largest system)")
    print("=" * 70)
    
    for dopant in dopants:
        print(f"\\n{dopant}:")
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
    print("\\n" + "=" * 70)
    print("Strain sensitivity vs system size")
    print("=" * 70)
    
    for dopant in dopants:
        if '+0%' in results[dopant] and '+3%' in results[dopant]:
            data_0 = results[dopant]['+0%']
            data_3 = results[dopant]['+3%']
            
            if len(data_0['E_per_c60']) == len(data_3['E_per_c60']) and len(data_0['E_per_c60']) > 0:
                print(f"\\n{dopant}:")
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
    print(f"\\nSaved: size_scaling_analysis.png")
    
    # Save JSON
    with open(Path(__file__).parent / "size_scaling_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    print("Saved: size_scaling_results.json")
    
    # Conclusion
    print("\\n" + "=" * 70)
    print("CONCLUSION: Finite Size Effects")
    print("=" * 70)
    print("If E/atom converges to < 1 meV for systems >= 120 atoms,")
    print("the dimer (120 atoms) used in Exp1-6 is reliable.")

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
    print(f"Total calculations: {total_calcs}")
    print(f"Run script: {run_script}")
    print(f"Analysis: {analysis_script}")

if __name__ == "__main__":
    main()
