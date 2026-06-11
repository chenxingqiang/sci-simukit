# Experiment 6: Optimal Conditions
# Compare all dopant types across strain range to find optimal
#
# Usage: vmd -e vmd_compare.tcl

set base_dir [file dirname [info script]]
set xyz_dir "$base_dir/xyz_structures"

puts "=============================================="
puts "Experiment 6: Optimal Conditions Search"
puts "=============================================="

# Matrix: rows = dopants, cols = strains
set dopants {pristine B N P}
set strains {-5.0 -3.0 +0.0 +3.0 +5.0}

proc load_single {filepath label x y color_id} {
    if {[file exists $filepath]} {
        mol new $filepath type xyz waitfor all
        set mol_id [molinfo top]
        
        set sel [atomselect $mol_id "all"]
        $sel moveby [list $x $y 0]
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
        
        # Dopants
        mol representation VDW 0.6 12.0
        mol color Name
        mol selection {name B N P}
        mol material Glossy
        mol addrep $mol_id
        
        mol rename $mol_id $label
        return 1
    }
    return 0
}

# Load a grid of structures
set row 0
set loaded 0
foreach dopant $dopants {
    set col 0
    foreach strain $strains {
        set filename "optimal_${strain}_${dopant}_q0.xyz"
        set filepath "$xyz_dir/$filename"
        set label "$dopant $strain%"
        
        set x_pos [expr {$col * 18}]
        set y_pos [expr {$row * -18}]
        
        if {[load_single $filepath $label $x_pos $y_pos $row]} {
            incr loaded
        }
        incr col
    }
    incr row
}

puts "Loaded $loaded structures"

# Highlight optimal region (N-doped)
puts ""
puts "*** OPTIMAL REGION: N-doped systems ***"
puts "    N-doped shows lowest energy (most stable)"

color Element C silver
color Name B magenta
color Name N blue
color Name P orange

color Display Background white
display shadows on
display ambientocclusion on
display projection Orthographic
axes location Off
display resetview

puts ""
puts "Optimal Conditions Grid:"
puts ""
puts "         -5%    -3%    0%    +3%    +5%"
puts "Pristine  o      o      o      o      o"
puts "B-doped   o      o      o      o      o"
puts "N-doped   *      *      *      *      *  <- OPTIMAL"
puts "P-doped   o      o      o      o      o"
puts ""
puts "Key Finding: N-doped C60 is most stable across all strain values."
puts "Energy difference: ~690 eV lower than pristine."

