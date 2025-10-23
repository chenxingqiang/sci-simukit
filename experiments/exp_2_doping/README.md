# 实验2: 掺杂合成实验

## 📋 实验目标
合成B/N/P掺杂的qHP C₆₀网络

## 🎯 验证指标
- 掺杂浓度: 2.5%, 5.0%, 7.5% ± 0.2%
- 掺杂均匀性: 标准偏差 < 10%
- 化学状态: B³⁺, N³⁻, P³⁺ 确认

## 🔬 实验方法

### 1. 化学气相沉积 (CVD)
- **设备**: 管式炉CVD系统
- **参数**: 温度800°C, 压力10⁻³ Torr, 时间2h
- **前驱体**: BCl₃, NH₃, PH₃

### 2. 离子注入
- **设备**: 离子注入机
- **参数**: 能量50keV, 剂量10¹⁵ cm⁻²
- **离子**: B⁺, N⁺, P⁺

### 3. X射线光电子能谱 (XPS)
- **设备**: Thermo Scientific K-Alpha
- **参数**: Al Kα辐射, 通能50eV
- **分析**: 结合能和化学状态

### 4. 能量色散X射线光谱 (EDX)
- **设备**: SEM-EDX系统
- **参数**: 加速电压15kV, 束流1nA
- **分析**: 元素分布和浓度

## 📁 文件夹结构
```
exp_2_doping/
├── inputs/
│   ├── samples/           # 样品信息
│   ├── protocols/         # 合成协议
│   └── parameters/        # 设备参数
├── outputs/
│   ├── cvd/              # CVD数据
│   ├── ion_implant/      # 离子注入数据
│   ├── xps/              # XPS数据
│   └── edx/              # EDX数据
├── analysis/
│   ├── doping_synthesis.py # 掺杂分析
│   ├── concentration_analysis.py # 浓度分析
│   └── uniformity_check.py # 均匀性检查
├── results/
│   ├── doping_concentrations.json
│   ├── chemical_states.json
│   └── uniformity_report.json
└── README.md
```

## ✅ 验证逻辑
```
IF 掺杂浓度 = 目标值 ± 0.2%
AND 掺杂均匀性 < 10% 标准偏差
AND 化学状态正确
THEN 掺杂合成验证通过
```

## 📊 预期结果
- XPS显示正确的结合能峰位
- EDX显示均匀的元素分布
- 浓度测量值与目标值一致
- 化学状态符合预期
