# 实验1: 结构表征实验

## 📋 实验目标
验证qHP C₆₀网络的结构参数和应变响应

## 🎯 验证指标
- 晶格参数: a = 36.67 ± 0.5 Å, b = 30.84 ± 0.3 Å
- 应变响应: 线性关系 ε = Δa/a₀
- 结构稳定性: 应变范围 -5% 到 +5% 内保持qHP相

## 🔬 实验方法

### 1. X射线衍射 (XRD)
- **设备**: Bruker D8 Advance
- **参数**: Cu Kα辐射, 2θ = 5-80°, 步长0.02°
- **样品**: 不同应变下的qHP C₆₀薄膜

### 2. 透射电子显微镜 (TEM)
- **设备**: JEOL JEM-2100F
- **参数**: 200kV, 高分辨率模式
- **样品**: 超薄切片, 厚度<50nm

### 3. 拉曼光谱
- **设备**: Renishaw inVia
- **参数**: 532nm激光, 功率1mW, 积分时间10s
- **测量**: 应变诱导的键长变化

### 4. 原子力显微镜 (AFM)
- **设备**: Bruker Dimension Icon
- **模式**: 轻敲模式, 扫描范围5×5μm
- **测量**: 表面形貌和粗糙度

## 📁 文件夹结构
```
exp_1_structure/
├── inputs/
│   ├── samples/           # 样品信息
│   ├── protocols/         # 实验协议
│   └── parameters/       # 设备参数
├── outputs/
│   ├── xrd/              # XRD数据
│   ├── tem/              # TEM图像
│   ├── raman/            # 拉曼光谱
│   └── afm/              # AFM数据
├── analysis/
│   ├── lattice_params.py # 晶格参数分析
│   ├── strain_response.py # 应变响应分析
│   └── stability_check.py # 结构稳定性检查
├── results/
│   ├── lattice_parameters.json
│   ├── strain_response.json
│   └── stability_report.json
└── README.md
```

## ✅ 验证逻辑
```
IF 实验晶格参数 = 理论值 ± 误差范围
AND 应变响应呈线性关系
AND 结构在应变范围内稳定
THEN 结构模型验证通过
```

## 📊 预期结果
- XRD峰位与理论晶格参数一致
- 拉曼峰位随应变线性移动
- TEM显示qHP相结构完整
- AFM显示表面平整度<1nm
