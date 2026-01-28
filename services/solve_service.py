"""
求解服务
独立的 CalculiX 求解微服务
"""

import subprocess
import re
from pathlib import Path

class SolveService:
    """求解服务"""
    
    def __init__(self, container_name='cae_calculix'):
        self.container_name = container_name
    
    def run_analysis(self, inp_file, analysis_type='static'):
        """运行分析"""
        
        # 去除 .inp 后缀
        base_name = str(Path(inp_file).with_suffix(''))
        
        cmd = [
            'docker', 'exec', self.container_name,
            'ccx', base_name
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600
            )
            
            if result.returncode == 0:
                # 提取结果
                results = self._extract_results(base_name)
                
                return {
                    'success': True,
                    'frd_file': f"{base_name}.frd",
                    'dat_file': f"{base_name}.dat",
                    'results': results,
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
                'error': 'Analysis timeout (1 hour)'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_results(self, base_name):
        """从结果文件提取关键数据"""
        dat_file = f"{base_name}.dat"
        
        results = {
            'max_stress': None,
            'max_displacement': None
        }
        
        try:
            with open(dat_file, 'r') as f:
                content = f.read()
            
            # 提取最大应力
            stress_pattern = r'maximum.*von Mises.*?(\d+\.?\d*)'
            stress_match = re.search(stress_pattern, content, re.IGNORECASE)
            if stress_match:
                results['max_stress'] = float(stress_match.group(1))
            
            # 提取最大位移
            disp_pattern = r'maximum.*displacement.*?(\d+\.?\d*)'
            disp_match = re.search(disp_pattern, content, re.IGNORECASE)
            if disp_match:
                results['max_displacement'] = float(disp_match.group(1))
        
        except Exception as e:
            print(f"提取结果失败: {e}")
        
        return results
    
    def check_convergence(self, dat_file):
        """检查收敛性"""
        try:
            with open(dat_file, 'r') as f:
                content = f.read()
            
            # 检查收敛标志
            if 'CONVERGENCE' in content.upper():
                return {'converged': True}
            elif 'NO CONVERGENCE' in content.upper():
                return {
                    'converged': False,
                    'reason': 'Failed to converge'
                }
            else:
                return {
                    'converged': False,
                    'reason': 'Unknown status'
                }
        
        except Exception as e:
            return {
                'converged': False,
                'reason': str(e)
            }
    
    def estimate_time(self, inp_file):
        """估算求解时间"""
        try:
            with open(inp_file, 'r') as f:
                content = f.read()
            
            # 估算基于节点数和单元数
            node_pattern = r'\*NODE.*?(\d+)'
            elem_pattern = r'\*ELEMENT.*?(\d+)'
            
            # 简化估算：假设每1000个单元需要1秒
            # 实际时间取决于分析类型和复杂度
            
            return {
                'estimated_seconds': 60,  # 默认估计
                'note': 'Actual time depends on problem complexity'
            }
        
        except:
            return {'estimated_seconds': None}
    
    def validate_input_file(self, inp_file):
        """验证输入文件"""
        errors = []
        warnings = []
        
        try:
            with open(inp_file, 'r') as f:
                content = f.read()
            
            # 检查必要的关键字
            required_keywords = ['*NODE', '*ELEMENT', '*MATERIAL', '*STEP']
            
            for keyword in required_keywords:
                if keyword not in content.upper():
                    errors.append(f"Missing required keyword: {keyword}")
            
            # 检查常见问题
            if '*BOUNDARY' not in content.upper():
                warnings.append("No boundary conditions defined")
            
            if '*CLOAD' not in content.upper() and '*DLOAD' not in content.upper():
                warnings.append("No loads defined")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings
            }
        
        except Exception as e:
            return {
                'valid': False,
                'errors': [str(e)],
                'warnings': []
            }


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 测试网格服务
    print("测试网格生成服务...")
    mesh_service = MeshGenerationService()
    
    result = mesh_service.generate_mesh(
        '/app/input/bracket.step',
        params={'clmax': 5.0, 'clmin': 0.5}
    )
    
    print(f"网格生成结果: {result}")
    
    # 测试求解服务
    print("\n测试求解服务...")
    solve_service = SolveService()
    
    result = solve_service.run_analysis('/app/analyses/bracket.inp')
    
    print(f"求解结果: {result}")