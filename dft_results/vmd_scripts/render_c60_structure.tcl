# VMD Visualization Script for C60 Graphullerene Structures
# Best rendering settings for publication-quality images
# 
# Usage: vmd -e render_c60_structure.tcl -args structure.xyz output.tga

# Parse command line arguments
set xyz_file [lindex $argv 0]
set output_file [lindex $argv 1]

if {$xyz_file eq ""} {
    puts "Usage: vmd -e render_c60_structure.tcl -args structure.xyz output.tga"
    exit
}

# Load molecule
mol new $xyz_file type xyz waitfor all

# Delete default representation
mol delrep 0 top

# Representation 1: Carbon atoms as CPK spheres (smaller for clarity)
mol representation CPK 0.8 0.3 12.0 12.0
mol color Element
mol selection {name C}
mol material AOChalky
mol addrep top

# Representation 2: Bonds as thicker lines
mol representation DynamicBonds 1.8 0.15 12.0
mol color Element
mol selection {all}
mol material AOChalky
mol addrep top

# Representation 3: Highlight dopant atoms (if any) - B, N, P
mol representation VDW 1.0 12.0
mol color Name
mol selection {name B N P}
mol material Glossy
mol addrep top

# Set element colors (standard CPK scheme with enhancements)
color Element C gray
color Element B pink
color Element N blue
color Element P orange

# Background and lighting
color Display Background white
display shadows on
display ambientocclusion on
display aoambient 0.8
display aodirect 0.3
display depthcue off

# Camera settings
display projection Orthographic
display nearclip set 0.01
display farclip set 10000

# Reset view
display resetview
rotate x by 15
rotate y by 25

# Rendering settings
display rendermode GLSL
axes location Off

# If output file specified, render to Targa format
if {$output_file ne ""} {
    render TachyonInternal $output_file
    puts "Rendered to: $output_file"
}

puts "C60 structure loaded and visualized successfully."
puts "Atoms: [molinfo top get numatoms]"

