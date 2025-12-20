#!/bin/bash
# Run all electronic structure calculations

cd inputs

echo 'Running elec_neg5p0_pristine...'
mpirun -np 8 cp2k.popt -i elec_neg5p0_pristine.inp -o elec_neg5p0_pristine.out
echo 'Done.'

echo 'Running elec_neg5p0_B...'
mpirun -np 8 cp2k.popt -i elec_neg5p0_B.inp -o elec_neg5p0_B.out
echo 'Done.'

echo 'Running elec_neg5p0_N...'
mpirun -np 8 cp2k.popt -i elec_neg5p0_N.inp -o elec_neg5p0_N.out
echo 'Done.'

echo 'Running elec_neg5p0_P...'
mpirun -np 8 cp2k.popt -i elec_neg5p0_P.inp -o elec_neg5p0_P.out
echo 'Done.'

echo 'Running elec_pos0p0_pristine...'
mpirun -np 8 cp2k.popt -i elec_pos0p0_pristine.inp -o elec_pos0p0_pristine.out
echo 'Done.'

echo 'Running elec_pos0p0_B...'
mpirun -np 8 cp2k.popt -i elec_pos0p0_B.inp -o elec_pos0p0_B.out
echo 'Done.'

echo 'Running elec_pos0p0_N...'
mpirun -np 8 cp2k.popt -i elec_pos0p0_N.inp -o elec_pos0p0_N.out
echo 'Done.'

echo 'Running elec_pos0p0_P...'
mpirun -np 8 cp2k.popt -i elec_pos0p0_P.inp -o elec_pos0p0_P.out
echo 'Done.'

echo 'Running elec_pos5p0_pristine...'
mpirun -np 8 cp2k.popt -i elec_pos5p0_pristine.inp -o elec_pos5p0_pristine.out
echo 'Done.'

echo 'Running elec_pos5p0_B...'
mpirun -np 8 cp2k.popt -i elec_pos5p0_B.inp -o elec_pos5p0_B.out
echo 'Done.'

echo 'Running elec_pos5p0_N...'
mpirun -np 8 cp2k.popt -i elec_pos5p0_N.inp -o elec_pos5p0_N.out
echo 'Done.'

echo 'Running elec_pos5p0_P...'
mpirun -np 8 cp2k.popt -i elec_pos5p0_P.inp -o elec_pos5p0_P.out
echo 'Done.'

