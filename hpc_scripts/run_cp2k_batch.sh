#!/bin/bash
#SBATCH --job-name=graphullerene_dft
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --time=48:00:00
#SBATCH --partition=gpu
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err

# 加载模块
module load cp2k/2025.2
module load python/3.9

# 设置环境变量
export OMP_NUM_THREADS=1
export CP2K_DATA_DIR=/path/to/cp2k/data

# 切换到工作目录
cd $SLURM_SUBMIT_DIR

# 运行计算
echo "开始DFT计算: $(date)"

# 批量运行CP2K计算
for inp in cp2k_inputs/*.inp; do
    base=$(basename $inp .inp)
    echo "处理: $base"
    mpirun -np $SLURM_NTASKS cp2k.popt -i $inp -o outputs/${base}.out
done

echo "计算完成: $(date)"

# 收集结果
python scripts/collect_hpc_results.py
