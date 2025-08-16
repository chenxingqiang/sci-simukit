#!/usr/bin/env python3
"""提取CP2K计算能量"""

import sys
import re
from pathlib import Path
import pandas as pd
import argparse

def extract_energy(output_file):
    """从CP2K输出文件提取总能量"""
    energy = None
    
    with open(output_file, 'r') as f:
        for line in f:
            if "ENERGY| Total FORCE_EVAL" in line:
                match = re.search(r'(-?\d+\.\d+)', line)
                if match:
                    energy = float(match.group(1))
    
    return energy

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', type=int, help='批次号')
    args = parser.parse_args()
    
    results = []
    output_dir = Path('outputs')
    
    for out_file in output_dir.glob('*.out'):
        energy = extract_energy(out_file)
        if energy:
            results.append({
                'structure': out_file.stem,
                'total_energy': energy
            })
    
    # 保存结果
    df = pd.DataFrame(results)
    if args.batch:
        df.to_csv(f'batch_{args.batch}_energies.csv', index=False)
    else:
        df.to_csv('all_energies.csv', index=False)
    
    print(f"提取了 {len(results)} 个能量值")

if __name__ == "__main__":
    main()
