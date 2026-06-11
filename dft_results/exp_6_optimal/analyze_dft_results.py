#!/usr/bin/env python3
"""
实验6: DFT结果分析脚本
从真实DFT输出文件中提取能量、带隙等数据并生成分析结果
独立于计算脚本运行
"""

import numpy as np
import json
import matplotlib.pyplot as plt
from pathlib import Path
import re
import logging
from typing import Dict, List, Optional

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DFTResultAnalyzer:
    """DFT结果分析器 - 从真实输出文件提取数据"""
    
    def __init__(self, experiment_dir: str = "."):
        self.experiment_dir = Path(experiment_dir).resolve()
        self.outputs_dir = self.experiment_dir / "outputs"
        self.results_dir = self.experiment_dir / "results"
        self.figures_dir = self.experiment_dir / "figures"
        
        # 确保目录存在
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        
        # 实验配置
        self.strain_values = [-5.0, -3.0, 0.0, 3.0, 5.0]
        self.doping_types = ['pristine', 'B', 'N', 'P']
        
    def extract_energy_from_output(self, output_file: Path) -> Optional[float]:
        """从CP2K输出文件提取总能量"""
        if not output_file.exists():
            return None
            
        try:
            with open(output_file, 'r') as f:
                content = f.read()
                
            # 查找最终能量
            match = re.search(r'ENERGY\| Total FORCE_EVAL \( QS \) energy \[a.u.\]:\s*([-+]?\d+\.\d+)', content)
            if match:
                return float(match.group(1))
        except Exception as e:
            logger.warning(f"提取能量失败 {output_file.name}: {e}")
            
        return None
    
    def extract_convergence_info(self, output_file: Path) -> Dict:
        """从CP2K输出文件提取收敛信息"""
        info = {
            'converged': False,
            'scf_steps': 0,
            'final_eps': None
        }
        
        if not output_file.exists():
            return info
            
        try:
            with open(output_file, 'r') as f:
                content = f.read()
                
            # 检查是否正常结束
            if 'PROGRAM ENDED' in content:
                info['converged'] = True
                
            # 统计SCF步数
            scf_matches = re.findall(r'^\s+\d+\s+OT\s+\w+', content, re.MULTILINE)
            info['scf_steps'] = len(scf_matches)
            
            # 提取最终收敛精度
            eps_matches = re.findall(r'OT\s+\w+\s+[\d.E+-]+\s+[\d.]+\s+([\d.E+-]+)', content)
            if eps_matches:
                info['final_eps'] = float(eps_matches[-1])
                
        except Exception as e:
            logger.warning(f"提取收敛信息失败 {output_file.name}: {e}")
            
        return info
    
    def extract_atom_count(self, output_file: Path) -> int:
        """从CP2K输出文件提取原子数"""
        if not output_file.exists():
            return 0
            
        try:
            with open(output_file, 'r') as f:
                content = f.read()
                
            # 查找原子数
            match = re.search(r'- Atoms:\s+(\d+)', content)
            if match:
                return int(match.group(1))
                
            match = re.search(r'Number of atoms:\s+(\d+)', content)
            if match:
                return int(match.group(1))
                
        except Exception as e:
            logger.warning(f"提取原子数失败 {output_file.name}: {e}")
            
        return 0
    
    def find_output_files(self) -> List[Path]:
        """查找所有DFT输出文件"""
        output_files = list(self.outputs_dir.glob("*.out"))
        logger.info(f"找到 {len(output_files)} 个输出文件")
        return output_files
    
    def parse_filename(self, filename: str) -> Dict:
        """解析输出文件名提取应变和掺杂信息"""
        info = {'strain': None, 'dopant': None, 'charge': 0}
        
        # 解析应变值 (如: optimal_+0.0_B_q0.out)
        strain_match = re.search(r'_([-+]?\d+\.?\d*)_', filename)
        if strain_match:
            info['strain'] = float(strain_match.group(1))
        
        # 解析掺杂类型
        if '_pristine_' in filename or '_pristine.' in filename:
            info['dopant'] = 'pristine'
        elif '_B_' in filename or '_B.' in filename:
            info['dopant'] = 'B'
        elif '_N_' in filename or '_N.' in filename:
            info['dopant'] = 'N'
        elif '_P_' in filename or '_P.' in filename:
            info['dopant'] = 'P'
        elif '_B+N_' in filename:
            info['dopant'] = 'B+N'
            
        # 解析电荷状态
        charge_match = re.search(r'_q(\d+)', filename)
        if charge_match:
            info['charge'] = int(charge_match.group(1))
            
        return info
    
    def analyze_all_outputs(self) -> Dict:
        """分析所有输出文件"""
        logger.info("=" * 60)
        logger.info("开始分析DFT输出文件")
        logger.info("=" * 60)
        
        output_files = self.find_output_files()
        results = {}
        
        for output_file in output_files:
            file_info = self.parse_filename(output_file.name)
            
            if file_info['strain'] is None or file_info['dopant'] is None:
                logger.warning(f"无法解析文件名: {output_file.name}")
                continue
            
            # 提取数据
            energy = self.extract_energy_from_output(output_file)
            convergence = self.extract_convergence_info(output_file)
            n_atoms = self.extract_atom_count(output_file)
            
            key = f"strain_{file_info['strain']:+.1f}_{file_info['dopant']}"
            
            results[key] = {
                'strain': file_info['strain'],
                'dopant': file_info['dopant'],
                'charge': file_info['charge'],
                'total_energy_Ha': energy,
                'total_energy_eV': energy * 27.2114 if energy else None,
                'n_atoms': n_atoms,
                'energy_per_atom_Ha': energy / n_atoms if energy and n_atoms > 0 else None,
                'converged': convergence['converged'],
                'scf_steps': convergence['scf_steps'],
                'final_eps': convergence['final_eps'],
                'output_file': output_file.name,
                'status': 'success' if energy and convergence['converged'] else 'incomplete'
            }
            
            status = "✓" if results[key]['status'] == 'success' else "✗"
            logger.info(f"  {status} {key}: E = {energy:.6f} Ha" if energy else f"  ✗ {key}: 无能量数据")
        
        return results
    
    def calculate_derived_properties(self, results: Dict) -> Dict:
        """计算衍生性质（相对能量、应变敏感度等）"""
        logger.info("\n计算衍生性质...")
        
        # 找到pristine在0%应变的能量作为参考
        ref_key = "strain_+0.0_pristine"
        ref_energy = results.get(ref_key, {}).get('total_energy_Ha')
        
        for key, data in results.items():
            if data['total_energy_Ha'] is not None and ref_energy is not None:
                # 相对于pristine的能量差
                data['relative_energy_Ha'] = data['total_energy_Ha'] - ref_energy
                data['relative_energy_eV'] = data['relative_energy_Ha'] * 27.2114
            else:
                data['relative_energy_Ha'] = None
                data['relative_energy_eV'] = None
        
        # 计算每种掺杂类型的应变敏感度
        for dopant in self.doping_types:
            dopant_data = [(data['strain'], data['total_energy_Ha']) 
                          for key, data in results.items() 
                          if data['dopant'] == dopant and data['total_energy_Ha'] is not None]
            
            if len(dopant_data) >= 2:
                strains = [d[0] for d in dopant_data]
                energies = [d[1] for d in dopant_data]
                
                # 线性拟合计算dE/dε
                coeffs = np.polyfit(strains, energies, 1)
                slope_Ha_per_percent = coeffs[0]
                slope_meV_per_percent = slope_Ha_per_percent * 27.2114 * 1000
                
                logger.info(f"  {dopant}: dE/dε = {slope_meV_per_percent:.2f} meV/%")
                
                # 更新每个点的应变敏感度
                for key, data in results.items():
                    if data['dopant'] == dopant:
                        data['strain_sensitivity_meV_per_percent'] = slope_meV_per_percent
        
        return results
    
    def generate_analysis_summary(self, results: Dict) -> Dict:
        """生成分析摘要"""
        logger.info("\n生成分析摘要...")
        
        summary = {
            'total_calculations': len(results),
            'successful_calculations': sum(1 for r in results.values() if r['status'] == 'success'),
            'dopant_types': list(set(r['dopant'] for r in results.values())),
            'strain_values': sorted(list(set(r['strain'] for r in results.values()))),
            'energy_statistics': {},
            'strain_sensitivity': {}
        }
        
        # 按掺杂类型统计
        for dopant in summary['dopant_types']:
            dopant_results = [r for r in results.values() if r['dopant'] == dopant and r['status'] == 'success']
            
            if dopant_results:
                energies = [r['total_energy_Ha'] for r in dopant_results]
                summary['energy_statistics'][dopant] = {
                    'count': len(dopant_results),
                    'min_energy_Ha': min(energies),
                    'max_energy_Ha': max(energies),
                    'mean_energy_Ha': np.mean(energies),
                    'energy_range_meV': (max(energies) - min(energies)) * 27.2114 * 1000
                }
                
                # 应变敏感度
                if 'strain_sensitivity_meV_per_percent' in dopant_results[0]:
                    summary['strain_sensitivity'][dopant] = dopant_results[0]['strain_sensitivity_meV_per_percent']
        
        # 找到最稳定配置
        successful = [(k, v) for k, v in results.items() if v['status'] == 'success']
        if successful:
            most_stable = min(successful, key=lambda x: x[1]['total_energy_Ha'])
            summary['most_stable_config'] = {
                'key': most_stable[0],
                'strain': most_stable[1]['strain'],
                'dopant': most_stable[1]['dopant'],
                'energy_Ha': most_stable[1]['total_energy_Ha']
            }
        
        return summary
    
    def plot_results(self, results: Dict, summary: Dict):
        """生成可视化图表"""
        logger.info("\n生成图表...")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        
        # 颜色映射
        colors = {'pristine': 'black', 'B': 'red', 'N': 'blue', 'P': 'green', 'B+N': 'purple'}
        markers = {'pristine': 'o', 'B': 's', 'N': '^', 'P': 'D', 'B+N': 'p'}
        
        # 1. 总能量 vs 应变
        ax1 = axes[0, 0]
        for dopant in self.doping_types:
            dopant_data = [(r['strain'], r['total_energy_Ha']) 
                          for r in results.values() 
                          if r['dopant'] == dopant and r['total_energy_Ha'] is not None]
            if dopant_data:
                dopant_data.sort(key=lambda x: x[0])
                strains = [d[0] for d in dopant_data]
                energies = [d[1] for d in dopant_data]
                ax1.plot(strains, energies, marker=markers.get(dopant, 'o'), 
                        color=colors.get(dopant, 'gray'), label=dopant, linewidth=2, markersize=8)
        
        ax1.set_xlabel('Strain (%)', fontsize=12)
        ax1.set_ylabel('Total Energy (Ha)', fontsize=12)
        ax1.set_title('Total Energy vs Strain', fontsize=14)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 相对能量 vs 应变 (相对于0%应变的pristine)
        ax2 = axes[0, 1]
        for dopant in self.doping_types:
            dopant_data = [(r['strain'], r['relative_energy_eV']) 
                          for r in results.values() 
                          if r['dopant'] == dopant and r.get('relative_energy_eV') is not None]
            if dopant_data:
                dopant_data.sort(key=lambda x: x[0])
                strains = [d[0] for d in dopant_data]
                rel_energies = [d[1] for d in dopant_data]
                ax2.plot(strains, rel_energies, marker=markers.get(dopant, 'o'), 
                        color=colors.get(dopant, 'gray'), label=dopant, linewidth=2, markersize=8)
        
        ax2.axhline(0, color='gray', linestyle='--', linewidth=0.8)
        ax2.set_xlabel('Strain (%)', fontsize=12)
        ax2.set_ylabel('Relative Energy (eV)', fontsize=12)
        ax2.set_title('Relative Energy vs Strain (ref: pristine @ 0%)', fontsize=14)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. 应变敏感度对比
        ax3 = axes[1, 0]
        if summary.get('strain_sensitivity'):
            dopants = list(summary['strain_sensitivity'].keys())
            sensitivities = [summary['strain_sensitivity'][d] for d in dopants]
            bar_colors = [colors.get(d, 'gray') for d in dopants]
            
            bars = ax3.bar(dopants, sensitivities, color=bar_colors, edgecolor='black', linewidth=1.5)
            ax3.axhline(0, color='gray', linestyle='--', linewidth=0.8)
            ax3.set_xlabel('Dopant Type', fontsize=12)
            ax3.set_ylabel('Strain Sensitivity (meV/%)', fontsize=12)
            ax3.set_title('Strain Sensitivity by Dopant Type', fontsize=14)
            ax3.grid(axis='y', alpha=0.3)
            
            # 添加数值标签
            for bar, sens in zip(bars, sensitivities):
                ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                        f'{sens:.1f}', ha='center', va='bottom', fontsize=10)
        
        # 4. 数据摘要
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        summary_text = f"""
DFT Calculation Summary
========================

Total Calculations: {summary['total_calculations']}
Successful: {summary['successful_calculations']}
Dopant Types: {', '.join(summary['dopant_types'])}
Strain Range: {min(summary['strain_values']):.1f}% to {max(summary['strain_values']):.1f}%

Most Stable Configuration:
  {summary.get('most_stable_config', {}).get('dopant', 'N/A')} @ {summary.get('most_stable_config', {}).get('strain', 'N/A')}% strain
  Energy: {summary.get('most_stable_config', {}).get('energy_Ha', 'N/A'):.6f} Ha

Strain Sensitivity (meV/%):
"""
        for dopant, sens in summary.get('strain_sensitivity', {}).items():
            summary_text += f"  {dopant}: {sens:.2f}\n"
        
        ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, fontsize=11,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        # 保存图表
        plot_file = self.figures_dir / "real_dft_analysis.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.savefig(self.figures_dir / "real_dft_analysis.pdf", bbox_inches='tight')
        plt.close()
        
        logger.info(f"  图表已保存: {plot_file}")
        
        return str(plot_file)
    
    def save_results(self, results: Dict, summary: Dict):
        """保存分析结果到JSON文件"""
        logger.info("\n保存结果...")
        
        # 转换numpy类型
        def convert_numpy(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(i) for i in obj]
            return obj
        
        # 保存详细结果
        results_file = self.results_dir / "real_dft_results.json"
        with open(results_file, 'w') as f:
            json.dump(convert_numpy(results), f, indent=2)
        logger.info(f"  详细结果: {results_file}")
        
        # 保存摘要
        summary_file = self.results_dir / "analysis_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(convert_numpy(summary), f, indent=2)
        logger.info(f"  分析摘要: {summary_file}")
        
        return results_file, summary_file
    
    def run_analysis(self):
        """运行完整分析流程"""
        logger.info("=" * 60)
        logger.info("实验6: DFT结果分析")
        logger.info("=" * 60)
        
        # 1. 分析所有输出文件
        results = self.analyze_all_outputs()
        
        if not results:
            logger.error("未找到有效的DFT结果!")
            return None
        
        # 2. 计算衍生性质
        results = self.calculate_derived_properties(results)
        
        # 3. 生成分析摘要
        summary = self.generate_analysis_summary(results)
        
        # 4. 生成图表
        plot_file = self.plot_results(results, summary)
        summary['plot_file'] = plot_file
        
        # 5. 保存结果
        self.save_results(results, summary)
        
        # 6. 打印最终摘要
        logger.info("\n" + "=" * 60)
        logger.info("分析完成!")
        logger.info("=" * 60)
        logger.info(f"  成功分析: {summary['successful_calculations']}/{summary['total_calculations']} 个计算")
        logger.info(f"  最稳定配置: {summary.get('most_stable_config', {}).get('dopant', 'N/A')} @ "
                   f"{summary.get('most_stable_config', {}).get('strain', 'N/A')}%")
        
        if summary.get('strain_sensitivity'):
            logger.info("\n  应变敏感度 (meV/%):")
            for dopant, sens in sorted(summary['strain_sensitivity'].items(), 
                                       key=lambda x: abs(x[1]), reverse=True):
                logger.info(f"    {dopant}: {sens:+.2f}")
        
        return {'results': results, 'summary': summary}


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='分析实验6 DFT计算结果')
    parser.add_argument('--dir', type=str, default='.', 
                       help='实验目录路径 (包含outputs子目录)')
    args = parser.parse_args()
    
    analyzer = DFTResultAnalyzer(args.dir)
    results = analyzer.run_analysis()
    
    return results


if __name__ == "__main__":
    main()

