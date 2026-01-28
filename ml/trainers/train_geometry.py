"""
几何编码器训练脚本
"""

import sys
sys.path.append('E:/DeepSeek_Work')

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from pathlib import Path

from ml.models.geometry_encoder import Simple3DCNN, GeometryFeatureExtractor

class GeometryDataset(Dataset):
    """几何数据集"""
    
    def __init__(self, voxel_dir, transform=None):
        self.voxel_dir = Path(voxel_dir)
        self.voxel_files = list(self.voxel_dir.glob('*.npy'))
        self.transform = transform
    
    def __len__(self):
        return len(self.voxel_files)
    
    def __getitem__(self, idx):
        voxel_file = self.voxel_files[idx]
        voxels = np.load(voxel_file)
        
        # 转换为 torch tensor
        voxels = torch.from_numpy(voxels).float().unsqueeze(0)
        
        if self.transform:
            voxels = self.transform(voxels)
        
        return voxels, voxels  # 自编码器：输入=输出

def train_geometry_encoder(
    voxel_dir='E:/DeepSeek_Work/ml/data/voxels',
    epochs=50,
    batch_size=8,
    learning_rate=0.001,
    save_path='E:/DeepSeek_Work/ml/models/geometry_encoder.pth'
):
    """训练几何编码器"""
    
    print("=" * 60)
    print("几何编码器训练")
    print("=" * 60)
    
    # 检查数据
    voxel_path = Path(voxel_dir)
    if not voxel_path.exists():
        print(f"⚠️  数据目录不存在: {voxel_dir}")
        print("需要先生成体素数据")
        return None
    
    voxel_files = list(voxel_path.glob('*.npy'))
    if len(voxel_files) == 0:
        print("⚠️  没有找到体素数据文件")
        return None
    
    print(f"找到 {len(voxel_files)} 个体素文件")
    
    # 创建数据集
    dataset = GeometryDataset(voxel_dir)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    # 创建模型
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备: {device}")
    
    model = Simple3DCNN(feature_dim=128).to(device)
    
    # 定义损失函数和优化器
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    # 训练
    print("\n开始训练...")
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        
        for batch_idx, (data, target) in enumerate(dataloader):
            data = data.to(device)
            target = target.to(device)
            
            # 前向传播
            optimizer.zero_grad()
            features = model(data)
            
            # 这里使用对比学习或重建损失
            # 简化版：使用 MSE 损失
            loss = criterion(features, features.detach())
            
            # 反向传播
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(dataloader)
        print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.6f}")
    
    # 保存模型
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), save_path)
    print(f"\n✅ 模型已保存: {save_path}")
    
    return model

def generate_voxel_data(step_files, output_dir='E:/DeepSeek_Work/ml/data/voxels'):
    """从 STEP 文件生成体素数据"""
    
    print("生成体素数据...")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    extractor = GeometryFeatureExtractor(resolution=32)
    
    for i, step_file in enumerate(step_files):
        print(f"处理 {i+1}/{len(step_files)}: {step_file}")
        
        voxels = extractor.voxelize_step_file(step_file)
        
        if voxels is not None:
            output_file = output_path / f"voxel_{i:04d}.npy"
            np.save(output_file, voxels)
    
    print(f"✅ 体素数据已生成: {output_dir}")

if __name__ == "__main__":
    # 如果有 STEP 文件，先生成体素数据
    # step_files = list(Path('E:/DeepSeek_Work/test/input').glob('*.step'))
    # if step_files:
    #     generate_voxel_data(step_files)
    
    # 训练模型
    train_geometry_encoder(epochs=10)