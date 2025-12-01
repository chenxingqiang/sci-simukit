# 极化子结合能计算方案

## 📋 概述

为了与论文中的极化子结合能λ (0.10-0.13 eV) 直接对应，我们实施了专门的极化子结合能计算模块。

## 🎯 计算目标

**极化子结合能 λ (Polaron Binding Energy)**:
- 定义: 电荷载流子与晶格弛豫的耦合能
- 公式: `λ = E(charged, relaxed) - E(charged, neutral_geom)`
- 物理意义: 描述电荷在材料中的局域化程度
- 论文参考值: λ = 0.10-0.13 eV (pristine C₆₀)

## 🔬 计算方法

### 理论基础
根据论文使用的Koopmans functional方法，极化子结合能通过以下步骤计算：

1. **中性体系**: E(neutral) - 计算中性C₆₀的能量
2. **带电体系(中性几何)**: E(charged, neutral_geom) - 在中性几何构型下添加/移除一个电子
3. **带电体系(优化几何)**: E(charged, relaxed) - 优化带电体系的几何构型
4. **极化子结合能**: λ = E(charged, relaxed) - E(charged, neutral_geom)

### 计算细节
- **泛函**: PBE + rVV10 (与论文一致)
- **基组**: DZVP-MOLOPT-GTH
- **电荷态**: 
  - 电子极化子: 负电荷 (charge = -1)
  - 空穴极化子: 正电荷 (charge = +1)
- **几何优化**: BFGS优化器，最大200步

## 📊 计算体系

我们将计算以下4个体系的极化子结合能：

| 体系 | 掺杂元素 | 浓度 | 预期λ (eV) |
|------|---------|------|-----------|
| 1. Pristine C₆₀ | - | - | 0.10-0.13 |
| 2. B-doped C₆₀ | B (硼) | 5% | 待计算 |
| 3. N-doped C₆₀ | N (氮) | 5% | 待计算 |
| 4. P-doped C₆₀ | P (磷) | 5% | 待计算 |

## ⏱️ 时间估算

每个体系需要完成以下计算：
1. 中性体系单点能量: ~15-30分钟
2. 带电体系单点能量: ~15-30分钟
3. 带电体系几何优化: ~60-90分钟
4. (可选) 空穴极化子: 重复2-3

**总计**: 
- 每个体系: ~2小时 (只计算电子极化子)
- 每个体系: ~3-4小时 (计算电子+空穴极化子)
- **全部4个体系**: ~8-16小时

## 🚀 执行方案

### 方案A: 测试运行 (推荐先执行)
```bash
cd /Users/xingqiangchen/sci-simukit/experiments/exp_2_doping
python test_polaron_calc.py
```
- 只计算pristine C₆₀
- 验证计算流程是否正确
- 检查结果是否在合理范围内 (0.10-0.13 eV)
- 时间: ~2小时

### 方案B: 完整批量计算
```bash
cd /Users/xingqiangchen/sci-simukit/experiments/exp_2_doping
python calculate_polaron_binding.py
```
- 计算全部4个体系
- 生成完整的极化子结合能数据
- 时间: ~8-16小时

### 方案C: 后台运行 (长时间计算)
```bash
cd /Users/xingqiangchen/sci-simukit/experiments/exp_2_doping
nohup python calculate_polaron_binding.py > polaron_calc.log 2>&1 &
```
- 后台运行，不占用终端
- 可以通过 `tail -f polaron_calc.log` 查看进度

## 📈 预期结果

### Pristine C₆₀ (验证计算)
- **预期**: λ ≈ 0.10-0.13 eV
- **用途**: 验证计算方法的准确性

### 掺杂C₆₀ (新结果)
- **B掺杂**: 预期λ略有变化（硼是电子缺陷型）
- **N掺杂**: 预期λ略有变化（氮是电子富集型）
- **P掺杂**: 预期λ接近pristine（磷与碳性质相近）

## 🎯 与论文的对应关系

计算完成后，我们将得到：

| 当前计算 | 论文对应 | 数值 |
|---------|---------|------|
| 掺杂形成能 E_f | 已有 | 31-461 eV |
| **极化子结合能 λ** | **直接对应** | **待计算** |
| 电子耦合 J | 待计算 | 论文: 33-81 meV |

**完成后**: 我们将同时拥有掺杂形成能和极化子结合能，完整描述掺杂体系的性质。

## ⚠️ 注意事项

1. **计算资源**: 确保有足够的CPU和内存（建议4GB+）
2. **时间安排**: 长时间计算建议后台运行或晚上执行
3. **中断恢复**: 每个体系计算完成后自动保存，可以中断后继续
4. **结果验证**: Pristine C₆₀的结果应在0.10-0.13 eV范围内

## 📝 下一步

### 立即执行 (测试)
```bash
python test_polaron_calc.py
```

### 稍后执行 (完整计算)
```bash
# 在合适的时间运行
python calculate_polaron_binding.py
```

### 查看结果
```bash
# 查看已计算的结果
cat polaron_calculations/polaron_binding_summary.json

# 查看单个体系结果
cat polaron_calculations/polaron_binding_pristine_0.05.json
```

## 💡 建议

**推荐流程**:
1. ✅ 先运行测试 (`test_polaron_calc.py`) - 2小时
2. ✅ 验证pristine C₆₀的结果是否合理
3. ✅ 如果结果正确，运行完整计算
4. ✅ 分析所有掺杂体系的极化子结合能
5. ✅ 更新实验2的结果，同时报告E_f和λ

---

**准备开始了吗？** 🚀

