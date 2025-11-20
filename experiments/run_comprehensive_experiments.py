#!/usr/bin/env python3
"""
综合实验运行器 - 依次运行所有实验
运行实验1-6的真实实验脚本并生成综合报告
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

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveExperimentRunner:
    """综合实验运行器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.experiments_dir = self.project_root / "experiments"
        
        # 实验配置
        self.experiments = {
            'exp_1_structure': {
                'name': '结构表征实验',
                'script': 'exp_1_structure/run_structure_experiment.py',
                'description': '验证qHP C₆₀网络的结构参数和应变响应'
            },
            'exp_2_doping': {
                'name': '掺杂合成实验',
                'script': 'exp_2_doping/run_doping_experiment.py',
                'description': '验证qHP C₆₀网络的掺杂合成和化学状态'
            },
            'exp_3_electronic': {
                'name': '电子性质测量实验',
                'script': 'exp_3_electronic/run_electronic_experiment.py',
                'description': '验证电子性质和协同效应'
            },
            'exp_4_polaron': {
                'name': '极化子转变验证实验',
                'script': 'exp_4_polaron/run_polaron_experiment.py',
                'description': '验证极化子转变机制'
            },
            'exp_5_synergy': {
                'name': '协同效应定量验证实验',
                'script': 'exp_5_synergy/run_synergy_experiment.py',
                'description': '验证应变-掺杂协同效应'
            },
            'exp_6_optimal': {
                'name': '最优条件验证实验',
                'script': 'exp_6_optimal/run_optimal_experiment.py',
                'description': '验证最优掺杂条件'
            }
        }
        
        # 创建结果目录
        self.results_dir = self.experiments_dir / "comprehensive_results"
        self.results_dir.mkdir(exist_ok=True)
    
    def run_single_experiment(self, exp_id: str) -> Dict:
        """运行单个实验"""
        logger.info(f"🚀 开始运行 {exp_id}: {self.experiments[exp_id]['name']}")
        
        exp_config = self.experiments[exp_id]
        script_path = self.experiments_dir / exp_config['script']
        
        if not script_path.exists():
            logger.warning(f"实验脚本不存在: {script_path}")
            return {
                'experiment_id': exp_id,
                'status': 'skipped',
                'reason': 'script_not_found',
                'results': None
            }
        
        try:
            # 运行实验脚本
            start_time = time.time()
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=3600  # 1小时超时
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                logger.info(f"✅ {exp_id} 运行成功，用时: {execution_time:.2f}s")
                
                # 读取实验结果
                exp_dir = self.experiments_dir / exp_id
                validation_report_file = exp_dir / "results" / "validation_report.json"
                
                if validation_report_file.exists():
                    with open(validation_report_file, 'r') as f:
                        validation_report = json.load(f)
                    
                    return {
                        'experiment_id': exp_id,
                        'status': 'success',
                        'execution_time': execution_time,
                        'results': validation_report,
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }
                else:
                    return {
                        'experiment_id': exp_id,
                        'status': 'success_no_results',
                        'execution_time': execution_time,
                        'results': None,
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }
            else:
                logger.error(f"❌ {exp_id} 运行失败，返回码: {result.returncode}")
                return {
                    'experiment_id': exp_id,
                    'status': 'failed',
                    'execution_time': execution_time,
                    'results': None,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'return_code': result.returncode
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ {exp_id} 运行超时")
            return {
                'experiment_id': exp_id,
                'status': 'timeout',
                'execution_time': 3600,
                'results': None,
                'stdout': '',
                'stderr': 'Timeout after 1 hour'
            }
        except Exception as e:
            logger.error(f"💥 {exp_id} 运行异常: {e}")
            return {
                'experiment_id': exp_id,
                'status': 'error',
                'execution_time': 0,
                'results': None,
                'stdout': '',
                'stderr': str(e)
            }
    
    def run_all_experiments(self, experiment_list: List[str] = None) -> Dict:
        """运行所有实验"""
        if experiment_list is None:
            experiment_list = list(self.experiments.keys())
        
        logger.info(f"🎯 开始运行 {len(experiment_list)} 个实验")
        
        all_results = {}
        start_time = time.time()
        
        for exp_id in experiment_list:
            if exp_id not in self.experiments:
                logger.warning(f"未知实验ID: {exp_id}")
                continue
            
            exp_result = self.run_single_experiment(exp_id)
            all_results[exp_id] = exp_result
            
            # 添加延迟避免系统过载
            time.sleep(2)
        
        total_time = time.time() - start_time
        
        # 生成综合报告
        comprehensive_report = self.generate_comprehensive_report(all_results, total_time)
        
        # 保存结果
        self.save_comprehensive_results(all_results, comprehensive_report)
        
        return {
            'experiment_results': all_results,
            'comprehensive_report': comprehensive_report,
            'total_execution_time': total_time
        }
    
    def generate_comprehensive_report(self, all_results: Dict, total_time: float) -> Dict:
        """生成综合报告"""
        logger.info("📊 生成综合实验报告...")
        
        # 统计信息
        total_experiments = len(all_results)
        successful_experiments = sum(1 for r in all_results.values() if r['status'] == 'success')
        failed_experiments = sum(1 for r in all_results.values() if r['status'] == 'failed')
        skipped_experiments = sum(1 for r in all_results.values() if r['status'] == 'skipped')
        
        # 验证结果统计
        validation_summary = {}
        for exp_id, result in all_results.items():
            if result['status'] == 'success' and result['results']:
                validation_results = result['results'].get('validation_results', {})
                validation_summary[exp_id] = {
                    'overall_valid': validation_results.get('overall_valid', False),
                    'validation_details': validation_results
                }
        
        # 计算总体成功率
        overall_success_rate = successful_experiments / total_experiments if total_experiments > 0 else 0
        
        # 计算验证成功率
        valid_experiments = sum(1 for v in validation_summary.values() if v['overall_valid'])
        validation_success_rate = valid_experiments / len(validation_summary) if validation_summary else 0
        
        comprehensive_report = {
            'summary': {
                'total_experiments': total_experiments,
                'successful_experiments': successful_experiments,
                'failed_experiments': failed_experiments,
                'skipped_experiments': skipped_experiments,
                'overall_success_rate': overall_success_rate,
                'validation_success_rate': validation_success_rate,
                'total_execution_time': total_time
            },
            'experiment_details': {},
            'validation_summary': validation_summary,
            'recommendations': self._generate_recommendations(all_results, validation_summary)
        }
        
        # 添加实验详情
        for exp_id, result in all_results.items():
            exp_config = self.experiments[exp_id]
            comprehensive_report['experiment_details'][exp_id] = {
                'name': exp_config['name'],
                'description': exp_config['description'],
                'status': result['status'],
                'execution_time': result.get('execution_time', 0),
                'overall_valid': result['results'].get('validation_results', {}).get('overall_valid', False) if result['results'] else False
            }
        
        return comprehensive_report
    
    def _generate_recommendations(self, all_results: Dict, validation_summary: Dict) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于成功率
        successful_count = sum(1 for r in all_results.values() if r['status'] == 'success')
        total_count = len(all_results)
        
        if successful_count / total_count < 0.8:
            recommendations.append("实验成功率较低，建议检查实验环境和脚本配置")
        
        # 基于验证结果
        valid_count = sum(1 for v in validation_summary.values() if v['overall_valid'])
        if valid_count < len(validation_summary) * 0.8:
            recommendations.append("验证成功率较低，建议检查理论预测值和实验参数")
        
        # 基于具体实验
        failed_experiments = [exp_id for exp_id, result in all_results.items() if result['status'] == 'failed']
        if failed_experiments:
            recommendations.append(f"以下实验需要重点关注: {', '.join(failed_experiments)}")
        
        # 基于执行时间
        long_running_experiments = [exp_id for exp_id, result in all_results.items() 
                                  if result.get('execution_time', 0) > 300]  # 5分钟以上
        if long_running_experiments:
            recommendations.append(f"以下实验执行时间较长，建议优化: {', '.join(long_running_experiments)}")
        
        if not recommendations:
            recommendations.append("所有实验运行良好，建议继续后续分析")
        
        return recommendations
    
    def save_comprehensive_results(self, all_results: Dict, comprehensive_report: Dict):
        """保存综合结果"""
        logger.info("💾 保存综合实验结果...")
        
        def convert_numpy_types(obj):
            """转换numpy类型为Python原生类型"""
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            else:
                return obj
        
        # 保存详细结果
        detailed_results_file = self.results_dir / "detailed_results.json"
        with open(detailed_results_file, 'w') as f:
            json.dump(convert_numpy_types(all_results), f, indent=2)
        
        # 保存综合报告
        comprehensive_report_file = self.results_dir / "comprehensive_report.json"
        with open(comprehensive_report_file, 'w') as f:
            json.dump(convert_numpy_types(comprehensive_report), f, indent=2)
        
        # 生成Markdown报告
        markdown_report = self._generate_markdown_report(comprehensive_report)
        markdown_file = self.results_dir / "comprehensive_report.md"
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        
        logger.info(f"结果已保存:")
        logger.info(f"  详细结果: {detailed_results_file}")
        logger.info(f"  综合报告: {comprehensive_report_file}")
        logger.info(f"  Markdown报告: {markdown_file}")
    
    def _generate_markdown_report(self, comprehensive_report: Dict) -> str:
        """生成Markdown格式的综合报告"""
        summary = comprehensive_report['summary']
        experiment_details = comprehensive_report['experiment_details']
        validation_summary = comprehensive_report['validation_summary']
        recommendations = comprehensive_report['recommendations']
        
        report = f"""# 综合实验验证报告

## 执行摘要

- **总实验数**: {summary['total_experiments']}
- **成功实验数**: {summary['successful_experiments']}
- **失败实验数**: {summary['failed_experiments']}
- **跳过实验数**: {summary['skipped_experiments']}
- **总体成功率**: {summary['overall_success_rate']:.1%}
- **验证成功率**: {summary['validation_success_rate']:.1%}
- **总执行时间**: {summary['total_execution_time']:.2f} 秒

## 实验详情

| 实验ID | 实验名称 | 状态 | 执行时间(s) | 验证结果 |
|--------|----------|------|-------------|----------|
"""
        
        for exp_id, details in experiment_details.items():
            status_emoji = {
                'success': '✅',
                'failed': '❌',
                'skipped': '⏭️',
                'timeout': '⏰',
                'error': '💥'
            }.get(details['status'], '❓')
            
            validation_emoji = '✓' if details['overall_valid'] else '✗'
            
            report += f"| {exp_id} | {details['name']} | {status_emoji} {details['status']} | {details['execution_time']:.2f} | {validation_emoji} |\n"
        
        report += f"""
## 验证结果详情

"""
        
        for exp_id, validation in validation_summary.items():
            exp_name = experiment_details[exp_id]['name']
            overall_valid = validation['overall_valid']
            validation_details = validation['validation_details']
            
            report += f"### {exp_name} ({exp_id})\n\n"
            report += f"**总体验证**: {'✅ 通过' if overall_valid else '❌ 未通过'}\n\n"
            
            if validation_details:
                report += "**详细验证结果**:\n"
                for key, value in validation_details.items():
                    if isinstance(value, bool):
                        emoji = '✓' if value else '✗'
                        report += f"- {key}: {emoji}\n"
                    else:
                        report += f"- {key}: {value}\n"
            
            report += "\n"
        
        report += f"""
## 建议

"""
        
        for i, recommendation in enumerate(recommendations, 1):
            report += f"{i}. {recommendation}\n"
        
        report += f"""
## 结论

基于 {summary['total_experiments']} 个实验的综合验证结果：

- **实验执行**: {summary['successful_experiments']}/{summary['total_experiments']} 个实验成功执行
- **理论验证**: {len([v for v in validation_summary.values() if v['overall_valid']])}/{len(validation_summary)} 个实验通过理论验证
- **整体评估**: {'实验验证成功' if summary['validation_success_rate'] > 0.8 else '需要进一步优化'}

"""
        
        return report
    
    def run_experiments_1_and_2(self):
        """运行实验1和2（已实现的实验）"""
        logger.info("🎯 运行实验1和2（已实现的实验）")
        
        experiment_list = ['exp_1_structure', 'exp_2_doping']
        return self.run_all_experiments(experiment_list)
    
    def run_all_6_experiments(self):
        """运行所有6个实验"""
        logger.info("🎯 运行所有6个实验")
        
        experiment_list = ['exp_1_structure', 'exp_2_doping', 'exp_3_electronic', 
                          'exp_4_polaron', 'exp_5_synergy', 'exp_6_optimal']
        return self.run_all_experiments(experiment_list)

def main():
    """主函数"""
    runner = ComprehensiveExperimentRunner()
    
    # 运行所有6个实验
    results = runner.run_all_6_experiments()
    
    # 输出总结
    comprehensive_report = results['comprehensive_report']
    summary = comprehensive_report['summary']
    
    logger.info("🎉 综合实验完成!")
    logger.info(f"  总实验数: {summary['total_experiments']}")
    logger.info(f"  成功实验数: {summary['successful_experiments']}")
    logger.info(f"  总体成功率: {summary['overall_success_rate']:.1%}")
    logger.info(f"  验证成功率: {summary['validation_success_rate']:.1%}")
    logger.info(f"  总执行时间: {summary['total_execution_time']:.2f} 秒")
    
    return results

if __name__ == "__main__":
    main()
