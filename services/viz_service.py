"""
可视化服务
功能：自动生成应力云图、位移云图、动画
"""

import sys
from pathlib import Path
import json

# 尝试导入 PyVista
try:
    import pyvista as pv
    PYVISTA_AVAILABLE = True
except ImportError:
    PYVISTA_AVAILABLE = False
    print("Warning: PyVista not available, visualization will be disabled")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("Warning: NumPy not available")

class VisualizationService:
    """可视化服务类"""

    def __init__(self):
        # 启动虚拟显示（Docker 环境）
        if PYVISTA_AVAILABLE:
            try:
                pv.start_xvfb()
            except:
                pass

    def visualize_stress(self, frd_file, output_png, options=None):
        """生成应力云图"""
        if not PYVISTA_AVAILABLE:
            return {
                'success': False,
                'error': 'PyVista not installed. Please install with: pip install pyvista'
            }

        if not NUMPY_AVAILABLE:
            return {
                'success': False,
                'error': 'NumPy not installed. Please install with: pip install numpy'
            }

        options = options or {}

        try:
            # 读取结果文件
            mesh = pv.read(frd_file)

            # 查找应力数据
            stress_arrays = [name for name in mesh.array_names if 'stress' in name.lower() or 'mises' in name.lower()]

            if not stress_arrays:
                return {'success': False, 'error': 'No stress data found'}

            scalar_name = stress_arrays[0]

            # 创建绘图器
            plotter = pv.Plotter(
                off_screen=True,
                window_size=options.get('window_size', [1920, 1080])
            )

            # 获取数据范围
            data = mesh[scalar_name]
            vmin = data.min()
            vmax = data.max()

            # 添加网格
            plotter.add_mesh(
                mesh,
                scalars=scalar_name,
                cmap=options.get('colormap', 'jet'),
                show_edges=options.get('show_edges', False),
                edge_color=options.get('edge_color', 'black'),
                scalar_bar_args={'title': 'Stress (MPa)'},
                lighting=True
            )

            # 设置相机位置
            if 'camera_position' in options:
                plotter.camera_position = options['camera_position']
            else:
                plotter.camera_position = 'isometric'

            # 保存截图
            plotter.screenshot(output_png, window_size=options.get('window_size', [1920, 1080]))
            plotter.close()

            return {
                'success': True,
                'output': output_png,
                'data_range': [float(vmin), float(vmax)]
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def visualize_displacement(self, frd_file, output_png, options=None):
        """生成位移云图"""
        if not PYVISTA_AVAILABLE:
            return {
                'success': False,
                'error': 'PyVista not installed. Please install with: pip install pyvista'
            }

        options = options or {}

        try:
            mesh = pv.read(frd_file)

            # 查找位移数据
            disp_arrays = [name for name in mesh.array_names if 'disp' in name.lower() or 'displacement' in name.lower()]

            if not disp_arrays:
                return {'success': False, 'error': 'No displacement data found'}

            scalar_name = disp_arrays[0]

            plotter = pv.Plotter(off_screen=True)
            plotter.add_mesh(
                mesh,
                scalars=scalar_name,
                cmap=options.get('colormap', 'viridis'),
                show_edges=options.get('show_edges', False)
            )

            plotter.screenshot(output_png)
            plotter.close()

            return {'success': True, 'output': output_png}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def create_animation(self, frd_file, output_gif, options=None):
        """创建旋转动画"""
        if not PYVISTA_AVAILABLE:
            return {
                'success': False,
                'error': 'PyVista not installed. Please install with: pip install pyvista'
            }

        options = options or {}

        try:
            mesh = pv.read(frd_file)
            plotter = pv.Plotter(off_screen=True)
            plotter.add_mesh(mesh, color=options.get('color', 'lightblue'))

            # 创建旋转动画
            plotter.open_gif(output_gif, fps=options.get('fps', 15))
            plotter.write_frame()

            for angle in np.linspace(0, 360, options.get('frames', 30)):
                plotter.camera.azimuth = angle
                plotter.write_frame()

            plotter.close()

            return {'success': True, 'output': output_gif}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def visualize_frd(self, frd_file, viz_type="stress"):
        """读取FRD文件并返回基本信息"""
        if not PYVISTA_AVAILABLE:
            print("Warning: PyVista not available")
            return None

        try:
            mesh = pv.read(frd_file)
            return {
                'file': frd_file,
                'n_points': mesh.n_points,
                'n_cells': mesh.n_cells,
                'array_names': mesh.array_names,
                'viz_type': viz_type
            }
        except Exception as e:
            print(f"Error reading FRD file: {e}")
            return None
