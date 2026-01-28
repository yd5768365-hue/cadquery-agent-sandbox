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