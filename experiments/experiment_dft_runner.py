#!/usr/bin/env python3
"""
实验验证DFT运行器 - 使用简化的输入文件
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
        logging.FileHandler('experiment_dft_runner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ExperimentDFTRunner:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.cp2k_exe = "/opt/homebrew/bin/cp2k.ssmp"
        self.experiment_base_dir = self.project_root / "experiments"
        
        # 验证CP2K可执行文件
        if not Path(self.cp2k_exe).exists():
            raise FileNotFoundError(f"CP2K可执行文件不存在: {self.cp2k_exe}")
        
        logger.info(f"实验DFT运行器初始化，项目根目录: {self.project_root}")

    def create_strain_input_file(self, strain_percent: float, output_path: Path):
        """创建应变C60输入文件"""
        # 基础晶格参数
        base_a = 36.67
        base_b = 30.84
        
        # 计算应变后的晶格参数
        if strain_percent > 0:
            a = base_a * (1 + strain_percent / 100)
            b = base_b * (1 + strain_percent / 100)
        else:
            a = base_a * (1 + strain_percent / 100)
            b = base_b * (1 + strain_percent / 100)
        
        # 创建简化的C60输入文件
        input_content = f"""&GLOBAL
  PROJECT C60_strain_{strain_percent:+.1f}
  RUN_TYPE ENERGY
  PRINT_LEVEL LOW
&END GLOBAL
&FORCE_EVAL
  METHOD Quickstep
  &DFT
    BASIS_SET_FILE_NAME BASIS_MOLOPT
    POTENTIAL_FILE_NAME GTH_POTENTIALS
    &MGRID
      CUTOFF 400
    &END MGRID
    &QS
      METHOD GPW
    &END QS
    &SCF
      SCF_GUESS ATOMIC
      MAX_SCF 50
      EPS_SCF 1.0E-6
      IGNORE_CONVERGENCE_FAILURE TRUE
      &OT
        MINIMIZER CG
        PRECONDITIONER FULL_SINGLE_INVERSE
      &END OT
    &END SCF
    &XC
      &XC_FUNCTIONAL
        &PBE
        &END PBE
      &END XC_FUNCTIONAL
    &END XC
  &END DFT
  &SUBSYS
    &CELL
A  {a:.2f}    0.00    0.00
B   0.00   {b:.2f}    0.00
C   0.00    0.00   20.00
    &END CELL
    &COORD
C         0.0000000000        0.0000000000        0.0000000000
C         1.4000000000        0.0000000000        0.0000000000
C         0.7000000000        1.2124355650        0.0000000000
C         0.7000000000        0.4041451883        1.1428571429
C         2.1000000000        0.4041451883        1.1428571429
C         1.4000000000        1.2124355650        1.1428571429
C         3.5000000000        0.0000000000        0.0000000000
C         4.9000000000        0.0000000000        0.0000000000
C         4.2000000000        1.2124355650        0.0000000000
C         4.2000000000        0.4041451883        1.1428571429
C         5.6000000000        0.4041451883        1.1428571429
C         4.9000000000        1.2124355650        1.1428571429
C         7.0000000000        0.0000000000        0.0000000000
C         8.4000000000        0.0000000000        0.0000000000
C         7.7000000000        1.2124355650        0.0000000000
C         7.7000000000        0.4041451883        1.1428571429
C         9.1000000000        0.4041451883        1.1428571429
C         8.4000000000        1.2124355650        1.1428571429
C        10.5000000000        0.0000000000        0.0000000000
C        11.9000000000        0.0000000000        0.0000000000
C        11.2000000000        1.2124355650        0.0000000000
C        11.2000000000        0.4041451883        1.1428571429
C        12.6000000000        0.4041451883        1.1428571429
C        11.9000000000        1.2124355650        1.1428571429
C        14.0000000000        0.0000000000        0.0000000000
C        15.4000000000        0.0000000000        0.0000000000
C        14.7000000000        1.2124355650        0.0000000000
C        14.7000000000        0.4041451883        1.1428571429
C        16.1000000000        0.4041451883        1.1428571429
C        15.4000000000        1.2124355650        1.1428571429
C        17.5000000000        0.0000000000        0.0000000000
C        18.9000000000        0.0000000000        0.0000000000
C        18.2000000000        1.2124355650        0.0000000000
C        18.2000000000        0.4041451883        1.1428571429
C        19.6000000000        0.4041451883        1.1428571429
C        18.9000000000        1.2124355650        1.1428571429
C        21.0000000000        0.0000000000        0.0000000000
C        22.4000000000        0.0000000000        0.0000000000
C        21.7000000000        1.2124355650        0.0000000000
C        21.7000000000        0.4041451883        1.1428571429
C        23.1000000000        0.4041451883        1.1428571429
C        22.4000000000        1.2124355650        1.1428571429
C        24.5000000000        0.0000000000        0.0000000000
C        25.9000000000        0.0000000000        0.0000000000
C        25.2000000000        1.2124355650        0.0000000000
C        25.2000000000        0.4041451883        1.1428571429
C        26.6000000000        0.4041451883        1.1428571429
C        25.9000000000        1.2124355650        1.1428571429
C        28.0000000000        0.0000000000        0.0000000000
C        29.4000000000        0.0000000000        0.0000000000
C        28.7000000000        1.2124355650        0.0000000000
C        28.7000000000        0.4041451883        1.1428571429
C        30.1000000000        0.4041451883        1.1428571429
C        29.4000000000        1.2124355650        1.1428571429
C        31.5000000000        0.0000000000        0.0000000000
C        32.9000000000        0.0000000000        0.0000000000
C        32.2000000000        1.2124355650        0.0000000000
C        32.2000000000        0.4041451883        1.1428571429
C        33.6000000000        0.4041451883        1.1428571429
C        32.9000000000        1.2124355650        1.1428571429
C        35.0000000000        0.0000000000        0.0000000000
C        36.4000000000        0.0000000000        0.0000000000
C        35.7000000000        1.2124355650        0.0000000000
C        35.7000000000        0.4041451883        1.1428571429
C        37.1000000000        0.4041451883        1.1428571429
C        36.4000000000        1.2124355650        1.1428571429
    &END COORD
    &KIND C
      BASIS_SET DZVP-MOLOPT-GTH
      POTENTIAL GTH-PBE
    &END KIND
  &END SUBSYS
&END FORCE_EVAL"""
        
        # 写入文件
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(input_content)
        
        logger.info(f"创建应变输入文件: {output_path} (应变: {strain_percent}%)")

    def run_dft_calculation(self, input_name: str, output_dir: Path, 
                          timeout: int = 1800) -> Dict:
        """运行单个DFT计算"""
        logger.info(f"开始DFT计算: {input_name}")
        
        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 输入和输出文件
        input_file = output_dir / f"{input_name}.inp"
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

    def run_strain_experiment(self, exp_id: str = "exp_1_structure") -> Dict:
        """运行应变实验"""
        logger.info(f"开始运行应变实验: {exp_id}")
        
        exp_dir = self.experiment_base_dir / exp_id
        dft_outputs_dir = exp_dir / "outputs" / "dft_raw_outputs"
        
        # 应变范围：-5% 到 +5%
        strain_values = [-5.0, -2.5, 0.0, 2.5, 5.0]
        results = {}
        
        for strain in strain_values:
            input_name = f"C60_strain_{strain:+.1f}_pristine"
            
            # 创建输入文件
            input_file = dft_outputs_dir / f"{input_name}.inp"
            self.create_strain_input_file(strain, input_file)
            
            # 运行计算
            result = self.run_dft_calculation(
                input_name=input_name,
                output_dir=dft_outputs_dir,
                timeout=1800
            )
            
            results[input_name] = result
        
        logger.info(f"应变实验 {exp_id} 完成")
        return results

def main():
    """主函数 - 运行应变实验"""
    try:
        runner = ExperimentDFTRunner()
        
        print("🧮 开始DFT应变实验验证")
        print("="*50)
        
        # 运行应变实验
        results = runner.run_strain_experiment("exp_1_structure")
        
        # 打印结果摘要
        print("\n📊 DFT应变实验结果摘要:")
        print("-" * 50)
        
        for calc_name, result in results.items():
            if result["status"] == "completed":
                output_info = result.get("output_info", {})
                energy = output_info.get("total_energy", "N/A")
                gap = output_info.get("homo_lumo_gap", "N/A")
                converged = output_info.get("converged", False)
                print(f"  {calc_name}:")
                print(f"    能量: {energy} Hartree")
                print(f"    带隙: {gap} eV")
                print(f"    收敛: {converged}")
            else:
                print(f"  {calc_name}: 失败 - {result.get('error', '未知错误')}")
        
        print("\n✅ 应变实验验证完成")
        
    except Exception as e:
        logger.error(f"主函数执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
