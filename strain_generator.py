#!/usr/bin/env python3
"""
富勒烯应变结构生成器
基于您的graphullerene项目，生成不同应变下的结构

作者: 基于您的项目经验
版本: 1.0
"""

import numpy as np
import os
import argparse
from ase import Atoms
from ase.io import read, write
from pathlib import Path
from typing import List, Tuple, Optional
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StrainGenerator:
    """
    应变结构生成器
    基于您的graphullerene项目中的结构，生成不同应变下的变形结构
    """
    
    def __init__(self, base_dir: str = "graphullerene"):
        """
        初始化应变生成器
        
        Args:
            base_dir: 基础结构文件目录（您的graphullerene文件夹）
        """
        self.base_dir = Path(base_dir)
        self.output_dir = Path("strained_structures")
        self.output_dir.mkdir(exist_ok=True)
        
        # 基于您项目中的结构文件
        self.base_structures = {
            'pristine_1': '1.xyz',
            'pristine_2': '2.xyz', 
            'pristine_3': '3.xyz',
            'pristine_4': '4.xyz',
            'pristine_5': '5.xyz',
            'C60': 'C60.xyz'
        }
        
    def apply_strain(self, atoms: Atoms, strain_type: str, strain_value: float) -> Atoms:
        """
        对原子结构施加应变
        
        Args:
            atoms: ASE原子对象
            strain_type: 应变类型 ('biaxial', 'uniaxial_x', 'uniaxial_y', 'shear')
            strain_value: 应变值（百分比，如5表示5%应变）
        
        Returns:
            应变后的原子结构
        """
        strained_atoms = atoms.copy()
        cell = strained_atoms.get_cell()
        positions = strained_atoms.get_positions()
        
        # 应变张量
        strain_tensor = np.eye(3)
        strain_factor = 1.0 + strain_value / 100.0
        
        if strain_type == 'biaxial':
            # 双轴应变（x和y方向）
            strain_tensor[0, 0] = strain_factor
            strain_tensor[1, 1] = strain_factor
            
        elif strain_type == 'uniaxial_x':
            # x方向单轴应变
            strain_tensor[0, 0] = strain_factor
            
        elif strain_type == 'uniaxial_y':
            # y方向单轴应变
            strain_tensor[1, 1] = strain_factor
            
        elif strain_type == 'shear':
            # 剪切应变
            strain_tensor[0, 1] = strain_value / 100.0
            
        else:
            raise ValueError(f"不支持的应变类型: {strain_type}")
        
        # 应用应变到晶胞和原子坐标
        new_cell = np.dot(cell, strain_tensor)
        new_positions = np.dot(positions, strain_tensor)
        
        strained_atoms.set_cell(new_cell)
        strained_atoms.set_positions(new_positions)
        
        return strained_atoms
    
    def generate_strain_series(self, 
                             structure_name: str,
                             strain_range: Tuple[float, float] = (-5.0, 5.0),
                             strain_step: float = 1.0,
                             strain_types: List[str] = ['biaxial']) -> None:
        """
        生成应变系列结构
        
        Args:
            structure_name: 基础结构名称
            strain_range: 应变范围（最小值，最大值）
            strain_step: 应变步长
            strain_types: 应变类型列表
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
        
        # 生成应变值数组
        strain_min, strain_max = strain_range
        strain_values = np.arange(strain_min, strain_max + strain_step, strain_step)
        
        for strain_type in strain_types:
            strain_dir = self.output_dir / f"{structure_name}_{strain_type}"
            strain_dir.mkdir(exist_ok=True)
            
            logger.info(f"生成 {strain_type} 应变结构...")
            
            for strain_value in strain_values:
                # 应用应变
                strained_atoms = self.apply_strain(base_atoms, strain_type, strain_value)
                
                # 生成输出文件名
                strain_str = f"{strain_value:+.1f}".replace('.', 'p').replace('-', 'm').replace('+', 'p')
                output_file = strain_dir / f"{structure_name}_{strain_type}_{strain_str}percent.xyz"
                
                # 写入文件
                write(str(output_file), strained_atoms)
                logger.info(f"已生成: {output_file}")
    
    def generate_all_strain_structures(self,
                                     strain_range: Tuple[float, float] = (-5.0, 5.0),
                                     strain_step: float = 1.0) -> None:
        """
        基于您的所有基础结构生成应变系列
        """
        logger.info("开始生成所有应变结构...")
        
        # 应变类型（重点关注双轴应变，这是论文中的主要内容）
        strain_types = ['biaxial', 'uniaxial_x', 'uniaxial_y']
        
        for structure_name in self.base_structures.keys():
            logger.info(f"\n处理结构: {structure_name}")
            self.generate_strain_series(
                structure_name=structure_name,
                strain_range=strain_range,
                strain_step=strain_step,
                strain_types=strain_types
            )
    
    def analyze_strain_effects(self) -> None:
        """
        分析应变效应（可用于后续数据分析）
        """
        logger.info("分析应变效应...")
        
        analysis_file = self.output_dir / "strain_analysis.txt"
        with open(analysis_file, 'w') as f:
            f.write("富勒烯应变结构分析报告\n")
            f.write("=" * 50 + "\n\n")
            
            # 统计生成的结构数量
            total_structures = 0
            for strain_dir in self.output_dir.iterdir():
                if strain_dir.is_dir():
                    xyz_files = list(strain_dir.glob("*.xyz"))
                    count = len(xyz_files)
                    total_structures += count
                    f.write(f"{strain_dir.name}: {count} 个结构\n")
            
            f.write(f"\n总计: {total_structures} 个应变结构\n")
            f.write("\n建议后续步骤:\n")
            f.write("1. 使用CP2K进行DFT计算\n")
            f.write("2. 分析电子结构变化\n")
            f.write("3. 计算电子迁移率\n")
            f.write("4. 训练机器学习模型\n")
        
        logger.info(f"分析报告已保存至: {analysis_file}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='富勒烯应变结构生成器')
    parser.add_argument('--strain_range', nargs=2, type=float, 
                       default=[-5.0, 5.0], help='应变范围 (最小值 最大值)')
    parser.add_argument('--strain_step', type=float, default=1.0, 
                       help='应变步长')
    parser.add_argument('--structure', type=str, 
                       help='指定结构名称（不指定则生成所有结构）')
    parser.add_argument('--base_dir', type=str, default='graphullerene',
                       help='基础结构文件目录')
    
    args = parser.parse_args()
    
    # 创建应变生成器
    generator = StrainGenerator(base_dir=args.base_dir)
    
    if args.structure:
        # 生成指定结构的应变系列
        generator.generate_strain_series(
            structure_name=args.structure,
            strain_range=tuple(args.strain_range),
            strain_step=args.strain_step,
            strain_types=['biaxial', 'uniaxial_x', 'uniaxial_y']
        )
    else:
        # 生成所有结构的应变系列
        generator.generate_all_strain_structures(
            strain_range=tuple(args.strain_range),
            strain_step=args.strain_step
        )
    
    # 生成分析报告
    generator.analyze_strain_effects()
    
    logger.info("应变结构生成完成！")

if __name__ == "__main__":
    main()
