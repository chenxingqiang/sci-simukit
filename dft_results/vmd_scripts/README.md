# VMD Visualization Scripts for C60 Graphullerene

## 结构可视化

### 交互式查看
在VMD中加载xyz文件后，执行：
```tcl
source /path/to/interactive_view.tcl
```

可用命令：
- `setup_c60_view` - 重置为默认视图
- `highlight_c60_cage N` - 高亮第N个C60笼(1-4)
- `show_bonds_only` - 线框视图
- `show_spacefilling` - 空间填充视图
- `render_image filename.tga` - 保存图像

### 批量渲染
```bash
vmd -e render_c60_structure.tcl -args structure.xyz output.tga
```

## 电子轨道可视化

⚠️ **需要重新计算生成cube文件**

在CP2K输入文件中添加以下设置来输出分子轨道：

```
&FORCE_EVAL
  &DFT
    &PRINT
      &MO_CUBES
        NHOMO 5         ! 输出5个最高占据轨道
        NLUMO 5         ! 输出5个最低未占据轨道
        WRITE_CUBE T
      &END MO_CUBES
      
      &E_DENSITY_CUBE
        STRIDE 2 2 2    ! 电子密度（可选）
      &END E_DENSITY_CUBE
    &END PRINT
  &END DFT
&END FORCE_EVAL
```

### 查看cube文件
```tcl
# 在VMD中加载cube文件
mol new HOMO.cube type cube waitfor all

# 添加等值面表示
mol representation Isosurface 0.02 0 0 0 1 1
mol color ColorID 0
mol material Transparent
mol addrep top

# 添加负值等值面（不同颜色）
mol representation Isosurface -0.02 0 0 0 1 1
mol color ColorID 1
mol addrep top
```

## 文件说明

| 文件 | 用途 |
|------|------|
| `render_c60_structure.tcl` | 批量渲染脚本 |
| `interactive_view.tcl` | 交互式查看脚本 |
| `view_orbital.tcl` | 轨道可视化脚本（需cube文件）|

## 颜色方案

| 元素 | 颜色 |
|------|------|
| C | 银灰色 |
| B | 品红色 |
| N | 蓝色 |
| P | 橙色 |
| Li | 绿色 |
| Na | 黄色 |
| K | 紫色 |

## 主文结构图（批量）

1. 从 CP2K 输入导出 XYZ（已修复路径为 `dft_results/`）：
   ```bash
   python3 dft_results/export_xyz_files.py
   ```

2. 一键渲染 scheme 图到 `paper/figures/final_figures/`：
   ```bash
   bash paper/figures/render_vmd_structures.sh
   ```
   输出：`scheme_tetramer_doping.png`（Pristine | B | N 并排）及单结构 PNG。

3. 交互式对比（Exp5 四聚体）：
   ```bash
   cd dft_results/exp_5_synergy && vmd -e vmd_compare.tcl
   ```

若 VMD 不在 PATH，脚本会尝试 `/Applications/VMD.app/...`；也可 `export PATH="/Applications/VMD.app/Contents/vmd:$PATH"`。

## VBM/CBM 补充图 (Figure S4 风格)

Exp.7 pristine @ ε=0% 已有 HOMO/LUMO cube：
- HOMO (VBM): `WFN_00240`
- LUMO (CBM): `WFN_00241`

一键渲染（VMD + matplotlib DOS）：

```bash
bash paper/figures/render_vbm_cbm_figure.sh
```

输出：`paper/figures/final_figures/figureS4_vbm_cbm_dos.pdf`

### macOS VMD 路径

若 `vmd` 不在 PATH，使用 App 内二进制并设置 `VMDDIR`：

```bash
export VMDDIR=/Applications/VMD.app/Contents/vmd2/lib
$VMDDIR/vmd_MACOSXARM64 -dispdev text -e dft_results/vmd_scripts/render_vbm_cbm.tcl -args ...
```

（旧版安装脚本可能硬编码错误路径；直接调用 `vmd_MACOSXARM64` 即可。）
