# 富勒烯应变工程实验实施计划
## 基于@graphullerene/项目的完整实验方案

**基于论文：** "Strain-Tuned Heteroatom-Doped Graphullerene Networks: Engineering Quantum Transport Properties through Controlled Lattice Deformation"

---

## 🎯 实验目标

基于您的graphullerene项目，实现论文中提出的应变调控杂原子掺杂富勒烯网络的完整实验流程，从原子尺度设计到器件级验证。

---

## 🛠️ 必需软件工具清单

### 1. **核心计算软件**

#### **CP2K** - 第一性原理DFT计算
- **官方网站：** https://www.cp2k.org/
- **下载：** https://github.com/cp2k/cp2k/releases
- **用途：** 
  - 电子结构计算
  - 几何优化
  - 分子动力学模拟
  - Koopmans泛函计算
- **您项目中的配置：** 已有hybrid-vdw-cell-opt.inp等输入文件

#### **Quantum ESPRESSO** - 输运性质计算
- **官方网站：** https://www.quantum-espresso.org/
- **下载：** https://gitlab.com/QEF/q-e/-/releases
- **用途：**
  - 能带结构计算
  - 态密度分析
  - 输运性质计算（结合Wannier90）

#### **VASP** - 商业DFT软件（可选）
- **官方网站：** https://www.vasp.at/
- **获取：** 需要学术许可证
- **优势：** 高效的平面波基组计算

### 2. **机器学习框架**

#### **Python环境配置**
```bash
# 创建conda环境
conda create -n fullerene-ml python=3.9
conda activate fullerene-ml

# 核心科学计算库
pip install numpy pandas scipy matplotlib seaborn
pip install scikit-learn

# 深度学习框架
pip install torch torchvision torchaudio
pip install tensorflow

# 材料科学专用库
pip install ase pymatgen
pip install schnetpack
pip install dgl-cu11x  # 图神经网络
```

#### **关键Python库**
- **ASE (Atomic Simulation Environment)：** 原子结构操作
- **Pymatgen：** 材料科学计算
- **SchNetPack：** 分子性质预测
- **DGL：** 图神经网络
- **PyTorch Geometric：** 几何深度学习

### 3. **数据处理与可视化**

#### **分子可视化**
- **VESTA：** https://jp-minerals.org/vesta/en/
- **VMD：** https://www.ks.uiuc.edu/Research/vmd/
- **Ovito：** https://ovito.org/

#### **数据分析**
- **Jupyter Notebook：** 交互式编程环境
- **Matplotlib/Seaborn：** 绘图库
- **Plotly：** 交互式图表

---

## 📋 实验实施步骤

### **第一阶段：基础结构优化**

#### 1.1 pristine qHP C₆₀网络优化
```bash
# 基于您的hybrid-vdw-cell-opt.inp
cp2k.popt -i hybrid-vdw-cell-opt.inp -o cell_opt.out
```

**输入文件修改要点：**
- 使用PBE+rVV10泛函（b=7.8）
- ADMM方法加速混合泛函计算
- 胞参数优化确定基准结构

#### 1.2 应变场施加
```bash
# 创建应变变形结构（-5% to +5%）
python strain_generator.py --strain_range -5 5 --step 1
```

### **第二阶段：杂原子掺杂设计**

#### 2.1 掺杂位点选择
基于您的项目经验：
- B掺杂：2.5%, 5.0%, 7.5%浓度
- N掺杂：同上浓度范围  
- P掺杂：同上浓度范围
- 混合掺杂：B/N共掺杂优化组合

#### 2.2 掺杂结构生成
```python
# Python脚本示例
from ase import Atoms
from ase.io import write
import numpy as np

def create_doped_structure(base_structure, dopant_atom, concentration):
    """创建掺杂结构"""
    # 基于您的C60网络结构
    # 随机/系统性地替换C原子
    pass
```

### **第三阶段：高通量DFT计算**

#### 3.1 电子结构计算
基于您的C60-hole-fixed-environment.inp模板：

```bash
# 批量DFT计算脚本
for structure in structures/*.xyz; do
    cp template.inp ${structure%.xyz}.inp
    # 修改坐标文件路径
    sed -i "s/COORD_FILE_NAME.*/COORD_FILE_NAME $structure/" ${structure%.xyz}.inp
    # 提交计算
    sbatch submit_cp2k.sh ${structure%.xyz}.inp
done
```

#### 3.2 Koopmans泛函优化
参考您的alpha-30-probe.inp：
- 优化α参数以消除自相互作用误差
- 准确描述极化子形成能

### **第四阶段：输运性质计算**

#### 4.1 能带结构与态密度
```bash
# Quantum ESPRESSO计算
pw.x < scf.in > scf.out
bands.x < bands.in > bands.out
dos.x < dos.in > dos.out
```

#### 4.2 电子迁移率计算
使用Fermi黄金定则方法：
```python
def calculate_mobility(coupling_matrix, reorganization_energy, temperature):
    """
    计算电子迁移率
    基于论文公式 μ = (e/kBT) Σ Pi Σ νij rij² exp(-ΔGij/kBT)
    """
    # 实现迁移率计算
    pass
```

### **第五阶段：机器学习模型训练**

#### 5.1 数据集准备
```python
# 特征提取
features = [
    'atomic_positions',
    'bond_lengths', 
    'doping_concentrations',
    'strain_tensors'
]

targets = [
    'band_gap',
    'electron_mobility', 
    'formation_energy'
]
```

#### 5.2 图神经网络模型
```python
import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, global_mean_pool

class GraphullereneGNN(torch.nn.Module):
    def __init__(self, num_features, hidden_dim=128):
        super().__init__()
        self.conv1 = GCNConv(num_features, hidden_dim)
        self.conv2 = GCNConv(hidden_dim, hidden_dim)
        self.conv3 = GCNConv(hidden_dim, hidden_dim)
        self.fc = torch.nn.Linear(hidden_dim, 3)  # band_gap, mobility, formation_energy
    
    def forward(self, x, edge_index, batch):
        x = F.relu(self.conv1(x, edge_index))
        x = F.relu(self.conv2(x, edge_index))
        x = F.relu(self.conv3(x, edge_index))
        x = global_mean_pool(x, batch)
        x = self.fc(x)
        return x
```

### **第六阶段：性能验证与优化**

#### 6.1 模型验证
- 5折交叉验证
- R² > 0.95目标
- 与DFT结果对比验证

#### 6.2 最优结构预测
```python
# 使用训练好的模型预测新组合
best_compositions = model.predict_optimal_structures(
    strain_range=(-5, 5),
    doping_concentrations=[2.5, 5.0, 7.5],
    dopant_combinations=['B', 'N', 'P', 'B+N']
)
```

---

## 🖥️ 计算资源需求

### **硬件要求**
- **CPU：** 32-64核高性能计算节点
- **内存：** 128-256 GB RAM
- **存储：** 1-10 TB SSD存储
- **GPU：** NVIDIA Tesla V100或A100（机器学习训练）

### **软件许可**
- **CP2K：** 开源免费
- **Quantum ESPRESSO：** 开源免费
- **VASP：** 需要学术许可证（约$2000-5000）
- **Python生态：** 开源免费

---

## 📊 预期输出结果

### **理论计算结果**
1. **电子结构数据：**
   - 能带结构图
   - 态密度曲线
   - 带隙随应变变化

2. **输运性质：**
   - 电子迁移率数据表
   - 应变-迁移率关系
   - 温度依赖性分析

3. **机器学习模型：**
   - 训练好的GNN模型
   - 性能预测新组合
   - 最优设计建议

### **实验验证策略**
1. **合成路径：** 基于文献的C₆₀网络聚合方法
2. **表征技术：** STM, ARPES, 电输运测量
3. **器件制备：** 柔性基底上的器件验证

---

## 🚀 实施时间表

| 阶段 | 任务 | 预计时间 | 主要工具 |
|------|------|----------|----------|
| 1 | 基础结构优化 | 2-3周 | CP2K |
| 2 | 杂原子掺杂设计 | 1-2周 | ASE, Python |
| 3 | 高通量DFT计算 | 4-6周 | CP2K, QE |
| 4 | 输运性质计算 | 2-3周 | QE, Python |
| 5 | 机器学习训练 | 3-4周 | PyTorch, DGL |
| 6 | 验证与优化 | 2-3周 | 综合 |

**总预计时间：** 4-6个月

---

## 💡 关键技术要点

### **基于您项目的优势**
1. **已有计算框架：** CP2K输入文件模板完善
2. **参数优化经验：** rVV10参数(b=7.8)已验证
3. **结构数据：** 多个MD构型可用作训练数据
4. **计算协议：** ADMM加速的混合泛函方法

### **创新实现策略**
1. **多尺度集成：** DFT + ML + 实验验证
2. **高通量筛选：** 自动化计算流程
3. **实时优化：** 机器学习指导的迭代设计
4. **性能预测：** 器件级性能的理论预测

---

## 📥 下载资源汇总

### **必需软件下载链接**
1. **CP2K：** https://github.com/cp2k/cp2k/releases/latest
2. **Quantum ESPRESSO：** https://gitlab.com/QEF/q-e/-/releases
3. **Python/Anaconda：** https://www.anaconda.com/products/distribution
4. **VESTA：** https://jp-minerals.org/vesta/en/download.html
5. **VMD：** https://www.ks.uiuc.edu/Research/vmd/current/

### **Python包安装命令**
```bash
# 一键安装所有依赖
pip install -r requirements.txt
```

这个实验方案完全基于您现有的graphullerene项目基础，充分利用已有的计算经验和数据，通过系统性的扩展实现论文中提出的完整研究流程。所有工具都可以通过网络搜索获得，大部分为开源免费软件。
