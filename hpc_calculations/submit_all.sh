#!/bin/bash
# 主控脚本 - 提交所有批次

echo "提交 7 个批次的计算任务"

# 提交所有批次

echo "提交批次 1"
JOB_ID_1=$(sbatch --parsable batch_scripts/batch_1.sh)
echo "批次 1 任务ID: $JOB_ID_1"

echo "提交批次 2"
JOB_ID_2=$(sbatch --parsable batch_scripts/batch_2.sh)
echo "批次 2 任务ID: $JOB_ID_2"

echo "提交批次 3"
JOB_ID_3=$(sbatch --parsable batch_scripts/batch_3.sh)
echo "批次 3 任务ID: $JOB_ID_3"

echo "提交批次 4"
JOB_ID_4=$(sbatch --parsable batch_scripts/batch_4.sh)
echo "批次 4 任务ID: $JOB_ID_4"

echo "提交批次 5"
JOB_ID_5=$(sbatch --parsable batch_scripts/batch_5.sh)
echo "批次 5 任务ID: $JOB_ID_5"

echo "提交批次 6"
JOB_ID_6=$(sbatch --parsable batch_scripts/batch_6.sh)
echo "批次 6 任务ID: $JOB_ID_6"

echo "提交批次 7"
JOB_ID_7=$(sbatch --parsable batch_scripts/batch_7.sh)
echo "批次 7 任务ID: $JOB_ID_7"

# 等待所有任务完成
echo "等待所有任务完成..."

# 创建依赖任务收集结果
sbatch --dependency=afterok:$(echo $JOB_ID_* | tr ' ' ':') scripts/collect_all_results.sh

echo "所有任务已提交"
