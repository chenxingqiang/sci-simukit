# Render publication structure panels for graphullerene manuscript.
# Usage: vmd -dispdev text -e render_scheme_panels.tcl -args OUT_DIR XYZ_DIR

set out_dir [lindex $argv 0]
set xyz_dir [lindex $argv 1]

if {$out_dir eq "" || $xyz_dir eq ""} {
    puts "Usage: vmd -dispdev text -e render_scheme_panels.tcl -args OUT_DIR XYZ_DIR"
    exit 1
}

file mkdir $out_dir

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

proc style_mol {mol_id} {
    mol delrep 0 $mol_id
    mol representation DynamicBonds 1.6 0.10 12.0
    mol color Element
    mol selection {all}
    mol material AOEdgy
    mol addrep $mol_id
    mol representation VDW 0.28 12.0
    mol color Element
    mol selection {name C}
    mol material AOChalky
    mol addrep $mol_id
    mol representation VDW 0.55 12.0
    mol color Element
    mol selection {name B or name N or name P}
    mol material Glossy
    mol addrep $mol_id
}

proc load_shifted {xyz label dx dy dz} {
    if {![file exists $xyz]} {
        puts "Missing: $xyz"
        return -1
    }
    mol new $xyz type xyz waitfor all
    set mid [molinfo top]
    set sel [atomselect $mid all]
    $sel moveby [list $dx $dy $dz]
    $sel delete
    style_mol $mid
    mol rename $mid $label
    return $mid
}

proc render_tachyon {out_tga width height} {
    display resize $width $height
    render TachyonInternal $out_tga
}

apply_pub_style

set panels {
    {C60_strain_+0.0_pristine_synergy.xyz "Pristine" 0}
    {C60_strain_+0.0_B_doped_synergy.xyz "B-doped" 38}
    {C60_strain_+0.0_N_doped_synergy.xyz "N-doped" 76}
    {C60_strain_+0.0_P_doped_synergy.xyz "P-doped" 114}
}

set mids {}
foreach p $panels {
    set fname [lindex $p 0]
    set label [lindex $p 1]
    set dx [lindex $p 2]
    set xyz [file join $xyz_dir $fname]
    set mid [load_shifted $xyz $label $dx 0 0]
    if {$mid >= 0} { lappend mids $mid }
}

if {[llength $mids] == 0} {
    puts "No structures loaded; check XYZ_DIR"
    exit 1
}

mol top [lindex $mids 0]
display resetview
rotate x by 12
rotate y by 22
scale by 0.85

set out_tga [file join $out_dir scheme_tetramer_doping.tga]
render_tachyon $out_tga 2800 800
puts "Wrote $out_tga"

foreach p $panels {
    set fname [lindex $p 0]
    set xyz [file join $xyz_dir $fname]
    if {![file exists $xyz]} { continue }
    mol new $xyz type xyz waitfor all
    set mid [molinfo top]
    style_mol $mid
    display resetview
    rotate x by 12
    rotate y by 22
    set stem [file rootname $fname]
    set out_one [file join $out_dir "${stem}.tga"]
    render_tachyon $out_one 1200 1200
    puts "Wrote $out_one"
    mol delete $mid
}

quit
