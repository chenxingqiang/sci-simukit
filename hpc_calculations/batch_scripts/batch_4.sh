#!/bin/bash
#SBATCH --job-name=graphullerene_batch4
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --time=24:00:00
#SBATCH --partition=gpu
#SBATCH --output=batch4-%j.out
#SBATCH --error=batch4-%j.err

# 加载模块
module load cp2k/2025.2
module load python/3.9

# 设置环境
export OMP_NUM_THREADS=1
export CP2K_DATA_DIR=$CP2K_HOME/data

# 进入工作目录
cd $SLURM_SUBMIT_DIR

echo "开始批次 4 - $(date)"

# 运行计算

echo "运行: C60_strain_p0p0_N_2.5p_config1.inp"
mpirun -np $SLURM_NTASKS cp2k.popt -i inputs/C60_strain_p0p0_N_2.5p_config1.inp -o outputs/C60_strain_p0p0_N_2.5p_config1.out

echo "运行: C60_strain_p0p0_N_5.0p_config1.inp"
mpirun -np $SLURM_NTASKS cp2k.popt -i inputs/C60_strain_p0p0_N_5.0p_config1.inp -o outputs/C60_strain_p0p0_N_5.0p_config1.out

echo "运行: C60_strain_p0p0_N_7.5p_config1.inp"
mpirun -np $SLURM_NTASKS cp2k.popt -i inputs/C60_strain_p0p0_N_7.5p_config1.inp -o outputs/C60_strain_p0p0_N_7.5p_config1.out

echo "运行: C60_strain_p0p0_P_2.5p_config1.inp"
mpirun -np $SLURM_NTASKS cp2k.popt -i inputs/C60_strain_p0p0_P_2.5p_config1.inp -o outputs/C60_strain_p0p0_P_2.5p_config1.out

echo "运行: C60_strain_p0p0_P_5.0p_config1.inp"
mpirun -np $SLURM_NTASKS cp2k.popt -i inputs/C60_strain_p0p0_P_5.0p_config1.inp -o outputs/C60_strain_p0p0_P_5.0p_config1.out

echo "运行: C60_strain_p0p0_P_7.5p_config1.inp"
mpirun -np $SLURM_NTASKS cp2k.popt -i inputs/C60_strain_p0p0_P_7.5p_config1.inp -o outputs/C60_strain_p0p0_P_7.5p_config1.out

echo "运行: C60_strain_p0p0_mixed_B2.5_N2.5_config1.inp"
mpirun -np $SLURM_NTASKS cp2k.popt -i inputs/C60_strain_p0p0_mixed_B2.5_N2.5_config1.inp -o outputs/C60_strain_p0p0_mixed_B2.5_N2.5_config1.out

echo "运行: C60_strain_p0p0_mixed_B5.0_N2.5_config1.inp"
mpirun -np $SLURM_NTASKS cp2k.popt -i inputs/C60_strain_p0p0_mixed_B5.0_N2.5_config1.inp -o outputs/C60_strain_p0p0_mixed_B5.0_N2.5_config1.out

echo "运行: C60_strain_p0p0_mixed_B2.5_N5.0_config1.inp"
mpirun -np $SLURM_NTASKS cp2k.popt -i inputs/C60_strain_p0p0_mixed_B2.5_N5.0_config1.inp -o outputs/C60_strain_p0p0_mixed_B2.5_N5.0_config1.out

echo "运行: C60_strain_+2.5_pristine.inp"
mpirun -np $SLURM_NTASKS cp2k.popt -i inputs/C60_strain_+2.5_pristine.inp -o outputs/C60_strain_+2.5_pristine.out

echo "批次 4 完成 - $(date)"

# 收集能量数据
python scripts/extract_energies.py --batch 4
