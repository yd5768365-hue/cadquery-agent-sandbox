"""
统一的导入助手模块
处理 Docker 容器环境中的模块导入问题
"""

import sys
import os
from pathlib import Path

# 切换到项目根目录
os.chdir('/app')

# 确保Python路径包含必要的目录
paths_to_add = [
    '/app',
    '/app/server',
    '/app/ml',
    '/app/services',
]

for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

print(f"当前工作目录: {os.getcwd()}")
print(f"Python路径: {sys.path[:5]}")

# 尝试导入并导出所有需要的模块
try:
    from server.data_collector import SimulationDataCollector
    print("✓ 成功导入 SimulationDataCollector")
except ImportError as e:
    print(f"✗ 导入 SimulationDataCollector 失败: {e}")
    SimulationDataCollector = None

try:
    from server.tasks import get_task_status, get_job_progress
    print("✓ 成功导入任务函数")
except ImportError as e:
    print(f"✗ 导入任务函数失败: {e}")
    get_task_status = None
    get_job_progress = None

try:
    from ml.models.surrogate_model import SurrogateModel
    print("✓ 成功导入 SurrogateModel")
except ImportError as e:
    print(f"✗ 导入 SurrogateModel 失败: {e}")
    SurrogateModel = None

try:
    from ml.trainers.train_surrogate import train_surrogate_model
    print("✓ 成功导入 train_surrogate_model")
except ImportError as e:
    print(f"✗ 导入 train_surrogate_model 失败: {e}")
    train_surrogate_model = None

try:
    from services.viz_service import VisualizationService
    print("✓ 成功导入 VisualizationService")
except ImportError as e:
    print(f"✗ 导入 VisualizationService 失败: {e}")
    VisualizationService = None

# 如果某些模块导入失败，创建模拟类
if SimulationDataCollector is None:
    print("创建 SimulationDataCollector 模拟类")
    class SimulationDataCollector:
        def get_statistics(self):
            return {
                'total_simulations': 0,
                'successful_simulations': 0,
                'avg_duration': 0,
                'by_type': {}
            }

        def get_training_data(self):
            return []

        def get_recent_simulations(self, limit=10):
            return []

if VisualizationService is None:
    print("创建 VisualizationService 模拟类")
    class VisualizationService:
        def __init__(self):
            self.visualizer = None

        def visualize_frd(self, frd_file):
            return None

# 导出所有可用的模块
__all__ = [
    'SimulationDataCollector',
    'get_task_status',
    'get_job_progress',
    'SurrogateModel',
    'train_surrogate_model',
    'VisualizationService',
]
