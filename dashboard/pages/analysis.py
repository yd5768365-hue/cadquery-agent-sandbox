import streamlit as st
import pandas as pd
import numpy as np

# 导入统一的导入助手
from utils.imports import SimulationDataCollector

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
        # 获取统计数据
        stats = collector.get_statistics()

        # 总览卡片
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="总仿真次数",
                value=stats.get('total_simulations', 0),
                delta="今日 +5"
            )

        with col2:
            st.metric(
                label="成功率",
                value=f"{stats.get('success_rate', 0):.1f}%",
                delta="+2.3%"
            )

        with col3:
            st.metric(
                label="平均耗时",
                value=f"{stats.get('avg_duration', 0):.1f}s",
                delta="-5.2s"
            )

        # 按类型统计
        by_type = stats.get('by_type', {})

        if by_type:
            st.subheader("按仿真类型统计")

            types_df = pd.DataFrame(list(by_type.items()), columns=['类型', '数量'])

            fig = px.pie(
                types_df,
                values='数量',
                names='类型',
                title='仿真类型分布'
            )
            st.plotly_chart(fig, use_container_width=True)

        # 最近仿真记录
        recent = collector.get_recent_simulations(limit=10)

        if recent:
            st.subheader("最近仿真记录")

            recent_df = pd.DataFrame(recent)
            st.dataframe(recent_df, use_container_width=True)

    else:
        # 按类型筛选数据
        training_data = collector.get_training_data(analysis_type)

        if not training_data:
            st.info(f"暂无 {analysis_type} 类型的仿真数据")
        else:
            # 数据统计
            st.subheader(f"{analysis_type} 仿真数据统计")

            df = pd.DataFrame(training_data)

            # 基本统计信息
            st.write("基本统计:")
            st.write(df.describe())

            # 数据可视化
            col1, col2 = st.columns(2)

            with col1:
                # 直方图
                fig = px.histogram(
                    df,
                    x='value',
                    title=f'{analysis_type} 数值分布',
                    nbins=30
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # 时间序列
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    time_fig = px.line(
                        df,
                        x='timestamp',
                        y='value',
                        title=f'{analysis_type} 时间趋势'
                    )
                    st.plotly_chart(time_fig, use_container_width=True)

            # 数据下载
            st.download_button(
                label="下载分析数据 (CSV)",
                data=df.to_csv(index=False),
                file_name=f'{analysis_type}_analysis.csv',
                mime='text/csv'
            )

# Streamlit 页面入口
show_analysis_page()
