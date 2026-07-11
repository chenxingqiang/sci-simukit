# Molecular surface snapshot (QuickSurf / MSMS / Surf). Parallel to render_structure_cpk.tcl.
# Usage: vmd -dispdev text -e render_structure_surface.tcl -args STRUCT.xyz OUT.tga [dopant] [mode]
#   mode: quicksurf | quicksurf_cages | msms | msms_cages | surf | surf_cages
# Env: VMD_MSMS_PROBE (default 1.3, clamped 1.2--1.4); MSMSSERVER for MSMS binary.

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

proc msms_probe {} {
    set p 1.3
    if {[info exists ::env(VMD_MSMS_PROBE)] && $::env(VMD_MSMS_PROBE) ne ""} {
        set p $::env(VMD_MSMS_PROBE)
    }
    if {$p < 1.2} { set p 1.2 }
    if {$p > 1.4} { set p 1.4 }
    return $p
}

proc style_surf_core {mol_id sel color_mode color_val {material AOChalky} {probe 1.3}} {
    mol representation Surf $probe 2.5
    if {$color_mode eq "element"} {
        mol color Element
    } else {
        mol color ColorID $color_val
    }
    mol selection $sel
    mol material $material
    mol addrep $mol_id
}

proc style_msms_core {mol_id sel color_mode color_val {material AOChalky}} {
    set probe [msms_probe]
    mol representation MSMS $probe 2.0
    if {$color_mode eq "element"} {
        mol color Element
    } else {
        mol color ColorID $color_val
    }
    mol selection $sel
    mol material $material
    mol addrep $mol_id
}

proc style_quicksurf {mol_id {dopant ""}} {
    mol delrep 0 $mol_id
    mol representation QuickSurf 2.0
    mol color Element
    mol selection {name C}
    mol material AOChalky
    mol addrep $mol_id
    if {$dopant ne ""} {
        mol representation VDW 0.85 16.0
        mol color Element
        mol selection "name $dopant"
        mol material Glossy
        mol addrep $mol_id
    }
}

proc style_quicksurf_cages {mol_id {dopant ""}} {
    set atoms_per_cage 60
    set natoms [molinfo $mol_id get numatoms]
    set ncages [expr {int(floor(double($natoms) / $atoms_per_cage))}]
    if {$ncages < 1} { set ncages 1 }

    mol delrep 0 $mol_id
    for {set k 0} {$k < $ncages} {incr k} {
        set i0 [expr {$k * $atoms_per_cage}]
        set i1 [expr {$i0 + $atoms_per_cage - 1}]
        if {$i1 >= $natoms} { set i1 [expr {$natoms - 1}] }
        mol representation QuickSurf 2.0
        mol color Element
        mol selection "index $i0 to $i1 and name C"
        mol material AOChalky
        mol addrep $mol_id
    }
    if {$dopant ne ""} {
        mol representation VDW 0.90 16.0
        mol color Element
        mol selection "name $dopant"
        mol material Glossy
        mol addrep $mol_id
    }
}

proc style_surf {mol_id {dopant ""}} {
    set probe [msms_probe]
    mol delrep 0 $mol_id
    style_surf_core $mol_id {name C} element "" AOChalky $probe
    if {$dopant ne ""} {
        mol representation VDW 0.85 16.0
        mol color Element
        mol selection "name $dopant"
        mol material Glossy
        mol addrep $mol_id
    }
}

proc style_surf_cages {mol_id {dopant ""}} {
    set atoms_per_cage 60
    set natoms [molinfo $mol_id get numatoms]
    set ncages [expr {int(floor(double($natoms) / $atoms_per_cage))}]
    if {$ncages < 1} { set ncages 1 }

    set probe [msms_probe]
    mol delrep 0 $mol_id
    for {set k 0} {$k < $ncages} {incr k} {
        set i0 [expr {$k * $atoms_per_cage}]
        set i1 [expr {$i0 + $atoms_per_cage - 1}]
        if {$i1 >= $natoms} { set i1 [expr {$natoms - 1}] }
        set sel "index $i0 to $i1 and name C"
        style_surf_core $mol_id $sel element "" AOChalky $probe
    }
    if {$dopant ne ""} {
        mol representation VDW 0.90 16.0
        mol color Element
        mol selection "name $dopant"
        mol material Glossy
        mol addrep $mol_id
    }
}

proc style_msms {mol_id {dopant ""}} {
    mol delrep 0 $mol_id
    if {[catch {style_msms_core $mol_id {name C} element ""} err]} {
        puts "MSMS failed ($err); fallback Surf"
        if {[catch {style_surf $mol_id $dopant} err2]} {
            puts "Surf failed ($err2); fallback QuickSurf"
            style_quicksurf $mol_id $dopant
        }
        return
    }
    if {$dopant ne ""} {
        mol representation VDW 0.85 16.0
        mol color Element
        mol selection "name $dopant"
        mol material Glossy
        mol addrep $mol_id
    }
}

proc style_msms_cages {mol_id {dopant ""}} {
    set atoms_per_cage 60
    set natoms [molinfo $mol_id get numatoms]
    set ncages [expr {int(floor(double($natoms) / $atoms_per_cage))}]
    if {$ncages < 1} { set ncages 1 }

    mol delrep 0 $mol_id
    set ok 1
    for {set k 0} {$k < $ncages} {incr k} {
        set i0 [expr {$k * $atoms_per_cage}]
        set i1 [expr {$i0 + $atoms_per_cage - 1}]
        if {$i1 >= $natoms} { set i1 [expr {$natoms - 1}] }
        set sel "index $i0 to $i1 and name C"
        if {[catch {style_msms_core $mol_id $sel element ""} err]} {
            puts "MSMS cage $k failed ($err); fallback Surf cages"
            set ok 0
            break
        }
    }
    if {!$ok} {
        style_surf_cages $mol_id $dopant
        return
    }
    if {$dopant ne ""} {
        mol representation VDW 0.90 16.0
        mol color Element
        mol selection "name $dopant"
        mol material Glossy
        mol addrep $mol_id
    }
}

proc frame_on_atoms {mol_id {scale_target 38.0}} {
    set sel [atomselect $mol_id {name C}]
    set mm [measure minmax $sel]
    set dx [expr {[lindex $mm 1 0] - [lindex $mm 0 0]}]
    set dy [expr {[lindex $mm 1 1] - [lindex $mm 0 1]}]
    set dz [expr {[lindex $mm 1 2] - [lindex $mm 0 2]}]
    set span [expr {max($dx, max($dy, $dz))}]
    set min_xy [expr {min($dx, $dy)}]

    # Frame on atoms (not the origin); periodic slabs are thin along z.
    display resetview $sel

    set rot_x 0
    set rot_y 0
    if {[info exists ::env(VMD_VIEW_ROT_X)] && $::env(VMD_VIEW_ROT_X) ne ""} {
        set rot_x $::env(VMD_VIEW_ROT_X)
        set rot_y $::env(VMD_VIEW_ROT_Y)
    } elseif {$min_xy > 0.1 && $dz < 0.45 * $min_xy} {
        # ab-plane supercell: face-on view along the layer normal (no oblique tilt).
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

if {[llength $argv] < 2} {
    puts "Usage: vmd -e render_structure_surface.tcl -args STRUCT.xyz OUT.tga \[dopant\] \[mode\]"
    quit
}

set xyz [lindex $argv 0]
set out_tga [lindex $argv 1]
set dopant ""
set mode "quicksurf"
if {[llength $argv] >= 3} { set dopant [lindex $argv 2] }
if {[llength $argv] >= 4} { set mode [lindex $argv 3] }

mol delete all
mol new $xyz type xyz waitfor all
set mid [molinfo top]

switch -- $mode {
    quicksurf_cages { style_quicksurf_cages $mid $dopant }
    msms            { style_msms $mid $dopant }
    msms_cages      { style_msms_cages $mid $dopant }
    surf            { style_surf $mid $dopant }
    surf_cages      { style_surf_cages $mid $dopant }
    default         { style_quicksurf $mid $dopant }
}

apply_pub_style
frame_on_atoms $mid
display resize 1200 1000
render TachyonInternal $out_tga
set probe [msms_probe]
puts "Rendered molecular surface ($mode, probe=${probe}A) $out_tga"
quit
