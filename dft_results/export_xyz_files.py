#!/usr/bin/env python3
"""
从CP2K输入文件中提取坐标并导出为XYZ格式
"""

import re
from pathlib import Path


def extract_coords_from_inp(inp_file: Path) -> list:
    """从CP2K inp文件中提取原子坐标"""
    coords = []
    in_coord_block = False
    
    with open(inp_file, 'r') as f:
        for line in f:
            line = line.strip()
            if '&COORD' in line:
                in_coord_block = True
                continue
            if '&END COORD' in line:
                in_coord_block = False
                continue
            if in_coord_block and line:
                parts = line.split()
                if len(parts) >= 4:
                    element = parts[0]
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    coords.append((element, x, y, z))
    
    return coords


def write_xyz(coords: list, xyz_file: Path, comment: str = ""):
    """将坐标写入XYZ文件"""
    with open(xyz_file, 'w') as f:
        f.write(f"{len(coords)}\n")
        f.write(f"{comment}\n")
        for elem, x, y, z in coords:
            f.write(f"{elem:2s}  {x:12.6f}  {y:12.6f}  {z:12.6f}\n")


def extract_coords_from_out(out_file: Path) -> list:
    """从CP2K out文件中提取原子坐标"""
    coords = []
    in_coord_block = False
    
    with open(out_file, 'r') as f:
        for line in f:
            # 查找 ATOMIC COORDINATES 部分
            if 'ATOMIC COORDINATES IN ANGSTROM' in line:
                in_coord_block = True
                continue
            if in_coord_block:
                line = line.strip()
                if not line or line.startswith('---'):
                    continue
                if 'Atom' in line and 'Kind' in line:
                    continue
                if line.startswith('TOTAL') or line.startswith('QS'):
                    break
                parts = line.split()
                if len(parts) >= 5:
                    try:
                        element = parts[1]
                        x, y, z = float(parts[4]), float(parts[5]), float(parts[6])
                        coords.append((element, x, y, z))
                    except (ValueError, IndexError):
                        continue
    
    return coords


def process_experiment(exp_dir: Path):
    """处理一个实验目录"""
    xyz_dir = exp_dir / "xyz_structures"
    xyz_dir.mkdir(exist_ok=True)
    count = 0
    
    # 尝试多个可能的位置查找inp文件
    inp_files = []
    for search_dir in [exp_dir / "outputs", exp_dir]:
        if search_dir.exists():
            inp_files.extend(list(search_dir.glob("*.inp")))
    
    # 从inp文件提取
    for inp_file in inp_files:
        coords = extract_coords_from_inp(inp_file)
        if coords:
            xyz_file = xyz_dir / f"{inp_file.stem}.xyz"
            comment = f"Extracted from {inp_file.name}, {len(coords)} atoms"
            write_xyz(coords, xyz_file, comment)
            count += 1
    
    # 如果没有inp文件，尝试从out文件提取
    if count == 0:
        out_files = []
        for search_dir in [exp_dir / "outputs", exp_dir]:
            if search_dir.exists():
                out_files.extend(list(search_dir.glob("*.out")))
        
        for out_file in out_files:
            coords = extract_coords_from_out(out_file)
            if coords:
                xyz_file = xyz_dir / f"{out_file.stem}.xyz"
                comment = f"Extracted from {out_file.name}, {len(coords)} atoms"
                write_xyz(coords, xyz_file, comment)
                count += 1
    
    if count > 0:
        print(f"  ✓ {exp_dir.name}: 导出 {count} 个xyz文件到 xyz_structures/")
    else:
        print(f"  跳过: {exp_dir.name} (无可用坐标文件)")
    
    return count


def main():
    base_dir = Path("/Users/xingqiangchen/sci-simukit/dft_results_download")
    
    print("=" * 60)
    print("导出实验体系XYZ坐标文件")
    print("=" * 60)
    
    experiments = [
        "exp_1_structure",
        "exp_2_doping", 
        "exp_3_electronic",
        "exp_4_polaron",
        "exp_5_synergy",
        "exp_6_optimal"
    ]
    
    total = 0
    for exp_name in experiments:
        exp_dir = base_dir / exp_name
        if exp_dir.exists():
            total += process_experiment(exp_dir)
    
    print("\n" + "=" * 60)
    print(f"总计导出 {total} 个XYZ文件")
    print("=" * 60)


if __name__ == "__main__":
    main()

