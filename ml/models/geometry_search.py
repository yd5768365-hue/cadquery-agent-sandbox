# ml/models/geometry_search.py
"""
几何相似度搜索
使用 FAISS 向量库快速检索相似几何
"""

import faiss
import numpy as np
import json
from pathlib import Path

class GeometryVectorDatabase:
    """几何特征向量数据库"""
    
    def __init__(self, feature_dim=128, db_path="E:/DeepSeek_Work/ml/data/geometry_vectors.db"):
        self.feature_dim = feature_dim
        self.db_path = Path(db_path)
        
        # 创建 FAISS 索引
        self.index = faiss.IndexFlatL2(feature_dim)
        
        # 元数据
        self.metadata = []
        
        # 加载已有数据
        self._load_database()
    
    def add_geometry(self, feature_vector, metadata):
        """添加几何特征到数据库"""
        # 确保特征是正确的形状
        if feature_vector.shape[0] != self.feature_dim:
            raise ValueError(f"Feature dimension mismatch: expected {self.feature_dim}, got {feature_vector.shape[0]}")
        
        # 添加到 FAISS 索引
        feature_vector = feature_vector.reshape(1, -1).astype('float32')
        self.index.add(feature_vector)
        
        # 保存元数据
        self.metadata.append(metadata)
        
        # 保存数据库
        self._save_database()
    
    def search_similar(self, query_vector, k=5):
        """搜索相似几何"""
        if self.index.ntotal == 0:
            return []
        
        query_vector = query_vector.reshape(1, -1).astype('float32')
        
        # 搜索
        distances, indices = self.index.search(query_vector, min(k, self.index.ntotal))
        
        # 整理结果
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                results.append({
                    'metadata': self.metadata[idx],
                    'distance': float(distances[0][i]),
                    'similarity': 1.0 / (1.0 + float(distances[0][i]))
                })
        
        return results
    
    def _save_database(self):
        """保存数据库"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存 FAISS 索引
        faiss.write_index(self.index, str(self.db_path.with_suffix('.index')))
        
        # 保存元数据
        with open(self.db_path.with_suffix('.json'), 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    def _load_database(self):
        """加载数据库"""
        index_file = self.db_path.with_suffix('.index')
        metadata_file = self.db_path.with_suffix('.json')
        
        if index_file.exists():
            self.index = faiss.read_index(str(index_file))
        
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
    
    def get_statistics(self):
        """获取统计信息"""
        return {
            'total_geometries': self.index.ntotal,
            'feature_dimension': self.feature_dim,
            'metadata_count': len(self.metadata)
        }


# ml/trainers/train_geometry_encoder.py
"""
训练几何编码器（可选）
如果有大量几何数据，可以训练专门的编码器
"""

def train_geometry_encoder(data_dir, epochs=50, batch_size=8):
    """训练几何编码器"""
    
    import torch
    from torch.utils.data import Dataset, DataLoader
    from ml.models.geometry_encoder import Simple3DCNN, GeometryFeatureExtractor
    
    # 这里需要准备训练数据
    # 实际应用中，可以使用对比学习或自编码器训练
    
    print("几何编码器训练（简化版）")
    print("注意：完整训练需要大量几何数据和 GPU")
    
    model = Simple3DCNN(feature_dim=128)
    
    # 训练逻辑...
    
    print("训练完成（示例）")
    
    return model


# 使用示例
if __name__ == "__main__":
    # 创建特征提取器
    extractor = GeometryFeatureExtractor(resolution=32, feature_dim=128)
    
    # 提取特征
    step_file = "E:/DeepSeek_Work/test/input/bracket.step"
    features = extractor.extract_features(step_file)
    
    if features is not None:
        print(f"特征向量维度: {features.shape}")
        
        # 添加到数据库
        db = GeometryVectorDatabase()
        db.add_geometry(features, {
            'file': step_file,
            'name': 'bracket',
            'timestamp': '2024-01-27'
        })
        
        # 搜索相似几何
        similar = db.search_similar(features, k=5)
        print(f"找到 {len(similar)} 个相似几何")