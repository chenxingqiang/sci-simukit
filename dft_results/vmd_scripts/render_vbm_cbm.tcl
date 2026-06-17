# Render VBM (HOMO) and CBM (LUMO) isosurfaces — Figure S4 style
# Usage:
#   VMDDIR=/Applications/VMD.app/Contents/vmd2/lib \
#     $VMDDIR/vmd_MACOSXARM64 -dispdev text -e render_vbm_cbm.tcl \
#     -args HOMO.cube LUMO.cube OUT_VBM.png OUT_CBM.png

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

proc render_band_edge {cube_file out_png isovalue band_color} {
    mol delete all
    mol new $cube_file type cube waitfor all
    set mid [molinfo top]

    mol delrep 0 $mid

    mol representation DynamicBonds 1.6 0.12 12.0
    mol color Element
    mol selection {name C}
    mol material AOChalky
    mol addrep $mid

    mol representation VDW 0.25 12.0
    mol color Element
    mol selection {name C}
    mol material AOChalky
    mol addrep $mid

    mol addfile $cube_file type cube waitfor all
    mol representation Isosurface $isovalue 0 0 0 1 1
    mol color ColorID $band_color
    mol selection {all}
    mol material Transparent
    mol addrep $mid

    setup_display
    display resetview
    rotate x by 12
    rotate y by 28
    scale by 0.92

    display resize 1200 900
    render TachyonInternal $out_png
    puts "Rendered $out_png (isovalue=$isovalue)"
}

if {[llength $argv] < 4} {
    puts "Usage: vmd -e render_vbm_cbm.tcl -args HOMO.cube LUMO.cube OUT_VBM.png OUT_CBM.png ?isovalue?"
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
