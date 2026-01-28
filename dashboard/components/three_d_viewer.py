import pyvista as pv
import streamlit as st
from stpyvista import stpyvista
import numpy as np

class CAE3DViewer:
    """CAE 3D 可视化组件"""
    
    def __init__(self):
        self.plotter = None
    
    def load_mesh(self, mesh_file):
        """加载网格文件"""
        try:
            mesh = pv.read(mesh_file)
            return mesh
        except Exception as e:
            st.error(f"加载网格失败: {e}")
            return None
    
    def create_stress_viewer(self, frd_file, colormap='jet'):
        """创建应力可视化"""
        mesh = self.load_mesh(frd_file)
        
        if mesh is None:
            return None
        
        # 查找应力数据
        stress_arrays = [name for name in mesh.array_names 
                        if 'stress' in name.lower() or 'mises' in name.lower()]
        
        if not stress_arrays:
            st.warning("未找到应力数据")
            return None
        
        scalar_name = stress_arrays[0]
        
        # 创建绘图器
        self.plotter = pv.Plotter()
        
        # 添加网格
        self.plotter.add_mesh(
            mesh,
            scalars=scalar_name,
            cmap=colormap,
            show_edges=False,
            scalar_bar_args={
                'title': 'Von Mises Stress (MPa)',
                'title_font_size': 20,
                'label_font_size': 16
            }
        )
        
        self.plotter.camera_position = 'iso'
        self.plotter.show_axes()
        
        return self.plotter
    
    def create_displacement_viewer(self, frd_file, scale_factor=10.0):
        """创建位移可视化"""
        mesh = self.load_mesh(frd_file)
        
        if mesh is None:
            return None
        
        # 查找位移数据
        disp_arrays = [name for name in mesh.array_names 
                      if 'disp' in name.lower()]
        
        if not disp_arrays:
            st.warning("未找到位移数据")
            return None
        
        disp_name = disp_arrays[0]
        displacement = mesh[disp_name]
        
        # 应用位移
        if displacement.ndim == 2 and displacement.shape[1] == 3:
            warped = mesh.warp_by_vector(disp_name, factor=scale_factor)
            magnitude = np.linalg.norm(displacement, axis=1)
        else:
            warped = mesh
            magnitude = displacement
        
        # 创建绘图器
        self.plotter = pv.Plotter()
        
        # 添加变形网格
        self.plotter.add_mesh(
            warped,
            scalars=magnitude,
            cmap='viridis',
            show_edges=False,
            scalar_bar_args={
                'title': f'Displacement (mm, x{scale_factor})',
                'title_font_size': 20
            }
        )
        
        # 添加原始轮廓
        self.plotter.add_mesh(
            mesh,
            opacity=0.3,
            color='gray',
            show_edges=True
        )
        
        self.plotter.camera_position = 'iso'
        self.plotter.show_axes()
        
        return self.plotter
    
    def render_in_streamlit(self):
        """在 Streamlit 中渲染"""
        if self.plotter:
            stpyvista(self.plotter, key="cae_3d_viewer")
    
    def add_clipping_plane(self, normal='x'):
        """添加剖切平面"""
        if self.plotter:
            self.plotter.add_plane_widget(
                callback=lambda plane: self.plotter.add_mesh(
                    plane,
                    color='red',
                    opacity=0.3
                )
            )
    
    def create_multi_view(self, mesh_files, titles=None):
        """创建多视图"""
        n = len(mesh_files)
        
        self.plotter = pv.Plotter(shape=(1, n))
        
        for i, mesh_file in enumerate(mesh_files):
            mesh = self.load_mesh(mesh_file)
            
            if mesh:
                self.plotter.subplot(0, i)
                
                if titles and i < len(titles):
                    self.plotter.add_text(titles[i], font_size=12)
                
                scalar_name = mesh.array_names[0] if mesh.array_names else None
                
                self.plotter.add_mesh(
                    mesh,
                    scalars=scalar_name,
                    cmap='jet',
                    show_edges=False
                )
                
                self.plotter.camera_position = 'iso'
        
        return self.plotter