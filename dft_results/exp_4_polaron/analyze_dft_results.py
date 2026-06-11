#!/usr/bin/env python3
"""
实验4: DFT结果分析脚本
从真实DFT输出文件中提取能量数据
独立于计算脚本运行
"""

import numpy as np
import json
import matplotlib.pyplot as plt
from pathlib import Path
import re
import logging
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Exp4DFTAnalyzer:
    """实验4 极化子转变DFT结果分析器"""
    
    def __init__(self, experiment_dir: str = "."):
        self.experiment_dir = Path(experiment_dir).resolve()
        
        # 支持两种目录结构
        if (self.experiment_dir / "outputs").exists():
            self.outputs_dir = self.experiment_dir / "outputs"
        else:
            self.outputs_dir = self.experiment_dir
        
        self.results_dir = self.experiment_dir / "results"
        self.figures_dir = self.experiment_dir / "figures"
        
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        
        self.doping_types = ['pristine', 'B', 'N', 'P']
    
    def extract_energy(self, output_file: Path) -> Optional[float]:
        """提取总能量"""
        if not output_file.exists():
            return None
        try:
            with open(output_file, 'r') as f:
                content = f.read()
            match = re.search(r'ENERGY\| Total FORCE_EVAL \( QS \) energy \[a.u.\]:\s*([-+]?\d+\.\d+)', content)
            if match:
                return float(match.group(1))
        except:
            pass
        return None
    
    def is_completed(self, output_file: Path) -> bool:
        """检查是否完成"""
        if not output_file.exists():
            return False
        try:
            with open(output_file, 'r') as f:
                return 'PROGRAM ENDED' in f.read()
        except:
            return False
    
    def extract_atom_count(self, output_file: Path) -> int:
        """提取原子数"""
        if not output_file.exists():
            return 0
        try:
            with open(output_file, 'r') as f:
                content = f.read()
            match = re.search(r'- Atoms:\s+(\d+)', content)
            if match:
                return int(match.group(1))
        except:
            pass
        return 0
    
    def parse_filename(self, filename: str) -> Dict:
        """解析文件名"""
        info = {'strain': None, 'dopant': None, 'charge': 0}
        
        # 解析应变
        strain_match = re.search(r'_([-+]?\d+\.?\d*)_', filename)
        if strain_match:
            info['strain'] = float(strain_match.group(1))
        
        # 解析掺杂类型
        if 'pristine' in filename.lower():
            info['dopant'] = 'pristine'
        elif '_B_' in filename:
            info['dopant'] = 'B'
        elif '_N_' in filename:
            info['dopant'] = 'N'
        elif '_P_' in filename:
            info['dopant'] = 'P'
        
        # 解析电荷
        charge_match = re.search(r'_q(\d+)', filename)
        if charge_match:
            info['charge'] = int(charge_match.group(1))
        
        return info
    
    def analyze_all_outputs(self) -> Dict:
        """分析所有输出"""
        logger.info("=" * 60)
        logger.info("实验4: 极化子转变DFT结果分析")
        logger.info("=" * 60)
        
        output_files = list(self.outputs_dir.glob("*.out"))
        logger.info(f"找到 {len(output_files)} 个输出文件")
        
        results = {}
        
        for output_file in output_files:
            file_info = self.parse_filename(output_file.name)
            
            if file_info['strain'] is None or file_info['dopant'] is None:
                continue
            
            energy = self.extract_energy(output_file)
            completed = self.is_completed(output_file)
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
                'converged': completed,
                'output_file': output_file.name,
                'status': 'success' if energy and completed else 'incomplete'
            }
            
            status = "✓" if results[key]['status'] == 'success' else "✗"
            if energy:
                logger.info(f"  {status} {key}: E = {energy:.6f} Ha ({n_atoms} atoms)")
            else:
                logger.info(f"  ✗ {key}: 无能量数据")
        
        return results
    
    def calculate_polaron_metrics(self, results: Dict) -> Dict:
        """计算极化子相关指标"""
        logger.info("\n计算极化子指标...")
        
        metrics = {
            'doping_effects': {},
            'strain_effects': {},
            'pristine_reference': None
        }
        
        # 找到pristine参考能量
        pristine_0 = None
        for key, data in results.items():
            if data['dopant'] == 'pristine' and data['strain'] == 0.0:
                pristine_0 = data['total_energy_Ha']
                metrics['pristine_reference'] = pristine_0
                break
        
        if not pristine_0:
            # 尝试找任何pristine
            for key, data in results.items():
                if data['dopant'] == 'pristine' and data['total_energy_Ha']:
                    pristine_0 = data['total_energy_Ha']
                    metrics['pristine_reference'] = pristine_0
                    break
        
        # 计算掺杂效应
        for key, data in results.items():
            if data['dopant'] != 'pristine' and data['total_energy_Ha'] and pristine_0:
                # 找同应变的pristine
                pristine_key = f"strain_{data['strain']:+.1f}_pristine"
                pristine_energy = results.get(pristine_key, {}).get('total_energy_Ha')
                
                if pristine_energy:
                    delta_E = (data['total_energy_Ha'] - pristine_energy) * 27.2114
                    metrics['doping_effects'][key] = {
                        'delta_E_eV': delta_E,
                        'dopant': data['dopant'],
                        'strain': data['strain']
                    }
                    logger.info(f"  {data['dopant']} @ {data['strain']}%: ΔE = {delta_E:.3f} eV")
        
        # 计算应变效应
        for dopant in self.doping_types:
            dopant_data = [(d['strain'], d['total_energy_Ha']) 
                          for d in results.values() 
                          if d['dopant'] == dopant and d['total_energy_Ha']]
            
            if len(dopant_data) >= 2:
                strains = [d[0] for d in dopant_data]
                energies = [d[1] for d in dopant_data]
                coeffs = np.polyfit(strains, energies, 1)
                slope_meV = coeffs[0] * 27.2114 * 1000
                metrics['strain_effects'][dopant] = slope_meV
        
        return metrics
    
    def generate_summary(self, results: Dict, metrics: Dict) -> Dict:
        """生成摘要"""
        summary = {
            'total_calculations': len(results),
            'successful_calculations': sum(1 for r in results.values() if r['status'] == 'success'),
            'dopant_types': list(set(r['dopant'] for r in results.values())),
            'strain_values': sorted(list(set(r['strain'] for r in results.values()))),
            'strain_effects': metrics['strain_effects'],
            'doping_effects_count': len(metrics['doping_effects'])
        }
        
        # 找最稳定配置
        successful = [(k, v) for k, v in results.items() if v['status'] == 'success']
        if successful:
            most_stable = min(successful, key=lambda x: x[1]['total_energy_Ha'])
            summary['most_stable'] = {
                'key': most_stable[0],
                'strain': most_stable[1]['strain'],
                'dopant': most_stable[1]['dopant'],
                'energy_Ha': most_stable[1]['total_energy_Ha']
            }
        
        return summary
    
    def plot_results(self, results: Dict, metrics: Dict):
        """生成图表"""
        logger.info("\n生成图表...")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        
        colors = {'pristine': 'black', 'B': 'red', 'N': 'blue', 'P': 'green'}
        markers = {'pristine': 'o', 'B': 's', 'N': '^', 'P': 'D'}
        
        # 1. 总能量 vs 应变
        ax1 = axes[0, 0]
        for dopant in self.doping_types:
            data = [(r['strain'], r['total_energy_Ha']) 
                   for r in results.values() 
                   if r['dopant'] == dopant and r['total_energy_Ha']]
            if data:
                data.sort()
                ax1.plot([d[0] for d in data], [d[1] for d in data], 
                        marker=markers.get(dopant, 'o'), color=colors.get(dopant, 'gray'),
                        label=dopant, linewidth=2, markersize=8)
        
        ax1.set_xlabel('Strain (%)', fontsize=12)
        ax1.set_ylabel('Total Energy (Ha)', fontsize=12)
        ax1.set_title('Total Energy vs Strain (C60 Dimer)', fontsize=14)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 掺杂效应
        ax2 = axes[0, 1]
        if metrics['doping_effects']:
            for dopant in ['B', 'N', 'P']:
                data = [(v['strain'], v['delta_E_eV']) 
                       for v in metrics['doping_effects'].values() 
                       if v['dopant'] == dopant]
                if data:
                    data.sort()
                    ax2.plot([d[0] for d in data], [d[1] for d in data],
                            marker=markers.get(dopant, 'o'), color=colors.get(dopant, 'gray'),
                            label=f'{dopant} doping', linewidth=2, markersize=8)
        
        ax2.axhline(0, color='gray', linestyle='--')
        ax2.set_xlabel('Strain (%)', fontsize=12)
        ax2.set_ylabel('Doping Effect ΔE (eV)', fontsize=12)
        ax2.set_title('Doping Effect on Total Energy', fontsize=14)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. 应变敏感度对比
        ax3 = axes[1, 0]
        if metrics['strain_effects']:
            dopants = list(metrics['strain_effects'].keys())
            values = [metrics['strain_effects'][d] for d in dopants]
            bar_colors = [colors.get(d, 'gray') for d in dopants]
            
            bars = ax3.bar(dopants, values, color=bar_colors, edgecolor='black')
            ax3.axhline(0, color='gray', linestyle='--')
            ax3.set_xlabel('Dopant Type', fontsize=12)
            ax3.set_ylabel('Strain Sensitivity (meV/%)', fontsize=12)
            ax3.set_title('Strain Sensitivity Comparison', fontsize=14)
            ax3.grid(axis='y', alpha=0.3)
        
        # 4. 数据摘要
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        summary_text = f"""
DFT Calculation Summary (Exp4: Polaron)
=========================================

Total Calculations: {len(results)}
Successful: {sum(1 for r in results.values() if r['status'] == 'success')}

Strain Sensitivity (meV/%):
"""
        for dopant, sens in metrics.get('strain_effects', {}).items():
            summary_text += f"  {dopant}: {sens:+.2f}\n"
        
        ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, fontsize=11,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        plot_file = self.figures_dir / "real_dft_analysis.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.savefig(self.figures_dir / "real_dft_analysis.pdf", bbox_inches='tight')
        plt.close()
        
        logger.info(f"  图表已保存: {plot_file}")
    
    def save_results(self, results: Dict, metrics: Dict, summary: Dict):
        """保存结果"""
        logger.info("\n保存结果...")
        
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
        
        with open(self.results_dir / "real_dft_results.json", 'w') as f:
            json.dump(convert_numpy(results), f, indent=2)
        
        with open(self.results_dir / "polaron_metrics.json", 'w') as f:
            json.dump(convert_numpy(metrics), f, indent=2)
        
        with open(self.results_dir / "analysis_summary.json", 'w') as f:
            json.dump(convert_numpy(summary), f, indent=2)
        
        logger.info(f"  结果已保存到: {self.results_dir}")
    
    def run_analysis(self):
        """运行完整分析"""
        results = self.analyze_all_outputs()
        
        if not results:
            logger.error("未找到有效数据!")
            return None
        
        metrics = self.calculate_polaron_metrics(results)
        summary = self.generate_summary(results, metrics)
        
        self.plot_results(results, metrics)
        self.save_results(results, metrics, summary)
        
        logger.info("\n" + "=" * 60)
        logger.info("分析完成!")
        logger.info("=" * 60)
        logger.info(f"  成功分析: {summary['successful_calculations']}/{summary['total_calculations']}")
        
        if summary.get('most_stable'):
            logger.info(f"  最稳定配置: {summary['most_stable']['dopant']} @ "
                       f"{summary['most_stable']['strain']}%")
        
        return {'results': results, 'metrics': metrics, 'summary': summary}


def main():
    import argparse
    parser = argparse.ArgumentParser(description='分析实验4 DFT结果')
    parser.add_argument('--dir', type=str, default='.', help='实验目录')
    args = parser.parse_args()
    
    analyzer = Exp4DFTAnalyzer(args.dir)
    analyzer.run_analysis()


if __name__ == "__main__":
    main()

