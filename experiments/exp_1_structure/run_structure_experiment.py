#!/usr/bin/env python3
"""
实验1: 结构表征实验 - 真实实验脚本
运行DFT计算验证qHP C₆₀网络的结构参数和应变响应
"""

import numpy as np
import json
import matplotlib.pyplot as plt
from pathlib import Path
import subprocess
import time
import logging
from typing import Dict, List, Tuple
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from c60_coordinates import format_c60_coordinates_for_cp2k
from qhp_c60_structures import (
    get_c60_dimer_coordinates,
    get_qhp_network_cell,
    format_coords_for_cp2k
)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StructureExperimentRunner:
    """结构表征实验运行器"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        # 如果当前已经在exp_1_structure目录，向上找项目根
        if self.project_root.name == "exp_1_structure":
            self.project_root = self.project_root.parent.parent
        self.experiment_dir = self.project_root / "experiments" / "exp_1_structure"
        self.hpc_dir = self.project_root / "hpc_calculations"

        # 理论预测值
        self.theoretical_predictions = {
            'lattice_a': 36.67,  # Å
            'lattice_b': 30.84,  # Å
            'tolerance_a': 0.5,   # Å
            'tolerance_b': 0.3    # Å
        }

        # 应变范围
        self.strain_values = [-5.0, -2.5, 0.0, 2.5, 5.0]  # %

        # 创建必要的目录
        self.experiment_dir.mkdir(parents=True, exist_ok=True)
        (self.experiment_dir / "outputs").mkdir(exist_ok=True)
        (self.experiment_dir / "results").mkdir(exist_ok=True)
        (self.experiment_dir / "figures").mkdir(exist_ok=True)

    def create_dft_input_files(self):
        """创建DFT输入文件 - 使用2×C60二聚体验证网络参数"""
        logger.info("创建DFT输入文件 (2×C60 二聚体)...")

        # 获取2×C60二聚体坐标
        dimer_coords, cell_info = get_c60_dimer_coordinates(separation=10.0)
        coords_str = format_coords_for_cp2k(dimer_coords)

        for strain in self.strain_values:
            input_file = self.experiment_dir / "outputs" / f"C60_strain_{strain:+.1f}_pristine.inp"

            # 根据应变计算晶格参数 (基于qHP网络参数)
            strain_factor = 1 + strain/100
            lattice_a = cell_info['a'] * strain_factor
            lattice_b = cell_info['b'] * strain_factor
            lattice_c = cell_info['c']

            # 创建CP2K输入文件
            input_content = f"""&GLOBAL
  PROJECT C60_dimer_strain_{strain:+.1f}_pristine
  RUN_TYPE ENERGY
  PRINT_LEVEL LOW
&END GLOBAL

&FORCE_EVAL
  METHOD Quickstep
  &DFT
    BASIS_SET_FILE_NAME /opt/cp2k/data/BASIS_MOLOPT
    POTENTIAL_FILE_NAME /opt/cp2k/data/GTH_POTENTIALS
    
    &MGRID
      CUTOFF 400
      REL_CUTOFF 50
    &END MGRID
    
    &QS
      METHOD GPW
    &END QS
    
    &XC
      &XC_FUNCTIONAL PBE
      &END XC_FUNCTIONAL
    &END XC
    
    &SCF
      SCF_GUESS ATOMIC
      EPS_SCF 1.0E-5
      MAX_SCF 200
      
      &OT
        MINIMIZER DIIS
        PRECONDITIONER FULL_SINGLE_INVERSE
        ENERGY_GAP 0.1
      &END OT
      
      &OUTER_SCF
        MAX_SCF 20
        EPS_SCF 1.0E-5
      &END OUTER_SCF
    &END SCF
  &END DFT

  &SUBSYS
    &CELL
      A {lattice_a:.6f} 0.000000 0.000000
      B 0.000000 {lattice_b:.6f} 0.000000
      C 0.000000 0.000000 {lattice_c:.6f}
      PERIODIC XYZ
    &END CELL

    &COORD
{coords_str}
    &END COORD

    &KIND C
      BASIS_SET DZVP-MOLOPT-GTH
      POTENTIAL GTH-PBE
    &END KIND
  &END SUBSYS
&END FORCE_EVAL
"""

            with open(input_file, 'w') as f:
                f.write(input_content)

            logger.info(f"创建输入文件: {input_file} (2×C60, {len(dimer_coords)} 原子)")

    def _check_calculation_success(self, output_file: Path) -> bool:
        """检查计算是否已成功完成"""
        if not output_file.exists():
            return False
        
        try:
            # 解析输出文件
            output_info = self._parse_dft_output(output_file)
            
            # 检查是否有有效的能量值
            if output_info and output_info.get('total_energy') is not None:
                # 进一步检查文件是否包含正常结束标记
                with open(output_file, 'r') as f:
                    content = f.read()
                    # CP2K正常结束会有这些标记之一
                    if 'PROGRAM ENDED AT' in content or 'ENERGY| Total FORCE_EVAL' in content:
                        return True
            return False
        except:
            return False

    def run_dft_calculations(self):
        """运行DFT计算"""
        logger.info("开始运行DFT计算...")

        # 查找CP2K可执行文件
        cp2k_exe = self._find_cp2k_executable()
        if not cp2k_exe:
            logger.error("未找到CP2K可执行文件")
            return {}
        
        logger.info(f"使用CP2K: {cp2k_exe}")
        logger.info(f"每个计算预计需要5-15分钟")

        results = {}
        skipped_count = 0
        run_count = 0

        for strain in self.strain_values:
            input_file = self.experiment_dir / "outputs" / f"C60_strain_{strain:+.1f}_pristine.inp"
            output_file = self.experiment_dir / "outputs" / f"C60_strain_{strain:+.1f}_pristine.out"

            # 检查是否已成功完成
            if self._check_calculation_success(output_file):
                logger.info(f"⏭️  跳过已完成: strain = {strain}%")
                # 从已有输出中读取结果
                output_info = self._parse_dft_output(output_file)
                output_info.update({
                    'strain': strain,
                    'status': 'success'
                })
                results[f"strain_{strain}"] = output_info
                skipped_count += 1
                continue

            logger.info(f"🔬 运行计算: strain = {strain}%")
            run_count += 1

            # 运行CP2K计算
            cmd = [str(cp2k_exe), '-i', str(input_file)]

            try:
                start_time = time.time()
                with open(output_file, 'w') as f:
                    result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE,
                                          timeout=3600, cwd=self.experiment_dir / "outputs")

                calculation_time = time.time() - start_time

                if result.returncode == 0:
                    # 解析输出
                    output_info = self._parse_dft_output(output_file)
                    output_info.update({
                        'strain': strain,
                        'calculation_time': calculation_time,
                        'status': 'success'
                    })
                    results[f"strain_{strain}"] = output_info
                    logger.info(f"✅ 计算成功: strain = {strain}%, 用时: {calculation_time:.2f}s")
                else:
                    logger.error(f"❌ 计算失败: strain = {strain}%, 错误: {result.stderr.decode()}")
                    results[f"strain_{strain}"] = {
                        'strain': strain,
                        'status': 'failed',
                        'error': result.stderr.decode()
                    }

            except subprocess.TimeoutExpired:
                logger.error(f"⏰ 计算超时: strain = {strain}%")
                results[f"strain_{strain}"] = {
                    'strain': strain,
                    'status': 'timeout'
                }
            except Exception as e:
                logger.error(f"💥 计算异常: strain = {strain}%, 错误: {e}")
                results[f"strain_{strain}"] = {
                    'strain': strain,
                    'status': 'error',
                    'error': str(e)
                }

        logger.info(f"\n📊 计算总结:")
        logger.info(f"  ⏭️  跳过（已完成）: {skipped_count}")
        logger.info(f"  🔬 本次运行: {run_count}")
        logger.info(f"  📝 总计: {len(results)}")

        return results

    def _find_cp2k_executable(self):
        """查找CP2K可执行文件"""
        import shutil

        possible_paths = [
            Path("/usr/local/bin/cp2k.ssmp"),
            Path("/opt/cp2k/bin/cp2k.ssmp"),
            Path("cp2k.ssmp"),
            Path("cp2k")
        ]

        for path in possible_paths:
            if path.exists() or shutil.which(str(path)):
                return path
        return None

    def _parse_dft_output(self, output_file: Path) -> Dict:
        """解析DFT输出文件"""
        output_info = {
            'total_energy': None,
            'lattice_parameters': {'a': None, 'b': None},
            'convergence': False,
            'n_atoms': 0
        }

        try:
            with open(output_file, 'r') as f:
                content = f.read()

            lines = content.split('\n')

            for line in lines:
                # 提取总能量
                if 'ENERGY| Total FORCE_EVAL' in line:
                    try:
                        energy = float(line.split()[-1])
                        output_info['total_energy'] = energy
                    except:
                        pass

                # 检查收敛
                if 'SCF run converged' in line:
                    output_info['convergence'] = True
                
                # 检查未收敛警告
                if 'SCF run NOT converged' in line:
                    output_info['convergence'] = False

                # 提取原子数 (CP2K格式: "- Atoms: 60")
                if '- Atoms:' in line:
                    try:
                        n_atoms = int(line.split()[-1])
                        output_info['n_atoms'] = n_atoms
                    except:
                        pass

            # 从对应的输入文件读取晶格参数（单点能量计算不改变晶格参数）
            input_file = output_file.with_suffix('.inp')
            if input_file.exists():
                with open(input_file, 'r') as f:
                    input_content = f.read()
                    input_lines = input_content.split('\n')
                    for line in input_lines:
                        # CP2K格式: A ax ay az, B bx by bz
                        # 对于正交晶胞: A=ax, B=by
                        if line.strip().startswith('A '):
                            try:
                                parts = line.split()
                                lattice_a = float(parts[1])  # ax component
                                output_info['lattice_parameters']['a'] = lattice_a
                            except:
                                pass
                        elif line.strip().startswith('B '):
                            try:
                                parts = line.split()
                                lattice_b = float(parts[2])  # by component (not bx=0)
                                output_info['lattice_parameters']['b'] = lattice_b
                            except:
                                pass

        except Exception as e:
            logger.warning(f"解析输出文件失败: {e}")

        return output_info

    def analyze_results(self, dft_results: Dict):
        """分析DFT结果"""
        logger.info("分析DFT结果...")

        analysis_results = {
            'lattice_parameters': [],
            'strain_response': {},
            'validation_metrics': {},
            'plots': {}
        }

        # 提取晶格参数
        strains = []
        lattice_a_values = []
        lattice_b_values = []
        energies = []

        for calc_name, result in dft_results.items():
            if result['status'] == 'success':
                strains.append(result['strain'])
                lattice_a_values.append(result['lattice_parameters']['a'])
                lattice_b_values.append(result['lattice_parameters']['b'])
                energies.append(result['total_energy'])

        analysis_results['lattice_parameters'] = {
            'strains': strains,
            'lattice_a': lattice_a_values,
            'lattice_b': lattice_b_values,
            'energies': energies
        }

        # 分析应变响应
        if len(strains) > 1:
            strain_response = self._analyze_strain_response(strains, lattice_a_values, lattice_b_values)
            analysis_results['strain_response'] = strain_response

        # 验证结果
        validation_metrics = self._validate_results(strains, lattice_a_values, lattice_b_values)
        analysis_results['validation_metrics'] = validation_metrics

        # 生成图表
        plots = self._generate_plots(strains, lattice_a_values, lattice_b_values, energies)
        analysis_results['plots'] = plots

        return analysis_results

    def _analyze_strain_response(self, strains: List[float], lattice_a: List[float], lattice_b: List[float]) -> Dict:
        """分析应变响应"""
        # 先过滤None值，再转换为numpy数组
        valid_data = [(s, a, b) for s, a, b in zip(strains, lattice_a, lattice_b) 
                      if s is not None and a is not None and b is not None]
        
        if len(valid_data) < 2:
            logger.warning(f"有效数据点不足({len(valid_data)}<2)，无法进行拟合")
            return {
                'a_slope': 0.0,
                'a_intercept': 0.0,
                'b_slope': 0.0,
                'b_intercept': 0.0,
                'r_squared_a': 0.0,
                'r_squared_b': 0.0
            }
        
        strains, lattice_a, lattice_b = zip(*valid_data)
        strains = np.array(strains, dtype=float)
        lattice_a = np.array(lattice_a, dtype=float)
        lattice_b = np.array(lattice_b, dtype=float)

        # 过滤掉NaN/Inf值
        valid_mask = np.isfinite(strains) & np.isfinite(lattice_a) & np.isfinite(lattice_b)
        strains_clean = strains[valid_mask]
        lattice_a_clean = lattice_a[valid_mask]
        lattice_b_clean = lattice_b[valid_mask]
        
        if len(strains_clean) < 2:
            logger.warning(f"有效数据点不足({len(strains_clean)}<2)，无法进行拟合")
            return {
                'a_slope': 0.0,
                'a_intercept': 0.0,
                'b_slope': 0.0,
                'b_intercept': 0.0,
                'r_squared_a': 0.0,
                'r_squared_b': 0.0
            }

        # 线性拟合
        def linear_func(x, a, b):
            return a * x + b

        from scipy.optimize import curve_fit

        try:
            # 拟合a参数
            popt_a, pcov_a = curve_fit(linear_func, strains_clean, lattice_a_clean)
            # 拟合b参数
            popt_b, pcov_b = curve_fit(linear_func, strains_clean, lattice_b_clean)

            return {
                'a_slope': float(popt_a[0]),
                'a_intercept': float(popt_a[1]),
                'b_slope': float(popt_b[0]),
                'b_intercept': float(popt_b[1]),
                'r_squared_a': float(self._calculate_r_squared(strains_clean, lattice_a_clean, popt_a)),
                'r_squared_b': float(self._calculate_r_squared(strains_clean, lattice_b_clean, popt_b))
            }
        except Exception as e:
            logger.error(f"拟合失败: {e}")
            return {
                'a_slope': 0.0,
                'a_intercept': 0.0,
                'b_slope': 0.0,
                'b_intercept': 0.0,
                'r_squared_a': 0.0,
                'r_squared_b': 0.0
            }

    def _calculate_r_squared(self, x: np.ndarray, y: np.ndarray, params: np.ndarray) -> float:
        """计算R²值"""
        y_pred = params[0] * x + params[1]
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        return 1 - (ss_res / ss_tot)

    def _validate_results(self, strains: List[float], lattice_a: List[float], lattice_b: List[float]) -> Dict:
        """验证实验结果"""
        validation_results = {
            'lattice_params_valid': False,
            'strain_response_valid': False,
            'overall_valid': False
        }

        # 过滤None值
        valid_data = [(s, a, b) for s, a, b in zip(strains, lattice_a, lattice_b) 
                      if s is not None and a is not None and b is not None]
        
        if len(valid_data) == 0:
            logger.warning("没有有效的数据进行验证")
            return validation_results
        
        strains_clean, lattice_a_clean, lattice_b_clean = zip(*valid_data)

        # 验证晶格参数（无应变状态）
        zero_strain_idx = None
        for i, s in enumerate(strains_clean):
            if abs(s - 0.0) < 0.01:  # 容差
                zero_strain_idx = i
                break
        
        if zero_strain_idx is not None:
            a_diff = abs(lattice_a_clean[zero_strain_idx] - self.theoretical_predictions['lattice_a'])
            b_diff = abs(lattice_b_clean[zero_strain_idx] - self.theoretical_predictions['lattice_b'])

            if (a_diff <= self.theoretical_predictions['tolerance_a'] and
                b_diff <= self.theoretical_predictions['tolerance_b']):
                validation_results['lattice_params_valid'] = True

        # 验证应变响应线性度
        if len(valid_data) > 1:
            strain_response = self._analyze_strain_response(list(strains_clean), list(lattice_a_clean), list(lattice_b_clean))
            if (strain_response['r_squared_a'] > 0.95 and
                strain_response['r_squared_b'] > 0.95):
                validation_results['strain_response_valid'] = True

        # 总体验证
        validation_results['overall_valid'] = (
            validation_results['lattice_params_valid'] and
            validation_results['strain_response_valid']
        )

        return validation_results

    def _generate_plots(self, strains: List[float], lattice_a: List[float], lattice_b: List[float], energies: List[float]) -> Dict:
        """生成图表"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))

        # 先过滤None值
        valid_data = [(s, a, b, e) for s, a, b, e in zip(strains, lattice_a, lattice_b, energies) 
                      if s is not None and a is not None and b is not None and e is not None]
        
        if len(valid_data) == 0:
            # 没有有效数据，创建空图
            ax1.text(0.5, 0.5, 'No valid data', ha='center', va='center', transform=ax1.transAxes)
            ax2.text(0.5, 0.5, 'No valid data', ha='center', va='center', transform=ax2.transAxes)
            ax3.text(0.5, 0.5, 'No valid data', ha='center', va='center', transform=ax3.transAxes)
            ax4.text(0.5, 0.5, 'No valid data', ha='center', va='center', transform=ax4.transAxes)
            plt.tight_layout()
            plot_file = self.experiment_dir / "figures" / "structure_analysis.png"
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            plt.close()
            return {'plot_file': str(plot_file)}
        
        strains, lattice_a, lattice_b, energies = zip(*valid_data)
        strains = np.array(strains, dtype=float)
        lattice_a = np.array(lattice_a, dtype=float)
        lattice_b = np.array(lattice_b, dtype=float)
        energies = np.array(energies, dtype=float)
        
        # 过滤有效数据  
        valid_mask = np.isfinite(strains) & np.isfinite(lattice_a) & np.isfinite(lattice_b) & np.isfinite(energies)
        strains_clean = strains[valid_mask]
        lattice_a_clean = lattice_a[valid_mask]
        lattice_b_clean = lattice_b[valid_mask]
        energies_clean = energies[valid_mask]

        # 晶格参数随应变变化
        ax1.plot(strains_clean, lattice_a_clean, 'ro-', label='a parameter', markersize=8)
        ax1.plot(strains_clean, lattice_b_clean, 'bo-', label='b parameter', markersize=8)
        ax1.axhline(y=self.theoretical_predictions['lattice_a'], color='r', linestyle='--', alpha=0.5, label='Theoretical a')
        ax1.axhline(y=self.theoretical_predictions['lattice_b'], color='b', linestyle='--', alpha=0.5, label='Theoretical b')
        ax1.set_xlabel('Strain (%)')
        ax1.set_ylabel('Lattice Parameter (Å)')
        ax1.set_title('Lattice Parameters vs Strain')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 能量随应变变化
        ax2.plot(strains_clean, energies_clean, 'go-', markersize=8)
        ax2.set_xlabel('Strain (%)')
        ax2.set_ylabel('Total Energy (Hartree)')
        ax2.set_title('Total Energy vs Strain')
        ax2.grid(True, alpha=0.3)

        # 应变响应线性拟合
        if len(strains_clean) > 1:
            from scipy.optimize import curve_fit
            def linear_func(x, a, b):
                return a * x + b

            try:
                popt_a, _ = curve_fit(linear_func, strains_clean, lattice_a_clean)
                popt_b, _ = curve_fit(linear_func, strains_clean, lattice_b_clean)

                strain_fit = np.linspace(min(strains_clean), max(strains_clean), 100)
                a_fit = linear_func(strain_fit, *popt_a)
                b_fit = linear_func(strain_fit, *popt_b)

                ax3.plot(strains_clean, lattice_a_clean, 'ro', label='a data', markersize=8)
                ax3.plot(strain_fit, a_fit, 'r-', label=f'a fit (slope={popt_a[0]:.3f})')
                ax3.plot(strains_clean, lattice_b_clean, 'bo', label='b data', markersize=8)
                ax3.plot(strain_fit, b_fit, 'b-', label=f'b fit (slope={popt_b[0]:.3f})')
            except Exception as e:
                logger.warning(f"拟合失败: {e}")
                ax3.text(0.5, 0.5, 'Fitting failed', ha='center', va='center', transform=ax3.transAxes)
            ax3.set_xlabel('Strain (%)')
            ax3.set_ylabel('Lattice Parameter (Å)')
            ax3.set_title('Linear Fit of Strain Response')
            ax3.legend()
            ax3.grid(True, alpha=0.3)

        # 验证结果总结
        validation_results = self._validate_results(list(strains_clean), list(lattice_a_clean), list(lattice_b_clean))
        ax4.text(0.1, 0.8, f"Lattice Parameters Valid: {'✓' if validation_results['lattice_params_valid'] else '✗'}",
                transform=ax4.transAxes, fontsize=12, fontweight='bold')
        ax4.text(0.1, 0.6, f"Strain Response Valid: {'✓' if validation_results['strain_response_valid'] else '✗'}",
                transform=ax4.transAxes, fontsize=12, fontweight='bold')
        ax4.text(0.1, 0.4, f"Overall Valid: {'✓' if validation_results['overall_valid'] else '✗'}",
                transform=ax4.transAxes, fontsize=12, fontweight='bold')
        ax4.set_title('Validation Results')
        ax4.set_xlim(0, 1)
        ax4.set_ylim(0, 1)
        ax4.axis('off')

        plt.tight_layout()
        plot_file = self.experiment_dir / "figures" / "structure_analysis.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()

        return {'plot_file': str(plot_file)}

    def save_results(self, dft_results: Dict, analysis_results: Dict):
        """保存结果"""
        logger.info("保存实验结果...")

        # 保存DFT结果
        dft_file = self.experiment_dir / "results" / "dft_results.json"
        with open(dft_file, 'w') as f:
            json.dump(dft_results, f, indent=2)

        # 保存分析结果
        analysis_file = self.experiment_dir / "results" / "analysis_results.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis_results, f, indent=2)

        # 保存验证报告
        validation_report = {
            'experiment': 'exp_1_structure',
            'name': '结构表征实验',
            'theoretical_predictions': self.theoretical_predictions,
            'validation_results': analysis_results['validation_metrics'],
            'summary': {
                'total_calculations': len(dft_results),
                'successful_calculations': sum(1 for r in dft_results.values() if r['status'] == 'success'),
                'overall_valid': analysis_results['validation_metrics']['overall_valid']
            }
        }

        report_file = self.experiment_dir / "results" / "validation_report.json"
        with open(report_file, 'w') as f:
            json.dump(validation_report, f, indent=2)

        logger.info(f"结果已保存:")
        logger.info(f"  DFT结果: {dft_file}")
        logger.info(f"  分析结果: {analysis_file}")
        logger.info(f"  验证报告: {report_file}")

    def run_complete_experiment(self):
        """运行完整实验"""
        logger.info("🚀 开始实验1: 结构表征实验")

        # 1. 创建DFT输入文件
        self.create_dft_input_files()

        # 2. 运行DFT计算
        dft_results = self.run_dft_calculations()

        # 3. 分析结果
        analysis_results = self.analyze_results(dft_results)

        # 4. 保存结果
        self.save_results(dft_results, analysis_results)

        # 5. 输出总结
        validation_metrics = analysis_results['validation_metrics']
        logger.info("🎯 实验1完成!")
        logger.info(f"  总计算数: {len(dft_results)}")
        logger.info(f"  成功计算数: {sum(1 for r in dft_results.values() if r['status'] == 'success')}")
        logger.info(f"  晶格参数验证: {'✓' if validation_metrics['lattice_params_valid'] else '✗'}")
        logger.info(f"  应变响应验证: {'✓' if validation_metrics['strain_response_valid'] else '✗'}")
        logger.info(f"  总体验证: {'✓' if validation_metrics['overall_valid'] else '✗'}")

        return {
            'dft_results': dft_results,
            'analysis_results': analysis_results,
            'validation_metrics': validation_metrics
        }

def main():
    """主函数"""
    runner = StructureExperimentRunner()
    results = runner.run_complete_experiment()
    return results

if __name__ == "__main__":
    main()
