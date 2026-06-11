# Experiment 4: Polaron Transition - 0% vs +3% Strain
# Compare charge localization before/after strain application
#
# Usage: vmd -e vmd_compare.tcl

set base_dir [file dirname [info script]]
set xyz_dir "$base_dir/xyz_structures"

puts "=============================================="
puts "Experiment 4: Polaron Transition (0% -> +3%)"
puts "=============================================="

# Before (0% strain) and After (+3% strain) for each dopant
set comparisons {
    {{polaron_+0.0_pristine_q0.xyz "Before: Pristine 0%"} {polaron_+3.0_pristine_q0.xyz "After: Pristine +3%"}}
    {{polaron_+0.0_B_q0.xyz "Before: B-doped 0%"} {polaron_+3.0_B_q0.xyz "After: B-doped +3%"}}
    {{polaron_+0.0_N_q0.xyz "Before: N-doped 0%"} {polaron_+3.0_N_q0.xyz "After: N-doped +3%"}}
    {{polaron_+0.0_P_q0.xyz "Before: P-doped 0%"} {polaron_+3.0_P_q0.xyz "After: P-doped +3%"}}
}

set dopant_colors {7 1 0 3}

proc load_mol {filepath label color x y} {
    if {[file exists $filepath]} {
        mol new $filepath type xyz waitfor all
        set mol_id [molinfo top]
        
        set sel [atomselect $mol_id "all"]
        $sel moveby [list $x $y 0]
        $sel delete
        
        mol delrep 0 $mol_id
        
        # Bonds
        mol representation DynamicBonds 1.8 0.1 12.0
        mol color ColorID $color
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
        puts "  $label"
        return 1
    }
    return 0
}

set row 0
foreach pair $comparisons {
    set color [lindex $dopant_colors $row]
    set y_pos [expr {$row * -35}]
    
    set before [lindex $pair 0]
    set after [lindex $pair 1]
    
    # Before (left)
    load_mol "$xyz_dir/[lindex $before 0]" [lindex $before 1] $color 0 $y_pos
    
    # After (right)
    load_mol "$xyz_dir/[lindex $after 0]" [lindex $after 1] $color 30 $y_pos
    
    # Arrow indicator
    puts "  --> Strain Applied -->"
    
    incr row
}

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
puts "Polaron Transition Comparison:"
puts "Each row: Before (0%) | After (+3%) strain"
puts ""
puts "Row 1: Pristine"
puts "Row 2: B-doped (highest strain sensitivity)"
puts "Row 3: N-doped"
puts "Row 4: P-doped"
puts ""
puts "Key observation: B-doped shows largest structural/electronic change"

