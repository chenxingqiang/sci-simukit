#!/bin/bash

# 论文复现计算运行脚本
# Paper reproduction calculation runner

echo "=== 论文复现：单分子层富勒烯网络中的电子局域化和迁移率 ==="
echo "Paper: Electron Localization and Mobility in Monolayer Fullerene Networks"
echo "Authors: Capobianco et al."
echo ""

# 检查 CP2K 是否可用
if ! command -v cp2k.ssmp &> /dev/null; then
    echo "错误：未找到 cp2k.ssmp"
    echo "请确保 CP2K 已正确安装并在 PATH 中"
    exit 1
fi

echo "使用的 CP2K 版本："
cp2k.ssmp --version | head -1

# 创建结果目录
mkdir -p results
mkdir -p results/probe_method
mkdir -p results/dielectric
mkdir -p results/md_simulation
mkdir -p results/polaron_ipr

echo ""
echo "=== 计算1：氟原子探针方法确定 αK 值 ==="
echo "目标：确定 Koopman's compliant αK 值（预期：20.9%-21.4%）"
echo ""

# 创建简化的测试计算
cat > simple_c60_test.inp << 'EOF'
&GLOBAL
  PROJECT simple_c60_test
  RUN_TYPE ENERGY
  PRINT_LEVEL MEDIUM
&END GLOBAL

&FORCE_EVAL
  METHOD Quickstep
  &DFT
    BASIS_SET_FILE_NAME BASIS_MOLOPT
    POTENTIAL_FILE_NAME GTH_POTENTIALS
    
    &MGRID
      CUTOFF 400  # 降低截断以快速测试
      REL_CUTOFF 50
    &END MGRID
    
    &QS
      METHOD GPW
      EPS_DEFAULT 1.0E-8
    &END QS
    
    &SCF
      SCF_GUESS ATOMIC
      MAX_SCF 50
      EPS_SCF 1.0E-5
      IGNORE_CONVERGENCE_FAILURE
      
      &OT
        MINIMIZER CG
        PRECONDITIONER FULL_SINGLE_INVERSE
      &END OT
    &END SCF
    
    # 使用 PBE 泛函进行初始测试
    &XC
      &XC_FUNCTIONAL
        &PBE
        &END PBE
      &END XC_FUNCTIONAL
    &END XC
    
    &PRINT
      &MO
        EIGENVALUES
        &EACH
          QS_SCF 0
        &END EACH
      &END MO
    &END PRINT
  &END DFT
  
  &SUBSYS
    &CELL
      ABC 10.0 10.0 10.0
      PERIODIC NONE
    &END CELL
    
    &TOPOLOGY
      COORD_FILE_NAME ../C60.xyz
      COORD_FILE_FORMAT XYZ
    &END TOPOLOGY
    
    &KIND C
      BASIS_SET DZVP-MOLOPT-GTH-q4
      POTENTIAL GTH-PBE-q4
    &END KIND
  &END SUBSYS
&END FORCE_EVAL
EOF

echo "运行简化的 C60 测试计算..."
if cp2k.ssmp -i simple_c60_test.inp -o simple_c60_test.out; then
    echo "✓ 简化测试计算成功完成"
    
    # 提取关键信息
    if grep -q "PROGRAM ENDED" simple_c60_test.out; then
        echo "✓ CP2K 正常结束"
        
        # 提取总能量
        total_energy=$(grep "Total energy:" simple_c60_test.out | tail -1 | awk '{print $3}')
        echo "  总能量: $total_energy Hartree"
        
        # 提取 HOMO-LUMO 能级
        echo "  提取分子轨道能级..."
        
        # 继续运行更复杂的计算
        echo ""
        echo "=== 现在运行 vdW 相互作用测试 ==="
        
        # 创建包含 vdW 修正的测试
        cat > c60_vdw_test.inp << 'EOF'
&GLOBAL
  PROJECT c60_vdw_test
  RUN_TYPE ENERGY
  PRINT_LEVEL MEDIUM
&END GLOBAL

&FORCE_EVAL
  METHOD Quickstep
  &DFT
    BASIS_SET_FILE_NAME BASIS_MOLOPT
    POTENTIAL_FILE_NAME GTH_POTENTIALS
    
    &MGRID
      CUTOFF 400
      REL_CUTOFF 50
    &END MGRID
    
    &QS
      METHOD GPW
      EPS_DEFAULT 1.0E-8
    &END QS
    
    &SCF
      SCF_GUESS ATOMIC
      MAX_SCF 50
      EPS_SCF 1.0E-5
      IGNORE_CONVERGENCE_FAILURE
      
      &OT
        MINIMIZER CG
        PRECONDITIONER FULL_SINGLE_INVERSE
      &END OT
    &END SCF
    
    # PBE + rVV10 泛函
    &XC
      &XC_FUNCTIONAL
        &PBE
        &END PBE
      &END XC_FUNCTIONAL
      
      &vdW_POTENTIAL
        DISPERSION_FUNCTIONAL NON_LOCAL
        &NON_LOCAL
          TYPE RVV10
          PARAMETERS 6.3 0.0093
          CUTOFF 200
        &END NON_LOCAL
      &END vdW_POTENTIAL
    &END XC
    
    &PRINT
      &MO
        EIGENVALUES
        &EACH
          QS_SCF 0
        &END EACH
      &END MO
    &END PRINT
  &END DFT
  
  &SUBSYS
    &CELL
      ABC 15.0 15.0 15.0
      PERIODIC NONE
    &END CELL
    
    &TOPOLOGY
      COORD_FILE_NAME ../C60.xyz
      COORD_FILE_FORMAT XYZ
    &END TOPOLOGY
    
    &KIND C
      BASIS_SET DZVP-MOLOPT-GTH-q4
      POTENTIAL GTH-PBE-q4
    &END KIND
  &END SUBSYS
&END FORCE_EVAL
EOF
        
        echo "运行 PBE+rVV10 测试..."
        if cp2k.ssmp -i c60_vdw_test.inp -o c60_vdw_test.out; then
            echo "✓ PBE+rVV10 计算成功完成"
            
            # 比较能量
            vdw_energy=$(grep "Total energy:" c60_vdw_test.out | tail -1 | awk '{print $3}')
            echo "  PBE+rVV10 总能量: $vdw_energy Hartree"
            
            if [ ! -z "$total_energy" ] && [ ! -z "$vdw_energy" ]; then
                vdw_correction=$(echo "$vdw_energy - $total_energy" | bc -l)
                echo "  vdW 修正: $vdw_correction Hartree"
            fi
        else
            echo "✗ PBE+rVV10 计算失败"
        fi
    else
        echo "✗ CP2K 计算未正常结束"
    fi
else
    echo "✗ 简化测试计算失败"
    echo "请检查 CP2K 安装和输入文件"
fi

echo ""
echo "=== 测试总结 ==="
echo "基础功能测试完成。"
echo ""
echo "论文复现计算清单："
echo "1. [ ] 氟原子探针方法确定 αK = 21%"
echo "2. [ ] 计算介电常数 ε∞ = 3.80"
echo "3. [ ] MD 模拟热重整化效应"
echo "4. [ ] 计算反参与比(IPR)分析电子局域化"
echo "5. [ ] 验证带隙、电离势、电子亲和能"
echo ""
echo "下一步："
echo "- 优化计算参数和基组"
echo "- 运行完整的超胞计算"
echo "- 实现混合泛函 PBE(αK)+rVV10-b7.8"
echo ""
echo "参考论文数据："
echo "- vdW C60 带隙: ~2.0 eV"
echo "- αK 最优值: 20.9%-21.4%"
echo "- IPR 比值: vdW=34, qHP=30"
