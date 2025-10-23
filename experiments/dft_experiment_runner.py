#!/usr/bin/env python3
"""
DFT实验运行器 - 基于成功的测试脚本
"""
import os
import sys
import subprocess
import shutil
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dft_experiment_runner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DFTExperimentRunner:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.cp2k_exe = "/opt/homebrew/bin/cp2k.ssmp"  # 使用单线程版本
        self.hpc_inputs_dir = self.project_root / "hpc_calculations" / "inputs"
        self.experiment_base_dir = self.project_root / "experiments"
        
        # 验证CP2K可执行文件
        if not Path(self.cp2k_exe).exists():
            raise FileNotFoundError(f"CP2K可执行文件不存在: {self.cp2k_exe}")
        
        logger.info(f"DFT实验运行器初始化，项目根目录: {self.project_root}")
        logger.info(f"CP2K可执行文件: {self.cp2k_exe}")

    def _get_cp2k_input_path(self, input_name: str) -> Path:
        """获取CP2K输入文件的完整路径"""
        return self.hpc_inputs_dir / f"{input_name}.inp"

    def run_dft_calculation(self, input_name: str, output_dir: Path, 
                          timeout: int = 1800) -> Dict:
        """
        运行单个DFT计算
        
        Args:
            input_name: 输入文件名（不带.inp后缀）
            output_dir: 输出目录
            timeout: 超时时间（秒）
        
        Returns:
            包含计算结果的字典
        """
        logger.info(f"开始DFT计算: {input_name}")
        
        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 检查输入文件
        input_file = self._get_cp2k_input_path(input_name)
        if not input_file.exists():
            error_msg = f"CP2K输入文件不存在: {input_file}"
            logger.error(error_msg)
            return {"status": "failed", "error": error_msg}
        
        # 复制输入文件到输出目录
        local_input = output_dir / f"{input_name}.inp"
        shutil.copy2(input_file, local_input)
        
        # 输出文件
        output_file = output_dir / f"{input_name}.out"
        
        # 构建shell命令
        shell_cmd = f"cd {output_dir} && {self.cp2k_exe} -i {input_name}.inp > {input_name}.out 2>&1"
        
        logger.info(f"运行命令: {shell_cmd}")
        
        try:
            # 运行计算
            result = subprocess.run(
                shell_cmd,
                shell=True,
                timeout=timeout,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"计算 {input_name} 成功完成")
                
                # 检查输出文件
                if output_file.exists() and output_file.stat().st_size > 0:
                    # 解析输出文件
                    output_info = self._parse_output_file(output_file)
                    return {
                        "status": "completed",
                        "output_path": str(output_file),
                        "output_info": output_info
                    }
                else:
                    error_msg = f"输出文件不存在或为空: {output_file}"
                    logger.error(error_msg)
                    return {"status": "failed", "error": error_msg}
            else:
                error_msg = f"DFT计算失败，返回码: {result.returncode}"
                logger.error(error_msg)
                if result.stderr:
                    logger.error(f"错误信息: {result.stderr}")
                return {"status": "failed", "error": error_msg}
                
        except subprocess.TimeoutExpired:
            error_msg = f"DFT计算超时 ({timeout}秒)"
            logger.error(error_msg)
            return {"status": "failed", "error": error_msg}
        except Exception as e:
            error_msg = f"DFT计算异常: {e}"
            logger.error(error_msg)
            return {"status": "failed", "error": error_msg}

    def _parse_output_file(self, output_file: Path) -> Dict:
        """解析CP2K输出文件，提取关键信息"""
        output_info = {}
        
        try:
            with open(output_file, 'r') as f:
                content = f.read()
            
            # 提取总能量
            if "ENERGY| Total FORCE_EVAL" in content:
                lines = content.split('\n')
                for line in lines:
                    if "ENERGY| Total FORCE_EVAL" in line:
                        try:
                            energy_str = line.split()[-1]
                            output_info['total_energy'] = float(energy_str)
                            break
                        except (ValueError, IndexError):
                            pass
            
            # 提取HOMO-LUMO gap
            if "HOMO-LUMO gap" in content:
                lines = content.split('\n')
                for line in lines:
                    if "HOMO-LUMO gap" in line:
                        try:
                            gap_str = line.split()[-1]
                            output_info['homo_lumo_gap'] = float(gap_str)
                            break
                        except (ValueError, IndexError):
                            pass
            
            # 检查是否收敛
            output_info['converged'] = "SCF run NOT converged" not in content
            
            logger.info(f"解析输出文件: {output_info}")
            
        except Exception as e:
            logger.warning(f"解析输出文件失败: {e}")
        
        return output_info

    def run_dft_for_experiment(self, exp_id: str, input_files: List[str], 
                             timeout: int = 1800) -> Dict:
        """
        为特定实验运行多个DFT计算
        
        Args:
            exp_id: 实验ID
            input_files: 输入文件列表（不带.inp后缀）
            timeout: 超时时间（秒）
        
        Returns:
            包含所有计算结果的字典
        """
        logger.info(f"开始为实验 {exp_id} 运行DFT计算...")
        
        exp_dir = self.experiment_base_dir / exp_id
        dft_outputs_dir = exp_dir / "outputs" / "dft_raw_outputs"
        
        results = {}
        for input_name in input_files:
            logger.info(f"运行计算: {input_name} for {exp_id}")
            
            result = self.run_dft_calculation(
                input_name=input_name,
                output_dir=dft_outputs_dir,
                timeout=timeout
            )
            
            results[input_name] = result
        
        logger.info(f"实验 {exp_id} 的DFT计算完成")
        return results

    def list_available_calculations(self) -> List[str]:
        """列出可用的DFT计算"""
        if not self.hpc_inputs_dir.exists():
            logger.warning(f"输入文件目录不存在: {self.hpc_inputs_dir}")
            return []
        
        input_files = []
        for inp_file in self.hpc_inputs_dir.glob("*.inp"):
            input_files.append(inp_file.stem)
        
        logger.info(f"找到 {len(input_files)} 个可用的DFT计算")
        return sorted(input_files)

def main():
    """主函数 - 运行示例DFT计算"""
    try:
        runner = DFTExperimentRunner()
        
        # 列出可用的计算
        available_calcs = runner.list_available_calculations()
        print(f"可用的DFT计算: {len(available_calcs)} 个")
        
        # 运行一些示例计算
        example_calcs = [
            "C60_strain_+0.0_pristine",
            "C60_strain_+2.5_pristine",
            "C60_strain_p0p0_B_5.0p_config1"
        ]
        
        # 只运行存在的计算
        valid_calcs = [calc for calc in example_calcs if calc in available_calcs]
        
        if valid_calcs:
            print(f"运行示例计算: {valid_calcs}")
            results = runner.run_dft_for_experiment("dft_test", valid_calcs)
            
            # 打印结果摘要
            print("\n📊 DFT计算结果摘要:")
            for calc_name, result in results.items():
                if result["status"] == "completed":
                    output_info = result.get("output_info", {})
                    energy = output_info.get("total_energy", "N/A")
                    gap = output_info.get("homo_lumo_gap", "N/A")
                    converged = output_info.get("converged", False)
                    print(f"  {calc_name}: 能量={energy}, 带隙={gap}, 收敛={converged}")
                else:
                    print(f"  {calc_name}: 失败 - {result.get('error', '未知错误')}")
        else:
            print("❌ 没有找到可用的示例计算")
            
    except Exception as e:
        logger.error(f"主函数执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()