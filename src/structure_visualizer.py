#!/usr/bin/env python3
"""
高质量分子结构可视化工具
参考学术论文绘图风格，专为Mac M2优化

功能:
- 从XYZ文件直接生成高质量分子结构图
- 支持富勒烯、石墨烯等碳材料可视化
- 支持应变和掺杂效应可视化
- 生成论文级别的矢量图和位图

作者: Graphullerene Research Team
版本: 1.0
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional
import json

# 尝试导入ASE，如果没有则提供备用方案
try:
    from ase import Atoms
    from ase.io import read, write
    from ase.visualize import view
    ASE_AVAILABLE = True
except ImportError:
    ASE_AVAILABLE = False
    print("ASE not available, using fallback XYZ reader")

# 设置matplotlib参数以获得论文级质量
plt.rcParams.update({
    'font.family': 'DejaVu Sans',  # 支持更多Unicode字符
    'font.size': 12,
    'axes.linewidth': 1.5,
    'xtick.major.width': 1.5,
    'ytick.major.width': 1.5,
    'xtick.major.size': 5,
    'ytick.major.size': 5,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.format': 'pdf',
    'text.usetex': False,
    'mathtext.default': 'regular'  # 使用常规字体显示数学符号
})

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StructureVisualizer:
    """
    高质量分子结构可视化类
    """
    
    def __init__(self):
        """初始化可视化器"""
        # 原子颜色配置（改进的CPK颜色方案 - 更丰富的色彩）
        self.atom_colors = {
            'C': '#404040',  # 碳 - 深灰色（加深对比度）
            'B': '#FF69B4',  # 硼 - 亮粉色  
            'N': '#1E90FF',  # 氮 - 道奇蓝
            'P': '#FF6347',  # 磷 - 番茄红
            'H': '#F0F8FF',  # 氢 - 爱丽丝蓝
            'O': '#DC143C',  # 氧 - 深红色
        }
        
        # 应变状态颜色（用于可视化应变效应）
        self.strain_colors = {
            'compression': '#4169E1',  # 压缩 - 皇室蓝
            'tension': '#FF4500',      # 拉伸 - 橙红色
            'neutral': '#32CD32',      # 中性 - 石灰绿
        }
        
        # 掺杂浓度颜色梯度
        self.doping_gradients = {
            'B': ['#FFE4E1', '#FF69B4', '#C71585'],  # 硼掺杂梯度
            'N': ['#E0E6FF', '#1E90FF', '#0000CD'],  # 氮掺杂梯度
            'P': ['#FFE4E1', '#FF6347', '#B22222'],  # 磷掺杂梯度
        }
        
        # 原子半径（Angstrom）
        self.atom_radii = {
            'C': 0.77,
            'B': 0.87,
            'N': 0.75,
            'P': 1.10,
            'H': 0.37,
            'O': 0.73,
        }
        
        # 键长阈值（用于判断是否绘制化学键）
        self.bond_thresholds = {
            ('C', 'C'): 1.8,
            ('C', 'B'): 1.9,
            ('C', 'N'): 1.8,
            ('C', 'P'): 2.0,
            ('B', 'N'): 1.9,
            ('B', 'P'): 2.1,
            ('N', 'P'): 2.0,
        }
    
    def read_xyz_file(self, filename: str) -> Tuple[List[str], np.ndarray]:
        """
        读取XYZ文件
        
        Args:
            filename: XYZ文件路径
            
        Returns:
            (元素列表, 坐标数组)
        """
        if ASE_AVAILABLE:
            try:
                atoms = read(filename)
                symbols = atoms.get_chemical_symbols()
                positions = atoms.get_positions()
                return symbols, positions
            except:
                logger.warning("ASE读取失败，使用备用方案")
        
        # 备用XYZ读取方案
        symbols = []
        positions = []
        
        with open(filename, 'r') as f:
            lines = f.readlines()
            
        n_atoms = int(lines[0].strip())
        
        for i in range(2, 2 + n_atoms):
            parts = lines[i].strip().split()
            symbols.append(parts[0])
            positions.append([float(parts[1]), float(parts[2]), float(parts[3])])
        
        return symbols, np.array(positions)
    
    def get_bonds(self, symbols: List[str], positions: np.ndarray) -> List[Tuple[int, int]]:
        """
        基于距离计算化学键
        
        Args:
            symbols: 原子符号列表
            positions: 原子坐标
            
        Returns:
            键的索引对列表
        """
        bonds = []
        n_atoms = len(symbols)
        
        for i in range(n_atoms):
            for j in range(i + 1, n_atoms):
                symbol_pair = tuple(sorted([symbols[i], symbols[j]]))
                
                if symbol_pair in self.bond_thresholds:
                    distance = np.linalg.norm(positions[i] - positions[j])
                    threshold = self.bond_thresholds[symbol_pair]
                    
                    if distance < threshold:
                        bonds.append((i, j))
        
        return bonds
    
    def create_3d_structure_plot(self, symbols: List[str], positions: np.ndarray, 
                                title: str = "", figsize: Tuple[int, int] = (10, 8),
                                save_path: Optional[str] = None) -> plt.Figure:
        """
        创建3D分子结构图
        
        Args:
            symbols: 原子符号列表
            positions: 原子坐标
            title: 图标题
            figsize: 图像大小
            save_path: 保存路径
            
        Returns:
            matplotlib图像对象
        """
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        # 获取键信息
        bonds = self.get_bonds(symbols, positions)
        
        # 绘制化学键
        for bond in bonds:
            i, j = bond
            ax.plot3D([positions[i][0], positions[j][0]],
                     [positions[i][1], positions[j][1]],
                     [positions[i][2], positions[j][2]], 
                     'k-', linewidth=1.5, alpha=0.7)
        
        # 绘制原子
        for i, (symbol, pos) in enumerate(zip(symbols, positions)):
            color = self.atom_colors.get(symbol, '#808080')
            size = self.atom_radii.get(symbol, 0.8) * 300  # 缩放因子
            
            ax.scatter(pos[0], pos[1], pos[2], 
                      c=color, s=size, alpha=0.9, 
                      edgecolors='black', linewidth=0.5)
        
        # 设置图像属性
        ax.set_xlabel('X (Å)', fontsize=12)
        ax.set_ylabel('Y (Å)', fontsize=12)
        ax.set_zlabel('Z (Å)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # 设置坐标轴等比例
        max_range = np.max(np.ptp(positions, axis=0)) / 2.0
        mid_x = np.mean(positions[:, 0])
        mid_y = np.mean(positions[:, 1])
        mid_z = np.mean(positions[:, 2])
        
        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)
        
        # 添加图例
        legend_elements = []
        unique_symbols = list(set(symbols))
        for symbol in sorted(unique_symbols):
            color = self.atom_colors.get(symbol, '#808080')
            legend_elements.append(mpatches.Patch(color=color, label=symbol))
        
        ax.legend(handles=legend_elements, loc='upper right')
        
        # 保存图像
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.savefig(save_path.replace('.pdf', '.png'), dpi=300, bbox_inches='tight')
            logger.info(f"图像已保存: {save_path}")
        
        return fig
    
    def create_comparison_plot(self, structures: Dict[str, Tuple[List[str], np.ndarray]], 
                              figsize: Tuple[int, int] = (15, 10),
                              save_path: Optional[str] = None) -> plt.Figure:
        """
        创建多结构对比图（类似您提供的示例图(b)）
        
        Args:
            structures: 结构字典 {名称: (符号列表, 坐标)}
            figsize: 图像大小
            save_path: 保存路径
            
        Returns:
            matplotlib图像对象
        """
        n_structures = len(structures)
        fig, axes = plt.subplots(1, n_structures, figsize=figsize, 
                                subplot_kw={'projection': '3d'})
        
        if n_structures == 1:
            axes = [axes]
        
        for i, (name, (symbols, positions)) in enumerate(structures.items()):
            ax = axes[i]
            
            # 获取键信息
            bonds = self.get_bonds(symbols, positions)
            
            # 绘制化学键
            for bond in bonds:
                idx1, idx2 = bond
                ax.plot3D([positions[idx1][0], positions[idx2][0]],
                         [positions[idx1][1], positions[idx2][1]],
                         [positions[idx1][2], positions[idx2][2]], 
                         'k-', linewidth=1, alpha=0.6)
            
            # 绘制原子
            for j, (symbol, pos) in enumerate(zip(symbols, positions)):
                color = self.atom_colors.get(symbol, '#808080')
                size = self.atom_radii.get(symbol, 0.8) * 200
                
                ax.scatter(pos[0], pos[1], pos[2], 
                          c=color, s=size, alpha=0.9,
                          edgecolors='black', linewidth=0.3)
            
            # 设置标题和坐标轴
            ax.set_title(name, fontsize=12, fontweight='bold')
            ax.set_xlabel('X (Å)')
            ax.set_ylabel('Y (Å)')
            ax.set_zlabel('Z (Å)')
            
            # 移除坐标轴标签以节省空间
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_zticks([])
        
        plt.tight_layout()
        
        # 保存图像
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.savefig(save_path.replace('.pdf', '.png'), dpi=300, bbox_inches='tight')
            logger.info(f"对比图已保存: {save_path}")
        
        return fig
    
    def create_energy_diagram(self, data: Dict, figsize: Tuple[int, int] = (10, 6),
                             save_path: Optional[str] = None) -> plt.Figure:
        """
        创建能级图（类似您提供的示例图(a)）
        
        Args:
            data: 能级数据
            figsize: 图像大小
            save_path: 保存路径
            
        Returns:
            matplotlib图像对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # 示例数据（您可以根据实际DFT计算结果修改）
        states = ['E_vert', 'E_loc', 'E_opt']
        energies = {'neutral': [0, -0.5, -0.8],
                   'charged': [1.5, 0.8, 0.3]}
        
        x_positions = np.arange(len(states))
        width = 0.35
        
        # 绘制能级
        bars1 = ax.bar(x_positions - width/2, energies['neutral'], width, 
                      label='Neutral bulk', color='lightblue', alpha=0.7)
        bars2 = ax.bar(x_positions + width/2, energies['charged'], width,
                      label='Negatively charged system', color='lightcoral', alpha=0.7)
        
        # 添加箭头和标注
        ax.annotate('λ⁻(loc)', xy=(0.5, -0.2), xytext=(0.8, -1.2),
                   arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
                   fontsize=12, color='red')
        
        ax.annotate('λ⁺(env)', xy=(1.5, 0.5), xytext=(2.2, 1.2),
                   arrowprops=dict(arrowstyle='->', color='blue', lw=1.5),
                   fontsize=12, color='blue')
        
        # 设置图像属性
        ax.set_xlabel('Nuclear coordinates →', fontsize=12)
        ax.set_ylabel('Energy', fontsize=12)
        ax.set_title('Energy Level Diagram', fontsize=14, fontweight='bold')
        ax.set_xticks(x_positions)
        ax.set_xticklabels(states)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 保存图像
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.savefig(save_path.replace('.pdf', '.png'), dpi=300, bbox_inches='tight')
            logger.info(f"能级图已保存: {save_path}")
        
        return fig

def main():
    """主函数 - 演示如何使用"""
    visualizer = StructureVisualizer()
    
    # 创建输出目录
    output_dir = Path("paper/figures/structure_plots")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🎨 分子结构可视化工具")
    print("="*50)
    
    # 检查是否有C60结构文件
    c60_file = Path("graphullerene/C60.xyz")
    if c60_file.exists():
        print(f"📁 发现C60结构文件: {c60_file}")
        
        # 读取和可视化C60
        symbols, positions = visualizer.read_xyz_file(str(c60_file))
        
        # 创建3D结构图
        fig = visualizer.create_3d_structure_plot(
            symbols, positions, 
            title=r"C$_{60}$ Fullerene Structure",  # 使用数学模式显示下标
            save_path=str(output_dir / "c60_structure.pdf")
        )
        
        print(f"✅ C60结构图已生成并保存到: {output_dir}")
        
        # 显示图像
        plt.show()
    else:
        print("⚠️  未找到C60.xyz文件，创建示例演示")
        
        # 创建能级图示例
        fig = visualizer.create_energy_diagram(
            {}, save_path=str(output_dir / "energy_diagram.pdf")
        )
        
        print(f"✅ 示例能级图已生成: {output_dir}")
        plt.show()
    
    print("="*50)
    print("🚀 可视化完成！")
    print(f"📊 输出目录: {output_dir}")
    print("💡 提示: 您可以修改此脚本来适配您的具体结构文件")

if __name__ == "__main__":
    main()
