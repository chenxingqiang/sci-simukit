#!/usr/bin/env python3
'''收集HPC计算结果'''

import os
import pandas as pd
from pathlib import Path
import json

def collect_results():
    results = []
    
    # 遍历输出文件
    for out_file in Path('outputs').glob('*.out'):
        # 解析输出文件获取能量、带隙等
        # 这里是示例代码，实际需要根据CP2K输出格式解析
        data = {
            'structure': out_file.stem,
            'total_energy': -100.0,  # 示例值
            'band_gap': 1.8,         # 示例值
            'computation_time': 3600  # 秒
        }
        results.append(data)
    
    # 保存结果
    df = pd.DataFrame(results)
    df.to_csv('hpc_results.csv', index=False)
    
    print(f"收集了 {len(results)} 个计算结果")

if __name__ == "__main__":
    collect_results()
