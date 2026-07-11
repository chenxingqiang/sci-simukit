# CPK / space-filling periodic supercell snapshot (distinct from ball-and-stick snapshot.tcl).
# Usage: vmd -dispdev text -e render_structure_cpk.tcl -args STRUCT.xyz OUT.tga [dopant] [mode]
#   mode: cpk (default) | cages (per-C60 ColorID, n>=4)

proc apply_pub_style {} {
    color Element C gray
    color Element B magenta
    color Element N blue
    color Element P orange
    color Display Background white
    display shadows on
    display ambientocclusion on
    display aoambient 0.82
    display aodirect 0.32
    display depthcue off
    display projection Orthographic
    axes location Off
}

proc style_cpk {mol_id {dopant ""}} {
    mol delrep 0 $mol_id
    mol representation CPK 0.88 0.22 12.0 12.0
    mol color Element
    mol selection {name C}
    mol material AOChalky
    mol addrep $mol_id
    if {$dopant ne ""} {
        mol representation VDW 0.72 12.0
        mol color Element
        mol selection "name $dopant"
        mol material Glossy
        mol addrep $mol_id
    }
}

proc style_cages {mol_id {dopant ""}} {
    set atoms_per_cage 60
    set natoms [molinfo $mol_id get numatoms]
    set ncages [expr {int(floor(double($natoms) / $atoms_per_cage))}]
    if {$ncages < 1} { set ncages 1 }

    mol delrep 0 $mol_id
    set palette {2 3 4 5 6 7 8 9}
    for {set k 0} {$k < $ncages} {incr k} {
        set i0 [expr {$k * $atoms_per_cage}]
        set i1 [expr {$i0 + $atoms_per_cage - 1}]
        if {$i1 >= $natoms} { set i1 [expr {$natoms - 1}] }
        set cid [lindex $palette [expr {$k % [llength $palette]}]]
        mol representation VDW 0.50 12.0
        mol color ColorID $cid
        mol selection "index $i0 to $i1 and name C"
        mol material AOChalky
        mol addrep $mol_id
    }
    if {$dopant ne ""} {
        mol representation VDW 0.78 12.0
        mol color Element
        mol selection "name $dopant"
        mol material Glossy
        mol addrep $mol_id
    }
}

proc frame_on_atoms {mol_id {scale_target 38.0}} {
    set sel [atomselect $mol_id {name C}]
    set mm [measure minmax $sel]
    set span [veclength [vecsub [lindex $mm 1] [lindex $mm 0]]]
    $sel delete
    display resetview
    rotate x by 14
    rotate y by 30
    if {$span > 0.1} {
        scale by [expr {$scale_target / $span}]
    }
}

if {[llength $argv] < 2} {
    puts "Usage: vmd -e render_structure_cpk.tcl -args STRUCT.xyz OUT.tga \[dopant\] \[cpk\|cages\]"
    quit
}

set xyz [lindex $argv 0]
set out_tga [lindex $argv 1]
set dopant ""
set mode "cpk"
if {[llength $argv] >= 3} { set dopant [lindex $argv 2] }
if {[llength $argv] >= 4} { set mode [lindex $argv 3] }

mol delete all
mol new $xyz type xyz waitfor all
set mid [molinfo top]

if {$mode eq "cages"} {
    style_cages $mid $dopant
} else {
    style_cpk $mid $dopant
}

apply_pub_style
frame_on_atoms $mid
display resize 1200 1000
render TachyonInternal $out_tga
puts "Rendered CPK structure ($mode) $out_tga"
quit
