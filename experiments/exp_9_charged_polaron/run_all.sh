#!/bin/bash
# Run all charged polaron calculations

cd inputs

echo 'Running pristine neutral...'
mpirun -np 8 cp2k.popt -i polaron_pristine_qpos0.inp -o polaron_pristine_qpos0.out
echo 'Done.'

echo 'Running pristine cation (+1)...'
mpirun -np 8 cp2k.popt -i polaron_pristine_qpos1.inp -o polaron_pristine_qpos1.out
echo 'Done.'

echo 'Running pristine anion (-1)...'
mpirun -np 8 cp2k.popt -i polaron_pristine_qneg1.inp -o polaron_pristine_qneg1.out
echo 'Done.'

echo 'Running N neutral...'
mpirun -np 8 cp2k.popt -i polaron_N_qpos0.inp -o polaron_N_qpos0.out
echo 'Done.'

echo 'Running N cation (+1)...'
mpirun -np 8 cp2k.popt -i polaron_N_qpos1.inp -o polaron_N_qpos1.out
echo 'Done.'

echo 'Running N anion (-1)...'
mpirun -np 8 cp2k.popt -i polaron_N_qneg1.inp -o polaron_N_qneg1.out
echo 'Done.'

echo 'Running B neutral...'
mpirun -np 8 cp2k.popt -i polaron_B_qpos0.inp -o polaron_B_qpos0.out
echo 'Done.'

echo 'Running B cation (+1)...'
mpirun -np 8 cp2k.popt -i polaron_B_qpos1.inp -o polaron_B_qpos1.out
echo 'Done.'

echo 'Running B anion (-1)...'
mpirun -np 8 cp2k.popt -i polaron_B_qneg1.inp -o polaron_B_qneg1.out
echo 'Done.'

echo 'Running P neutral...'
mpirun -np 8 cp2k.popt -i polaron_P_qpos0.inp -o polaron_P_qpos0.out
echo 'Done.'

echo 'Running P cation (+1)...'
mpirun -np 8 cp2k.popt -i polaron_P_qpos1.inp -o polaron_P_qpos1.out
echo 'Done.'

echo 'Running P anion (-1)...'
mpirun -np 8 cp2k.popt -i polaron_P_qneg1.inp -o polaron_P_qneg1.out
echo 'Done.'

