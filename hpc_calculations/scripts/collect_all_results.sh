#!/bin/bash
#SBATCH --job-name=collect_results
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=1:00:00
#SBATCH --output=collect-%j.out

echo "收集所有计算结果"

# 合并所有批次结果
python scripts/merge_all_results.py

# 生成分析报告
python scripts/generate_hpc_report.py

echo "结果收集完成"
