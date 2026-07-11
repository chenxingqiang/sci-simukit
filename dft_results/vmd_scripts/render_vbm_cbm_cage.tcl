# Render HOMO/LUMO isosurface zoomed on one C60 cage (full-cell cube + cage XYZ).
# Usage: vmd -dispdev text -e render_vbm_cbm_cage.tcl -args CUBE.cube CAGE.xyz OUT.tga COLORID ?isovalue?

proc setup_display {} {
    color Display Background white
    display shadows on
    display ambientocclusion on
    display aoambient 0.75
    display aodirect 0.35
    display depthcue off
    display projection Orthographic
    axes location Off
    color Element C gray
}

proc frame_on_atoms {mol_id} {
    set sel [atomselect $mol_id all]
    set mm [measure minmax $sel]
    set span [veclength [vecsub [lindex $mm 1] [lindex $mm 0]]]
    $sel delete
    display resetview
    rotate x by 14
    rotate y by 30
    if {$span > 0.1} {
        scale by [expr {42.0 / $span}]
    }
}

if {[llength $argv] < 4} {
    puts "Usage: vmd -e render_vbm_cbm_cage.tcl -args CUBE CAGE.xyz OUT.tga COLORID ?isovalue?"
    quit
}

set cube_file [lindex $argv 0]
set cage_xyz  [lindex $argv 1]
set out_tga   [lindex $argv 2]
set band_color [lindex $argv 3]
set isovalue  0.015
if {[llength $argv] >= 5} { set isovalue [lindex $argv 4] }

mol delete all
mol new $cube_file type cube waitfor all
set cube_id [molinfo top]

mol new $cage_xyz type xyz waitfor all
set cage_id [molinfo top]

mol delrep 0 $cube_id
mol representation Isosurface $isovalue 0 0 0 1 1
mol color ColorID $band_color
mol selection {name C}
mol material Transparent
mol addrep $cube_id

mol delrep 0 $cage_id
mol representation DynamicBonds 1.5 0.12 12.0
mol color Element
mol selection {name C}
mol material AOChalky
mol addrep $cage_id

mol representation VDW 0.32 12.0
mol color Element
mol selection {name C}
mol material AOChalky
mol addrep $cage_id

setup_display
frame_on_atoms $cage_id
display resize 900 900
render TachyonInternal $out_tga
puts "Rendered cage tile $out_tga"
quit
