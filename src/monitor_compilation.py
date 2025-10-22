#!/usr/bin/env python3
"""
CP2K编译进度监控器
Monitor CP2K compilation progress
"""

import os
import time
import subprocess
from pathlib import Path

def check_compilation_status():
    """检查编译状态"""
    project_root = Path(__file__).parent.parent
    cp2k_dir = project_root / "cp2k-2025.2"
    
    print("🔍 检查CP2K编译状态...")
    
    # 检查make进程
    try:
        result = subprocess.run(['pgrep', '-f', 'make.*cp2k'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 编译进程运行中...")
            pids = result.stdout.strip().split('\n')
            print(f"   进程ID: {', '.join(pids)}")
        else:
            print("❌ 未发现运行中的编译进程")
    except Exception as e:
        print(f"⚠️  检查进程时出错: {e}")
    
    # 检查可执行文件
    exe_patterns = [
        cp2k_dir / "exe" / "*" / "cp2k*",
        cp2k_dir / "cp2k.psmp",
        cp2k_dir / "cp2k.ssmp",
    ]
    
    found_exe = False
    for pattern in exe_patterns:
        import glob
        exe_files = glob.glob(str(pattern))
        if exe_files:
            print(f"🎉 找到可执行文件: {exe_files}")
            found_exe = True
            
            # 测试可执行文件
            for exe in exe_files:
                try:
                    result = subprocess.run([exe, '--version'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        print(f"✅ {exe} 工作正常")
                        print(f"   版本信息: {result.stdout.split()[0:3]}")
                    else:
                        print(f"⚠️  {exe} 测试失败")
                except Exception as e:
                    print(f"⚠️  测试 {exe} 时出错: {e}")
    
    if not found_exe:
        print("❌ 未找到CP2K可执行文件")
        
        # 检查编译日志
        if os.path.exists("make.log"):
            print("📋 检查编译日志...")
            with open("make.log", "r") as f:
                lines = f.readlines()
                # 显示最后几行
                print("   最后几行:")
                for line in lines[-10:]:
                    print(f"   {line.strip()}")
    
    return found_exe

def monitor_compilation(check_interval=30):
    """监控编译过程"""
    print("🚀 开始监控CP2K编译...")
    print(f"   检查间隔: {check_interval}秒")
    
    start_time = time.time()
    check_count = 0
    
    while True:
        check_count += 1
        elapsed = time.time() - start_time
        
        print(f"\n{'='*50}")
        print(f"检查 #{check_count} (已运行 {elapsed/60:.1f} 分钟)")
        print(f"{'='*50}")
        
        found_exe = check_compilation_status()
        
        if found_exe:
            print("\n🎉 编译成功完成!")
            break
        
        if elapsed > 3600:  # 1小时超时
            print("\n⏰ 编译超时 (1小时)，可能有问题")
            break
        
        print(f"\n⏳ 等待 {check_interval} 秒后继续检查...")
        time.sleep(check_interval)

if __name__ == "__main__":
    try:
        monitor_compilation()
    except KeyboardInterrupt:
        print("\n\n👋 监控已停止")
    except Exception as e:
        print(f"\n❌ 监控出错: {e}")
