# VMD Orbital Visualization Script
# For visualizing molecular orbitals from cube files
#
# Usage: vmd -e view_orbital.tcl -args structure.xyz orbital.cube

proc load_orbital {xyz_file cube_file {isovalue 0.02}} {
    # Load structure
    mol new $xyz_file type xyz waitfor all
    set mol_id [molinfo top]
    
    # Setup structure representation
    mol delrep 0 $mol_id
    
    # Bonds
    mol representation DynamicBonds 1.8 0.1 12.0
    mol color Element
    mol selection {all}
    mol material AOEdgy
    mol addrep $mol_id
    
    # Small atoms
    mol representation VDW 0.3 12.0
    mol color Element
    mol selection {all}
    mol material AOChalky
    mol addrep $mol_id
    
    # Load orbital cube file
    mol addfile $cube_file type cube waitfor all
    
    # Positive lobe (blue)
    mol representation Isosurface $isovalue 0 0 0 1 1
    mol color ColorID 0
    mol selection {all}
    mol material Transparent
    mol addrep $mol_id
    
    # Negative lobe (red)
    mol representation Isosurface [expr {-$isovalue}] 0 0 0 1 1
    mol color ColorID 1
    mol selection {all}
    mol material Transparent
    mol addrep $mol_id
    
    # Display settings
    color Display Background white
    display shadows on
    display ambientocclusion on
    axes location Off
    
    puts "Loaded orbital with isovalue: +/- $isovalue"
}

proc set_isovalue {value} {
    # Update isosurface value for all orbital representations
    set mol_id [molinfo top]
    set numreps [molinfo $mol_id get numreps]
    
    # Find and update isosurface reps (typically the last two)
    for {set i 2} {$i < $numreps} {incr i} {
        set rep_info [molinfo $mol_id get "{rep $i}"]
        if {[string match "*Isosurface*" $rep_info]} {
            # Get current sign from rep index
            if {$i == 2} {
                mol modstyle $i $mol_id Isosurface $value 0 0 0 1 1
            } else {
                mol modstyle $i $mol_id Isosurface [expr {-$value}] 0 0 0 1 1
            }
        }
    }
    puts "Isovalue set to: +/- $value"
}

proc orbital_colors {pos_color neg_color} {
    # Set custom colors for orbital lobes
    # Colors: 0=blue, 1=red, 3=orange, 4=yellow, 7=green, 10=cyan, 11=purple
    set mol_id [molinfo top]
    set numreps [molinfo $mol_id get numreps]
    
    for {set i 2} {$i < $numreps} {incr i} {
        if {$i == 2} {
            mol modcolor $i $mol_id ColorID $pos_color
        } elseif {$i == 3} {
            mol modcolor $i $mol_id ColorID $neg_color
        }
    }
    puts "Orbital colors updated"
}

proc render_orbital {filename} {
    # Render high-quality orbital image
    display resize 1920 1080
    render TachyonInternal $filename
    puts "Orbital image saved to: $filename"
}

# Parse command line if run directly
if {[llength $argv] >= 2} {
    set xyz_file [lindex $argv 0]
    set cube_file [lindex $argv 1]
    load_orbital $xyz_file $cube_file
}

puts ""
puts "Orbital Visualization Commands:"
puts "  load_orbital xyz cube ?isovalue? - Load structure and orbital"
puts "  set_isovalue value               - Adjust isovalue"
puts "  orbital_colors pos neg           - Set lobe colors (0=blue,1=red...)"
puts "  render_orbital filename          - Save image"

