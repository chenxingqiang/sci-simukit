POSCAR.C60 qHP C60 unit cell employed for band structure calculations

hybrid-vdw-cell-opt.inp cell optimization at OK input for vdW C60

alpha-30-probe.inp example of probe input to estimate Koopman's compliant alpha


MD. inp files input for MD simulations
C60.xyz and graph.xyz starting config. of MD simulation

1-5.xyz and g1-g5.xyz structural configurations extrapolated from MD of vdW C60 and qHP C60

C60-hole-fixed-environment.inp geometry optimization input for hole/electron in vdw C60 with fixed enviroment (coordinate file is C60-room.xyz) 
comment  the part
&CONSTRAINT
 &FIXED_ATOMS
  LIST 1..1860
 &END FIXED_ATOMS
&END CONSTRAINT
to fully relax the cell

Substitute 
  LIST 1..1860
with 
  LIST 1861..1920
  to keep fixed the central molecule
