#!/usr/bin/env python3
"""
本地DFT计算管理器
Local DFT Calculation Manager

用于在本地环境运行CP2K DFT计算，包括：
- 环境检查和设置
- 计算任务调度
- 结果分析和可视化

作者: X.Q. Chen
日期: 2025-01-17
"""

import os
import sys
import subprocess
import shutil
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional
import json
import multiprocessing as mp

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('local_dft.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LocalDFTManager:
    """本地DFT计算管理器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.cp2k_dir = self.project_root / "cp2k-2025.2"
        self.hpc_dir = self.project_root / "hpc_calculations"
        self.results_dir = self.project_root / "results" / "local_dft"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # CP2K 可执行文件路径
        self.cp2k_exe = None
        self.n_cores = mp.cpu_count()
        
        logger.info(f"初始化本地DFT管理器")
        logger.info(f"项目根目录: {self.project_root}")
        logger.info(f"可用CPU核心数: {self.n_cores}")
    
    def check_environment(self) -> Dict[str, bool]:
        """检查计算环境"""
        status = {}
        
        # 检查CP2K目录
        status['cp2k_source'] = self.cp2k_dir.exists()
        logger.info(f"CP2K源码目录: {status['cp2k_source']}")
        
        # 检查编译工具
        compilers = ['gcc', 'gfortran', 'make', 'cmake']
        for compiler in compilers:
            status[compiler] = shutil.which(compiler) is not None
            logger.info(f"{compiler}: {status[compiler]}")
        
        # 检查MPI
        status['mpirun'] = shutil.which('mpirun') is not None
        status['mpiexec'] = shutil.which('mpiexec') is not None
        logger.info(f"MPI: mpirun={status['mpirun']}, mpiexec={status['mpiexec']}")
        
        # 检查已编译的CP2K
        possible_exe_paths = [
            self.cp2k_dir / "exe" / "Linux-x86-64-gfortran" / "cp2k.psmp",
            self.cp2k_dir / "exe" / "Darwin-x86-64-gfortran" / "cp2k.psmp", 
            self.cp2k_dir / "exe" / "local" / "cp2k.psmp",
        ]
        
        for exe_path in possible_exe_paths:
            if exe_path.exists():
                self.cp2k_exe = exe_path
                status['cp2k_executable'] = True
                logger.info(f"找到CP2K可执行文件: {exe_path}")
                break
        else:
            # 检查系统安装的 CP2K (Homebrew等)
            for exe_name in ['cp2k.ssmp', 'cp2k.psmp', 'cp2k']:
                exe_path = shutil.which(exe_name)
                if exe_path:
                    self.cp2k_exe = Path(exe_path)
                    status['cp2k_executable'] = True
                    logger.info(f"找到系统CP2K可执行文件: {exe_path}")
                    break
            else:
                status['cp2k_executable'] = False
                logger.warning("未找到CP2K可执行文件")
        
        # 检查输入文件
        input_dir = self.hpc_dir / "inputs"
        status['input_files'] = input_dir.exists() and len(list(input_dir.glob("*.inp"))) > 0
        if status['input_files']:
            n_inputs = len(list(input_dir.glob("*.inp")))
            logger.info(f"找到 {n_inputs} 个CP2K输入文件")
        
        return status
    
    def compile_cp2k(self, force: bool = False) -> bool:
        """编译CP2K"""
        if self.cp2k_exe and self.cp2k_exe.exists() and not force:
            logger.info("CP2K已编译，跳过编译步骤")
            return True
        
        if not self.cp2k_dir.exists():
            logger.error("CP2K源码目录不存在")
            return False
        
        logger.info("开始编译CP2K...")
        
        # 检查架构配置文件
        arch_dir = self.cp2k_dir / "arch"
        
        # macOS配置
        if sys.platform == "darwin":
            arch_files = list(arch_dir.glob("Darwin*.psmp"))
            if not arch_files:
                logger.error("未找到macOS架构配置文件")
                return False
            arch_file = arch_files[0].stem
        else:
            # Linux配置
            arch_files = list(arch_dir.glob("Linux*.psmp"))
            if not arch_files:
                logger.error("未找到Linux架构配置文件")
                return False
            arch_file = arch_files[0].stem
        
        logger.info(f"使用架构配置: {arch_file}")
        
        # 编译命令
        compile_cmd = [
            "make", "-j", str(self.n_cores), 
            f"ARCH={arch_file}", "VERSION=psmp"
        ]
        
        try:
            # 切换到CP2K目录
            original_dir = os.getcwd()
            os.chdir(self.cp2k_dir)
            
            logger.info(f"执行编译命令: {' '.join(compile_cmd)}")
            result = subprocess.run(
                compile_cmd, 
                capture_output=True, 
                text=True, 
                timeout=3600  # 1小时超时
            )
            
            os.chdir(original_dir)
            
            if result.returncode == 0:
                logger.info("CP2K编译成功!")
                # 重新检查可执行文件
                self.check_environment()
                return True
            else:
                logger.error(f"CP2K编译失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("CP2K编译超时")
            return False
        except Exception as e:
            logger.error(f"编译过程出错: {e}")
            return False
    
    def list_available_calculations(self) -> List[str]:
        """列出可用的计算输入文件"""
        input_dir = self.hpc_dir / "inputs"
        if not input_dir.exists():
            return []
        
        inp_files = list(input_dir.glob("*.inp"))
        return [f.stem for f in inp_files]
    
    def run_single_calculation(self, input_name: str, n_procs: int = None) -> bool:
        """运行单个DFT计算"""
        if not self.cp2k_exe or not self.cp2k_exe.exists():
            logger.error("CP2K可执行文件不存在，请先编译CP2K")
            return False
        
        input_file = self.hpc_dir / "inputs" / f"{input_name}.inp"
        if not input_file.exists():
            logger.error(f"输入文件不存在: {input_file}")
            return False
        
        # 设置进程数
        if n_procs is None:
            n_procs = min(4, self.n_cores)  # 默认使用4核心或全部核心
        
        # 创建计算目录
        calc_dir = self.results_dir / input_name
        calc_dir.mkdir(exist_ok=True)
        
        # 复制输入文件
        local_input = calc_dir / f"{input_name}.inp"
        shutil.copy2(input_file, local_input)
        
        # 输出文件
        output_file = calc_dir / f"{input_name}.out"
        
        # 运行命令
        if shutil.which('mpirun'):
            cmd = ['mpirun', '-np', str(n_procs), str(self.cp2k_exe), '-i', str(local_input)]
        else:
            cmd = [str(self.cp2k_exe), '-i', str(local_input)]
        
        logger.info(f"开始计算: {input_name}")
        logger.info(f"命令: {' '.join(cmd)}")
        logger.info(f"工作目录: {calc_dir}")
        
        start_time = time.time()
        
        try:
            with open(output_file, 'w') as f:
                result = subprocess.run(
                    cmd,
                    cwd=calc_dir,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    timeout=7200  # 2小时超时
                )
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            if result.returncode == 0:
                logger.info(f"计算完成: {input_name} ({elapsed:.1f}秒)")
                
                # 保存计算信息
                calc_info = {
                    'input_name': input_name,
                    'start_time': start_time,
                    'end_time': end_time,
                    'elapsed_time': elapsed,
                    'n_procs': n_procs,
                    'status': 'completed',
                    'return_code': result.returncode
                }
                
                with open(calc_dir / 'calc_info.json', 'w') as f:
                    json.dump(calc_info, f, indent=2)
                
                return True
            else:
                logger.error(f"计算失败: {input_name} (返回码: {result.returncode})")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"计算超时: {input_name}")
            return False
        except Exception as e:
            logger.error(f"计算过程出错: {e}")
            return False
    
    def run_batch_calculations(self, input_names: List[str], n_procs_per_calc: int = 2) -> Dict[str, bool]:
        """批量运行DFT计算"""
        results = {}
        
        logger.info(f"开始批量计算，共 {len(input_names)} 个任务")
        
        for i, input_name in enumerate(input_names, 1):
            logger.info(f"进度: {i}/{len(input_names)} - {input_name}")
            results[input_name] = self.run_single_calculation(input_name, n_procs_per_calc)
            
            # 简单的间隔，避免系统过载
            if i < len(input_names):
                time.sleep(2)
        
        # 总结结果
        completed = sum(results.values())
        logger.info(f"批量计算完成: {completed}/{len(input_names)} 成功")
        
        return results
    
    def analyze_result(self, input_name: str) -> Optional[Dict]:
        """分析单个计算结果"""
        calc_dir = self.results_dir / input_name
        output_file = calc_dir / f"{input_name}.out"
        
        if not output_file.exists():
            logger.error(f"输出文件不存在: {output_file}")
            return None
        
        try:
            with open(output_file, 'r') as f:
                content = f.read()
            
            analysis = {
                'input_name': input_name,
                'converged': False,
                'total_energy': None,
                'n_scf_cycles': None,
                'warnings': [],
                'errors': []
            }
            
            # 检查收敛
            if "SCF run converged" in content:
                analysis['converged'] = True
            
            # 提取总能量
            import re
            energy_pattern = r"Total energy:\s*([-\d\.]+)"
            energy_matches = re.findall(energy_pattern, content)
            if energy_matches:
                analysis['total_energy'] = float(energy_matches[-1])
            
            # 统计SCF循环次数
            scf_pattern = r"SCF ITERATION \s*(\d+)"
            scf_matches = re.findall(scf_pattern, content)
            if scf_matches:
                analysis['n_scf_cycles'] = max(int(x) for x in scf_matches)
            
            # 检查警告和错误
            if "WARNING" in content:
                analysis['warnings'] = re.findall(r"WARNING.*", content)
            
            if "ERROR" in content or "ABORT" in content:
                analysis['errors'] = re.findall(r"(ERROR.*|ABORT.*)", content)
            
            return analysis
            
        except Exception as e:
            logger.error(f"分析结果时出错: {e}")
            return None
    
    def get_summary_report(self) -> Dict:
        """获取所有计算的总结报告"""
        completed_calcs = []
        
        for calc_dir in self.results_dir.iterdir():
            if calc_dir.is_dir():
                analysis = self.analyze_result(calc_dir.name)
                if analysis:
                    completed_calcs.append(analysis)
        
        # 统计信息
        total = len(completed_calcs)
        converged = sum(1 for c in completed_calcs if c['converged'])
        with_errors = sum(1 for c in completed_calcs if c['errors'])
        
        report = {
            'total_calculations': total,
            'converged': converged,
            'with_errors': with_errors,
            'success_rate': converged / total if total > 0 else 0,
            'calculations': completed_calcs
        }
        
        return report

def main():
    """主函数"""
    print("🧮 本地DFT计算管理器")
    print("=" * 50)
    
    manager = LocalDFTManager()
    
    # 检查环境
    print("\n1. 检查计算环境...")
    env_status = manager.check_environment()
    
    for key, status in env_status.items():
        status_str = "✓" if status else "✗"
        print(f"   {status_str} {key}")
    
    # 如果没有CP2K可执行文件，尝试编译
    if not env_status.get('cp2k_executable', False):
        print("\n2. 编译CP2K...")
        if env_status.get('cp2k_source', False):
            compile_success = manager.compile_cp2k()
            if not compile_success:
                print("❌ CP2K编译失败，无法继续")
                return
        else:
            print("❌ 未找到CP2K源码，无法编译")
            return
    else:
        print("\n2. CP2K已准备就绪 ✓")
    
    # 列出可用计算
    print("\n3. 可用的DFT计算:")
    available_calcs = manager.list_available_calculations()
    
    if not available_calcs:
        print("   ❌ 未找到输入文件")
        return
    
    # 显示前几个作为示例
    for i, calc in enumerate(available_calcs[:10], 1):
        print(f"   {i:2d}. {calc}")
    
    if len(available_calcs) > 10:
        print(f"   ... 还有 {len(available_calcs) - 10} 个")
    
    print(f"\n   总计: {len(available_calcs)} 个计算")
    
    # 询问用户是否运行测试计算
    print("\n4. 选择要运行的计算:")
    print("   t) 运行测试计算(最简单的)")
    print("   a) 运行所有计算")
    print("   s) 自定义选择")
    print("   q) 退出")
    
    choice = input("\n请选择 [t/a/s/q]: ").strip().lower()
    
    if choice == 'q':
        print("退出程序")
        return
    elif choice == 't':
        # 运行最简单的测试计算
        test_calc = "C60_strain_+0.0_pristine"  # 无应变的纯净C60
        if test_calc in available_calcs:
            print(f"\n5. 运行测试计算: {test_calc}")
            success = manager.run_single_calculation(test_calc, n_procs=2)
            if success:
                print("✓ 测试计算完成")
                analysis = manager.analyze_result(test_calc)
                if analysis:
                    print(f"   收敛: {analysis['converged']}")
                    if analysis['total_energy']:
                        print(f"   总能量: {analysis['total_energy']:.6f} Hartree")
            else:
                print("❌ 测试计算失败")
        else:
            print(f"❌ 未找到测试计算: {test_calc}")
    
    elif choice == 'a':
        print("\n5. 运行所有计算...")
        print("⚠️  这将需要很长时间!")
        confirm = input("确认运行所有计算? [y/N]: ").strip().lower()
        if confirm == 'y':
            results = manager.run_batch_calculations(available_calcs, n_procs_per_calc=2)
            print("\n计算完成!")
    
    elif choice == 's':
        print("\n5. 自定义选择计算...")
        selected = []
        for i, calc in enumerate(available_calcs):
            include = input(f"包含 {calc}? [y/N]: ").strip().lower()
            if include == 'y':
                selected.append(calc)
        
        if selected:
            print(f"\n运行选中的 {len(selected)} 个计算...")
            results = manager.run_batch_calculations(selected, n_procs_per_calc=2)
    
    # 显示总结报告
    print("\n6. 总结报告:")
    report = manager.get_summary_report()
    print(f"   总计算数: {report['total_calculations']}")
    print(f"   成功收敛: {report['converged']}")
    print(f"   成功率: {report['success_rate']:.1%}")
    
    print("\n计算完成! 🎉")
    print(f"结果保存在: {manager.results_dir}")

if __name__ == "__main__":
    main()
