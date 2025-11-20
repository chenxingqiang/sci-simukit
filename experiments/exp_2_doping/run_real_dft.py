#!/usr/bin/env python3
"""
真实DFT计算运行脚本 - 实验2: 掺杂合成验证
运行CP2K计算获取真实的第一性原理数据
"""

import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

# CP2K路径
CP2K_EXE = "/opt/homebrew/bin/cp2k.psmp"
CP2K_DATA_DIR = "/opt/homebrew/Cellar/cp2k/2025.1/share/cp2k/data"

# 修复输入文件 - 添加BASIS_SET和POTENTIAL路径
def fix_input_file(inp_file):
    """在输入文件中添加BASIS_SET和POTENTIAL文件路径"""
    with open(inp_file, 'r') as f:
        content = f.read()
    
    # 如果已经有DFT_PLUS_U或BASIS_SET_FILE_NAME，跳过
    if 'BASIS_SET_FILE_NAME' in content:
        print(f"  ✓ {inp_file.name} 已包含BASIS_SET路径")
        return True
    
    # 在&DFT之后添加BASIS_SET和POTENTIAL路径
    lines = content.split('\n')
    new_lines = []
    dft_found = False
    
    for line in lines:
        new_lines.append(line)
        if '&DFT' in line and not dft_found:
            dft_found = True
            # 添加basis set和potential文件
            new_lines.append(f'    BASIS_SET_FILE_NAME {CP2K_DATA_DIR}/BASIS_MOLOPT')
            new_lines.append(f'    POTENTIAL_FILE_NAME {CP2K_DATA_DIR}/GTH_POTENTIALS')
    
    # 写回文件
    with open(inp_file, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print(f"  ✓ {inp_file.name} 已修复")
    return True

# 运行单个CP2K计算
def run_cp2k(inp_file, out_file):
    """运行CP2K计算"""
    try:
        start_time = time.time()
        print(f"\n{'='*60}")
        print(f"运行: {inp_file.name}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # 运行CP2K
        result = subprocess.run(
            [CP2K_EXE, '-i', str(inp_file), '-o', str(out_file)],
            capture_output=True,
            text=True,
            timeout=3600  # 1小时超时
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ 成功! 用时: {elapsed/60:.1f} 分钟")
            return True, elapsed
        else:
            print(f"❌ 失败! 返回码: {result.returncode}")
            print(f"错误信息: {result.stderr[-500:]}")  # 最后500字符
            return False, elapsed
            
    except subprocess.TimeoutExpired:
        print(f"⏰ 超时 (>1小时)")
        return False, 3600
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False, 0

# 提取DFT结果
def extract_results(out_file, dopant, concentration):
    """从输出文件中提取能量等信息"""
    try:
        with open(out_file, 'r') as f:
            content = f.read()
        
        # 提取总能量
        energy = None
        for line in content.split('\n'):
            if 'ENERGY| Total FORCE_EVAL' in line:
                parts = line.split()
                energy = float(parts[-1])
                break
        
        # 提取SCF收敛信息
        converged = 'SCF run converged' in content
        
        # 提取原子数
        n_atoms = content.count('ATOMIC COORDINATES')
        
        return {
            'dopant': dopant,
            'concentration': concentration,
            'total_energy': energy,
            'convergence': converged,
            'n_atoms': n_atoms,
            'status': 'success' if converged else 'failed'
        }
    except Exception as e:
        print(f"  ⚠️ 提取结果失败: {e}")
        return None

def main():
    """主函数"""
    outputs_dir = Path('/Users/xingqiangchen/sci-simukit/experiments/exp_2_doping/outputs')
    results_dir = Path('/Users/xingqiangchen/sci-simukit/experiments/exp_2_doping/results')
    results_dir.mkdir(exist_ok=True)
    
    # 获取所有输入文件
    inp_files = sorted(outputs_dir.glob('*.inp'))
    
    print(f"\n🚀 实验2: 掺杂合成验证 - 真实DFT计算")
    print(f"=" * 60)
    print(f"总计算数: {len(inp_files)}")
    print(f"CP2K版本: 2025.1")
    print(f"数据目录: {CP2K_DATA_DIR}")
    print(f"=" * 60)
    
    # Step 1: 修复所有输入文件
    print(f"\n📝 Step 1: 修复输入文件...")
    for inp_file in inp_files:
        fix_input_file(inp_file)
    
    print(f"\n✅ 所有输入文件已修复!")
    
    # Step 2: 运行计算
    print(f"\n🔬 Step 2: 开始运行DFT计算...")
    print(f"注意: 每个计算约需2-4分钟")
    
    results = {}
    successful = 0
    failed = 0
    total_time = 0
    
    for i, inp_file in enumerate(inp_files, 1):
        out_file = inp_file.with_suffix('.out')
        
        # 从文件名提取掺杂信息
        # 格式: C60_<dopant>_<concentration>_doped.inp
        parts = inp_file.stem.split('_')
        dopant = parts[1]
        concentration = float(parts[2])
        
        print(f"\n[{i}/{len(inp_files)}] {dopant} @ {concentration*100:.1f}%")
        
        # 运行计算
        success, elapsed = run_cp2k(inp_file, out_file)
        total_time += elapsed
        
        if success:
            # 提取结果
            result = extract_results(out_file, dopant, concentration)
            if result:
                key = f"{dopant}_{concentration}"
                results[key] = result
                successful += 1
            else:
                failed += 1
        else:
            failed += 1
        
        # 每5个计算保存一次
        if i % 5 == 0:
            with open(results_dir / 'dft_results_realtime.json', 'w') as f:
                json.dump(results, f, indent=2)
    
    # Step 3: 保存最终结果
    print(f"\n💾 Step 3: 保存结果...")
    
    final_results = {
        'metadata': {
            'experiment': 'exp_2_doping',
            'total_calculations': len(inp_files),
            'successful': successful,
            'failed': failed,
            'total_time_hours': total_time / 3600,
            'completion_date': datetime.now().isoformat()
        },
        'results': results
    }
    
    with open(results_dir / 'real_dft_results.json', 'w') as f:
        json.dump(final_results, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"🎉 实验2完成!")
    print(f"{'='*60}")
    print(f"✅ 成功: {successful}/{len(inp_files)}")
    print(f"❌ 失败: {failed}/{len(inp_files)}")
    print(f"⏱️  总用时: {total_time/60:.1f} 分钟 ({total_time/3600:.2f} 小时)")
    print(f"📊 结果文件: {results_dir / 'real_dft_results.json'}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()

