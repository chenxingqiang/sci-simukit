#!/usr/bin/env python3
"""
Professional GNN Architecture Visualizer for Graphullerene Research
重新设计更清晰、更专业的GNN模型架构图

基于draw_convnet.py改编，专门用于绘制GNN模型架构图
"""

import os
import numpy as np
import matplotlib.pyplot as plt
plt.rcdefaults()
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Arrow
from matplotlib.patches import Polygon
import matplotlib.patches as mpatches

# PRL标准设置
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['font.size'] = 11

def draw_clean_gnn_architecture():
    """绘制清晰简洁的GNN架构图"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 定义颜色方案
    colors = {
        'input': '#E3F2FD',      # 浅蓝色
        'gat': '#E8F5E8',       # 浅绿色
        'pool': '#FFF3E0',      # 浅橙色
        'output': '#FCE4EC',    # 浅粉色
        'arrow': '#424242',     # 深灰色
        'text': '#212121'       # 深黑色
    }
    
    # 清除背景
    ax.set_facecolor('white')
    
    # 定义层的位置和尺寸
    layer_width = 80
    layer_height = 40
    layer_spacing = 100
    
    # 输入层
    input_x = 50
    input_y = 200
    
    # 绘制分子图（简化版）
    center = [input_x, input_y]
    radius = 15
    
    # 中心节点
    ax.add_patch(Circle(center, 4, facecolor='#1976D2', edgecolor='black', linewidth=1))
    
    # 周围节点
    angles = np.linspace(0, 2*np.pi, 6, endpoint=False)
    for angle in angles:
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)
        ax.add_patch(Circle([x, y], 3, facecolor='#1976D2', edgecolor='black', linewidth=1))
        # 连接线
        ax.plot([center[0], x], [center[1], y], 'k-', linewidth=1, alpha=0.6)
    
    # 输入层标签
    ax.text(input_x, input_y - 35, 'Input Graph\n(Molecular Structure)', 
            ha='center', va='center', fontsize=12, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.5", facecolor=colors['input'], edgecolor='black'))
    
    # GAT层1
    gat1_x = input_x + layer_spacing
    gat1_y = input_y
    
    # 绘制GAT层
    gat_rect = Rectangle((gat1_x - layer_width/2, gat1_y - layer_height/2), 
                        layer_width, layer_height, 
                        facecolor=colors['gat'], edgecolor='black', linewidth=2)
    ax.add_patch(gat_rect)
    
    # GAT层内部结构
    for i in range(3):
        x_pos = gat1_x - 20 + i * 20
        y_pos = gat1_y
        ax.add_patch(Circle([x_pos, y_pos], 6, facecolor='#4CAF50', edgecolor='black', linewidth=1))
    
    ax.text(gat1_x, gat1_y - 35, 'GAT Layer 1\n(128 neurons)', 
            ha='center', va='center', fontsize=12, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.5", facecolor=colors['gat'], edgecolor='black'))
    
    # GAT层2
    gat2_x = gat1_x + layer_spacing
    gat2_y = input_y
    
    gat_rect2 = Rectangle((gat2_x - layer_width/2, gat2_y - layer_height/2), 
                         layer_width, layer_height, 
                         facecolor=colors['gat'], edgecolor='black', linewidth=2)
    ax.add_patch(gat_rect2)
    
    for i in range(3):
        x_pos = gat2_x - 20 + i * 20
        y_pos = gat2_y
        ax.add_patch(Circle([x_pos, y_pos], 6, facecolor='#4CAF50', edgecolor='black', linewidth=1))
    
    ax.text(gat2_x, gat2_y - 35, 'GAT Layer 2\n(128 neurons)', 
            ha='center', va='center', fontsize=12, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.5", facecolor=colors['gat'], edgecolor='black'))
    
    # GAT层3
    gat3_x = gat2_x + layer_spacing
    gat3_y = input_y
    
    gat_rect3 = Rectangle((gat3_x - layer_width/2, gat3_y - layer_height/2), 
                         layer_width, layer_height, 
                         facecolor=colors['gat'], edgecolor='black', linewidth=2)
    ax.add_patch(gat_rect3)
    
    for i in range(3):
        x_pos = gat3_x - 20 + i * 20
        y_pos = gat3_y
        ax.add_patch(Circle([x_pos, y_pos], 6, facecolor='#4CAF50', edgecolor='black', linewidth=1))
    
    ax.text(gat3_x, gat3_y - 35, 'GAT Layer 3\n(128 neurons)', 
            ha='center', va='center', fontsize=12, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.5", facecolor=colors['gat'], edgecolor='black'))
    
    # 全局池化层
    pool_x = gat3_x + layer_spacing
    pool_y = input_y
    
    pool_rect = Rectangle((pool_x - layer_width/2, pool_y - layer_height/2), 
                         layer_width, layer_height, 
                         facecolor=colors['pool'], edgecolor='black', linewidth=2)
    ax.add_patch(pool_rect)
    
    # 池化层内部
    ax.add_patch(Circle([pool_x, pool_y], 8, facecolor='#FF9800', edgecolor='black', linewidth=1))
    
    ax.text(pool_x, pool_y - 35, 'Global Pooling\n(Mean Aggregation)', 
            ha='center', va='center', fontsize=12, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.5", facecolor=colors['pool'], edgecolor='black'))
    
    # 输出层
    output_x = pool_x + layer_spacing
    output_y = input_y
    
    output_rect = Rectangle((output_x - layer_width/2, output_y - layer_height/2), 
                          layer_width, layer_height, 
                          facecolor=colors['output'], edgecolor='black', linewidth=2)
    ax.add_patch(output_rect)
    
    # 输出层内部
    for i in range(3):
        x_pos = output_x - 20 + i * 20
        y_pos = output_y
        ax.add_patch(Circle([x_pos, y_pos], 5, facecolor='#E91E63', edgecolor='black', linewidth=1))
    
    ax.text(output_x, output_y - 35, 'Output Layer\n(Band Gap, Mobility, Formation Energy)', 
            ha='center', va='center', fontsize=12, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.5", facecolor=colors['output'], edgecolor='black'))
    
    # 添加连接箭头
    arrow_positions = [
        (input_x + 25, input_y, gat1_x - 25, gat1_y),
        (gat1_x + 25, gat1_y, gat2_x - 25, gat2_y),
        (gat2_x + 25, gat2_y, gat3_x - 25, gat3_y),
        (gat3_x + 25, gat3_y, pool_x - 25, pool_y),
        (pool_x + 25, pool_y, output_x - 25, output_y)
    ]
    
    for start_x, start_y, end_x, end_y in arrow_positions:
        ax.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y),
                   arrowprops=dict(arrowstyle='->', lw=3, color=colors['arrow']))
    
    # 添加特征说明（右侧）
    feature_x = 50
    feature_y = 100
    
    # 节点特征
    ax.text(feature_x, feature_y, 'Node Features:\n• Atomic type\n• Position\n• Local environment', 
            ha='center', va='center', fontsize=10,
            bbox=dict(boxstyle="round,pad=0.5", facecolor=colors['input'], edgecolor='black'))
    
    # 边特征
    ax.text(feature_x + 120, feature_y, 'Edge Features:\n• Bond type\n• Distance\n• Strain tensor', 
            ha='center', va='center', fontsize=10,
            bbox=dict(boxstyle="round,pad=0.5", facecolor=colors['gat'], edgecolor='black'))
    
    # 注意力机制
    ax.text(feature_x + 240, feature_y, 'Attention Mechanism:\n• α_ij = softmax(e_ij)\n• e_ij = LeakyReLU(a^T[Wh_i||Wh_j])', 
            ha='center', va='center', fontsize=10,
            bbox=dict(boxstyle="round,pad=0.5", facecolor=colors['pool'], edgecolor='black'))
    
    # 模型性能
    ax.text(feature_x + 360, feature_y, 'Model Performance:\n• R² = 0.975\n• MAE < 0.5 cm²V⁻¹s⁻¹\n• Training: 500+ DFT calculations', 
            ha='center', va='center', fontsize=10,
            bbox=dict(boxstyle="round,pad=0.5", facecolor=colors['output'], edgecolor='black'))
    
    # 添加注意力权重箭头
    ax.annotate('α_ij', xy=(gat1_x, gat1_y + 25), xytext=(feature_x + 240, feature_y + 30),
               arrowprops=dict(arrowstyle='->', lw=2, color='red'),
               fontsize=10, color='red', fontweight='bold')
    
    # 设置图形属性
    ax.set_xlim(0, 700)
    ax.set_ylim(0, 300)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # 添加总标题
    ax.text(350, 280, 'Graph Neural Network Architecture for Graphullerene Property Prediction', 
            fontsize=16, fontweight='bold', ha='center', va='center')
    
    plt.tight_layout()
    
    # 保存图片
    output_dir = "paper/figures/publication_quality"
    os.makedirs(output_dir, exist_ok=True)
    
    plt.savefig(os.path.join(output_dir, 'gnn_architecture_clean.pdf'),
                bbox_inches='tight', pad_inches=0.2, dpi=300)
    plt.savefig(os.path.join(output_dir, 'gnn_architecture_clean.png'),
                bbox_inches='tight', pad_inches=0.2, dpi=300)
    
    print("清洁版GNN架构图已保存至:", os.path.join(output_dir, 'gnn_architecture_clean.pdf'))
    
    plt.show()

def draw_minimal_gnn():
    """绘制最简化的GNN架构图"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 定义颜色
    colors = {
        'input': '#E3F2FD',
        'gat': '#E8F5E8', 
        'pool': '#FFF3E0',
        'output': '#FCE4EC',
        'arrow': '#424242'
    }
    
    # 清除背景
    ax.set_facecolor('white')
    
    # 定义位置
    y_center = 100
    layer_width = 60
    layer_height = 30
    spacing = 80
    
    positions = [
        (50, y_center, 'Input\nGraph'),
        (130, y_center, 'GAT\nLayer 1'),
        (210, y_center, 'GAT\nLayer 2'), 
        (290, y_center, 'GAT\nLayer 3'),
        (370, y_center, 'Global\nPooling'),
        (450, y_center, 'Output\nPrediction')
    ]
    
    layer_colors = [colors['input'], colors['gat'], colors['gat'], colors['gat'], colors['pool'], colors['output']]
    
    # 绘制各层
    for i, (x, y, label) in enumerate(positions):
        # 绘制层
        rect = Rectangle((x - layer_width/2, y - layer_height/2), 
                        layer_width, layer_height,
                        facecolor=layer_colors[i], edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        
        # 添加标签
        ax.text(x, y, label, ha='center', va='center', fontsize=11, fontweight='bold')
        
        # 添加连接箭头
        if i < len(positions) - 1:
            next_x = positions[i+1][0]
            ax.annotate('', xy=(next_x - layer_width/2, y), xytext=(x + layer_width/2, y),
                       arrowprops=dict(arrowstyle='->', lw=2, color=colors['arrow']))
    
    # 添加特征说明
    ax.text(50, 50, 'Node Features:\n• Atomic type\n• Position', 
            ha='center', va='center', fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", facecolor=colors['input'], edgecolor='black'))
    
    ax.text(200, 50, 'Edge Features:\n• Bond type\n• Distance', 
            ha='center', va='center', fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", facecolor=colors['gat'], edgecolor='black'))
    
    ax.text(350, 50, 'Model Performance:\n• R² = 0.975\n• MAE < 0.5', 
            ha='center', va='center', fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", facecolor=colors['output'], edgecolor='black'))
    
    # 设置图形属性
    ax.set_xlim(0, 500)
    ax.set_ylim(0, 150)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # 添加标题
    ax.text(250, 140, 'Graph Neural Network Architecture', 
            fontsize=14, fontweight='bold', ha='center', va='center')
    
    plt.tight_layout()
    
    # 保存图片
    output_dir = "paper/figures/publication_quality"
    os.makedirs(output_dir, exist_ok=True)
    
    plt.savefig(os.path.join(output_dir, 'gnn_architecture_minimal.pdf'),
                bbox_inches='tight', pad_inches=0.1, dpi=300)
    plt.savefig(os.path.join(output_dir, 'gnn_architecture_minimal.png'),
                bbox_inches='tight', pad_inches=0.1, dpi=300)
    
    print("简化版GNN架构图已保存至:", os.path.join(output_dir, 'gnn_architecture_minimal.pdf'))
    
    plt.show()

if __name__ == '__main__':
    print("生成清洁版GNN模型架构图...")
    print("1. 清洁版架构图")
    draw_clean_gnn_architecture()
    print("2. 最简化架构图")
    draw_minimal_gnn()
    print("完成！")
