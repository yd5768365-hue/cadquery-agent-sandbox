"""
Celery任务定义
包含所有的异步任务
"""

from celery import Celery
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Celery实例
celery = Celery(
    'tasks',
    broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

# Celery配置
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分钟超时
    task_soft_time_limit=25 * 60,  # 25分钟软超时
    worker_prefetch_multiplier=1,
    task_acks_late=True
)

@celery.task(bind=True)
def run_gmsh_meshing(self, geometry_file: str, mesh_params: dict):
    """
    Gmsh网格生成任务
    
    Args:
        geometry_file: 几何文件路径
        mesh_params: 网格参数字典
        
    Returns:
        dict: 包含网格文件路径和信息的字典
    """
    try:
        logger.info(f"开始网格生成: {geometry_file}")
        
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': '初始化...'}
        )
        
        # 检查输入文件
        if not Path(geometry_file).exists():
            raise FileNotFoundError(f"几何文件不存在: {geometry_file}")
        
        # 创建输出目录
        output_dir = Path(geometry_file).parent / "mesh"
        output_dir.mkdir(exist_ok=True)
        
        # 生成网格文件名
        mesh_file = output_dir / f"{Path(geometry_file).stem}.msh"
        
        # 构建Gmsh命令
        cmd = [
            'gmsh', geometry_file,
            '-2',  # 2D网格
            '-o', str(mesh_file)
        ]
        
        # 添加网格参数
        if mesh_params.get('clmax'):
            cmd.extend(['-clmax', str(mesh_params['clmax'])])
        if mesh_params.get('clmin'):
            cmd.extend(['-clmin', str(mesh_params['clmin'])])
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 30, 'total': 100, 'status': '运行Gmsh...'}
        )
        
        # 运行Gmsh
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10分钟超时
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Gmsh失败: {result.stderr}")
        
        # 获取网格信息
        mesh_info = {
            'file': str(mesh_file),
            'size': mesh_file.stat().st_size if mesh_file.exists() else 0,
            'params': mesh_params
        }
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'status': '完成'}
        )
        
        logger.info(f"网格生成完成: {mesh_file}")
        
        return {
            'status': 'success',
            'mesh_file': str(mesh_file),
            'mesh_info': mesh_info
        }
        
    except Exception as e:
        logger.error(f"网格生成失败: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }

@celery.task(bind=True)
def run_calculix_simulation(self, mesh_file: str, simulation_params: dict):
    """
    CalculiX仿真任务
    
    Args:
        mesh_file: 网格文件路径
        simulation_params: 仿真参数字典
        
    Returns:
        dict: 包含仿真结果的字典
    """
    try:
        logger.info(f"开始仿真: {mesh_file}")
        
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': '准备输入文件...'}
        )
        
        # 检查网格文件
        if not Path(mesh_file).exists():
            raise FileNotFoundError(f"网格文件不存在: {mesh_file}")
        
        # 创建工作目录
        work_dir = Path(mesh_file).parent / "simulation"
        work_dir.mkdir(exist_ok=True)
        
        # 转换网格格式为CalculiX格式
        inp_file = work_dir / f"{Path(mesh_file).stem}.inp"
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 20, 'total': 100, 'status': '转换网格格式...'}
        )
        
        # 使用gmsh转换格式
        convert_cmd = ['gmsh', mesh_file, '-o', str(inp_file)]
        result = subprocess.run(convert_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"网格格式转换失败: {result.stderr}")
        
        # 创建CalculiX输入文件
        ccx_input_file = work_dir / "simulation.inp"
        create_calculix_input(inp_file, ccx_input_file, simulation_params)
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 50, 'total': 100, 'status': '运行CalculiX...'}
        )
        
        # 运行CalculiX
        ccx_cmd = ['ccx', '-i', str(ccx_input_file.with_suffix(''))]
        result = subprocess.run(
            ccx_cmd,
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=1800  # 30分钟超时
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"CalculiX仿真失败: {result.stderr}")
        
        # 处理结果
        results = process_calculix_results(work_dir)
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'status': '处理结果...'}
        )
        
        logger.info(f"仿真完成: {mesh_file}")
        
        return {
            'status': 'success',
            'results': results,
            'work_dir': str(work_dir)
        }
        
    except Exception as e:
        logger.error(f"仿真失败: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }

@celery.task(bind=True)
def run_visualization(self, result_file: str, viz_params: dict):
    """
    可视化任务
    
    Args:
        result_file: 结果文件路径
        viz_params: 可视化参数字典
        
    Returns:
        dict: 包含可视化结果的字典
    """
    try:
        logger.info(f"开始可视化: {result_file}")
        
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': '初始化...'}
        )
        
        # 检查结果文件
        if not Path(result_file).exists():
            raise FileNotFoundError(f"结果文件不存在: {result_file}")
        
        # 创建输出目录
        output_dir = Path(result_file).parent / "visualization"
        output_dir.mkdir(exist_ok=True)
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 50, 'total': 100, 'status': '生成可视化...'}
        )
        
        # 根据参数生成可视化
        if viz_params.get('type') == 'stress':
            output_file = output_dir / "stress.png"
            # 这里应该调用实际的可视化代码
            # visualize_stress(result_file, output_file, viz_params)
            
        elif viz_params.get('type') == 'displacement':
            output_file = output_dir / "displacement.png"
            # visualize_displacement(result_file, output_file, viz_params)
            
        else:
            output_file = output_dir / "general.png"
            # general_visualization(result_file, output_file, viz_params)
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'status': '完成'}
        )
        
        logger.info(f"可视化完成: {output_file}")
        
        return {
            'status': 'success',
            'output_file': str(output_file),
            'viz_params': viz_params
        }
        
    except Exception as e:
        logger.error(f"可视化失败: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }

@celery.task(bind=True)
def run_ml_prediction(self, features: list, model_type: str = 'stress'):
    """
    机器学习预测任务
    
    Args:
        features: 特征列表
        model_type: 模型类型
        
    Returns:
        dict: 包含预测结果的字典
    """
    try:
        logger.info(f"开始ML预测: {model_type}")
        
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': '加载模型...'}
        )
        
        # 加载模型
        from ml.models.surrogate_model import SurrogateModel
        
        model = SurrogateModel()
        model_path = f"E:/DeepSeek_Work/ml/models/surrogate_{model_type}.pkl"
        
        if not Path(model_path).exists():
            raise FileNotFoundError(f"模型文件不存在: {model_path}")
        
        model.load(model_path)
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 50, 'total': 100, 'status': '进行预测...'}
        )
        
        # 进行预测
        prediction = model.predict(features)
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'status': '完成'}
        )
        
        logger.info(f"ML预测完成: {model_type}")
        
        return {
            'status': 'success',
            'prediction': prediction,
            'model_type': model_type
        }
        
    except Exception as e:
        logger.error(f"ML预测失败: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }

# 辅助函数
def create_calculix_input(mesh_file, output_file, params):
    """创建CalculiX输入文件"""
    # 这里应该实现实际的输入文件创建逻辑
    # 简化示例
    with open(output_file, 'w') as f:
        f.write("*HEADING\n")
        f.write(f"Simulation job - {datetime.now()}\n")
        f.write("*INCLUDE, INPUT={mesh_file.name}\n")
        # 添加材料属性、边界条件、载荷等
        f.write("*MATERIAL, NAME=STEEL\n")
        f.write("*ELASTIC\n")
        f.write("210000, 0.3\n")
        # ... 更多输入文件内容

def process_calculix_results(work_dir):
    """处理CalculiX结果"""
    results = {
        'max_stress': 0.0,
        'min_stress': 0.0,
        'mean_stress': 0.0,
        'max_displacement': 0.0,
        'volume': 0.0,
        'mass': 0.0
    }
    
    # 这里应该实现实际的结果处理逻辑
    # 读取.frd文件并提取结果
    
    return results

def get_task_status(task_id):
    """获取任务状态"""
    from celery.result import AsyncResult
    
    result = AsyncResult(task_id, app=celery)
    return {
        'task_id': task_id,
        'status': result.state,
        'result': result.result if result.ready() else None,
        'progress': result.info.get('current', 0) if result.info else 0,
        'total': result.info.get('total', 100) if result.info else 100
    }

def get_job_progress(job_id):
    """获取作业进度"""
    # 这里可以实现更复杂的进度跟踪逻辑
    return get_task_status(job_id)