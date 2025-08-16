#!/bin/bash
#PBS -N graphullerene_dft
#PBS -l nodes=1:ppn=32
#PBS -l walltime=48:00:00
#PBS -q gpu
#PBS -o pbs-${PBS_JOBID}.out
#PBS -e pbs-${PBS_JOBID}.err

# 切换到提交目录
cd $PBS_O_WORKDIR

# 加载模块和运行（与SLURM类似）
module load cp2k/2025.2
module load python/3.9

# 运行计算
mpirun -np 32 cp2k.popt -i input.inp -o output.out
