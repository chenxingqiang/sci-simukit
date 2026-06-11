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

