"""
网格生成服务
独立的网格生成微服务
"""

import subprocess
import json
import sys
from pathlib import Path

class MeshGenerationService:
    """网格生成服务"""
    
    def __init__(self, container_name='cae_gmsh'):
        self.container_name = container_name
    
    def generate_mesh(self, input_file, output_file=None, params=None):
        """生成网格"""
        
        if output_file is None:
            output_file = str(Path(input_file).with_suffix('.msh'))
        
        params = params or {}
        clmax = params.get('clmax', 5.0)
        clmin = params.get('clmin', 0.5)
        algorithm = params.get('algorithm', 'auto')
        optimize = params.get('optimize', True)
        
        # 构建命令
        cmd = [
            'docker', 'exec', self.container_name,
            'gmsh', input_file,
            '-3',
            '-clmax', str(clmax),
            '-clmin', str(clmin),
            '-algo', algorithm,
        ]
        
        if optimize:
            cmd.append('-optimize')
        
        cmd.extend(['-o', output_file])
        
        # 执行
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                # 获取网格统计
                stats = self._get_mesh_statistics(output_file)
                
                return {
                    'success': True,
                    'mesh_file': output_file,
                    'statistics': stats,
                    'stdout': result.stdout
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr
                }
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Mesh generation timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_mesh_statistics(self, mesh_file):
        """获取网格统计信息"""
        cmd = [
            'docker', 'exec', self.container_name,
            'gmsh', mesh_file, '-info'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # 解析输出
            stats = {
                'num_nodes': 0,
                'num_elements': 0
            }
            
            for line in result.stdout.split('\n'):
                if 'nodes' in line.lower():
                    try:
                        stats['num_nodes'] = int(line.split()[0])
                    except:
                        pass
                elif 'elements' in line.lower():
                    try:
                        stats['num_elements'] = int(line.split()[0])
                    except:
                        pass
            
            return stats
        
        except:
            return {}
    
    def validate_geometry(self, step_file):
        """验证几何"""
        cmd = [
            'docker', 'exec', self.container_name,
            'gmsh', step_file, '-0', '-check'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            return {
                'valid': result.returncode == 0,
                'message': result.stdout if result.returncode == 0 else result.stderr
            }
        except Exception as e:
            return {
                'valid': False,
                'message': str(e)
            }
    
    def repair_geometry(self, step_file, output_file=None):
        """修复几何"""
        if output_file is None:
            output_file = str(Path(step_file).with_suffix('.step.fixed'))
        
        cmd = [
            'docker', 'exec', self.container_name,
            'gmsh', step_file, '-0',
            '-string', 'Geometry.OCCFixDegenerated=1; Geometry.OCCFixSmallEdges=1;',
            '-o', output_file
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            return {
                'success': result.returncode == 0,
                'repaired_file': output_file,
                'message': result.stdout if result.returncode == 0 else result.stderr
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
