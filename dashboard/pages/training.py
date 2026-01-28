import streamlit as st
import plotly.graph_objects as go
import time

# 导入统一的导入助手
from utils.imports import (
    train_surrogate_model,
    SurrogateModel,
    SimulationDataCollector
)

def show_training_page():
    """模型训练页面"""

    st.title("🤖 模型训练")

    collector = SimulationDataCollector()

    # 检查数据量
    try:
        training_data = collector.get_training_data()
        data_count = len(training_data)
    except:
        training_data = []
        data_count = 0

    st.info(f"📊 当前可用训练数据: {data_count} 条")

    if data_count == 0:
        st.warning("没有足够的训练数据，请先运行一些仿真任务")
        st.stop()

    # 训练参数配置
    st.divider()
    st.subheader("⚙️ 训练参数")

    col1, col2 = st.columns(2)

    with col1:
        model_type = st.selectbox(
            "模型类型",
            ["Neural Network", "Random Forest", "XGBoost"],
            help="选择要训练的模型类型"
        )

        epochs = st.slider(
            "训练轮数",
            min_value=10,
            max_value=500,
            value=100,
            step=10,
            help="神经网络的训练轮数"
        )

    with col2:
        batch_size = st.selectbox(
            "批大小",
            [16, 32, 64, 128],
            index=1,
            help="每个批次的样本数量"
        )

        validation_split = st.slider(
            "验证集比例",
            min_value=0.1,
            max_value=0.3,
            value=0.2,
            step=0.05,
            help="用于验证的数据比例"
        )

    # 高级选项
    with st.expander("🔧 高级选项"):
        learning_rate = st.slider(
            "学习率",
            min_value=0.0001,
            max_value=0.1,
            value=0.001,
            format="%.4f"
        )

        early_stopping = st.checkbox(
            "早停机制",
            value=True,
            help="当验证损失不再下降时停止训练"
        )

    # 开始训练
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("🚀 开始训练", type="primary", use_container_width=True):
            # 创建训练进度条
            progress_bar = st.progress(0)
            status_text = st.empty()

            # 训练模型
            try:
                if train_surrogate_model:
                    model = train_surrogate_model(
                        training_data=training_data,
                        model_type=model_type,
                        epochs=epochs,
                        batch_size=batch_size,
                        validation_split=validation_split,
                        learning_rate=learning_rate,
                        early_stopping=early_stopping
                    )

                    # 模拟训练进度
                    for i in range(100):
                        progress_bar.progress(i + 1)
                        status_text.text(f"训练进度: {i + 1}%")
                        time.sleep(0.05)

                    status_text.text("✅ 训练完成！")

                    # 显示训练结果
                    st.success("模型训练成功！")

                    # 模型评估
                    st.subheader("📈 模型评估")

                    # 创建模拟的评估图表
                    metrics = {
                        '准确率': 0.92,
                        '精确率': 0.89,
                        '召回率': 0.95,
                        'F1分数': 0.92
                    }

                    fig = go.Figure()

                    fig.add_trace(go.Bar(
                        x=list(metrics.keys()),
                        y=list(metrics.values()),
                        marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
                    ))

                    fig.update_layout(
                        title="模型性能指标",
                        yaxis_range=[0, 1],
                        xaxis_title="指标",
                        yaxis_title="分数"
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # 保存模型
                    st.subheader("💾 保存模型")

                    model_name = st.text_input(
                        "模型名称",
                        value=f"{model_type.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    )

                    if st.button("保存模型"):
                        st.success(f"模型 '{model_name}' 已保存！")

                    # 下载模型
                    if st.button("下载模型文件"):
                        st.download_button(
                            label="下载 .pkl 文件",
                            data=b"model_data_placeholder",
                            file_name=f"{model_name}.pkl",
                            mime="application/octet-stream"
                        )

                else:
                    st.error("训练功能暂不可用")

            except Exception as e:
                st.error(f"训练失败: {str(e)}")

    # 历史模型
    st.divider()
    st.subheader("📚 已训练模型")

    # 模拟模型列表
    models = [
        {
            'name': 'neural_network_20260127_143022',
            'type': 'Neural Network',
            'accuracy': 0.92,
            'date': '2026-01-27 14:30:22',
            'size': '2.5 MB'
        },
        {
            'name': 'random_forest_20260126_100515',
            'type': 'Random Forest',
            'accuracy': 0.87,
            'date': '2026-01-26 10:05:15',
            'size': '1.8 MB'
        }
    ]

    for model in models:
        with st.expander(f"{model['name']}"):
            col1, col2, col3, col4 = st.columns(4)

            col1.write(f"**类型**: {model['type']}")
            col2.write(f"**准确率**: {model['accuracy']:.2f}")
            col3.write(f"**日期**: {model['date']}")
            col4.write(f"**大小**: {model['size']}")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("加载模型", key=f"load_{model['name']}"):
                    st.info(f"已加载模型: {model['name']}")

            with col2:
                if st.button("删除模型", key=f"delete_{model['name']}"):
                    st.warning(f"模型 '{model['name']}' 已删除")

from datetime import datetime

# Streamlit 页面入口
show_training_page()
