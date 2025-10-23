#!/usr/bin/env python3
"""
简化的DFT测试脚本
"""
import subprocess
import shutil
import os
from pathlib import Path

def test_dft_simple():
    """简化的DFT测试"""
    print("🧮 DFT简化测试")
    print("="*40)
    
    # 查找CP2K单线程版本
    cp2k_exe = "/opt/homebrew/bin/cp2k.ssmp"
    if not Path(cp2k_exe).exists():
        print("❌ 未找到CP2K单线程可执行文件")
        return False
    print(f"✅ 找到CP2K: {cp2k_exe}")
    
    # 创建测试目录
    test_dir = Path("experiments/dft_test")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制输入文件
    input_file = Path("experiments/simple_c60_test.inp")
    if not input_file.exists():
        print("❌ 未找到测试输入文件")
        return False
    
    local_input = test_dir / "simple_c60_test.inp"
    shutil.copy2(input_file, local_input)
    
    # 输出文件
    output_file = test_dir / "simple_c60_test.out"
    
    # 构建命令
    cmd = [cp2k_exe, "-i", str(local_input)]
    
    print(f"🚀 开始DFT计算...")
    print(f"命令: {' '.join(cmd)}")
    print(f"工作目录: {test_dir}")
    
    # 运行计算
    try:
        # 使用shell命令运行
        shell_cmd = f"cd {test_dir} && {cp2k_exe} -i simple_c60_test.inp > simple_c60_test.out 2>&1"
        
        result = subprocess.run(
            shell_cmd,
            shell=True,
            timeout=300,  # 5分钟超时
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ DFT计算成功完成")
            
            # 检查输出内容
            with open(output_file, 'r') as f:
                content = f.read()
                
            if "ENERGY| Total FORCE_EVAL" in content:
                print("✅ 找到总能量信息")
                print("✅ DFT系统测试成功")
                return True
            else:
                print("❌ 输出文件不完整")
                return False
        else:
            print("❌ DFT计算失败")
            print(f"返回码: {result.returncode}")
            if result.stderr:
                print(f"错误信息: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ DFT计算超时")
        return False
    except Exception as e:
        print(f"❌ DFT计算异常: {e}")
        return False

if __name__ == "__main__":
    if test_dft_simple():
        print("\n🎉 DFT系统测试通过！")
        exit(0)
    else:
        print("\n❌ DFT系统测试失败")
        exit(1)
