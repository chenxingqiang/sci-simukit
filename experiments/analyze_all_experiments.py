#!/usr/bin/env python3
"""
统一分析所有实验的DFT结果
从真实DFT输出文件中提取能量数据
"""

import numpy as np
import json
import matplotlib.pyplot as plt
from pathlib import Path
import re
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def extract_energy(output_file: Path) -> Optional[float]:
    """从CP2K输出文件提取总能量"""
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


def is_completed(output_file: Path) -> bool:
    """检查计算是否完成"""
    if not output_file.exists():
        return False
    try:
        with open(output_file, 'r') as f:
            return 'PROGRAM ENDED' in f.read()
    except:
        return False


def analyze_experiment(exp_name: str, outputs_dir: Path) -> Dict:
    """分析单个实验的所有输出"""
    results = {}
    
    output_files = list(outputs_dir.glob("*.out"))
    logger.info(f"\n{exp_name}: 找到 {len(output_files)} 个输出文件")
    
    for output_file in output_files:
        energy = extract_energy(output_file)
        completed = is_completed(output_file)
        
        # 解析文件名
        filename = output_file.stem
        
        # 提取应变
        strain_match = re.search(r'_([-+]?\d+\.?\d*)_', filename)
        strain = float(strain_match.group(1)) if strain_match else None
        
        # 提取掺杂类型
        dopant = 'unknown'
        if 'pristine' in filename.lower():
            dopant = 'pristine'
        elif '_B_' in filename or '_B.' in filename or filename.endswith('_B'):
            dopant = 'B'
        elif '_N_' in filename or '_N.' in filename or filename.endswith('_N'):
            dopant = 'N'
        elif '_P_' in filename or '_P.' in filename or filename.endswith('_P'):
            dopant = 'P'
        elif '_B+N_' in filename:
            dopant = 'B+N'
        
        results[filename] = {
            'file': output_file.name,
            'strain': strain,
            'dopant': dopant,
            'energy_Ha': energy,
            'energy_eV': energy * 27.2114 if energy else None,
            'completed': completed,
            'status': 'success' if energy and completed else 'incomplete'
        }
        
        status = "✓" if results[filename]['status'] == 'success' else "✗"
        if energy:
            logger.info(f"  {status} {filename}: E = {energy:.6f} Ha")
        else:
            logger.info(f"  ✗ {filename}: 无能量数据")
    
    return results


def main():
    """分析所有实验"""
    # 可以在本地或服务器运行
    base_dirs = [
        Path("/Users/xingqiangchen/sci-simukit/dft_results_download"),  # 本地下载
        Path("/opt/sci-simukit/experiments"),  # 服务器
    ]
    
    base_dir = None
    for d in base_dirs:
        if d.exists():
            base_dir = d
            break
    
    if not base_dir:
        logger.error("未找到实验目录!")
        return
    
    logger.info("=" * 60)
    logger.info("DFT实验结果统一分析")
    logger.info(f"基础目录: {base_dir}")
    logger.info("=" * 60)
    
    # 定义实验目录映射
    experiments = {
        'exp1_structure': base_dir / 'exp_1_structure' / 'outputs',
        'exp2_doping': base_dir / 'exp_2_doping' / 'outputs', 
        'exp3_electronic': base_dir / 'exp_3_electronic' / 'outputs',
        'exp4_polaron': base_dir / 'exp_4_polaron' / 'outputs',
        'exp5_synergy': base_dir / 'dft_results_exp5_complete',
        'exp6_optimal': base_dir / 'exp_6_optimal' / 'outputs',
    }
    
    all_results = {}
    summary = {
        'total_experiments': 0,
        'total_calculations': 0,
        'successful_calculations': 0,
        'experiments': {}
    }
    
    for exp_name, outputs_dir in experiments.items():
        if outputs_dir.exists():
            results = analyze_experiment(exp_name, outputs_dir)
            all_results[exp_name] = results
            
            n_total = len(results)
            n_success = sum(1 for r in results.values() if r['status'] == 'success')
            
            summary['total_experiments'] += 1
            summary['total_calculations'] += n_total
            summary['successful_calculations'] += n_success
            summary['experiments'][exp_name] = {
                'total': n_total,
                'successful': n_success,
                'completion_rate': f"{n_success/n_total*100:.1f}%" if n_total > 0 else "0%"
            }
        else:
            logger.warning(f"{exp_name}: 目录不存在 - {outputs_dir}")
    
    # 打印总结
    logger.info("\n" + "=" * 60)
    logger.info("总结")
    logger.info("=" * 60)
    logger.info(f"总实验数: {summary['total_experiments']}")
    logger.info(f"总计算数: {summary['total_calculations']}")
    logger.info(f"成功计算: {summary['successful_calculations']}")
    logger.info(f"完成率: {summary['successful_calculations']/summary['total_calculations']*100:.1f}%")
    
    for exp_name, exp_summary in summary['experiments'].items():
        logger.info(f"  {exp_name}: {exp_summary['successful']}/{exp_summary['total']} ({exp_summary['completion_rate']})")
    
    # 保存结果
    output_dir = base_dir / 'analysis_results'
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / 'all_experiments_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    with open(output_dir / 'experiments_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"\n结果已保存到: {output_dir}")
    
    return all_results, summary


if __name__ == "__main__":
    main()

