# Experiment 2: Doping Effect Comparison
# Compare pristine vs B/N/P doped C60 at different concentrations
#
# Usage: vmd -e vmd_compare.tcl

set base_dir [file dirname [info script]]
set xyz_dir "$base_dir/xyz_structures"

# Define structures: pristine and doped at 3% concentration
set structures {
    {C60_pristine_0.03.xyz      "Pristine"     7}
    {C60_B_0.03_doped.xyz       "B-doped"      1}
    {C60_N_0.03_doped.xyz       "N-doped"      0}
    {C60_P_0.03_doped.xyz       "P-doped"      3}
}

puts "=============================================="
puts "Experiment 2: Doping Effect Comparison"
puts "=============================================="

set x_offset 0
foreach struct $structures {
    set filename [lindex $struct 0]
    set label [lindex $struct 1]
    set color_id [lindex $struct 2]
    
    set filepath "$xyz_dir/$filename"
    if {[file exists $filepath]} {
        mol new $filepath type xyz waitfor all
        set mol_id [molinfo top]
        
        # Move structure
        set sel [atomselect $mol_id "all"]
        $sel moveby [list $x_offset 0 0]
        $sel delete
        
        mol delrep 0 $mol_id
        
        # Carbon backbone
        mol representation Licorice 0.12 12.0 12.0
        mol color Element
        mol selection {name C}
        mol material AOEdgy
        mol addrep $mol_id
        
        # Carbon atoms
        mol representation VDW 0.35 12.0
        mol color Element
        mol selection {name C}
        mol material AOChalky
        mol addrep $mol_id
        
        # Highlight dopant atoms (larger)
        mol representation VDW 0.7 12.0
        mol color Name
        mol selection {name B N P}
        mol material Glossy
        mol addrep $mol_id
        
        mol rename $mol_id $label
        puts "  Loaded: $label"
        
        set x_offset [expr {$x_offset + 15}]
    }
}

# Set element colors
color Element C silver
color Name B magenta
color Name N blue
color Name P orange

# Display settings
color Display Background white
display shadows on
display ambientocclusion on
display projection Orthographic
axes location Off
display resetview

puts ""
puts "Doping comparison loaded."
puts "Left to Right: Pristine -> B-doped -> N-doped -> P-doped"
puts ""
puts "Dopant atoms highlighted with larger spheres:"
puts "  B: Magenta"
puts "  N: Blue"
puts "  P: Orange"

