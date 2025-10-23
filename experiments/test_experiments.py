#!/usr/bin/env python3
"""
实验验证系统测试脚本
测试已创建的前3个实验
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime

def test_experiment(exp_id, exp_name):
    """测试单个实验"""
    print(f"\n{'='*50}")
    print(f"测试实验: {exp_name}")
    print(f"{'='*50}")
    
    exp_dir = f"experiments/{exp_id}"
    script_name = {
        "exp_1_structure": "lattice_params.py",
        "exp_2_doping": "doping_synthesis.py", 
        "exp_3_electronic": "electronic_properties.py"
    }.get(exp_id, "unknown.py")
    script_path = os.path.join(exp_dir, "analysis", script_name)
    
    if not os.path.exists(script_path):
        print(f"❌ 脚本不存在: {script_path}")
        return False
        
    try:
        # 切换到实验目录
        original_dir = os.getcwd()
        os.chdir(exp_dir)
        
        # 运行实验脚本
        result = subprocess.run([sys.executable, f"analysis/{script_name}"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✅ 实验 {exp_id} 测试成功")
            print(f"输出: {result.stdout[:200]}...")
            return True
        else:
            print(f"❌ 实验 {exp_id} 测试失败")
            print(f"错误: {result.stderr[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ 实验 {exp_id} 超时")
        return False
    except Exception as e:
        print(f"💥 实验 {exp_id} 异常: {e}")
        return False
    finally:
        os.chdir(original_dir)

def main():
    """主函数"""
    print("🧪 实验验证系统测试")
    print("="*50)
    
    # 测试前3个实验
    experiments = [
        ("exp_1_structure", "结构表征实验"),
        ("exp_2_doping", "掺杂合成实验"), 
        ("exp_3_electronic", "电子性质测量")
    ]
    
    success_count = 0
    total_count = len(experiments)
    
    for exp_id, exp_name in experiments:
        if test_experiment(exp_id, exp_name):
            success_count += 1
        time.sleep(1)
    
    print(f"\n{'='*50}")
    print(f"测试完成!")
    print(f"成功: {success_count}/{total_count}")
    print(f"{'='*50}")
    
    # 生成测试报告
    report = {
        "test_summary": {
            "total_experiments": total_count,
            "successful_tests": success_count,
            "test_date": datetime.now().isoformat(),
            "success_rate": f"{success_count/total_count*100:.1f}%"
        },
        "experiments_tested": experiments
    }
    
    with open("experiments/test_report.json", "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📊 测试报告已生成: experiments/test_report.json")

if __name__ == "__main__":
    main()
