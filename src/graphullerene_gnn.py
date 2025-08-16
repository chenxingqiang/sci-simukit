#!/usr/bin/env python3
"""
富勒烯网络图神经网络预测模型
基于您的graphullerene项目，实现带隙和电子迁移率的预测

作者: 基于您的项目经验
版本: 1.0
"""

import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, GATConv, global_mean_pool, global_max_pool, global_add_pool
from torch_geometric.data import Data, DataLoader
from torch_geometric.transforms import Compose, NormalizeFeatures
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import logging
import json
from ase import Atoms
from ase.io import read
from ase.neighborlist import NeighborList
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split
import pickle

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GraphullereneGNN(torch.nn.Module):
    """
    富勒烯网络图神经网络模型
    预测带隙、电子迁移率和形成能
    """
    
    def __init__(self, 
                 num_node_features: int,
                 hidden_dim: int = 128,
                 num_layers: int = 4,
                 num_outputs: int = 3,  # band_gap, mobility, formation_energy
                 dropout: float = 0.1,
                 use_attention: bool = True):
        """
        初始化GNN模型
        
        Args:
            num_node_features: 节点特征维度
            hidden_dim: 隐藏层维度
            num_layers: GNN层数
            num_outputs: 输出维度
            dropout: Dropout率
            use_attention: 是否使用注意力机制
        """
        super(GraphullereneGNN, self).__init__()
        
        self.num_layers = num_layers
        self.hidden_dim = hidden_dim
        self.dropout = dropout
        self.use_attention = use_attention
        
        # 输入投影层
        self.input_proj = torch.nn.Linear(num_node_features, hidden_dim)
        
        # GNN层
        self.convs = torch.nn.ModuleList()
        self.batch_norms = torch.nn.ModuleList()
        
        for i in range(num_layers):
            if use_attention:
                conv = GATConv(hidden_dim, hidden_dim // 8, heads=8, dropout=dropout)
            else:
                conv = GCNConv(hidden_dim, hidden_dim)
            
            self.convs.append(conv)
            self.batch_norms.append(torch.nn.BatchNorm1d(hidden_dim))
        
        # 全局池化
        self.global_pool = global_mean_pool
        
        # 输出头
        self.output_heads = torch.nn.ModuleList([
            torch.nn.Sequential(
                torch.nn.Linear(hidden_dim, hidden_dim // 2),
                torch.nn.ReLU(),
                torch.nn.Dropout(dropout),
                torch.nn.Linear(hidden_dim // 2, 1)
            ) for _ in range(num_outputs)
        ])
        
        # 输出标签
        self.output_labels = ['band_gap', 'electron_mobility', 'formation_energy']
    
    def forward(self, data):
        """前向传播"""
        x, edge_index, batch = data.x, data.edge_index, data.batch
        
        # 输入投影
        x = F.relu(self.input_proj(x))
        
        # GNN层
        for i, (conv, bn) in enumerate(zip(self.convs, self.batch_norms)):
            x = conv(x, edge_index)
            x = bn(x)
            x = F.relu(x)
            x = F.dropout(x, p=self.dropout, training=self.training)
        
        # 全局池化
        x = self.global_pool(x, batch)
        
        # 多任务输出
        outputs = []
        for head in self.output_heads:
            outputs.append(head(x))
        
        return torch.cat(outputs, dim=1)

class GraphullereneDataProcessor:
    """
    富勒烯数据处理器
    将ASE结构转换为PyG图数据
    """
    
    def __init__(self, cutoff_radius: float = 2.0):
        """
        初始化数据处理器
        
        Args:
            cutoff_radius: 邻居原子截断半径
        """
        self.cutoff_radius = cutoff_radius
        
        # 原子特征映射
        self.atom_features = {
            'C': [6, 4, 2.55, 77],      # 原子序数, 价电子数, 电负性, 原子半径
            'B': [5, 3, 2.04, 88],
            'N': [7, 5, 3.04, 71],
            'P': [15, 5, 2.19, 107]
        }
    
    def atoms_to_graph(self, atoms: Atoms, metadata: Dict = None) -> Data:
        """
        将ASE原子结构转换为PyG图数据
        
        Args:
            atoms: ASE原子结构
            metadata: 结构元数据（应变、掺杂信息等）
            
        Returns:
            PyG图数据对象
        """
        # 构建邻居列表
        nl = NeighborList([self.cutoff_radius/2] * len(atoms), 
                         self_interaction=False, bothways=True)
        nl.update(atoms)
        
        # 边索引
        edge_indices = []
        for i in range(len(atoms)):
            neighbors, _ = nl.get_neighbors(i)
            for j in neighbors:
                edge_indices.append([i, j])
        
        edge_index = torch.tensor(edge_indices, dtype=torch.long).t().contiguous()
        
        # 节点特征
        node_features = []
        for atom in atoms:
            symbol = atom.symbol
            if symbol in self.atom_features:
                features = self.atom_features[symbol].copy()
            else:
                # 未知原子类型，使用碳的特征
                features = self.atom_features['C'].copy()
            
            node_features.append(features)
        
        # 添加结构级特征（如果有元数据）
        if metadata:
            # 应变信息
            strain_value = metadata.get('strain_value', 0.0)
            
            # 掺杂信息
            doping_info = self._encode_doping_info(metadata)
            
            # 将结构级特征添加到每个节点
            for i in range(len(node_features)):
                node_features[i].extend([strain_value] + doping_info)
        
        x = torch.tensor(node_features, dtype=torch.float)
        
        # 创建图数据
        data = Data(x=x, edge_index=edge_index)
        
        return data
    
    def _encode_doping_info(self, metadata: Dict) -> List[float]:
        """
        编码掺杂信息
        
        Args:
            metadata: 结构元数据
            
        Returns:
            掺杂信息编码
        """
        # 初始化掺杂浓度向量 [B_conc, N_conc, P_conc]
        doping_concs = [0.0, 0.0, 0.0]
        dopant_map = {'B': 0, 'N': 1, 'P': 2}
        
        doping_type = metadata.get('doping_type', 'pristine')
        
        if doping_type == 'single':
            dopant = metadata.get('dopant')
            concentration = metadata.get('concentration', 0.0)
            if dopant in dopant_map:
                doping_concs[dopant_map[dopant]] = concentration
                
        elif doping_type == 'mixed':
            dopants = metadata.get('dopants', {})
            for dopant, conc in dopants.items():
                if dopant in dopant_map:
                    doping_concs[dopant_map[dopant]] = conc
        
        return doping_concs
    
    def process_dataset(self, 
                       structure_dir: Path,
                       metadata_file: Path = None) -> List[Data]:
        """
        处理整个数据集
        
        Args:
            structure_dir: 结构文件目录
            metadata_file: 元数据文件
            
        Returns:
            图数据列表
        """
        logger.info("开始处理数据集...")
        
        # 加载元数据
        metadata = {}
        if metadata_file and metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        
        # 处理所有xyz文件
        graph_data_list = []
        xyz_files = list(structure_dir.rglob("*.xyz"))
        
        logger.info(f"找到 {len(xyz_files)} 个结构文件")
        
        for xyz_file in xyz_files:
            try:
                # 读取结构
                atoms = read(str(xyz_file))
                
                # 获取对应元数据
                file_metadata = metadata.get(str(xyz_file), {})
                
                # 转换为图数据
                graph_data = self.atoms_to_graph(atoms, file_metadata)
                
                # 添加文件路径标识
                graph_data.file_path = str(xyz_file)
                
                graph_data_list.append(graph_data)
                
            except Exception as e:
                logger.warning(f"处理文件 {xyz_file} 时出错: {e}")
                continue
        
        logger.info(f"成功处理 {len(graph_data_list)} 个结构")
        return graph_data_list

class GraphullereneTrainer:
    """
    富勒烯GNN模型训练器
    """
    
    def __init__(self, 
                 model: GraphullereneGNN,
                 device: str = 'cpu'):
        """
        初始化训练器
        
        Args:
            model: GNN模型
            device: 计算设备
        """
        self.model = model.to(device)
        self.device = device
        self.train_losses = []
        self.val_losses = []
        self.best_val_loss = float('inf')
        
    def train_epoch(self, dataloader: DataLoader, optimizer, criterion):
        """训练一个epoch"""
        self.model.train()
        total_loss = 0
        
        for batch in dataloader:
            batch = batch.to(self.device)
            optimizer.zero_grad()
            
            # 前向传播
            pred = self.model(batch)
            
            # 计算损失（多任务学习）
            if hasattr(batch, 'y') and batch.y is not None:
                loss = criterion(pred, batch.y)
            else:
                # 如果没有标签，跳过这个batch
                continue
            
            # 反向传播
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        return total_loss / len(dataloader)
    
    def evaluate(self, dataloader: DataLoader, criterion):
        """评估模型"""
        self.model.eval()
        total_loss = 0
        predictions = []
        targets = []
        
        with torch.no_grad():
            for batch in dataloader:
                batch = batch.to(self.device)
                pred = self.model(batch)
                
                if hasattr(batch, 'y') and batch.y is not None:
                    loss = criterion(pred, batch.y)
                    total_loss += loss.item()
                    
                    predictions.append(pred.cpu().numpy())
                    targets.append(batch.y.cpu().numpy())
        
        avg_loss = total_loss / len(dataloader) if len(dataloader) > 0 else 0
        
        if predictions:
            predictions = np.vstack(predictions)
            targets = np.vstack(targets)
            
            # 计算R²分数
            r2_scores = []
            for i in range(predictions.shape[1]):
                r2 = r2_score(targets[:, i], predictions[:, i])
                r2_scores.append(r2)
            
            return avg_loss, predictions, targets, r2_scores
        
        return avg_loss, None, None, None
    
    def train(self, 
             train_loader: DataLoader,
             val_loader: DataLoader = None,
             num_epochs: int = 100,
             learning_rate: float = 0.001,
             save_path: Path = None):
        """
        训练模型
        
        Args:
            train_loader: 训练数据加载器
            val_loader: 验证数据加载器
            num_epochs: 训练轮数
            learning_rate: 学习率
            save_path: 模型保存路径
        """
        
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        criterion = torch.nn.MSELoss()
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.8, patience=10
        )
        
        logger.info("开始训练...")
        
        for epoch in range(num_epochs):
            # 训练
            train_loss = self.train_epoch(train_loader, optimizer, criterion)
            self.train_losses.append(train_loss)
            
            # 验证
            if val_loader:
                val_loss, _, _, r2_scores = self.evaluate(val_loader, criterion)
                self.val_losses.append(val_loss)
                scheduler.step(val_loss)
                
                # 保存最佳模型
                if val_loss < self.best_val_loss:
                    self.best_val_loss = val_loss
                    if save_path:
                        torch.save(self.model.state_dict(), save_path)
                
                if epoch % 10 == 0:
                    logger.info(f"Epoch {epoch:3d}: Train Loss = {train_loss:.4f}, "
                              f"Val Loss = {val_loss:.4f}")
                    if r2_scores:
                        logger.info(f"R² scores: {[f'{r2:.3f}' for r2 in r2_scores]}")
            else:
                if epoch % 10 == 0:
                    logger.info(f"Epoch {epoch:3d}: Train Loss = {train_loss:.4f}")
        
        logger.info("训练完成！")
    
    def plot_training_history(self, save_path: Path = None):
        """绘制训练历史"""
        plt.figure(figsize=(10, 6))
        
        plt.subplot(1, 2, 1)
        plt.plot(self.train_losses, label='Training Loss')
        if self.val_losses:
            plt.plot(self.val_losses, label='Validation Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.title('Training History')
        
        if save_path:
            plt.savefig(save_path)
        plt.show()

def create_demo_training_data():
    """
    创建演示训练数据
    在没有DFT计算结果时，用于测试GNN模型
    """
    logger.info("创建演示训练数据...")
    
    # 生成模拟的性质数据
    np.random.seed(42)
    n_samples = 100
    
    demo_data = []
    
    for i in range(n_samples):
        # 模拟的结构参数
        strain = np.random.uniform(-5, 5)
        b_conc = np.random.uniform(0, 10)
        n_conc = np.random.uniform(0, 10)
        p_conc = np.random.uniform(0, 10)
        
        # 模拟的性质（基于简单的关系）
        band_gap = 1.8 + 0.1 * strain + 0.05 * b_conc - 0.03 * n_conc + np.random.normal(0, 0.1)
        mobility = 8.7 * (1 + 0.2 * strain) * (1 + 0.1 * (b_conc + n_conc)) + np.random.normal(0, 0.5)
        formation_energy = 0.5 + 0.02 * (b_conc + n_conc + p_conc) + np.random.normal(0, 0.05)
        
        demo_data.append({
            'strain': strain,
            'b_conc': b_conc,
            'n_conc': n_conc,
            'p_conc': p_conc,
            'band_gap': band_gap,
            'mobility': mobility,
            'formation_energy': formation_energy
        })
    
    return pd.DataFrame(demo_data)

def main():
    """主函数 - 演示GNN模型训练"""
    logger.info("富勒烯GNN模型演示")
    
    # 创建演示数据
    demo_data = create_demo_training_data()
    logger.info(f"演示数据集大小: {len(demo_data)}")
    
    # 创建简单的图数据用于测试
    # 注意：这里使用简化的图结构，实际应用中需要从xyz文件构建
    graph_data_list = []
    
    for idx, row in demo_data.iterrows():
        # 创建简化的图（10个节点的完全图）
        num_nodes = 10
        x = torch.randn(num_nodes, 7)  # 7维节点特征
        
        # 添加结构级特征
        x[:, -4:] = torch.tensor([row['strain'], row['b_conc'], 
                                 row['n_conc'], row['p_conc']])
        
        # 创建边（完全图）
        edge_index = torch.combinations(torch.arange(num_nodes), 2).t()
        edge_index = torch.cat([edge_index, edge_index.flip(0)], dim=1)
        
        # 目标值 - 确保是2D张量 [1, 3]
        y = torch.tensor([row['band_gap'], row['mobility'], 
                         row['formation_energy']], dtype=torch.float).unsqueeze(0)
        
        data = Data(x=x, edge_index=edge_index, y=y)
        graph_data_list.append(data)
    
    # 分割数据集
    train_data, test_data = train_test_split(graph_data_list, test_size=0.2, random_state=42)
    train_data, val_data = train_test_split(train_data, test_size=0.2, random_state=42)
    
    # 创建数据加载器
    train_loader = DataLoader(train_data, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_data, batch_size=16, shuffle=False)
    test_loader = DataLoader(test_data, batch_size=16, shuffle=False)
    
    # 创建模型
    model = GraphullereneGNN(
        num_node_features=7,
        hidden_dim=64,
        num_layers=3,
        num_outputs=3,
        dropout=0.1,
        use_attention=True
    )
    
    logger.info(f"模型参数数量: {sum(p.numel() for p in model.parameters())}")
    
    # 创建训练器
    trainer = GraphullereneTrainer(model)
    
    # 训练模型
    save_path = Path("best_graphullerene_gnn.pth")
    trainer.train(
        train_loader=train_loader,
        val_loader=val_loader,
        num_epochs=50,
        learning_rate=0.001,
        save_path=save_path
    )
    
    # 测试模型
    logger.info("评估测试集...")
    test_loss, predictions, targets, r2_scores = trainer.evaluate(test_loader, torch.nn.MSELoss())
    
    if r2_scores:
        logger.info(f"测试集 R² 分数:")
        for i, (label, r2) in enumerate(zip(model.output_labels, r2_scores)):
            logger.info(f"  {label}: {r2:.3f}")
    
    # 绘制训练历史
    trainer.plot_training_history(save_path=Path("training_history.png"))
    
    logger.info("GNN模型演示完成！")

if __name__ == "__main__":
    main()
