#!/usr/bin/env python3
"""
qHP C60 Network Structure Module

Provides qHP (quasi-hexagonal-planar) C60 network structures for DFT calculations.
These structures are from validated reference files in graphullerene/ directory.

Structure hierarchy:
- 1x C60 monomer (60 atoms): Basic unit, for quick tests
- 2x C60 dimer (120 atoms): For J coupling and polaron calculations
- 4x C60 network (240 atoms): For network properties (bandgap, mobility)

Paper reference lattice parameters:
- a = 36.67 Å (along [100])
- b = 30.84 Å (along [010])

Author: X.Q. Chen
Date: 2025-12-02
"""

import numpy as np
from pathlib import Path
from typing import Tuple, List, Dict, Optional


# =============================================================================
# Single C60 Molecule (60 atoms)
# =============================================================================

def get_single_c60_coordinates() -> List[Tuple[float, float, float]]:
    """
    Returns single C60 fullerene coordinates (60 atoms)
    Centered at origin, molecular diameter ~7 Å
    """
    # Standard C60 molecular coordinates (Angstrom) from ASE
    return [
        (2.21019530, 0.58666310, 2.66695040),
        (3.10763930, 0.15770080, 1.63002860),
        (1.32844300, -0.31589390, 3.23632320),
        (3.09087090, -1.15850050, 1.20142400),
        (3.18792450, -1.45745990, -0.19970050),
        (3.22146230, 1.22309660, 0.67394400),
        (3.31612100, 0.93515860, -0.67651510),
        (3.29849810, -0.43011420, -1.12041380),
        (-0.44808420, 1.35914840, 3.20810200),
        (0.46720560, 2.29498300, 2.61752640),
        (-0.02565750, 0.07642190, 3.50862590),
        (1.77279170, 1.91765840, 2.35296910),
        (2.39546230, 2.30956890, 1.11895390),
        (-0.26101950, 3.08209350, 1.66231170),
        (0.34077260, 3.45923880, 0.47459680),
        (1.69511710, 3.06924460, 0.19766230),
        (-2.12583940, -0.84588530, 2.67009630),
        (-2.56209900, 0.48552020, 2.35317150),
        (-0.87815210, -1.04619850, 3.23673020),
        (-1.74150960, 1.56799630, 2.61973330),
        (-1.62624680, 2.63570300, 1.66418110),
        (-3.29848100, 0.43018710, 1.12042080),
        (-3.18794690, 1.45738950, 0.19960300),
        (-2.33602610, 2.58136270, 0.47609120),
        (-0.50052100, -2.97977710, 1.79403080),
        (-1.79443380, -2.77290870, 1.20478910),
        (-0.05142450, -2.13288410, 2.79388300),
        (-2.58914710, -1.72258280, 1.63297150),
        (-3.31607050, -0.93506360, 0.67652680),
        (-1.69519190, -3.06925810, -0.19765640),
        (-2.39549010, -2.30968530, -1.11898620),
        (-3.22141820, -1.22318350, -0.67395810),
        (2.17582340, -2.09462630, 1.79225290),
        (1.71186190, -2.97496810, 0.75571980),
        (1.31306560, -1.68294160, 2.79438920),
        (0.39590240, -3.40513950, 0.75576380),
        (-0.34082190, -3.45918830, -0.47456100),
        (2.33600570, -2.58144990, -0.47610500),
        (1.62637570, -2.63573490, -1.66423090),
        (0.26113520, -3.08212710, -1.66226180),
        (-2.21008440, -0.58686360, -2.66703000),
        (-1.77269700, -1.91789690, -2.35304660),
        (-0.46707230, -2.29505090, -2.61751050),
        (-1.32835000, 0.31576830, -3.23623750),
        (-2.17598820, 2.09453830, -1.79232940),
        (-3.09096630, 1.15834720, -1.20157490),
        (-3.10760900, -0.15784530, -1.63016270),
        (-1.31313650, 1.68282920, -2.79436390),
        (0.50032240, 2.97996370, -1.79402030),
        (-0.39611480, 3.40528170, -0.75572720),
        (-1.71206290, 2.97491220, -0.75579880),
        (0.05128240, 2.13294780, -2.79374500),
        (2.12586300, 0.84608090, -2.67005340),
        (2.58918530, 1.72277420, -1.63295620),
        (1.79430100, 2.77306840, -1.20482620),
        (0.87813230, 1.04635140, -3.23653130),
        (0.44824520, -1.35910610, -3.20805100),
        (1.74169480, -1.56795570, -2.61977140),
        (2.56217240, -0.48535290, -2.35320260),
        (0.02579040, -0.07635670, -3.50844460),
    ]


# =============================================================================
# 2x C60 Dimer (120 atoms) - For J coupling calculations
# =============================================================================

def get_c60_dimer_coordinates(separation: float = 10.0) -> Tuple[List[Tuple[float, float, float]], Dict]:
    """
    Returns 2x C60 dimer coordinates for electronic coupling (J) calculations.
    
    Args:
        separation: Distance between C60 centers in Angstrom (default 10.0 Å)
    
    Returns:
        Tuple of (coordinates, cell_info)
        - coordinates: List of (x, y, z) tuples for 120 atoms
        - cell_info: Dictionary with lattice parameters
    
    Note: 
        For qHP network, inter-C60 distance is ~10 Å in-plane
        Paper: J = 75 meV (pristine) → 135 meV (optimized)
    """
    single_c60 = np.array(get_single_c60_coordinates())
    
    # Center first C60
    c60_1 = single_c60.copy()
    
    # Second C60 displaced along x-axis
    c60_2 = single_c60.copy()
    c60_2[:, 0] += separation
    
    all_coords = np.vstack([c60_1, c60_2])
    
    # Cell parameters (with vacuum in z direction)
    cell_info = {
        'a': separation + 14.0,  # ~24 Å for separation=10
        'b': 15.0,
        'c': 25.0,  # Large vacuum in z for 2D system
        'n_atoms': 120,
        'n_c60': 2,
        'description': f'2x C60 dimer, separation={separation} Å'
    }
    
    # Shift coordinates to positive quadrant
    all_coords[:, 0] += 7.0  # Shift x
    all_coords[:, 1] += 7.5  # Shift y  
    all_coords[:, 2] += 12.5  # Shift z
    
    return [(x, y, z) for x, y, z in all_coords], cell_info


# =============================================================================
# 4x C60 Network (240 atoms) - For network properties
# =============================================================================

def get_c60_network_coordinates() -> Tuple[List[Tuple[float, float, float]], Dict]:
    """
    Returns 4x C60 network coordinates from validated structure.
    This is a 2x2 arrangement suitable for band structure calculations.
    
    Returns:
        Tuple of (coordinates, cell_info)
    
    Source: graphullerene/C60.xyz (validated qHP structure)
    """
    # Load from reference file if available
    ref_file = Path(__file__).parent.parent / "graphullerene" / "C60.xyz"
    
    if ref_file.exists():
        coords = _load_xyz_file(ref_file)
        n_atoms = len(coords)
    else:
        # Fallback: Generate 2x2 grid of C60 molecules
        coords, _ = _generate_2x2_c60_grid()
        n_atoms = len(coords)
    
    cell_info = {
        'a': 14.26,  # From C60.xyz structure
        'b': 14.26,
        'c': 14.26,
        'n_atoms': n_atoms,
        'n_c60': n_atoms // 60,
        'description': f'{n_atoms // 60}x C60 network (2x2 arrangement)'
    }
    
    return coords, cell_info


def get_qhp_network_cell() -> Tuple[List[Tuple[float, float, float]], Dict]:
    """
    Returns qHP C60 network unit cell with proper lattice parameters.
    
    Paper values:
        a = 36.67 Å
        b = 30.84 Å
        
    Returns coordinates for 2x C60 unit cell (120 atoms)
    """
    # Load from POSCAR.C60 reference (2x C60 unit cell)
    ref_file = Path(__file__).parent.parent / "graphullerene" / "POSCAR.C60"
    
    if ref_file.exists():
        coords, lattice = _load_poscar_file(ref_file)
    else:
        # Fallback to dimer with qHP parameters
        coords, _ = get_c60_dimer_coordinates(separation=9.128)  # POSCAR a-parameter
        lattice = {
            'a': 9.128,
            'b': 15.805,
            'c': 28.81,
        }
    
    cell_info = {
        'a': lattice['a'],
        'b': lattice['b'],
        'c': lattice['c'],
        'n_atoms': len(coords),
        'n_c60': len(coords) // 60,
        'description': 'qHP C60 unit cell (POSCAR reference)',
        'periodic': True
    }
    
    return coords, cell_info


# =============================================================================
# Doped Structure Generation
# =============================================================================

def create_substitutional_doped_structure(
    base_coords: List[Tuple[float, float, float]],
    dopant: str,
    concentration: float,
    seed: int = 42
) -> Tuple[List[Tuple[str, float, float, float]], Dict]:
    """
    Create substitutionally doped structure by replacing C atoms with dopant.
    
    Args:
        base_coords: Base carbon coordinates
        dopant: Dopant element ('B', 'N', 'P')
        concentration: Doping concentration (0.0 - 1.0)
        seed: Random seed for reproducibility
    
    Returns:
        Tuple of (atoms_with_symbols, doping_info)
        - atoms_with_symbols: List of (element, x, y, z)
        - doping_info: Dictionary with doping statistics
    """
    np.random.seed(seed)
    n_atoms = len(base_coords)
    n_dopants = int(round(n_atoms * concentration))
    
    # Select random atoms to replace
    dopant_indices = np.random.choice(n_atoms, n_dopants, replace=False)
    dopant_indices_set = set(dopant_indices)
    
    atoms = []
    for i, (x, y, z) in enumerate(base_coords):
        if i in dopant_indices_set:
            atoms.append((dopant, x, y, z))
        else:
            atoms.append(('C', x, y, z))
    
    doping_info = {
        'dopant': dopant,
        'concentration': concentration,
        'n_dopants': n_dopants,
        'n_carbon': n_atoms - n_dopants,
        'dopant_indices': list(dopant_indices),
        'actual_concentration': n_dopants / n_atoms
    }
    
    return atoms, doping_info


def create_mixed_doped_structure(
    base_coords: List[Tuple[float, float, float]],
    doping_config: Dict[str, float],
    seed: int = 42
) -> Tuple[List[Tuple[str, float, float, float]], Dict]:
    """
    Create mixed doped structure (e.g., B+N co-doping).
    
    Args:
        base_coords: Base carbon coordinates
        doping_config: Dict of {element: concentration}, e.g., {'B': 0.03, 'N': 0.02}
        seed: Random seed
    
    Returns:
        Tuple of (atoms_with_symbols, doping_info)
    """
    np.random.seed(seed)
    n_atoms = len(base_coords)
    
    # Calculate number of each dopant
    dopant_counts = {}
    total_dopants = 0
    for element, conc in doping_config.items():
        n = int(round(n_atoms * conc))
        dopant_counts[element] = n
        total_dopants += n
    
    # Select random positions (non-overlapping)
    all_dopant_indices = np.random.choice(n_atoms, total_dopants, replace=False)
    
    # Assign dopants to positions
    dopant_map = {}
    idx = 0
    for element, count in dopant_counts.items():
        for _ in range(count):
            dopant_map[all_dopant_indices[idx]] = element
            idx += 1
    
    atoms = []
    for i, (x, y, z) in enumerate(base_coords):
        if i in dopant_map:
            atoms.append((dopant_map[i], x, y, z))
        else:
            atoms.append(('C', x, y, z))
    
    doping_info = {
        'doping_config': doping_config,
        'dopant_counts': dopant_counts,
        'n_carbon': n_atoms - total_dopants,
        'total_concentration': total_dopants / n_atoms,
        'dopant_indices': dopant_map
    }
    
    return atoms, doping_info


# =============================================================================
# CP2K Input Formatting
# =============================================================================

def format_coords_for_cp2k(
    coords: List[Tuple],
    element: str = 'C',
    indent: str = '      '
) -> str:
    """
    Format coordinates for CP2K &COORD block.
    
    Args:
        coords: List of (x, y, z) or (element, x, y, z) tuples
        element: Default element (used if coords don't include element)
        indent: Indentation string
    
    Returns:
        Formatted string for CP2K input
    """
    lines = []
    for coord in coords:
        if len(coord) == 3:
            x, y, z = coord
            el = element
        else:
            el, x, y, z = coord
        lines.append(f"{indent}{el}  {x:.6f}  {y:.6f}  {z:.6f}")
    
    return "\n".join(lines)


def get_cell_block(cell_info: Dict, strain: float = 0.0) -> str:
    """
    Generate CP2K &CELL block with optional strain.
    
    Args:
        cell_info: Dictionary with 'a', 'b', 'c' lattice parameters
        strain: Strain percentage (e.g., 3.0 for 3% strain)
    
    Returns:
        Formatted &CELL block string
    """
    factor = 1.0 + strain / 100.0
    a = cell_info['a'] * factor
    b = cell_info['b'] * factor
    c = cell_info['c']  # No strain in z for 2D systems
    
    return f"""    &CELL
      A  {a:.6f}  0.000000  0.000000
      B  0.000000  {b:.6f}  0.000000
      C  0.000000  0.000000  {c:.6f}
      PERIODIC XYZ
    &END CELL"""


# =============================================================================
# Helper Functions
# =============================================================================

def _load_xyz_file(filepath: Path) -> List[Tuple[float, float, float]]:
    """Load coordinates from XYZ file."""
    coords = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
        # Skip header (first two lines)
        for line in lines[2:]:
            parts = line.split()
            if len(parts) >= 4 and parts[0] == 'C':
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                coords.append((x, y, z))
    return coords


def _load_poscar_file(filepath: Path) -> Tuple[List[Tuple[float, float, float]], Dict]:
    """Load coordinates from VASP POSCAR file."""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Parse lattice vectors
    scale = float(lines[1].strip())
    a_vec = [float(x) * scale for x in lines[2].split()]
    b_vec = [float(x) * scale for x in lines[3].split()]
    c_vec = [float(x) * scale for x in lines[4].split()]
    
    lattice = {
        'a': a_vec[0],
        'b': b_vec[1],
        'c': c_vec[2]
    }
    
    # Parse number of atoms
    n_atoms = int(lines[6].strip())
    
    # Parse coordinates (Direct format)
    coords = []
    for i in range(8, 8 + n_atoms):
        parts = lines[i].split()
        # Convert fractional to Cartesian
        fx, fy, fz = float(parts[0]), float(parts[1]), float(parts[2])
        x = fx * lattice['a']
        y = fy * lattice['b']
        z = fz * lattice['c']
        coords.append((x, y, z))
    
    return coords, lattice


def _generate_2x2_c60_grid() -> Tuple[List[Tuple[float, float, float]], Dict]:
    """Generate 2x2 grid of C60 molecules."""
    single_c60 = np.array(get_single_c60_coordinates())
    spacing = 10.0  # Å between C60 centers
    
    all_coords = []
    for ix in range(2):
        for iy in range(2):
            c60 = single_c60.copy()
            c60[:, 0] += ix * spacing
            c60[:, 1] += iy * spacing
            all_coords.extend([(x, y, z) for x, y, z in c60])
    
    return all_coords, {'spacing': spacing}


# =============================================================================
# Structure Validation
# =============================================================================

def validate_structure(coords: List, expected_atoms: int, name: str = "Structure") -> bool:
    """Validate structure has expected number of atoms."""
    actual = len(coords)
    if actual != expected_atoms:
        print(f"WARNING: {name} has {actual} atoms, expected {expected_atoms}")
        return False
    return True


# =============================================================================
# Multi-C60 System Generation (for synergy experiments)
# =============================================================================

def get_supercell_dimensions(n_molecules: int) -> Tuple[float, float, float]:
    """
    Get lattice dimensions for a supercell containing n C60 molecules.
    
    Args:
        n_molecules: Number of C60 molecules (1, 2, 3, 4, ...)
    
    Returns:
        Tuple of (a, b, c) lattice parameters in Angstrom
    """
    # Base dimensions for single C60
    base_a = 14.26  # Å (C60 diameter + spacing)
    base_b = 14.26
    base_c = 20.0   # Vacuum layer for 2D system
    
    # Arrange molecules in a grid
    if n_molecules <= 2:
        return (base_a * n_molecules, base_b, base_c)
    elif n_molecules <= 4:
        nx = 2
        ny = (n_molecules + 1) // 2
        return (base_a * nx, base_b * ny, base_c)
    else:
        nx = int(np.ceil(np.sqrt(n_molecules)))
        ny = (n_molecules + nx - 1) // nx
        return (base_a * nx, base_b * ny, base_c)


def get_multi_c60_coordinates(n_molecules: int) -> Tuple[List[Tuple[float, float, float]], Dict]:
    """
    Generate coordinates for multiple C60 molecules in a supercell.
    
    Args:
        n_molecules: Number of C60 molecules
    
    Returns:
        Tuple of (coordinates, cell_info)
    """
    single_c60 = np.array(get_single_c60_coordinates())
    spacing = 10.0  # Å between C60 centers
    
    # Determine grid arrangement
    if n_molecules <= 2:
        grid = [(i, 0) for i in range(n_molecules)]
    elif n_molecules <= 4:
        grid = [(i % 2, i // 2) for i in range(n_molecules)]
    else:
        nx = int(np.ceil(np.sqrt(n_molecules)))
        grid = [(i % nx, i // nx) for i in range(n_molecules)]
    
    all_coords = []
    for ix, iy in grid:
        c60 = single_c60.copy()
        c60[:, 0] += ix * spacing + 7.0  # Center in cell
        c60[:, 1] += iy * spacing + 7.0
        c60[:, 2] += 10.0  # Center in z
        all_coords.extend([(x, y, z) for x, y, z in c60])
    
    lattice_a, lattice_b, lattice_c = get_supercell_dimensions(n_molecules)
    
    cell_info = {
        'a': lattice_a,
        'b': lattice_b,
        'c': lattice_c,
        'n_atoms': len(all_coords),
        'n_c60': n_molecules,
        'description': f'{n_molecules}× C60 supercell'
    }
    
    return all_coords, cell_info


def format_multi_c60_coordinates_for_cp2k(n_molecules: int) -> str:
    """
    Generate multi-C60 coordinates formatted for CP2K input.
    
    Args:
        n_molecules: Number of C60 molecules
    
    Returns:
        Formatted string for CP2K &COORD block
    """
    coords, _ = get_multi_c60_coordinates(n_molecules)
    return format_coords_for_cp2k(coords)


# =============================================================================
# Main Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("qHP C60 Structure Module Test")
    print("=" * 60)
    
    # Test single C60
    single = get_single_c60_coordinates()
    print(f"\n1. Single C60: {len(single)} atoms")
    
    # Test dimer
    dimer, dimer_info = get_c60_dimer_coordinates()
    print(f"\n2. C60 Dimer: {len(dimer)} atoms")
    print(f"   Cell: a={dimer_info['a']:.2f}, b={dimer_info['b']:.2f}, c={dimer_info['c']:.2f} Å")
    
    # Test network
    network, network_info = get_c60_network_coordinates()
    print(f"\n3. C60 Network: {len(network)} atoms ({network_info['n_c60']} molecules)")
    
    # Test qHP cell
    qhp, qhp_info = get_qhp_network_cell()
    print(f"\n4. qHP Unit Cell: {len(qhp)} atoms")
    print(f"   Cell: a={qhp_info['a']:.3f}, b={qhp_info['b']:.3f}, c={qhp_info['c']:.3f} Å")
    
    # Test doped structure
    print("\n5. Doped Structures:")
    base = get_single_c60_coordinates()
    
    for dopant in ['B', 'N', 'P']:
        doped, info = create_substitutional_doped_structure(base, dopant, 0.05)
        n_dopants = info['n_dopants']
        print(f"   {dopant} 5%: {n_dopants} dopants / {len(doped)} atoms")
    
    # Test mixed doping
    mixed, mixed_info = create_mixed_doped_structure(base, {'B': 0.03, 'N': 0.02})
    print(f"\n6. Mixed B+N (3%B + 2%N):")
    print(f"   B: {mixed_info['dopant_counts']['B']}, N: {mixed_info['dopant_counts']['N']}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")

