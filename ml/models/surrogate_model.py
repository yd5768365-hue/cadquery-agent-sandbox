"""
代理模型（Surrogate Model）
用于快速预测CAE仿真结果
"""

import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SurrogateModel:
    """代理模型类"""
    
    def __init__(self, model_type='random_forest', model_path=None):
        self.model_type = model_type
        self.model = None
        self.scaler = None
        self.is_loaded = False
        
        if model_path:
            self.load(model_path)
    
    def load(self, model_path):
        """加载模型"""
        try:
            data = joblib.load(model_path)
            self.model = data.get('model')
            self.scaler = data.get('scaler')
            self.is_loaded = True
            logger.info(f"模型加载成功: {model_path}")
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            self.is_loaded = False
    
    def save(self, model_path):
        """保存模型"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'model_type': self.model_type
        }, model_path)
        logger.info(f"模型保存成功: {model_path}")
    
    def train(self, X, y, test_size=0.2, save_path=None):
        """训练模型"""
        # 数据分割
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # 特征标准化
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # 创建模型
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            n_jobs=-1,
            random_state=42
        )
        
        # 训练
        self.model.fit(X_train_scaled, y_train)
        
        # 评估
        y_train_pred = self.model.predict(X_train_scaled)
        y_test_pred = self.model.predict(X_test_scaled)
        
        metrics = {
            'train_r2': r2_score(y_train, y_train_pred),
            'test_r2': r2_score(y_test, y_test_pred),
            'train_mae': mean_absolute_error(y_train, y_train_pred),
            'test_mae': mean_absolute_error(y_test, y_test_pred),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_test_pred))
        }
        
        # 保存模型
        if save_path:
            self.save(save_path)
        
        return metrics
    
    def prepare_data(self, data):
        """准备训练数据"""
        X = []
        y = []
        
        for record in data:
            # 特征提取
            features = [
                record[3] or 50000,  # 网格单元数
                5.0,  # clmax (默认值)
                0.5,  # clmin (默认值)
                100,  # 材料弹性模量
                0.3,  # 泊松比
                record[5] if record[5] else 1.0  # 载荷
            ]
            X.append(features)
            
            # 目标值（应力）
            if record[6]:  # max_stress
                y.append([record[6], record[7] if record[7] else 0, record[8] if record[8] else 0])
        
        return np.array(X), np.array(y)
    
    def predict(self, features, return_uncertainty=False):
        """预测"""
        if not self.is_loaded:
            return {
                'max_stress': 0.0,
                'mean_stress': 0.0,
                'max_displacement': 0.0,
                'confidence': 0.0
            }
        
        # 确保特征是二维数组
        if len(features) == 6:
            features = np.array([features])
        else:
            features = np.array(features)
        
        # 特征标准化
        features_scaled = self.scaler.transform(features)
        
        # 预测
        prediction = self.model.predict(features_scaled)[0]
        
        # 计算置信度（基于树的数量和方差）
        if hasattr(self.model, 'estimators_'):
            predictions = np.array([tree.predict(features_scaled)[0] for tree in self.model.estimators_])
            std = np.std(predictions)
            confidence = min(1.0, max(0.0, 1.0 - std / (np.mean(predictions) + 1e-6)))
        else:
            confidence = 0.8  # 默认置信度
        
        result = {
            'max_stress': float(prediction[0]),
            'mean_stress': float(prediction[1]),
            'max_displacement': float(prediction[2]),
            'confidence': float(confidence)
        }
        
        if return_uncertainty:
            result['std'] = float(std) if 'std' in locals() else 0.0
        
        return result
    
    def get_feature_importance(self):
        """获取特征重要性"""
        if self.is_loaded and hasattr(self.model, 'feature_importances_'):
            return self.model.feature_importances_
        return None
