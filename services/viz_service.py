"""
可视化服务
功能：自动生成应力云图、位移云图、动画
"""

import pyvista as pv
import numpy as np
from pathlib import Path
import json

class VisualizationService:
    """可视化服务类"""
    
    def __init__(self):
        # 启动虚拟显示（Docker 环境）
        try:
            pv.start_xvfb()
        except:
            pass
    
    def visualize_stress(self, frd_file, output_png, options=None):
        """生成应力云图"""
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
                scalar_bar_args={
                    'title': 'Von Mises Stress (MPa)',
                    'title_font_size': 24,
                    'label_font_size': 18,
                    'bold': True,
                    'n_labels': 5
                },
                clim=[vmin, vmax]
            )
            
            # 添加统计信息
            stats_text = f"""Max: {vmax:.2f} MPa
Min: {vmin:.2f} MPa
Mean: {data.mean():.2f} MPa
Std: {data.std():.2f} MPa"""
            
            plotter.add_text(
                stats_text,
                position='upper_left',
                font_size=14,
                color='white',
                font='arial'
            )
            
            # 设置相机
            camera_position = options.get('camera_position', 'iso')
            if camera_position == 'iso':
                plotter.camera_position = 'iso'
            elif camera_position == 'xy':
                plotter.camera_position = 'xy'
            elif camera_position == 'xz':
                plotter.camera_position = 'xz'
            elif camera_position == 'yz':
                plotter.camera_position = 'yz'
            
            plotter.camera.zoom(options.get('zoom', 1.3))
            
            # 添加坐标轴
            if options.get('show_axes', True):
                plotter.show_axes()
            
            # 添加比例尺
            if options.get('show_ruler', False):
                plotter.add_ruler()
            
            # 保存截图
            plotter.screenshot(output_png, transparent_background=False)
            plotter.close()
            
            return {
                'success': True,
                'output': output_png,
                'statistics': {
                    'max_stress': float(vmax),
                    'min_stress': float(vmin),
                    'mean_stress': float(data.mean()),
                    'std_stress': float(data.std())
                }
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def visualize_displacement(self, frd_file, output_png, scale_factor=1.0, options=None):
        """生成位移云图"""
        options = options or {}
        
        try:
            mesh = pv.read(frd_file)
            
            # 查找位移数据
            disp_arrays = [name for name in mesh.array_names if 'disp' in name.lower()]
            
            if not disp_arrays:
                return {'success': False, 'error': 'No displacement data found'}
            
            disp_name = disp_arrays[0]
            
            # 应用位移（放大显示）
            if mesh.n_arrays > 0:
                displacement = mesh[disp_name]
                if displacement.ndim == 2 and displacement.shape[1] == 3:
                    warped = mesh.warp_by_vector(disp_name, factor=scale_factor)
                else:
                    warped = mesh
            else:
                warped = mesh
            
            # 计算位移幅值
            if displacement.ndim == 2:
                magnitude = np.linalg.norm(displacement, axis=1)
            else:
                magnitude = displacement
            
            # 创建绘图器
            plotter = pv.Plotter(off_screen=True, window_size=[1920, 1080])
            
            # 添加变形网格
            plotter.add_mesh(
                warped,
                scalars=magnitude,
                cmap='viridis',
                show_edges=False,
                scalar_bar_args={
                    'title': f'Displacement (mm, x{scale_factor})',
                    'title_font_size': 24,
                    'label_font_size': 18
                }
            )
            
            # 添加原始轮廓（半透明）
            if options.get('show_original', True):
                plotter.add_mesh(mesh, opacity=0.3, color='gray', show_edges=True)
            
            # 统计信息
            stats_text = f"""Max Disp: {magnitude.max():.4f} mm
Scale: {scale_factor}x"""
            
            plotter.add_text(stats_text, position='upper_left', font_size=14, color='white')
            
            plotter.camera_position = 'iso'
            plotter.camera.zoom(1.3)
            plotter.show_axes()
            
            plotter.screenshot(output_png)
            plotter.close()
            
            return {
                'success': True,
                'output': output_png,
                'statistics': {
                    'max_displacement': float(magnitude.max()),
                    'mean_displacement': float(magnitude.mean()),
                    'scale_factor': scale_factor
                }
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_animation(self, frd_file, output_gif, num_frames=30, options=None):
        """创建动画（旋转视图）"""
        options = options or {}
        
        try:
            mesh = pv.read(frd_file)
            
            # 查找标量数据
            scalar_name = mesh.array_names[0] if mesh.array_names else None
            
            if not scalar_name:
                return {'success': False, 'error': 'No data to visualize'}
            
            plotter = pv.Plotter(off_screen=True, window_size=[800, 600])
            
            plotter.add_mesh(
                mesh,
                scalars=scalar_name,
                cmap='jet',
                show_edges=False
            )
            
            plotter.camera_position = 'iso'
            
            # 打开 GIF 动画
            plotter.open_gif(output_gif, fps=options.get('fps', 10))
            
            # 旋转动画
            for i in range(num_frames):
                plotter.camera.azimuth += 360 / num_frames
                plotter.write_frame()
            
            plotter.close()
            
            return {
                'success': True,
                'output': output_gif,
                'num_frames': num_frames
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_comparison(self, frd_files, output_png, titles=None):
        """创建多个结果的对比图"""
        try:
            n = len(frd_files)
            
            plotter = pv.Plotter(
                shape=(1, n),
                off_screen=True,
                window_size=[600*n, 600]
            )
            
            for i, frd_file in enumerate(frd_files):
                mesh = pv.read(frd_file)
                scalar_name = mesh.array_names[0] if mesh.array_names else None
                
                plotter.subplot(0, i)
                
                if titles and i < len(titles):
                    plotter.add_text(titles[i], font_size=16)
                
                plotter.add_mesh(
                    mesh,
                    scalars=scalar_name,
                    cmap='jet',
                    show_edges=False
                )
                
                plotter.camera_position = 'iso'
            
            plotter.screenshot(output_png)
            plotter.close()
            
            return {'success': True, 'output': output_png}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
