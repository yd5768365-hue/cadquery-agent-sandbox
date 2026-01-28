import streamlit as st
import sys
import os

from server.data_collector import SimulationDataCollector
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from dashboard.components.charts import *

def show_monitor_page():
    """实时监控页面"""
    
    st.title("📊 实时监控仪表盘")
    
    # 加载数据
    collector = SimulationDataCollector()
    stats = collector.get_statistics()
    
    # 顶部指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = stats.get('total_simulations', 0)
        st.metric(
            label="总仿真数",
            value=total,
            delta="+5 今日"
        )
    
    with col2:
        success = stats.get('successful_simulations', 0)
        rate = (success / max(total, 1)) * 100
        st.metric(
            label="成功率",
            value=f"{rate:.1f}%",
            delta="+2.3%"
        )
    
    with col3:
        avg_duration = stats.get('avg_duration', 0)
        if avg_duration:
            duration_str = f"{avg_duration/60:.1f} 分钟"
        else:
            duration_str = "N/A"
        st.metric(
            label="平均耗时",
            value=duration_str,
            delta="-12%"
        )
    
    with col4:
        st.metric(
            label="运行中任务",
            value="2",
            delta="实时"
        )
    
    st.markdown("---")
    
    # 图表区域
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 仿真类型分布")
        
        by_type = stats.get('by_type', {})
        if by_type:
            labels = list(by_type.keys())
            values = list(by_type.values())
            
            fig = create_pie_chart(labels, values, "仿真类型分布")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无数据")
    
    with col2:
        st.subheader("📈 最近7天趋势")
        
        # 生成模拟数据
        dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
        values = [12, 15, 18, 14, 20, 22, 25]
        
        fig = create_time_series_chart(dates, values, "仿真数量趋势", "仿真数")
        st.plotly_chart(fig, use_container_width=True)
    
    # 最近仿真记录
    st.subheader("🕒 最近仿真记录")
    
    training_data = collector.get_training_data(limit=10)
    
    if training_data:
        records = []
        for record in training_data:
            records.append({
                '仿真ID': record[0][:8],
                '类型': record[1],
                '网格单元': record[3] if record[3] else 'N/A',
                '最大应力(MPa)': f"{record[6]:.2f}" if record[6] else 'N/A',
                '状态': '✅ 完成'
            })
        
        df_records = pd.DataFrame(records)
        st.dataframe(df_records, use_container_width=True, hide_index=True)
    else:
        st.info("暂无仿真记录")
    
    # 刷新按钮
    if st.button("🔄 刷新数据"):
        st.rerun()
