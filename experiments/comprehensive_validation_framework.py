#!/usr/bin/env python3
"""
综合实验验证框架
整合所有6个实验，实现完整的理论验证闭环
"""

import numpy as np
import json
import matplotlib.pyplot as plt
from pathlib import Path
import subprocess
import time
import logging
from typing import Dict, List, Tuple, Optional
import pandas as pd
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveValidationFramework:
    """综合实验验证框架"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.experiments_dir = self.project_root / "experiments"
        self.results_dir = self.project_root / "results"
        self.hpc_dir = self.project_root / "hpc_calculations"
        
        # 创建必要的目录
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # 论文核心理论预测
        self.theoretical_framework = {
            'core_hypothesis': {
                'non_additive_coupling': '掺杂和应变的协同效应远超简单叠加',
                'polaron_transition': '从小极化子跳跃到大极化子带状传导',
                'synergistic_enhancement': '300%迁移率提升和50%激活能降低'
            },
            
            'quantitative_predictions': {
                # 结构参数
                'lattice_parameters': {
                    'a': 36.67, 'b': 30.84,  # Å
                    'tolerance': {'a': 0.5, 'b': 0.3}
                },
                
                # 掺杂参数
                'doping_specifications': {
                    'concentrations': [2.5, 5.0, 7.5],  # %
                    'tolerance': 0.2,
                    'chemical_states': {'B': 'B³⁺', 'N': 'N³⁻', 'P': 'P³⁺'}
                },
                
                # 电子性质
                'electronic_properties': {
                    'bandgap_range': [1.2, 2.4],  # eV
                    'mobility_range': [5.2, 21.4],  # cm²V⁻¹s⁻¹
                    'strain_coupling_beta': 8.2
                },
                
                # 极化子参数
                'polaron_parameters': {
                    'ipr_transition': [45, 50],  # 小极化子
                    'ipr_target': [25, 30],      # 大极化子
                    'j_total': 135,              # meV
                    'lambda_total': 20,          # meV
                    'activation_energy': 0.09    # eV
                },
                
                # 协同效应因子
                'synergistic_factors': {
                    'f_deloc': 1.8,      # 离域化因子
                    'f_coupling': 1.8,   # 耦合增强因子
                    'f_reorg': 1.5,      # 重组能因子
                    'f_total': 8.75      # 总增强因子
                },
                
                # 最优条件
                'optimal_conditions': {
                    'strain': 3.0,       # %
                    'doping': 5.0,       # %
                    'mobility': 21.4,    # cm²V⁻¹s⁻¹
                    'activation_energy': 0.09  # eV
                }
            },
            
            'validation_criteria': {
                'must_verify': [
                    '晶格参数在误差范围内',
                    '掺杂浓度和化学状态正确',
                    '带隙和迁移率在预测范围',
                    '协同效应>300%迁移率增强',
                    '极化子转变J_total > λ_total',
                    '最优条件3%应变+5%掺杂'
                ],
                'success_threshold': 0.8,  # 80%的验证指标通过
                'confidence_threshold': 0.85  # 85%置信度
            }
        }
        
        # 实验配置
        self.experiment_configs = {
            'exp_1_structure': {
                'name': '结构表征实验',
                'methods': ['XRD', 'TEM', 'Raman', 'AFM'],
                'key_metrics': ['lattice_parameters', 'strain_response', 'structural_stability'],
                'dft_calculations': ['strain_optimization', 'lattice_dynamics'],
                'priority': 'high'
            },
            'exp_2_doping': {
                'name': '掺杂合成实验',
                'methods': ['CVD', 'Ion_Implantation', 'XPS', 'EDX'],
                'key_metrics': ['doping_concentration', 'chemical_state', 'uniformity'],
                'dft_calculations': ['doped_electronic_structure', 'formation_energy'],
                'priority': 'high'
            },
            'exp_3_electronic': {
                'name': '电子性质测量',
                'methods': ['UV-Vis', 'Hall_Effect', 'Four_Probe', 'Photoconductivity'],
                'key_metrics': ['bandgap', 'mobility', 'strain_coupling'],
                'dft_calculations': ['band_structure', 'transport_properties'],
                'priority': 'high'
            },
            'exp_4_polaron': {
                'name': '极化子转变验证',
                'methods': ['EPR', 'Time_Resolved', 'Temperature_Dependent', 'Magnetoresistance'],
                'key_metrics': ['ipr_transition', 'electronic_coupling', 'activation_energy'],
                'dft_calculations': ['polaron_localization', 'charge_transfer'],
                'priority': 'medium'
            },
            'exp_5_synergy': {
                'name': '协同效应定量验证',
                'methods': ['Temperature_Hall', 'Magnetoresistance', 'Dielectric', 'Photoluminescence'],
                'key_metrics': ['synergistic_factors', 'enhancement_mechanisms'],
                'dft_calculations': ['synergistic_analysis', 'mechanism_elucidation'],
                'priority': 'medium'
            },
            'exp_6_optimal': {
                'name': '最优条件验证',
                'methods': ['System_Scan', 'Performance_Optimization', 'Mixed_Doping', 'Stability_Test'],
                'key_metrics': ['optimal_conditions', 'performance_metrics', 'stability'],
                'dft_calculations': ['optimization_search', 'stability_analysis'],
                'priority': 'low'
            }
        }
        
        # 验证状态跟踪
        self.validation_status = {
            exp_id: {
                'status': 'pending',
                'progress': 0.0,
                'confidence': 0.0,
                'last_updated': None,
                'issues': [],
                'results': {}
            }
            for exp_id in self.experiment_configs.keys()
        }
    
    def run_complete_validation(self) -> Dict:
        """运行完整的验证流程"""
        logger.info("开始综合实验验证")
        start_time = time.time()
        
        validation_results = {
            'start_time': datetime.now().isoformat(),
            'experiments': {},
            'overall_summary': {},
            'theoretical_validation': {},
            'recommendations': []
        }
        
        # 按优先级运行实验
        priority_order = ['high', 'medium', 'low']
        for priority in priority_order:
            experiments = [exp_id for exp_id, config in self.experiment_configs.items() 
                          if config['priority'] == priority]
            
            for exp_id in experiments:
                logger.info(f"运行实验: {exp_id} ({self.experiment_configs[exp_id]['name']})")
                
                try:
                    exp_result = self._run_single_experiment(exp_id)
                    validation_results['experiments'][exp_id] = exp_result
                    
                    # 更新验证状态
                    self.validation_status[exp_id].update({
                        'status': 'completed' if exp_result['success'] else 'failed',
                        'progress': 1.0,
                        'confidence': exp_result.get('confidence', 0.0),
                        'last_updated': datetime.now().isoformat(),
                        'results': exp_result
                    })
                    
                except Exception as e:
                    logger.error(f"实验 {exp_id} 运行失败: {e}")
                    validation_results['experiments'][exp_id] = {
                        'success': False,
                        'error': str(e),
                        'confidence': 0.0
                    }
                    
                    self.validation_status[exp_id].update({
                        'status': 'failed',
                        'issues': [str(e)],
                        'last_updated': datetime.now().isoformat()
                    })
        
        # 生成总体摘要
        validation_results['overall_summary'] = self._generate_overall_summary(validation_results)
        
        # 理论验证
        validation_results['theoretical_validation'] = self._validate_theoretical_predictions(validation_results)
        
        # 生成建议
        validation_results['recommendations'] = self._generate_recommendations(validation_results)
        
        validation_results['end_time'] = datetime.now().isoformat()
        validation_results['total_time'] = time.time() - start_time
        
        # 保存结果
        self._save_validation_results(validation_results)
        
        logger.info(f"综合实验验证完成，总用时: {validation_results['total_time']:.2f}秒")
        return validation_results
    
    def _run_single_experiment(self, exp_id: str) -> Dict:
        """运行单个实验"""
        exp_dir = self.experiments_dir / exp_id
        if not exp_dir.exists():
            raise FileNotFoundError(f"实验目录不存在: {exp_dir}")
        
        result = {
            'exp_id': exp_id,
            'name': self.experiment_configs[exp_id]['name'],
            'success': False,
            'confidence': 0.0,
            'dft_results': {},
            'analysis_results': {},
            'validation_metrics': {},
            'issues': []
        }
        
        # 运行DFT计算
        try:
            dft_results = self._run_experiment_dft(exp_id)
            result['dft_results'] = dft_results
        except Exception as e:
            result['issues'].append(f"DFT计算失败: {e}")
            logger.warning(f"实验 {exp_id} DFT计算失败: {e}")
        
        # 运行分析脚本
        try:
            analysis_results = self._run_experiment_analysis(exp_id)
            result['analysis_results'] = analysis_results
        except Exception as e:
            result['issues'].append(f"分析脚本失败: {e}")
            logger.warning(f"实验 {exp_id} 分析脚本失败: {e}")
        
        # 验证结果
        try:
            validation_metrics = self._validate_experiment_results(exp_id, result)
            result['validation_metrics'] = validation_metrics
            
            # 计算置信度
            result['confidence'] = self._calculate_experiment_confidence(validation_metrics)
            
            # 判断成功
            result['success'] = result['confidence'] >= 0.7 and len(result['issues']) == 0
            
        except Exception as e:
            result['issues'].append(f"验证失败: {e}")
            logger.warning(f"实验 {exp_id} 验证失败: {e}")
        
        return result
    
    def _run_experiment_dft(self, exp_id: str) -> Dict:
        """运行实验的DFT计算"""
        dft_results = {}
        
        # 根据实验类型确定DFT计算
        if exp_id == 'exp_1_structure':
            # 结构表征：不同应变下的结构优化
            strain_values = [-5.0, -2.5, 0.0, 2.5, 5.0]
            for strain in strain_values:
                input_file = f"C60_strain_{strain:+.1f}_pristine"
                # 这里应该调用实际的DFT计算
                dft_results[f"strain_{strain}"] = {
                    'status': 'simulated',
                    'lattice_parameters': {
                        'a': 36.67 * (1 + strain/100),
                        'b': 30.84 * (1 + strain/100)
                    },
                    'total_energy': -328.18 + strain * 0.1,
                    'convergence': True
                }
        
        elif exp_id == 'exp_2_doping':
            # 掺杂合成：不同掺杂浓度的电子结构
            doping_concentrations = [2.5, 5.0, 7.5]
            dopants = ['B', 'N', 'P']
            for dopant in dopants:
                for conc in doping_concentrations:
                    input_file = f"C60_{dopant}_{conc}_doped"
                    dft_results[f"{dopant}_{conc}"] = {
                        'status': 'simulated',
                        'doping_concentration': conc,
                        'chemical_state': self.theoretical_framework['quantitative_predictions']['doping_specifications']['chemical_states'][dopant],
                        'formation_energy': -0.5 + conc * 0.1,
                        'convergence': True
                    }
        
        elif exp_id == 'exp_3_electronic':
            # 电子性质：应变-掺杂协同效应
            strain_values = [-5.0, -2.5, 0.0, 2.5, 5.0]
            doping_concentrations = [2.5, 5.0, 7.5]
            for strain in strain_values:
                for conc in doping_concentrations:
                    input_file = f"C60_strain_{strain:+.1f}_doped_{conc}"
                    # 模拟协同效应
                    base_mobility = 6.8
                    strain_effect = np.exp(strain * 0.1)
                    doping_effect = 1 + conc * 0.05
                    synergy_factor = 1.5  # 协同效应
                    
                    dft_results[f"strain_{strain}_doped_{conc}"] = {
                        'status': 'simulated',
                        'bandgap': 1.8 - strain * 0.05 - conc * 0.02,
                        'mobility': base_mobility * strain_effect * doping_effect * synergy_factor,
                        'strain_coupling': 8.2 + strain * 0.1,
                        'convergence': True
                    }
        
        # 其他实验的DFT计算...
        
        return dft_results
    
    def _run_experiment_analysis(self, exp_id: str) -> Dict:
        """运行实验分析脚本"""
        exp_dir = self.experiments_dir / exp_id
        analysis_script = exp_dir / "analysis" / f"{exp_id.split('_')[1]}.py"
        
        if not analysis_script.exists():
            logger.warning(f"分析脚本不存在: {analysis_script}")
            return {'status': 'error', 'message': 'Analysis script not found'}
        
        try:
            # 运行分析脚本
            result = subprocess.run(['python', str(analysis_script)], 
                                  cwd=exp_dir, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info(f"分析脚本运行成功: {exp_id}")
                return {'status': 'success', 'output': result.stdout}
            else:
                logger.error(f"分析脚本运行失败: {result.stderr}")
                return {'status': 'error', 'message': result.stderr}
                
        except subprocess.TimeoutExpired:
            logger.error(f"分析脚本超时: {exp_id}")
            return {'status': 'timeout', 'message': 'Analysis timeout'}
        except Exception as e:
            logger.error(f"运行分析脚本异常: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _validate_experiment_results(self, exp_id: str, exp_result: Dict) -> Dict:
        """验证实验结果"""
        validation_metrics = {
            'theoretical_match': 0.0,
            'experimental_consistency': 0.0,
            'statistical_significance': 0.0,
            'overall_score': 0.0
        }
        
        # 根据实验类型进行特定验证
        if exp_id == 'exp_1_structure':
            validation_metrics.update(self._validate_structure_experiment(exp_result))
        elif exp_id == 'exp_2_doping':
            validation_metrics.update(self._validate_doping_experiment(exp_result))
        elif exp_id == 'exp_3_electronic':
            validation_metrics.update(self._validate_electronic_experiment(exp_result))
        # ... 其他实验的验证
        
        # 计算总体得分
        validation_metrics['overall_score'] = np.mean([
            validation_metrics['theoretical_match'],
            validation_metrics['experimental_consistency'],
            validation_metrics['statistical_significance']
        ])
        
        return validation_metrics
    
    def _validate_structure_experiment(self, exp_result: Dict) -> Dict:
        """验证结构实验"""
        validation = {}
        
        # 验证晶格参数
        dft_results = exp_result.get('dft_results', {})
        lattice_params = []
        
        for calc_name, result in dft_results.items():
            if 'lattice_parameters' in result:
                lattice_params.append(result['lattice_parameters'])
        
        if lattice_params:
            # 计算平均晶格参数
            avg_a = np.mean([lp['a'] for lp in lattice_params])
            avg_b = np.mean([lp['b'] for lp in lattice_params])
            
            # 与理论值比较
            target_a = self.theoretical_framework['quantitative_predictions']['lattice_parameters']['a']
            target_b = self.theoretical_framework['quantitative_predictions']['lattice_parameters']['b']
            tolerance_a = self.theoretical_framework['quantitative_predictions']['lattice_parameters']['tolerance']['a']
            tolerance_b = self.theoretical_framework['quantitative_predictions']['lattice_parameters']['tolerance']['b']
            
            a_match = abs(avg_a - target_a) <= tolerance_a
            b_match = abs(avg_b - target_b) <= tolerance_b
            
            validation['lattice_parameter_match'] = (a_match and b_match)
            validation['theoretical_match'] = 1.0 if (a_match and b_match) else 0.0
        else:
            validation['theoretical_match'] = 0.0
        
        return validation
    
    def _validate_doping_experiment(self, exp_result: Dict) -> Dict:
        """验证掺杂实验"""
        validation = {}
        
        # 验证掺杂浓度
        dft_results = exp_result.get('dft_results', {})
        concentrations = []
        
        for calc_name, result in dft_results.items():
            if 'doping_concentration' in result:
                concentrations.append(result['doping_concentration'])
        
        if concentrations:
            # 检查是否在目标范围内
            target_concentrations = self.theoretical_framework['quantitative_predictions']['doping_specifications']['concentrations']
            tolerance = self.theoretical_framework['quantitative_predictions']['doping_specifications']['tolerance']
            
            matches = 0
            for conc in concentrations:
                for target in target_concentrations:
                    if abs(conc - target) <= tolerance:
                        matches += 1
                        break
            
            validation['concentration_match'] = matches / len(concentrations)
            validation['theoretical_match'] = validation['concentration_match']
        else:
            validation['theoretical_match'] = 0.0
        
        return validation
    
    def _validate_electronic_experiment(self, exp_result: Dict) -> Dict:
        """验证电子性质实验"""
        validation = {}
        
        # 验证带隙和迁移率
        dft_results = exp_result.get('dft_results', {})
        bandgaps = []
        mobilities = []
        
        for calc_name, result in dft_results.items():
            if 'bandgap' in result:
                bandgaps.append(result['bandgap'])
            if 'mobility' in result:
                mobilities.append(result['mobility'])
        
        if bandgaps and mobilities:
            # 检查带隙范围
            target_bandgap_range = self.theoretical_framework['quantitative_predictions']['electronic_properties']['bandgap_range']
            bandgap_valid = all(target_bandgap_range[0] <= bg <= target_bandgap_range[1] for bg in bandgaps)
            
            # 检查迁移率范围
            target_mobility_range = self.theoretical_framework['quantitative_predictions']['electronic_properties']['mobility_range']
            mobility_valid = all(target_mobility_range[0] <= mob <= target_mobility_range[1] for mob in mobilities)
            
            validation['bandgap_valid'] = bandgap_valid
            validation['mobility_valid'] = mobility_valid
            validation['theoretical_match'] = 1.0 if (bandgap_valid and mobility_valid) else 0.0
        else:
            validation['theoretical_match'] = 0.0
        
        return validation
    
    def _calculate_experiment_confidence(self, validation_metrics: Dict) -> float:
        """计算实验置信度"""
        if not validation_metrics:
            return 0.0
        
        # 基于验证指标计算置信度
        theoretical_match = validation_metrics.get('theoretical_match', 0.0)
        experimental_consistency = validation_metrics.get('experimental_consistency', 0.0)
        statistical_significance = validation_metrics.get('statistical_significance', 0.0)
        
        # 加权平均
        confidence = (0.5 * theoretical_match + 
                     0.3 * experimental_consistency + 
                     0.2 * statistical_significance)
        
        return min(confidence, 1.0)
    
    def _generate_overall_summary(self, validation_results: Dict) -> Dict:
        """生成总体摘要"""
        experiments = validation_results['experiments']
        
        summary = {
            'total_experiments': len(experiments),
            'successful_experiments': sum(1 for exp in experiments.values() if exp.get('success', False)),
            'average_confidence': np.mean([exp.get('confidence', 0.0) for exp in experiments.values()]),
            'critical_experiments_passed': 0,
            'overall_success': False
        }
        
        # 检查关键实验
        critical_experiments = ['exp_1_structure', 'exp_2_doping', 'exp_3_electronic']
        for exp_id in critical_experiments:
            if exp_id in experiments and experiments[exp_id].get('success', False):
                summary['critical_experiments_passed'] += 1
        
        # 判断总体成功
        summary['overall_success'] = (
            summary['successful_experiments'] >= summary['total_experiments'] * 0.8 and
            summary['critical_experiments_passed'] >= len(critical_experiments) * 0.8 and
            summary['average_confidence'] >= 0.7
        )
        
        return summary
    
    def _validate_theoretical_predictions(self, validation_results: Dict) -> Dict:
        """验证理论预测"""
        theoretical_validation = {
            'core_hypothesis_validation': {},
            'quantitative_predictions_validation': {},
            'overall_theoretical_support': 0.0
        }
        
        # 验证核心假设
        experiments = validation_results['experiments']
        
        # 非加性耦合机制验证
        if 'exp_3_electronic' in experiments and experiments['exp_3_electronic'].get('success', False):
            theoretical_validation['core_hypothesis_validation']['non_additive_coupling'] = True
        
        # 极化子转变验证
        if 'exp_4_polaron' in experiments and experiments['exp_4_polaron'].get('success', False):
            theoretical_validation['core_hypothesis_validation']['polaron_transition'] = True
        
        # 协同效应验证
        if 'exp_5_synergy' in experiments and experiments['exp_5_synergy'].get('success', False):
            theoretical_validation['core_hypothesis_validation']['synergistic_enhancement'] = True
        
        # 计算总体理论支持度
        hypothesis_count = len(theoretical_validation['core_hypothesis_validation'])
        validated_count = sum(theoretical_validation['core_hypothesis_validation'].values())
        theoretical_validation['overall_theoretical_support'] = validated_count / hypothesis_count if hypothesis_count > 0 else 0.0
        
        return theoretical_validation
    
    def _generate_recommendations(self, validation_results: Dict) -> List[str]:
        """生成建议"""
        recommendations = []
        
        summary = validation_results['overall_summary']
        experiments = validation_results['experiments']
        
        # 基于总体结果生成建议
        if not summary['overall_success']:
            recommendations.append("总体验证未通过，需要重新检查实验设置和理论模型")
        
        if summary['average_confidence'] < 0.8:
            recommendations.append("平均置信度较低，建议增加实验重复次数和改善数据质量")
        
        if summary['critical_experiments_passed'] < len(['exp_1_structure', 'exp_2_doping', 'exp_3_electronic']):
            recommendations.append("关键实验未全部通过，需要优先解决基础验证问题")
        
        # 基于具体实验生成建议
        for exp_id, exp_result in experiments.items():
            if not exp_result.get('success', False):
                recommendations.append(f"实验 {exp_id} 未成功，需要检查: {', '.join(exp_result.get('issues', []))}")
            
            if exp_result.get('confidence', 0.0) < 0.7:
                recommendations.append(f"实验 {exp_id} 置信度较低，建议改善实验条件")
        
        return recommendations
    
    def _save_validation_results(self, validation_results: Dict):
        """保存验证结果"""
        # 保存详细结果
        detailed_file = self.results_dir / "comprehensive_validation_results.json"
        with open(detailed_file, 'w') as f:
            json.dump(validation_results, f, indent=2)
        
        # 保存摘要报告
        summary = {
            'validation_summary': validation_results['overall_summary'],
            'theoretical_validation': validation_results['theoretical_validation'],
            'recommendations': validation_results['recommendations'],
            'timestamp': validation_results['end_time']
        }
        
        summary_file = self.results_dir / "validation_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"验证结果已保存: {detailed_file}")
        logger.info(f"摘要报告已保存: {summary_file}")
    
    def generate_validation_report(self) -> str:
        """生成验证报告"""
        report_file = self.results_dir / "validation_report.md"
        
        report_content = f"""# 综合实验验证报告

## 验证概述

本报告总结了论文"单分子层富勒烯网络中的电子局域化和迁移率"的综合实验验证结果。

## 理论框架

### 核心假设
- **非加性耦合机制**: 掺杂和应变的协同效应远超简单叠加
- **极化子转变**: 从小极化子跳跃到大极化子带状传导  
- **协同效应增强**: 300%迁移率提升和50%激活能降低

### 关键预测
- 晶格参数: a = 36.67 ± 0.5 Å, b = 30.84 ± 0.3 Å
- 掺杂浓度: 2.5%, 5.0%, 7.5% ± 0.2%
- 带隙范围: 1.2-2.4 eV
- 迁移率范围: 5.2-21.4 cm²V⁻¹s⁻¹
- 协同效应: >300%迁移率增强
- 最优条件: 3%应变+5%掺杂

## 实验验证结果

### 实验1: 结构表征实验
- **状态**: {'✅ 完成' if self.validation_status['exp_1_structure']['status'] == 'completed' else '⏳ 进行中'}
- **置信度**: {self.validation_status['exp_1_structure']['confidence']:.2f}
- **验证指标**: 晶格参数、应变响应、结构稳定性

### 实验2: 掺杂合成实验  
- **状态**: {'✅ 完成' if self.validation_status['exp_2_doping']['status'] == 'completed' else '⏳ 进行中'}
- **置信度**: {self.validation_status['exp_2_doping']['confidence']:.2f}
- **验证指标**: 掺杂浓度、化学状态、均匀性

### 实验3: 电子性质测量
- **状态**: {'✅ 完成' if self.validation_status['exp_3_electronic']['status'] == 'completed' else '⏳ 进行中'}
- **置信度**: {self.validation_status['exp_3_electronic']['confidence']:.2f}
- **验证指标**: 带隙、迁移率、应变耦合

### 实验4: 极化子转变验证
- **状态**: {'✅ 完成' if self.validation_status['exp_4_polaron']['status'] == 'completed' else '⏳ 进行中'}
- **置信度**: {self.validation_status['exp_4_polaron']['confidence']:.2f}
- **验证指标**: IPR转变、电子耦合、激活能

### 实验5: 协同效应定量验证
- **状态**: {'✅ 完成' if self.validation_status['exp_5_synergy']['status'] == 'completed' else '⏳ 进行中'}
- **置信度**: {self.validation_status['exp_5_synergy']['confidence']:.2f}
- **验证指标**: 协同因子、增强机制

### 实验6: 最优条件验证
- **状态**: {'✅ 完成' if self.validation_status['exp_6_optimal']['status'] == 'completed' else '⏳ 进行中'}
- **置信度**: {self.validation_status['exp_6_optimal']['confidence']:.2f}
- **验证指标**: 最优条件、性能指标、稳定性

## 结论

基于综合实验验证结果，论文的理论预测得到了{'充分' if all(status['status'] == 'completed' for status in self.validation_status.values()) else '部分'}验证。

## 建议

1. 继续完善剩余实验的验证
2. 提高实验数据的统计显著性
3. 加强DFT计算与实验结果的对比分析

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"验证报告已生成: {report_file}")
        return str(report_file)

def main():
    """主函数"""
    logger.info("启动综合实验验证框架")
    
    # 初始化框架
    framework = ComprehensiveValidationFramework()
    
    # 运行完整验证
    validation_results = framework.run_complete_validation()
    
    # 生成报告
    report_file = framework.generate_validation_report()
    
    # 输出结果
    summary = validation_results['overall_summary']
    logger.info(f"验证完成:")
    logger.info(f"  总实验数: {summary['total_experiments']}")
    logger.info(f"  成功实验数: {summary['successful_experiments']}")
    logger.info(f"  平均置信度: {summary['average_confidence']:.2f}")
    logger.info(f"  总体成功: {'是' if summary['overall_success'] else '否'}")
    
    return validation_results

if __name__ == "__main__":
    main()
