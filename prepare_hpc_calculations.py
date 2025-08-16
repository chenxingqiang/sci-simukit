#!/usr/bin/env python3
"""
高性能计算准备脚本
为HPC集群准备CP2K计算任务

作者: 基于您的项目经验
版本: 1.0
"""

import os
import shutil
from pathlib import Path
import json
import logging
import argparse

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HPCPreparation:
    """
    HPC计算准备类
    """
    
    def __init__(self, structure_dir: str = "data/strain_doped_structures",
                 output_dir: str = "hpc_calculations"):
        """
        初始化HPC准备
        
        Args:
            structure_dir: 结构文件目录
            output_dir: HPC计算输出目录
        """
        self.structure_dir = Path(structure_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # CP2K模板文件
        self.template_dir = Path("graphullerene")
        
    def prepare_cp2k_inputs(self):
        """准备所有CP2K输入文件"""
        logger.info("开始准备CP2K输入文件...")
        
        # 读取元数据
        metadata_file = self.structure_dir / "dataset_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        else:
            logger.error("未找到数据集元数据文件")
            return
        
        # 为每个结构创建CP2K输入
        batch_count = 0
        batch_size = 10  # 每批10个计算
        current_batch = []
        
        for xyz_path, meta in metadata.items():
            # 跳过非C60结构（暂时）
            if 'C60' not in xyz_path:
                continue
                
            # 生成输入文件名
            xyz_file = Path(xyz_path)
            if not xyz_file.exists():
                # 尝试相对路径
                xyz_file = self.structure_dir / xyz_file.name
                if not xyz_file.exists():
                    logger.warning(f"未找到结构文件: {xyz_path}")
                    continue
            
            inp_name = xyz_file.stem + ".inp"
            
            # 选择合适的模板
            if meta.get('strain_value', 0) != 0:
                template_name = "hybrid-vdw-cell-opt.inp"
            else:
                template_name = "alpha-30-probe.inp"
            
            # 创建输入文件
            self._create_cp2k_input(xyz_file, inp_name, template_name, meta)
            
            current_batch.append(inp_name)
            
            # 达到批量大小，创建批处理脚本
            if len(current_batch) >= batch_size:
                batch_count += 1
                self._create_batch_script(batch_count, current_batch)
                current_batch = []
        
        # 处理剩余的计算
        if current_batch:
            batch_count += 1
            self._create_batch_script(batch_count, current_batch)
        
        logger.info(f"创建了 {batch_count} 个批处理任务")
        
        # 创建主控脚本
        self._create_master_script(batch_count)
    
    def _create_cp2k_input(self, xyz_file: Path, inp_name: str, 
                          template_name: str, metadata: dict):
        """
        创建单个CP2K输入文件
        
        Args:
            xyz_file: XYZ结构文件
            inp_name: 输入文件名
            template_name: 模板文件名
            metadata: 结构元数据
        """
        # 读取模板
        template_path = self.template_dir / template_name
        if not template_path.exists():
            logger.error(f"模板文件不存在: {template_path}")
            return
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # 替换参数
        content = template_content
        
        # 项目名称
        project_name = xyz_file.stem.replace('.', '_')
        content = content.replace("PROJECT el", f"PROJECT {project_name}")
        
        # 结构文件路径
        relative_xyz = f"../structures/{xyz_file.name}"
        content = content.replace("COORD_FILE_NAME   ./C60.xyz", 
                                f"COORD_FILE_NAME   {relative_xyz}")
        
        # 根据应变调整晶胞参数（如果需要）
        strain = metadata.get('strain_value', 0.0)
        if strain != 0:
            # 假设原始晶胞为30 Å
            cell_size = 30.0 * (1 + strain/100.0)
            content = content.replace("ABC 30.0 30.0 30.0", 
                                    f"ABC {cell_size:.2f} {cell_size:.2f} {cell_size:.2f}")
        
        # 写入输入文件
        inp_path = self.output_dir / "inputs" / inp_name
        inp_path.parent.mkdir(exist_ok=True)
        
        with open(inp_path, 'w') as f:
            f.write(content)
        
        # 复制结构文件
        struct_dir = self.output_dir / "structures"
        struct_dir.mkdir(exist_ok=True)
        shutil.copy2(xyz_file, struct_dir / xyz_file.name)
    
    def _create_batch_script(self, batch_id: int, inp_files: list):
        """
        创建批处理脚本
        
        Args:
            batch_id: 批次ID
            inp_files: 输入文件列表
        """
        script_content = f"""#!/bin/bash
#SBATCH --job-name=graphullerene_batch{batch_id}
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --time=24:00:00
#SBATCH --partition=gpu
#SBATCH --output=batch{batch_id}-%j.out
#SBATCH --error=batch{batch_id}-%j.err

# 加载模块
module load cp2k/2025.2
module load python/3.9

# 设置环境
export OMP_NUM_THREADS=1
export CP2K_DATA_DIR=$CP2K_HOME/data

# 进入工作目录
cd $SLURM_SUBMIT_DIR

echo "开始批次 {batch_id} - $(date)"

# 运行计算
"""
        
        for inp_file in inp_files:
            base_name = Path(inp_file).stem
            script_content += f"""
echo "运行: {inp_file}"
mpirun -np $SLURM_NTASKS cp2k.popt -i inputs/{inp_file} -o outputs/{base_name}.out
"""
        
        script_content += f"""
echo "批次 {batch_id} 完成 - $(date)"

# 收集能量数据
python scripts/extract_energies.py --batch {batch_id}
"""
        
        # 保存脚本
        script_path = self.output_dir / "batch_scripts" / f"batch_{batch_id}.sh"
        script_path.parent.mkdir(exist_ok=True)
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
    
    def _create_master_script(self, total_batches: int):
        """
        创建主控脚本
        
        Args:
            total_batches: 总批次数
        """
        master_script = f"""#!/bin/bash
# 主控脚本 - 提交所有批次

echo "提交 {total_batches} 个批次的计算任务"

# 提交所有批次
"""
        
        for i in range(1, total_batches + 1):
            master_script += f"""
echo "提交批次 {i}"
JOB_ID_{i}=$(sbatch --parsable batch_scripts/batch_{i}.sh)
echo "批次 {i} 任务ID: $JOB_ID_{i}"
"""
        
        master_script += """
# 等待所有任务完成
echo "等待所有任务完成..."

# 创建依赖任务收集结果
sbatch --dependency=afterok:$(echo $JOB_ID_* | tr ' ' ':') scripts/collect_all_results.sh

echo "所有任务已提交"
"""
        
        master_path = self.output_dir / "submit_all.sh"
        with open(master_path, 'w') as f:
            f.write(master_script)
        
        os.chmod(master_path, 0o755)
        
        # 创建结果收集脚本
        self._create_collection_scripts()
    
    def _create_collection_scripts(self):
        """创建结果收集脚本"""
        
        # 能量提取脚本
        extract_script = '''#!/usr/bin/env python3
"""提取CP2K计算能量"""

import sys
import re
from pathlib import Path
import pandas as pd
import argparse

def extract_energy(output_file):
    """从CP2K输出文件提取总能量"""
    energy = None
    
    with open(output_file, 'r') as f:
        for line in f:
            if "ENERGY| Total FORCE_EVAL" in line:
                match = re.search(r'(-?\d+\.\d+)', line)
                if match:
                    energy = float(match.group(1))
    
    return energy

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', type=int, help='批次号')
    args = parser.parse_args()
    
    results = []
    output_dir = Path('outputs')
    
    for out_file in output_dir.glob('*.out'):
        energy = extract_energy(out_file)
        if energy:
            results.append({
                'structure': out_file.stem,
                'total_energy': energy
            })
    
    # 保存结果
    df = pd.DataFrame(results)
    if args.batch:
        df.to_csv(f'batch_{args.batch}_energies.csv', index=False)
    else:
        df.to_csv('all_energies.csv', index=False)
    
    print(f"提取了 {len(results)} 个能量值")

if __name__ == "__main__":
    main()
'''
        
        script_dir = self.output_dir / "scripts"
        script_dir.mkdir(exist_ok=True)
        
        with open(script_dir / "extract_energies.py", 'w') as f:
            f.write(extract_script)
        
        # 最终收集脚本
        collect_script = '''#!/bin/bash
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
'''
        
        with open(script_dir / "collect_all_results.sh", 'w') as f:
            f.write(collect_script)
        
        os.chmod(script_dir / "collect_all_results.sh", 0o755)
    
    def create_analysis_scripts(self):
        """创建分析脚本"""
        
        merge_script = '''#!/usr/bin/env python3
"""合并所有批次结果"""

import pandas as pd
from pathlib import Path
import json

# 读取元数据
with open('../data/strain_doped_structures/dataset_metadata.json', 'r') as f:
    metadata = json.load(f)

# 合并所有能量文件
all_results = []
for csv_file in Path('.').glob('batch_*_energies.csv'):
    df = pd.read_csv(csv_file)
    all_results.append(df)

if all_results:
    combined_df = pd.concat(all_results, ignore_index=True)
    
    # 添加元数据信息
    for idx, row in combined_df.iterrows():
        struct_name = row['structure']
        # 查找对应的元数据
        for path, meta in metadata.items():
            if struct_name in path:
                combined_df.at[idx, 'strain'] = meta.get('strain_value', 0)
                combined_df.at[idx, 'doping_type'] = meta.get('doping_type', 'pristine')
                if meta.get('doping_type') == 'single':
                    combined_df.at[idx, 'dopant'] = meta.get('dopant', '')
                    combined_df.at[idx, 'concentration'] = meta.get('concentration', 0)
                break
    
    # 保存最终结果
    combined_df.to_csv('final_dft_results.csv', index=False)
    print(f"合并了 {len(combined_df)} 个计算结果")
else:
    print("未找到任何结果文件")
'''
        
        report_script = '''#!/usr/bin/env python3
"""生成HPC计算报告"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 读取结果
df = pd.read_csv('final_dft_results.csv')

# 生成报告
with open('hpc_calculation_report.md', 'w') as f:
    f.write("# HPC DFT计算结果报告\\n\\n")
    f.write(f"## 总览\\n")
    f.write(f"- 完成计算: {len(df)} 个结构\\n")
    f.write(f"- 应变范围: {df['strain'].min():.1f}% 到 {df['strain'].max():.1f}%\\n")
    f.write(f"- 掺杂类型: {df['doping_type'].unique().tolist()}\\n\\n")
    
    f.write("## 能量分析\\n")
    
    # 按应变分组
    strain_groups = df.groupby('strain')['total_energy'].mean()
    f.write(f"### 应变效应\\n")
    for strain, energy in strain_groups.items():
        f.write(f"- {strain:+.1f}%: {energy:.4f} Ha\\n")
    
    f.write("\\n### 掺杂效应\\n")
    doping_groups = df.groupby('doping_type')['total_energy'].mean()
    for doping, energy in doping_groups.items():
        f.write(f"- {doping}: {energy:.4f} Ha\\n")

# 绘制能量图
plt.figure(figsize=(10, 6))
for doping_type in df['doping_type'].unique():
    data = df[df['doping_type'] == doping_type]
    plt.scatter(data['strain'], data['total_energy'], label=doping_type, alpha=0.7)

plt.xlabel('Strain (%)')
plt.ylabel('Total Energy (Ha)')
plt.title('DFT Total Energy vs Strain')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('energy_vs_strain.png', dpi=300, bbox_inches='tight')
plt.close()

print("报告生成完成: hpc_calculation_report.md")
'''
        
        script_dir = self.output_dir / "scripts"
        
        with open(script_dir / "merge_all_results.py", 'w') as f:
            f.write(merge_script)
        
        with open(script_dir / "generate_hpc_report.py", 'w') as f:
            f.write(report_script)
    
    def prepare_full_package(self):
        """准备完整的HPC计算包"""
        logger.info("准备完整HPC计算包...")
        
        # 1. 准备CP2K输入
        self.prepare_cp2k_inputs()
        
        # 2. 创建分析脚本
        self.create_analysis_scripts()
        
        # 3. 创建README
        self._create_readme()
        
        # 4. 创建目录结构
        dirs_to_create = ['outputs', 'logs', 'results']
        for dir_name in dirs_to_create:
            (self.output_dir / dir_name).mkdir(exist_ok=True)
        
        # 5. 打包
        self._create_tarball()
        
        logger.info("HPC计算包准备完成！")
    
    def _create_readme(self):
        """创建README文件"""
        readme_content = """# Graphullerene HPC计算包

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
"""
        
        with open(self.output_dir / "README.md", 'w') as f:
            f.write(readme_content)
    
    def _create_tarball(self):
        """创建压缩包"""
        import tarfile
        
        tar_name = "graphullerene_hpc.tar.gz"
        logger.info(f"创建压缩包: {tar_name}")
        
        with tarfile.open(tar_name, "w:gz") as tar:
            tar.add(self.output_dir, arcname="hpc_calculations")
        
        logger.info(f"压缩包创建完成: {tar_name}")
        
        # 计算大小
        size_mb = os.path.getsize(tar_name) / (1024 * 1024)
        logger.info(f"文件大小: {size_mb:.2f} MB")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='准备HPC计算')
    parser.add_argument('--structure_dir', type=str, 
                       default='data/strain_doped_structures',
                       help='结构文件目录')
    parser.add_argument('--output_dir', type=str,
                       default='hpc_calculations',
                       help='输出目录')
    
    args = parser.parse_args()
    
    # 创建HPC准备器
    prep = HPCPreparation(args.structure_dir, args.output_dir)
    
    # 准备完整包
    prep.prepare_full_package()
    
    print("\n" + "="*60)
    print("✅ HPC计算准备完成！")
    print("="*60)
    print("📦 压缩包: graphullerene_hpc.tar.gz")
    print("📁 目录: hpc_calculations/")
    print("🚀 使用方法:")
    print("   1. scp graphullerene_hpc.tar.gz cluster:~/")
    print("   2. ssh cluster")
    print("   3. tar -xzf graphullerene_hpc.tar.gz")
    print("   4. cd hpc_calculations")
    print("   5. ./submit_all.sh")
    print("="*60)
    print("💡 提示:")
    print("   - 检查批处理脚本中的队列参数")
    print("   - 确认CP2K模块加载命令")
    print("   - 根据集群配置调整资源分配")
    print("="*60)

if __name__ == "__main__":
    main()
