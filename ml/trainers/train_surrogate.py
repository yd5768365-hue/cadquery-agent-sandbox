"""
代理模型训练脚本
"""

import sys
sys.path.append('E:/DeepSeek_Work')

from server.data_collector import SimulationDataCollector
from ml.models.surrogate_model import SurrogateModel

def train_surrogate_model(analysis_type='stress', min_samples=50):
    """训练代理模型"""
    
    print("=" * 60)
    print("代理模型训练")
    print("=" * 60)
    
    # 加载数据
    collector = SimulationDataCollector()
    data = collector.get_training_data(analysis_type=analysis_type)
    
    print(f"\n加载数据: {len(data)} 条记录")
    
    if len(data) < min_samples:
        print(f"⚠️  数据不足！需要至少 {min_samples} 条记录，当前只有 {len(data)} 条")
        print(f"   建议：继续运行仿真积累数据")
        return None
    
    # 创建模型
    model = SurrogateModel(model_type='random_forest')
    
    # 准备数据
    X, y = model.prepare_data(data)
    
    print(f"\n特征矩阵: {X.shape}")
    print(f"目标矩阵: {y.shape}")
    
    # 训练
    metrics = model.train(
        X, y,
        test_size=0.2,
        save_path=f'E:/DeepSeek_Work/ml/models/surrogate_{analysis_type}.pkl'
    )
    
    print("\n✅ 训练完成！")
    print(f"   模型准确度 R²: {metrics['test_r2']:.4f}")
    print(f"   平均绝对误差: {metrics['test_mae']:.2f} MPa")
    
    if metrics['test_r2'] > 0.85:
        print(f"   评价: 优秀！可以用于快速预测")
    elif metrics['test_r2'] > 0.70:
        print(f"   评价: 良好，建议继续积累数据提升精度")
    else:
        print(f"   评价: 精度不足，需要更多训练数据")
    
    return model

if __name__ == "__main__":
    train_surrogate_model()


# ml/models/prediction_engine.py
"""
预测引擎 - 智能决策是否需要完整仿真
"""

class PredictionEngine:
    """智能预测引擎"""
    
    def __init__(self, surrogate_model_path=None, confidence_threshold=0.8):
        self.surrogate_model = None
        self.confidence_threshold = confidence_threshold
        
        if surrogate_model_path:
            self.load_model(surrogate_model_path)
    
    def load_model(self, model_path):
        """加载代理模型"""
        from ml.models.surrogate_model import SurrogateModel
        self.surrogate_model = SurrogateModel()
        self.surrogate_model.load(model_path)
    
    def predict_or_simulate(self, features, force_simulate=False):
        """智能决策：预测还是仿真"""
        
        # 如果没有模型或强制仿真
        if not self.surrogate_model or force_simulate:
            return {
                'method': 'full_simulation',
                'reason': 'No model available or forced simulation',
                'should_simulate': True
            }
        
        # 使用代理模型预测
        prediction = self.surrogate_model.predict(features, return_uncertainty=True)
        
        confidence = prediction.get('confidence', 0)
        
        # 决策逻辑
        if confidence >= self.confidence_threshold:
            return {
                'method': 'surrogate_prediction',
                'prediction': prediction,
                'confidence': confidence,
                'should_simulate': False,
                'reason': f'High confidence ({confidence:.2%}), using surrogate model'
            }
        else:
            return {
                'method': 'full_simulation',
                'prediction': prediction,  # 仍提供预测作为参考
                'confidence': confidence,
                'should_simulate': True,
                'reason': f'Low confidence ({confidence:.2%}), running full simulation'
            }
    
    def get_recommendation(self, prediction_result):
        """基于预测结果给出工程建议"""
        if prediction_result['method'] == 'surrogate_prediction':
            pred = prediction_result['prediction']
            max_stress = pred['max_stress']
            
            # 简单的安全性判断
            if max_stress > 400:
                return "⚠️  预测应力较高，建议降低载荷或增加厚度"
            elif max_stress > 250:
                return "✓ 应力水平合理，可以进行详细仿真验证"
            else:
                return "✓ 应力水平较低，设计偏保守，可考虑轻量化"
        else:
            return "需要完整仿真以获得准确结果"