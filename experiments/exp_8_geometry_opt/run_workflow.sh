#!/bin/bash
# Two-step workflow: GEO_OPT -> ENERGY

cd inputs

echo '=== Step 1: Geometry Optimization - geoopt_pos0p0_pristine ==='
mpirun -np 8 cp2k.popt -i geoopt_pos0p0_pristine.inp -o geoopt_pos0p0_pristine.out

# Extract final geometry from trajectory
tail -n 61 geoopt_pos0p0_pristine-pos-1.xyz > geoopt_pos0p0_pristine_optimized.xyz

echo '=== Step 2: Single Point Energy - geoopt_pos0p0_pristine ==='
sed -e 's/{project_name}/geoopt_pos0p0_pristine_sp/' \
    -e 's/{optimized_xyz}/geoopt_pos0p0_pristine_optimized.xyz/' \
    -e 's/{box_a}/15.0/' \
    -e 's/{box_b}/15.0/' \
    -e 's/{box_c}/20.0/' \
    single_point_template.inp > geoopt_pos0p0_pristine_sp.inp

mpirun -np 8 cp2k.popt -i geoopt_pos0p0_pristine_sp.inp -o geoopt_pos0p0_pristine_sp.out
echo 'Done: geoopt_pos0p0_pristine'

echo '=== Step 1: Geometry Optimization - geoopt_pos0p0_N ==='
mpirun -np 8 cp2k.popt -i geoopt_pos0p0_N.inp -o geoopt_pos0p0_N.out

# Extract final geometry from trajectory
tail -n 61 geoopt_pos0p0_N-pos-1.xyz > geoopt_pos0p0_N_optimized.xyz

echo '=== Step 2: Single Point Energy - geoopt_pos0p0_N ==='
sed -e 's/{project_name}/geoopt_pos0p0_N_sp/' \
    -e 's/{optimized_xyz}/geoopt_pos0p0_N_optimized.xyz/' \
    -e 's/{box_a}/15.0/' \
    -e 's/{box_b}/15.0/' \
    -e 's/{box_c}/20.0/' \
    single_point_template.inp > geoopt_pos0p0_N_sp.inp

mpirun -np 8 cp2k.popt -i geoopt_pos0p0_N_sp.inp -o geoopt_pos0p0_N_sp.out
echo 'Done: geoopt_pos0p0_N'

echo '=== Step 1: Geometry Optimization - geoopt_pos0p0_B ==='
mpirun -np 8 cp2k.popt -i geoopt_pos0p0_B.inp -o geoopt_pos0p0_B.out

# Extract final geometry from trajectory
tail -n 61 geoopt_pos0p0_B-pos-1.xyz > geoopt_pos0p0_B_optimized.xyz

echo '=== Step 2: Single Point Energy - geoopt_pos0p0_B ==='
sed -e 's/{project_name}/geoopt_pos0p0_B_sp/' \
    -e 's/{optimized_xyz}/geoopt_pos0p0_B_optimized.xyz/' \
    -e 's/{box_a}/15.0/' \
    -e 's/{box_b}/15.0/' \
    -e 's/{box_c}/20.0/' \
    single_point_template.inp > geoopt_pos0p0_B_sp.inp

mpirun -np 8 cp2k.popt -i geoopt_pos0p0_B_sp.inp -o geoopt_pos0p0_B_sp.out
echo 'Done: geoopt_pos0p0_B'

echo '=== Step 1: Geometry Optimization - geoopt_pos0p0_P ==='
mpirun -np 8 cp2k.popt -i geoopt_pos0p0_P.inp -o geoopt_pos0p0_P.out

# Extract final geometry from trajectory
tail -n 61 geoopt_pos0p0_P-pos-1.xyz > geoopt_pos0p0_P_optimized.xyz

echo '=== Step 2: Single Point Energy - geoopt_pos0p0_P ==='
sed -e 's/{project_name}/geoopt_pos0p0_P_sp/' \
    -e 's/{optimized_xyz}/geoopt_pos0p0_P_optimized.xyz/' \
    -e 's/{box_a}/15.0/' \
    -e 's/{box_b}/15.0/' \
    -e 's/{box_c}/20.0/' \
    single_point_template.inp > geoopt_pos0p0_P_sp.inp

mpirun -np 8 cp2k.popt -i geoopt_pos0p0_P_sp.inp -o geoopt_pos0p0_P_sp.out
echo 'Done: geoopt_pos0p0_P'

echo '=== Step 1: Geometry Optimization - geoopt_pos3p0_pristine ==='
mpirun -np 8 cp2k.popt -i geoopt_pos3p0_pristine.inp -o geoopt_pos3p0_pristine.out

# Extract final geometry from trajectory
tail -n 61 geoopt_pos3p0_pristine-pos-1.xyz > geoopt_pos3p0_pristine_optimized.xyz

echo '=== Step 2: Single Point Energy - geoopt_pos3p0_pristine ==='
sed -e 's/{project_name}/geoopt_pos3p0_pristine_sp/' \
    -e 's/{optimized_xyz}/geoopt_pos3p0_pristine_optimized.xyz/' \
    -e 's/{box_a}/15.0/' \
    -e 's/{box_b}/15.0/' \
    -e 's/{box_c}/20.0/' \
    single_point_template.inp > geoopt_pos3p0_pristine_sp.inp

mpirun -np 8 cp2k.popt -i geoopt_pos3p0_pristine_sp.inp -o geoopt_pos3p0_pristine_sp.out
echo 'Done: geoopt_pos3p0_pristine'

echo '=== Step 1: Geometry Optimization - geoopt_pos3p0_N ==='
mpirun -np 8 cp2k.popt -i geoopt_pos3p0_N.inp -o geoopt_pos3p0_N.out

# Extract final geometry from trajectory
tail -n 61 geoopt_pos3p0_N-pos-1.xyz > geoopt_pos3p0_N_optimized.xyz

echo '=== Step 2: Single Point Energy - geoopt_pos3p0_N ==='
sed -e 's/{project_name}/geoopt_pos3p0_N_sp/' \
    -e 's/{optimized_xyz}/geoopt_pos3p0_N_optimized.xyz/' \
    -e 's/{box_a}/15.0/' \
    -e 's/{box_b}/15.0/' \
    -e 's/{box_c}/20.0/' \
    single_point_template.inp > geoopt_pos3p0_N_sp.inp

mpirun -np 8 cp2k.popt -i geoopt_pos3p0_N_sp.inp -o geoopt_pos3p0_N_sp.out
echo 'Done: geoopt_pos3p0_N'

echo '=== Step 1: Geometry Optimization - geoopt_pos3p0_B ==='
mpirun -np 8 cp2k.popt -i geoopt_pos3p0_B.inp -o geoopt_pos3p0_B.out

# Extract final geometry from trajectory
tail -n 61 geoopt_pos3p0_B-pos-1.xyz > geoopt_pos3p0_B_optimized.xyz

echo '=== Step 2: Single Point Energy - geoopt_pos3p0_B ==='
sed -e 's/{project_name}/geoopt_pos3p0_B_sp/' \
    -e 's/{optimized_xyz}/geoopt_pos3p0_B_optimized.xyz/' \
    -e 's/{box_a}/15.0/' \
    -e 's/{box_b}/15.0/' \
    -e 's/{box_c}/20.0/' \
    single_point_template.inp > geoopt_pos3p0_B_sp.inp

mpirun -np 8 cp2k.popt -i geoopt_pos3p0_B_sp.inp -o geoopt_pos3p0_B_sp.out
echo 'Done: geoopt_pos3p0_B'

echo '=== Step 1: Geometry Optimization - geoopt_pos3p0_P ==='
mpirun -np 8 cp2k.popt -i geoopt_pos3p0_P.inp -o geoopt_pos3p0_P.out

# Extract final geometry from trajectory
tail -n 61 geoopt_pos3p0_P-pos-1.xyz > geoopt_pos3p0_P_optimized.xyz

echo '=== Step 2: Single Point Energy - geoopt_pos3p0_P ==='
sed -e 's/{project_name}/geoopt_pos3p0_P_sp/' \
    -e 's/{optimized_xyz}/geoopt_pos3p0_P_optimized.xyz/' \
    -e 's/{box_a}/15.0/' \
    -e 's/{box_b}/15.0/' \
    -e 's/{box_c}/20.0/' \
    single_point_template.inp > geoopt_pos3p0_P_sp.inp

mpirun -np 8 cp2k.popt -i geoopt_pos3p0_P_sp.inp -o geoopt_pos3p0_P_sp.out
echo 'Done: geoopt_pos3p0_P'

