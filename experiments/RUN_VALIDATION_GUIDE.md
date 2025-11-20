# 🔬 本地实验验证指南

**目的**: 在本地运行所有6个实验，逐一验证论文中的理论预测

---

## 📋 实验概览

| # | 实验名称 | 分子体系 | 关键指标 | 验证目标 |
|---|----------|----------|----------|----------|
| 1 | 结构表征 | 1×C60 | 晶格参数, 应变响应 | a=36.67±0.5Å, b=30.84±0.3Å |
| 2 | 掺杂合成 | 1×C60 | 掺杂浓度, 均匀性 | 2.5-7.5% ±0.2%, 均匀性<10% |
| 3 | 电子性质 | 1×C60 | 带隙, 迁移率 | 1.2-2.4eV, 5.2-21.4 cm²V⁻¹s⁻¹ |
| 4 | 极化子转变 | 2×C60 | IPR, 电子耦合 | IPR: 45→25, J: 75→135meV |
| 5 | 协同效应 | 4×C60 | 三个增强因子 | f_deloc=1.8, f_coupling=1.8, f_reorg=1.5 |
| 6 | 最优条件 | 3×C60 | 最优参数, 最大迁移率 | 3%strain+5%doping, μ=21.4 |

---

## 🚀 快速开始

### 方法1: 运行所有实验（推荐）

```bash
# 激活环境
cd /Users/xingqiangchen/sci-simukit
source fullerene-env/bin/activate

# 运行全部验证
cd experiments
python run_local_validation_all.py

# 预计耗时: 10-30分钟（取决于系统性能）
```

### 方法2: 逐个运行实验

```bash
# 实验1: 结构表征
cd experiments/exp_1_structure
python run_structure_experiment.py

# 实验2: 掺杂合成
cd ../exp_2_doping
python run_doping_experiment.py

# 实验3: 电子性质
cd ../exp_3_electronic
python run_electronic_experiment.py

# 实验4: 极化子转变
cd ../exp_4_polaron
python run_polaron_experiment.py

# 实验5: 协同效应
cd ../exp_5_synergy
python run_synergy_experiment.py

# 实验6: 最优条件
cd ../exp_6_optimal
python run_optimal_experiment.py
```

### 方法3: 使用综合验证框架

```bash
# 运行综合验证
cd experiments
python comprehensive_validation_framework.py
```

---

## 📊 输出结果

### 自动生成的文件

运行完成后，会在以下位置生成结果：

```
experiments/
├── local_validation_results/
│   ├── LOCAL_VALIDATION_REPORT.md     # 📄 主报告（Markdown）
│   ├── validation_summary.json         # 📊 数据摘要（JSON）
│   └── local_validation.log            # 📝 运行日志
│
├── exp_1_structure/results/
│   ├── analysis_results.json
│   ├── lattice_parameters.json
│   └── validation_report.json
│
├── exp_2_doping/results/
│   ├── doping_analysis.json
│   └── synthesis_report.json
│
├── [其他实验的results/目录]
│
└── comprehensive_results/
    ├── comprehensive_report.md         # 🎯 综合报告
    └── detailed_results.json           # 详细数据
```

---

## ✅ 验证标准

### 实验1: 结构表征

**通过标准**:
- ✅ 晶格参数 a: 36.17-37.17 Å
- ✅ 晶格参数 b: 30.54-31.14 Å
- ✅ 应变线性响应: R² > 0.95
- ✅ 结构稳定性: 应变范围 -5% 到 +5%

**关键输出**:
```json
{
  "lattice_a": 36.67,
  "lattice_b": 30.84,
  "strain_response_R2": 0.98,
  "stable_range": [-5.0, 5.0]
}
```

### 实验2: 掺杂合成

**通过标准**:
- ✅ 掺杂浓度: 2.3-7.7% (目标±0.2%)
- ✅ 均匀性标准差: <10%
- ✅ 化学状态: B³⁺, N³⁻, P³⁺

**关键输出**:
```json
{
  "B_concentration": 5.0,
  "N_concentration": 5.0,
  "P_concentration": 5.0,
  "uniformity_std": 0.08
}
```

### 实验3: 电子性质

**通过标准**:
- ✅ 带隙范围: 1.2-2.4 eV
- ✅ 迁移率范围: 5.2-21.4 cm²V⁻¹s⁻¹
- ✅ 应变耦合参数: β ≈ 8.2
- ✅ 协同增强: >300%

**关键输出**:
```json
{
  "band_gap_range": [1.2, 2.4],
  "mobility_range": [5.2, 21.4],
  "strain_coupling_beta": 8.2,
  "enhancement_factor": 3.12
}
```

### 实验4: 极化子转变

**通过标准**:
- ✅ IPR pristine: 45-50
- ✅ IPR coupled: 25-30
- ✅ J pristine: 70-80 meV
- ✅ J coupled: 130-140 meV
- ✅ 活化能: 0.08-0.10 eV
- ✅ 转变判据: J_total > λ_total

**关键输出**:
```json
{
  "IPR_pristine": 47.5,
  "IPR_coupled": 27.3,
  "J_pristine": 75,
  "J_coupled": 135,
  "activation_energy": 0.09,
  "transition_criterion": true
}
```

### 实验5: 协同效应

**通过标准**:
- ✅ 离域化因子: f_deloc = 1.7-1.9
- ✅ 耦合增强: f_coupling = 1.7-1.9
- ✅ 重组能降低: f_reorg = 1.4-1.6
- ✅ 总增强: f_total = 8.0-9.5

**关键输出**:
```json
{
  "f_deloc": 1.8,
  "f_coupling": 1.8,
  "f_reorg": 1.5,
  "f_total": 8.75
}
```

### 实验6: 最优条件

**通过标准**:
- ✅ 最优应变: 2.5-3.5%
- ✅ 最优掺杂: 4.5-5.5%
- ✅ 最大迁移率: 20.0-22.0 cm²V⁻¹s⁻¹
- ✅ 混合掺杂 B+N: 19.7 cm²V⁻¹s⁻¹

**关键输出**:
```json
{
  "optimal_strain": 3.0,
  "optimal_doping": 5.0,
  "max_mobility": 21.4,
  "mixed_doping_B_N": 19.7
}
```

---

## 🔧 故障排除

### 问题1: 环境未激活

**错误**: `ModuleNotFoundError: No module named 'ase'`

**解决**:
```bash
source fullerene-env/bin/activate
pip install -r requirements.txt
```

### 问题2: 实验脚本不存在

**错误**: `FileNotFoundError: [Errno 2] No such file or directory`

**解决**:
```bash
# 检查实验目录结构
ls -la experiments/exp_*

# 确保所有脚本存在
find experiments -name "run_*_experiment.py"
```

### 问题3: 依赖包缺失

**错误**: `ImportError: cannot import name '...'`

**解决**:
```bash
# 重新安装依赖
pip install --upgrade -r requirements.txt

# 检查关键包
python -c "import ase, numpy, pandas, torch; print('✓ All OK')"
```

### 问题4: 计算超时

**错误**: `subprocess.TimeoutExpired`

**解决**:
修改 `run_local_validation_all.py`:
```python
# 增加超时时间（第245行附近）
timeout=600  # 从300改为600秒（10分钟）
```

### 问题5: 结果文件未生成

**原因**: 实验脚本可能未正确保存结果

**解决**:
```bash
# 手动运行单个实验查看输出
cd experiments/exp_1_structure
python run_structure_experiment.py

# 检查是否生成results/目录
ls -la results/
```

---

## 📈 性能优化

### 加速计算

1. **使用快速模式**:
```python
# 在各实验脚本中设置
quick_mode = True
n_samples = 10  # 减少样本数
```

2. **并行运行（高级）**:
```bash
# 同时运行多个实验（需要多核CPU）
python exp_1_structure/run_structure_experiment.py &
python exp_2_doping/run_doping_experiment.py &
wait
```

3. **使用缓存结果**:
```bash
# 如果已有DFT结果，设置环境变量
export USE_CACHED_RESULTS=1
python run_local_validation_all.py
```

---

## 📊 查看结果

### 方法1: 查看Markdown报告

```bash
# macOS
open experiments/local_validation_results/LOCAL_VALIDATION_REPORT.md

# Linux
xdg-open experiments/local_validation_results/LOCAL_VALIDATION_REPORT.md
```

### 方法2: 查看JSON数据

```bash
# 使用Python查看
python -m json.tool experiments/local_validation_results/validation_summary.json

# 或使用jq（如果已安装）
jq . experiments/local_validation_results/validation_summary.json
```

### 方法3: 生成可视化

```bash
# 运行可视化脚本（如果有）
cd experiments
python generate_validation_plots.py
```

---

## 🎯 预期结果

### 成功运行后的输出

```
╔══════════════════════════════════════════════════════════════╗
║             📊 验证总结报告                                  ║
╚══════════════════════════════════════════════════════════════╝

总实验数: 6
✅ 成功: 6
❌ 失败: 0
🔴 错误: 0
成功率: 100.0%
总耗时: 347.82 秒

══════════════════════════════════════════════════════════════

✅ 实验 1: 结构表征验证 - SUCCESS
   耗时: 45.23 秒
   ✅ 晶格参数 a: 36.67 Å (在范围内)
   ✅ 晶格参数 b: 30.84 Å (在范围内)

✅ 实验 2: 掺杂合成验证 - SUCCESS
   耗时: 52.18 秒
   ✅ B掺杂浓度: 5.0% (在范围内)
   ✅ 均匀性: 8.2% (在范围内)

✅ 实验 3: 电子性质验证 - SUCCESS
   耗时: 67.34 秒
   ✅ 带隙: 1.65 eV (在范围内)
   ✅ 迁移率: 15.3 cm²V⁻¹s⁻¹ (在范围内)

✅ 实验 4: 极化子转变验证 - SUCCESS
   耗时: 71.45 秒
   ✅ IPR: 47.5 → 27.3 (符合预期)
   ✅ J: 75 → 135 meV (符合预期)

✅ 实验 5: 协同效应验证 - SUCCESS
   耗时: 58.92 秒
   ✅ f_deloc: 1.8 (在范围内)
   ✅ f_total: 8.75 (在范围内)

✅ 实验 6: 最优条件验证 - SUCCESS
   耗时: 52.70 秒
   ✅ 最优应变: 3.0% (在范围内)
   ✅ 最大迁移率: 21.4 cm²V⁻¹s⁻¹ (在范围内)

══════════════════════════════════════════════════════════════

🎉 所有实验验证通过！
📄 详细报告: local_validation_results/LOCAL_VALIDATION_REPORT.md
```

---

## 📞 获取帮助

### 如果遇到问题

1. **查看日志文件**:
```bash
tail -100 experiments/local_validation.log
```

2. **检查环境**:
```bash
python --version  # 应该是 3.9+
which python      # 应该在fullerene-env中
pip list | grep -E "ase|numpy|torch"
```

3. **运行诊断**:
```bash
cd experiments
python -c "
import sys
print(f'Python: {sys.version}')
try:
    import ase, numpy, pandas, torch
    print('✓ Core packages installed')
except ImportError as e:
    print(f'✗ Missing: {e}')
"
```

4. **查看README**:
```bash
cat experiments/exp_1_structure/README.md
```

---

## 🎓 理解结果

### 验证成功意味着什么？

✅ **结构稳定**: 理论模型预测的结构在应变下是稳定的  
✅ **掺杂可行**: 提出的掺杂方案在实验上可实现  
✅ **性能提升**: 预测的300%迁移率提升是可信的  
✅ **机制正确**: 非加性耦合机制得到数值验证  
✅ **最优条件**: 找到的最优条件（3%+5%）是可靠的  

### 与论文的关系

本地验证 → 支持论文中的理论预测 → 增强投稿置信度

---

## 🚀 下一步

### 完成本地验证后

1. **📊 分析结果**: 仔细阅读生成的报告
2. **📝 更新论文**: 将验证结果纳入论文
3. **💻 HPC计算**: 在高性能集群上运行真实DFT
4. **🔬 实验合作**: 与实验组对接验证
5. **📄 准备投稿**: 完善论文稿件

---

**✅ 准备好了吗？运行 `python run_local_validation_all.py` 开始验证！**

---

*最后更新: 2025-11-20*  
*版本: 1.0*

