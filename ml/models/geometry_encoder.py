"""
几何特征提取器
使用 3D CNN 或 PointNet 提取几何特征向量
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

class Simple3DCNN(nn.Module):
    """简单的 3D CNN 几何编码器"""
    
    def __init__(self, input_shape=(64, 64, 64), feature_dim=128):
        super(Simple3DCNN, self).__init__()
        
        self.conv1 = nn.Conv3d(1, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm3d(32)
        self.pool1 = nn.MaxPool3d(2)
        
        self.conv2 = nn.Conv3d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm3d(64)
        self.pool2 = nn.MaxPool3d(2)
        
        self.conv3 = nn.Conv3d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm3d(128)
        self.pool3 = nn.MaxPool3d(2)
        
        # 计算展平后的维度
        final_size = input_shape[0] // 8
        self.flatten_dim = 128 * (final_size ** 3)
        
        self.fc1 = nn.Linear(self.flatten_dim, 512)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(512, feature_dim)
    
    def forward(self, x):
        # x shape: (batch, 1, D, H, W)
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.pool1(x)
        
        x = F.relu(self.bn2(self.conv2(x)))
        x = self.pool2(x)
        
        x = F.relu(self.bn3(self.conv3(x)))
        x = self.pool3(x)
        
        x = x.view(x.size(0), -1)
        
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        
        return F.normalize(x, p=2, dim=1)  # L2 归一化


class GeometryFeatureExtractor:
    """几何特征提取器"""
    
    def __init__(self, model_path=None, resolution=64, feature_dim=128):
        self.resolution = resolution
        self.feature_dim = feature_dim
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 创建模型
        self.model = Simple3DCNN(
            input_shape=(resolution, resolution, resolution),
            feature_dim=feature_dim
        ).to(self.device)
        
        if model_path:
            self.load_model(model_path)
    
    def voxelize_step_file(self, step_file, resolution=None):
        """将 STEP 文件转换为体素网格"""
        resolution = resolution or self.resolution
        
        try:
            import cadquery as cq
            
            # 加载几何
            shape = cq.importers.importStep(step_file)
            
            # 获取包围盒
            bb = shape.val().BoundingBox()
            
            # 创建体素网格
            x_min, x_max = bb.xmin, bb.xmax
            y_min, y_max = bb.ymin, bb.ymax
            z_min, z_max = bb.zmin, bb.zmax
            
            # 计算体素大小
            x_size = (x_max - x_min) / resolution
            y_size = (y_max - y_min) / resolution
            z_size = (z_max - z_min) / resolution
            
            # 初始化体素网格
            voxels = np.zeros((resolution, resolution, resolution), dtype=np.float32)
            
            # 填充体素（简化版：采样点检测）
            for i in range(resolution):
                for j in range(resolution):
                    for k in range(resolution):
                        x = x_min + (i + 0.5) * x_size
                        y = y_min + (j + 0.5) * y_size
                        z = z_min + (k + 0.5) * z_size
                        
                        point = cq.Vector(x, y, z)
                        
                        # 检查点是否在几何内部
                        # 这里使用简化方法，实际应用需要更精确的算法
                        try:
                            is_inside = shape.val().isInside(point, tolerance=max(x_size, y_size, z_size))
                            voxels[i, j, k] = 1.0 if is_inside else 0.0
                        except:
                            voxels[i, j, k] = 0.0
            
            return voxels
        
        except Exception as e:
            print(f"体素化失败: {e}")
            return None
    
    def extract_features(self, step_file):
        """提取几何特征向量"""
        # 体素化
        voxels = self.voxelize_step_file(step_file)
        
        if voxels is None:
            return None
        
        # 转换为 PyTorch 张量
        voxels_tensor = torch.from_numpy(voxels).unsqueeze(0).unsqueeze(0).to(self.device)
        
        # 提取特征
        self.model.eval()
        with torch.no_grad():
            features = self.model(voxels_tensor)
        
        return features.cpu().numpy()[0]
    
    def save_model(self, filepath):
        """保存模型"""
        torch.save(self.model.state_dict(), filepath)
        print(f"模型已保存: {filepath}")
    
    def load_model(self, filepath):
        """加载模型"""
        self.model.load_state_dict(torch.load(filepath, map_location=self.device))
        self.model.eval()
        print(f"模型已加载: {filepath}")


