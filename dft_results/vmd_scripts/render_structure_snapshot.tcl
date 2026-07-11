# Single-structure publication snapshot (no MO cube).
# Usage: vmd -dispdev text -e render_structure_snapshot.tcl -args STRUCT.xyz OUT.tga

proc apply_pub_style {} {
    color Element C gray
    color Element B magenta
    color Element N blue
    color Element P orange
    color Display Background white
    display shadows on
    display ambientocclusion on
    display aoambient 0.8
    display aodirect 0.3
    display depthcue off
    display projection Orthographic
    axes location Off
}

proc style_mol {mol_id {dopant ""}} {
    mol delrep 0 $mol_id
    mol representation DynamicBonds 1.55 0.10 12.0
    mol color Element
    mol selection {all}
    mol material AOEdgy
    mol addrep $mol_id
    mol representation VDW 0.30 12.0
    mol color Element
    mol selection {name C}
    mol material AOChalky
    mol addrep $mol_id
    if {$dopant ne ""} {
        mol representation VDW 0.55 12.0
        mol color Element
        mol selection "name $dopant"
        mol material Glossy
        mol addrep $mol_id
    }
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

if {[llength $argv] < 2} {
    puts "Usage: vmd -e render_structure_snapshot.tcl -args STRUCT.xyz OUT.tga"
    quit
}

set xyz [lindex $argv 0]
set out_tga [lindex $argv 1]
set dopant ""
if {[llength $argv] >= 3} { set dopant [lindex $argv 2] }

mol delete all
mol new $xyz type xyz waitfor all
set mid [molinfo top]
style_mol $mid $dopant
apply_pub_style
frame_on_atoms $mid
display resize 1200 1000
render TachyonInternal $out_tga
puts "Rendered structure $out_tga"
quit
