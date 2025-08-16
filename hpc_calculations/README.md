# Graphullerene HPC计算包

## 目录结构
```
hpc_calculations/
├── inputs/         # CP2K输入文件
├── structures/     # XYZ结构文件
├── batch_scripts/  # 批处理脚本
├── scripts/        # 分析脚本
├── outputs/        # 计算输出（运行后生成）
├── logs/           # 日志文件
├── results/        # 最终结果
└── submit_all.sh   # 主控脚本
```

## 使用方法

### 1. 上传到HPC集群
```bash
scp graphullerene_hpc.tar.gz username@cluster:~/
ssh username@cluster
tar -xzf graphullerene_hpc.tar.gz
cd hpc_calculations
```

### 2. 检查和修改参数
- 编辑批处理脚本中的队列参数
- 确认CP2K模块名称
- 调整计算资源分配

### 3. 提交计算
```bash
# 提交所有批次
./submit_all.sh

# 或单独提交某个批次
sbatch batch_scripts/batch_1.sh
```

### 4. 监控进度
```bash
# 查看任务状态
squeue -u $USER

# 查看输出
tail -f batch1-*.out
```

### 5. 收集结果
结果自动收集，最终文件：
- `final_dft_results.csv` - 所有计算结果
- `hpc_calculation_report.md` - 分析报告
- `energy_vs_strain.png` - 能量图

## 注意事项
- 确保有足够的计算时间配额
- 检查磁盘空间
- 定期备份结果

## 故障排除
- 如果计算失败，检查 `*.err` 文件
- 内存不足：减少并行任务数
- 时间超限：增加walltime或减少批次大小
