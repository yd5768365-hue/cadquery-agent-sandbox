"""
回归模型基础类
提供统一的模型接口
"""

import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.preprocessing import StandardScaler
import joblib

class BaseRegressionModel:
    """回归模型基类"""
    
    def __init__(self, model_type='random_forest', **kwargs):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.is_fitted = False
        self._create_model(**kwargs)
    
    def _create_model(self, **kwargs):
        """创建模型实例"""
        if self.model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', 20),
                min_samples_split=kwargs.get('min_samples_split', 5),
                n_jobs=-1,
                random_state=42
            )
        elif self.model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', 5),
                learning_rate=kwargs.get('learning_rate', 0.1),
                random_state=42
            )
        elif self.model_type == 'ridge':
            self.model = Ridge(
                alpha=kwargs.get('alpha', 1.0)
            )
        elif self.model_type == 'lasso':
            self.model = Lasso(
                alpha=kwargs.get('alpha', 1.0)
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def fit(self, X, y):
        """训练模型"""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_fitted = True
        return self
    
    def predict(self, X):
        """预测"""
        if not self.is_fitted:
            raise ValueError("Model not fitted yet")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def score(self, X, y):
        """评估模型"""
        X_scaled = self.scaler.transform(X)
        return self.model.score(X_scaled, y)
    
    def save(self, filepath):
        """保存模型"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'model_type': self.model_type,
            'is_fitted': self.is_fitted
        }, filepath)
    
    def load(self, filepath):
        """加载模型"""
        data = joblib.load(filepath)
        self.model = data['model']
        self.scaler = data['scaler']
        self.model_type = data['model_type']
        self.is_fitted = data['is_fitted']
        return self


class MultiOutputRegressionModel(BaseRegressionModel):
    """多输出回归模型"""
    
    def __init__(self, model_type='random_forest', n_outputs=3, **kwargs):
        self.n_outputs = n_outputs
        super().__init__(model_type, **kwargs)
    
    def predict(self, X):
        """预测多个输出"""
        predictions = super().predict(X)
        
        # 如果是单样本，确保返回正确的形状
        if len(predictions.shape) == 1:
            predictions = predictions.reshape(1, -1)
        
        return predictions
    
    def get_feature_importance(self):
        """获取特征重要性"""
        if hasattr(self.model, 'feature_importances_'):
            return self.model.feature_importances_
        return None

