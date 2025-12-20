#!/bin/bash
# Run size scaling calculations
# Note: Larger systems require more memory and time

cd inputs

echo '=== size_1x60_pristine (60 atoms, ~0.5 GB) ==='
mpirun -np 4 cp2k.popt -i size_1x60_pristine.inp -o size_1x60_pristine.out
echo 'Done.'

echo '=== size_1x60_N (60 atoms, ~0.5 GB) ==='
mpirun -np 4 cp2k.popt -i size_1x60_N.inp -o size_1x60_N.out
echo 'Done.'

echo '=== size_2x60_pristine (120 atoms, ~1.0 GB) ==='
mpirun -np 4 cp2k.popt -i size_2x60_pristine.inp -o size_2x60_pristine.out
echo 'Done.'

echo '=== size_2x60_N (120 atoms, ~1.0 GB) ==='
mpirun -np 4 cp2k.popt -i size_2x60_N.inp -o size_2x60_N.out
echo 'Done.'

echo '=== size_4x60_pristine (240 atoms, ~2.0 GB) ==='
mpirun -np 8 cp2k.popt -i size_4x60_pristine.inp -o size_4x60_pristine.out
echo 'Done.'

echo '=== size_4x60_N (240 atoms, ~2.0 GB) ==='
mpirun -np 8 cp2k.popt -i size_4x60_N.inp -o size_4x60_N.out
echo 'Done.'

echo '=== size_6x60_pristine (360 atoms, ~3.0 GB) ==='
mpirun -np 12 cp2k.popt -i size_6x60_pristine.inp -o size_6x60_pristine.out
echo 'Done.'

echo '=== size_6x60_N (360 atoms, ~3.0 GB) ==='
mpirun -np 12 cp2k.popt -i size_6x60_N.inp -o size_6x60_N.out
echo 'Done.'

echo '=== size_8x60_pristine (480 atoms, ~4.0 GB) ==='
mpirun -np 16 cp2k.popt -i size_8x60_pristine.inp -o size_8x60_pristine.out
echo 'Done.'

echo '=== size_8x60_N (480 atoms, ~4.0 GB) ==='
mpirun -np 16 cp2k.popt -i size_8x60_N.inp -o size_8x60_N.out
echo 'Done.'

