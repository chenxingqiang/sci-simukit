# VMD Interactive Visualization Script for C60 Graphullerene
# High-quality settings for interactive exploration
#
# Usage: In VMD console after loading structure:
#   source interactive_view.tcl

proc setup_c60_view {} {
    # Delete all existing representations
    set numreps [molinfo top get numreps]
    for {set i 0} {$i < $numreps} {incr i} {
        mol delrep 0 top
    }
    
    # Representation 1: Carbon backbone as licorice
    mol representation Licorice 0.15 12.0 12.0
    mol color Element
    mol selection {name C}
    mol material AOEdgy
    mol addrep top
    
    # Representation 2: All atoms as small spheres (VDW)
    mol representation VDW 0.5 12.0
    mol color Element
    mol selection {all}
    mol material AOChalky
    mol addrep top
    
    # Representation 3: Highlight dopants with larger spheres
    mol representation VDW 0.8 12.0
    mol color Name
    mol selection {name B N P Li Na K}
    mol material Glossy
    mol addrep top
    
    # Set custom colors
    color Element C silver
    color Element B magenta
    color Element N blue
    color Element P orange
    color Element Li green
    color Element Na yellow
    color Element K purple
    
    # Display settings
    color Display Background white
    display shadows on
    display ambientocclusion on
    display aoambient 0.75
    display aodirect 0.35
    display depthcue off
    display projection Orthographic
    axes location Off
    
    # Reset and orient view
    display resetview
    
    puts "C60 visualization setup complete!"
    puts "Use mouse to rotate, zoom, and explore."
}

proc highlight_c60_cage {cage_num} {
    # Highlight a specific C60 cage (for dimer/tetramer systems)
    # cage_num: 1, 2, 3, or 4
    
    set atoms_per_cage 60
    set start_idx [expr {($cage_num - 1) * $atoms_per_cage}]
    set end_idx [expr {$cage_num * $atoms_per_cage - 1}]
    
    mol representation VDW 0.6 12.0
    mol color ColorID [expr {$cage_num + 1}]
    mol selection "index $start_idx to $end_idx"
    mol material Transparent
    mol addrep top
    
    puts "Highlighted C60 cage $cage_num (atoms $start_idx-$end_idx)"
}

proc show_bonds_only {} {
    # Show only bonds (wireframe style)
    set numreps [molinfo top get numreps]
    for {set i 0} {$i < $numreps} {incr i} {
        mol delrep 0 top
    }
    
    mol representation DynamicBonds 1.8 0.1 12.0
    mol color Element
    mol selection {all}
    mol material AOEdgy
    mol addrep top
    
    color Element C gray
    puts "Showing bonds only"
}

proc show_spacefilling {} {
    # Space-filling representation
    set numreps [molinfo top get numreps]
    for {set i 0} {$i < $numreps} {incr i} {
        mol delrep 0 top
    }
    
    mol representation VDW 1.0 12.0
    mol color Element
    mol selection {all}
    mol material AOChalky
    mol addrep top
    
    puts "Showing space-filling view"
}

proc render_image {filename} {
    # Render high-quality image
    render TachyonInternal $filename
    puts "Image saved to: $filename"
}

# Auto-run setup when sourced
setup_c60_view

puts ""
puts "Available commands:"
puts "  setup_c60_view      - Reset to default view"
puts "  highlight_c60_cage N - Highlight cage N (1-4)"
puts "  show_bonds_only     - Wireframe view"
puts "  show_spacefilling   - Space-filling view"  
puts "  render_image file   - Save image to file"

