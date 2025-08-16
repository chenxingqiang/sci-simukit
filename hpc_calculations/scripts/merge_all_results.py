#!/usr/bin/env python3
"""合并所有批次结果"""

import pandas as pd
from pathlib import Path
import json

# 读取元数据
with open('../data/strain_doped_structures/dataset_metadata.json', 'r') as f:
    metadata = json.load(f)

# 合并所有能量文件
all_results = []
for csv_file in Path('.').glob('batch_*_energies.csv'):
    df = pd.read_csv(csv_file)
    all_results.append(df)

if all_results:
    combined_df = pd.concat(all_results, ignore_index=True)
    
    # 添加元数据信息
    for idx, row in combined_df.iterrows():
        struct_name = row['structure']
        # 查找对应的元数据
        for path, meta in metadata.items():
            if struct_name in path:
                combined_df.at[idx, 'strain'] = meta.get('strain_value', 0)
                combined_df.at[idx, 'doping_type'] = meta.get('doping_type', 'pristine')
                if meta.get('doping_type') == 'single':
                    combined_df.at[idx, 'dopant'] = meta.get('dopant', '')
                    combined_df.at[idx, 'concentration'] = meta.get('concentration', 0)
                break
    
    # 保存最终结果
    combined_df.to_csv('final_dft_results.csv', index=False)
    print(f"合并了 {len(combined_df)} 个计算结果")
else:
    print("未找到任何结果文件")
