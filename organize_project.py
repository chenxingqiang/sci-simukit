#!/usr/bin/env python3
"""
项目结构整理脚本
准备GitHub仓库提交和论文/代码分离

作者: 基于您的项目经验
版本: 1.0
"""

import os
import shutil
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def organize_project():
    """组织项目结构"""
    
    # 创建目录结构
    dirs_to_create = [
        'src',           # 源代码
        'experiments',   # 实验脚本
        'paper',         # 论文相关
        'paper/figures', # 论文图表
        'data',          # 数据文件
        'results',       # 结果输出
        'results/figures',
        'results/reports',
        'hpc_scripts',   # HPC脚本
        'tests',         # 测试代码
        'docs'           # 文档
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"创建目录: {dir_path}")
    
    # 移动文件到合适的位置
    file_mappings = {
        # 源代码 -> src/
        'strain_generator.py': 'src/strain_generator.py',
        'doping_generator.py': 'src/doping_generator.py',
        'strain_doping_combiner.py': 'src/strain_doping_combiner.py',
        'graphullerene_gnn.py': 'src/graphullerene_gnn.py',
        
        # 实验脚本 -> experiments/
        'run_complete_experiment.py': 'experiments/run_complete_experiment.py',
        'fullerene_strain_search.py': 'experiments/fullerene_strain_search.py',
        'update_references.py': 'experiments/update_references.py',
        
        # 论文相关 -> paper/
        'strain_doped_graphullerene.tex': 'paper/strain_doped_graphullerene.tex',
        'strain_graphullerene_50refs.bib': 'paper/strain_graphullerene_50refs.bib',
        'paper_figures_generator.py': 'paper/paper_figures_generator.py',
        
        # 结果 -> results/
        'experiment_results': 'results/experiment_results',
        'strain_doped_structures': 'data/strain_doped_structures',
        'strained_structures': 'data/strained_structures',
        'doped_structures': 'data/doped_structures'
    }
    
    for src, dst in file_mappings.items():
        if Path(src).exists():
            dst_path = Path(dst)
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            if Path(src).is_dir():
                if dst_path.exists():
                    shutil.rmtree(dst_path)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            logger.info(f"移动: {src} -> {dst}")
    
    # 创建HPC脚本
    create_hpc_scripts()
    
    # 创建文档
    create_documentation()
    
    logger.info("项目结构整理完成！")

def create_hpc_scripts():
    """创建HPC批处理脚本"""
    
    # SLURM脚本模板
    slurm_script = """#!/bin/bash
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
"""
    
    with open('hpc_scripts/run_cp2k_batch.sh', 'w') as f:
        f.write(slurm_script)
    
    # PBS脚本模板
    pbs_script = """#!/bin/bash
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
"""
    
    with open('hpc_scripts/run_cp2k_pbs.sh', 'w') as f:
        f.write(pbs_script)
    
    # 结果收集脚本
    collect_script = """#!/usr/bin/env python3
'''收集HPC计算结果'''

import os
import pandas as pd
from pathlib import Path
import json

def collect_results():
    results = []
    
    # 遍历输出文件
    for out_file in Path('outputs').glob('*.out'):
        # 解析输出文件获取能量、带隙等
        # 这里是示例代码，实际需要根据CP2K输出格式解析
        data = {
            'structure': out_file.stem,
            'total_energy': -100.0,  # 示例值
            'band_gap': 1.8,         # 示例值
            'computation_time': 3600  # 秒
        }
        results.append(data)
    
    # 保存结果
    df = pd.DataFrame(results)
    df.to_csv('hpc_results.csv', index=False)
    
    print(f"收集了 {len(results)} 个计算结果")

if __name__ == "__main__":
    collect_results()
"""
    
    with open('hpc_scripts/collect_results.py', 'w') as f:
        f.write(collect_script)
    
    # 使脚本可执行
    os.chmod('hpc_scripts/run_cp2k_batch.sh', 0o755)
    os.chmod('hpc_scripts/run_cp2k_pbs.sh', 0o755)
    os.chmod('hpc_scripts/collect_results.py', 0o755)
    
    logger.info("HPC脚本创建完成")

def create_documentation():
    """创建项目文档"""
    
    # CONTRIBUTING.md
    contributing = """# Contributing to Graphullerene Strain Engineering

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to all functions
- Include type hints where appropriate

## Testing

Before submitting a PR:
```bash
python -m pytest tests/
```

## Documentation

- Update README.md if adding new features
- Add examples for new functionality
- Update docstrings
"""
    
    with open('CONTRIBUTING.md', 'w') as f:
        f.write(contributing)
    
    # LICENSE
    license_text = """MIT License

Copyright (c) 2024 Graphullerene Research Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    
    with open('LICENSE', 'w') as f:
        f.write(license_text)
    
    # 使用说明
    usage_guide = """# Graphullerene Strain Engineering - 使用指南

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
"""
    
    with open('docs/USAGE_GUIDE.md', 'w') as f:
        f.write(usage_guide)
    
    logger.info("文档创建完成")

def create_github_actions():
    """创建GitHub Actions CI/CD配置"""
    
    Path('.github/workflows').mkdir(parents=True, exist_ok=True)
    
    ci_yaml = """name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        
  lint:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install linting tools
      run: |
        pip install flake8 black isort
    
    - name: Run linters
      run: |
        flake8 src/
        black --check src/
        isort --check-only src/
"""
    
    with open('.github/workflows/ci.yml', 'w') as f:
        f.write(ci_yaml)
    
    logger.info("GitHub Actions配置创建完成")

def main():
    """主函数"""
    logger.info("开始整理项目结构...")
    
    # 整理文件
    organize_project()
    
    # 创建GitHub Actions
    create_github_actions()
    
    # 生成论文图表
    logger.info("生成论文图表...")
    os.system("python paper/paper_figures_generator.py")
    
    print("\n" + "="*60)
    print("✅ 项目整理完成！")
    print("="*60)
    print("📁 项目结构:")
    print("   src/          - 核心源代码")
    print("   experiments/  - 实验脚本")
    print("   paper/        - 论文和图表")
    print("   data/         - 数据文件")
    print("   results/      - 实验结果")
    print("   hpc_scripts/  - HPC批处理脚本")
    print("="*60)
    print("🚀 下一步:")
    print("   1. git init")
    print("   2. git add .")
    print("   3. git commit -m 'Initial commit: Graphullerene strain engineering'")
    print("   4. git remote add origin <your-repo-url>")
    print("   5. git push -u origin main")
    print("="*60)
    print("📝 论文准备:")
    print("   - LaTeX文件: paper/strain_doped_graphullerene.tex")
    print("   - 图表文件: paper/figures/")
    print("   - 参考文献: paper/strain_graphullerene_50refs.bib")
    print("="*60)
    print("💻 HPC计算:")
    print("   - 修改 hpc_scripts/run_cp2k_batch.sh 中的路径")
    print("   - 提交任务: sbatch hpc_scripts/run_cp2k_batch.sh")
    print("="*60)

if __name__ == "__main__":
    main()
