# Render VBM (HOMO) and CBM (LUMO) isosurfaces — Figure S4 style
# Usage: vmd -dispdev text -e render_vbm_cbm.tcl -args HOMO.cube LUMO.cube OUT_VBM.tga OUT_CBM.tga ?isovalue?

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
    set sel [atomselect $mol_id {name C}]
    set mm [measure minmax $sel]
    set span [veclength [vecsub [lindex $mm 1] [lindex $mm 0]]]
    $sel delete
    display resetview
    rotate x by 14
    rotate y by 30
    if {$span > 0.1} {
        scale by [expr {38.0 / $span}]
    }
}

proc render_band_edge {cube_file out_tga isovalue band_color} {
    mol delete all
    mol new $cube_file type cube waitfor all
    set mid [molinfo top]

    mol delrep 0 $mid

    mol representation DynamicBonds 1.5 0.12 12.0
    mol color Element
    mol selection {name C}
    mol material AOChalky
    mol addrep $mid

    mol representation VDW 0.32 12.0
    mol color Element
    mol selection {name C}
    mol material AOChalky
    mol addrep $mid

    mol addfile $cube_file type cube waitfor all
    mol representation Isosurface $isovalue 0 0 0 1 1
    mol color ColorID $band_color
    mol selection {name C}
    mol material Transparent
    mol addrep $mid

    setup_display
    frame_on_atoms $mid

    display resize 1200 1000
    render TachyonInternal $out_tga
    puts "Rendered $out_tga (isovalue=$isovalue)"
}

if {[llength $argv] < 4} {
    puts "Usage: vmd -e render_vbm_cbm.tcl -args HOMO.cube LUMO.cube OUT_VBM.tga OUT_CBM.tga ?isovalue?"
    quit
}

set homo_cube [lindex $argv 0]
set lumo_cube [lindex $argv 1]
set out_vbm   [lindex $argv 2]
set out_cbm   [lindex $argv 3]
set isovalue  0.015
if {[llength $argv] >= 5} { set isovalue [lindex $argv 4] }

render_band_edge $homo_cube $out_vbm $isovalue 11
render_band_edge $lumo_cube $out_cbm $isovalue 10
quit
