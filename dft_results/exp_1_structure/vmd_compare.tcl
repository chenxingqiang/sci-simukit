# Experiment 1: Strain Effect on C60 Dimer Structure
# Compare structures at different strain levels: -5%, -2.5%, 0%, +2.5%, +5%
#
# Usage: vmd -e vmd_compare.tcl

set base_dir [file dirname [info script]]
set xyz_dir "$base_dir/xyz_structures"

# Define structures to compare
set structures {
    {C60_strain_-5.0_pristine.xyz  "Compress -5%"  0}
    {C60_strain_-2.5_pristine.xyz  "Compress -2.5%" 3}
    {C60_strain_+0.0_pristine.xyz  "Pristine 0%"   7}
    {C60_strain_+2.5_pristine.xyz  "Stretch +2.5%" 10}
    {C60_strain_+5.0_pristine.xyz  "Stretch +5%"   1}
}

puts "=============================================="
puts "Experiment 1: Strain Effect Comparison"
puts "=============================================="

# Load all structures with different colors
set x_offset 0
foreach struct $structures {
    set filename [lindex $struct 0]
    set label [lindex $struct 1]
    set color_id [lindex $struct 2]
    
    set filepath "$xyz_dir/$filename"
    if {[file exists $filepath]} {
        mol new $filepath type xyz waitfor all
        set mol_id [molinfo top]
        
        # Move structure to side
        set sel [atomselect $mol_id "all"]
        $sel moveby [list $x_offset 0 0]
        $sel delete
        
        # Setup representation
        mol delrep 0 $mol_id
        
        # Bonds with color
        mol representation DynamicBonds 1.8 0.12 12.0
        mol color ColorID $color_id
        mol selection {all}
        mol material AOEdgy
        mol addrep $mol_id
        
        # Atoms
        mol representation VDW 0.35 12.0
        mol color ColorID $color_id
        mol selection {all}
        mol material AOChalky
        mol addrep $mol_id
        
        mol rename $mol_id $label
        puts "  Loaded: $label"
        
        set x_offset [expr {$x_offset + 25}]
    }
}

# Display settings
color Display Background white
display shadows on
display ambientocclusion on
display projection Orthographic
axes location Off
display resetview

puts ""
puts "Strain comparison loaded."
puts "Left to Right: -5% -> -2.5% -> 0% -> +2.5% -> +5%"
puts ""
puts "Color Legend:"
puts "  Blue: Compression (-5%)"
puts "  Orange: Compression (-2.5%)"
puts "  Green: Pristine (0%)"
puts "  Cyan: Stretch (+2.5%)"
puts "  Red: Stretch (+5%)"

