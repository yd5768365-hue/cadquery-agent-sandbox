import streamlit as st
import sys
import os

# 切换到项目根目录
os.chdir('/app')

# 确保Python路径包含必要的目录
if '/app' not in sys.path:
    sys.path.insert(0, '/app')

from services.viz_service import VisualizationService
from dashboard.components.three_d_viewer import CAE3DViewer

def show_visualize_page():
    """可视化页面"""
    
    st.title("🎨 3D 可视化")
    
    # 文件选择
    result_file = st.text_input(
        "结果文件路径",
        "E:/DeepSeek_Work/test/results/example.frd",
        help="输入 .frd 结果文件的完整路径"
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        viz_type = st.selectbox(
            "可视化类型",
            ["应力云图", "位移云图", "旋转动画"]
        )
    
    with col2:
        colormap = st.selectbox(
            "配色方案",
            ["jet", "viridis", "plasma", "coolwarm", "rainbow"]
        )
    
    with col3:
        scale_factor = st.number_input(
            "位移放大倍数",
            min_value=1.0,
            max_value=100.0,
            value=10.0,
            step=1.0
        )
    
    # 生成按钮
    if st.button("🎨 生成可视化", use_container_width=True):
        if not os.path.exists(result_file):
            st.error(f"文件不存在: {result_file}")
        else:
            with st.spinner("生成中..."):
                try:
                    viz = VisualizationService()
                    output_dir = "E:/DeepSeek_Work/test/visualizations"
                    os.makedirs(output_dir, exist_ok=True)
                    
                    if viz_type == "应力云图":
                        result = viz.visualize_stress(
                            result_file,
                            f"{output_dir}/stress.png",
                            options={'colormap': colormap}
                        )
                    elif viz_type == "位移云图":
                        result = viz.visualize_displacement(
                            result_file,
                            f"{output_dir}/displacement.png",
                            scale_factor=scale_factor
                        )
                    else:
                        result = viz.create_animation(
                            result_file,
                            f"{output_dir}/rotation.gif",
                            num_frames=36
                        )
                    
                    if result['success']:
                        st.success("✅ 生成成功！")
                        
                        # 显示图片
                        if viz_type != "旋转动画":
                            st.image(result['output'], use_column_width=True)
                            
                            # 显示统计信息
                            if 'statistics' in result:
                                stats = result['statistics']
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    if 'max_stress' in stats:
                                        st.metric("最大应力", f"{stats['max_stress']:.2f} MPa")
                                
                                with col2:
                                    if 'mean_stress' in stats:
                                        st.metric("平均应力", f"{stats['mean_stress']:.2f} MPa")
                                
                                with col3:
                                    if 'max_displacement' in stats:
                                        st.metric("最大位移", f"{stats['max_displacement']:.4f} mm")
                        else:
                            st.info("动画已生成，请在文件系统中查看")
                    else:
                        st.error(f"生成失败: {result['error']}")
                
                except Exception as e:
                    st.error(f"错误: {e}")
    
    st.markdown("---")
    
    # 历史可视化
    st.subheader("📂 历史可视化")
    
    viz_dir = "E:/DeepSeek_Work/test/visualizations"
    
    if os.path.exists(viz_dir):
        images = [f for f in os.listdir(viz_dir) if f.endswith(('.png', '.jpg'))]
        
        if images:
            # 分页显示
            items_per_page = 6
            total_pages = (len(images) - 1) // items_per_page + 1
            
            page = st.number_input(
                "页码",
                min_value=1,
                max_value=total_pages,
                value=1,
                step=1
            )
            
            start_idx = (page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, len(images))
            
            cols = st.columns(3)
            for i, img in enumerate(images[start_idx:end_idx]):
                with cols[i % 3]:
                    st.image(
                        os.path.join(viz_dir, img),
                        caption=img,
                        use_column_width=True
                    )
        else:
            st.info("暂无历史可视化")
    else:
        st.info("可视化目录不存在")