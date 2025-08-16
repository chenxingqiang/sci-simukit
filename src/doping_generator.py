#!/usr/bin/env python3
"""
杂原子掺杂结构生成器
基于您的graphullerene项目，生成B/N/P掺杂的富勒烯网络结构

作者: 基于您的项目经验
版本: 1.0
"""

import numpy as np
import os
import argparse
from ase import Atoms
from ase.io import read, write
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import logging
import random
from itertools import combinations

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DopingGenerator:
    """
    杂原子掺杂结构生成器
    基于您的富勒烯网络，系统性地生成B/N/P掺杂结构
    """

    def __init__(self, base_dir: str = "graphullerene"):
        """
        初始化掺杂生成器

        Args:
            base_dir: 基础结构文件目录
        """
        self.base_dir = Path(base_dir)
        self.output_dir = Path("doped_structures")
        self.output_dir.mkdir(exist_ok=True)

        # 掺杂元素配置
        self.dopants = {
            'B': {'atomic_number': 5, 'symbol': 'B'},
            'N': {'atomic_number': 7, 'symbol': 'N'},
            'P': {'atomic_number': 15, 'symbol': 'P'}
        }

        # 基于您项目中的结构文件
        self.base_structures = {
            'pristine_1': '1.xyz',
            'pristine_2': '2.xyz',
            'pristine_3': '3.xyz',
            'pristine_4': '4.xyz',
            'pristine_5': '5.xyz',
            'C60': 'C60.xyz'
        }

    def get_carbon_indices(self, atoms: Atoms) -> List[int]:
        """
        获取结构中所有碳原子的索引

        Args:
            atoms: ASE原子对象

        Returns:
            碳原子索引列表
        """
        carbon_indices = []
        for i, symbol in enumerate(atoms.get_chemical_symbols()):
            if symbol == 'C':
                carbon_indices.append(i)
        return carbon_indices

    def create_doped_structure(self,
                             atoms: Atoms,
                             dopant: str,
                             concentration: float,
                             doping_strategy: str = 'random') -> Atoms:
        """
        创建掺杂结构

        Args:
            atoms: 基础原子结构
            dopant: 掺杂元素 ('B', 'N', 'P')
            concentration: 掺杂浓度（百分比）
            doping_strategy: 掺杂策略 ('random', 'uniform', 'clustered')

        Returns:
            掺杂后的原子结构
        """
        doped_atoms = atoms.copy()
        carbon_indices = self.get_carbon_indices(atoms)

        # 计算需要掺杂的原子数量
        total_carbons = len(carbon_indices)
        n_dopants = max(1, int(total_carbons * concentration / 100.0))

        logger.info(f"总碳原子数: {total_carbons}, 掺杂原子数: {n_dopants} ({concentration:.1f}%)")

        # 选择掺杂位点
        if doping_strategy == 'random':
            doping_sites = random.sample(carbon_indices, n_dopants)
        elif doping_strategy == 'uniform':
            # 均匀分布掺杂
            step = total_carbons // n_dopants
            doping_sites = [carbon_indices[i * step] for i in range(n_dopants)]
        elif doping_strategy == 'clustered':
            # 团簇掺杂（选择邻近的原子）
            start_idx = random.choice(carbon_indices)
            doping_sites = self._get_clustered_sites(atoms, start_idx, n_dopants)
        else:
            raise ValueError(f"不支持的掺杂策略: {doping_strategy}")

        # 替换碳原子为掺杂原子
        symbols = doped_atoms.get_chemical_symbols()
        for site in doping_sites:
            symbols[site] = dopant

        doped_atoms.set_chemical_symbols(symbols)

        return doped_atoms

    def _get_clustered_sites(self, atoms: Atoms, start_idx: int, n_sites: int) -> List[int]:
        """
        获取团簇掺杂位点

        Args:
            atoms: 原子结构
            start_idx: 起始原子索引
            n_sites: 需要的位点数量

        Returns:
            团簇掺杂位点列表
        """
        from ase.neighborlist import NeighborList

        # 构建邻居列表
        cutoff = 2.0  # 键长截断距离
        nl = NeighborList([cutoff/2] * len(atoms), self_interaction=False, bothways=True)
        nl.update(atoms)

        clustered_sites = [start_idx]
        candidates = set([start_idx])

        while len(clustered_sites) < n_sites:
            # 扩展邻居
            new_candidates = set()
            for site in candidates:
                indices, _ = nl.get_neighbors(site)
                for idx in indices:
                    if atoms.get_chemical_symbols()[idx] == 'C' and idx not in clustered_sites:
                        new_candidates.add(idx)

            if not new_candidates:
                # 如果没有更多邻居，随机选择
                carbon_indices = self.get_carbon_indices(atoms)
                remaining = [i for i in carbon_indices if i not in clustered_sites]
                new_candidates = set(remaining[:n_sites - len(clustered_sites)])

            # 添加新位点
            needed = n_sites - len(clustered_sites)
            new_sites = list(new_candidates)[:needed]
            clustered_sites.extend(new_sites)
            candidates.update(new_sites)

        return clustered_sites[:n_sites]

    def create_mixed_doping(self,
                          atoms: Atoms,
                          dopant_config: Dict[str, float]) -> Atoms:
        """
        创建混合掺杂结构

        Args:
            atoms: 基础原子结构
            dopant_config: 掺杂配置 {'B': 2.5, 'N': 2.5} 表示B和N各掺杂2.5%

        Returns:
            混合掺杂结构
        """
        mixed_doped = atoms.copy()
        carbon_indices = self.get_carbon_indices(atoms)
        total_carbons = len(carbon_indices)

        used_sites = set()

        for dopant, concentration in dopant_config.items():
            n_dopants = max(1, int(total_carbons * concentration / 100.0))

            # 选择未使用的掺杂位点
            available_sites = [i for i in carbon_indices if i not in used_sites]
            if len(available_sites) < n_dopants:
                logger.warning(f"可用位点不足，{dopant}元素实际掺杂数量: {len(available_sites)}")
                n_dopants = len(available_sites)

            doping_sites = random.sample(available_sites, n_dopants)
            used_sites.update(doping_sites)

            # 替换原子
            symbols = mixed_doped.get_chemical_symbols()
            for site in doping_sites:
                symbols[site] = dopant
            mixed_doped.set_chemical_symbols(symbols)

            logger.info(f"{dopant}掺杂: {n_dopants}个原子 ({concentration:.1f}%)")

        return mixed_doped

    def generate_doping_series(self,
                             structure_name: str,
                             concentrations: List[float] = [2.5, 5.0, 7.5],
                             dopants: List[str] = ['B', 'N', 'P'],
                             strategies: List[str] = ['random'],
                             n_configs: int = 3) -> None:
        """
        生成掺杂系列结构

        Args:
            structure_name: 基础结构名称
            concentrations: 掺杂浓度列表
            dopants: 掺杂元素列表
            strategies: 掺杂策略列表
            n_configs: 每种配置生成的结构数量
        """

        if structure_name not in self.base_structures:
            logger.error(f"未找到结构: {structure_name}")
            return

        # 读取基础结构
        structure_file = self.base_dir / self.base_structures[structure_name]
        if not structure_file.exists():
            logger.error(f"结构文件不存在: {structure_file}")
            return

        logger.info(f"读取基础结构: {structure_file}")
        base_atoms = read(str(structure_file))

        # 为每种掺杂组合生成结构
        for dopant in dopants:
            for concentration in concentrations:
                for strategy in strategies:
                    # 创建输出目录
                    output_subdir = self.output_dir / f"{structure_name}_{dopant}_{concentration}percent_{strategy}"
                    output_subdir.mkdir(exist_ok=True)

                    logger.info(f"生成 {dopant} {concentration}% {strategy} 掺杂结构...")

                    for config_idx in range(n_configs):
                        # 生成掺杂结构
                        doped_atoms = self.create_doped_structure(
                            base_atoms, dopant, concentration, strategy
                        )

                        # 保存结构
                        output_file = output_subdir / f"{structure_name}_{dopant}_{concentration}p_{strategy}_{config_idx+1}.xyz"
                        write(str(output_file), doped_atoms)
                        logger.info(f"已生成: {output_file}")

    def generate_mixed_doping_series(self,
                                   structure_name: str,
                                   mixed_configs: List[Dict[str, float]] = None,
                                   n_configs: int = 3) -> None:
        """
        生成混合掺杂系列结构

        Args:
            structure_name: 基础结构名称
            mixed_configs: 混合掺杂配置列表
            n_configs: 每种配置生成的结构数量
        """

        if mixed_configs is None:
            # 默认混合掺杂配置
            mixed_configs = [
                {'B': 2.5, 'N': 2.5},  # B-N共掺杂
                {'B': 5.0, 'N': 2.5},  # B多N少
                {'B': 2.5, 'N': 5.0},  # N多B少
                {'B': 1.7, 'N': 1.7, 'P': 1.6},  # 三元共掺杂
            ]

        if structure_name not in self.base_structures:
            logger.error(f"未找到结构: {structure_name}")
            return

        # 读取基础结构
        structure_file = self.base_dir / self.base_structures[structure_name]
        base_atoms = read(str(structure_file))

        for config_idx, dopant_config in enumerate(mixed_configs):
            # 创建配置名称
            config_name = "_".join([f"{k}{v}" for k, v in dopant_config.items()])

            # 创建输出目录
            output_subdir = self.output_dir / f"{structure_name}_mixed_{config_name}"
            output_subdir.mkdir(exist_ok=True)

            logger.info(f"生成混合掺杂结构: {dopant_config}")

            for struct_idx in range(n_configs):
                # 生成混合掺杂结构
                mixed_doped = self.create_mixed_doping(base_atoms, dopant_config)

                # 保存结构
                output_file = output_subdir / f"{structure_name}_mixed_{config_name}_{struct_idx+1}.xyz"
                write(str(output_file), mixed_doped)
                logger.info(f"已生成: {output_file}")

    def generate_all_doped_structures(self,
                                    concentrations: List[float] = [2.5, 5.0, 7.5],
                                    include_mixed: bool = True) -> None:
        """
        基于您的所有基础结构生成完整的掺杂结构库
        """
        logger.info("开始生成所有掺杂结构...")

        dopants = ['B', 'N', 'P']
        strategies = ['random', 'uniform']  # 重点关注随机和均匀分布

        for structure_name in self.base_structures.keys():
            logger.info(f"\n处理结构: {structure_name}")

            # 生成单元素掺杂
            self.generate_doping_series(
                structure_name=structure_name,
                concentrations=concentrations,
                dopants=dopants,
                strategies=strategies,
                n_configs=3
            )

            # 生成混合掺杂
            if include_mixed:
                self.generate_mixed_doping_series(
                    structure_name=structure_name,
                    n_configs=3
                )

    def analyze_doping_effects(self) -> None:
        """
        分析掺杂效应统计
        """
        logger.info("分析掺杂效应...")

        analysis_file = self.output_dir / "doping_analysis.txt"
        with open(analysis_file, 'w') as f:
            f.write("富勒烯掺杂结构分析报告\n")
            f.write("=" * 50 + "\n\n")

            # 统计掺杂结构
            dopant_stats = {}
            total_structures = 0

            for doping_dir in self.output_dir.iterdir():
                if doping_dir.is_dir():
                    xyz_files = list(doping_dir.glob("*.xyz"))
                    count = len(xyz_files)
                    total_structures += count

                    # 解析掺杂类型
                    dir_name = doping_dir.name
                    if '_B_' in dir_name:
                        dopant_type = 'B'
                    elif '_N_' in dir_name:
                        dopant_type = 'N'
                    elif '_P_' in dir_name:
                        dopant_type = 'P'
                    elif '_mixed_' in dir_name:
                        dopant_type = 'Mixed'
                    else:
                        dopant_type = 'Unknown'

                    if dopant_type not in dopant_stats:
                        dopant_stats[dopant_type] = 0
                    dopant_stats[dopant_type] += count

                    f.write(f"{dir_name}: {count} 个结构\n")

            f.write(f"\n掺杂类型统计:\n")
            for dopant_type, count in dopant_stats.items():
                f.write(f"{dopant_type}: {count} 个结构\n")

            f.write(f"\n总计: {total_structures} 个掺杂结构\n")

            f.write(f"\n下一步实验流程:\n")
            f.write("1. 结合应变生成器生成应变+掺杂组合结构\n")
            f.write("2. 使用CP2K计算电子结构\n")
            f.write("3. 分析掺杂对带隙和迁移率的影响\n")
            f.write("4. 训练预测模型\n")

        logger.info(f"分析报告已保存至: {analysis_file}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='富勒烯杂原子掺杂结构生成器')
    parser.add_argument('--concentrations', nargs='+', type=float,
                       default=[2.5, 5.0, 7.5], help='掺杂浓度列表')
    parser.add_argument('--dopants', nargs='+', type=str,
                       default=['B', 'N', 'P'], help='掺杂元素列表')
    parser.add_argument('--structure', type=str,
                       help='指定结构名称（不指定则生成所有结构）')
    parser.add_argument('--base_dir', type=str, default='graphullerene',
                       help='基础结构文件目录')
    parser.add_argument('--include_mixed', action='store_true',
                       help='包含混合掺杂结构')
    parser.add_argument('--n_configs', type=int, default=3,
                       help='每种配置生成的结构数量')

    args = parser.parse_args()

    # 创建掺杂生成器
    generator = DopingGenerator(base_dir=args.base_dir)

    if args.structure:
        # 生成指定结构的掺杂系列
        generator.generate_doping_series(
            structure_name=args.structure,
            concentrations=args.concentrations,
            dopants=args.dopants,
            strategies=['random', 'uniform'],
            n_configs=args.n_configs
        )

        if args.include_mixed:
            generator.generate_mixed_doping_series(
                structure_name=args.structure,
                n_configs=args.n_configs
            )
    else:
        # 生成所有结构的掺杂系列
        generator.generate_all_doped_structures(
            concentrations=args.concentrations,
            include_mixed=args.include_mixed
        )

    # 生成分析报告
    generator.analyze_doping_effects()

    logger.info("掺杂结构生成完成！")

if __name__ == "__main__":
    main()
