#!/usr/bin/env python3
"""
DFT实验快速测试
运行一个简单的DFT计算来验证系统
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path

def find_cp2k():
    """查找CP2K可执行文件，优先使用单线程版本"""
    # 优先使用单线程版本避免MPI问题
    single_thread_paths = [
        "/opt/homebrew/bin/cp2k.ssmp",
        "/usr/local/bin/cp2k.ssmp",
        "cp2k.ssmp"
    ]
    
    for path in single_thread_paths:
        if shutil.which(path):
            return shutil.which(path)
    
    # 如果找不到单线程版本，尝试多线程版本
    multi_thread_paths = [
        "cp2k",
        "cp2k.popt", 
        "cp2k.psmp",
        "/usr/local/bin/cp2k",
        "/opt/cp2k/bin/cp2k"
    ]
    
    for path in multi_thread_paths:
        if shutil.which(path):
            return shutil.which(path)
    return None

def test_simple_dft():
    """测试简单的DFT计算"""
    print("🧮 DFT快速测试")
    print("="*40)
    
    # 查找CP2K
    cp2k_exe = find_cp2k()
    if not cp2k_exe:
        print("❌ 未找到CP2K可执行文件")
        print("请安装CP2K或设置PATH环境变量")
        return False
        
    print(f"✅ 找到CP2K: {cp2k_exe}")
    
    # 查找输入文件
    project_root = Path("/Users/xingqiangchen/sci-simukit")
    inputs_dir = project_root / "hpc_calculations" / "inputs"
    
    if not inputs_dir.exists():
        print("❌ 未找到DFT输入文件目录")
        return False
        
    # 3. 使用简化的测试输入文件
    test_input_file = project_root / "experiments" / "simple_c60_test.inp"
    if not test_input_file.exists():
        print("❌ 未找到简化测试输入文件")
        return False
    
    test_calc = "simple_c60_test"
        
    print(f"✅ 选择测试计算: {test_calc}")
    
    # 创建测试目录
    test_dir = Path("experiments") / "dft_test"
    test_dir.mkdir(exist_ok=True)
    
    # 复制简化输入文件
    local_input = test_dir / f"{test_calc}.inp"
    shutil.copy2(test_input_file, local_input)
    
    # 输出文件
    output_file = test_dir / f"{test_calc}.out"
    
    # 构建命令
    cmd = [cp2k_exe, "-i", str(local_input)]
    
    print(f"🚀 开始DFT计算...")
    print(f"命令: {' '.join(cmd)}")
    print(f"工作目录: {test_dir}")
    
    # 确保在正确的工作目录
    os.chdir(project_root)
    
    start_time = time.time()
    
    try:
        with open(output_file, 'w') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, 
                                  cwd=test_dir, timeout=1800)  # 30分钟超时
            
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ DFT计算成功完成!")
            print(f"耗时: {elapsed_time:.1f}秒")
            print(f"输出文件: {output_file}")
            
            # 检查输出文件
            if output_file.exists() and output_file.stat().st_size > 0:
                print(f"✅ 输出文件生成成功 ({output_file.stat().st_size} 字节)")
                
                # 简单检查输出内容
                with open(output_file, 'r') as f:
                    content = f.read()
                    
                if "ENERGY| Total FORCE_EVAL" in content:
                    print("✅ 找到总能量信息")
                    
                if "HOMO-LUMO gap" in content:
                    print("✅ 找到带隙信息")
                    
                print(f"\n📊 DFT测试成功! 系统可以正常运行DFT计算")
                return True
            else:
                print("❌ 输出文件为空或不存在")
                return False
        else:
            print(f"❌ DFT计算失败")
            print(f"错误信息: {result.stderr.decode()[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ DFT计算超时 (30分钟)")
        return False
    except Exception as e:
        print(f"💥 DFT计算异常: {e}")
        return False

def main():
    """主函数"""
    success = test_simple_dft()
    
    if success:
        print(f"\n🎉 DFT系统测试通过!")
        print(f"现在可以运行完整的DFT实验验证")
        print(f"使用: python experiments/dft_experiment_runner.py")
    else:
        print(f"\n❌ DFT系统测试失败")
        print(f"请检查CP2K安装和输入文件")

if __name__ == "__main__":
    main()
