#!/usr/bin/env python3
"""生成HPC计算报告"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 读取结果
df = pd.read_csv('final_dft_results.csv')

# 生成报告
with open('hpc_calculation_report.md', 'w') as f:
    f.write("# HPC DFT计算结果报告\n\n")
    f.write(f"## 总览\n")
    f.write(f"- 完成计算: {len(df)} 个结构\n")
    f.write(f"- 应变范围: {df['strain'].min():.1f}% 到 {df['strain'].max():.1f}%\n")
    f.write(f"- 掺杂类型: {df['doping_type'].unique().tolist()}\n\n")
    
    f.write("## 能量分析\n")
    
    # 按应变分组
    strain_groups = df.groupby('strain')['total_energy'].mean()
    f.write(f"### 应变效应\n")
    for strain, energy in strain_groups.items():
        f.write(f"- {strain:+.1f}%: {energy:.4f} Ha\n")
    
    f.write("\n### 掺杂效应\n")
    doping_groups = df.groupby('doping_type')['total_energy'].mean()
    for doping, energy in doping_groups.items():
        f.write(f"- {doping}: {energy:.4f} Ha\n")

# 绘制能量图
plt.figure(figsize=(10, 6))
for doping_type in df['doping_type'].unique():
    data = df[df['doping_type'] == doping_type]
    plt.scatter(data['strain'], data['total_energy'], label=doping_type, alpha=0.7)

plt.xlabel('Strain (%)')
plt.ylabel('Total Energy (Ha)')
plt.title('DFT Total Energy vs Strain')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('energy_vs_strain.png', dpi=300, bbox_inches='tight')
plt.close()

print("报告生成完成: hpc_calculation_report.md")
