# Experiment 3: Strain-Doping Coupling Effect
# Compare C60 dimer at 0% vs +3% strain for each dopant type
#
# Usage: vmd -e vmd_compare.tcl

set base_dir [file dirname [info script]]
set xyz_dir "$base_dir/xyz_structures"

puts "=============================================="
puts "Experiment 3: Strain-Doping Coupling"
puts "=============================================="

# Row 1: 0% strain - pristine, B, N, P
# Row 2: +3% strain - pristine, B, N, P

set row1 {
    {C60_strain_+0.0_pristine.xyz  "0% Pristine"  7}
    {C60_strain_+0.0_B_doped.xyz   "0% B-doped"   1}
    {C60_strain_+0.0_N_doped.xyz   "0% N-doped"   0}
    {C60_strain_+0.0_P_doped.xyz   "0% P-doped"   3}
}

set row2 {
    {C60_strain_+3.0_pristine.xyz  "+3% Pristine" 7}
    {C60_strain_+3.0_B_doped.xyz   "+3% B-doped"  1}
    {C60_strain_+3.0_N_doped.xyz   "+3% N-doped"  0}
    {C60_strain_+3.0_P_doped.xyz   "+3% P-doped"  3}
}

proc load_structure {filepath label color_id x_off y_off} {
    global xyz_dir
    set fullpath "$xyz_dir/$filepath"
    
    if {[file exists $fullpath]} {
        mol new $fullpath type xyz waitfor all
        set mol_id [molinfo top]
        
        set sel [atomselect $mol_id "all"]
        $sel moveby [list $x_off $y_off 0]
        $sel delete
        
        mol delrep 0 $mol_id
        
        # Bonds
        mol representation DynamicBonds 1.8 0.1 12.0
        mol color Element
        mol selection {all}
        mol material AOEdgy
        mol addrep $mol_id
        
        # Atoms
        mol representation VDW 0.3 12.0
        mol color Element
        mol selection {name C}
        mol material AOChalky
        mol addrep $mol_id
        
        # Dopants highlighted
        mol representation VDW 0.65 12.0
        mol color Name
        mol selection {name B N P}
        mol material Glossy
        mol addrep $mol_id
        
        mol rename $mol_id $label
        puts "  Loaded: $label"
        return 1
    }
    return 0
}

# Load Row 1 (0% strain) - top row
set x_offset 0
foreach struct $row1 {
    load_structure [lindex $struct 0] [lindex $struct 1] [lindex $struct 2] $x_offset 20
    set x_offset [expr {$x_offset + 28}]
}

# Load Row 2 (+3% strain) - bottom row  
set x_offset 0
foreach struct $row2 {
    load_structure [lindex $struct 0] [lindex $struct 1] [lindex $struct 2] $x_offset -20
    set x_offset [expr {$x_offset + 28}]
}

# Colors
color Element C silver
color Name B magenta
color Name N blue  
color Name P orange

# Display
color Display Background white
display shadows on
display ambientocclusion on
display projection Orthographic
axes location Off
display resetview
rotate x by 90

puts ""
puts "Strain-Doping coupling comparison:"
puts ""
puts "Top Row (0% strain):    Pristine | B-doped | N-doped | P-doped"
puts "Bottom Row (+3% strain): Pristine | B-doped | N-doped | P-doped"
puts ""
puts "Compare vertical pairs to see strain effect on each dopant type."

