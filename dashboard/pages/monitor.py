import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 导入统一的导入助手
from utils.imports import SimulationDataCollector, get_task_status

def show_monitor_page():
    """实时监控页面"""

    st.title("📊 实时监控仪表盘")

    # 加载数据
    collector = SimulationDataCollector()
    stats = collector.get_statistics()

    # 顶部指标卡片
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="总仿真次数",
            value=stats.get('total_simulations', 0),
            delta="今日 +5"
        )

    with col2:
        st.metric(
            label="成功次数",
            value=stats.get('successful_simulations', 0),
            delta="成功率 95%"
        )

    with col3:
        st.metric(
            label="运行中",
            value=stats.get('running_tasks', 0),
            delta="当前"
        )

    with col4:
        st.metric(
            label="平均耗时",
            value=f"{stats.get('avg_duration', 0):.1f}s",
            delta="-5.2s"
        )

    # 任务状态监控
    st.divider()
    st.subheader("🔍 任务监控")

    # 任务ID输入
    task_id = st.text_input(
        "输入任务ID",
        placeholder="例如: task-abc123",
        help="输入要查询的任务ID"
    )

    if task_id:
        if st.button("查询任务状态"):
            if get_task_status:
                status = get_task_status(task_id)
                st.json(status)
            else:
                st.warning("任务状态查询功能暂不可用")

    # 最近任务列表
    st.subheader("📋 最近任务")

    recent_tasks = collector.get_recent_simulations(limit=20)

    if recent_tasks:
        tasks_df = pd.DataFrame(recent_tasks)

        # 状态列着色
        def color_status(status):
            if status == 'completed':
                return 'background-color: #d4edda'
            elif status == 'failed':
                return 'background-color: #f8d7da'
            elif status == 'running':
                return 'background-color: #fff3cd'
            return ''

        # 显示表格
        st.dataframe(
            tasks_df,
            column_config={
                "status": st.column_config.TextColumn("状态", help="任务当前状态"),
                "duration": st.column_config.NumberColumn("耗时 (秒)", format="%.2f"),
            },
            use_container_width=True
        )

        # 任务状态分布
        col1, col2 = st.columns(2)

        with col1:
            status_counts = tasks_df['status'].value_counts()

            fig_pie = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title='任务状态分布'
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            if 'duration' in tasks_df.columns:
                fig_box = px.box(
                    tasks_df,
                    y='duration',
                    title='耗时分布'
                )
                st.plotly_chart(fig_box, use_container_width=True)

    else:
        st.info("暂无任务记录")

    # 系统性能监控
    st.divider()
    st.subheader("⚡ 系统性能")

    # 模拟性能数据
    perf_data = {
        'CPU 使用率': 45.2,
        '内存使用率': 62.8,
        '磁盘使用率': 34.5,
        '网络流量': 125.6
    }

    for metric, value in perf_data.items():
        st.progress(value / 100, text=f"{metric}: {value:.1f}%")

    # 刷新按钮
    if st.button("🔄 刷新数据"):
        st.rerun()

    # 自动刷新选项
    auto_refresh = st.checkbox("自动刷新 (每5秒)", value=False)

    if auto_refresh:
        time.sleep(5)
        st.rerun()

import time

# Streamlit 页面入口
show_monitor_page()
