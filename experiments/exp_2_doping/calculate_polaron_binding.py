#!/usr/bin/env python3
"""
极化子结合能计算模块

计算掺杂C60体系的极化子结合能 λ (Polaron Binding Energy)

根据论文方法:
λ = E(charged, relaxed) - E(neutral) - [E(charged) - E(neutral)]_rigid
  = E(charged, relaxed) - E(charged, neutral_geometry)
  
物理意义: 电荷载流子与晶格弛豫的耦合能
论文参考值: λ = 0.10-0.13 eV (pristine C60)
"""

import subprocess
import json
import logging
from pathlib import Path
import sys
import time

# 添加父目录到路径以导入c60_coordinates
sys.path.append(str(Path(__file__).parent.parent))
from c60_coordinates import format_c60_coordinates_for_cp2k

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PolaronBindingCalculator:
    """极化子结合能计算器"""
    
    def __init__(self, experiment_dir=None):
        self.experiment_dir = experiment_dir or Path(__file__).parent
        self.polaron_dir = self.experiment_dir / "polaron_calculations"
        self.polaron_dir.mkdir(exist_ok=True)
        
        # 要计算的掺杂体系
        self.doping_systems = [
            {'dopant': 'pristine', 'concentration': 0.05},
            {'dopant': 'B', 'concentration': 0.05},
            {'dopant': 'N', 'concentration': 0.05},
            {'dopant': 'P', 'concentration': 0.05},
        ]
        
    def create_cp2k_input_polaron(self, dopant: str, concentration: float, 
                                   charge: int = 0, geo_opt: bool = False) -> str:
        """
        创建极化子计算的CP2K输入文件
        
        Args:
            dopant: 掺杂元素 (pristine, B, N, P)
            concentration: 掺杂浓度
            charge: 体系电荷 (0=中性, -1=负离子, +1=正离子)
            geo_opt: 是否进行几何优化
        """
        
        # 计算掺杂原子数
        n_c60_atoms = 60
        n_dopant = max(1, int(n_c60_atoms * concentration)) if dopant != 'pristine' else 0
        
        # 获取C60坐标并进行掺杂
        c60_coords_str = format_c60_coordinates_for_cp2k()
        
        if dopant != 'pristine' and n_dopant > 0:
            coords_lines = c60_coords_str.split('\n')
            import random
            random.seed(42 + hash(f"{dopant}_{concentration}"))
            replace_indices = sorted(random.sample(range(len(coords_lines)), n_dopant))
            
            for idx in replace_indices:
                coords_lines[idx] = coords_lines[idx].replace('C ', f'{dopant} ', 1)
            
            c60_coords_str = '\n'.join(coords_lines)
        
        # 选择运行类型
        run_type = "GEO_OPT" if geo_opt else "ENERGY"
        
        # 构建输入文件
        input_content = f"""&GLOBAL
  PROJECT C60_{dopant}_{concentration:.2f}_charge_{charge:+d}{'_opt' if geo_opt else ''}
  RUN_TYPE {run_type}
  PRINT_LEVEL MEDIUM
&END GLOBAL

&FORCE_EVAL
  METHOD Quickstep
  
  &DFT
    BASIS_SET_FILE_NAME /opt/cp2k/data/BASIS_MOLOPT
    BASIS_SET_FILE_NAME /opt/cp2k/data/BASIS_MOLOPT_UZH
    POTENTIAL_FILE_NAME /opt/cp2k/data/GTH_POTENTIALS
    
    CHARGE {charge}
    
    &QS
      METHOD GPW
      EPS_DEFAULT 1.0E-10
      EPS_PGF_ORB 1.0E-8
    &END QS
    
    &MGRID
      CUTOFF 400
      REL_CUTOFF 50
      NGRIDS 4
    &END MGRID
    
    &POISSON
      PERIODIC NONE
      PSOLVER MT
    &END POISSON
    
    &SCF
      MAX_SCF 200
      EPS_SCF 1.0E-5
      SCF_GUESS ATOMIC
      
      &OT
        MINIMIZER DIIS
        PRECONDITIONER FULL_SINGLE_INVERSE
        ENERGY_GAP 0.1
      &END OT
      
      &OUTER_SCF
        MAX_SCF 20
        EPS_SCF 1.0E-5
      &END OUTER_SCF
      
      &PRINT
        &RESTART ON
          BACKUP_COPIES 0
          &EACH
            QS_SCF 50
          &END EACH
        &END RESTART
      &END PRINT
    &END SCF
    
    &XC
      &XC_FUNCTIONAL PBE
      &END XC_FUNCTIONAL
      
      &VDW_POTENTIAL
        POTENTIAL_TYPE NON_LOCAL
        &NON_LOCAL
          TYPE RVV10
          KERNEL_FILE_NAME /opt/cp2k/data/rVV10_kernel_table.dat
        &END NON_LOCAL
      &END VDW_POTENTIAL
    &END XC
    
    {"UKS .TRUE." if charge != 0 else ""}
    MULTIPLICITY {abs(charge) + 1 if charge != 0 else 1}
    
  &END DFT
  
    &SUBSYS
    &CELL
      ABC 25.0 25.0 25.0
      PERIODIC NONE
    &END CELL
    
    &COORD
{c60_coords_str}
    &END COORD
    
    &KIND C
      BASIS_SET DZVP-MOLOPT-GTH
      POTENTIAL GTH-PBE
    &END KIND
    
    &KIND B
      BASIS_SET DZVP-MOLOPT-PBE-GTH-q3
      POTENTIAL GTH-PBE-q3
    &END KIND
    
    &KIND N
      BASIS_SET DZVP-MOLOPT-PBE-GTH-q5
      POTENTIAL GTH-PBE-q5
    &END KIND
    
    &KIND P
      BASIS_SET DZVP-MOLOPT-PBE-GTH-q5
      POTENTIAL GTH-PBE-q5
    &END KIND
  &END SUBSYS
"""
        
        input_content += "&END FORCE_EVAL\n"
        
        # 如果是几何优化，添加MOTION设置 (必须在FORCE_EVAL之外)
        if geo_opt:
            input_content += """
&MOTION
  &GEO_OPT
    TYPE MINIMIZATION
    MAX_ITER 200
    OPTIMIZER BFGS
    
    &BFGS
      TRUST_RADIUS 0.25
    &END BFGS
  &END GEO_OPT
&END MOTION
"""
        
        return input_content
    
    def calculate_polaron_binding_energy(self, dopant: str, concentration: float) -> dict:
        """
        计算指定掺杂体系的极化子结合能
        
        λ = E(charged, relaxed) - E(charged, neutral_geom)
        
        Returns:
            dict with keys: lambda_electron, lambda_hole, neutral_energy, etc.
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"计算极化子结合能: {dopant} @ {concentration:.1%}")
        logger.info(f"{'='*70}")
        
        results = {
            'dopant': dopant,
            'concentration': concentration,
            'status': 'pending'
        }
        
        cp2k_exe = self._find_cp2k_executable()
        if not cp2k_exe:
            logger.error("未找到CP2K可执行文件")
            results['status'] = 'no_cp2k'
            return results
        
        try:
            # 步骤1: 计算中性体系能量 E(neutral)
            logger.info("\n📍 步骤1: 计算中性体系能量...")
            neutral_energy = self._run_single_point(
                dopant, concentration, charge=0, cp2k_exe=cp2k_exe
            )
            
            if neutral_energy is None:
                results['status'] = 'neutral_failed'
                return results
            
            logger.info(f"✅ 中性能量: {neutral_energy:.6f} Hartree")
            results['neutral_energy'] = neutral_energy
            
            # 步骤2: 计算电子极化子
            logger.info("\n📍 步骤2: 计算电子极化子 (electron polaron)...")
            
            # 2a. 带电体系在中性几何构型下的能量
            logger.info("  2a. 计算 E(charged, neutral_geom)...")
            charged_neutral_geom = self._run_single_point(
                dopant, concentration, charge=-1, cp2k_exe=cp2k_exe
            )
            
            if charged_neutral_geom is None:
                results['status'] = 'charged_neutral_failed'
                return results
            
            logger.info(f"  ✅ E(e-, neutral_geom): {charged_neutral_geom:.6f} Hartree")
            
            # 2b. 带电体系优化后的能量
            logger.info("  2b. 计算 E(charged, relaxed)...")
            charged_relaxed = self._run_geometry_optimization(
                dopant, concentration, charge=-1, cp2k_exe=cp2k_exe
            )
            
            if charged_relaxed is None:
                logger.warning("  ⚠️ 几何优化失败，使用单点能量作为近似")
                charged_relaxed = charged_neutral_geom
            else:
                logger.info(f"  ✅ E(e-, relaxed): {charged_relaxed:.6f} Hartree")
            
            # 计算电子极化子结合能 (单位: Hartree)
            lambda_electron_hartree = charged_relaxed - charged_neutral_geom
            lambda_electron_eV = lambda_electron_hartree * 27.211  # 转换为eV
            
            results['electron_polaron'] = {
                'E_neutral': neutral_energy,
                'E_charged_neutral_geom': charged_neutral_geom,
                'E_charged_relaxed': charged_relaxed,
                'lambda_hartree': lambda_electron_hartree,
                'lambda_eV': lambda_electron_eV
            }
            
            logger.info(f"\n✨ 电子极化子结合能: λ_e = {lambda_electron_eV:.4f} eV ({lambda_electron_hartree:.6f} Hartree)")
            
            # 步骤3: 计算空穴极化子 (可选，时间允许的话)
            logger.info("\n📍 步骤3: 计算空穴极化子 (hole polaron)...")
            
            charged_hole_neutral_geom = self._run_single_point(
                dopant, concentration, charge=+1, cp2k_exe=cp2k_exe
            )
            
            if charged_hole_neutral_geom is not None:
                logger.info(f"  ✅ E(h+, neutral_geom): {charged_hole_neutral_geom:.6f} Hartree")
                
                charged_hole_relaxed = self._run_geometry_optimization(
                    dopant, concentration, charge=+1, cp2k_exe=cp2k_exe
                )
                
                if charged_hole_relaxed is None:
                    charged_hole_relaxed = charged_hole_neutral_geom
                else:
                    logger.info(f"  ✅ E(h+, relaxed): {charged_hole_relaxed:.6f} Hartree")
                
                lambda_hole_hartree = charged_hole_relaxed - charged_hole_neutral_geom
                lambda_hole_eV = lambda_hole_hartree * 27.211
                
                results['hole_polaron'] = {
                    'E_charged_neutral_geom': charged_hole_neutral_geom,
                    'E_charged_relaxed': charged_hole_relaxed,
                    'lambda_hartree': lambda_hole_hartree,
                    'lambda_eV': lambda_hole_eV
                }
                
                logger.info(f"\n✨ 空穴极化子结合能: λ_h = {lambda_hole_eV:.4f} eV ({lambda_hole_hartree:.6f} Hartree)")
            
            results['status'] = 'success'
            
            # 保存结果
            self._save_polaron_results(results)
            
        except Exception as e:
            logger.error(f"计算失败: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    def _run_single_point(self, dopant: str, concentration: float, 
                          charge: int, cp2k_exe) -> float:
        """运行单点能量计算"""
        input_content = self.create_cp2k_input_polaron(
            dopant, concentration, charge=charge, geo_opt=False
        )
        
        input_file = self.polaron_dir / f"C60_{dopant}_{concentration:.2f}_q{charge:+d}.inp"
        output_file = self.polaron_dir / f"C60_{dopant}_{concentration:.2f}_q{charge:+d}.out"
        
        with open(input_file, 'w') as f:
            f.write(input_content)
        
        # MPI并行 (32 CPU)
        nprocs = int(os.environ.get('NPROCS', '32'))
        cmd = ['mpirun', '-np', str(nprocs), str(cp2k_exe), '-i', str(input_file)]
        logger.info(f"    命令: mpirun -np {nprocs} {cp2k_exe}")
        
        try:
            start_time = time.time()
            with open(output_file, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE,
                                      timeout=7200, cwd=self.polaron_dir)  # 2小时超时
            
            calc_time = time.time() - start_time
            
            if result.returncode == 0:
                energy = self._extract_energy(output_file)
                if energy is not None:
                    logger.info(f"    ⏱️  用时: {calc_time:.1f}s")
                    return energy
            
        except subprocess.TimeoutExpired:
            logger.error(f"    ❌ 计算超时")
        except Exception as e:
            logger.error(f"    ❌ 计算异常: {e}")
        
        return None
    
    def _run_geometry_optimization(self, dopant: str, concentration: float,
                                   charge: int, cp2k_exe) -> float:
        """运行几何优化"""
        input_content = self.create_cp2k_input_polaron(
            dopant, concentration, charge=charge, geo_opt=True
        )
        
        input_file = self.polaron_dir / f"C60_{dopant}_{concentration:.2f}_q{charge:+d}_opt.inp"
        output_file = self.polaron_dir / f"C60_{dopant}_{concentration:.2f}_q{charge:+d}_opt.out"
        
        with open(input_file, 'w') as f:
            f.write(input_content)
        
        # MPI并行 (32 CPU)
        nprocs = int(os.environ.get('NPROCS', '32'))
        cmd = ['mpirun', '-np', str(nprocs), str(cp2k_exe), '-i', str(input_file)]
        logger.info(f"    命令: mpirun -np {nprocs} {cp2k_exe}")
        
        try:
            start_time = time.time()
            with open(output_file, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE,
                                      timeout=7200, cwd=self.polaron_dir)  # 2小时超时
            
            calc_time = time.time() - start_time
            
            if result.returncode == 0:
                energy = self._extract_energy(output_file)
                if energy is not None:
                    logger.info(f"    ⏱️  用时: {calc_time:.1f}s")
                    return energy
            
        except subprocess.TimeoutExpired:
            logger.warning(f"    ⚠️ 几何优化超时")
        except Exception as e:
            logger.warning(f"    ⚠️ 几何优化异常: {e}")
        
        return None
    
    def _extract_energy(self, output_file: Path) -> float:
        """从输出文件中提取能量"""
        try:
            with open(output_file, 'r') as f:
                content = f.read()
            
            # 查找最后一个ENERGY行
            for line in reversed(content.split('\n')):
                if 'ENERGY| Total FORCE_EVAL' in line:
                    energy = float(line.split()[-1])
                    return energy
        except Exception as e:
            logger.error(f"提取能量失败: {e}")
        
        return None
    
    def _find_cp2k_executable(self):
        """查找CP2K可执行文件 (优先并行版本)"""
        import shutil
        
        possible_paths = [
            Path("/opt/cp2k/exe/Linux-aarch64-minimal/cp2k.psmp"),
            Path("/opt/cp2k/exe/local/cp2k.psmp"),
            Path("/usr/local/bin/cp2k.psmp"),
            Path("/opt/cp2k/exe/Linux-aarch64-minimal/cp2k.psmp"),
            Path("cp2k.psmp"),
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
            
        if shutil.which('cp2k.psmp'):
            return 'cp2k.psmp'
        
        return None
    
    def _save_polaron_results(self, results: dict):
        """保存极化子结合能结果"""
        output_file = self.polaron_dir / f"polaron_binding_{results['dopant']}_{results['concentration']:.2f}.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n💾 结果已保存: {output_file}")
    
    def run_all_calculations(self):
        """运行所有掺杂体系的极化子结合能计算"""
        logger.info("="*70)
        logger.info("开始批量计算极化子结合能")
        logger.info("="*70)
        logger.info(f"\n计划计算 {len(self.doping_systems)} 个体系")
        logger.info("预计总时间: ~{} 小时\n".format(len(self.doping_systems) * 2))
        
        all_results = []
        
        for i, system in enumerate(self.doping_systems, 1):
            logger.info(f"\n[{i}/{len(self.doping_systems)}] 计算体系: {system['dopant']} @ {system['concentration']:.1%}")
            
            result = self.calculate_polaron_binding_energy(
                system['dopant'], system['concentration']
            )
            
            all_results.append(result)
        
        # 保存汇总结果
        summary_file = self.polaron_dir / "polaron_binding_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        # 打印汇总
        self._print_summary(all_results)
        
        return all_results
    
    def _print_summary(self, results: list):
        """打印结果汇总"""
        logger.info("\n" + "="*70)
        logger.info("📊 极化子结合能计算结果汇总")
        logger.info("="*70)
        
        logger.info(f"\n{'体系':<20} {'λ_electron (eV)':<20} {'λ_hole (eV)':<20} {'状态'}")
        logger.info("-"*70)
        
        for result in results:
            dopant = result['dopant']
            conc = result['concentration']
            system_name = f"{dopant} @ {conc:.1%}"
            
            if result['status'] == 'success':
                lambda_e = result.get('electron_polaron', {}).get('lambda_eV', 'N/A')
                lambda_h = result.get('hole_polaron', {}).get('lambda_eV', 'N/A')
                
                if isinstance(lambda_e, (int, float)):
                    lambda_e_str = f"{lambda_e:.4f}"
                else:
                    lambda_e_str = str(lambda_e)
                
                if isinstance(lambda_h, (int, float)):
                    lambda_h_str = f"{lambda_h:.4f}"
                else:
                    lambda_h_str = str(lambda_h)
                
                logger.info(f"{system_name:<20} {lambda_e_str:<20} {lambda_h_str:<20} ✅")
            else:
                logger.info(f"{system_name:<20} {'Failed':<20} {'Failed':<20} ❌")
        
        logger.info("\n" + "="*70)
        logger.info("论文参考值: λ = 0.10-0.13 eV (pristine C60)")
        logger.info("="*70)


def main():
    """主函数"""
    calculator = PolaronBindingCalculator()
    results = calculator.run_all_calculations()
    return results


if __name__ == "__main__":
    main()

