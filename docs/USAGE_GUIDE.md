# Graphullerene Strain Engineering - 使用指南

## 快速开始

### 1. 环境设置
```bash
python3 -m venv fullerene-env
source fullerene-env/bin/activate
pip install -r requirements.txt
```

### 2. 生成结构
```bash
# 生成应变结构
python src/strain_generator.py --strain_range -5 5

# 生成掺杂结构  
python src/doping_generator.py --dopants B N P

# 生成组合结构
python src/strain_doping_combiner.py
```

### 3. 运行实验
```bash
python experiments/run_complete_experiment.py --mode quick
```

### 4. 生成论文图表
```bash
python paper/paper_figures_generator.py
```

## 高性能计算

1. 准备输入文件
2. 修改HPC脚本中的路径
3. 提交任务：
   ```bash
   sbatch hpc_scripts/run_cp2k_batch.sh
   ```

## 数据分析

结果文件位于 `results/` 目录：
- `experiment_analysis_report.md` - 实验分析报告
- `figures/` - 生成的图表
- `hpc_results.csv` - DFT计算结果

## 常见问题

**Q: 如何调整应变范围？**
A: 修改 `--strain_range` 参数

**Q: 如何添加新的掺杂元素？**
A: 在 `doping_generator.py` 中添加元素配置

**Q: ML模型训练失败？**
A: 检查CUDA环境和PyTorch版本兼容性
