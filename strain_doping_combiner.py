#!/usr/bin/env python3
"""
应变+掺杂组合结构生成器
将应变工程与杂原子掺杂结合，生成用于机器学习训练的完整数据集

作者: 基于您的项目经验
版本: 1.0
"""

import numpy as np
import os
import argparse
from ase import Atoms
from ase.io import read, write
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import logging
import itertools
import json
from strain_generator import StrainGenerator
from doping_generator import DopingGenerator

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StrainDopingCombiner:
    """
    应变+掺杂组合生成器
    生成论文中需要的完整参数空间结构
    """

    def __init__(self, base_dir: str = "graphullerene"):
        """
        初始化组合生成器

        Args:
            base_dir: 基础结构文件目录
        """
        self.base_dir = Path(base_dir)
        self.output_dir = Path("strain_doped_structures")
        self.output_dir.mkdir(exist_ok=True)

        # 初始化子生成器
        self.strain_gen = StrainGenerator(base_dir)
        self.doping_gen = DopingGenerator(base_dir)

        # 实验参数空间（基于论文设计）
        self.parameter_space = {
            'structures': ['C60', 'pristine_1', 'pristine_2'],  # 重点结构
            'strain_types': ['biaxial'],  # 论文重点关注双轴应变
            'strain_values': [-5.0, -2.5, 0.0, 2.5, 5.0],  # 应变范围
            'dopants': ['B', 'N', 'P'],
            'doping_concentrations': [2.5, 5.0, 7.5],
            'mixed_doping': [
                {'B': 2.5, 'N': 2.5},
                {'B': 5.0, 'N': 2.5},
                {'B': 2.5, 'N': 5.0}
            ]
        }

        self.metadata = {}  # 存储生成结构的元数据

    def generate_strained_doped_structure(self,
                                        base_atoms: Atoms,
                                        strain_type: str,
                                        strain_value: float,
                                        doping_config: Dict) -> Atoms:
        """
        生成单个应变+掺杂组合结构

        Args:
            base_atoms: 基础原子结构
            strain_type: 应变类型
            strain_value: 应变值
            doping_config: 掺杂配置 {'type': 'single', 'dopant': 'B', 'concentration': 5.0}
                         或 {'type': 'mixed', 'dopants': {'B': 2.5, 'N': 2.5}}

        Returns:
            应变+掺杂结构
        """
        # 首先应用应变
        strained_atoms = self.strain_gen.apply_strain(base_atoms, strain_type, strain_value)

        # 然后应用掺杂
        if doping_config['type'] == 'single':
            final_atoms = self.doping_gen.create_doped_structure(
                strained_atoms,
                doping_config['dopant'],
                doping_config['concentration'],
                doping_strategy='random'
            )
        elif doping_config['type'] == 'mixed':
            final_atoms = self.doping_gen.create_mixed_doping(
                strained_atoms,
                doping_config['dopants']
            )
        else:
            raise ValueError(f"不支持的掺杂类型: {doping_config['type']}")

        return final_atoms

    def generate_systematic_dataset(self,
                                  structures: List[str] = None,
                                  strain_range: Tuple[float, float] = (-5.0, 5.0),
                                  n_configs_per_combo: int = 2) -> None:
        """
        系统性生成训练数据集

        Args:
            structures: 要处理的结构列表
            strain_range: 应变范围
            n_configs_per_combo: 每种组合生成的配置数量
        """

        if structures is None:
            structures = self.parameter_space['structures']

        logger.info("开始生成系统性应变+掺杂数据集...")
        logger.info(f"结构数量: {len(structures)}")
        logger.info(f"应变范围: {strain_range}")

        total_combinations = 0
        generated_count = 0

        for structure_name in structures:
            if structure_name not in self.strain_gen.base_structures:
                logger.warning(f"跳过未知结构: {structure_name}")
                continue

            # 读取基础结构
            structure_file = self.base_dir / self.strain_gen.base_structures[structure_name]
            if not structure_file.exists():
                logger.error(f"结构文件不存在: {structure_file}")
                continue

            base_atoms = read(str(structure_file))
            logger.info(f"\n处理结构: {structure_name}")

            # 创建结构专用输出目录
            struct_output_dir = self.output_dir / structure_name
            struct_output_dir.mkdir(exist_ok=True)

            # 遍历应变值
            for strain_value in self.parameter_space['strain_values']:
                if not (strain_range[0] <= strain_value <= strain_range[1]):
                    continue

                # 1. pristine应变结构
                strain_config = {
                    'structure': structure_name,
                    'strain_type': 'biaxial',
                    'strain_value': strain_value,
                    'doping': 'pristine'
                }

                strained_atoms = self.strain_gen.apply_strain(
                    base_atoms, 'biaxial', strain_value
                )

                output_file = struct_output_dir / f"{structure_name}_strain_{strain_value:+.1f}_pristine.xyz"
                write(str(output_file), strained_atoms)

                self.metadata[str(output_file)] = strain_config
                generated_count += 1
                total_combinations += 1

                # 2. 单元素掺杂 + 应变
                for dopant in self.parameter_space['dopants']:
                    for concentration in self.parameter_space['doping_concentrations']:
                        for config_idx in range(n_configs_per_combo):

                            doping_config = {
                                'type': 'single',
                                'dopant': dopant,
                                'concentration': concentration
                            }

                            # 生成应变+掺杂结构
                            final_atoms = self.generate_strained_doped_structure(
                                base_atoms, 'biaxial', strain_value, doping_config
                            )

                            # 保存结构
                            strain_str = f"{strain_value:+.1f}".replace('.', 'p').replace('-', 'm').replace('+', 'p')
                            output_file = struct_output_dir / f"{structure_name}_strain_{strain_str}_{dopant}_{concentration}p_config{config_idx+1}.xyz"
                            write(str(output_file), final_atoms)

                            # 保存元数据
                            metadata_entry = {
                                'structure': structure_name,
                                'strain_type': 'biaxial',
                                'strain_value': strain_value,
                                'doping_type': 'single',
                                'dopant': dopant,
                                'concentration': concentration,
                                'config_index': config_idx + 1
                            }
                            self.metadata[str(output_file)] = metadata_entry
                            generated_count += 1
                            total_combinations += 1

                # 3. 混合掺杂 + 应变
                for mixed_config in self.parameter_space['mixed_doping']:
                    for config_idx in range(n_configs_per_combo):

                        doping_config = {
                            'type': 'mixed',
                            'dopants': mixed_config
                        }

                        # 生成应变+混合掺杂结构
                        final_atoms = self.generate_strained_doped_structure(
                            base_atoms, 'biaxial', strain_value, doping_config
                        )

                        # 生成文件名
                        mixed_name = "_".join([f"{k}{v}" for k, v in mixed_config.items()])
                        strain_str = f"{strain_value:+.1f}".replace('.', 'p').replace('-', 'm').replace('+', 'p')
                        output_file = struct_output_dir / f"{structure_name}_strain_{strain_str}_mixed_{mixed_name}_config{config_idx+1}.xyz"
                        write(str(output_file), final_atoms)

                        # 保存元数据
                        metadata_entry = {
                            'structure': structure_name,
                            'strain_type': 'biaxial',
                            'strain_value': strain_value,
                            'doping_type': 'mixed',
                            'dopants': mixed_config,
                            'config_index': config_idx + 1
                        }
                        self.metadata[str(output_file)] = metadata_entry
                        generated_count += 1
                        total_combinations += 1

            logger.info(f"{structure_name} 完成: {generated_count} 个结构")

        logger.info(f"\n数据集生成完成！")
        logger.info(f"总计: {generated_count} 个结构")

        # 保存元数据
        self.save_metadata()

    def save_metadata(self) -> None:
        """保存生成结构的元数据"""
        metadata_file = self.output_dir / "dataset_metadata.json"

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)

        logger.info(f"元数据已保存至: {metadata_file}")

        # 生成统计报告
        self.generate_dataset_report()

    def generate_dataset_report(self) -> None:
        """生成数据集统计报告"""
        report_file = self.output_dir / "dataset_report.txt"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("富勒烯应变+掺杂数据集报告\n")
            f.write("=" * 60 + "\n\n")

            # 基本统计
            total_structures = len(self.metadata)
            f.write(f"总结构数量: {total_structures}\n\n")

            # 按结构分类统计
            structure_stats = {}
            strain_stats = {}
            doping_stats = {}

            for file_path, meta in self.metadata.items():
                struct = meta['structure']
                strain = meta['strain_value']
                doping = meta.get('doping', meta.get('doping_type', 'unknown'))

                structure_stats[struct] = structure_stats.get(struct, 0) + 1
                strain_stats[strain] = strain_stats.get(strain, 0) + 1
                doping_stats[doping] = doping_stats.get(doping, 0) + 1

            f.write("按基础结构统计:\n")
            for struct, count in sorted(structure_stats.items()):
                f.write(f"  {struct}: {count} 个结构\n")

            f.write(f"\n按应变值统计:\n")
            for strain, count in sorted(strain_stats.items()):
                f.write(f"  {strain:+.1f}%: {count} 个结构\n")

            f.write(f"\n按掺杂类型统计:\n")
            for doping, count in sorted(doping_stats.items()):
                f.write(f"  {doping}: {count} 个结构\n")

            f.write(f"\n数据集用途:\n")
            f.write("1. DFT高通量计算输入\n")
            f.write("2. 机器学习训练数据\n")
            f.write("3. 性质-结构关系分析\n")
            f.write("4. 最优材料参数预测\n")

            f.write(f"\n推荐计算流程:\n")
            f.write("1. CP2K几何优化 → 稳定结构\n")
            f.write("2. 电子结构计算 → 带隙、DOS\n")
            f.write("3. 输运性质计算 → 电子迁移率\n")
            f.write("4. GNN模型训练 → 性质预测\n")

        logger.info(f"数据集报告已保存至: {report_file}")

    def create_cp2k_input_templates(self) -> None:
        """
        基于您的模板创建CP2K输入文件
        """
        logger.info("创建CP2K输入文件模板...")

        cp2k_dir = self.output_dir / "cp2k_inputs"
        cp2k_dir.mkdir(exist_ok=True)

        # 读取您的模板文件
        template_files = [
            "hybrid-vdw-cell-opt.inp",
            "C60-hole-fixed-environment.inp"
        ]

        for template_name in template_files:
            template_path = self.base_dir / template_name
            if template_path.exists():
                # 复制并修改模板
                template_content = template_path.read_text()

                # 为批量计算修改模板
                modified_template = template_content.replace(
                    "PROJECT el", "PROJECT strain_doped"
                ).replace(
                    "COORD_FILE_NAME   ./C60.xyz", "COORD_FILE_NAME   STRUCTURE_FILE_PLACEHOLDER"
                )

                output_template = cp2k_dir / f"template_{template_name}"
                output_template.write_text(modified_template)

                logger.info(f"已创建模板: {output_template}")

    def generate_quick_test_dataset(self) -> None:
        """
        生成用于快速测试的小数据集
        """
        logger.info("生成快速测试数据集...")

        # 减少参数空间用于测试
        test_params = {
            'structures': ['C60'],
            'strain_values': [-2.5, 0.0, 2.5],
            'dopants': ['B', 'N'],
            'concentrations': [5.0]
        }

        self.generate_systematic_dataset(
            structures=test_params['structures'],
            strain_range=(-5.0, 5.0),
            n_configs_per_combo=1
        )

        logger.info("快速测试数据集生成完成！")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='应变+掺杂组合结构生成器')
    parser.add_argument('--structures', nargs='+', type=str,
                       help='指定结构列表')
    parser.add_argument('--strain_range', nargs=2, type=float,
                       default=[-5.0, 5.0], help='应变范围')
    parser.add_argument('--base_dir', type=str, default='graphullerene',
                       help='基础结构文件目录')
    parser.add_argument('--quick_test', action='store_true',
                       help='生成快速测试数据集')
    parser.add_argument('--n_configs', type=int, default=2,
                       help='每种组合的配置数量')
    parser.add_argument('--create_cp2k_templates', action='store_true',
                       help='创建CP2K输入文件模板')

    args = parser.parse_args()

    # 创建组合生成器
    combiner = StrainDopingCombiner(base_dir=args.base_dir)

    if args.quick_test:
        # 快速测试模式
        combiner.generate_quick_test_dataset()
    else:
        # 完整数据集生成
        combiner.generate_systematic_dataset(
            structures=args.structures,
            strain_range=tuple(args.strain_range),
            n_configs_per_combo=args.n_configs
        )

    if args.create_cp2k_templates:
        combiner.create_cp2k_input_templates()

    logger.info("所有任务完成！")

if __name__ == "__main__":
    main()
