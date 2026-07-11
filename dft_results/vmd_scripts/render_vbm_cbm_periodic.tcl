# MO isosurface on periodic supercell: cube grid + full-cell XYZ (physical coordinates).
# Usage: vmd -e render_vbm_cbm_periodic.tcl -args CUBE FULL.xyz OUT.tga COLORID ?isovalue?

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

proc frame_on_supercell {mol_id {scale_target 38.0}} {
    set sel [atomselect $mol_id {name C}]
    set mm [measure minmax $sel]
    set dx [expr {[lindex $mm 1 0] - [lindex $mm 0 0]}]
    set dy [expr {[lindex $mm 1 1] - [lindex $mm 0 1]}]
    set dz [expr {[lindex $mm 1 2] - [lindex $mm 0 2]}]
    set span [expr {max($dx, max($dy, $dz))}]
    set min_xy [expr {min($dx, $dy)}]
    display resetview $sel
    set rot_x 0
    set rot_y 0
    if {[info exists ::env(VMD_VIEW_ROT_X)] && $::env(VMD_VIEW_ROT_X) ne ""} {
        set rot_x $::env(VMD_VIEW_ROT_X)
        set rot_y $::env(VMD_VIEW_ROT_Y)
    } elseif {$min_xy > 0.1 && $dz < 0.45 * $min_xy} {
        set rot_x 0
        set rot_y 0
    } else {
        set rot_x 14
        set rot_y 30
    }
    if {$rot_x != 0} { rotate x by $rot_x }
    if {$rot_y != 0} { rotate y by $rot_y }
    $sel delete
    if {$span > 0.1} {
        scale by [expr {$scale_target / $span}]
    }
}

if {[llength $argv] < 4} {
    puts "Usage: vmd -e render_vbm_cbm_periodic.tcl -args CUBE FULL.xyz OUT.tga COLORID ?isovalue?"
    quit
}

set cube_file [lindex $argv 0]
set xyz_file  [lindex $argv 1]
set out_tga   [lindex $argv 2]
set band_color [lindex $argv 3]
set isovalue  0.015
if {[llength $argv] >= 5} { set isovalue [lindex $argv 4] }

mol delete all
mol new $cube_file type cube waitfor all
set cube_id [molinfo top]

mol new $xyz_file type xyz waitfor all
set xyz_id [molinfo top]

mol delrep 0 $cube_id
mol representation Isosurface $isovalue 0 0 0 1 1
mol color ColorID $band_color
mol selection {name C}
mol material Transparent
mol addrep $cube_id

mol delrep 0 $xyz_id
mol representation DynamicBonds 1.55 0.10 12.0
mol color Element
mol selection {name C}
mol material AOChalky
mol addrep $xyz_id

mol representation VDW 0.30 12.0
mol color Element
mol selection {name C}
mol material AOChalky
mol addrep $xyz_id

setup_display
frame_on_supercell $xyz_id
display resize 1200 1000
render TachyonInternal $out_tga
puts "Rendered periodic supercell $out_tga"
quit
