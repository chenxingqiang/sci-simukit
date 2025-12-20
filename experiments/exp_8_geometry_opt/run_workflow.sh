#!/bin/bash
# Two-step workflow: GEO_OPT -> ENERGY
# System: C60 dimer (120 atoms), no strain

cd inputs

echo '=== Step 1: Geometry Optimization - geoopt_pristine ==='
mpirun -np 8 cp2k.popt -i geoopt_pristine.inp -o geoopt_pristine.out

# Extract final geometry from trajectory
tail -n 121 geoopt_pristine-pos-1.xyz > geoopt_pristine_optimized.xyz

echo '=== Step 2: Single Point Energy - geoopt_pristine ==='
sed -e 's/{project_name}/geoopt_pristine_sp/' \
    -e 's/{optimized_xyz}/geoopt_pristine_optimized.xyz/' \
    single_point_template.inp > geoopt_pristine_sp.inp

mpirun -np 8 cp2k.popt -i geoopt_pristine_sp.inp -o geoopt_pristine_sp.out
echo 'Done: geoopt_pristine'

echo '=== Step 1: Geometry Optimization - geoopt_N ==='
mpirun -np 8 cp2k.popt -i geoopt_N.inp -o geoopt_N.out

# Extract final geometry from trajectory
tail -n 121 geoopt_N-pos-1.xyz > geoopt_N_optimized.xyz

echo '=== Step 2: Single Point Energy - geoopt_N ==='
sed -e 's/{project_name}/geoopt_N_sp/' \
    -e 's/{optimized_xyz}/geoopt_N_optimized.xyz/' \
    single_point_template.inp > geoopt_N_sp.inp

mpirun -np 8 cp2k.popt -i geoopt_N_sp.inp -o geoopt_N_sp.out
echo 'Done: geoopt_N'

echo '=== Step 1: Geometry Optimization - geoopt_B ==='
mpirun -np 8 cp2k.popt -i geoopt_B.inp -o geoopt_B.out

# Extract final geometry from trajectory
tail -n 121 geoopt_B-pos-1.xyz > geoopt_B_optimized.xyz

echo '=== Step 2: Single Point Energy - geoopt_B ==='
sed -e 's/{project_name}/geoopt_B_sp/' \
    -e 's/{optimized_xyz}/geoopt_B_optimized.xyz/' \
    single_point_template.inp > geoopt_B_sp.inp

mpirun -np 8 cp2k.popt -i geoopt_B_sp.inp -o geoopt_B_sp.out
echo 'Done: geoopt_B'

echo '=== Step 1: Geometry Optimization - geoopt_P ==='
mpirun -np 8 cp2k.popt -i geoopt_P.inp -o geoopt_P.out

# Extract final geometry from trajectory
tail -n 121 geoopt_P-pos-1.xyz > geoopt_P_optimized.xyz

echo '=== Step 2: Single Point Energy - geoopt_P ==='
sed -e 's/{project_name}/geoopt_P_sp/' \
    -e 's/{optimized_xyz}/geoopt_P_optimized.xyz/' \
    single_point_template.inp > geoopt_P_sp.inp

mpirun -np 8 cp2k.popt -i geoopt_P_sp.inp -o geoopt_P_sp.out
echo 'Done: geoopt_P'

