"""
代理模型（Surrogate Model）
功能：快速预测仿真结果，避免重复计算
"""

import numpy as np
import pickle
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import joblib

class SurrogateModel:
    """仿真结果代理模型"""
    
    def __init__(self, model_type='random_forest'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = []
        self.target_names = []
        
    def prepare_data(self, simulation_data):
        """准备训练数据"""
        X = []
        y = []
        
        for record in simulation_data:
            # 解析几何参数
            params_str = record[2] if record[2] else ""
            params = {}
            if params_str:
                for item in params_str.split(','):
                    if ':' in item:
                        k, v = item.split(':')
                        params[k] = float(v)
            
            # 特征：网格参数 + 几何参数
            features = [
                record[3] if record[3] else 0,  # num_elements
                record[4] if record[4] else 0,  # clmax
                record[5] if record[5] else 0,  # clmin
            ]
            
            # 添加几何参数
            for key in sorted(params.keys()):
                features.append(params[key])
            
            # 目标：最大应力、平均应力、最大位移
            targets = [
                record[6] if record[6] else 0,  # max_stress
                record[7] if record[7] else 0,  # mean_stress
                record[8] if record[8] else 0,  # max_displacement
            ]
            
            if any(targets):  # 只使用有结果的数据
                X.append(features)
                y.append(targets)
        
        return np.array(X), np.array(y)
    
    def train(self, X, y, test_size=0.2, save_path=None):
        """训练代理模型"""
        print(f"训练代理模型...")
        print(f"  数据集大小: {len(X)} 样本")
        print(f"  特征维度: {X.shape[1]}")
        
        # 数据标准化
        X_scaled = self.scaler.fit_transform(X)
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=test_size, random_state=42
        )
        
        # 选择模型
        if self.model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=20,
                min_samples_split=5,
                n_jobs=-1,
                random_state=42
            )
        elif self.model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        
        # 训练
        print("  训练中...")
        self.model.fit(X_train, y_train)
        
        # 评估
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)
        
        train_r2 = r2_score(y_train, y_pred_train, multioutput='uniform_average')
        test_r2 = r2_score(y_test, y_pred_test, multioutput='uniform_average')
        
        train_mae = mean_absolute_error(y_train, y_pred_train, multioutput='uniform_average')
        test_mae = mean_absolute_error(y_test, y_pred_test, multioutput='uniform_average')
        
        print(f"\n  训练集 R²: {train_r2:.4f}, MAE: {train_mae:.2f}")
        print(f"  测试集 R²: {test_r2:.4f}, MAE: {test_mae:.2f}")
        
        self.is_trained = True
        
        # 保存模型
        if save_path:
            self.save(save_path)
        
        return {
            'train_r2': train_r2,
            'test_r2': test_r2,
            'train_mae': train_mae,
            'test_mae': test_mae
        }
    
    def predict(self, features, return_uncertainty=True):
        """预测结果"""
        if not self.is_trained:
            raise ValueError("模型未训练")
        
        # 标准化
        features = np.array(features).reshape(1, -1)
        features_scaled = self.scaler.transform(features)
        
        # 预测
        prediction = self.model.predict(features_scaled)[0]
        
        result = {
            'max_stress': float(prediction[0]),
            'mean_stress': float(prediction[1]),
            'max_displacement': float(prediction[2])
        }
        
        # 估算不确定性（仅 RandomForest）
        if return_uncertainty and self.model_type == 'random_forest':
            tree_predictions = np.array([
                tree.predict(features_scaled)[0]
                for tree in self.model.estimators_
            ])
            
            uncertainty = np.std(tree_predictions, axis=0)
            
            result['uncertainty'] = {
                'max_stress': float(uncertainty[0]),
                'mean_stress': float(uncertainty[1]),
                'max_displacement': float(uncertainty[2])
            }
            
            # 计算置信度（基于相对不确定性）
            rel_uncertainty = uncertainty / (np.abs(prediction) + 1e-6)
            confidence = 1.0 / (1.0 + np.mean(rel_uncertainty))
            result['confidence'] = float(confidence)
        else:
            result['confidence'] = 0.8  # 默认置信度
        
        return result
    
    def save(self, filepath):
        """保存模型"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'model_type': self.model_type,
            'feature_names': self.feature_names,
            'target_names': self.target_names,
            'is_trained': self.is_trained
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model_data, filepath)
        print(f"模型已保存: {filepath}")
    
    def load(self, filepath):
        """加载模型"""
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.model_type = model_data['model_type']
        self.feature_names = model_data.get('feature_names', [])
        self.target_names = model_data.get('target_names', [])
        self.is_trained = model_data['is_trained']
        
        print(f"模型已加载: {filepath}")
        return self