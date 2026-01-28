import streamlit as st
import sys
import os

# 切换到项目根目录
os.chdir('/app')

# 确保Python路径包含必要的目录
if '/app' not in sys.path:
    sys.path.insert(0, '/app')

from server.data_collector import SimulationDataCollector
from components.charts import *
import pandas as pd
import numpy as np

def show_analysis_page():
    """数据分析页面"""
    
    st.title("📈 数据分析")
    
    collector = SimulationDataCollector()
    
    # 分析类型选择
    analysis_type = st.selectbox(
        "选择分析类型",
        ["全部", "stress", "thermal", "modal"]
    )
    
    if analysis_type == "全部":
        analysis_type = None
    
    # 加载数据
    training_data = collector.get_training_data(analysis_type=analysis_type)
    
    if not training_data:
        st.warning("暂无数据可分析")
        return
    
    st.success(f"✅ 已加载 {len(training_data)} 条记录")
    
    # 提取数据
    max_stresses = [r[6] for r in training_data if r[6]]
    mean_stresses = [r[7] for r in training_data if r[7]]
    max_disps = [r[8] for r in training_data if r[8]]
    num_elements = [r[3] for r in training_data if r[3]]
    
    # 统计摘要
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if max_stresses:
            st.metric(
                "应力范围",
                f"{min(max_stresses):.1f} - {max(max_stresses):.1f} MPa"
            )
    
    with col2:
        if mean_stresses:
            st.metric(
                "平均应力",
                f"{sum(mean_stresses)/len(mean_stresses):.1f} MPa"
            )
    
    with col3:
        if max_disps:
            st.metric(
                "最大位移",
                f"{max(max_disps):.4f} mm"
            )
    
    with col4:
        if num_elements:
            st.metric(
                "平均单元数",
                f"{int(sum(num_elements)/len(num_elements)):,}"
            )
    
    st.markdown("---")
    
    # 可视化标签页
    tab1, tab2, tab3, tab4 = st.tabs([
        "应力分布",
        "散点矩阵",
        "相关性分析",
        "统计分析"
    ])
    
    with tab1:
        st.subheader("应力分布直方图")
        
        if max_stresses:
            fig = create_histogram(
                max_stresses,
                bins=30,
                title="最大应力分布",
                x_label="应力 (MPa)"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("参数散点矩阵")
        
        if max_stresses and mean_stresses:
            fig = create_scatter_plot(
                max_stresses,
                mean_stresses[:len(max_stresses)],
                "最大应力 (MPa)",
                "平均应力 (MPa)",
                "应力相关性"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        if max_stresses and num_elements:
            fig = create_scatter_plot(
                num_elements[:len(max_stresses)],
                max_stresses,
                "网格单元数",
                "最大应力 (MPa)",
                "网格密度 vs 应力"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("数据相关性热力图")
        
        if len(max_stresses) > 1:
            # 构建相关性矩阵
            df = pd.DataFrame({
                '最大应力': max_stresses,
                '平均应力': mean_stresses[:len(max_stresses)],
            })
            
            correlation = df.corr()
            
            fig = create_heatmap(
                correlation.values,
                correlation.columns.tolist(),
                correlation.index.tolist(),
                "参数相关性矩阵"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("统计分析")
        
        if max_stresses:
            # 箱线图
            data_dict = {
                '最大应力': max_stresses,
                '平均应力': mean_stresses[:len(max_stresses)]
            }
            
            fig = create_box_plot(data_dict, "应力分布箱线图")
            st.plotly_chart(fig, use_container_width=True)
            
            # 统计表格
            st.subheader("详细统计信息")
            
            stats_df = pd.DataFrame({
                '指标': ['最大应力', '平均应力', '最大位移'],
                '最小值': [
                    min(max_stresses) if max_stresses else 0,
                    min(mean_stresses) if mean_stresses else 0,
                    min(max_disps) if max_disps else 0
                ],
                '最大值': [
                    max(max_stresses) if max_stresses else 0,
                    max(mean_stresses) if mean_stresses else 0,
                    max(max_disps) if max_disps else 0
                ],
                '平均值': [
                    np.mean(max_stresses) if max_stresses else 0,
                    np.mean(mean_stresses) if mean_stresses else 0,
                    np.mean(max_disps) if max_disps else 0
                ],
                '标准差': [
                    np.std(max_stresses) if max_stresses else 0,
                    np.std(mean_stresses) if mean_stresses else 0,
                    np.std(max_disps) if max_disps else 0
                ]
            })
            
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
