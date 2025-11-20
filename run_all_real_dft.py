#!/usr/bin/env python3
"""
运行所有真实DFT计算
修复配置并逐个运行实验1-6的真实CP2K计算
"""

import subprocess
import json
import time
import re
from pathlib import Path
from datetime import datetime
import sys

# CP2K配置
CP2K_EXE = "/opt/homebrew/bin/cp2k.psmp"
CP2K_DATA = "/opt/homebrew/Cellar/cp2k/2025.1/share/cp2k/data"

# 正确的basis set映射
BASIS_SETS = {
    'C': 'DZVP-MOLOPT-GTH',
    'B': 'DZVP-MOLOPT-GTH',
    'N': 'DZVP-MOLOPT-GTH',
    'P': 'DZVP-MOLOPT-GTH',
    'Li': 'DZVP-MOLOPT-SR-GTH',
    'Na': 'DZVP-MOLOPT-SR-GTH',
    'K': 'DZVP-MOLOPT-SR-GTH',
    'Rb': 'DZVP-MOLOPT-SR-GTH',
    'Cs': 'DZVP-MOLOPT-SR-GTH',
}

class RealDFTRunner:
    """真实DFT计算运行器"""
    
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.experiments_dir = self.project_root / 'experiments'
        self.total_calcs = 0
        self.successful_calcs = 0
        self.failed_calcs = 0
        self.start_time = time.time()
        
    def fix_input_file(self, inp_file):
        """修复单个输入文件"""
        try:
            with open(inp_file, 'r') as f:
                content = f.read()
            
            # 检查是否已修复
            if 'DZVP-MOLOPT-GTH' in content and 'BASIS_SET_FILE_NAME' in content:
                return True
            
            lines = content.split('\n')
            new_lines = []
            dft_section = False
            kind_section = False
            
            for line in lines:
                # 在&DFT后添加文件路径
                if '&DFT' in line and not dft_section:
                    new_lines.append(line)
                    if 'BASIS_SET_FILE_NAME' not in content:
                        new_lines.append(f'    BASIS_SET_FILE_NAME {CP2K_DATA}/BASIS_MOLOPT')
                        new_lines.append(f'    POTENTIAL_FILE_NAME {CP2K_DATA}/GTH_POTENTIALS')
                    dft_section = True
                    continue
                
                # 修复BASIS_SET名称
                if 'BASIS_SET' in line and 'MOLOPT-DZVP' in line:
                    # 提取元素符号
                    kind_match = None
                    for i in range(len(new_lines)-1, max(0, len(new_lines)-5), -1):
                        if '&KIND' in new_lines[i]:
                            kind_match = re.search(r'&KIND\s+(\w+)', new_lines[i])
                            break
                    
                    if kind_match:
                        element = kind_match.group(1)
                        basis_set = BASIS_SETS.get(element, 'DZVP-MOLOPT-GTH')
                        line = f'      BASIS_SET {basis_set}'
                
                new_lines.append(line)
            
            # 写回文件
            with open(inp_file, 'w') as f:
                f.write('\n'.join(new_lines))
            
            return True
            
        except Exception as e:
            print(f"  ❌ 修复失败: {e}")
            return False
    
    def run_cp2k_calc(self, inp_file, timeout=1800):
        """运行单个CP2K计算"""
        out_file = inp_file.with_suffix('.out')
        
        try:
            print(f"\n{'='*60}")
            print(f"运行: {inp_file.name}")
            print(f"时间: {datetime.now().strftime('%H:%M:%S')}")
            
            start = time.time()
            result = subprocess.run(
                [CP2K_EXE, '-i', str(inp_file), '-o', str(out_file)],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            elapsed = time.time() - start
            
            # 检查是否成功
            if result.returncode == 0:
                # 验证输出文件
                if self.validate_output(out_file):
                    print(f"✅ 成功! 用时: {elapsed/60:.1f} 分钟")
                    self.successful_calcs += 1
                    return True, elapsed
                else:
                    print(f"⚠️  完成但未收敛")
                    self.failed_calcs += 1
                    return False, elapsed
            else:
                print(f"❌ 失败! 返回码: {result.returncode}")
                if out_file.exists():
                    with open(out_file, 'r') as f:
                        lines = f.readlines()
                        print(f"错误: {lines[-5:][-200:]}")  # 最后几行
                self.failed_calcs += 1
                return False, elapsed
                
        except subprocess.TimeoutExpired:
            print(f"⏰ 超时 (>{timeout/60:.0f} 分钟)")
            self.failed_calcs += 1
            return False, timeout
        except Exception as e:
            print(f"❌ 异常: {e}")
            self.failed_calcs += 1
            return False, 0
    
    def validate_output(self, out_file):
        """验证输出文件是否成功"""
        try:
            with open(out_file, 'r') as f:
                content = f.read()
            
            # 检查是否包含成功标志
            if 'SCF run converged' in content or 'ENERGY| Total FORCE_EVAL' in content:
                # 检查文件是否足够长（成功的计算通常有数千行）
                if len(content.split('\n')) > 500:
                    return True
            
            return False
        except:
            return False
    
    def extract_energy(self, out_file):
        """从输出文件提取能量"""
        try:
            with open(out_file, 'r') as f:
                content = f.read()
            
            # 查找总能量
            match = re.search(r'ENERGY\| Total FORCE_EVAL.*?:\s+([-\d.]+)', content)
            if match:
                return float(match.group(1))
            return None
        except:
            return None
    
    def run_experiment(self, exp_name, max_calcs=None):
        """运行单个实验的所有计算"""
        exp_dir = self.experiments_dir / exp_name
        outputs_dir = exp_dir / 'outputs'
        results_dir = exp_dir / 'results'
        results_dir.mkdir(exist_ok=True)
        
        print(f"\n{'#'*70}")
        print(f"# 实验: {exp_name}")
        print(f"{'#'*70}")
        
        # 获取所有输入文件
        inp_files = sorted(outputs_dir.glob('*.inp'))
        if max_calcs:
            inp_files = inp_files[:max_calcs]
        
        print(f"找到 {len(inp_files)} 个计算")
        
        # Step 1: 修复所有输入文件
        print(f"\n📝 修复输入文件...")
        fixed = 0
        for inp_file in inp_files:
            if self.fix_input_file(inp_file):
                fixed += 1
        print(f"✅ 修复完成: {fixed}/{len(inp_files)}")
        
        # Step 2: 运行计算
        print(f"\n🔬 开始DFT计算...")
        results = {}
        
        for i, inp_file in enumerate(inp_files, 1):
            print(f"\n[{i}/{len(inp_files)}] {exp_name}")
            self.total_calcs += 1
            
            success, elapsed = self.run_cp2k_calc(inp_file)
            
            if success:
                energy = self.extract_energy(inp_file.with_suffix('.out'))
                results[inp_file.stem] = {
                    'status': 'success',
                    'energy': energy,
                    'time': elapsed
                }
            else:
                results[inp_file.stem] = {
                    'status': 'failed',
                    'time': elapsed
                }
            
            # 每5个计算保存一次
            if i % 5 == 0:
                self.save_results(results_dir, results)
        
        # 保存最终结果
        self.save_results(results_dir, results)
        
        return results
    
    def save_results(self, results_dir, results):
        """保存结果"""
        output_file = results_dir / 'real_dft_results.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
    
    def run_all_experiments(self):
        """运行所有实验"""
        experiments = [
            ('exp_1_structure', 10),  # 10个计算
            ('exp_2_doping', 32),      # 32个计算 
            ('exp_3_electronic', 20),  # 20个计算
            ('exp_4_polaron', 20),     # 20个计算
            ('exp_5_synergy', 20),     # 20个计算
            ('exp_6_optimal', 35),     # 35个计算
        ]
        
        print(f"\n{'='*70}")
        print(f"🚀 开始运行所有真实DFT计算")
        print(f"{'='*70}")
        print(f"CP2K: {CP2K_EXE}")
        print(f"数据: {CP2K_DATA}")
        print(f"总计算数: {sum(n for _, n in experiments)}")
        print(f"{'='*70}")
        
        all_results = {}
        
        for exp_name, expected_calcs in experiments:
            results = self.run_experiment(exp_name, max_calcs=None)
            all_results[exp_name] = results
            
            # 进度报告
            elapsed = time.time() - self.start_time
            print(f"\n{'='*60}")
            print(f"进度: {self.total_calcs} 完成")
            print(f"成功: {self.successful_calcs}")
            print(f"失败: {self.failed_calcs}")
            print(f"用时: {elapsed/3600:.2f} 小时")
            print(f"{'='*60}")
        
        # 最终报告
        self.print_final_report()
        
        return all_results
    
    def print_final_report(self):
        """打印最终报告"""
        total_time = time.time() - self.start_time
        
        print(f"\n{'='*70}")
        print(f"🎉 所有计算完成!")
        print(f"{'='*70}")
        print(f"总计算数: {self.total_calcs}")
        print(f"成功: {self.successful_calcs} ({self.successful_calcs/self.total_calcs*100:.1f}%)")
        print(f"失败: {self.failed_calcs} ({self.failed_calcs/self.total_calcs*100:.1f}%)")
        print(f"总用时: {total_time/3600:.2f} 小时")
        print(f"{'='*70}")

def main():
    """主函数"""
    project_root = '/Users/xingqiangchen/sci-simukit'
    runner = RealDFTRunner(project_root)
    
    try:
        runner.run_all_experiments()
    except KeyboardInterrupt:
        print(f"\n\n⚠️  用户中断")
        runner.print_final_report()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        runner.print_final_report()
        sys.exit(1)

if __name__ == '__main__':
    main()

