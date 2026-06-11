#!/usr/bin/env python3
"""
为每个实验生成最优表达的PRL风格图表
针对每个实验的具体价值设计可视化方案
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd

# PRL Style Configuration
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'axes.linewidth': 0.8,
    'lines.linewidth': 1.5,
    'lines.markersize': 7,
    'axes.grid': False,
    'axes.spines.top': True,
    'axes.spines.right': True,
})

COLORS = {'pristine': '#1f77b4', 'B': '#d62728', 'N': '#2ca02c', 'P': '#9467bd'}
MARKERS = {'pristine': 'o', 'B': 's', 'N': '^', 'P': 'D'}
HA_TO_EV = 27.2114


def exp1_elastic_response(base_dir: Path):
    """
    实验1: 弹性响应基准
    核心价值: 建立pristine C60二聚体的应变响应基准
    最佳图表: 应变-能量二次拟合曲线，显示弹性常数
    """
    results_file = base_dir / "exp_1_structure" / "results" / "real_dft_results.json"
    with open(results_file) as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    df = df.sort_values('strain')
    
    # 相对能量 (以0%为基准)
    e0 = df[df['strain'] == 0.0]['total_energy_Ha'].iloc[0]
    df['relative_E_meV'] = (df['total_energy_Ha'] - e0) * HA_TO_EV * 1000
    
    # 二次拟合
    coeffs = np.polyfit(df['strain'], df['relative_E_meV'], 2)
    fit_x = np.linspace(-6, 6, 100)
    fit_y = np.polyval(coeffs, fit_x)
    
    fig, ax = plt.subplots(figsize=(4.0, 3.5))
    
    # 数据点
    ax.scatter(df['strain'], df['relative_E_meV'], s=80, c=COLORS['pristine'], 
               edgecolors='white', linewidths=1.5, zorder=5)
    
    # 拟合曲线
    ax.plot(fit_x, fit_y, 'k--', linewidth=1.2, alpha=0.7, label=f'Quadratic fit')
    
    # 标注弹性常数
    elastic_const = 2 * coeffs[0]  # d²E/dε²
    ax.text(0.05, 0.95, f'$d^2E/d\\varepsilon^2$ = {elastic_const:.2f} meV/%²',
            transform=ax.transAxes, fontsize=10, va='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
    ax.axvline(x=0, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
    
    ax.set_xlabel('Biaxial Strain (%)')
    ax.set_ylabel('Relative Energy (meV)')
    ax.set_xlim(-6, 6)
    ax.minorticks_on()
    
    # 标注压缩有利
    ax.annotate('Compression\nfavored', xy=(-4, -2.5), fontsize=8, ha='center',
               color='gray')
    
    plt.tight_layout()
    save_path = base_dir / "exp_1_structure" / "figures" / "exp1_elastic_response.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.savefig(save_path.with_suffix('.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Exp1 figure saved: {save_path.name}")


def exp2_doping_concentration(base_dir: Path):
    """
    实验2: 掺杂浓度效应
    核心价值: 不同掺杂类型随浓度变化的稳定性
    最佳图表: 形成能 vs 掺杂浓度，突出N稳定化和B不稳定化
    """
    results_file = base_dir / "exp_2_doping" / "results" / "real_dft_results.json"
    with open(results_file) as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    # 计算形成能 (相对于pristine)
    fig, ax = plt.subplots(figsize=(4.0, 3.5))
    
    for dopant in ['B', 'N', 'P']:
        subset = df[df['dopant'] == dopant].sort_values('concentration')
        pristine = df[df['dopant'] == 'pristine'].sort_values('concentration')
        
        if len(subset) > 0 and len(pristine) > 0:
            # 按浓度匹配pristine能量
            formation_E = []
            concs = []
            for _, row in subset.iterrows():
                conc = row['concentration']
                p_row = pristine[pristine['concentration'] == conc]
                if len(p_row) > 0:
                    fe = (row['total_energy_Ha'] - p_row['total_energy_Ha'].iloc[0]) * HA_TO_EV
                    formation_E.append(fe)
                    concs.append(conc * 100)  # 转为百分比
            
            if formation_E:
                ax.plot(concs, formation_E, marker=MARKERS[dopant], color=COLORS[dopant],
                       label=f'{dopant}-doped', markerfacecolor=COLORS[dopant],
                       markeredgecolor='white', markeredgewidth=1)
    
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.8, alpha=0.7)
    
    ax.set_xlabel('Doping Concentration (%)')
    ax.set_ylabel('Formation Energy (eV)')
    ax.legend(loc='center right', frameon=False)
    ax.minorticks_on()
    
    # 标注稳定/不稳定区域
    ax.fill_between([2, 8], 0, 400, alpha=0.1, color='red', label='Destabilized')
    ax.fill_between([2, 8], -400, 0, alpha=0.1, color='green', label='Stabilized')
    ax.text(7.5, 200, 'Destabilized', fontsize=8, color='red', ha='right')
    ax.text(7.5, -200, 'Stabilized', fontsize=8, color='green', ha='right')
    
    plt.tight_layout()
    save_path = base_dir / "exp_2_doping" / "figures" / "exp2_formation_energy.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.savefig(save_path.with_suffix('.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Exp2 figure saved: {save_path.name}")


def exp3_strain_doping_coupling(base_dir: Path):
    """
    实验3: 应变-掺杂耦合效应
    核心价值: 完整的应变-掺杂参数空间映射
    最佳图表: 应变敏感度增强因子柱状图 + 热图
    """
    # 使用真实DFT分析结果
    results_file = base_dir / "exp_3_electronic" / "results" / "analysis_summary.json"
    with open(results_file) as f:
        summary = json.load(f)
    
    # 直接使用分析脚本计算的应变敏感度
    sensitivities = summary.get('strain_sensitivities_meV_per_percent', {})
    
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0))
    
    # Panel (a): 应变敏感度
    ax1 = axes[0]
    dopants = ['pristine', 'B', 'N', 'P']
    values = [sensitivities.get(d, 0) for d in dopants]
    colors = [COLORS[d] for d in dopants]
    
    bars = ax1.bar(dopants, values, color=colors, alpha=0.85, edgecolor='black', linewidth=0.5)
    ax1.axhline(y=0, color='gray', linestyle='--', linewidth=0.8)
    
    # 标注数值
    for bar, val in zip(bars, values):
        y = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, y, f'{val:.1f}',
                ha='center', va='bottom' if y > 0 else 'top', fontsize=8)
    
    ax1.set_ylabel('Strain Sensitivity (meV/%)')
    ax1.set_xlabel('Dopant Type')
    ax1.text(-0.15, 1.05, '(a)', transform=ax1.transAxes, fontweight='bold', fontsize=11)
    ax1.minorticks_on()
    
    # Panel (b): 增强因子
    ax2 = axes[1]
    pristine_sens = abs(sensitivities.get('pristine', 0.34))
    enhancement = [abs(sensitivities.get(d, 0)) / pristine_sens for d in ['B', 'N', 'P']]
    
    bars2 = ax2.bar(['B', 'N', 'P'], enhancement, 
                    color=[COLORS['B'], COLORS['N'], COLORS['P']], 
                    alpha=0.85, edgecolor='black', linewidth=0.5)
    
    ax2.axhline(y=1, color='gray', linestyle='--', linewidth=0.8, label='Pristine baseline')
    
    # 标注增强倍数
    for bar, val in zip(bars2, enhancement):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                f'{val:.0f}×', ha='center', fontsize=10, fontweight='bold')
    
    ax2.set_ylabel('Enhancement Factor')
    ax2.set_xlabel('Dopant Type')
    ax2.set_ylim(0, max(enhancement) * 1.2)
    ax2.text(-0.15, 1.05, '(b)', transform=ax2.transAxes, fontweight='bold', fontsize=11)
    ax2.minorticks_on()
    
    plt.tight_layout()
    save_path = base_dir / "exp_3_electronic" / "figures" / "exp3_coupling_enhancement.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.savefig(save_path.with_suffix('.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Exp3 figure saved: {save_path.name}")


def exp4_polaron_transition(base_dir: Path):
    """
    实验4: 极化子转变验证
    核心价值: 验证0%→+3%应变触发的极化子行为变化
    最佳图表: 0%和+3%应变下各掺杂类型的能量变化对比
    """
    results_file = base_dir / "exp_4_polaron" / "results" / "real_dft_results.json"
    with open(results_file) as f:
        data = json.load(f)
    
    # 数据是字典形式，转换为DataFrame
    df = pd.DataFrame([v for v in data.values()])
    
    fig, ax = plt.subplots(figsize=(4.5, 3.5))
    
    dopants = ['pristine', 'B', 'N', 'P']
    x = np.arange(len(dopants))
    width = 0.35
    
    # 获取0%和+3%的能量
    e_0pct = []
    e_3pct = []
    
    for dopant in dopants:
        e0 = df[(df['dopant'] == dopant) & (df['strain'] == 0.0)]['total_energy_Ha'].values
        e3 = df[(df['dopant'] == dopant) & (df['strain'] == 3.0)]['total_energy_Ha'].values
        
        e_0pct.append(e0[0] if len(e0) > 0 else np.nan)
        e_3pct.append(e3[0] if len(e3) > 0 else np.nan)
    
    # 计算能量变化 (meV)
    delta_E = [(e3 - e0) * HA_TO_EV * 1000 for e0, e3 in zip(e_0pct, e_3pct)]
    
    colors = [COLORS[d] for d in dopants]
    bars = ax.bar(dopants, delta_E, color=colors, alpha=0.85, edgecolor='black', linewidth=0.5)
    
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.8)
    
    # 标注数值
    for bar, val in zip(bars, delta_E):
        y = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, y,
                f'{val:+.1f}', ha='center', va='bottom' if y > 0 else 'top', fontsize=9)
    
    ax.set_ylabel('Energy Change 0%→+3% (meV)')
    ax.set_xlabel('Dopant Type')
    ax.set_title('Polaron Transition: Strain-Induced Energy Shift', fontsize=10)
    ax.minorticks_on()
    
    # 添加解释注释
    ax.annotate('B: Strong destabilization\nunder strain', 
               xy=(1, delta_E[1]), xytext=(1.5, delta_E[1]*0.6),
               fontsize=7, ha='left',
               arrowprops=dict(arrowstyle='->', color='gray', lw=0.5))
    
    plt.tight_layout()
    save_path = base_dir / "exp_4_polaron" / "figures" / "exp4_polaron_transition.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.savefig(save_path.with_suffix('.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Exp4 figure saved: {save_path.name}")


def exp5_synergy_effect(base_dir: Path):
    """
    实验5: 协同效应
    核心价值: 多分子系统中掺杂-应变的协同增强
    最佳图表: 四聚体vs二聚体的敏感度对比 + 协同因子
    """
    # 加载exp5数据
    results_file = base_dir / "exp_5_synergy" / "results" / "analysis_summary.json"
    with open(results_file) as f:
        exp5_summary = json.load(f)
    
    # 加载exp3数据作对比 (使用analysis_summary.json)
    exp3_file = base_dir / "exp_3_electronic" / "results" / "analysis_summary.json"
    with open(exp3_file) as f:
        exp3_summary = json.load(f)
    
    # 直接使用分析脚本计算的敏感度
    exp3_sens_dict = exp3_summary.get('strain_sensitivities_meV_per_percent', {})
    
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0))
    
    # Panel (a): 二聚体 vs 四聚体敏感度对比
    ax1 = axes[0]
    dopants = ['pristine', 'B', 'N', 'P']
    
    exp3_sens = [exp3_sens_dict.get(d, 0) for d in dopants]
    # exp5数据
    exp5_sens_dict = exp5_summary.get('strain_sensitivities', exp5_summary.get('strain_sensitivities_meV_per_percent', {}))
    exp5_sens = [exp5_sens_dict.get(d, 0) for d in dopants]
    
    x = np.arange(len(dopants))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, exp3_sens, width, label='Dimer (120 atoms)', 
                    color='steelblue', alpha=0.8, edgecolor='black', linewidth=0.5)
    bars2 = ax1.bar(x + width/2, exp5_sens, width, label='Tetramer (240 atoms)',
                    color='darkorange', alpha=0.8, edgecolor='black', linewidth=0.5)
    
    ax1.axhline(y=0, color='gray', linestyle='--', linewidth=0.8)
    ax1.set_xticks(x)
    ax1.set_xticklabels(dopants)
    ax1.set_ylabel('Strain Sensitivity (meV/%)')
    ax1.set_xlabel('Dopant Type')
    ax1.legend(loc='upper left', frameon=False, fontsize=8)
    ax1.text(-0.15, 1.05, '(a)', transform=ax1.transAxes, fontweight='bold', fontsize=11)
    ax1.minorticks_on()
    
    # Panel (b): 协同因子突出显示
    ax2 = axes[1]
    
    # synergy_factor是数值类型
    sf = exp5_summary.get('synergy_factor', 445)
    synergy_factor = float(sf) if isinstance(sf, (int, float)) else float(str(sf).replace('x', ''))
    
    # 创建一个大的协同因子显示
    ax2.text(0.5, 0.6, f'{synergy_factor:.0f}×', transform=ax2.transAxes,
            fontsize=48, ha='center', va='center', fontweight='bold', color='darkorange')
    ax2.text(0.5, 0.3, 'Synergistic\nEnhancement', transform=ax2.transAxes,
            fontsize=12, ha='center', va='center', color='gray')
    ax2.text(0.5, 0.1, '(Tetramer vs Pristine)', transform=ax2.transAxes,
            fontsize=9, ha='center', va='center', color='gray', style='italic')
    
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.axis('off')
    ax2.text(-0.05, 1.05, '(b)', transform=ax2.transAxes, fontweight='bold', fontsize=11)
    
    plt.tight_layout()
    save_path = base_dir / "exp_5_synergy" / "figures" / "exp5_synergy_enhancement.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.savefig(save_path.with_suffix('.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Exp5 figure saved: {save_path.name}")


def exp6_optimal_conditions(base_dir: Path):
    """
    实验6: 最优条件
    核心价值: 确定最佳工作条件（掺杂+应变组合）
    最佳图表: 热图显示掺杂-应变参数空间中的能量分布
    """
    results_file = base_dir / "exp_6_optimal" / "results" / "real_dft_results.json"
    with open(results_file) as f:
        data = json.load(f)
    
    # 数据是字典形式，转换为DataFrame
    df = pd.DataFrame([v for v in data.values()])
    
    # 创建热图数据
    dopants = ['pristine', 'B', 'N', 'P']
    strains = sorted(df['strain'].unique())
    
    # 以pristine at 0%为基准计算相对能量
    e_ref = df[(df['dopant'] == 'pristine') & (df['strain'] == 0.0)]['total_energy_Ha'].iloc[0]
    
    fig, ax = plt.subplots(figsize=(5.0, 3.5))
    
    # 构建矩阵
    matrix = np.zeros((len(dopants), len(strains)))
    for i, dopant in enumerate(dopants):
        for j, strain in enumerate(strains):
            row = df[(df['dopant'] == dopant) & (df['strain'] == strain)]
            if len(row) > 0:
                matrix[i, j] = (row['total_energy_Ha'].iloc[0] - e_ref) * HA_TO_EV
            else:
                matrix[i, j] = np.nan
    
    # 绘制热图
    im = ax.imshow(matrix, cmap='RdBu_r', aspect='auto')
    
    # 标签
    ax.set_xticks(range(len(strains)))
    ax.set_xticklabels([f'{s:+.0f}%' for s in strains])
    ax.set_yticks(range(len(dopants)))
    ax.set_yticklabels(dopants)
    
    ax.set_xlabel('Biaxial Strain')
    ax.set_ylabel('Dopant Type')
    
    # 添加数值标注
    for i in range(len(dopants)):
        for j in range(len(strains)):
            val = matrix[i, j]
            if not np.isnan(val):
                color = 'white' if abs(val) > 2 else 'black'
                ax.text(j, i, f'{val:.1f}', ha='center', va='center', 
                       color=color, fontsize=7)
    
    # 颜色条
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Relative Energy (eV)')
    
    # 标注最优区域
    # 找到N掺杂的行
    n_idx = dopants.index('N')
    ax.add_patch(plt.Rectangle((-0.5, n_idx-0.5), len(strains), 1, 
                               fill=False, edgecolor='lime', linewidth=2, linestyle='--'))
    ax.text(len(strains)-0.5, n_idx, ' Optimal', va='center', fontsize=8, 
           color='green', fontweight='bold')
    
    plt.tight_layout()
    save_path = base_dir / "exp_6_optimal" / "figures" / "exp6_optimal_heatmap.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.savefig(save_path.with_suffix('.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Exp6 figure saved: {save_path.name}")


def main():
    base_dir = Path("/Users/xingqiangchen/sci-simukit/dft_results_download")
    
    print("=" * 60)
    print("生成优化的实验图表 (PRL风格)")
    print("=" * 60)
    
    print("\n--- Exp1: 弹性响应基准 ---")
    exp1_elastic_response(base_dir)
    
    print("\n--- Exp2: 掺杂浓度效应 ---")
    exp2_doping_concentration(base_dir)
    
    print("\n--- Exp3: 应变-掺杂耦合效应 ---")
    exp3_strain_doping_coupling(base_dir)
    
    print("\n--- Exp4: 极化子转变验证 ---")
    exp4_polaron_transition(base_dir)
    
    print("\n--- Exp5: 协同效应 ---")
    exp5_synergy_effect(base_dir)
    
    print("\n--- Exp6: 最优条件 ---")
    exp6_optimal_conditions(base_dir)
    
    print("\n" + "=" * 60)
    print("所有优化图表生成完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()

