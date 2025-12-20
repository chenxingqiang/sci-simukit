#!/bin/bash
# Polaron workflow: GEO_OPT -> ENERGY
# Captures polaron lattice distortion

cd inputs

echo '=== pristine neutral: Step 1 - GEO_OPT ==='
mpirun -np 8 cp2k.popt -i polaron_pristine_qpos0_opt.inp -o polaron_pristine_qpos0_opt.out

# Extract optimized geometry (last frame: 122 lines = 1 atom count + 1 comment + 120 coords)
tail -n 122 polaron_pristine_qpos0_opt-pos-1.xyz > polaron_pristine_qpos0_opt_final.xyz

echo '=== pristine neutral: Step 2 - ENERGY ==='
sed -e 's/{project_name}/polaron_pristine_qpos0_sp/' \
    -e 's/{optimized_xyz}/polaron_pristine_qpos0_opt_final.xyz/' \
    -e 's/{charge}/0/' \
    -e 's/{multiplicity}/1/' \
    -e 's/{uks}/.FALSE./' \
    single_point_template.inp > polaron_pristine_qpos0_sp.inp

mpirun -np 8 cp2k.popt -i polaron_pristine_qpos0_sp.inp -o polaron_pristine_qpos0_sp.out
echo 'Done: pristine neutral'

echo '=== pristine cation (+1): Step 1 - GEO_OPT ==='
mpirun -np 8 cp2k.popt -i polaron_pristine_qpos1_opt.inp -o polaron_pristine_qpos1_opt.out

# Extract optimized geometry (last frame: 122 lines = 1 atom count + 1 comment + 120 coords)
tail -n 122 polaron_pristine_qpos1_opt-pos-1.xyz > polaron_pristine_qpos1_opt_final.xyz

echo '=== pristine cation (+1): Step 2 - ENERGY ==='
sed -e 's/{project_name}/polaron_pristine_qpos1_sp/' \
    -e 's/{optimized_xyz}/polaron_pristine_qpos1_opt_final.xyz/' \
    -e 's/{charge}/1/' \
    -e 's/{multiplicity}/2/' \
    -e 's/{uks}/.TRUE./' \
    single_point_template.inp > polaron_pristine_qpos1_sp.inp

mpirun -np 8 cp2k.popt -i polaron_pristine_qpos1_sp.inp -o polaron_pristine_qpos1_sp.out
echo 'Done: pristine cation (+1)'

echo '=== pristine anion (-1): Step 1 - GEO_OPT ==='
mpirun -np 8 cp2k.popt -i polaron_pristine_qneg1_opt.inp -o polaron_pristine_qneg1_opt.out

# Extract optimized geometry (last frame: 122 lines = 1 atom count + 1 comment + 120 coords)
tail -n 122 polaron_pristine_qneg1_opt-pos-1.xyz > polaron_pristine_qneg1_opt_final.xyz

echo '=== pristine anion (-1): Step 2 - ENERGY ==='
sed -e 's/{project_name}/polaron_pristine_qneg1_sp/' \
    -e 's/{optimized_xyz}/polaron_pristine_qneg1_opt_final.xyz/' \
    -e 's/{charge}/-1/' \
    -e 's/{multiplicity}/2/' \
    -e 's/{uks}/.TRUE./' \
    single_point_template.inp > polaron_pristine_qneg1_sp.inp

mpirun -np 8 cp2k.popt -i polaron_pristine_qneg1_sp.inp -o polaron_pristine_qneg1_sp.out
echo 'Done: pristine anion (-1)'

echo '=== N neutral: Step 1 - GEO_OPT ==='
mpirun -np 8 cp2k.popt -i polaron_N_qpos0_opt.inp -o polaron_N_qpos0_opt.out

# Extract optimized geometry (last frame: 122 lines = 1 atom count + 1 comment + 120 coords)
tail -n 122 polaron_N_qpos0_opt-pos-1.xyz > polaron_N_qpos0_opt_final.xyz

echo '=== N neutral: Step 2 - ENERGY ==='
sed -e 's/{project_name}/polaron_N_qpos0_sp/' \
    -e 's/{optimized_xyz}/polaron_N_qpos0_opt_final.xyz/' \
    -e 's/{charge}/0/' \
    -e 's/{multiplicity}/1/' \
    -e 's/{uks}/.FALSE./' \
    single_point_template.inp > polaron_N_qpos0_sp.inp

mpirun -np 8 cp2k.popt -i polaron_N_qpos0_sp.inp -o polaron_N_qpos0_sp.out
echo 'Done: N neutral'

echo '=== N cation (+1): Step 1 - GEO_OPT ==='
mpirun -np 8 cp2k.popt -i polaron_N_qpos1_opt.inp -o polaron_N_qpos1_opt.out

# Extract optimized geometry (last frame: 122 lines = 1 atom count + 1 comment + 120 coords)
tail -n 122 polaron_N_qpos1_opt-pos-1.xyz > polaron_N_qpos1_opt_final.xyz

echo '=== N cation (+1): Step 2 - ENERGY ==='
sed -e 's/{project_name}/polaron_N_qpos1_sp/' \
    -e 's/{optimized_xyz}/polaron_N_qpos1_opt_final.xyz/' \
    -e 's/{charge}/1/' \
    -e 's/{multiplicity}/2/' \
    -e 's/{uks}/.TRUE./' \
    single_point_template.inp > polaron_N_qpos1_sp.inp

mpirun -np 8 cp2k.popt -i polaron_N_qpos1_sp.inp -o polaron_N_qpos1_sp.out
echo 'Done: N cation (+1)'

echo '=== N anion (-1): Step 1 - GEO_OPT ==='
mpirun -np 8 cp2k.popt -i polaron_N_qneg1_opt.inp -o polaron_N_qneg1_opt.out

# Extract optimized geometry (last frame: 122 lines = 1 atom count + 1 comment + 120 coords)
tail -n 122 polaron_N_qneg1_opt-pos-1.xyz > polaron_N_qneg1_opt_final.xyz

echo '=== N anion (-1): Step 2 - ENERGY ==='
sed -e 's/{project_name}/polaron_N_qneg1_sp/' \
    -e 's/{optimized_xyz}/polaron_N_qneg1_opt_final.xyz/' \
    -e 's/{charge}/-1/' \
    -e 's/{multiplicity}/2/' \
    -e 's/{uks}/.TRUE./' \
    single_point_template.inp > polaron_N_qneg1_sp.inp

mpirun -np 8 cp2k.popt -i polaron_N_qneg1_sp.inp -o polaron_N_qneg1_sp.out
echo 'Done: N anion (-1)'

echo '=== B neutral: Step 1 - GEO_OPT ==='
mpirun -np 8 cp2k.popt -i polaron_B_qpos0_opt.inp -o polaron_B_qpos0_opt.out

# Extract optimized geometry (last frame: 122 lines = 1 atom count + 1 comment + 120 coords)
tail -n 122 polaron_B_qpos0_opt-pos-1.xyz > polaron_B_qpos0_opt_final.xyz

echo '=== B neutral: Step 2 - ENERGY ==='
sed -e 's/{project_name}/polaron_B_qpos0_sp/' \
    -e 's/{optimized_xyz}/polaron_B_qpos0_opt_final.xyz/' \
    -e 's/{charge}/0/' \
    -e 's/{multiplicity}/1/' \
    -e 's/{uks}/.FALSE./' \
    single_point_template.inp > polaron_B_qpos0_sp.inp

mpirun -np 8 cp2k.popt -i polaron_B_qpos0_sp.inp -o polaron_B_qpos0_sp.out
echo 'Done: B neutral'

echo '=== B cation (+1): Step 1 - GEO_OPT ==='
mpirun -np 8 cp2k.popt -i polaron_B_qpos1_opt.inp -o polaron_B_qpos1_opt.out

# Extract optimized geometry (last frame: 122 lines = 1 atom count + 1 comment + 120 coords)
tail -n 122 polaron_B_qpos1_opt-pos-1.xyz > polaron_B_qpos1_opt_final.xyz

echo '=== B cation (+1): Step 2 - ENERGY ==='
sed -e 's/{project_name}/polaron_B_qpos1_sp/' \
    -e 's/{optimized_xyz}/polaron_B_qpos1_opt_final.xyz/' \
    -e 's/{charge}/1/' \
    -e 's/{multiplicity}/2/' \
    -e 's/{uks}/.TRUE./' \
    single_point_template.inp > polaron_B_qpos1_sp.inp

mpirun -np 8 cp2k.popt -i polaron_B_qpos1_sp.inp -o polaron_B_qpos1_sp.out
echo 'Done: B cation (+1)'

echo '=== B anion (-1): Step 1 - GEO_OPT ==='
mpirun -np 8 cp2k.popt -i polaron_B_qneg1_opt.inp -o polaron_B_qneg1_opt.out

# Extract optimized geometry (last frame: 122 lines = 1 atom count + 1 comment + 120 coords)
tail -n 122 polaron_B_qneg1_opt-pos-1.xyz > polaron_B_qneg1_opt_final.xyz

echo '=== B anion (-1): Step 2 - ENERGY ==='
sed -e 's/{project_name}/polaron_B_qneg1_sp/' \
    -e 's/{optimized_xyz}/polaron_B_qneg1_opt_final.xyz/' \
    -e 's/{charge}/-1/' \
    -e 's/{multiplicity}/2/' \
    -e 's/{uks}/.TRUE./' \
    single_point_template.inp > polaron_B_qneg1_sp.inp

mpirun -np 8 cp2k.popt -i polaron_B_qneg1_sp.inp -o polaron_B_qneg1_sp.out
echo 'Done: B anion (-1)'

echo '=== P neutral: Step 1 - GEO_OPT ==='
mpirun -np 8 cp2k.popt -i polaron_P_qpos0_opt.inp -o polaron_P_qpos0_opt.out

# Extract optimized geometry (last frame: 122 lines = 1 atom count + 1 comment + 120 coords)
tail -n 122 polaron_P_qpos0_opt-pos-1.xyz > polaron_P_qpos0_opt_final.xyz

echo '=== P neutral: Step 2 - ENERGY ==='
sed -e 's/{project_name}/polaron_P_qpos0_sp/' \
    -e 's/{optimized_xyz}/polaron_P_qpos0_opt_final.xyz/' \
    -e 's/{charge}/0/' \
    -e 's/{multiplicity}/1/' \
    -e 's/{uks}/.FALSE./' \
    single_point_template.inp > polaron_P_qpos0_sp.inp

mpirun -np 8 cp2k.popt -i polaron_P_qpos0_sp.inp -o polaron_P_qpos0_sp.out
echo 'Done: P neutral'

echo '=== P cation (+1): Step 1 - GEO_OPT ==='
mpirun -np 8 cp2k.popt -i polaron_P_qpos1_opt.inp -o polaron_P_qpos1_opt.out

# Extract optimized geometry (last frame: 122 lines = 1 atom count + 1 comment + 120 coords)
tail -n 122 polaron_P_qpos1_opt-pos-1.xyz > polaron_P_qpos1_opt_final.xyz

echo '=== P cation (+1): Step 2 - ENERGY ==='
sed -e 's/{project_name}/polaron_P_qpos1_sp/' \
    -e 's/{optimized_xyz}/polaron_P_qpos1_opt_final.xyz/' \
    -e 's/{charge}/1/' \
    -e 's/{multiplicity}/2/' \
    -e 's/{uks}/.TRUE./' \
    single_point_template.inp > polaron_P_qpos1_sp.inp

mpirun -np 8 cp2k.popt -i polaron_P_qpos1_sp.inp -o polaron_P_qpos1_sp.out
echo 'Done: P cation (+1)'

echo '=== P anion (-1): Step 1 - GEO_OPT ==='
mpirun -np 8 cp2k.popt -i polaron_P_qneg1_opt.inp -o polaron_P_qneg1_opt.out

# Extract optimized geometry (last frame: 122 lines = 1 atom count + 1 comment + 120 coords)
tail -n 122 polaron_P_qneg1_opt-pos-1.xyz > polaron_P_qneg1_opt_final.xyz

echo '=== P anion (-1): Step 2 - ENERGY ==='
sed -e 's/{project_name}/polaron_P_qneg1_sp/' \
    -e 's/{optimized_xyz}/polaron_P_qneg1_opt_final.xyz/' \
    -e 's/{charge}/-1/' \
    -e 's/{multiplicity}/2/' \
    -e 's/{uks}/.TRUE./' \
    single_point_template.inp > polaron_P_qneg1_sp.inp

mpirun -np 8 cp2k.popt -i polaron_P_qneg1_sp.inp -o polaron_P_qneg1_sp.out
echo 'Done: P anion (-1)'

