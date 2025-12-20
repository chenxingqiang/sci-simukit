#!/bin/bash
# Size scaling calculations
# Ordered by size (small systems first for quick validation)

cd inputs

echo '=== size_1x60_pristine_pos0pct (60 atoms, ~0.5 GB) ==='
mpirun -np 4 cp2k.popt -i size_1x60_pristine_pos0pct.inp -o size_1x60_pristine_pos0pct.out
echo 'Done.'

echo '=== size_1x60_pristine_pos3pct (60 atoms, ~0.5 GB) ==='
mpirun -np 4 cp2k.popt -i size_1x60_pristine_pos3pct.inp -o size_1x60_pristine_pos3pct.out
echo 'Done.'

echo '=== size_1x60_N_pos0pct (60 atoms, ~0.5 GB) ==='
mpirun -np 4 cp2k.popt -i size_1x60_N_pos0pct.inp -o size_1x60_N_pos0pct.out
echo 'Done.'

echo '=== size_1x60_N_pos3pct (60 atoms, ~0.5 GB) ==='
mpirun -np 4 cp2k.popt -i size_1x60_N_pos3pct.inp -o size_1x60_N_pos3pct.out
echo 'Done.'

echo '=== size_1x60_B_pos0pct (60 atoms, ~0.5 GB) ==='
mpirun -np 4 cp2k.popt -i size_1x60_B_pos0pct.inp -o size_1x60_B_pos0pct.out
echo 'Done.'

echo '=== size_1x60_B_pos3pct (60 atoms, ~0.5 GB) ==='
mpirun -np 4 cp2k.popt -i size_1x60_B_pos3pct.inp -o size_1x60_B_pos3pct.out
echo 'Done.'

echo '=== size_1x60_P_pos0pct (60 atoms, ~0.5 GB) ==='
mpirun -np 4 cp2k.popt -i size_1x60_P_pos0pct.inp -o size_1x60_P_pos0pct.out
echo 'Done.'

echo '=== size_1x60_P_pos3pct (60 atoms, ~0.5 GB) ==='
mpirun -np 4 cp2k.popt -i size_1x60_P_pos3pct.inp -o size_1x60_P_pos3pct.out
echo 'Done.'

echo '=== size_2x60_pristine_pos0pct (120 atoms, ~1.0 GB) ==='
mpirun -np 4 cp2k.popt -i size_2x60_pristine_pos0pct.inp -o size_2x60_pristine_pos0pct.out
echo 'Done.'

echo '=== size_2x60_pristine_pos3pct (120 atoms, ~1.0 GB) ==='
mpirun -np 4 cp2k.popt -i size_2x60_pristine_pos3pct.inp -o size_2x60_pristine_pos3pct.out
echo 'Done.'

echo '=== size_2x60_N_pos0pct (120 atoms, ~1.0 GB) ==='
mpirun -np 4 cp2k.popt -i size_2x60_N_pos0pct.inp -o size_2x60_N_pos0pct.out
echo 'Done.'

echo '=== size_2x60_N_pos3pct (120 atoms, ~1.0 GB) ==='
mpirun -np 4 cp2k.popt -i size_2x60_N_pos3pct.inp -o size_2x60_N_pos3pct.out
echo 'Done.'

echo '=== size_2x60_B_pos0pct (120 atoms, ~1.0 GB) ==='
mpirun -np 4 cp2k.popt -i size_2x60_B_pos0pct.inp -o size_2x60_B_pos0pct.out
echo 'Done.'

echo '=== size_2x60_B_pos3pct (120 atoms, ~1.0 GB) ==='
mpirun -np 4 cp2k.popt -i size_2x60_B_pos3pct.inp -o size_2x60_B_pos3pct.out
echo 'Done.'

echo '=== size_2x60_P_pos0pct (120 atoms, ~1.0 GB) ==='
mpirun -np 4 cp2k.popt -i size_2x60_P_pos0pct.inp -o size_2x60_P_pos0pct.out
echo 'Done.'

echo '=== size_2x60_P_pos3pct (120 atoms, ~1.0 GB) ==='
mpirun -np 4 cp2k.popt -i size_2x60_P_pos3pct.inp -o size_2x60_P_pos3pct.out
echo 'Done.'

echo '=== size_4x60_pristine_pos0pct (240 atoms, ~2.0 GB) ==='
mpirun -np 8 cp2k.popt -i size_4x60_pristine_pos0pct.inp -o size_4x60_pristine_pos0pct.out
echo 'Done.'

echo '=== size_4x60_pristine_pos3pct (240 atoms, ~2.0 GB) ==='
mpirun -np 8 cp2k.popt -i size_4x60_pristine_pos3pct.inp -o size_4x60_pristine_pos3pct.out
echo 'Done.'

echo '=== size_4x60_N_pos0pct (240 atoms, ~2.0 GB) ==='
mpirun -np 8 cp2k.popt -i size_4x60_N_pos0pct.inp -o size_4x60_N_pos0pct.out
echo 'Done.'

echo '=== size_4x60_N_pos3pct (240 atoms, ~2.0 GB) ==='
mpirun -np 8 cp2k.popt -i size_4x60_N_pos3pct.inp -o size_4x60_N_pos3pct.out
echo 'Done.'

echo '=== size_4x60_B_pos0pct (240 atoms, ~2.0 GB) ==='
mpirun -np 8 cp2k.popt -i size_4x60_B_pos0pct.inp -o size_4x60_B_pos0pct.out
echo 'Done.'

echo '=== size_4x60_B_pos3pct (240 atoms, ~2.0 GB) ==='
mpirun -np 8 cp2k.popt -i size_4x60_B_pos3pct.inp -o size_4x60_B_pos3pct.out
echo 'Done.'

echo '=== size_4x60_P_pos0pct (240 atoms, ~2.0 GB) ==='
mpirun -np 8 cp2k.popt -i size_4x60_P_pos0pct.inp -o size_4x60_P_pos0pct.out
echo 'Done.'

echo '=== size_4x60_P_pos3pct (240 atoms, ~2.0 GB) ==='
mpirun -np 8 cp2k.popt -i size_4x60_P_pos3pct.inp -o size_4x60_P_pos3pct.out
echo 'Done.'

echo '=== size_6x60_pristine_pos0pct (360 atoms, ~3.0 GB) ==='
mpirun -np 12 cp2k.popt -i size_6x60_pristine_pos0pct.inp -o size_6x60_pristine_pos0pct.out
echo 'Done.'

echo '=== size_6x60_pristine_pos3pct (360 atoms, ~3.0 GB) ==='
mpirun -np 12 cp2k.popt -i size_6x60_pristine_pos3pct.inp -o size_6x60_pristine_pos3pct.out
echo 'Done.'

echo '=== size_6x60_N_pos0pct (360 atoms, ~3.0 GB) ==='
mpirun -np 12 cp2k.popt -i size_6x60_N_pos0pct.inp -o size_6x60_N_pos0pct.out
echo 'Done.'

echo '=== size_6x60_N_pos3pct (360 atoms, ~3.0 GB) ==='
mpirun -np 12 cp2k.popt -i size_6x60_N_pos3pct.inp -o size_6x60_N_pos3pct.out
echo 'Done.'

echo '=== size_6x60_B_pos0pct (360 atoms, ~3.0 GB) ==='
mpirun -np 12 cp2k.popt -i size_6x60_B_pos0pct.inp -o size_6x60_B_pos0pct.out
echo 'Done.'

echo '=== size_6x60_B_pos3pct (360 atoms, ~3.0 GB) ==='
mpirun -np 12 cp2k.popt -i size_6x60_B_pos3pct.inp -o size_6x60_B_pos3pct.out
echo 'Done.'

echo '=== size_6x60_P_pos0pct (360 atoms, ~3.0 GB) ==='
mpirun -np 12 cp2k.popt -i size_6x60_P_pos0pct.inp -o size_6x60_P_pos0pct.out
echo 'Done.'

echo '=== size_6x60_P_pos3pct (360 atoms, ~3.0 GB) ==='
mpirun -np 12 cp2k.popt -i size_6x60_P_pos3pct.inp -o size_6x60_P_pos3pct.out
echo 'Done.'

echo '=== size_8x60_pristine_pos0pct (480 atoms, ~4.0 GB) ==='
mpirun -np 16 cp2k.popt -i size_8x60_pristine_pos0pct.inp -o size_8x60_pristine_pos0pct.out
echo 'Done.'

echo '=== size_8x60_pristine_pos3pct (480 atoms, ~4.0 GB) ==='
mpirun -np 16 cp2k.popt -i size_8x60_pristine_pos3pct.inp -o size_8x60_pristine_pos3pct.out
echo 'Done.'

echo '=== size_8x60_N_pos0pct (480 atoms, ~4.0 GB) ==='
mpirun -np 16 cp2k.popt -i size_8x60_N_pos0pct.inp -o size_8x60_N_pos0pct.out
echo 'Done.'

echo '=== size_8x60_N_pos3pct (480 atoms, ~4.0 GB) ==='
mpirun -np 16 cp2k.popt -i size_8x60_N_pos3pct.inp -o size_8x60_N_pos3pct.out
echo 'Done.'

echo '=== size_8x60_B_pos0pct (480 atoms, ~4.0 GB) ==='
mpirun -np 16 cp2k.popt -i size_8x60_B_pos0pct.inp -o size_8x60_B_pos0pct.out
echo 'Done.'

echo '=== size_8x60_B_pos3pct (480 atoms, ~4.0 GB) ==='
mpirun -np 16 cp2k.popt -i size_8x60_B_pos3pct.inp -o size_8x60_B_pos3pct.out
echo 'Done.'

echo '=== size_8x60_P_pos0pct (480 atoms, ~4.0 GB) ==='
mpirun -np 16 cp2k.popt -i size_8x60_P_pos0pct.inp -o size_8x60_P_pos0pct.out
echo 'Done.'

echo '=== size_8x60_P_pos3pct (480 atoms, ~4.0 GB) ==='
mpirun -np 16 cp2k.popt -i size_8x60_P_pos3pct.inp -o size_8x60_P_pos3pct.out
echo 'Done.'

